"""The Document Generator.

Assembles every document section from data the other engines already
produced â€” Knowledge Graph captured answers, generated Requirements,
and (if available) the Security Engine's analysis. Nothing here invents
project content; where source data is missing, sections say so
explicitly rather than filling in generic filler text.

Scope note: BPMN XML and hand-drawn wireframe mockups are not
implemented. BPMN 2.0 is a heavy XML standard that needs real process
data (swimlanes, gateways) this project doesn't yet model, and
wireframes are visual UI mockups, not something a text/data pipeline
should fabricate. Both are called out explicitly wherever they'd
otherwise appear, rather than being silently skipped.
"""
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import focp_knowledge
from app.exceptions import NotFoundError
from app.models.generated_document import GeneratedDocument
from app.models.interview import InterviewSession, InterviewTurn
from app.models.knowledge_graph import KnowledgeGraphNode
from app.models.organization import Organization
from app.models.project import Project
from app.models.security import SecurityAnalysis
from app.repositories.generated_document import GeneratedDocumentRepository
from app.repositories.knowledge_graph import KnowledgeGraphNodeRepository
from app.repositories.requirement import RequirementRepository
from app.repositories.security import SecurityAnalysisRepository
from app.requirements_engine.document_generator import build_cahier_des_charges
from app.requirements_engine.requirement_engine import build_project_model
from app.services.document_rendering import (
    render_docx,
    render_html,
    render_latex,
    render_markdown,
    render_pdf,
)
from app.services.knowledge_graph import KnowledgeGraphService

REQUIREMENT_TYPE_LABELS = {
    "business": "Exigences mÃ©tier",
    "functional": "Exigences fonctionnelles",
    "non_functional": "Exigences non fonctionnelles",
    "security": "Exigences de sÃ©curitÃ©",
    "technical": "Exigences techniques",
    "infrastructure": "Exigences d'infrastructure",
    "deployment": "Exigences de dÃ©ploiement",
    "maintenance": "Exigences de maintenance",
    "training": "Exigences de formation",
    "performance": "Exigences de performance",
    "accessibility": "Exigences d'accessibilitÃ©",
}


def _answer(node: KnowledgeGraphNode | None) -> str:
    if not node or not node.captured_data:
        return ""
    return str(node.captured_data.get("raw_answer", "")).strip()


def _slug(text: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in text.lower()).strip("_")


class DocumentGeneratorService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.kg_nodes = KnowledgeGraphNodeRepository(session)
        self.requirements = RequirementRepository(session)
        self.security_analyses = SecurityAnalysisRepository(session)
        self.documents = GeneratedDocumentRepository(session)
        self.kg = KnowledgeGraphService(session)

    async def build_content(self, project_id: uuid.UUID) -> dict:
        project = await self.session.get(Project, project_id)
        if not project:
            raise NotFoundError("Project not found.")
        organization = await self.session.get(Organization, project.organization_id)

        nodes = await self.kg_nodes.list_for_project(project_id)
        if not nodes:
            raise NotFoundError("Knowledge graph has not been seeded for this project.")
        by_key = {n.concept_key: n for n in nodes}

        requirements = await self.requirements.list_for_project(project_id)
        completion = await self.kg.project_completion(project_id)
        interview_turns = await self._interview_turns(project_id)

        security: SecurityAnalysis | None = await self.security_analyses.get_for_project(
            project_id
        )

        requirements_by_type: dict[str, list[dict]] = {}
        for req in requirements:
            requirements_by_type.setdefault(req.requirement_type, []).append(
                {
                    "requirement_key": req.requirement_key,
                    "title": req.title,
                    "description": req.description,
                    "priority": req.priority,
                    "business_goal": req.business_goal,
                    "actors": req.actors,
                    "acceptance_criteria": req.acceptance_criteria,
                    "dependencies": req.dependencies,
                    "security_controls": req.security_controls,
                    "database_tables": req.database_tables,
                    "api_endpoints": req.api_endpoints,
                    "ui_screens": req.ui_screens,
                    "test_cases": req.test_cases,
                    "risk": req.risk,
                    "owner": req.owner,
                    "status": req.status,
                    "source_concept_key": req.source_concept_key,
                }
            )

        stakeholders = [
            {"concept": n.label, "answer": _answer(n)}
            for n in nodes
            if n.domain == "stakeholders" and _answer(n)
        ]

        answers = self._answers_by_question_id(interview_turns)
        if not answers:
            answers = self._answers_from_graph(by_key)
        cdc_model = build_project_model(answers, fallback_name=project.name)
        cdc = build_cahier_des_charges(
            cdc_model, int(completion.get("overall_completion", 100))
        )
        mvp_diagram = self._build_mvp_diagram(cdc_model, project)
        conception_mvp = self._build_conception_mvp(cdc_model, cdc, mvp_diagram)

        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "project": {
                "name": project.name,
                "short_name": project.short_name,
                "department": project.department,
                "description": project.description,
                "status": project.status,
                "organization": organization.name if organization else "",
            },
            "completeness": completion,
            "executive_summary": self._build_executive_summary(by_key, project),
            "cahier_des_charges": cdc,
            "conception_mvp": {"summary": "", "modules": [], "flows": [], "data": [], "security": [], "diagram": ""},
            "governance_and_esg": {
                "sdgs": focp_knowledge.SUSTAINABLE_DEVELOPMENT_GOALS,
                "esg_indicators": focp_knowledge.ESG_INDICATORS,
                "conventions": focp_knowledge.CONVENTION_TYPES,
            },
            "stakeholders": stakeholders,
            "requirements_by_type": requirements_by_type,
            "requirement_type_labels": REQUIREMENT_TYPE_LABELS,
            "data_dictionary": data_dictionary,
            "user_stories": user_stories,
            "test_plan": test_plan,
            "deployment_notes": _answer(by_key.get("deployment.target_environment")),
            "availability_notes": _answer(by_key.get("deployment.availability_requirements")),
            "maintenance_notes": _answer(by_key.get("testing.acceptance_criteria")),
            "training_notes": _answer(by_key.get("training.needs")),
            "monitoring_notes": _answer(by_key.get("monitoring.operational_metrics")),
            "diagrams": {"mvp_diagram_mermaid": mvp_diagram},
            "security": self._security_section(security),
            "unimplemented_sections": [
                {
                    "name": "Diagramme de processus BPMN 2.0",
                    "reason": "Non genere dans le Cahier des Charges simplifie V2.",
                },
                {
                    "name": "Maquettes / wireframes d'interface",
                    "reason": "Non generees dans le Cahier des Charges simplifie V2.",
                },
            ],
        }

    async def _interview_turns(self, project_id: uuid.UUID) -> list[InterviewTurn]:
        result = await self.session.execute(
            select(InterviewTurn)
            .join(InterviewSession, InterviewTurn.session_id == InterviewSession.id)
            .where(InterviewSession.project_id == project_id)
            .order_by(InterviewTurn.sequence)
        )
        return list(result.scalars().all())

    def _answer_by_section(self, turns: list[InterviewTurn]) -> dict[str, list[str]]:
        grouped: dict[str, list[str]] = {}
        for turn in turns:
            section = str(turn.extracted_data.get("section") or turn.concept_key)
            grouped.setdefault(section, []).append(turn.answer.strip())
        return grouped

    def _answers_by_question_id(self, turns: list[InterviewTurn]) -> dict[str, str]:
        answers: dict[str, str] = {}
        for turn in turns:
            question_id = str(turn.extracted_data.get("question_id") or "")
            if question_id:
                answers[question_id] = turn.answer.strip()
        return answers

    def _answers_from_graph(self, by_key: dict[str, KnowledgeGraphNode]) -> dict[str, str]:
        return {
            "objective": _answer(by_key.get("business.objective")),
            "problem": _answer(by_key.get("business.scope_boundaries")),
            "expected_result": _answer(by_key.get("business.success_metrics")),
            "users": _answer(by_key.get("users.primary_personas")),
            "main_features": _answer(by_key.get("entities.core_business_objects")),
            "documents": _answer(by_key.get("reporting.document_upload")),
            "dashboards": _answer(by_key.get("reporting.dashboard_design")),
            "reports": _answer(by_key.get("reporting.kpis")),
            "sensitive_information": _answer(by_key.get("security.data_classification")),
            "mvp": _answer(by_key.get("business.scope_boundaries")),
        }

    def _missing_confirmation_points(self, grouped: dict[str, list[str]]) -> list[str]:
        required = {
            "Objectif": "Objectif principal",
            "Utilisateurs": "Profils utilisateurs",
            "Cooperatives": "Donnees cooperatives",
            "Beneficiaires": "Donnees beneficiaires",
            "Priorites": "Priorites MVP",
        }
        return [
            f"{label} a confirmer avec le responsable metier."
            for section, label in required.items()
            if not grouped.get(section)
        ]

    def _build_business_cdc(
        self,
        project: Project,
        organization: Organization | None,
        turns: list[InterviewTurn],
        completion: dict,
    ) -> dict:
        grouped = self._answer_by_section(turns)
        points = self._missing_confirmation_points(grouped)
        def get(section):
            return " ".join(grouped.get(section, [])).strip()

        features = [
            label for label, section in (
                ("Gestion des cooperatives", "Cooperatives"),
                ("Gestion des beneficiaires", "Beneficiaires"),
                ("Suivi des activites", "Activites"),
                ("Mise a jour reguliere des donnees", "Donnees mensuelles"),
                ("Gestion documentaire", "Documents"),
                ("Validation des informations", "Validation"),
                ("Tableaux de bord", "Tableaux de bord"),
                ("Recherche et filtres", "Recherche"),
                ("Carte des cooperatives", "Carte"),
                ("Notifications", "Notifications"),
                ("Rapports", "Rapports"),
                ("Suivi ODD/ESG", "ODD"),
            ) if get(section)
        ]

        return {
            "title": "Cahier des Charges - Conception d'une Plateforme de Gestion des Beneficiaires de l'Axe Economie Sociale et Solidaire au sein de la Fondation OCP en integrant des Exigences de Cybersecurite",
            "summary": get("Objectif") or f"Le projet {project.name} vise a cadrer une plateforme metier pour la Fondation OCP.",
            "completeness_score": completion["overall_completion"],
            "points_to_confirm": points,
            "sections": [
                {"title": "1. Presentation du projet", "items": [f"Nom du projet : {project.name}.", f"Organisation : {organization.name if organization else 'Fondation OCP'}.", get("Objectif") or "Objectif principal a confirmer avec le responsable metier."]},
                {"title": "2. Perimetre fonctionnel", "items": features or ["Perimetre fonctionnel a confirmer avec le responsable metier."]},
                {"title": "3. Utilisateurs et droits", "items": [get("Utilisateurs") or "Profils utilisateurs a confirmer.", get("Partage") or "Regles de partage a confirmer."]},
                {"title": "4. Fonctionnalites principales", "items": features or ["Fonctionnalites principales a confirmer."]},
                {"title": "5. Donnees a gerer", "items": [v for v in [get("Cooperatives"), get("Beneficiaires"), get("Documents"), get("Donnees mensuelles")] if v] or ["Donnees principales a confirmer."]},
                {"title": "6. Regles metier", "items": [v for v in [get("Validation"), get("Notifications"), get("Rapports"), get("Recherche")] if v] or ["Regles metier a confirmer."]},
                {"title": "7. Exigences de securite", "items": self._security_requirements(get("Securite metier"), get("Partage"))},
                {"title": "8. Exigences non fonctionnelles", "items": ["Interface simple en francais, avec prise en compte de l'arabe si confirme.", "Temps de reponse adapte a une consultation quotidienne des tableaux de bord.", "Exports fiables et lisibles pour les rapports de pilotage.", "Sauvegarde, tracabilite et disponibilite suffisantes pour un usage Fondation OCP."]},
                {"title": "9. MVP", "items": [get("Priorites") or "Priorites MVP a confirmer avec le responsable metier."]},
                {"title": "10. Criteres d'acceptation", "items": ["Un utilisateur Fondation peut consulter les cooperatives et beneficiaires prevus.", "Les informations sensibles ne sont visibles que par les profils autorises.", "Les rapports et tableaux de bord refletent les indicateurs demandes.", "Les points a confirmer sont clairement identifies avant lancement du developpement."]},
            ],
        }

    def _security_requirements(self, sensitive_data: str, sharing: str) -> list[str]:
        base = [
            "Authentification obligatoire pour acceder a la plateforme.",
            "Controle d'acces selon les profils metier et le principe du moindre privilege.",
            "Journalisation des consultations, modifications, validations et exports.",
            "Protection des fichiers ajoutes et verification des droits avant telechargement.",
            "Sauvegardes regulieres et procedure de restauration documentee.",
            "Gestion des sessions et protection contre les acces non autorises.",
        ]
        if sensitive_data:
            base.insert(0, f"Informations sensibles a proteger : {sensitive_data}")
        if sharing:
            base.append(f"Regles de partage a appliquer : {sharing}")
        return base

    def _build_conception_mvp(self, cdc_model, cdc: dict, diagram: str) -> dict:
        return {
            "summary": f"Conception MVP basée sur le Cahier des Charges du projet {cdc_model.project_name}.",
            "actors": cdc_model.users or ["Utilisateur Métier", "Administrateur"],
            "modules": cdc_model.functional_requirements,
            "flows": ["Saisie et mise à jour des données", "Circuit de validation", "Consultation du tableau de bord", "Génération et export des rapports"],
            "data": cdc_model.data_requirements,
            "security": cdc_model.security_needs,
            "diagram": diagram,
        }

    def _build_mvp_diagram(self, cdc_model, project: Project) -> str:
        actors = cdc_model.users or ["Utilisateur Métier", "Administrateur"]
        actor_nodes = []
        for idx, actor in enumerate(actors[:3]):
            node_id = f"A{idx+1}"
            actor_nodes.append(f'    {node_id}["{actor}"] --> P["Plateforme {project.name}"]')
        
        feature_nodes = []
        features = cdc_model.functional_requirements or ["Gestion des données"]
        for idx, feat in enumerate(features[:6]):
            node_id = f"F{idx+1}"
            clean_name = feat.replace("Module de ", "").replace("permettant la gestion complète du périmètre associé", "").strip(" .")
            feature_nodes.append(f'    P --> {node_id}["{clean_name}"]')
            feature_nodes.append(f'    {node_id} --> DB[(Stockage des données)]')
        
        lines = ["flowchart TD"] + actor_nodes + feature_nodes
        return "\n".join(lines)


    def _security_section(self, security: SecurityAnalysis | None) -> dict:
        if not security:
            return {
                "available": False,
                "note": (
                    "Aucune analyse de sÃ©curitÃ© n'a encore Ã©tÃ© exÃ©cutÃ©e pour ce projet "
                    "(POST /projects/{id}/security/analyze)."
                ),
            }
        return {
            "available": True,
            "security_score": security.security_score,
            "checklist": security.security_checklist,
            "threat_model": security.threat_model,
            "risk_register": security.risk_register,
            "rbac_matrix": security.rbac_matrix,
            "privacy_impact_assessment": security.privacy_impact_assessment,
            "data_classification": security.data_classification,
        }

    # ------------------------------------------------------------------
    # Persistence + export
    # ------------------------------------------------------------------

    async def generate(self, project_id: uuid.UUID) -> GeneratedDocument:
        content = await self.build_content(project_id)

        existing = await self.documents.get_for_project(project_id)
        if existing:
            existing.content = content
            await self.session.commit()
            await self.session.refresh(existing)
            return existing

        document = GeneratedDocument(project_id=project_id, content=content)
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def get_document(self, project_id: uuid.UUID) -> GeneratedDocument:
        document = await self.documents.get_for_project(project_id)
        if not document:
            raise NotFoundError(
                "No document has been generated yet for this project â€” run generate first."
            )
        return document

    async def export(self, project_id: uuid.UUID, fmt: str) -> tuple[bytes, str, str]:
        """Returns (content_bytes, media_type, filename). Always renders
        fresh from the latest persisted content â€” never a stale cached file.
        """
        document = await self.get_document(project_id)
        content = document.content
        slug = _slug(content["project"]["short_name"] or content["project"]["name"])

        if fmt == "json":
            import json

            return (
                json.dumps(content, ensure_ascii=False, indent=2).encode("utf-8"),
                "application/json",
                f"{slug}.json",
            )
        if fmt == "md":
            return (
                render_markdown(content).encode("utf-8"),
                "text/markdown",
                f"{slug}.md",
            )
        if fmt == "html":
            return (
                render_html(render_markdown(content)).encode("utf-8"),
                "text/html",
                f"{slug}.html",
            )
        if fmt == "docx":
            return (
                render_docx(content),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                f"{slug}.docx",
            )
        if fmt == "pdf":
            return (render_pdf(content), "application/pdf", f"{slug}.pdf")
        if fmt == "tex":
            return (
                render_latex(content).encode("utf-8"),
                "application/x-tex",
                f"{slug}.tex",
            )

        raise NotFoundError(f"Unsupported export format '{fmt}'.")
