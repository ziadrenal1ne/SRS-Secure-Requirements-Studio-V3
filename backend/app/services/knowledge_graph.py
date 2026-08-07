"""Knowledge Graph service.

This is the deterministic core of the "knowledge as interconnected
concepts" requirement — no LLM call is needed to seed a graph, compute
completion/confidence, find gaps, or pick the next concept to ask
about. The Interview Engine (Phase 3) layers an LLM on top of this to
turn "which concept is next" into "what should I actually ask", and to
turn a free-text answer into structured updates against a node — but
graph traversal itself stays fully testable without any AI in the loop.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.concept_catalog import CONCEPT_BY_KEY, CONCEPT_CATALOG
from app.exceptions import ConflictError, NotFoundError
from app.models.knowledge_graph import KnowledgeGraphEdge, KnowledgeGraphNode
from app.repositories.knowledge_graph import (
    KnowledgeGraphEdgeRepository,
    KnowledgeGraphNodeRepository,
)

_IMPORTANCE_WEIGHT = {"low": 1, "medium": 2, "high": 3, "critical": 4}
_RISK_WEIGHT = {"low": 1, "medium": 2, "high": 3, "critical": 4}

# A dependency is considered "satisfied enough" to unblock dependents once
# its completion reaches this threshold — it doesn't need to be perfect,
# just informative enough that follow-on questions make sense.
DEPENDENCY_SATISFACTION_THRESHOLD = 40
# A node is no longer offered as the "next question" once it crosses this.
NODE_SUFFICIENT_THRESHOLD = 80


class KnowledgeGraphService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.nodes = KnowledgeGraphNodeRepository(session)
        self.edges = KnowledgeGraphEdgeRepository(session)

    async def seed_project_graph(self, project_id: uuid.UUID) -> list[KnowledgeGraphNode]:
        existing = await self.nodes.list_for_project(project_id)
        if existing:
            raise ConflictError("Knowledge graph already seeded for this project.")

        created: dict[str, KnowledgeGraphNode] = {}
        for concept in CONCEPT_CATALOG:
            node = await self.nodes.add(
                KnowledgeGraphNode(
                    project_id=project_id,
                    concept_key=concept.key,
                    domain=concept.domain,
                    label=concept.label,
                    description=concept.description,
                    importance=concept.importance,
                    business_value=concept.business_value,
                    risk=concept.risk,
                    validation_rules=list(concept.validation_rules),
                    missing_information=[concept.label],
                )
            )
            created[concept.key] = node

        for concept in CONCEPT_CATALOG:
            for dep_key in concept.depends_on:
                await self.edges.add(
                    KnowledgeGraphEdge(
                        node_id=created[concept.key].id,
                        dependency_node_id=created[dep_key].id,
                    )
                )

        await self.session.commit()
        return list(created.values())

    async def get_graph(
        self, project_id: uuid.UUID
    ) -> tuple[list[KnowledgeGraphNode], list[KnowledgeGraphEdge]]:
        nodes = await self.nodes.list_for_project(project_id)
        edges = await self.edges.list_for_nodes([n.id for n in nodes])
        return nodes, edges

    async def _dependency_map(
        self, nodes: list[KnowledgeGraphNode]
    ) -> dict[uuid.UUID, list[uuid.UUID]]:
        edges = await self.edges.list_for_nodes([n.id for n in nodes])
        deps: dict[uuid.UUID, list[uuid.UUID]] = {n.id: [] for n in nodes}
        for edge in edges:
            deps.setdefault(edge.node_id, []).append(edge.dependency_node_id)
        return deps

    def _priority_score(self, node: KnowledgeGraphNode) -> float:
        importance = _IMPORTANCE_WEIGHT.get(node.importance, 2)
        risk = _RISK_WEIGHT.get(node.risk, 2)
        gap = 100 - node.completion
        return (importance * 3) + (risk * 2) + (node.business_value * 0.02) + (gap * 0.05)

    async def compute_gaps(self, project_id: uuid.UUID) -> list[KnowledgeGraphNode]:
        nodes = await self.nodes.list_for_project(project_id)
        if not nodes:
            raise NotFoundError("Knowledge graph has not been seeded for this project.")
        gaps = [n for n in nodes if n.completion < NODE_SUFFICIENT_THRESHOLD]
        gaps.sort(key=self._priority_score, reverse=True)
        return gaps

    async def next_concept(self, project_id: uuid.UUID) -> KnowledgeGraphNode | None:
        """The single highest-priority concept whose dependencies are
        already sufficiently answered — this is what the Interview
        Engine turns into the next question. Returns None once every
        concept has crossed the sufficiency threshold (interview complete).
        """
        nodes = await self.nodes.list_for_project(project_id)
        if not nodes:
            raise NotFoundError("Knowledge graph has not been seeded for this project.")

        by_id = {n.id: n for n in nodes}
        deps = await self._dependency_map(nodes)

        candidates = []
        for node in nodes:
            if node.completion >= NODE_SUFFICIENT_THRESHOLD:
                continue
            dependency_ids = deps.get(node.id, [])
            if all(
                by_id[dep_id].completion >= DEPENDENCY_SATISFACTION_THRESHOLD
                for dep_id in dependency_ids
                if dep_id in by_id
            ):
                candidates.append(node)

        if not candidates:
            return None

        candidates.sort(key=self._priority_score, reverse=True)
        return candidates[0]

    async def project_completion(self, project_id: uuid.UUID) -> dict:
        nodes = await self.nodes.list_for_project(project_id)
        if not nodes:
            raise NotFoundError("Knowledge graph has not been seeded for this project.")
        total = len(nodes)
        avg_completion = sum(n.completion for n in nodes) / total
        avg_confidence = sum(n.confidence for n in nodes) / total
        completed = sum(1 for n in nodes if n.completion >= NODE_SUFFICIENT_THRESHOLD)
        by_domain: dict[str, dict] = {}
        for node in nodes:
            d = by_domain.setdefault(node.domain, {"total": 0, "completed": 0})
            d["total"] += 1
            if node.completion >= NODE_SUFFICIENT_THRESHOLD:
                d["completed"] += 1
        return {
            "total_concepts": total,
            "completed_concepts": completed,
            "overall_completion": round(avg_completion, 1),
            "overall_confidence": round(avg_confidence, 1),
            "by_domain": by_domain,
        }

    async def apply_update(
        self,
        project_id: uuid.UUID,
        concept_key: str,
        *,
        captured_data: dict | None = None,
        completion_delta: int = 0,
        confidence_delta: int = 0,
        missing_information: list[str] | None = None,
        mark_question_asked: str | None = None,
    ) -> KnowledgeGraphNode:
        """Applied by the Interview Engine after interpreting an answer.
        Kept here (not in the interview service) so the update rules —
        clamping, status transitions — live in one place regardless of
        what triggers them (interview turn, manual admin edit, re-review).
        """
        if concept_key not in CONCEPT_BY_KEY:
            raise NotFoundError(f"Unknown concept '{concept_key}'.")

        node = await self.nodes.get_by_concept_key(project_id, concept_key)
        if not node:
            raise NotFoundError("Knowledge graph has not been seeded for this project.")

        if captured_data:
            node.captured_data = {**node.captured_data, **captured_data}
        node.completion = max(0, min(100, node.completion + completion_delta))
        node.confidence = max(0, min(100, node.confidence + confidence_delta))
        if missing_information is not None:
            node.missing_information = missing_information
        if mark_question_asked:
            node.generated_questions = [*node.generated_questions, mark_question_asked]

        if node.completion >= NODE_SUFFICIENT_THRESHOLD:
            node.status = "completed"
        elif node.completion > 0:
            node.status = "in_progress"
        else:
            node.status = "not_started"

        await self.session.commit()
        await self.session.refresh(node)
        return node
