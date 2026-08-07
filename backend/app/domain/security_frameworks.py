"""Maps each internal security control check to where it sits in major
public frameworks. This is a *reference mapping* at the category/family
level using well-established, publicly documented identifiers (e.g.
NIST 800-53's IA family is genuinely "Identification and
Authentication"; ISO 27002 Annex A.9 is genuinely "Access control").
It is deliberately NOT a claim of full ASVS/MASVS/ISO 27001/NIST
800-53/CIS Controls coverage or a certified compliance audit — that
would require a real audit against the actual control text, which this
engine doesn't attempt. Treat this as a starting point for a real
security review, not a substitute for one.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ControlMapping:
    control_key: str
    name: str
    description: str
    owasp_asvs: str
    owasp_api_top10: str | None
    iso_27002: str
    nist_800_53: str
    cis_controls: str
    linddun_categories: tuple[str, ...] = field(default_factory=tuple)


SECURITY_CONTROLS: tuple[ControlMapping, ...] = (
    ControlMapping(
        control_key="authentication",
        name="Authentification",
        description="Mécanisme de vérification de l'identité des utilisateurs.",
        owasp_asvs="V2 — Authentication",
        owasp_api_top10="API2:2023 — Broken Authentication",
        iso_27002="A.5.17 / A.8.5 — Authentication information",
        nist_800_53="IA family — Identification and Authentication",
        cis_controls="CIS Control 6 — Access Control Management",
        linddun_categories=("Linkability", "Identifiability"),
    ),
    ControlMapping(
        control_key="mfa",
        name="Authentification multifacteur",
        description="Facteur d'authentification supplémentaire au-delà du mot de passe.",
        owasp_asvs="V2.2 — General Authenticator Requirements",
        owasp_api_top10="API2:2023 — Broken Authentication",
        iso_27002="A.8.5 — Secure authentication",
        nist_800_53="IA-2(1) — Multi-factor authentication",
        cis_controls="CIS Control 6.5 — MFA for administrative access",
    ),
    ControlMapping(
        control_key="authorization",
        name="Autorisation (RBAC)",
        description="Contrôle d'accès basé sur les rôles pour restreindre les actions autorisées.",
        owasp_asvs="V4 — Access Control",
        owasp_api_top10="API1:2023 — Broken Object Level Authorization / API5:2023 — Broken Function Level Authorization",
        iso_27002="A.8.3 — Information access restriction",
        nist_800_53="AC family — Access Control",
        cis_controls="CIS Control 6 — Access Control Management",
        linddun_categories=("Non-repudiation", "Detectability"),
    ),
    ControlMapping(
        control_key="encryption",
        name="Chiffrement des données",
        description="Protection des données sensibles au repos et en transit.",
        owasp_asvs="V9 — Communications / V6 — Stored Cryptography",
        owasp_api_top10="API8:2023 — Security Misconfiguration",
        iso_27002="A.8.24 — Use of cryptography",
        nist_800_53="SC-13 / SC-28 — Cryptographic Protection",
        cis_controls="CIS Control 3 — Data Protection",
        linddun_categories=("Disclosure of information",),
    ),
    ControlMapping(
        control_key="audit_logging",
        name="Journalisation et audit",
        description="Traçabilité des accès et modifications pour détection et investigation.",
        owasp_asvs="V7 — Error Handling and Logging",
        owasp_api_top10="API9:2023 — Improper Inventory Management",
        iso_27002="A.8.15 — Logging",
        nist_800_53="AU family — Audit and Accountability",
        cis_controls="CIS Control 8 — Audit Log Management",
        linddun_categories=("Non-repudiation", "Detectability"),
    ),
    ControlMapping(
        control_key="backup_disaster_recovery",
        name="Sauvegarde et reprise d'activité",
        description="Capacité à restaurer le service et les données après un incident.",
        owasp_asvs="V1 — Architecture, Design and Threat Modeling",
        owasp_api_top10=None,
        iso_27002="A.8.13 — Information backup",
        nist_800_53="CP family — Contingency Planning",
        cis_controls="CIS Control 11 — Data Recovery",
    ),
    ControlMapping(
        control_key="secrets_management",
        name="Gestion des secrets",
        description="Stockage, rotation et accès contrôlé aux clés, jetons et identifiants.",
        owasp_asvs="V6 — Stored Cryptography",
        owasp_api_top10="API8:2023 — Security Misconfiguration",
        iso_27002="A.8.24 — Use of cryptography",
        nist_800_53="IA-5 — Authenticator Management",
        cis_controls="CIS Control 3 — Data Protection",
    ),
    ControlMapping(
        control_key="data_classification",
        name="Classification des données",
        description="Catégorisation des données par niveau de sensibilité pour appliquer des contrôles proportionnés.",
        owasp_asvs="V8 — Data Protection",
        owasp_api_top10=None,
        iso_27002="A.5.12 — Classification of information",
        nist_800_53="RA-2 — Security Categorization",
        cis_controls="CIS Control 3 — Data Protection",
        linddun_categories=("Disclosure of information",),
    ),
)

CONTROLS_BY_KEY = {c.control_key: c for c in SECURITY_CONTROLS}
