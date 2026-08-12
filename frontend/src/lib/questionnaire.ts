import type { WizardStep } from "./types";

const custom = "Autre / Ma réponse";

export const wizardSteps: WizardStep[] = [
  {
    id: "context",
    title: "Contexte du projet",
    shortTitle: "Contexte",
    description: "Nom, objectif, problème et résultat attendu.",
    questions: [
      { id: "project_name", title: "Quel est le nom du projet ?", helper: "", type: "text", required: true },
      { id: "objective", title: "Quel est l'objectif principal de ce projet ?", helper: "", type: "textarea", required: true },
      { id: "problem", title: "Quel problème souhaitez-vous résoudre ?", helper: "", type: "textarea", required: true },
      { id: "current_situation", title: "Comment ce problème est-il géré aujourd'hui ?", helper: "", type: "textarea" },
      { id: "expected_result", title: "Qu'aimeriez-vous pouvoir faire grâce à la nouvelle application ?", helper: "", type: "textarea", required: true },
    ],
  },
  {
    id: "users",
    title: "Utilisateurs",
    shortTitle: "Utilisateurs",
    description: "Profils, actions et visibilité des informations.",
    questions: [
      { id: "users", title: "Qui utilisera principalement l'application ?", helper: "", type: "checkbox", options: ["Administrateurs", "Employés", "Managers", "Clients", "Bénéficiaires", "Partenaires", "Responsables métier", custom].map((label) => ({ id: label, label })), customPrompt: "Ma réponse" },
      { id: "user_actions", title: "Que doit pouvoir faire chaque type d'utilisateur ?", helper: "", type: "textarea" },
      { id: "restricted_information", title: "Certaines informations doivent-elles être visibles seulement par certains utilisateurs ?", helper: "", type: "radio", options: ["Oui", "Non", "Je ne sais pas", custom].map((label) => ({ id: label, label })), customPrompt: "Ma réponse" },
    ],
  },
  {
    id: "features",
    title: "Fonctionnalités",
    shortTitle: "Fonctions",
    description: "Informations, documents, recherche et sorties.",
    questions: [
      { id: "main_features", title: "Quelles sont les principales fonctionnalités souhaitées ?", helper: "", type: "checkbox", options: ["Gestion des utilisateurs", "Gestion des données", "Gestion des bénéficiaires", "Gestion des documents", "Recherche & Filtres", "Tableaux de bord", "Statistiques", "Notifications", "Rapports", "Cartographie", "Import de fichiers", "Export de données", "Suivi d'activités", custom].map((label) => ({ id: label, label })), customPrompt: "Ma réponse" },
      { id: "view_information", title: "Quelles informations les utilisateurs doivent-ils consulter ?", helper: "", type: "textarea" },
      { id: "edit_information", title: "Quelles informations les utilisateurs doivent-ils ajouter ou modifier ?", helper: "", type: "textarea" },
      { id: "documents", title: "L'application doit-elle gérer des documents ?", helper: "Si oui, précisez les types.", type: "radio", options: ["Oui", "Non", custom].map((label) => ({ id: label, label })), customPrompt: "Ma réponse" },
      { id: "search", title: "Comment les utilisateurs doivent-ils rechercher les informations ?", helper: "", type: "checkbox", options: ["Nom", "Région", "Date", "Statut", "Catégorie", "Type", "Identifiant", custom].map((label) => ({ id: label, label })), customPrompt: "Ma réponse" },
      { id: "dashboards", title: "Quelles informations importantes voulez-vous voir sur les tableaux de bord ?", helper: "", type: "textarea" },
      { id: "maps", title: "Avez-vous besoin d'afficher des informations sur une carte ?", helper: "Si oui, précisez quoi afficher.", type: "radio", options: ["Oui", "Non", "Peut-être", custom].map((label) => ({ id: label, label })), customPrompt: "Ma réponse" },
      { id: "reports", title: "Avez-vous besoin de générer des rapports ?", helper: "Si oui, précisez lesquels.", type: "radio", options: ["Oui", "Non", custom].map((label) => ({ id: label, label })), customPrompt: "Ma réponse" },
      { id: "exports", title: "Dans quels formats souhaitez-vous récupérer les données ?", helper: "", type: "checkbox", options: ["PDF", "Excel", "CSV", "Word", custom].map((label) => ({ id: label, label })), customPrompt: "Ma réponse" },
      { id: "notifications", title: "L'application doit-elle envoyer des notifications ou rappels ?", helper: "Si oui, précisez les situations.", type: "radio", options: ["Oui", "Non", "Peut-être", custom].map((label) => ({ id: label, label })), customPrompt: "Ma réponse" },
    ],
  },
  {
    id: "workflow",
    title: "Processus métier",
    shortTitle: "Processus",
    description: "Étapes, validation, refus et historique.",
    questions: [
      { id: "main_workflow", title: "Pouvez-vous décrire les principales étapes d'utilisation ?", helper: "", type: "textarea" },
      { id: "validation", title: "Certaines informations doivent-elles être vérifiées ou validées ?", helper: "Si oui, précisez par qui.", type: "radio", options: ["Oui", "Non", "Je ne sais pas", custom].map((label) => ({ id: label, label })), customPrompt: "Ma réponse" },
      { id: "rejection", title: "Que doit-il se passer lorsqu'une demande est refusée ?", helper: "", type: "checkbox", options: ["Retour pour correction", "Notification", "Nouvelle soumission", "Archivage", custom].map((label) => ({ id: label, label })), customPrompt: "Ma réponse" },
      { id: "history", title: "Est-il important de conserver l'historique des modifications ?", helper: "", type: "radio", options: ["Oui", "Non", "Pour certaines informations seulement", "Je ne sais pas", custom].map((label) => ({ id: label, label })), customPrompt: "Ma réponse" },
    ],
  },
  {
    id: "constraints",
    title: "Contraintes",
    shortTitle: "Contraintes",
    description: "Protection, accès, appareils et langues.",
    questions: [
      { id: "sensitive_information", title: "Quelles informations doivent être particulièrement protégées ?", helper: "", type: "checkbox", options: ["Informations personnelles", "Informations financières", "Documents confidentiels", "Données médicales", "Données professionnelles", custom].map((label) => ({ id: label, label })), customPrompt: "Ma réponse" },
      { id: "availability", title: "L'application doit-elle fonctionner avec une connexion limitée ?", helper: "", type: "radio", options: ["En ligne uniquement", "Connexion limitée", "Hors ligne nécessaire", "Je ne sais pas", custom].map((label) => ({ id: label, label })), customPrompt: "Ma réponse" },
      { id: "devices", title: "Sur quels appareils l'application doit-elle fonctionner ?", helper: "", type: "checkbox", options: ["Ordinateur", "Smartphone", "Tablette", "Tous", custom].map((label) => ({ id: label, label })), customPrompt: "Ma réponse" },
      { id: "languages", title: "Quelles langues doivent être disponibles ?", helper: "", type: "checkbox", options: ["Français", "Arabe", "Anglais", custom].map((label) => ({ id: label, label })), customPrompt: "Ma réponse" },
    ],
  },
  {
    id: "priorities",
    title: "Priorités",
    shortTitle: "Priorités",
    description: "MVP, évolutions et dernières précisions.",
    questions: [
      { id: "mvp", title: "Quelles fonctionnalités sont indispensables pour la première version ?", helper: "", type: "textarea", required: true },
      { id: "future_features", title: "Quelles fonctionnalités pourraient être ajoutées plus tard ?", helper: "", type: "textarea" },
      { id: "special_constraints", title: "Y a-t-il des contraintes ou règles particulières à respecter ?", helper: "", type: "textarea" },
      { id: "final_notes", title: "Y a-t-il autre chose à prévoir dans l'application ?", helper: "", type: "textarea" },
    ],
  },
];
