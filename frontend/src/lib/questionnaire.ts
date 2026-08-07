import type { WizardStep } from "./types";

export const wizardSteps: WizardStep[] = [
  {
    id: "context",
    title: "Contexte Strategique",
    shortTitle: "Contexte",
    description: "Objectifs, perimetre, budget et KPI du projet.",
    questions: [
      {
        id: "business.objective",
        title: "Quel est l'objectif metier principal ?",
        helper: "Le probleme metier a resoudre.",
        type: "textarea",
        required: true,
      },
      {
        id: "business.scope_boundaries",
        title: "Quel est le perimetre fonctionnel et hors-perimetre ?",
        helper: "Ce qui est inclus et explicitement exclu.",
        type: "textarea",
        required: true,
      },
      {
        id: "business.success_metrics",
        title: "Quels sont les indicateurs de succes (KPI) ?",
        helper: "Comment mesurer la reussite du projet.",
        type: "textarea",
      }
    ]
  },
  {
    id: "stakeholders",
    title: "Parties Prenantes",
    shortTitle: "Parties Prenantes",
    description: "Sponsor, decideurs, et comite de pilotage.",
    questions: [
      {
        id: "stakeholders.sponsor",
        title: "Qui est le sponsor du projet ?",
        helper: "Le commanditaire principal.",
        type: "text",
        required: true,
      },
      {
        id: "stakeholders.decision_makers",
        title: "Qui sont les decideurs ?",
        helper: "Membres du comite de pilotage.",
        type: "text",
      },
      {
        id: "stakeholders.departments_involved",
        title: "Quels departements sont impliques ?",
        helper: "Directions concernees par le projet.",
        type: "checkbox",
        options: [
          { id: "opt-agri", label: "Agriculture & Developpement Rural" },
          { id: "opt-edu", label: "Education & Formation" },
          { id: "opt-entre", label: "Entrepreneuriat" },
          { id: "opt-com", label: "Communication & Partenariats" }
        ],
        customPrompt: "Autre departement..."
      }
    ]
  },
  {
    id: "beneficiaries",
    title: "Beneficiaires & Cooperatives",
    shortTitle: "Beneficiaires",
    description: "Definition et sources des beneficiaires.",
    questions: [
      {
        id: "beneficiaries.definition",
        title: "Qui sont les beneficiaires finaux ?",
        helper: "Agriculteurs, cooperatives, etudiants...",
        type: "textarea",
        required: true,
      },
      {
        id: "beneficiaries.data_sources",
        title: "Sources des donnees beneficiaires ?",
        helper: "D'ou proviennent les donnees existantes.",
        type: "textarea",
      },
      {
        id: "beneficiaries.privacy_sensitivity",
        title: "Sensibilite des donnees ?",
        helper: "Niveau de confidentialite (ex: donnees personnelles).",
        type: "radio",
        options: [
          { id: "low", label: "Publique" },
          { id: "medium", label: "Interne" },
          { id: "high", label: "Confidentielle (Donnees personnelles)" }
        ]
      }
    ]
  },
  {
    id: "users_roles",
    title: "Profils Utilisateurs & Roles",
    shortTitle: "Utilisateurs",
    description: "Qui va utiliser l'application.",
    questions: [
      {
        id: "users.primary_personas",
        title: "Quels sont les profils utilisateurs ?",
        helper: "Ceux qui se connectent au systeme.",
        type: "textarea",
        required: true,
      },
      {
        id: "users.access_channels",
        title: "Canaux d'acces ?",
        helper: "Web, Mobile, Tablette, API...",
        type: "checkbox",
        options: [
          { id: "web", label: "Web Desktop" },
          { id: "mobile", label: "Application Mobile" },
          { id: "tablet", label: "Tablette Terrain" }
        ]
      },
      {
        id: "roles.catalog",
        title: "Quels sont les roles specifiques ?",
        helper: "Admin, validateur, lecteur...",
        type: "textarea",
      }
    ]
  },
  {
    id: "permissions",
    title: "Permissions & Habilitations",
    shortTitle: "Permissions",
    description: "Matrice RBAC et visibilite.",
    questions: [
      {
        id: "permissions.matrix",
        title: "Matrice des permissions (RBAC) ?",
        helper: "Qui peut voir/modifier quoi.",
        type: "textarea",
      },
      {
        id: "permissions.data_visibility_scope",
        title: "Portee de visibilite ?",
        helper: "Par region, par departement, globale...",
        type: "textarea",
      }
    ]
  },
  {
    id: "entities_data",
    title: "Entites Metier & Donnees",
    shortTitle: "Entites",
    description: "Structure de donnees et volumetrie.",
    questions: [
      {
        id: "entities.core_business_objects",
        title: "Quels sont les objets metier principaux ?",
        helper: "Dossier, Projet, Beneficiaire, Convention...",
        type: "textarea",
        required: true,
      },
      {
        id: "entities.lifecycle_states",
        title: "Cycle de vie des entites (statuts) ?",
        helper: "Ex: Brouillon, Soumis, Valide, Rejete.",
        type: "textarea",
      },
      {
        id: "database.volume_growth",
        title: "Volumetrie et croissance ?",
        helper: "Nombre d'enregistrements prevus.",
        type: "text",
      }
    ]
  },
  {
    id: "workflow",
    title: "Processus & Workflows",
    shortTitle: "Workflows",
    description: "Processus de validation et approbation.",
    questions: [
      {
        id: "workflow.approval_process",
        title: "Processus d'approbation ?",
        helper: "Circuit de validation des donnees.",
        type: "textarea",
      },
      {
        id: "workflow.task_assignment",
        title: "Assignation des taches ?",
        helper: "Comment les taches sont distribuees.",
        type: "textarea",
      }
    ]
  },
  {
    id: "reporting",
    title: "Reporting & Tableaux de Bord",
    shortTitle: "Reporting",
    description: "Analytique et rapports.",
    questions: [
      {
        id: "reporting.kpis",
        title: "Quels rapports sont necessaires ?",
        helper: "Liste des rapports et tableaux de bord.",
        type: "textarea",
      },
      {
        id: "api.export_requirements",
        title: "Besoins d'export ?",
        helper: "CSV, PDF, Excel...",
        type: "checkbox",
        options: [
          { id: "csv", label: "Export CSV/Excel" },
          { id: "pdf", label: "Export PDF" }
        ]
      }
    ]
  },
  {
    id: "integrations",
    title: "Integrations & API",
    shortTitle: "Integrations",
    description: "Systemes tiers et APIs externes.",
    questions: [
      {
        id: "api.external_integrations",
        title: "Quels systemes externes integrer ?",
        helper: "ERP, CRM, systemes SIG/GIS, etc.",
        type: "textarea",
      },
      {
        id: "database.existing_systems",
        title: "Bases de donnees existantes a integrer ?",
        helper: "Sources de donnees legacy.",
        type: "textarea",
      }
    ]
  },
  {
    id: "notifications",
    title: "Notifications & Messagerie",
    shortTitle: "Notifications",
    description: "Alertes et communication.",
    questions: [
      {
        id: "notifications.channels",
        title: "Canaux de notification ?",
        helper: "Email, SMS, Push, In-app...",
        type: "checkbox",
        options: [
          { id: "email", label: "Email" },
          { id: "sms", label: "SMS" },
          { id: "in_app", label: "In-App" }
        ]
      },
      {
        id: "messaging.internal_communication",
        title: "Messagerie interne ?",
        helper: "Commentaires, chat, annotations.",
        type: "textarea",
      }
    ]
  },
  {
    id: "security",
    title: "Securite & Cybersecurite",
    shortTitle: "Securite",
    description: "Authentification et audit.",
    questions: [
      {
        id: "security.authentication_method",
        title: "Methode d'authentification ?",
        helper: "SSO, Mot de passe, MFA...",
        type: "checkbox",
        options: [
          { id: "sso", label: "SSO Azure AD" },
          { id: "mfa", label: "MFA" },
          { id: "local", label: "Local (Email/Mot de passe)" }
        ]
      },
      {
        id: "security.audit_logging",
        title: "Exigences d'audit (Logs) ?",
        helper: "Quelles actions tracer.",
        type: "textarea",
      }
    ]
  },
  {
    id: "infrastructure",
    title: "Infrastructure & Deploiement",
    shortTitle: "Infrastructure",
    description: "Hebergement et architecture.",
    questions: [
      {
        id: "deployment.target_environment",
        title: "Environnement cible ?",
        helper: "Cloud, On-premise, Hybride...",
        type: "radio",
        options: [
          { id: "cloud", label: "Cloud (AWS/Azure)" },
          { id: "onprem", label: "On-premise (Local)" }
        ]
      },
      {
        id: "deployment.availability_requirements",
        title: "Exigences de disponibilite (SLA) ?",
        helper: "Uptime attendu.",
        type: "text",
      }
    ]
  },
  {
    id: "maintenance",
    title: "Continuite & Maintenance",
    shortTitle: "Maintenance",
    description: "Disaster recovery et backup.",
    questions: [
      {
        id: "compliance.disaster_recovery",
        title: "Plan de reprise d'activite (PRA) ?",
        helper: "Objectifs RTO/RPO.",
        type: "textarea",
      },
      {
        id: "database.retention_policy",
        title: "Politique de retention des donnees ?",
        helper: "Duree de conservation.",
        type: "text",
      }
    ]
  },
  {
    id: "training",
    title: "Formation & Documentation",
    shortTitle: "Formation",
    description: "Besoins en formation et manuels.",
    questions: [
      {
        id: "training.needs",
        title: "Besoins en formation ?",
        helper: "Formations utilisateurs et admins.",
        type: "textarea",
      },
      {
        id: "testing.uat_stakeholders",
        title: "Parties prenantes UAT ?",
        helper: "Qui valide la recette fonctionnelle.",
        type: "textarea",
      }
    ]
  },
  {
    id: "compliance",
    title: "Conformite & Legal",
    shortTitle: "Conformite",
    description: "Lois et regulations.",
    questions: [
      {
        id: "security.regulatory_context",
        title: "Cadre reglementaire (Loi 09-08, RGPD) ?",
        helper: "Quelles lois s'appliquent.",
        type: "textarea",
      },
      {
        id: "compliance.internal_policies",
        title: "Politiques internes applicables ?",
        helper: "Chartes informatiques et qualite.",
        type: "textarea",
      }
    ]
  }
];
