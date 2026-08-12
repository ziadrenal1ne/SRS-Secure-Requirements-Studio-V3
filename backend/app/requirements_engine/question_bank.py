"""Business-oriented question bank used by offline and AI interviews."""

MIN_QUESTIONS = 20
TARGET_QUESTIONS = 24
MAX_QUESTIONS = 30
CUSTOM_CHOICE = "Autre / Ma reponse"


def with_custom(options: list[str]) -> list[str]:
    return [*options, CUSTOM_CHOICE]


QUESTIONS: list[dict] = [
    {"id": "project_name", "section": "context", "question": "Quel est le nom du projet ?", "type": "text", "required": True},
    {"id": "objective", "section": "context", "question": "Quel est l'objectif principal de ce projet ?", "type": "textarea", "required": True},
    {"id": "problem", "section": "context", "question": "Quel probleme souhaitez-vous resoudre ?", "type": "textarea", "required": True},
    {"id": "current_situation", "section": "context", "question": "Comment ce probleme est-il gere aujourd'hui ?", "type": "textarea"},
    {"id": "expected_result", "section": "context", "question": "Qu'aimeriez-vous pouvoir faire grace a la nouvelle application ?", "type": "textarea", "required": True},
    {"id": "users", "section": "users", "question": "Qui utilisera principalement l'application ?", "type": "checkbox", "choices": with_custom(["Administrateurs", "Employes", "Managers", "Clients", "Beneficiaires", "Partenaires", "Responsables"])},
    {"id": "user_actions", "section": "users", "question": "Que doit pouvoir faire chaque type d'utilisateur ?", "type": "textarea"},
    {"id": "restricted_information", "section": "users", "question": "Certaines informations doivent-elles etre visibles seulement par certains utilisateurs ?", "type": "radio", "choices": with_custom(["Oui", "Non", "Je ne sais pas"]), "follow_up": "Lesquelles et pour qui ?"},
    {"id": "main_features", "section": "features", "question": "Quelles sont les principales fonctionnalites souhaitees ?", "type": "checkbox", "choices": with_custom(["Gestion des utilisateurs", "Gestion des donnees", "Gestion des beneficiaires", "Gestion des documents", "Recherche", "Tableaux de bord", "Statistiques", "Notifications", "Rapports", "Cartographie", "Import de fichiers", "Export de donnees", "Suivi d'activites"])},
    {"id": "view_information", "section": "features", "question": "Quelles informations les utilisateurs doivent-ils consulter ?", "type": "textarea"},
    {"id": "edit_information", "section": "features", "question": "Quelles informations les utilisateurs doivent-ils ajouter ou modifier ?", "type": "textarea"},
    {"id": "documents", "section": "features", "question": "L'application doit-elle gerer des documents ?", "type": "radio", "choices": with_custom(["Oui", "Non"]), "follow_up": "Quels types de documents ?"},
    {"id": "search", "section": "features", "question": "Comment les utilisateurs doivent-ils rechercher les informations ?", "type": "checkbox", "choices": with_custom(["Nom", "Region", "Date", "Statut", "Categorie", "Type", "Identifiant"])},
    {"id": "dashboards", "section": "features", "question": "Quelles informations importantes voulez-vous voir sur les tableaux de bord ?", "type": "textarea"},
    {"id": "maps", "section": "features", "question": "Avez-vous besoin d'afficher des informations sur une carte ?", "type": "radio", "choices": with_custom(["Oui", "Non", "Peut-etre"]), "follow_up": "Que souhaitez-vous afficher sur la carte ?"},
    {"id": "reports", "section": "features", "question": "Avez-vous besoin de generer des rapports ?", "type": "radio", "choices": with_custom(["Oui", "Non"]), "follow_up": "Quels rapports souhaitez-vous ?"},
    {"id": "exports", "section": "features", "question": "Dans quels formats souhaitez-vous recuperer les donnees ?", "type": "checkbox", "choices": with_custom(["PDF", "Excel", "CSV", "Word"])},
    {"id": "notifications", "section": "features", "question": "L'application doit-elle envoyer des notifications ou rappels ?", "type": "radio", "choices": with_custom(["Oui", "Non", "Peut-etre"]), "follow_up": "Dans quelles situations ?"},
    {"id": "main_workflow", "section": "workflow", "question": "Pouvez-vous decrire les principales etapes d'utilisation ?", "type": "textarea"},
    {"id": "validation", "section": "workflow", "question": "Certaines informations doivent-elles etre verifiees ou validees ?", "type": "radio", "choices": with_custom(["Oui", "Non", "Je ne sais pas"]), "follow_up": "Qui doit les valider ?"},
    {"id": "rejection", "section": "workflow", "question": "Que doit-il se passer lorsqu'une demande est refusee ?", "type": "checkbox", "choices": with_custom(["Retour pour correction", "Notification", "Nouvelle soumission", "Archivage"])},
    {"id": "history", "section": "workflow", "question": "Est-il important de conserver l'historique des modifications ?", "type": "radio", "choices": with_custom(["Oui", "Non", "Pour certaines informations seulement", "Je ne sais pas"])},
    {"id": "sensitive_information", "section": "constraints", "question": "Quelles informations doivent etre particulierement protegees ?", "type": "checkbox", "choices": with_custom(["Informations personnelles", "Informations financieres", "Documents confidentiels", "Donnees medicales", "Donnees professionnelles"])},
    {"id": "availability", "section": "constraints", "question": "L'application doit-elle fonctionner avec une connexion limitee ?", "type": "radio", "choices": with_custom(["En ligne uniquement", "Connexion limitee", "Hors ligne necessaire", "Je ne sais pas"])},
    {"id": "devices", "section": "constraints", "question": "Sur quels appareils l'application doit-elle fonctionner ?", "type": "checkbox", "choices": with_custom(["Ordinateur", "Smartphone", "Tablette", "Tous"])},
    {"id": "languages", "section": "constraints", "question": "Quelles langues doivent etre disponibles ?", "type": "checkbox", "choices": with_custom(["Francais", "Arabe", "Anglais"])},
    {"id": "mvp", "section": "priorities", "question": "Quelles fonctionnalites sont indispensables pour la premiere version ?", "type": "textarea", "required": True},
    {"id": "future_features", "section": "priorities", "question": "Quelles fonctionnalites pourraient etre ajoutees plus tard ?", "type": "textarea"},
    {"id": "special_constraints", "section": "priorities", "question": "Y a-t-il des contraintes ou regles particulieres a respecter ?", "type": "textarea"},
    {"id": "final_notes", "section": "priorities", "question": "Y a-t-il autre chose a prevoir dans l'application ?", "type": "textarea"},
]

QUESTIONS_BY_ID = {question["id"]: question for question in QUESTIONS}
