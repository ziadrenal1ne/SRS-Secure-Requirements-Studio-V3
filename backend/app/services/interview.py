"""Business analyst interview engine for Secure Requirements Studio V2."""

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, NotFoundError
from app.models.interview import InterviewSession, InterviewTurn
from app.models.knowledge_graph import KnowledgeGraphNode
from app.repositories.interview import InterviewSessionRepository, InterviewTurnRepository
from app.requirements_engine.interview_engine import next_question
from app.requirements_engine.question_bank import MAX_QUESTIONS
from app.services.knowledge_graph import KnowledgeGraphService
from app.services.llm_client import LLMClient, TemplateLLMClient, get_llm_client
from app.services.requirement import RequirementService

MAX_INTERVIEW_QUESTIONS = MAX_QUESTIONS
TECHNICAL_TERMS = (
    "postgresql", "row-level", "sql", "jwt", "oauth", "rbac", "abac", "api",
    "orm", "docker", "kubernetes", "microservice", "backend", "frontend",
    "graphql", "redis", "totp", "architecture", "devops",
)

CONCEPT_KEYS = {
    "project_name": "business.objective",
    "objective": "business.success_metrics",
    "problem": "business.scope_boundaries",
    "current_situation": "business.scope_boundaries",
    "expected_result": "business.success_metrics",
    "users": "users.primary_personas",
    "user_actions": "roles.catalog",
    "restricted_information": "permissions.data_visibility_scope",
    "main_features": "entities.core_business_objects",
    "view_information": "entities.core_business_objects",
    "edit_information": "entities.core_business_objects",
    "documents": "reporting.document_upload",
    "search": "api.export_requirements",
    "dashboards": "reporting.dashboard_design",
    "maps": "users.access_channels",
    "reports": "reporting.kpis",
    "exports": "api.export_requirements",
    "notifications": "notifications.channels",
    "main_workflow": "workflow.approval_process",
    "validation": "workflow.approval_process",
    "rejection": "workflow.task_assignment",
    "history": "workflow.version_history",
    "sensitive_information": "security.data_classification",
    "availability": "deployment.availability_requirements",
    "devices": "users.access_channels",
    "languages": "accessibility.wcag",
    "mvp": "business.scope_boundaries",
    "future_features": "business.scope_boundaries",
    "special_constraints": "compliance.internal_policies",
    "final_notes": "testing.acceptance_criteria",
}


def technical_question(question: str) -> bool:
    lowered = question.lower()
    return any(term in lowered for term in TECHNICAL_TERMS)


def _answers_from_turns(turns: list[InterviewTurn]) -> dict[str, str]:
    answers: dict[str, str] = {}
    for turn in turns:
        question_id = str(turn.extracted_data.get("question_id") or "")
        if question_id:
            answers[question_id] = turn.answer.strip()
    return answers


def _planned_question(turns: list[InterviewTurn]) -> dict | None:
    return next_question(_answers_from_turns(turns), set(_answers_from_turns(turns)))


class InterviewService:
    def __init__(self, session: AsyncSession, llm_client: LLMClient | None = None):
        self.session = session
        self.sessions = InterviewSessionRepository(session)
        self.turns = InterviewTurnRepository(session)
        self.kg = KnowledgeGraphService(session)
        self.llm = llm_client or get_llm_client()

    def _history_for(self, interview_session: InterviewSession) -> list[dict]:
        return [{"question": t.question, "answer": t.answer} for t in interview_session.turns]

    def session_metadata(self, interview_session: InterviewSession) -> dict:
        planned = _planned_question(interview_session.turns)
        return {
            "pending_question_options": list(planned.get("choices", [])) if planned else [],
            "pending_section": planned.get("section") if planned else None,
            "max_questions": MAX_INTERVIEW_QUESTIONS,
        }

    async def _planned_node(
        self, project_id: uuid.UUID, concept_key: str
    ) -> KnowledgeGraphNode | None:
        nodes, _ = await self.kg.get_graph(project_id)
        return next((n for n in nodes if n.concept_key == concept_key), None)

    async def _ask_next_question(
        self, interview_session: InterviewSession
    ) -> tuple[KnowledgeGraphNode | None, str | None]:
        planned = _planned_question(interview_session.turns)
        if planned is None:
            interview_session.status = "completed"
            interview_session.pending_concept_key = None
            interview_session.pending_question = None
            await self.session.commit()
            return None, None

        concept_key = CONCEPT_KEYS.get(str(planned["id"]), "business.objective")
        next_node = await self._planned_node(interview_session.project_id, concept_key)
        if next_node is None:
            next_node = await self.kg.next_concept(interview_session.project_id)
        if next_node is None:
            interview_session.status = "completed"
            interview_session.pending_concept_key = None
            interview_session.pending_question = None
            await self.session.commit()
            return None, None

        question = str(planned["question"])
        await self.kg.apply_update(
            interview_session.project_id,
            next_node.concept_key,
            mark_question_asked=question,
        )
        interview_session.pending_concept_key = next_node.concept_key
        interview_session.pending_question = question
        await self.session.commit()
        return next_node, question

    async def start_or_resume(self, project_id: uuid.UUID) -> InterviewSession:
        existing = await self.sessions.get_active_for_project(project_id)
        if existing:
            if len(existing.turns) >= MAX_INTERVIEW_QUESTIONS:
                existing.status = "completed"
                existing.pending_concept_key = None
                existing.pending_question = None
                await self.session.commit()
            elif existing.pending_question is None and existing.status == "active":
                await self._ask_next_question(existing)
                refreshed = await self.sessions.get_with_turns(existing.id)
                assert refreshed is not None
                return refreshed
            return existing

        interview_session = await self.sessions.add(
            InterviewSession(project_id=project_id, status="active")
        )
        await self.session.commit()
        loaded = await self.sessions.get_with_turns(interview_session.id)
        assert loaded is not None
        await self._ask_next_question(loaded)
        refreshed = await self.sessions.get_with_turns(interview_session.id)
        assert refreshed is not None
        return refreshed

    async def submit_answer(self, project_id: uuid.UUID, answer_text: str) -> dict:
        interview_session = await self.sessions.get_active_for_project(project_id)
        if not interview_session:
            raise NotFoundError("No active interview session for this project.")
        if interview_session.status == "completed":
            raise ConflictError("This interview is already complete.")
        if len(interview_session.turns) >= MAX_INTERVIEW_QUESTIONS:
            interview_session.status = "completed"
            interview_session.pending_concept_key = None
            interview_session.pending_question = None
            await self.session.commit()
            raise ConflictError("The interview is already complete.")
        if not interview_session.pending_concept_key or not interview_session.pending_question:
            raise ConflictError("No question is currently pending for this session.")

        concept_key = interview_session.pending_concept_key
        question = interview_session.pending_question
        planned = _planned_question(interview_session.turns)
        question_id = str(planned["id"]) if planned else concept_key

        nodes, _ = await self.kg.get_graph(project_id)
        node = next((n for n in nodes if n.concept_key == concept_key), None)
        if node is None:
            raise NotFoundError("Pending concept no longer exists in the knowledge graph.")

        history = self._history_for(interview_session)
        try:
            interpretation = await self.llm.interpret_answer(node, question, answer_text, history)
        except Exception as exc:
            logging.getLogger(__name__).warning("llm_interpret_failed: %s", exc)
            interpretation = await TemplateLLMClient().interpret_answer(node, question, answer_text, history)
        captured_data = {
            **interpretation.captured_data,
            "raw_answer": answer_text.strip(),
            "question": question,
            "question_id": question_id,
            "section": planned.get("section") if planned else concept_key,
            "importance": "critical" if planned and planned.get("required") else "high",
        }

        updated_node = await self.kg.apply_update(
            project_id,
            concept_key,
            captured_data=captured_data,
            completion_delta=max(interpretation.completion_delta, 80),
            confidence_delta=max(interpretation.confidence_delta, 70),
            missing_information=interpretation.missing_information,
        )
        try:
            await RequirementService(self.session).generate_for_node(project_id, updated_node)
        except Exception as exc:
            logging.getLogger(__name__).warning("requirement_generation_failed: %s", exc)

        next_sequence = len(interview_session.turns) + 1
        turn = await self.turns.add(
            InterviewTurn(
                session_id=interview_session.id,
                sequence=next_sequence,
                concept_key=concept_key,
                question=question,
                answer=answer_text,
                completion_delta=interpretation.completion_delta,
                confidence_delta=interpretation.confidence_delta,
                consultant_note=interpretation.consultant_note,
                extracted_data=captured_data,
            )
        )
        if turn not in interview_session.turns:
            interview_session.turns.append(turn)
        interview_session.pending_concept_key = None
        interview_session.pending_question = None
        await self.session.commit()

        reloaded = await self.sessions.get_with_turns(interview_session.id)
        assert reloaded is not None
        next_node, next_question = await self._ask_next_question(reloaded)

        generated_document_id = None
        if reloaded.status == "completed":
            await self._close_remaining_gaps(project_id)
            from app.services.document_generator import DocumentGeneratorService

            document = await DocumentGeneratorService(self.session).generate(project_id)
            generated_document_id = document.id

        next_planned = _planned_question(reloaded.turns)
        return {
            "concept_key": concept_key,
            "consultant_note": interpretation.consultant_note,
            "updated_node": updated_node,
            "next_question": next_question,
            "next_concept_key": next_node.concept_key if next_node else None,
            "next_question_options": list(next_planned.get("choices", [])) if next_planned else [],
            "next_section": next_planned.get("section") if next_planned else None,
            "max_questions": MAX_INTERVIEW_QUESTIONS,
            "generated_document_id": generated_document_id,
            "interview_status": reloaded.status,
        }

    async def _close_remaining_gaps(self, project_id: uuid.UUID) -> None:
        nodes, _ = await self.kg.get_graph(project_id)
        for node in nodes:
            if node.completion < 75:
                node.completion = 75
                node.confidence = max(node.confidence, 55)
                node.status = "in_progress"
                node.missing_information = ["A confirmer avec le responsable metier."]
        await self.session.commit()

    async def get_state(self, project_id: uuid.UUID) -> InterviewSession:
        existing = await self.sessions.get_active_for_project(project_id)
        if not existing:
            raise NotFoundError("No interview session exists for this project yet.")
        return existing
