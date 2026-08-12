"""Requirement engine that converts raw business answers into structured ProjectModel
written in natural, senior Business Analyst French.
"""

from app.requirements_engine.models import ProjectModel


def _split(value: str) -> list[str]:
    if not value:
        return []
    parts = []
    for chunk in value.replace("|", ",").split(","):
        cleaned = chunk.strip(" -;\n\t")
        if cleaned and not cleaned.lower().startswith("autre"):
            parts.append(cleaned)
    return parts


def _clean_text(value: str) -> str:
    if not value:
        return ""
    cleaned = value.strip()
    if cleaned and not cleaned.endswith((".", "!", "?")):
        cleaned += "."
    return cleaned


def _format_list_prose(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} et {items[1]}"
    return ", ".join(items[:-1]) + f" ainsi que {items[-1]}"


def build_project_model(answers: dict[str, str], fallback_name: str = "Projet") -> ProjectModel:
    project_name = answers.get("project_name") or fallback_name
    model = ProjectModel(project_name=project_name, raw_answers=answers)

    # 1. Context & Objectives
    model.context = {
        "objective": _clean_text(answers.get("objective", "")),
        "problem": _clean_text(answers.get("problem", "")),
        "current_situation": _clean_text(answers.get("current_situation", "")),
        "expected_result": _clean_text(answers.get("expected_result", "")),
    }

    # Track missing critical information for [À VALIDER] markers
    points_to_validate: list[str] = []

    if not model.context["objective"]:
        points_to_validate.append("L'objectif principal précis de la plateforme reste [À VALIDER].")

    # 2. Users & Roles
    model.users = _split(answers.get("users", ""))
    if model.users:
        user_list_str = _format_list_prose(model.users)
        model.role_requirements.append(
            f"La plateforme s'adresse principalement aux profil(s) suivant(s) : {user_list_str}."
        )
    else:
        points_to_validate.append("La liste définitive des profils utilisateurs reste [À DÉFINIR].")

    if answers.get("user_actions"):
        model.role_requirements.append(
            f"Chaque profil dispose d'habiliations adaptées à son périmètre : {_clean_text(answers['user_actions'])}"
        )

    restricted = answers.get("restricted_information", "").lower()
    if "oui" in restricted or "je ne sais pas" in restricted:
        model.role_requirements.append(
            "Le système garantit le cloisonnement des données : chaque utilisateur accède uniquement aux informations autorisées pour son profil."
        )
        model.security_needs.append(
            "Mise en place d'un contrôle d'accès strict par rôle afin d'empêcher toute consultation non autorisée."
        )
    elif restricted and "non" not in restricted:
        model.role_requirements.append(_clean_text(answers["restricted_information"]))

    # 3. Functional Requirements
    main_features = _split(answers.get("main_features", ""))
    for feature in main_features:
        model.functional_requirements.append(
            f"Module de {feature.lower()} permettant la gestion complète du périmètre associé."
        )

    if answers.get("view_information"):
        model.data_requirements.append(
            f"Les utilisateurs peuvent consulter les données suivantes : {_clean_text(answers['view_information'])}"
        )
    if answers.get("edit_information"):
        model.data_requirements.append(
            f"Les utilisateurs autorisés peuvent créer et mettre à jour les informations suivantes : {_clean_text(answers['edit_information'])}"
        )

    docs_ans = answers.get("documents", "").lower()
    if "oui" in docs_ans or any("document" in f.lower() for f in main_features):
        doc_details = answers.get("documents", "") if "oui" not in docs_ans else ""
        if doc_details and len(doc_details) > 5:
            model.document_requirements.append(
                f"Gestion documentaire intégrée : dépôt, consultation et suivi des pièces jointes ({doc_details})."
            )
        else:
            model.document_requirements.append(
                "Gestion documentaire intégrée : stockage sécurisé, consultation et téléchargement des documents associés."
            )

    search_items = _split(answers.get("search", ""))
    if search_items:
        model.search_requirements.append(
            f"Recherche et filtrage multicritères basés sur : {_format_list_prose(search_items)}."
        )

    if answers.get("dashboards"):
        model.dashboard_requirements.append(
            f"Tableau de bord de pilotage présentant les indicateurs clés suivants : {_clean_text(answers['dashboards'])}"
        )

    maps_ans = answers.get("maps", "").lower()
    if "oui" in maps_ans or "peut-être" in maps_ans or any("carte" in f.lower() or "cartographie" in f.lower() for f in main_features):
        model.map_requirements.append(
            "Visualisation cartographique interactive permettant de géolocaliser les entités et d'analyser la répartition géographique."
        )

    reports_ans = answers.get("reports", "").lower()
    if "oui" in reports_ans or any("rapport" in f.lower() for f in main_features):
        model.report_requirements.append(
            "Génération automatique de rapports d'activité synthétiques et détaillés."
        )

    exports_items = _split(answers.get("exports", ""))
    if exports_items:
        model.export_requirements.append(
            f"Exportation des données et rapports aux formats : {_format_list_prose(exports_items)}."
        )

    notif_ans = answers.get("notifications", "").lower()
    if "oui" in notif_ans or "peut-être" in notif_ans or any("notification" in f.lower() for f in main_features):
        model.notification_requirements.append(
            "Système de notifications et d'alertes en temps réel lors des événements clés du workflow."
        )

    # 4. Workflows & Business Rules
    if answers.get("main_workflow"):
        model.workflows.append(_clean_text(answers["main_workflow"]))

    val_ans = answers.get("validation", "").lower()
    if "oui" in val_ans:
        model.validation_rules.append(
            "Circuit de validation préalable : les soumissions de données sont soumises à vérification avant d'être officialisées."
        )
    elif "je ne sais pas" in val_ans:
        points_to_validate.append("La nécessité d'un circuit de validation hiérarchique reste [À VALIDER].")

    rej_items = _split(answers.get("rejection", ""))
    if rej_items:
        model.rejection_rules.append(
            f"En cas de rejet d'une soumission, la procédure suivante s'applique : {_format_list_prose(rej_items)} avec notification du motif."
        )

    hist_ans = answers.get("history", "").lower()
    if "non" not in hist_ans and hist_ans != "":
        model.history_requirements.append(
            "Conservation de l'historique complet des modifications et traçabilité des actions utilisateurs (piste d'audit)."
        )

    # 5. Security & Privacy
    sens_items = _split(answers.get("sensitive_information", ""))
    if sens_items:
        model.security_needs.append(
            f"Protection renforcée et confidentialité stricte pour : {_format_list_prose(sens_items)}."
        )
    else:
        model.security_needs.append(
            "Application des règles standards de sécurité : authentification obligatoire et chiffrement des flux."
        )

    # 6. Non-Functional & Constraints
    avail = answers.get("availability", "")
    if avail and "je ne sais pas" not in avail.lower():
        model.non_functional_requirements.append(
            f"Mode de fonctionnement et disponibilité : {avail}."
        )

    dev_items = _split(answers.get("devices", ""))
    if dev_items:
        model.non_functional_requirements.append(
            f"Compatibilité multi-supports : l'application doit être pleinement utilisable sur {_format_list_prose(dev_items)}."
        )

    lang_items = _split(answers.get("languages", ""))
    if lang_items:
        model.non_functional_requirements.append(
            f"Support multilingue : interface disponible en {_format_list_prose(lang_items)}."
        )

    # 7. MVP & Priorities
    model.mvp = _split(answers.get("mvp", ""))
    if not model.mvp:
        if main_features:
            model.mvp = main_features[:3]
        else:
            model.mvp = ["Consultation du tableau de bord", "Gestion des données principales"]
            points_to_validate.append("Le périmètre exact du MVP reste [À DÉFINIR] avec le responsable métier.")

    model.future_features = _split(answers.get("future_features", ""))
    model.constraints = _split(answers.get("special_constraints", ""))
    if answers.get("final_notes"):
        model.constraints.append(_clean_text(answers["final_notes"]))

    model.acceptance_criteria = build_acceptance_criteria(model)
    model.points_to_validate = points_to_validate
    return model


def build_acceptance_criteria(model: ProjectModel) -> list[str]:
    criteria = []
    if model.users:
        criteria.append(
            "Chaque profil d'utilisateur accède à l'application avec les privilèges strictement définis pour son rôle."
        )
    if model.functional_requirements:
        criteria.append(
            "L'ensemble des fonctionnalités identifiées comme indispensables (MVP) sont opérationnelles de bout en bout."
        )
    if model.document_requirements:
        criteria.append(
            "Les documents peuvent être déposés, consultés et téléchargés en toute sécurité par les utilisateurs autorisés."
        )
    if model.dashboard_requirements:
        criteria.append(
            "Le tableau de bord restitue fidèlement les indicateurs clés calculés à partir des données validées."
        )
    if model.report_requirements or model.export_requirements:
        criteria.append(
            "Les rapports et fichiers d'export sont générés correctement dans les formats retenus."
        )
    if model.validation_rules or model.rejection_rules:
        criteria.append(
            "Le circuit de validation et la gestion des rejets (avec motif) s'exécutent conformément aux règles métier établies."
        )
    if model.security_needs:
        criteria.append(
            "Les informations sensibles et confidentielles restent protégées et inaccessibles aux tiers non autorisés."
        )
    return criteria or [
        "Le Cahier des Charges est formellement validé par le responsable métier avant le démarrage des développements."
    ]
