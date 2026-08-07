"""The Requirement Engine.

Requirements are derived from the Knowledge Graph, not typed in by a
person and not invented by an LLM from nothing: once a concept node
crosses the "sufficiently answered" threshold, this service turns it
into one or more Requirement rows, carrying forward what was actually
captured in the interview (the raw answer, the concept's dependencies,
its risk/importance) so every requirement traces back to exactly the
KG node it came from.
"""
import re
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.concept_catalog import CONCEPT_BY_KEY
from app.domain.requirement_types import (
    CONCEPT_REQUIREMENT_TEMPLATES,
    DOMAIN_TO_REQUIREMENT_TYPE,
    default_template_for,
)
from app.exceptions import NotFoundError
from app.models.knowledge_graph import KnowledgeGraphNode
from app.models.requirement import Requirement
from app.repositories.knowledge_graph import KnowledgeGraphEdgeRepository, KnowledgeGraphNodeRepository
from app.repositories.requirement import RequirementRepository
from app.services.knowledge_graph import NODE_SUFFICIENT_THRESHOLD

_TYPE_PREFIX = {
    "business": "BR",
    "functional": "FR",
    "non_functional": "NFR",
    "security": "SEC",
    "technical": "TR",
    "infrastructure": "INFRA",
    "deployment": "DEP",
    "maintenance": "MNT",
    "training": "TRN",
    "performance": "PERF",
    "accessibility": "ACC",
}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", text.lower()).strip("_")


class RequirementService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.requirements = RequirementRepository(session)
        self.kg_nodes = KnowledgeGraphNodeRepository(session)
        self.kg_edges = KnowledgeGraphEdgeRepository(session)

    async def _next_key(self, project_id: uuid.UUID, requirement_type: str) -> str:
        prefix = _TYPE_PREFIX[requirement_type]
        count = await self.requirements.count_for_type(project_id, requirement_type)
        return f"{prefix}-{count + 1:03d}"

    async def _dependency_requirement_keys(
        self, project_id: uuid.UUID, node: KnowledgeGraphNode
    ) -> list[str]:
        """Translate a node's KG dependencies into requirement_keys, but
        only for dependency concepts that have themselves already produced
        a requirement — a dependency that hasn't been asked about yet
        simply isn't traceable to anything, which is correct, not a bug.
        """
        concept = CONCEPT_BY_KEY.get(node.concept_key)
        if not concept or not concept.depends_on:
            return []
        keys = []
        for dep_key in concept.depends_on:
            dep_requirement = await self.requirements.get_by_source_concept(project_id, dep_key)
            if dep_requirement:
                keys.append(dep_requirement.requirement_key)
        return keys

    async def generate_for_node(
        self, project_id: uuid.UUID, node: KnowledgeGraphNode
    ) -> Requirement | None:
        """Idempotent: returns the existing requirement if this concept
        already produced one, generates a new one only if the node is
        sufficiently answered and doesn't have one yet.
        """
        if node.completion < NODE_SUFFICIENT_THRESHOLD:
            return None

        existing = await self.requirements.get_by_source_concept(project_id, node.concept_key)
        if existing:
            return existing

        requirement_type = DOMAIN_TO_REQUIREMENT_TYPE.get(node.domain, "functional")
        template = CONCEPT_REQUIREMENT_TEMPLATES.get(
            node.concept_key, default_template_for(node.domain, node.importance)
        )

        raw_answer = node.captured_data.get("raw_answer", "") if node.captured_data else ""
        description = raw_answer or node.description

        dependencies = await self._dependency_requirement_keys(project_id, node)

        database_tables = [f"{_slug(node.label)}"] if node.domain in ("entities", "database") else []
        api_endpoints = (
            [f"/api/v1/{_slug(node.label)}"] if node.domain == "api" else []
        )

        requirement_key = await self._next_key(project_id, requirement_type)

        requirement = Requirement(
            project_id=project_id,
            requirement_key=requirement_key,
            requirement_type=requirement_type,
            title=template.title_template.format(label=node.label),
            description=description,
            priority=template.default_priority,
            business_goal=node.description,
            risk=node.risk,
            status="draft",
            owner="",
            actors=list(template.default_actors) or ["Utilisateur"],
            acceptance_criteria=[
                f"Le systeme doit satisfaire : {node.label}.",
                *(
                    [f"Basé sur la réponse recueillie : {raw_answer[:200]}"]
                    if raw_answer
                    else []
                ),
            ],
            dependencies=dependencies,
            security_controls=list(template.default_security_controls),
            database_tables=database_tables,
            api_endpoints=api_endpoints,
            ui_screens=[],
            test_cases=list(template.default_test_case_hints) or [f"Vérifier : {node.label}"],
            source_concept_key=node.concept_key,
        )
        self.session.add(requirement)
        await self.session.commit()
        await self.session.refresh(requirement)
        return requirement

    async def generate_missing(self, project_id: uuid.UUID) -> list[Requirement]:
        """Scans the whole graph and generates requirements for every
        sufficiently-completed node that doesn't have one yet. Used both
        by a manual 'regenerate' endpoint and as a catch-up mechanism."""
        nodes = await self.kg_nodes.list_for_project(project_id)
        if not nodes:
            raise NotFoundError("Knowledge graph has not been seeded for this project.")

        created = []
        pending = [n for n in nodes if n.completion >= NODE_SUFFICIENT_THRESHOLD]
        # Two passes resolve dependency ordering: on pass one, a node whose
        # dependency hasn't produced a requirement yet just gets an empty
        # dependencies list; pass two picks up newly-created dependency
        # requirements for anything generated in pass one.
        for _ in range(2):
            for node in pending:
                req = await self.generate_for_node(project_id, node)
                if req and req not in created:
                    created.append(req)
        return created

    async def list_requirements(self, project_id: uuid.UUID) -> list[Requirement]:
        return await self.requirements.list_for_project(project_id)

    async def get_requirement(self, project_id: uuid.UUID, requirement_id: uuid.UUID) -> Requirement:
        req = await self.requirements.get(requirement_id)
        if not req or req.project_id != project_id:
            raise NotFoundError("Requirement not found.")
        return req

    async def update_requirement(
        self, project_id: uuid.UUID, requirement_id: uuid.UUID, updates: dict
    ) -> Requirement:
        req = await self.get_requirement(project_id, requirement_id)
        for field, value in updates.items():
            setattr(req, field, value)
        await self.session.commit()
        await self.session.refresh(req)
        return req

    async def traceability_matrix(self, project_id: uuid.UUID) -> list[dict]:
        reqs = await self.requirements.list_for_project(project_id)
        return [
            {
                "requirement_key": r.requirement_key,
                "requirement_type": r.requirement_type,
                "title": r.title,
                "priority": r.priority,
                "status": r.status,
                "risk": r.risk,
                "dependencies": r.dependencies,
                "security_controls": r.security_controls,
                "database_tables": r.database_tables,
                "api_endpoints": r.api_endpoints,
                "ui_screens": r.ui_screens,
                "test_cases": r.test_cases,
                "source_concept_key": r.source_concept_key,
            }
            for r in reqs
        ]
