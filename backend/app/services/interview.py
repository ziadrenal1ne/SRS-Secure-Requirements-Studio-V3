"""Business-oriented AI interview engine for Fondation OCP SRS."""

import logging
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, NotFoundError
from app.models.interview import InterviewSession, InterviewTurn
from app.models.knowledge_graph import KnowledgeGraphNode
from app.repositories.interview import InterviewSessionRepository, InterviewTurnRepository
from app.services.knowledge_graph import KnowledgeGraphService
from app.services.llm_client import LLMClient, get_llm_client
from app.services.requirement import RequirementService
from app.services.security_engine import SecurityEngineService

MAX_INTERVIEW_QUESTIONS = 20
TECHNICAL_TERMS = (
    "postgresql", "row-level", "sql", "jwt", "oauth", "rbac", "abac", "api",
    "orm", "docker", "kubernetes", "microservice", "backend", "frontend",
    "chiffrement au repos", "transaction", "devsecops",
)


@dataclass(frozen=True)
class BusinessQuestion:
    section: str
    concept_key: str
    question: str
    options: tuple[str, ...] = ()
    importance: str = "high"


BUSINESS_INTERVIEW_PLAN: tuple[BusinessQuestion, ...] = (
    BusinessQuestion("Objectif", "business.objective", "Quel est le principal objectif de cette plateforme ?"),
    BusinessQuestion("Utilisateurs", "users.primary_personas", "Qui utilisera principalement la plateforme ?", ("Equipes de la Fondation OCP", "Responsables de cooperatives", "Les deux", "Autre")),
    BusinessQuestion("Cooperatives", "entities.core_business_objects", "Quelles informations souhaitez-vous suivre pour chaque cooperative ?", ("Nom", "Ville ou region", "Activite", "Statut", "Contact", "Autre")),
    BusinessQuestion("Beneficiaires", "beneficiaries.definition", "Quelles informations souhaitez-vous suivre sur les beneficiaires ?", ("Femmes", "Hommes", "Jeunes", "Personnes en situation de handicap", "Beneficiaires indirects", "Autre")),
    BusinessQuestion("Activites", "entities.relationships", "Quelles activites des cooperatives souhaitez-vous suivre ?", ("Production", "Formation", "Vente", "Accompagnement", "Evenements", "Autre")),
    BusinessQuestion("Donnees mensuelles", "monitoring.operational_metrics", "Quelles informations doivent etre mises a jour regulierement ?", ("Nombre de beneficiaires", "Activites realisees", "Ventes ou revenus", "Difficultes rencontrees", "Autre")),
    BusinessQuestion("Documents", "reporting.document_upload", "Quels documents souhaitez-vous pouvoir ajouter a la plateforme ?", ("Rapports", "Conventions", "CSV", "Excel", "PDF", "Images", "Autre")),
    BusinessQuestion("Validation", "workflow.approval_process", "Apres l'envoi d'informations par une cooperative, souhaitez-vous qu'elles soient verifiees avant leur validation ?", ("Oui", "Non", "Selon le type d'information", "Je ne sais pas")),
    BusinessQuestion("Tableaux de bord", "reporting.dashboard_design", "Quelles informations voulez-vous voir rapidement sur votre tableau de bord ?", ("Cooperatives suivies", "Beneficiaires", "Documents en attente", "Activites recentes", "Alertes", "Autre")),
    BusinessQuestion("Indicateurs", "reporting.kpis", "Quels chiffres ou indicateurs sont les plus importants pour vous ?", ("Nombre de cooperatives", "Nombre de beneficiaires", "Repartition par region", "ODD touches", "Evolution mensuelle", "Autre")),
    BusinessQuestion("ODD", "business.success_metrics", "Souhaitez-vous relier les activites des cooperatives aux Objectifs de Developpement Durable (ODD) ?", ("Oui", "Non", "Pour certaines activites seulement", "Je ne sais pas")),
    BusinessQuestion("ESG", "compliance.internal_policies", "Quelles informations liees au developpement durable souhaitez-vous suivre ?", ("Impact social", "Impact environnemental", "Gouvernance", "Inclusion", "Autre")),
    BusinessQuestion("Recherche", "api.export_requirements", "Comment souhaitez-vous rechercher une cooperative ?", ("Nom", "Ville", "Region", "Activite", "ODD", "Nombre de beneficiaires", "Statut", "Autre")),
    BusinessQuestion("Carte", "users.access_channels", "Souhaitez-vous visualiser les cooperatives sur une carte ?", ("Oui", "Non", "Oui, avec quelques informations principales", "Je ne sais pas")),
    BusinessQuestion("Notifications", "notifications.channels", "Quelles situations doivent generer une notification ?", ("Donnees non mises a jour", "Rapport manquant", "Document a valider", "Convention arrivant a expiration", "Autre")),
    BusinessQuestion("Rapports", "api.export_requirements", "Quels types de rapports souhaitez-vous pouvoir consulter ou generer ?", ("Rapport mensuel", "Rapport par region", "Rapport par cooperative", "Rapport ODD/ESG", "Export Excel ou PDF", "Autre")),
    BusinessQuestion("Partage", "permissions.data_visibility_scope", "Souhaitez-vous pouvoir partager certaines informations ou rapports avec d'autres personnes de la Fondation ?", ("Oui", "Non", "Selon le type de rapport", "Je ne sais pas")),
    BusinessQuestion("Langues", "accessibility.wcag", "Dans quelles langues la plateforme doit-elle etre disponible ?", ("Francais", "Arabe", "Francais + Arabe", "Autre")),
    BusinessQuestion("Securite metier", "security.data_classification", "Quelles informations doivent etre particulierement protegees ou accessibles uniquement a certaines personnes ?", ("Donnees personnelles", "Documents officiels", "Informations financieres", "Donnees de localisation", "Autre"), "critical"),
    BusinessQuestion("Priorites", "business.scope_boundaries", "Parmi toutes ces fonctionnalites, lesquelles sont indispensables pour la premiere version de la plateforme ?", ("Gestion des cooperatives", "Beneficiaires", "Documents", "Tableaux de bord", "Rapports", "Notifications", "Autre"), "critical"),
)


def question_metadata(turn_count: int) -> BusinessQuestion | None:
    return None if turn_count >= MAX_INTERVIEW_QUESTIONS else BUSINESS_INTERVIEW_PLAN[turn_count]


def technical_question(question: str) -> bool:
    lowered = question.lower()
    return any(term in lowered for term in TECHNICAL_TERMS)


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
        planned = question_metadata(len(interview_session.turns))
        return {
            "pending_question_options": list(planned.options) if planned else [],
            "pending_section": planned.section if planned else None,
            "max_questions": MAX_INTERVIEW_QUESTIONS,
        }

    async def _planned_node(
        self, project_id: uuid.UUID, planned: BusinessQuestion
    ) -> KnowledgeGraphNode | None:
        nodes, _ = await self.kg.get_graph(project_id)
        return next((n for n in nodes if n.concept_key == planned.concept_key), None)

    async def _ask_next_question(
        self, interview_session: InterviewSession
    ) -> tuple[KnowledgeGraphNode | None, str | None]:
        planned = question_metadata(len(interview_session.turns))
        if planned is None:
            await self._close_remaining_gaps(interview_session.project_id)
            interview_session.status = "completed"
            interview_session.pending_concept_key = None
            interview_session.pending_question = None
            await self.session.commit()
            return None, None

        next_node = await self._planned_node(interview_session.project_id, planned)
        if next_node is None:
            next_node = await self.kg.next_concept(interview_session.project_id)
        if next_node is None:
            interview_session.status = "completed"
            interview_session.pending_concept_key = None
            interview_session.pending_question = None
            await self.session.commit()
            return None, None

        question = planned.question
        history = self._history_for(interview_session)
        if history:
            try:
                candidate = await self.llm.generate_question(next_node, history, planned)  # type: ignore[arg-type]
            except TypeError:
                candidate = await self.llm.generate_question(next_node, history)
            if candidate and not technical_question(candidate):
                question = candidate.strip()

        if question in next_node.generated_questions:
            question = planned.question

        await self.kg.apply_update(
            interview_session.project_id,
            next_node.concept_key,
            mark_question_asked=question,
        )
        interview_session.pending_concept_key = next_node.concept_key
        interview_session.pending_question = question
        await self.session.commit()
        return next_node, question

    async def _close_remaining_gaps(self, project_id: uuid.UUID) -> None:
        nodes, _ = await self.kg.get_graph(project_id)
        for node in nodes:
            if node.completion < 75:
                node.completion = 75
                node.confidence = max(node.confidence, 55)
                node.status = "in_progress"
                node.missing_information = ["A confirmer avec le responsable metier."]
        await self.session.commit()

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
        planned = question_metadata(len(interview_session.turns))

        nodes, _ = await self.kg.get_graph(project_id)
        node = next((n for n in nodes if n.concept_key == concept_key), None)
        if node is None:
            raise NotFoundError("Pending concept no longer exists in the knowledge graph.")

        history = self._history_for(interview_session)
        interpretation = await self.llm.interpret_answer(node, question, answer_text, history)
        captured_data = {
            **interpretation.captured_data,
            "raw_answer": answer_text.strip(),
            "question": question,
            "section": planned.section if planned else concept_key,
            "importance": planned.importance if planned else node.importance,
            "custom_answer": answer_text.strip(),
            "exigences_generees": self._derive_business_requirements(planned, answer_text),
        }

        updated_node = await self.kg.apply_update(
            project_id,
            concept_key,
            captured_data=captured_data,
            completion_delta=max(interpretation.completion_delta, 80),
            confidence_delta=max(interpretation.confidence_delta, 70),
            missing_information=interpretation.missing_information,
        )

        await RequirementService(self.session).generate_for_node(project_id, updated_node)
        if updated_node.concept_key in ("security.data_classification", "permissions.data_visibility_scope"):
            try:
                await SecurityEngineService(self.session).analyze(project_id)
            except Exception as exc:
                logging.getLogger(__name__).warning("Failed to trigger security engine: %s", exc)

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
            from app.services.document_generator import DocumentGeneratorService

            document = await DocumentGeneratorService(self.session).generate(project_id)
            generated_document_id = document.id

        next_planned = question_metadata(len(reloaded.turns))
        return {
            "concept_key": concept_key,
            "consultant_note": interpretation.consultant_note,
            "updated_node": updated_node,
            "next_question": next_question,
            "next_concept_key": next_node.concept_key if next_node else None,
            "next_question_options": list(next_planned.options) if next_planned else [],
            "next_section": next_planned.section if next_planned else None,
            "max_questions": MAX_INTERVIEW_QUESTIONS,
            "generated_document_id": generated_document_id,
            "interview_status": reloaded.status,
        }

    def _derive_business_requirements(
        self, planned: BusinessQuestion | None, answer: str
    ) -> list[str]:
        if not planned or not answer.strip():
            return []
        section = planned.section.lower()
        if "securite" in section:
            return [
                "Definir des droits d'acces selon les profils metier.",
                "Tracer les consultations, modifications et exports des informations sensibles.",
                "Proteger les documents et donnees personnelles contre les acces non autorises.",
            ]
        if "validation" in section:
            return ["Prevoir un circuit de verification avant validation lorsque le metier le demande."]
        if "priorites" in section:
            return ["Classer les fonctionnalites indispensables dans le perimetre MVP."]
        return [f"Integrer le besoin exprime dans la section {planned.section} du cahier des charges."]

    async def get_state(self, project_id: uuid.UUID) -> InterviewSession:
        existing = await self.sessions.get_active_for_project(project_id)
        if not existing:
            raise NotFoundError("No interview session exists for this project yet.")
        return existing
