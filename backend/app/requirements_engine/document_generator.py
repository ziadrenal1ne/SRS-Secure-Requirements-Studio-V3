"""Professional deterministic Cahier des Charges generator."""

from app.requirements_engine.models import ProjectModel


def _clean(items: list[str]) -> list[str]:
    return [item.strip().lstrip("-• ").strip() for item in items if item and item.strip()]


def _join(items: list[str]) -> str:
    clean = _clean(items)
    if len(clean) <= 1:
        return clean[0] if clean else ""
    if len(clean) == 2:
        return f"{clean[0]} et {clean[1]}"
    return ", ".join(clean[:-1]) + f" ainsi que {clean[-1]}"


def _section(title: str, items: list[str], *, optional: bool = False) -> dict | None:
    cleaned = _clean(items)
    if optional and not cleaned:
        return None
    return {"title": title, "items": cleaned or ["[À PRÉCISER] Information non encore documentée."]}


def _objective_items(model: ProjectModel) -> list[str]:
    items = []
    if model.context.get("objective"):
        items.append(model.context["objective"])
    if model.data_requirements:
        items.append("Centraliser les informations métier nécessaires au fonctionnement de la plateforme.")
    if model.workflows or model.validation_rules:
        items.append("Structurer les processus métier et fiabiliser les étapes de traitement, validation ou correction.")
    if model.dashboard_requirements or model.report_requirements:
        items.append("Fournir des tableaux de bord et rapports exploitables pour le pilotage opérationnel.")
    if model.search_requirements:
        items.append("Faciliter la recherche, le filtrage et l'analyse des informations.")
    if model.document_requirements:
        items.append("Gérer les documents associés au processus avec contrôle d'accès et traçabilité.")
    if model.notification_requirements:
        items.append("Notifier les utilisateurs concernés lors des événements importants.")
    if model.security_needs:
        items.append("Protéger les informations sensibles et limiter l'accès selon les rôles métier.")
    if model.history_requirements:
        items.append("Conserver une trace des modifications et des actions importantes.")
    return items


def _scope_items(model: ProjectModel) -> list[str]:
    return [
        f"Inclus dans le périmètre : {_join(model.functional_requirements)}." if model.functional_requirements else "",
        f"MVP : {_join(model.mvp)}." if model.mvp else "MVP : [À PRÉCISER].",
        f"Évolutions futures : {_join(model.future_features)}." if model.future_features else "Évolutions futures : [À VALIDER].",
        "Hors périmètre : tout module, intégration ou automatisation non mentionné explicitement dans les besoins collectés reste [À VALIDER].",
    ]


def _users_items(model: ProjectModel) -> list[str]:
    items = ["| Profil | Accès | Actions principales | Restrictions |", "| --- | --- | --- | --- |"]
    if model.users:
        actions = " ".join(model.role_requirements) or "[À PRÉCISER]"
        restrictions = "Accès limité au périmètre autorisé." if model.security_needs else "[À PRÉCISER]"
        for user in model.users:
            items.append(f"| {user} | Fonctions liées à son rôle | {actions} | {restrictions} |")
    else:
        items.append("| [À PRÉCISER] | [À PRÉCISER] | [À PRÉCISER] | [À PRÉCISER] |")
    return items


def _data_items(model: ProjectModel) -> list[str]:
    items = ["| Catégorie | Données principales | Consultation | Création / modification | Sensibilité |", "| --- | --- | --- | --- | --- |"]
    data = model.data_requirements or ["[À PRÉCISER] Données métier principales."]
    sensitive = _join(model.security_needs) if model.security_needs else "[À PRÉCISER]"
    for idx, item in enumerate(data, start=1):
        items.append(f"| Données métier {idx} | {item} | Profils autorisés | Profils autorisés | {sensitive} |")
    if model.document_requirements:
        items.append(f"| Documents | {_join(model.document_requirements)} | Profils autorisés | Profils autorisés | Selon contenu du document |")
    return items


def _features_items(model: ProjectModel) -> list[str]:
    features = model.functional_requirements or ["Gestion des informations métier principales [À PRÉCISER]."]
    items = []
    for idx, feature in enumerate(features, start=1):
        items.extend([
            f"F-{idx:03d} — {feature}",
            "Description : le module doit permettre aux utilisateurs autorisés de réaliser les actions métier associées sans ressaisie inutile.",
            f"Acteurs concernés : {_join(model.users) if model.users else '[À PRÉCISER]'}.",
            "Préconditions : l'utilisateur est authentifié et dispose des droits nécessaires.",
            f"Données concernées : {_join(model.data_requirements) if model.data_requirements else '[À PRÉCISER]'}.",
            "Résultat attendu : l'information est enregistrée, consultable par les profils autorisés et traçable lorsque le processus l'exige.",
        ])
    return items


def _workflow_items(model: ProjectModel) -> list[str]:
    if not (model.workflows or model.validation_rules or model.rejection_rules):
        return ["[À PRÉCISER] Aucun workflow détaillé n'a été confirmé, mais les actions de création, modification et consultation devront être ordonnées dans les spécifications fonctionnelles."]
    items = [*model.workflows]
    if model.validation_rules:
        items.append("Étapes de validation : les informations concernées passent par une vérification avant confirmation.")
    if model.rejection_rules:
        items.extend(model.rejection_rules)
    if model.history_requirements:
        items.extend(model.history_requirements)
    items.append("Diagramme synthétique : Création / saisie → Traitement → Validation éventuelle → Acceptation ou rejet → Correction si nécessaire → Historique.")
    return items


def _business_rules(model: ProjectModel) -> list[str]:
    rules = []
    idx = 1
    if model.users:
        rules.append(f"RB-{idx:03d} — Un utilisateur ne peut accéder qu'aux fonctions correspondant à son profil."); idx += 1
    if model.security_needs:
        rules.append(f"RB-{idx:03d} — Les informations identifiées comme sensibles sont réservées aux profils autorisés."); idx += 1
    if model.validation_rules:
        rules.append(f"RB-{idx:03d} — Une information soumise à validation ne devient effective qu'après décision du profil habilité."); idx += 1
    if model.rejection_rules:
        rules.append(f"RB-{idx:03d} — Tout rejet doit permettre la correction ou le traitement prévu par la règle métier confirmée."); idx += 1
    if model.history_requirements:
        rules.append(f"RB-{idx:03d} — Les modifications importantes doivent rester traçables dans l'historique.")
    return rules or ["RB-001 — Les règles métier détaillées restent [À PRÉCISER]."]


def _dashboard_items(model: ProjectModel) -> list[str]:
    items = ["| Profil | Informations / KPI | Filtres | Actions |", "| --- | --- | --- | --- |"]
    kpis = _join(model.dashboard_requirements) if model.dashboard_requirements else "[À PRÉCISER]"
    filters = _join(model.search_requirements) if model.search_requirements else "[À VALIDER]"
    if model.users:
        for user in model.users:
            items.append(f"| {user} | {kpis} | {filters} | Consulter, filtrer, exporter selon droits |")
    else:
        items.append(f"| [À PRÉCISER] | {kpis} | {filters} | [À PRÉCISER] |")
    return items


def _security_items(model: ProjectModel) -> list[str]:
    items = [
        "Contrôle d'accès : gestion des droits par profil métier et application du principe du moindre privilège.",
        "Authentification : accès réservé aux utilisateurs authentifiés ; politique de session sécurisée [À VALIDER].",
    ]
    if model.security_needs:
        items.append(f"Protection des données : {_join(model.security_needs)}.")
    else:
        items.append("Protection des données : classification des informations sensibles [À PRÉCISER].")
    if model.document_requirements:
        items.append("Fichiers : validation des types de fichiers, contrôle des droits avant téléchargement et stockage sécurisé [RECOMMANDATION].")
    if model.history_requirements or model.validation_rules or model.export_requirements:
        items.append("Audit et traçabilité : journalisation des modifications, validations, rejets, imports, exports et actions sensibles.")
    items.append("Résilience : sauvegardes régulières et procédure de restauration [À VALIDER].")
    return items


def _acceptance_items(model: ProjectModel) -> list[str]:
    items = []
    for idx, criterion in enumerate(model.acceptance_criteria, start=1):
        items.append(f"AC-{idx:03d} — {criterion}")
    return items or ["AC-001 — Le cahier des charges est validé par le responsable métier avant développement."]


def build_cahier_des_charges(model: ProjectModel, completeness: int = 100) -> dict:
    sections: list[dict | None] = [
        _section("1. Contexte et problématique", [
            model.context.get("current_situation", ""),
            model.context.get("problem", ""),
            model.context.get("expected_result", ""),
            "La plateforme cible doit réduire les traitements manuels, fiabiliser les données et clarifier les responsabilités entre les profils utilisateurs.",
        ]),
        _section("2. Objectifs de la plateforme", _objective_items(model)),
        _section("3. Périmètre fonctionnel", _scope_items(model)),
        _section("4. Utilisateurs et permissions", _users_items(model)),
        _section("5. Données gérées", _data_items(model)),
        _section("6. Fonctionnalités principales", _features_items(model)),
        _section("7. Workflow métier", _workflow_items(model)),
        _section("8. Règles métier", _business_rules(model)),
        _section("9. Recherche, filtres et tableaux de bord", [*model.search_requirements, *_dashboard_items(model)], optional=False),
        _section("10. Documents, rapports et exports", [*model.document_requirements, *model.report_requirements, *model.export_requirements], optional=True),
        _section("11. Notifications", model.notification_requirements, optional=True),
        _section("12. Exigences de cybersécurité", _security_items(model)),
        _section("13. Exigences non fonctionnelles", model.non_functional_requirements or ["Performance, disponibilité, ergonomie et accessibilité : niveaux cibles [À DÉFINIR]."]),
        _section("14. Contraintes techniques", ["Architecture cible conceptuelle [RECOMMANDATION] : interface web responsive, backend applicatif, base de données, stockage documentaire, journalisation et supervision. Les choix technologiques détaillés restent [À VALIDER]."]),
        _section("15. MVP et évolutions futures", _scope_items(model)[1:3]),
        _section("16. Livrables attendus", ["Application fonctionnelle.", "Code source.", "Documentation utilisateur.", "Documentation technique.", "Plan de tests et recette.", "Guide d'installation ou de déploiement [À VALIDER]."]),
        _section("17. Critères d'acceptation", _acceptance_items(model)),
        _section("18. Risques, hypothèses et points à valider", [
            *model.points_to_validate,
            "Qualité et complétude des données initiales : [À PRÉCISER].",
            "Canaux de notification, fréquence des sauvegardes et exigences de disponibilité : [À VALIDER].",
        ]),
        _section("Diagramme fonctionnel synthétique", [
            "Utilisateurs → Authentification / autorisation → Modules métier → Données / documents → Workflows → Tableaux de bord / rapports / exports → Audit et sécurité.",
        ]),
    ]

    summary = model.context.get("objective") or f"Cadrage fonctionnel et technique du projet {model.project_name}."
    return {
        "title": f"Cahier des Charges - {model.project_name}",
        "summary": summary,
        "completeness_score": completeness,
        "points_to_confirm": model.points_to_validate,
        "sections": [section for section in sections if section],
        "project_model": model.__dict__,
    }
