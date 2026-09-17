"""Normalize business answers into a structured ProjectModel without inventing scope."""

from app.requirements_engine.models import ProjectModel

CUSTOM_PREFIX = "custom:"
COMMENT_PREFIX = "comment:"


def _clean_answer(value: str) -> str:
    return (
        (value or "")
        .replace("**", "")
        .replace(CUSTOM_PREFIX, "")
        .replace(COMMENT_PREFIX, "Commentaire : ")
        .strip()
    )


def _split(value: str) -> list[str]:
    normalized = _clean_answer(value)
    if not normalized:
        return []
    for separator in ["|", "\n", ";", ","]:
        normalized = normalized.replace(separator, ",")
    items: list[str] = []
    for chunk in normalized.split(","):
        cleaned = chunk.strip(" -\t.")
        if cleaned and not cleaned.lower().startswith("autre /"):
            items.append(cleaned)
    return items


def _text(value: str) -> str:
    cleaned = _clean_answer(value)
    if cleaned and not cleaned.endswith((".", "!", "?")):
        cleaned += "."
    return cleaned


def _join(items: list[str]) -> str:
    clean = [item for item in items if item]
    if len(clean) <= 1:
        return clean[0] if clean else ""
    if len(clean) == 2:
        return f"{clean[0]} et {clean[1]}"
    return ", ".join(clean[:-1]) + f" ainsi que {clean[-1]}"


def _yes(value: str) -> bool:
    lowered = value.lower()
    return "oui" in lowered or "peut" in lowered


def _explicit_detail(value: str) -> str:
    cleaned = _clean_answer(value)
    lowered = cleaned.lower().strip()
    if lowered in {"oui", "non", "peut-etre", "peut-être", "je ne sais pas"}:
        return ""
    if lowered.startswith("oui."):
        return cleaned[4:].strip()
    if lowered.startswith("oui,"):
        return cleaned[4:].strip()
    return cleaned


def build_project_model(answers: dict[str, str], fallback_name: str = "Projet") -> ProjectModel:
    model = ProjectModel(
        project_name=(_clean_answer(answers.get("project_name", "")) or fallback_name).strip(),
        raw_answers=answers,
    )
    points: list[str] = []

    model.context = {
        "objective": _text(answers.get("objective", "")),
        "problem": _text(answers.get("problem", "")),
        "current_situation": _text(answers.get("current_situation", "")),
        "expected_result": _text(answers.get("expected_result", "")),
        "secondary_objectives": [],
    }
    if not model.context["objective"]:
        points.append("L'objectif principal du projet reste à préciser.")
    if not model.context["problem"]:
        points.append("La problématique métier reste à préciser.")

    model.users = _split(answers.get("users", ""))
    if not model.users:
        points.append("Les profils utilisateurs restent à préciser.")
    if actions := _text(answers.get("user_actions", "")):
        model.role_requirements.append(f"Actions attendues par profil : {actions}")

    restricted = answers.get("restricted_information", "")
    restricted_detail = _explicit_detail(restricted)
    if restricted and "non" not in restricted.lower():
        model.role_requirements.append("Certaines informations doivent être visibles uniquement par les profils autorisés.")
        if restricted_detail:
            model.role_requirements.append(restricted_detail)

    features = _split(answers.get("main_features", ""))
    if features:
        model.functional_requirements.append(f"Périmètre fonctionnel principal : {_join(features)}.")
    if view := _text(answers.get("view_information", "")):
        model.data_requirements.append(f"Informations à consulter : {view}")
    if edit := _text(answers.get("edit_information", "")):
        model.data_requirements.append(f"Informations à ajouter ou modifier : {edit}")

    documents = answers.get("documents", "")
    doc_detail = _explicit_detail(documents)
    if _yes(documents) or doc_detail or any("document" in item.lower() for item in features):
        model.document_requirements.append(
            _text(doc_detail) if doc_detail else "Dépôt, consultation et téléchargement des documents nécessaires au processus métier."
        )

    search = _split(answers.get("search", ""))
    if search:
        model.search_requirements.append(f"Recherche et filtres par {_join(search)}.")
    if dashboards := _text(answers.get("dashboards", "")):
        model.dashboard_requirements.append(f"Tableaux de bord attendus : {dashboards}")
    if _yes(answers.get("maps", "")) or any("cartograph" in item.lower() for item in features):
        detail = _explicit_detail(answers.get("maps", ""))
        model.map_requirements.append(_text(detail) if detail else "Carte ou localisation à prévoir selon les données géographiques mentionnées.")
    reports = answers.get("reports", "")
    report_detail = _explicit_detail(reports)
    if _yes(reports) or report_detail or any("rapport" in item.lower() for item in features):
        model.report_requirements.append(_text(report_detail) if report_detail else "Rapports métier à générer à partir des données validées.")
    exports = _split(answers.get("exports", ""))
    if exports:
        model.export_requirements.append(f"Exports attendus : {_join(exports)}.")
    notifications = answers.get("notifications", "")
    notification_detail = _explicit_detail(notifications)
    if _yes(notifications) or notification_detail or any("notification" in item.lower() for item in features):
        model.notification_requirements.append(
            _text(notification_detail) if notification_detail else "Notifications liées aux événements importants du processus."
        )

    if workflow := _text(answers.get("main_workflow", "")):
        model.workflows.append(workflow)
    validation = answers.get("validation", "")
    validation_detail = _explicit_detail(validation)
    if _yes(validation):
        model.validation_rules.append(_text(validation_detail) if validation_detail else "Les informations concernées doivent être vérifiées ou validées avant leur confirmation.")
    elif "je ne sais" in validation.lower():
        points.append("Le besoin de validation métier reste à confirmer.")
    rejection = _split(answers.get("rejection", ""))
    if rejection:
        model.rejection_rules.append(f"En cas d'information incorrecte ou rejetée : {_join(rejection)}.")
    history = answers.get("history", "")
    if history and "non" not in history.lower():
        model.history_requirements.append("Historique des modifications à conserver pour les informations concernées.")

    sensitive = _split(answers.get("sensitive_information", ""))
    if sensitive:
        model.security_needs.append(f"Informations à protéger particulièrement : {_join(sensitive)}.")
    if restricted and "non" not in restricted.lower():
        model.security_needs.append("Accès différencié aux informations selon les rôles métier.")
    if constraint := _text(answers.get("special_constraints", "")):
        model.security_needs.append(f"Contraintes confirmées : {constraint}")
    if not model.security_needs:
        points.append("Les informations sensibles à protéger restent à préciser.")

    for key, label in [
        ("availability", "Mode de fonctionnement"),
        ("devices", "Appareils ciblés"),
        ("languages", "Langues attendues"),
    ]:
        values = _split(answers.get(key, ""))
        if values and "Je ne sais pas" not in values:
            model.non_functional_requirements.append(f"{label} : {_join(values)}.")

    model.mvp = [_text(answers.get("mvp", "")).rstrip(".")] if answers.get("mvp") else []
    model.future_features = [_text(answers.get("future_features", "")).rstrip(".")] if answers.get("future_features") else []
    if final_notes := _text(answers.get("final_notes", "")):
        model.constraints.append(final_notes)
    if not model.mvp:
        points.append("Les fonctionnalités indispensables du MVP restent à préciser.")

    model.acceptance_criteria = build_acceptance_criteria(model)
    model.points_to_validate = points
    return model


def build_acceptance_criteria(model: ProjectModel) -> list[str]:
    criteria: list[str] = []
    if model.users:
        criteria.append("Chaque profil utilisateur accède uniquement aux fonctions prévues pour son rôle.")
    if model.mvp:
        criteria.append("Les fonctionnalités indispensables de la première version sont utilisables de bout en bout.")
    if model.document_requirements:
        criteria.append("Les documents demandés peuvent être ajoutés, consultés et exportés par les utilisateurs autorisés.")
    if model.report_requirements or model.export_requirements:
        criteria.append("Les rapports ou exports demandés sont générés à partir des données réellement saisies.")
    if model.notification_requirements:
        criteria.append("Les notifications prévues sont déclenchées aux étapes clés du workflow.")
    if model.security_needs:
        criteria.append("Les informations déclarées sensibles ne sont accessibles qu'aux profils autorisés.")
    return criteria or ["Le cahier des charges est validé par le responsable métier avant le lancement du développement."]
