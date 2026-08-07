"""Maps Knowledge Graph domains to requirement types, and each concept
to a small set of deterministic requirement templates. This is the
"knowledge -> requirement" derivation rule set — not questions, not
requirement text itself, just the structural mapping the Requirement
Engine uses to turn a sufficiently-answered concept into one or more
traceable requirements.
"""
from dataclasses import dataclass, field

REQUIREMENT_TYPES = (
    "business", "functional", "non_functional", "security", "technical",
    "infrastructure", "deployment", "maintenance", "training", "performance",
    "accessibility",
)

# One judgment call worth documenting: "testing" isn't its own requirement
# type in the spec's list, so testing/acceptance concepts are filed under
# "maintenance" (they govern how the system is verified and kept correct
# over time) and monitoring concepts under "non_functional" (operational
# qualities of the running system).
DOMAIN_TO_REQUIREMENT_TYPE: dict[str, str] = {
    "business": "business",
    "stakeholders": "business",
    "users": "functional",
    "beneficiaries": "functional",
    "roles": "functional",
    "permissions": "security",
    "entities": "technical",
    "database": "technical",
    "api": "technical",
    "security": "security",
    "deployment": "deployment",
    "testing": "maintenance",
    "training": "training",
    "monitoring": "non_functional",
    "compliance": "security",
    "workflow": "functional",
    "notifications": "functional",
    "messaging": "functional",
    "reporting": "functional",
    "legal": "business",
    "infrastructure": "infrastructure",
    "mobile": "functional",
    "accessibility": "accessibility",
}


@dataclass(frozen=True)
class RequirementTemplate:
    """Describes how to derive a requirement from a concept once its
    node is sufficiently answered. Text fields are templates filled in
    with the node's label/description/captured answer at generation
    time — the actual requirement wording still reflects what the
    person said, it isn't invented from nothing.
    """

    title_template: str  # may reference {label}
    default_priority: str  # low | medium | high | critical
    default_actors: tuple[str, ...] = field(default_factory=tuple)
    default_security_controls: tuple[str, ...] = field(default_factory=tuple)
    default_test_case_hints: tuple[str, ...] = field(default_factory=tuple)


# Per-concept overrides; concepts not listed here fall back to a generic
# template derived purely from domain + importance (see requirement.py).
CONCEPT_REQUIREMENT_TEMPLATES: dict[str, RequirementTemplate] = {
    "security.authentication_method": RequirementTemplate(
        title_template="Authentification des utilisateurs — {label}",
        default_priority="critical",
        default_actors=("Utilisateur", "Administrateur systeme"),
        default_security_controls=("MFA", "Gestion des sessions", "Politique de mot de passe"),
        default_test_case_hints=("Connexion reussie", "Connexion echouee", "Expiration de session"),
    ),
    "permissions.matrix": RequirementTemplate(
        title_template="Controle d'acces base sur les roles — {label}",
        default_priority="critical",
        default_actors=("Administrateur", "Tous roles definis"),
        default_security_controls=("RBAC", "Journalisation des acces"),
        default_test_case_hints=("Acces autorise par role", "Acces refuse hors perimetre"),
    ),
    "security.audit_logging": RequirementTemplate(
        title_template="Journalisation et audit — {label}",
        default_priority="high",
        default_actors=("Administrateur", "Auditeur"),
        default_security_controls=("Logs immuables", "Retention des journaux"),
    ),
    "beneficiaries.privacy_sensitivity": RequirementTemplate(
        title_template="Protection des donnees beneficiaires — {label}",
        default_priority="critical",
        default_actors=("Responsable donnees", "Beneficiaire"),
        default_security_controls=("Chiffrement au repos", "Chiffrement en transit", "Anonymisation"),
    ),
    "compliance.disaster_recovery": RequirementTemplate(
        title_template="Plan de reprise d'activite — {label}",
        default_priority="high",
        default_actors=("Equipe infrastructure",),
        default_security_controls=("Sauvegardes regulieres", "Tests de restauration"),
    ),
}


def default_template_for(domain: str, importance: str) -> RequirementTemplate:
    priority = {"low": "low", "medium": "medium", "high": "high", "critical": "critical"}.get(
        importance, "medium"
    )
    return RequirementTemplate(
        title_template="{label}",
        default_priority=priority,
    )
