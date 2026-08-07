"""The concept catalog is the *ontology*, not a questionnaire.

Each entry describes a concept the system needs to understand about a
project — its label, description, dependencies on other concepts,
importance, business value, and risk — but not any fixed question
text. Question text is generated at runtime by the Interview Engine
from a node's current state (see app/services/question_generation.py),
so the same concept can be asked about in different words depending on
what's already known, what's missing, and what the person said before.

This is what "Knowledge as interconnected concepts" means in practice:
a directed graph of concepts with dependencies, not a flat list of
questions. Adding a new concept here extends what the system can
reason about; it does not hardcode how it asks about it.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ConceptDefinition:
    key: str
    domain: str
    label: str
    description: str
    depends_on: tuple[str, ...] = field(default_factory=tuple)
    importance: str = "medium"  # low | medium | high | critical
    business_value: int = 50  # 0-100
    risk: str = "medium"  # low | medium | high | critical
    validation_rules: tuple[str, ...] = field(default_factory=tuple)


CONCEPT_CATALOG: tuple[ConceptDefinition, ...] = (
    # --- Business ---
    ConceptDefinition(
        key="business.objective",
        domain="business",
        label="Objectif métier principal",
        description="La raison d'être du projet: quel problème métier il résout et pour qui.",
        importance="critical", business_value=100, risk="high",
        validation_rules=("must_be_non_empty", "must_reference_a_measurable_outcome"),
    ),
    ConceptDefinition(
        key="business.success_metrics",
        domain="business",
        label="Indicateurs de succès",
        description="Comment le succès du projet sera mesuré (KPIs, cibles chiffrées).",
        depends_on=("business.objective",),
        importance="high", business_value=90, risk="medium",
        validation_rules=("must_be_measurable",),
    ),
    ConceptDefinition(
        key="business.scope_boundaries",
        domain="business",
        label="Périmètre et hors-périmètre",
        description="Ce que le projet couvre explicitement, et ce qu'il exclut.",
        depends_on=("business.objective",),
        importance="high", business_value=80, risk="high",
    ),
    ConceptDefinition(
        key="business.budget_constraints",
        domain="business",
        label="Contraintes budgétaires",
        description="Budget disponible, contraintes de coût, modèle de financement.",
        depends_on=("business.objective",),
        importance="medium", business_value=60, risk="medium",
    ),
    ConceptDefinition(
        key="business.timeline",
        domain="business",
        label="Échéancier",
        description="Dates clés, jalons, contraintes de calendrier.",
        depends_on=("business.objective",),
        importance="medium", business_value=60, risk="medium",
    ),

    # --- Stakeholders ---
    ConceptDefinition(
        key="stakeholders.sponsor",
        domain="stakeholders",
        label="Sponsor / commanditaire",
        description="Qui porte le projet côté direction et prend les décisions finales.",
        depends_on=("business.objective",),
        importance="critical", business_value=80, risk="high",
    ),
    ConceptDefinition(
        key="stakeholders.decision_makers",
        domain="stakeholders",
        label="Décideurs et comité de pilotage",
        description="Qui valide les livrables et arbitre les priorités.",
        depends_on=("stakeholders.sponsor",),
        importance="high", business_value=70, risk="medium",
    ),
    ConceptDefinition(
        key="stakeholders.departments_involved",
        domain="stakeholders",
        label="Directions et services impliqués",
        description="Quelles directions internes sont concernées par le projet.",
        depends_on=("business.objective",),
        importance="medium", business_value=60, risk="low",
    ),

    # --- Users ---
    ConceptDefinition(
        key="users.primary_personas",
        domain="users",
        label="Profils utilisateurs principaux",
        description="Qui utilisera le système au quotidien, et pour quoi faire.",
        depends_on=("business.objective",),
        importance="critical", business_value=90, risk="high",
    ),
    ConceptDefinition(
        key="users.access_channels",
        domain="users",
        label="Canaux d'accès",
        description="Web, mobile, API, guichet physique — comment les utilisateurs accèdent au système.",
        depends_on=("users.primary_personas",),
        importance="medium", business_value=60, risk="medium",
    ),
    ConceptDefinition(
        key="users.volume_estimate",
        domain="users",
        label="Volumétrie utilisateurs",
        description="Nombre d'utilisateurs attendus, pics de charge prévisibles.",
        depends_on=("users.primary_personas",),
        importance="medium", business_value=50, risk="medium",
        validation_rules=("must_be_numeric_or_range",),
    ),

    # --- Beneficiaries ---
    ConceptDefinition(
        key="beneficiaries.definition",
        domain="beneficiaries",
        label="Définition des bénéficiaires",
        description="Qui sont les bénéficiaires finaux du programme (distincts des utilisateurs du système).",
        depends_on=("business.objective",),
        importance="high", business_value=90, risk="high",
    ),
    ConceptDefinition(
        key="beneficiaries.data_sources",
        domain="beneficiaries",
        label="Sources des données bénéficiaires",
        description="D'où proviennent les données existantes sur les bénéficiaires (systèmes sources, formats).",
        depends_on=("beneficiaries.definition",),
        importance="critical", business_value=85, risk="high",
    ),
    ConceptDefinition(
        key="beneficiaries.privacy_sensitivity",
        domain="beneficiaries",
        label="Sensibilité des données bénéficiaires",
        description="Niveau de sensibilité et de confidentialité des données bénéficiaires collectées.",
        depends_on=("beneficiaries.definition",),
        importance="critical", business_value=70, risk="critical",
    ),

    # --- Roles ---
    ConceptDefinition(
        key="roles.catalog",
        domain="roles",
        label="Catalogue des rôles",
        description="Les rôles distincts qui interagiront avec le système (ex: administrateur, coordinateur régional).",
        depends_on=("users.primary_personas",),
        importance="critical", business_value=80, risk="high",
    ),
    ConceptDefinition(
        key="roles.hierarchy",
        domain="roles",
        label="Hiérarchie et délégation entre rôles",
        description="Comment les rôles s'organisent entre eux (délégation, supervision, escalade).",
        depends_on=("roles.catalog",),
        importance="medium", business_value=55, risk="medium",
    ),

    # --- Permissions ---
    ConceptDefinition(
        key="permissions.matrix",
        domain="permissions",
        label="Matrice des permissions",
        description="Quel rôle peut faire quoi sur quelle donnée (lecture, écriture, export, administration).",
        depends_on=("roles.catalog",),
        importance="critical", business_value=75, risk="critical",
    ),
    ConceptDefinition(
        key="permissions.data_visibility_scope",
        domain="permissions",
        label="Portée de visibilité des données",
        description="Restrictions de visibilité par région, entité, ou périmètre organisationnel.",
        depends_on=("permissions.matrix",),
        importance="high", business_value=65, risk="high",
    ),

    # --- Entities ---
    ConceptDefinition(
        key="entities.core_business_objects",
        domain="entities",
        label="Objets métier principaux",
        description="Les entités centrales du domaine (ex: bénéficiaire, projet, exploitation, dossier).",
        depends_on=("business.objective",),
        importance="critical", business_value=85, risk="medium",
    ),
    ConceptDefinition(
        key="entities.relationships",
        domain="entities",
        label="Relations entre entités",
        description="Comment les entités principales se relient entre elles (cardinalités, dépendances).",
        depends_on=("entities.core_business_objects",),
        importance="high", business_value=70, risk="medium",
    ),
    ConceptDefinition(
        key="entities.lifecycle_states",
        domain="entities",
        label="États et cycle de vie",
        description="Les statuts possibles des entités principales et les transitions autorisées.",
        depends_on=("entities.core_business_objects",),
        importance="medium", business_value=55, risk="medium",
    ),

    # --- Database ---
    ConceptDefinition(
        key="database.existing_systems",
        domain="database",
        label="Systèmes de données existants",
        description="Bases de données ou systèmes existants à intégrer ou migrer.",
        depends_on=("entities.core_business_objects",),
        importance="high", business_value=70, risk="high",
    ),
    ConceptDefinition(
        key="database.retention_policy",
        domain="database",
        label="Politique de rétention des données",
        description="Durée de conservation requise, règles d'archivage et de suppression.",
        depends_on=("entities.core_business_objects",),
        importance="medium", business_value=50, risk="high",
    ),
    ConceptDefinition(
        key="database.volume_growth",
        domain="database",
        label="Volumétrie et croissance",
        description="Volume actuel et projeté des données, taux de croissance attendu.",
        depends_on=("entities.core_business_objects",),
        importance="medium", business_value=45, risk="medium",
    ),

    # --- API ---
    ConceptDefinition(
        key="api.external_integrations",
        domain="api",
        label="Intégrations externes requises",
        description="Systèmes tiers avec lesquels le système doit échanger des données.",
        depends_on=("entities.core_business_objects",),
        importance="high", business_value=65, risk="high",
    ),
    ConceptDefinition(
        key="api.export_requirements",
        domain="api",
        label="Besoins d'export de données",
        description="Formats et fréquences d'export attendus (rapports, extractions, API publique).",
        depends_on=("entities.core_business_objects",),
        importance="medium", business_value=60, risk="medium",
    ),

    # --- Security ---
    ConceptDefinition(
        key="security.authentication_method",
        domain="security",
        label="Méthode d'authentification",
        description="Comment les utilisateurs s'authentifient (SSO, MFA, annuaire d'entreprise).",
        depends_on=("roles.catalog",),
        importance="critical", business_value=60, risk="critical",
    ),
    ConceptDefinition(
        key="security.data_classification",
        domain="security",
        label="Classification des données",
        description="Niveau de sensibilité des différentes catégories de données traitées.",
        depends_on=("beneficiaries.privacy_sensitivity",),
        importance="critical", business_value=55, risk="critical",
    ),
    ConceptDefinition(
        key="security.audit_logging",
        domain="security",
        label="Journalisation et audit",
        description="Ce qui doit être tracé (accès, modifications, exports) et pour combien de temps.",
        depends_on=("security.authentication_method",),
        importance="high", business_value=50, risk="high",
    ),
    ConceptDefinition(
        key="security.regulatory_context",
        domain="security",
        label="Cadre réglementaire applicable",
        description="Lois et réglementations applicables (protection des données, secteur d'activité).",
        depends_on=("beneficiaries.privacy_sensitivity",),
        importance="critical", business_value=50, risk="critical",
    ),

    # --- Deployment ---
    ConceptDefinition(
        key="deployment.target_environment",
        domain="deployment",
        label="Environnement cible",
        description="Cloud, on-premise, hybride — et contraintes de souveraineté des données.",
        depends_on=("database.existing_systems",),
        importance="high", business_value=55, risk="high",
    ),
    ConceptDefinition(
        key="deployment.availability_requirements",
        domain="deployment",
        label="Exigences de disponibilité",
        description="SLA attendu, fenêtres de maintenance tolérées, tolérance à la panne.",
        depends_on=("deployment.target_environment",),
        importance="medium", business_value=55, risk="medium",
    ),

    # --- Testing ---
    ConceptDefinition(
        key="testing.acceptance_criteria",
        domain="testing",
        label="Critères d'acceptation généraux",
        description="Comment le projet sera validé avant mise en production.",
        depends_on=("business.success_metrics",),
        importance="medium", business_value=55, risk="medium",
    ),
    ConceptDefinition(
        key="testing.uat_stakeholders",
        domain="testing",
        label="Parties prenantes des tests utilisateurs",
        description="Qui participera à la recette fonctionnelle (UAT).",
        depends_on=("testing.acceptance_criteria",),
        importance="low", business_value=40, risk="low",
    ),

    # --- Training ---
    ConceptDefinition(
        key="training.needs",
        domain="training",
        label="Besoins de formation",
        description="Quels profils devront être formés, et à quel niveau.",
        depends_on=("roles.catalog",),
        importance="low", business_value=40, risk="low",
    ),

    # --- Monitoring ---
    ConceptDefinition(
        key="monitoring.operational_metrics",
        domain="monitoring",
        label="Métriques opérationnelles à surveiller",
        description="Ce qui doit être surveillé une fois en production (performance, erreurs, usage).",
        depends_on=("deployment.target_environment",),
        importance="medium", business_value=50, risk="medium",
    ),
    ConceptDefinition(
        key="monitoring.alerting_thresholds",
        domain="monitoring",
        label="Seuils d'alerte",
        description="Conditions déclenchant une alerte et qui doit être notifié.",
        depends_on=("monitoring.operational_metrics",),
        importance="low", business_value=40, risk="medium",
    ),

    # --- Compliance ---
    ConceptDefinition(
        key="compliance.internal_policies",
        domain="compliance",
        label="Politiques internes applicables",
        description="Politiques internes de gouvernance, sécurité, ou qualité à respecter.",
        depends_on=("security.regulatory_context",),
        importance="medium", business_value=45, risk="high",
    ),
    ConceptDefinition(
        key="compliance.disaster_recovery",
        domain="compliance",
        label="Plan de reprise d'activité",
        description="Exigences de sauvegarde et de reprise après sinistre.",
        depends_on=("deployment.target_environment",),
        importance="medium", business_value=45, risk="critical",
    ),

    # --- Workflows ---
    ConceptDefinition(
        key="workflow.approval_process",
        domain="workflow",
        label="Processus d'approbation",
        description="Circuit de validation des donnees et des decisions.",
        depends_on=("roles.catalog",),
        importance="high", business_value=70, risk="medium",
    ),
    ConceptDefinition(
        key="workflow.task_assignment",
        domain="workflow",
        label="Assignation des taches",
        description="Mecanisme de distribution et suivi des taches.",
        depends_on=("workflow.approval_process",),
        importance="medium", business_value=60, risk="low",
    ),
    ConceptDefinition(
        key="workflow.version_history",
        domain="workflow",
        label="Historique des versions",
        description="Suivi des modifications et versions des entites.",
        depends_on=("entities.core_business_objects",),
        importance="medium", business_value=50, risk="medium",
    ),

    # --- Notifications & Messaging ---
    ConceptDefinition(
        key="notifications.channels",
        domain="notifications",
        label="Canaux de notification",
        description="Email, SMS, Push, In-app et leurs cas d'usage.",
        depends_on=("users.primary_personas",),
        importance="medium", business_value=55, risk="low",
    ),
    ConceptDefinition(
        key="notifications.escalation",
        domain="notifications",
        label="Regles d'escalade",
        description="Que faire si une tache ou notification n'est pas traitee.",
        depends_on=("notifications.channels",),
        importance="medium", business_value=50, risk="medium",
    ),
    ConceptDefinition(
        key="messaging.internal_communication",
        domain="messaging",
        label="Messagerie interne",
        description="Chat, commentaires ou annotations sur les objets metier.",
        depends_on=("entities.core_business_objects",),
        importance="low", business_value=40, risk="low",
    ),

    # --- Reporting & Documents ---
    ConceptDefinition(
        key="reporting.kpis",
        domain="reporting",
        label="KPIs et Indicateurs",
        description="Indicateurs de performance a afficher dans les tableaux de bord.",
        depends_on=("business.success_metrics",),
        importance="high", business_value=80, risk="low",
    ),
    ConceptDefinition(
        key="reporting.dashboard_design",
        domain="reporting",
        label="Conception des tableaux de bord",
        description="Organisation visuelle et audience des tableaux de bord.",
        depends_on=("reporting.kpis",),
        importance="medium", business_value=60, risk="low",
    ),
    ConceptDefinition(
        key="reporting.document_upload",
        domain="reporting",
        label="Gestion documentaire",
        description="Upload, stockage et cycle de vie des pieces jointes.",
        depends_on=("entities.core_business_objects",),
        importance="high", business_value=60, risk="medium",
    ),

    # --- Compliance & Legal ---
    ConceptDefinition(
        key="compliance.rgpd",
        domain="compliance",
        label="Conformite RGPD",
        description="Exigences de protection des donnees personnelles (UE).",
        depends_on=("security.regulatory_context",),
        importance="critical", business_value=50, risk="critical",
    ),
    ConceptDefinition(
        key="compliance.law_09_08",
        domain="compliance",
        label="Loi 09-08 (Maroc)",
        description="Protection des donnees a caractere personnel au Maroc.",
        depends_on=("security.regulatory_context",),
        importance="critical", business_value=50, risk="critical",
    ),
    ConceptDefinition(
        key="compliance.audit_trail",
        domain="compliance",
        label="Piste d'audit",
        description="Tracabilite legale des actions sur les donnees sensibles.",
        depends_on=("compliance.law_09_08",),
        importance="high", business_value=45, risk="high",
    ),
    ConceptDefinition(
        key="legal.data_processing_agreements",
        domain="legal",
        label="Accords de traitement de donnees (DPA)",
        description="Contrats avec les sous-traitants traitant des donnees.",
        depends_on=("compliance.law_09_08",),
        importance="medium", business_value=40, risk="high",
    ),
    ConceptDefinition(
        key="legal.retention_policies",
        domain="legal",
        label="Politiques de retention legales",
        description="Duree de conservation imposee par la loi.",
        depends_on=("compliance.law_09_08",),
        importance="medium", business_value=40, risk="high",
    ),

    # --- Advanced Security ---
    ConceptDefinition(
        key="security.incident_response",
        domain="security",
        label="Reponse aux incidents",
        description="Procedures en cas de violation de donnees ou cyberattaque.",
        depends_on=("security.data_classification",),
        importance="high", business_value=40, risk="critical",
    ),
    ConceptDefinition(
        key="security.sdlc",
        domain="security",
        label="Securite dans le SDLC",
        description="Pratiques DevSecOps (SAST, DAST, pentests).",
        depends_on=("deployment.target_environment",),
        importance="medium", business_value=45, risk="medium",
    ),

    # --- Infrastructure & Mobile ---
    ConceptDefinition(
        key="infrastructure.scalability",
        domain="infrastructure",
        label="Exigences de scalabilite",
        description="Capacite a gerer les pics de charge et la croissance.",
        depends_on=("database.volume_growth",),
        importance="high", business_value=60, risk="high",
    ),
    ConceptDefinition(
        key="infrastructure.offline_mode",
        domain="infrastructure",
        label="Mode hors-ligne",
        description="Capacite a fonctionner sans connexion internet (synchronisation).",
        depends_on=("users.access_channels",),
        importance="medium", business_value=70, risk="high",
    ),
    ConceptDefinition(
        key="mobile.requirements",
        domain="mobile",
        label="Exigences specifiques Mobile",
        description="Besoins propres aux applications mobiles (geolocalisation, push).",
        depends_on=("users.access_channels",),
        importance="medium", business_value=60, risk="medium",
    ),
    ConceptDefinition(
        key="accessibility.wcag",
        domain="accessibility",
        label="Accessibilite (WCAG)",
        description="Niveau d'accessibilite requis pour les utilisateurs en situation de handicap.",
        depends_on=("users.primary_personas",),
        importance="medium", business_value=50, risk="medium",
    ),

    # --- Maintenance & Training ---
    ConceptDefinition(
        key="maintenance.backup_strategy",
        domain="maintenance",
        label="Strategie de sauvegarde",
        description="Frequence, type et duree de retention des backups.",
        depends_on=("compliance.disaster_recovery",),
        importance="high", business_value=40, risk="critical",
    ),
    ConceptDefinition(
        key="maintenance.monitoring",
        domain="maintenance",
        label="Surveillance proactive",
        description="Outils et processus pour detecter les anomalies avant impact.",
        depends_on=("monitoring.operational_metrics",),
        importance="medium", business_value=45, risk="medium",
    ),
    ConceptDefinition(
        key="training.plan",
        domain="training",
        label="Plan de formation",
        description="Organisation, supports et planning des formations.",
        depends_on=("training.needs",),
        importance="medium", business_value=60, risk="low",
    ),
    ConceptDefinition(
        key="training.documentation_lifecycle",
        domain="training",
        label="Cycle de vie documentaire",
        description="Mise a jour et maintenance des manuels utilisateurs.",
        depends_on=("training.plan",),
        importance="low", business_value=40, risk="low",
    ),
)


CONCEPT_BY_KEY: dict[str, ConceptDefinition] = {c.key: c for c in CONCEPT_CATALOG}


def validate_catalog() -> None:
    """Fails fast at import time if the ontology itself is inconsistent —
    every dependency must point at a concept that actually exists, and
    there must be no cycles (dependencies form a DAG)."""
    for concept in CONCEPT_CATALOG:
        for dep in concept.depends_on:
            if dep not in CONCEPT_BY_KEY:
                raise ValueError(
                    f"Concept '{concept.key}' depends on unknown concept '{dep}'"
                )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(key: str) -> None:
        if key in visited:
            return
        if key in visiting:
            raise ValueError(f"Cycle detected in concept catalog involving '{key}'")
        visiting.add(key)
        for dep in CONCEPT_BY_KEY[key].depends_on:
            visit(dep)
        visiting.discard(key)
        visited.add(key)

    for concept in CONCEPT_CATALOG:
        visit(concept.key)


validate_catalog()
