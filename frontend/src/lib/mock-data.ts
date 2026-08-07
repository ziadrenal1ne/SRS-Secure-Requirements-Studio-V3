import type {
  Project,
  ActivityItem,
  NotificationItem,
  WizardStep,
  DocumentSection,
  AdminSubmission,
} from "./types";

// ---------------------------------------------------------------------------
// Projects
// ---------------------------------------------------------------------------

export const mainProject: Project = {
  id: "pgb-almoutmir",
  name: "Plateforme de Gestion des Bénéficiaires — Programme Al Moutmir",
  shortName: "PGB Al Moutmir",
  department: "Direction Agriculture & Développement Rural",
  owner: { name: "Salma Idrissi", role: "Cheffe de Programme Al Moutmir", initials: "SI" },
  status: "en_cours",
  progress: 68,
  securityScore: 82,
  createdAt: "2026-05-04T09:12:00",
  updatedAt: "2026-07-14T16:40:00",
  description:
    "Application interne destinée à recenser, suivre et accompagner les agriculteurs bénéficiaires du programme Al Moutmir, depuis leur inscription jusqu'au suivi post-campagne, avec remontée terrain via les techniciens régionaux.",
  modules: [
    { id: "mod-1", name: "Inscription des bénéficiaires", description: "Recensement des agriculteurs, pièces justificatives et validation par les coordinateurs régionaux." },
    { id: "mod-2", name: "Suivi des parcelles & campagnes", description: "Cartographie des parcelles, historique des campagnes agricoles et indicateurs de rendement." },
    { id: "mod-3", name: "Distribution des intrants", description: "Gestion des lots de semences et engrais distribués, traçabilité par bénéficiaire." },
    { id: "mod-4", name: "Reporting & tableaux de bord", description: "Génération de rapports régionaux et nationaux pour la direction du programme." },
    { id: "mod-5", name: "Gestion documentaire", description: "Centralisation des pièces d'identité, attestations foncières et rapports terrain." },
  ],
  roles: [
    { id: "role-1", name: "Agriculteur bénéficiaire", description: "Accès à son dossier personnel et à l'historique de ses campagnes.", permissions: ["Consulter son dossier", "Téléverser des documents", "Suivre les distributions reçues"] },
    { id: "role-2", name: "Technicien terrain", description: "Saisie terrain et mise à jour des données de parcelles.", permissions: ["Créer une fiche bénéficiaire", "Saisir les visites terrain", "Téléverser des photos de parcelles"] },
    { id: "role-3", name: "Coordinateur régional", description: "Validation des inscriptions et supervision d'une région.", permissions: ["Valider les inscriptions", "Consulter les rapports régionaux", "Gérer les distributions d'intrants"] },
    { id: "role-4", name: "Administrateur Fondation", description: "Accès complet, configuration et pilotage national du programme.", permissions: ["Gérer les utilisateurs", "Configurer les campagnes", "Exporter les données nationales", "Consulter les journaux d'audit"] },
  ],
  estimatedRequirements: 47,
  tags: ["Agriculture", "Bénéficiaires", "Terrain", "Mobile"],
};

export const projects: Project[] = [
  mainProject,
  {
    id: "boursiers-ocp",
    name: "Suivi des Boursiers — Fondation OCP",
    shortName: "Suivi des Boursiers",
    department: "Direction Éducation & Formation",
    owner: { name: "Yassine Bennani", role: "Responsable Programme Bourses", initials: "YB" },
    status: "valide",
    progress: 100,
    securityScore: 91,
    createdAt: "2026-02-11T10:00:00",
    updatedAt: "2026-06-02T11:20:00",
    description: "Suivi du parcours académique des étudiants boursiers, versements et évaluations annuelles.",
    modules: [
      { id: "mod-1", name: "Dossiers boursiers", description: "Gestion des dossiers académiques et administratifs." },
      { id: "mod-2", name: "Versements", description: "Suivi des échéances de bourses." },
    ],
    roles: [
      { id: "role-1", name: "Boursier", description: "Consultation de son dossier.", permissions: ["Consulter son dossier"] },
      { id: "role-2", name: "Gestionnaire bourses", description: "Gestion des versements.", permissions: ["Valider les versements"] },
    ],
    estimatedRequirements: 32,
    tags: ["Éducation", "Finance"],
  },
  {
    id: "reseau-reussite",
    name: "Portail Entrepreneuriat Rural — Réseau Réussite",
    shortName: "Réseau Réussite",
    department: "Direction Entrepreneuriat",
    owner: { name: "Nadia Berrada", role: "Cheffe de Projet Entrepreneuriat", initials: "NB" },
    status: "en_revue",
    progress: 84,
    securityScore: 76,
    createdAt: "2026-04-01T08:30:00",
    updatedAt: "2026-07-10T14:10:00",
    description: "Portail d'accompagnement des jeunes entrepreneurs ruraux : dépôt de projets, mentorat et financement.",
    modules: [
      { id: "mod-1", name: "Dépôt de projets", description: "Soumission des dossiers entrepreneuriaux." },
      { id: "mod-2", name: "Mentorat", description: "Mise en relation avec des mentors." },
    ],
    roles: [
      { id: "role-1", name: "Porteur de projet", description: "Soumission de dossier.", permissions: ["Déposer un dossier"] },
      { id: "role-2", name: "Mentor", description: "Suivi des porteurs de projet.", permissions: ["Consulter les dossiers assignés"] },
    ],
    estimatedRequirements: 38,
    tags: ["Entrepreneuriat", "Financement"],
  },
  {
    id: "cooperatives",
    name: "Gestion des Coopératives Agricoles",
    shortName: "Coopératives Agricoles",
    department: "Direction Agriculture & Développement Rural",
    owner: { name: "Hamza Fassi", role: "Chargé de Mission Coopératives", initials: "HF" },
    status: "brouillon",
    progress: 12,
    securityScore: 54,
    createdAt: "2026-07-08T09:00:00",
    updatedAt: "2026-07-15T09:45:00",
    description: "Recensement des coopératives partenaires et suivi de leur production annuelle.",
    modules: [{ id: "mod-1", name: "Annuaire coopératives", description: "Base des coopératives partenaires." }],
    roles: [{ id: "role-1", name: "Gestionnaire coopérative", description: "Déclaration de production.", permissions: ["Déclarer la production"] }],
    estimatedRequirements: 21,
    tags: ["Agriculture", "Coopératives"],
  },
  {
    id: "formation-techniciens",
    name: "Plateforme de Formation des Techniciens Agricoles",
    shortName: "Formation Techniciens",
    department: "Direction Formation",
    owner: { name: "Imane Zahidi", role: "Responsable Formation", initials: "IZ" },
    status: "en_cours",
    progress: 45,
    securityScore: 69,
    createdAt: "2026-05-20T09:00:00",
    updatedAt: "2026-07-12T10:15:00",
    description: "Modules e-learning et suivi de certification des techniciens terrain du réseau Al Moutmir.",
    modules: [{ id: "mod-1", name: "Modules e-learning", description: "Contenus de formation en ligne." }],
    roles: [{ id: "role-1", name: "Technicien en formation", description: "Suivi des modules.", permissions: ["Suivre un module"] }],
    estimatedRequirements: 26,
    tags: ["Formation", "E-learning"],
  },
  {
    id: "dons-partenariats",
    name: "Système de Gestion des Dons & Partenariats",
    shortName: "Dons & Partenariats",
    department: "Direction Communication & Partenariats",
    owner: { name: "Omar Tazi", role: "Responsable Partenariats", initials: "OT" },
    status: "en_cours",
    progress: 30,
    securityScore: 61,
    createdAt: "2026-06-15T09:00:00",
    updatedAt: "2026-07-09T17:30:00",
    description: "Centralisation des conventions de partenariat et suivi des dons matériels aux associations locales.",
    modules: [{ id: "mod-1", name: "Conventions", description: "Suivi des conventions de partenariat." }],
    roles: [{ id: "role-1", name: "Partenaire", description: "Consultation de la convention.", permissions: ["Consulter la convention"] }],
    estimatedRequirements: 18,
    tags: ["Partenariats", "Communication"],
  },
];

// ---------------------------------------------------------------------------
// Dashboard stats
// ---------------------------------------------------------------------------

export const dashboardStats = {
  totalProjects: projects.length,
  inProgress: projects.filter((p) => p.status === "en_cours").length,
  validated: projects.filter((p) => p.status === "valide").length,
  avgSecurityScore: Math.round(
    projects.reduce((sum, p) => sum + p.securityScore, 0) / projects.length
  ),
  requirementsGenerated: projects.reduce((sum, p) => sum + p.estimatedRequirements, 0),
};

// ---------------------------------------------------------------------------
// Activity & notifications
// ---------------------------------------------------------------------------

export const recentActivity: ActivityItem[] = [
  { id: "act-1", actor: "Salma Idrissi", initials: "SI", action: "a répondu à 6 nouvelles questions sur", target: "PGB Al Moutmir", time: "il y a 24 min", type: "update" },
  { id: "act-2", actor: "Nadia Berrada", initials: "NB", action: "a soumis pour revue le projet", target: "Réseau Réussite", time: "il y a 3 h", type: "submit" },
  { id: "act-3", actor: "Système", initials: "AI", action: "a généré le cahier des charges de", target: "Suivi des Boursiers", time: "hier à 18:04", type: "generate" },
  { id: "act-4", actor: "Hamza Fassi", initials: "HF", action: "a créé le projet", target: "Coopératives Agricoles", time: "il y a 2 jours", type: "create" },
  { id: "act-5", actor: "Omar Tazi", initials: "OT", action: "a laissé un commentaire sur", target: "Dons & Partenariats", time: "il y a 2 jours", type: "comment" },
  { id: "act-6", actor: "Imane Zahidi", initials: "IZ", action: "a mis à jour le module", target: "Formation Techniciens", time: "il y a 3 jours", type: "update" },
];

export const notifications: NotificationItem[] = [
  { id: "n-1", title: "Cahier des charges généré", description: "Le document de « Suivi des Boursiers » est prêt à être téléchargé.", time: "il y a 1 h", read: false, type: "success" },
  { id: "n-2", title: "Score de sécurité faible", description: "« Coopératives Agricoles » a un score de sécurité de 54/100.", time: "il y a 5 h", read: false, type: "warning" },
  { id: "n-3", title: "Nouvelle soumission pour revue", description: "Nadia Berrada a soumis « Réseau Réussite ».", time: "il y a 3 h", read: true, type: "info" },
  { id: "n-4", title: "Rappel autosauvegarde", description: "Votre brouillon « PGB Al Moutmir » a été sauvegardé automatiquement.", time: "hier", read: true, type: "info" },
];

// ---------------------------------------------------------------------------
// Wizard / questionnaire
// ---------------------------------------------------------------------------

export const legacyWizardSteps: WizardStep[] = [
  {
    id: "general",
    title: "Informations générales",
    shortTitle: "Général",
    description: "Le point de départ : à quoi sert ce projet et qui le porte.",
    questions: [
      {
        id: "q-nom-projet",
        title: "Comment souhaitez-vous nommer ce projet ?",
        helper: "Un nom clair permettra aux équipes techniques d'identifier rapidement le projet.",
        example: "Plateforme de Gestion des Bénéficiaires — Programme Al Moutmir",
        type: "text",
        placeholder: "Ex. Plateforme de Gestion des Bénéficiaires",
        required: true,
      },
      {
        id: "q-departement",
        title: "Quel département porte ce projet ?",
        helper: "Cela nous aide à contextualiser les rôles et les circuits de validation.",
        type: "select",
        required: true,
        options: [
          { id: "opt-agri", label: "Agriculture & Développement Rural" },
          { id: "opt-edu", label: "Éducation & Formation" },
          { id: "opt-entre", label: "Entrepreneuriat" },
          { id: "opt-com", label: "Communication & Partenariats" },
        ],
      },
      {
        id: "q-objectif",
        title: "Quel est l'objectif principal de votre application ?",
        helper: "Décrivez en une ou deux phrases le problème métier que l'application doit résoudre.",
        example: "Recenser les agriculteurs bénéficiaires du programme et suivre leurs campagnes agricoles de bout en bout.",
        type: "textarea",
        placeholder: "Décrivez l'objectif de votre projet…",
        required: true,
      },
    ],
  },
  {
    id: "utilisateurs",
    title: "Contexte métier & utilisateurs",
    shortTitle: "Utilisateurs",
    description: "Qui va utiliser l'application, et comment.",
    questions: [
      {
        id: "q-utilisateurs",
        title: "Qui utilisera cette application ?",
        helper: "Sélectionnez tous les profils concernés — cela déterminera les rôles générés dans le cahier des charges.",
        type: "checkbox",
        required: true,
        options: [
          { id: "opt-beneficiaires", label: "Agriculteurs bénéficiaires", description: "Consultent leur dossier personnel" },
          { id: "opt-techniciens", label: "Techniciens terrain", description: "Saisissent les données sur le terrain" },
          { id: "opt-coordinateurs", label: "Coordinateurs régionaux", description: "Valident et supervisent une région" },
          { id: "opt-partenaires", label: "Partenaires externes", description: "Consultent certains rapports" },
          { id: "opt-public", label: "Grand public", description: "Accès à une vitrine publique" },
        ],
      },
      {
        id: "q-volumetrie",
        title: "Quelle est la volumétrie estimée d'utilisateurs ?",
        helper: "Un ordre de grandeur suffit — il influence les exigences de performance et de scalabilité.",
        type: "radio",
        required: true,
        options: [
          { id: "opt-v1", label: "Moins de 100 utilisateurs" },
          { id: "opt-v2", label: "100 à 500 utilisateurs" },
          { id: "opt-v3", label: "500 à 2 000 utilisateurs" },
          { id: "opt-v4", label: "Plus de 2 000 utilisateurs" },
        ],
      },
      {
        id: "q-canaux",
        title: "Par quels canaux l'application sera-t-elle utilisée ?",
        helper: "Les techniciens terrain travaillent souvent hors connexion — précisez si un mode mobile est nécessaire.",
        type: "checkbox",
        required: true,
        options: [
          { id: "opt-web", label: "Portail web" },
          { id: "opt-mobile", label: "Application mobile terrain" },
          { id: "opt-hors-ligne", label: "Fonctionnement hors-ligne requis" },
        ],
      },
    ],
  },
  {
    id: "donnees",
    title: "Données & documents",
    shortTitle: "Données",
    description: "Ce que les utilisateurs vont téléverser, et ce qui est sensible.",
    questions: [
      {
        id: "q-documents",
        title: "Quels documents les utilisateurs devront-ils téléverser ?",
        helper: "Chaque type de document sélectionné peut faire apparaître des questions complémentaires.",
        type: "checkbox",
        required: true,
        options: [
          { id: "opt-cin", label: "Pièce d'identité (CIN)" },
          { id: "opt-foncier", label: "Attestation foncière" },
          { id: "opt-photos", label: "Photos de parcelles" },
          { id: "opt-csv", label: "Fichier CSV de données terrain" },
          { id: "opt-pdf", label: "Rapports PDF existants" },
        ],
        followUps: [
          {
            id: "fu-csv-volume",
            triggerOptionId: "opt-csv",
            question: {
              id: "q-volume-csv",
              title: "Quel est le volume estimé de lignes par fichier CSV importé ?",
              helper: "Cela permet d'anticiper les exigences de traitement par lots et de validation des données.",
              type: "radio",
              options: [
                { id: "opt-csv-1", label: "Moins de 1 000 lignes" },
                { id: "opt-csv-2", label: "1 000 à 10 000 lignes" },
                { id: "opt-csv-3", label: "Plus de 10 000 lignes" },
              ],
            },
          },
        ],
      },
      {
        id: "q-confidentiel",
        title: "Quelles informations sont considérées comme confidentielles ?",
        helper: "Ajoutez un tag par type de donnée sensible — cela alimente directement les exigences de sécurité.",
        example: "Numéro CIN, Localisation GPS des parcelles, Revenu agricole",
        type: "tags",
        required: true,
      },
    ],
  },
  {
    id: "fonctionnalites",
    title: "Fonctionnalités & rapports",
    shortTitle: "Fonctionnalités",
    description: "Les rapports attendus et le calendrier du projet.",
    questions: [
      {
        id: "q-rapports",
        title: "Quels types de rapports avez-vous besoin ?",
        helper: "Choisissez les formats qui correspondent à vos besoins de pilotage.",
        type: "cards",
        required: true,
        options: [
          { id: "opt-r1", label: "Rapport de suivi de campagne", description: "Vue détaillée par campagne agricole" },
          { id: "opt-r2", label: "Tableau de bord régional", description: "Indicateurs agrégés par région" },
          { id: "opt-r3", label: "Export réglementaire", description: "Format conforme aux exigences institutionnelles" },
          { id: "opt-r4", label: "Rapport d'impact annuel", description: "Synthèse destinée aux bailleurs de fonds" },
        ],
      },
      {
        id: "q-frequence",
        title: "À quelle fréquence ces rapports doivent-ils être générés ?",
        helper: "",
        type: "radio",
        options: [
          { id: "opt-f1", label: "Hebdomadaire" },
          { id: "opt-f2", label: "Mensuelle" },
          { id: "opt-f3", label: "Trimestrielle" },
          { id: "opt-f4", label: "À la demande" },
        ],
      },
      {
        id: "q-echeance",
        title: "Quelle échéance visez-vous pour la mise en production ?",
        helper: "Une date indicative suffit pour cadrer le planning.",
        type: "date",
      },
    ],
  },
  {
    id: "securite",
    title: "Sécurité & confidentialité",
    shortTitle: "Sécurité",
    description: "Le niveau de protection requis pour les données du projet.",
    questions: [
      {
        id: "q-sensibilite",
        title: "Quel est le niveau de sensibilité global des données ?",
        helper: "Ce niveau détermine les contrôles de sécurité recommandés dans le cahier des charges.",
        type: "radio",
        required: true,
        options: [
          { id: "opt-s1", label: "Publique", description: "Aucune restriction d'accès" },
          { id: "opt-s2", label: "Interne", description: "Réservée aux collaborateurs de la Fondation" },
          { id: "opt-s3", label: "Confidentielle", description: "Données personnelles des bénéficiaires" },
          { id: "opt-s4", label: "Hautement confidentielle", description: "Données financières ou d'identité sensibles" },
        ],
      },
      {
        id: "q-auth-forte",
        title: "Une authentification forte (MFA) est-elle nécessaire ?",
        helper: "Recommandé dès que des données personnelles ou financières sont manipulées.",
        type: "radio",
        options: [
          { id: "opt-mfa-oui", label: "Oui, pour tous les profils" },
          { id: "opt-mfa-partiel", label: "Oui, pour les administrateurs uniquement" },
          { id: "opt-mfa-non", label: "Non nécessaire" },
        ],
      },
      {
        id: "q-schema",
        title: "Avez-vous un schéma ou document existant à joindre ?",
        helper: "Diagramme de flux, existant technique ou maquette — facultatif mais utile pour l'équipe technique.",
        type: "upload",
      },
    ],
  },
];

export const wizardSteps: WizardStep[] = [
  {
    id: "cadrage-focp",
    title: "Cadrage Fondation OCP",
    shortTitle: "Cadrage",
    description: "Contexte Axe Eco-Social, population cible, objectifs ESG/ODD et perimetre.",
    questions: [
      {
        id: "q-beneficiaires-volumetrie",
        title: "Quelle volumetrie de beneficiaires et cooperatives la plateforme doit-elle couvrir ?",
        helper: "Cette reponse dimensionne l'architecture, les tableaux de bord, la base de donnees et les controles de performance.",
        description: "Indiquez les volumes actuels, les projections sur trois ans, les regions concernees et les pics d'utilisation attendus.",
        example: "1700 cooperatives, 85 000 beneficiaires directs, 12 regions, reporting mensuel.",
        recommendedAnswer: "Preciser beneficiaires directs, indirects, cooperatives, regions, villes et croissance prevue.",
        tooltip: "Inclure les donnees regionales si les cooperatives sont pilotees localement.",
        type: "cards",
        required: true,
        importance: "critique",
        dependencies: ["Architecture", "Base de donnees", "Performance", "Dashboards"],
        customPrompt: "Decrivez la volumetrie exacte, les projections et la repartition territoriale.",
        options: [
          { id: "vol-500", label: "Moins de 500 cooperatives", description: "Plateforme centralisee simple" },
          { id: "vol-2000", label: "500 a 2000 cooperatives", description: "Pilotage regional et reporting consolide" },
          { id: "vol-5000", label: "Plus de 2000 cooperatives", description: "Scalabilite, files de traitement et entrepot analytique" },
          { id: "vol-unknown", label: "Volumetrie a qualifier", description: "L'IA demandera les estimations manquantes" },
        ],
      },
      {
        id: "q-indicateurs-impact",
        title: "Quels indicateurs ESG, ODD et impact social doivent etre suivis ?",
        helper: "Les indicateurs alimentent les exigences, le modele de donnees, les exports et les tableaux de bord.",
        example: "ODD 1, ODD 2, revenu moyen, emplois crees, femmes beneficiaires, surface valorisee.",
        recommendedAnswer: "Associer chaque indicateur a une source, une formule, une frequence et un niveau d'agregation.",
        type: "textarea",
        required: true,
        importance: "critique",
        dependencies: ["KPIs", "Reporting", "Data quality", "Audit trail"],
        placeholder: "Listez indicateurs, formules, sources, frequence et responsables...",
      },
    ],
  },
  {
    id: "workflows",
    title: "Workflows & Collaboration",
    shortTitle: "Workflows",
    description: "Validation, messagerie, taches, versioning, audit et cycle de vie documentaire.",
    questions: [
      {
        id: "q-validation-rapports",
        title: "Comment les rapports des cooperatives sont-ils valides ?",
        helper: "Le choix cree les roles applicatifs, statuts, notifications, journaux d'audit et regles de blocage.",
        description: "Precisez qui soumet, qui controle, qui approuve, les delais et les cas de rejet.",
        example: "Saisie cooperative, controle regional, validation centrale, publication mensuelle.",
        recommendedAnswer: "Deux niveaux de validation pour les rapports sensibles ou consolides.",
        type: "radio",
        required: true,
        importance: "critique",
        dependencies: ["Notifications", "Audit trail", "RBAC cible", "Documents"],
        customPrompt: "Decrivez votre workflow de validation complet.",
        options: [
          { id: "automatic", label: "Automatique", description: "Validation par regles metier et controles de coherence" },
          { id: "admin", label: "Validation administrateur", description: "Un valideur central approuve les rapports" },
          { id: "two-level", label: "Validation a deux niveaux", description: "Regional puis central" },
          { id: "none", label: "Aucune validation", description: "Publication directe apres depot" },
          { id: "other", label: "Autre", description: "Workflow specifique Fondation OCP" },
        ],
      },
      {
        id: "q-collaboration",
        title: "Quels besoins de messagerie, affectation de taches et historique sont requis ?",
        helper: "Ces reponses ajoutent les modules de collaboration, version history, audit logs et SLA.",
        example: "Commentaires sur dossiers, assignation a un charge regional, journal des changements, escalade apres 5 jours.",
        recommendedAnswer: "Activer commentaires contextualises, taches assignees, historique versionne et audit inalterable.",
        type: "checkbox",
        importance: "haute",
        dependencies: ["Workflow", "Notifications", "Audit", "Maintenance"],
        customPrompt: "Ajoutez les regles de collaboration propres a votre direction.",
        options: [
          { id: "messaging", label: "Messagerie interne" },
          { id: "tasks", label: "Affectation de taches" },
          { id: "versions", label: "Historique des versions" },
          { id: "audit", label: "Audit trail complet" },
          { id: "sla", label: "SLA et escalades" },
        ],
      },
    ],
  },
  {
    id: "donnees-documents",
    title: "Donnees & Documents",
    shortTitle: "Donnees",
    description: "Documents, imports, donnees spatiales, confidentialite et retention.",
    questions: [
      {
        id: "q-documents-upload",
        title: "Quels documents et formats seront importes ou televerses ?",
        helper: "Les formats personnalises generent automatiquement modules, stockage, APIs et exigences de securite adaptees.",
        example: "CSV, Excel, PDF, images, GeoJSON, Shapefile, images drone.",
        recommendedAnswer: "Lister format, taille, frequence, source, controles et duree de conservation.",
        type: "checkbox",
        required: true,
        importance: "critique",
        dependencies: ["Stockage", "Antivirus", "GIS", "Exports", "Base de donnees"],
        customPrompt: "Ajoutez vos formats specifiques: GeoJSON, Shapefile, drone images, conventions signees...",
        options: [
          { id: "csv", label: "CSV" },
          { id: "excel", label: "Excel" },
          { id: "pdf", label: "PDF" },
          { id: "images", label: "Images" },
          { id: "other", label: "Autre" },
        ],
      },
      {
        id: "q-retention",
        title: "Quelles politiques de retention, archivage et suppression s'appliquent ?",
        helper: "La retention influence la conformite Loi 09-08, RGPD, sauvegardes et purge automatique.",
        example: "Dossiers beneficiaires 10 ans, logs 24 mois, exports anonymises 5 ans.",
        recommendedAnswer: "Definir une duree par categorie de donnees et une procedure d'effacement.",
        type: "textarea",
        importance: "haute",
        dependencies: ["PIA", "Backup", "Audit logs", "Legal compliance"],
        placeholder: "Retention par type de donnee, archivage, purge, exceptions legales...",
      },
    ],
  },
  {
    id: "cybersecurite",
    title: "Cybersecurite & Conformite",
    shortTitle: "Securite",
    description: "OWASP, STRIDE, DREAD, classification, PIA, chiffrement, sauvegarde et incident response.",
    questions: [
      {
        id: "q-classification",
        title: "Comment classer les donnees traitees par sensibilite ?",
        helper: "La classification pilote chiffrement, acces, journalisation, anonymisation et exports.",
        example: "CIN et telephone: confidentiel. Indicateurs agreges: interne. Coordonnees GPS: hautement confidentiel.",
        recommendedAnswer: "Utiliser Public, Interne, Confidentiel, Hautement confidentiel avec controles par classe.",
        type: "tags",
        required: true,
        importance: "critique",
        dependencies: ["OWASP ASVS", "PIA", "RBAC cible", "Encryption"],
      },
      {
        id: "q-drp",
        title: "Quels objectifs de sauvegarde, restauration et continuite sont attendus ?",
        helper: "Ces valeurs generent RPO/RTO, architecture de backup, monitoring et disaster recovery.",
        example: "RPO 4h, RTO 8h, sauvegarde quotidienne chiffree, test de restauration trimestriel.",
        recommendedAnswer: "Definir RPO/RTO par criticite et tester la restauration regulierement.",
        type: "textarea",
        importance: "haute",
        dependencies: ["Infrastructure", "Monitoring", "Incident response", "Maintenance"],
        placeholder: "RPO, RTO, frequence, localisation, chiffrement, tests de restauration...",
      },
    ],
  },
  {
    id: "architecture",
    title: "Architecture & Exploitation",
    shortTitle: "Architecture",
    description: "Hosting, integrations, mobile, offline, accessibilite, API et exploitation.",
    questions: [
      {
        id: "q-hosting",
        title: "Ou la plateforme sera-t-elle hebergee et exploitee ?",
        helper: "Le choix conditionne deploiement, supervision, sauvegarde, CI/CD et contraintes reseau.",
        example: "Cloud souverain, datacenter Fondation OCP, Vercel frontend, FastAPI conteneurise.",
        recommendedAnswer: "Documenter environnements dev/test/prod, secrets, reseau, supervision et procedure de release.",
        type: "radio",
        required: true,
        importance: "critique",
        dependencies: ["Docker", "CI/CD", "Monitoring", "Security controls"],
        customPrompt: "Decrivez votre cible d'hebergement, contraintes reseau et exigences d'exploitation.",
        options: [
          { id: "on-prem", label: "Datacenter interne" },
          { id: "cloud", label: "Cloud" },
          { id: "hybrid", label: "Hybride" },
          { id: "vercel-api", label: "Vercel + API conteneurisee" },
          { id: "undecided", label: "A determiner" },
        ],
      },
      {
        id: "q-integrations-mobile",
        title: "Quelles integrations, contraintes mobile, offline et accessibilite sont requises ?",
        helper: "Les reponses generent modules d'integration, APIs, files de synchronisation, tests et exigences WCAG.",
        example: "Import CSV mensuel, SMS, Power BI, mode offline terrain Android, WCAG 2.2 AA.",
        recommendedAnswer: "Lister systeme, protocole, frequence, proprietaire, SLA et donnees echangees.",
        type: "textarea",
        importance: "haute",
        dependencies: ["API", "Mobile", "Offline sync", "Accessibility", "External integrations"],
        placeholder: "Systemes externes, notifications, mobile/offline, accessibilite, volumes...",
      },
    ],
  },
];

// ---------------------------------------------------------------------------
// Generated document (Cahier des Charges)
// ---------------------------------------------------------------------------

export const documentSections: DocumentSection[] = [
  {
    id: "contexte",
    title: "Contexte métier",
    icon: "Building2",
    summary:
      "Le programme Al Moutmir accompagne chaque année plusieurs milliers d'agriculteurs à travers le Maroc. Le suivi actuel repose sur des fichiers Excel disparates gérés par chaque coordination régionale, ce qui limite la visibilité nationale et complique la traçabilité des distributions d'intrants.",
    paragraphs: [
      "La Fondation OCP souhaite doter la Direction Agriculture & Développement Rural d'une plateforme unifiée permettant de recenser les bénéficiaires, suivre leurs parcelles et campagnes, et consolider les rapports d'impact remontés du terrain.",
      "Le projet s'inscrit dans la continuité de la digitalisation des programmes de la Fondation, avec une attention particulière portée à la protection des données personnelles des agriculteurs.",
    ],
  },
  {
    id: "objectifs",
    title: "Objectifs du projet",
    icon: "Target",
    summary: "Quatre objectifs structurent le cadrage de la plateforme, du recensement jusqu'au reporting national.",
    requirements: [
      { id: "OBJ-01", code: "OBJ-01", label: "Centraliser le recensement des bénéficiaires", detail: "Remplacer les fichiers Excel régionaux par une base de données unique et fiable.", priority: "critique" },
      { id: "OBJ-02", code: "OBJ-02", label: "Fiabiliser la traçabilité des intrants distribués", detail: "Associer chaque lot distribué à un bénéficiaire et une campagne identifiés.", priority: "haute" },
      { id: "OBJ-03", code: "OBJ-03", label: "Accélérer la production des rapports d'impact", detail: "Générer automatiquement les indicateurs régionaux et nationaux.", priority: "haute" },
      { id: "OBJ-04", code: "OBJ-04", label: "Protéger les données personnelles des agriculteurs", detail: "Appliquer un contrôle d'accès strict conforme à la loi 09-08.", priority: "critique" },
    ],
  },
  {
    id: "fonctionnelles",
    title: "Exigences fonctionnelles",
    icon: "ListChecks",
    summary: "Les fonctionnalités couvrent l'ensemble du parcours, de l'inscription du bénéficiaire au reporting national.",
    requirements: [
      { id: "FR-01", code: "FR-01", label: "Inscription d'un bénéficiaire", detail: "Un technicien terrain peut créer une fiche bénéficiaire avec pièce d'identité et localisation de parcelle.", priority: "critique" },
      { id: "FR-02", code: "FR-02", label: "Validation régionale", detail: "Un coordinateur régional valide ou rejette une inscription avec motif.", priority: "haute" },
      { id: "FR-03", code: "FR-03", label: "Import de données terrain", detail: "Import de fichiers CSV de relevés terrain avec validation des lignes en erreur.", priority: "haute" },
      { id: "FR-04", code: "FR-04", label: "Suivi des distributions d'intrants", detail: "Enregistrement des lots de semences et engrais distribués par bénéficiaire.", priority: "moyenne" },
      { id: "FR-05", code: "FR-05", label: "Génération de rapports", detail: "Génération de rapports régionaux et nationaux filtrables par campagne.", priority: "haute" },
      { id: "FR-06", code: "FR-06", label: "Mode hors-ligne terrain", detail: "Saisie possible sans connexion avec synchronisation différée.", priority: "moyenne" },
    ],
  },
  {
    id: "techniques",
    title: "Exigences techniques",
    icon: "Cpu",
    summary: "Contraintes techniques garantissant la performance, la disponibilité et l'interopérabilité de la plateforme.",
    requirements: [
      { id: "NFR-01", code: "NFR-01", label: "Disponibilité", detail: "Disponibilité cible de 99,5% pendant les périodes de campagne.", priority: "haute" },
      { id: "NFR-02", code: "NFR-02", label: "Scalabilité", detail: "Support de 2 000 utilisateurs simultanés sans dégradation notable.", priority: "moyenne" },
      { id: "NFR-03", code: "NFR-03", label: "Compatibilité mobile", detail: "Application mobile compatible Android en priorité pour les techniciens terrain.", priority: "haute" },
      { id: "NFR-04", code: "NFR-04", label: "Interopérabilité", detail: "Export des données compatible avec les outils SIG existants de la Fondation.", priority: "moyenne" },
    ],
  },
  {
    id: "cybersecurite",
    title: "Exigences cybersécurité",
    icon: "ShieldCheck",
    summary: "Le score de sécurité calculé pour ce projet est de 82/100. Les exigences ci-dessous couvrent l'authentification, le chiffrement et la traçabilité des accès.",
    requirements: [
      { id: "SEC-01", code: "SEC-01", label: "Authentification multi-facteurs", detail: "MFA obligatoire pour les profils administrateur et coordinateur régional.", priority: "critique" },
      { id: "SEC-02", code: "SEC-02", label: "Chiffrement des données au repos", detail: "Chiffrement AES-256 des données personnelles des bénéficiaires en base.", priority: "critique" },
      { id: "SEC-03", code: "SEC-03", label: "Chiffrement en transit", detail: "TLS 1.3 obligatoire sur l'ensemble des flux, y compris la synchronisation mobile.", priority: "critique" },
      { id: "SEC-04", code: "SEC-04", label: "Journalisation des accès", detail: "Journal d'audit inaltérable de tous les accès aux données confidentielles, conservé 12 mois.", priority: "haute" },
      { id: "SEC-05", code: "SEC-05", label: "Anonymisation des exports", detail: "Les exports destinés aux partenaires externes masquent les identifiants directs (CIN, GPS).", priority: "haute" },
      { id: "SEC-06", code: "SEC-06", label: "Gestion des sessions", detail: "Expiration automatique de session après 15 minutes d'inactivité sur le portail web.", priority: "moyenne" },
    ],
  },
  {
    id: "rbac",
    title: "Contrôle d'accès (RBAC)",
    icon: "KeyRound",
    summary: "Quatre rôles couvrent l'ensemble des usages, avec un principe de moindre privilège appliqué par défaut.",
    table: {
      headers: ["Rôle", "Périmètre", "Droits principaux"],
      rows: [
        ["Agriculteur bénéficiaire", "Son propre dossier", "Consulter, téléverser des documents"],
        ["Technicien terrain", "Sa zone d'affectation", "Créer une fiche, saisir des visites, mode hors-ligne"],
        ["Coordinateur régional", "Sa région", "Valider les inscriptions, consulter les rapports régionaux"],
        ["Administrateur Fondation", "National", "Configuration, export national, journaux d'audit"],
      ],
    },
  },
  {
    id: "workflows",
    title: "Workflows",
    icon: "Workflow",
    summary: "Le circuit d'inscription d'un bénéficiaire suit quatre étapes avant activation de son dossier.",
    paragraphs: [
      "1. Le technicien terrain crée la fiche bénéficiaire et joint les pièces justificatives.",
      "2. Le dossier est soumis automatiquement au coordinateur régional compétent.",
      "3. Le coordinateur valide, rejette ou demande un complément d'information.",
      "4. Une fois validé, le dossier est activé et le bénéficiaire reçoit ses identifiants d'accès.",
    ],
  },
  {
    id: "database",
    title: "Modèle de données",
    icon: "Database",
    summary: "Les entités principales structurent le domaine bénéficiaires, parcelles, campagnes et distributions.",
    table: {
      headers: ["Entité", "Description", "Relations clés"],
      rows: [
        ["Bénéficiaire", "Agriculteur inscrit au programme", "1—N Parcelles, 1—N Distributions"],
        ["Parcelle", "Unité foncière suivie", "N—1 Bénéficiaire, 1—N Campagnes"],
        ["Campagne", "Période agricole (semis à récolte)", "N—1 Parcelle, 1—N Distributions"],
        ["Distribution", "Lot d'intrants remis", "N—1 Bénéficiaire, N—1 Campagne"],
      ],
    },
  },
  {
    id: "api",
    title: "Exigences API",
    icon: "Braces",
    summary: "Une API REST versionnée expose les ressources principales aux applications web et mobile.",
    requirements: [
      { id: "API-01", code: "API-01", label: "Authentification par jeton", detail: "OAuth2 / JWT avec rotation des jetons de rafraîchissement.", priority: "critique" },
      { id: "API-02", code: "API-02", label: "Limitation de débit", detail: "Rate limiting par utilisateur pour prévenir les abus sur les endpoints d'export.", priority: "moyenne" },
      { id: "API-03", code: "API-03", label: "Versionnage", detail: "Toute évolution majeure de l'API est versionnée (/v1, /v2) pour ne pas casser l'app mobile terrain.", priority: "moyenne" },
    ],
  },
  {
    id: "architecture",
    title: "Architecture",
    icon: "Network",
    summary: "Architecture en trois niveaux avec synchronisation différée pour les usages terrain hors-ligne.",
    paragraphs: [
      "Le front web et l'application mobile consomment une API centrale exposée par la couche métier.",
      "Un mécanisme de synchronisation par file d'attente permet aux techniciens terrain de saisir des données hors-ligne, synchronisées dès que la connexion est rétablie.",
      "Les données personnelles des bénéficiaires sont isolées dans une base chiffrée distincte des données opérationnelles agrégées utilisées pour le reporting.",
    ],
  },
];

// ---------------------------------------------------------------------------
// Admin
// ---------------------------------------------------------------------------

export const adminSubmissions: AdminSubmission[] = [
  { id: "sub-1", projectId: "reseau-reussite", projectName: "Réseau Réussite", submittedBy: "Nadia Berrada", department: "Entrepreneuriat", submittedAt: "2026-07-14T14:10:00", status: "en_revue", completeness: 100 },
  { id: "sub-2", projectId: "boursiers-ocp", projectName: "Suivi des Boursiers", submittedBy: "Yassine Bennani", department: "Éducation & Formation", submittedAt: "2026-06-01T09:30:00", status: "valide", completeness: 100 },
  { id: "sub-3", projectId: "pgb-almoutmir", projectName: "PGB Al Moutmir", submittedBy: "Salma Idrissi", department: "Agriculture & Développement Rural", submittedAt: "2026-07-14T16:40:00", status: "en_cours", completeness: 68 },
  { id: "sub-4", projectId: "formation-techniciens", projectName: "Formation Techniciens", submittedBy: "Imane Zahidi", department: "Formation", submittedAt: "2026-07-12T10:15:00", status: "en_cours", completeness: 45 },
];

export const monthlyGenerated = [
  { month: "Fév", documents: 2 },
  { month: "Mar", documents: 4 },
  { month: "Avr", documents: 3 },
  { month: "Mai", documents: 6 },
  { month: "Juin", documents: 8 },
  { month: "Juil", documents: 5 },
];

export const departmentDistribution = [
  { name: "Agriculture", value: 3 },
  { name: "Éducation", value: 1 },
  { name: "Entrepreneuriat", value: 1 },
  { name: "Communication", value: 1 },
];

export const securityScoreTrend = [
  { month: "Fév", score: 61 },
  { month: "Mar", score: 65 },
  { month: "Avr", score: 70 },
  { month: "Mai", score: 74 },
  { month: "Juin", score: 79 },
  { month: "Juil", score: 82 },
];

export const currentUser = {
  name: "Karim El Amrani",
  role: "Superviseur Digital & Innovation",
  initials: "KA",
};

export const documentVersions = [
  { id: "v1", version: "1.3", date: "2026-07-14T16:40:00", author: "Salma Idrissi", change: "Ajout des exigences de mode hors-ligne et mise à jour du RBAC." },
  { id: "v2", version: "1.2", date: "2026-06-28T11:20:00", author: "Karim El Amrani", change: "Renforcement des exigences de chiffrement suite à la revue sécurité." },
  { id: "v3", version: "1.1", date: "2026-06-10T09:05:00", author: "Salma Idrissi", change: "Ajout du module de distribution des intrants." },
  { id: "v4", version: "1.0", date: "2026-05-04T09:12:00", author: "Salma Idrissi", change: "Première génération du cahier des charges." },
];

export const generatedFiles = [
  { id: "f1", name: "Cahier_des_Charges_v1.3.pdf", type: "PDF", size: "1.8 Mo", date: "2026-07-14T16:40:00" },
  { id: "f2", name: "Export_RBAC_matrice.xlsx", type: "Excel", size: "84 Ko", date: "2026-07-14T16:40:00" },
  { id: "f3", name: "Diagramme_architecture.png", type: "Image", size: "620 Ko", date: "2026-07-12T10:00:00" },
  { id: "f4", name: "Cahier_des_Charges_v1.2.pdf", type: "PDF", size: "1.6 Mo", date: "2026-06-28T11:20:00" },
];

export const projectComments = [
  { id: "c1", author: "Karim El Amrani", initials: "KA", text: "Merci d'ajouter une exigence sur la rétention des logs d'audit à 12 mois — c'est requis par la politique interne.", time: "il y a 2 jours" },
  { id: "c2", author: "Salma Idrissi", initials: "SI", text: "C'est fait, voir SEC-04 dans la dernière version du document.", time: "il y a 1 jour" },
];
