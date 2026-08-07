"""The Security Engine.

Builds its analysis from what the Interview Engine and Requirement
Engine have already captured — Knowledge Graph nodes (their captured
answers, risk, importance, completion) and generated Requirements
(their actors) — rather than asking the person anything new. Every
output here is either a deterministic derivation from that data or an
explicit placeholder marked as needing human/legal sign-off (e.g. legal
basis in the Privacy Impact Assessment is never invented).

Scope note: the framework mapping in app/domain/security_frameworks.py
is a category-level reference, not a certified ASVS/MASVS/ISO/NIST/CIS
audit. This engine flags gaps and points at the right control family;
it doesn't replace an actual security review.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.security_frameworks import CONTROLS_BY_KEY, SECURITY_CONTROLS
from app.exceptions import NotFoundError
from app.models.knowledge_graph import KnowledgeGraphNode
from app.models.security import SecurityAnalysis
from app.repositories.knowledge_graph import KnowledgeGraphNodeRepository
from app.repositories.requirement import RequirementRepository
from app.repositories.security import SecurityAnalysisRepository
from app.services.knowledge_graph import NODE_SUFFICIENT_THRESHOLD

_RISK_WEIGHT = {"low": 2, "medium": 4, "high": 7, "critical": 9}

_MFA_KEYWORDS = ("mfa", "multi-facteur", "multifacteur", "multifactor", "2fa", "otp", "double authentification")
_ENCRYPTION_KEYWORDS = ("chiffr", "encrypt", "tls", "ssl", "aes")
_BACKUP_KEYWORDS = ("sauvegarde", "backup", "restauration", "reprise")
_SECRETS_KEYWORDS = ("secret", "vault", "coffre-fort", "gestion des cl", "kms")

# Which concepts (in priority order) generate which STRIDE threats, and
# a rough DREAD weighting anchor. Coverage is intentionally focused on
# the concepts most likely to represent real trust boundaries / data
# flows, not every concept in the catalog.
_STRIDE_CATALOG: list[dict] = [
    {
        "concept_key": "security.authentication_method",
        "category": "Spoofing",
        "threat": "Usurpation d'identité si l'authentification est absente ou faible.",
    },
    {
        "concept_key": "permissions.matrix",
        "category": "Elevation of Privilege",
        "threat": "Un utilisateur pourrait accéder à des fonctions ou données hors de son rôle.",
    },
    {
        "concept_key": "security.audit_logging",
        "category": "Repudiation",
        "threat": "Une action malveillante ou une erreur pourrait ne pas être traçable a posteriori.",
    },
    {
        "concept_key": "beneficiaries.privacy_sensitivity",
        "category": "Information Disclosure",
        "threat": "Exposition non autorisée de données sensibles sur les bénéficiaires.",
    },
    {
        "concept_key": "database.existing_systems",
        "category": "Tampering",
        "threat": "Modification non autorisée des données stockées ou en transit vers ce système.",
    },
    {
        "concept_key": "api.external_integrations",
        "category": "Denial of Service",
        "threat": "Une intégration externe défaillante ou attaquée pourrait dégrader la disponibilité du service.",
    },
    {
        "concept_key": "api.external_integrations",
        "category": "Spoofing",
        "threat": "Un système tiers usurpé pourrait injecter des données falsifiées via l'intégration.",
    },
    {
        "concept_key": "entities.core_business_objects",
        "category": "Tampering",
        "threat": "Altération non autorisée des objets métier centraux du système.",
    },
    {
        "concept_key": "deployment.target_environment",
        "category": "Denial of Service",
        "threat": "Une infrastructure mal dimensionnée ou mal isolée pourrait être indisponible sous charge ou attaque.",
    },
    {
        "concept_key": "workflow.approval_process",
        "category": "Elevation of Privilege",
        "threat": "Manipulation d'un workflow d'approbation pour forcer une validation sans les privilèges adéquats.",
    },
    {
        "concept_key": "api.external_integrations",
        "category": "Information Disclosure",
        "threat": "Fuite ou exposition non autorisée de données métier sensibles via une API mal sécurisée.",
    },
]


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(kw in lowered for kw in keywords)


def _answer_text(node: KnowledgeGraphNode | None) -> str:
    if not node or not node.captured_data:
        return ""
    return str(node.captured_data.get("raw_answer", ""))


class SecurityEngineService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.analyses = SecurityAnalysisRepository(session)
        self.kg_nodes = KnowledgeGraphNodeRepository(session)
        self.requirements = RequirementRepository(session)

    async def _node_map(self, project_id: uuid.UUID) -> dict[str, KnowledgeGraphNode]:
        nodes = await self.kg_nodes.list_for_project(project_id)
        if not nodes:
            raise NotFoundError("Knowledge graph has not been seeded for this project.")
        return {n.concept_key: n for n in nodes}

    # ------------------------------------------------------------------
    # Threat Model (STRIDE + DREAD)
    # ------------------------------------------------------------------

    def _dread_for(self, node: KnowledgeGraphNode | None) -> dict:
        weight = _RISK_WEIGHT.get(node.risk, 4) if node else 4
        damage = weight
        reproducibility = max(1, weight - 1)
        exploitability = max(1, weight - 2)
        affected_users = weight
        discoverability = max(1, weight - 1)
        total = round(
            (damage + reproducibility + exploitability + affected_users + discoverability) / 5, 1
        )
        return {
            "damage": damage,
            "reproducibility": reproducibility,
            "exploitability": exploitability,
            "affected_users": affected_users,
            "discoverability": discoverability,
            "score": total,
        }

    def _build_threat_model(self, nodes: dict[str, KnowledgeGraphNode]) -> list[dict]:
        threats = []
        for idx, entry in enumerate(_STRIDE_CATALOG, start=1):
            node = nodes.get(entry["concept_key"])
            addressed = bool(node and node.completion >= NODE_SUFFICIENT_THRESHOLD)
            threats.append(
                {
                    "threat_id": f"THR-{idx:03d}",
                    "source_concept_key": entry["concept_key"],
                    "stride_category": entry["category"],
                    "description": entry["threat"],
                    "dread": self._dread_for(node),
                    "status": "mitigation_documented" if addressed else "gap",
                    "mitigation_reference": self._recommendation_for_concept(entry["concept_key"]),
                }
            )
        threats.sort(key=lambda t: t["dread"]["score"], reverse=True)
        return threats

    def _recommendation_for_concept(self, concept_key: str) -> str:
        mapping = {
            "security.authentication_method": "authentication",
            "permissions.matrix": "authorization",
            "security.audit_logging": "audit_logging",
            "beneficiaries.privacy_sensitivity": "encryption",
            "database.existing_systems": "encryption",
            "api.external_integrations": "authentication",
            "entities.core_business_objects": "authorization",
            "deployment.target_environment": "backup_disaster_recovery",
        }
        control_key = mapping.get(concept_key)
        if not control_key:
            return "Documenter et valider ce point avec l'équipe sécurité."
        control = CONTROLS_BY_KEY[control_key]
        return f"Mettre en œuvre : {control.name} — {control.description}"

    # ------------------------------------------------------------------
    # RBAC Matrix
    # ------------------------------------------------------------------

    async def _build_rbac_matrix(self, project_id: uuid.UUID) -> dict:
        requirements = await self.requirements.list_for_project(project_id)
        actors: set[str] = set()
        for r in requirements:
            actors.update(a for a in r.actors if a)

        if not actors:
            actors = {"Utilisateur"}

        actions = ("create", "read", "update", "delete", "export", "administer")
        matrix: dict[str, dict[str, bool]] = {}
        for actor in sorted(actors):
            lowered = actor.lower()
            is_admin = any(k in lowered for k in ("administrateur", "admin", "responsable"))
            is_manager = any(
                k in lowered for k in ("coordinateur", "gestionnaire", "responsable", "sponsor")
            )
            matrix[actor] = {
                "create": is_admin or is_manager,
                "read": True,
                "update": is_admin or is_manager,
                "delete": is_admin,
                "export": is_admin or is_manager,
                "administer": is_admin,
            }
        return {
            "actions": list(actions),
            "roles": matrix,
            "note": (
                "Matrice générée automatiquement à partir des acteurs identifiés dans les "
                "exigences — à valider et affiner avec les propriétaires métier avant mise "
                "en œuvre."
            ),
        }

    # ------------------------------------------------------------------
    # Risk Register
    # ------------------------------------------------------------------

    def _build_risk_register(self, nodes: dict[str, KnowledgeGraphNode]) -> list[dict]:
        risky_nodes = [n for n in nodes.values() if n.risk in ("high", "critical")]
        risky_nodes.sort(
            key=lambda n: (_RISK_WEIGHT.get(n.risk, 0), 100 - n.completion), reverse=True
        )

        register = []
        for idx, node in enumerate(risky_nodes, start=1):
            addressed = node.completion >= NODE_SUFFICIENT_THRESHOLD
            likelihood = "faible" if addressed and node.confidence >= 60 else "élevée"
            register.append(
                {
                    "risk_id": f"R-{idx:03d}",
                    "title": node.label,
                    "domain": node.domain,
                    "description": node.description,
                    "impact": node.risk,
                    "likelihood": likelihood,
                    "risk_score": _RISK_WEIGHT.get(node.risk, 4)
                    * (1 if addressed else 2),
                    "status": "en cours de mitigation" if addressed else "ouvert — non traité",
                    "mitigation": self._recommendation_for_concept(node.concept_key)
                    if node.concept_key in {e["concept_key"] for e in _STRIDE_CATALOG}
                    else f"Clarifier et documenter : {node.label}.",
                    "source_concept_key": node.concept_key,
                }
            )
        return register

    # ------------------------------------------------------------------
    # Security Checklist (automatic gap detection)
    # ------------------------------------------------------------------

    def _check_status(
        self, nodes: dict[str, KnowledgeGraphNode], control_key: str
    ) -> tuple[str, str]:
        """Returns (status, evidence). status in present|partial|missing."""
        auth_node = nodes.get("security.authentication_method")
        authz_node = nodes.get("permissions.matrix")
        audit_node = nodes.get("security.audit_logging")
        dr_node = nodes.get("compliance.disaster_recovery")
        classification_node = nodes.get("security.data_classification")
        privacy_node = nodes.get("beneficiaries.privacy_sensitivity")
        deployment_node = nodes.get("deployment.target_environment")

        if control_key == "authentication":
            if not auth_node or auth_node.completion == 0:
                return "missing", "Aucune méthode d'authentification documentée."
            if auth_node.completion < NODE_SUFFICIENT_THRESHOLD:
                return "partial", "Méthode d'authentification partiellement documentée."
            return "present", _answer_text(auth_node)[:200]

        if control_key == "mfa":
            text = _answer_text(auth_node)
            if not text:
                return "missing", "Authentification non documentée — MFA non évalué."
            if _contains_any(text, _MFA_KEYWORDS):
                return "present", text[:200]
            return "missing", "Aucune mention de MFA/2FA dans la réponse sur l'authentification."

        if control_key == "authorization":
            if not authz_node or authz_node.completion == 0:
                return "missing", "Aucune matrice de permissions documentée."
            if authz_node.completion < NODE_SUFFICIENT_THRESHOLD:
                return "partial", "Matrice de permissions partiellement documentée."
            return "present", _answer_text(authz_node)[:200]

        if control_key == "encryption":
            combined = " ".join(
                _answer_text(n) for n in (classification_node, privacy_node) if n
            )
            if not combined.strip():
                return "missing", "Classification et sensibilité des données non documentées."
            if _contains_any(combined, _ENCRYPTION_KEYWORDS):
                return "present", combined[:200]
            return (
                "partial",
                "Sensibilité des données documentée, mais le chiffrement n'est pas explicitement mentionné.",
            )

        if control_key == "audit_logging":
            if not audit_node or audit_node.completion == 0:
                return "missing", "Aucune exigence de journalisation documentée."
            if audit_node.completion < NODE_SUFFICIENT_THRESHOLD:
                return "partial", "Journalisation partiellement documentée."
            return "present", _answer_text(audit_node)[:200]

        if control_key == "backup_disaster_recovery":
            text = _answer_text(dr_node)
            if dr_node and dr_node.completion >= NODE_SUFFICIENT_THRESHOLD:
                if _contains_any(text, _BACKUP_KEYWORDS) or True:
                    return "present", text[:200]
            if dr_node and dr_node.completion > 0:
                return "partial", "Plan de reprise partiellement documenté."
            return "missing", "Aucun plan de sauvegarde / reprise d'activité documenté."

        if control_key == "secrets_management":
            combined = " ".join(
                _answer_text(n) for n in (deployment_node, auth_node) if n
            )
            if _contains_any(combined, _SECRETS_KEYWORDS):
                return "present", combined[:200]
            return (
                "missing",
                "Aucune gestion des secrets (clés, jetons, identifiants) n'a été mentionnée.",
            )

        if control_key == "data_classification":
            if not classification_node or classification_node.completion == 0:
                return "missing", "Aucune classification des données documentée."
            if classification_node.completion < NODE_SUFFICIENT_THRESHOLD:
                return "partial", "Classification des données partiellement documentée."
            return "present", _answer_text(classification_node)[:200]

        return "missing", "Contrôle non évalué."

    def _build_checklist(self, nodes: dict[str, KnowledgeGraphNode]) -> list[dict]:
        checklist = []
        for control in SECURITY_CONTROLS:
            status, evidence = self._check_status(nodes, control.control_key)
            checklist.append(
                {
                    "control_key": control.control_key,
                    "name": control.name,
                    "status": status,
                    "evidence": evidence,
                    "recommendation": (
                        f"Mettre en œuvre : {control.description}"
                        if status != "present"
                        else "Contrôle en place — maintenir et revalider périodiquement."
                    ),
                    "framework_references": {
                        "owasp_asvs": control.owasp_asvs,
                        "owasp_api_top10": control.owasp_api_top10,
                        "iso_27002": control.iso_27002,
                        "nist_800_53": control.nist_800_53,
                        "cis_controls": control.cis_controls,
                    },
                }
            )
        return checklist

    # ------------------------------------------------------------------
    # Privacy Impact Assessment & Data Classification
    # ------------------------------------------------------------------

    def _build_privacy_impact_assessment(self, nodes: dict[str, KnowledgeGraphNode]) -> dict:
        privacy_node = nodes.get("beneficiaries.privacy_sensitivity")
        regulatory_node = nodes.get("security.regulatory_context")
        retention_node = nodes.get("database.retention_policy")
        definition_node = nodes.get("beneficiaries.definition")

        return {
            "data_subjects": _answer_text(definition_node) or "À préciser.",
            "sensitivity_summary": _answer_text(privacy_node) or "Non évaluée.",
            "regulatory_context": _answer_text(regulatory_node) or "À préciser avec la Direction Juridique.",
            "retention_summary": _answer_text(retention_node) or "Non définie.",
            "legal_basis": (
                "Non déterminé automatiquement — nécessite une validation par la Direction "
                "Juridique / le délégué à la protection des données avant mise en production."
            ),
            "recommended_mitigations": [
                self._recommendation_for_concept("beneficiaries.privacy_sensitivity"),
                "Minimiser la collecte aux seules données nécessaires à l'objectif du projet.",
                "Définir des durées de conservation explicites et un processus de purge.",
            ],
        }

    def _build_data_classification(self, nodes: dict[str, KnowledgeGraphNode]) -> list[dict]:
        privacy_node = nodes.get("beneficiaries.privacy_sensitivity")
        relevant = [
            n for n in nodes.values() if n.domain in ("entities", "database", "beneficiaries")
        ]
        entries = []
        for node in relevant:
            if node.domain == "beneficiaries" or (
                privacy_node and privacy_node.risk in ("high", "critical")
            ):
                level = "Confidentiel" if node.risk != "critical" else "Restreint"
            elif node.domain == "database":
                level = "Interne"
            else:
                level = "Interne"
            entries.append(
                {
                    "entity": node.label,
                    "classification_level": level,
                    "rationale": f"Basé sur le domaine '{node.domain}' et le niveau de risque '{node.risk}'.",
                    "source_concept_key": node.concept_key,
                }
            )
        return entries

    # ------------------------------------------------------------------
    # Aggregate score + orchestration
    # ------------------------------------------------------------------

    def _score(self, checklist: list[dict], risk_register: list[dict]) -> int:
        status_score = {"present": 100, "partial": 50, "missing": 0}
        base = sum(status_score[c["status"]] for c in checklist) / len(checklist)
        open_critical = sum(
            1 for r in risk_register if r["impact"] == "critical" and "ouvert" in r["status"]
        )
        penalty = min(20, open_critical * 3)
        return max(0, round(base - penalty))

    async def analyze(self, project_id: uuid.UUID) -> SecurityAnalysis:
        nodes = await self._node_map(project_id)

        threat_model = self._build_threat_model(nodes)
        rbac_matrix = await self._build_rbac_matrix(project_id)
        risk_register = self._build_risk_register(nodes)
        checklist = self._build_checklist(nodes)
        pia = self._build_privacy_impact_assessment(nodes)
        data_classification = self._build_data_classification(nodes)
        score = self._score(checklist, risk_register)

        existing = await self.analyses.get_for_project(project_id)
        if existing:
            existing.threat_model = threat_model
            existing.rbac_matrix = rbac_matrix
            existing.risk_register = risk_register
            existing.security_checklist = checklist
            existing.privacy_impact_assessment = pia
            existing.data_classification = data_classification
            existing.security_score = score
            await self._sync_project_score(project_id, score)
            await self.session.commit()
            await self.session.refresh(existing)
            return existing

        analysis = SecurityAnalysis(
            project_id=project_id,
            threat_model=threat_model,
            rbac_matrix=rbac_matrix,
            risk_register=risk_register,
            security_checklist=checklist,
            privacy_impact_assessment=pia,
            data_classification=data_classification,
            security_score=score,
        )
        self.session.add(analysis)
        await self._sync_project_score(project_id, score)
        await self.session.commit()
        await self.session.refresh(analysis)
        return analysis

    async def _sync_project_score(self, project_id: uuid.UUID, score: int) -> None:
        from app.models.project import Project

        project = await self.session.get(Project, project_id)
        if project:
            project.security_score = score

    async def get_analysis(self, project_id: uuid.UUID) -> SecurityAnalysis:
        analysis = await self.analyses.get_for_project(project_id)
        if not analysis:
            raise NotFoundError(
                "No security analysis exists yet for this project — run analyze first."
            )
        return analysis
