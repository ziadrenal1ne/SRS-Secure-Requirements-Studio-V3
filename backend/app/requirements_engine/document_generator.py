"""Document generator that turns a ProjectModel into a structured, professional Cahier des Charges.
Conforms strictly to the 10-section Business Analyst specification (3–5 pages target).
"""

from app.requirements_engine.models import ProjectModel


def _sec(title: str, items: list[str]) -> dict | None:
    clean = [i.strip() for i in items if i and i.strip()]
    return {"title": title, "items": clean} if clean else None


def build_cahier_des_charges(model: ProjectModel, completeness: int = 100) -> dict:
    sections: list[dict] = []

    # 1. CONTEXTE ET PROBLÉMATIQUE
    ctx_items = []
    if model.context.get("current_situation"):
        ctx_items.append(f"Situation actuelle : {model.context['current_situation']}")
    if model.context.get("problem"):
        ctx_items.append(f"Problématique : {model.context['problem']}")
    if not ctx_items:
        ctx_items.append(f"Présentation du projet {model.project_name} et de son environnement opérationnel.")
    sec1 = _sec("1. CONTEXTE ET PROBLÉMATIQUE", ctx_items)
    if sec1:
        sections.append(sec1)

    # 2. OBJECTIFS DE LA PLATEFORME
    obj_items = []
    if model.context.get("objective"):
        obj_items.append(f"Objectif principal : {model.context['objective']}")
    if model.context.get("expected_result"):
        obj_items.append(f"Résultats attendus : {model.context['expected_result']}")
    if not obj_items:
        obj_items.append(f"Déploiement d'une solution numérique adaptée aux besoins exprimés pour {model.project_name}.")
    sec2 = _sec("2. OBJECTIFS DE LA PLATEFORME", obj_items)
    if sec2:
        sections.append(sec2)

    # 3. UTILISATEURS ET PÉRIMÈTRE
    user_items = []
    if model.users:
        user_items.append(f"Profils identifiés : {', '.join(model.users)}.")
    user_items.extend(model.role_requirements)
    sec3 = _sec("3. UTILISATEURS ET PÉRIMÈTRE", user_items)
    if sec3:
        sections.append(sec3)

    # 4. FONCTIONNALITÉS PRINCIPALES (Subsections included dynamically)
    func_items = []
    if model.functional_requirements:
        func_items.extend(model.functional_requirements)
    if model.data_requirements:
        func_items.extend(model.data_requirements)
    if model.document_requirements:
        func_items.extend(model.document_requirements)
    if model.search_requirements:
        func_items.extend(model.search_requirements)
    if model.dashboard_requirements:
        func_items.extend(model.dashboard_requirements)
    if model.report_requirements or model.export_requirements:
        func_items.extend(model.report_requirements)
        func_items.extend(model.export_requirements)
    if model.notification_requirements:
        func_items.extend(model.notification_requirements)
    if model.map_requirements:
        func_items.extend(model.map_requirements)

    if not func_items:
        func_items.append("Consultation et gestion des données métier de l'application.")

    sec4 = _sec("4. FONCTIONNALITÉS PRINCIPALES", func_items)
    if sec4:
        sections.append(sec4)

    # 5. PROCESSUS MÉTIER
    wf_items = []
    wf_items.extend(model.workflows)
    wf_items.extend(model.validation_rules)
    wf_items.extend(model.rejection_rules)
    wf_items.extend(model.history_requirements)
    if not wf_items:
        wf_items.append("Saisie directe et mise à jour simple des données par les utilisateurs autorisés.")
    sec5 = _sec("5. PROCESSUS MÉTIER", wf_items)
    if sec5:
        sections.append(sec5)

    # 6. EXIGENCES DE SÉCURITÉ ET DE CONFIDENTIALITÉ
    sec_items = []
    sec_items.extend(model.security_needs)
    if not sec_items:
        sec_items.append("Authentification obligatoire, gestion stricte des droits d'accès et protection des données.")
    sec6 = _sec("6. EXIGENCES DE SÉCURITÉ ET DE CONFIDENTIALITÉ", sec_items)
    if sec6:
        sections.append(sec6)

    # 7. EXIGENCES NON FONCTIONNELLES
    nfr_items = []
    nfr_items.extend(model.non_functional_requirements)
    nfr_items.extend(model.constraints)
    if not nfr_items:
        nfr_items.append("Interface intuitive, disponible en ligne avec des temps de réponse adaptés.")
    sec7 = _sec("7. EXIGENCES NON FONCTIONNELLES", nfr_items)
    if sec7:
        sections.append(sec7)

    # 8. MVP — FONCTIONNALITÉS INDISPENSABLES
    mvp_items = [f"• {item}" if not item.startswith("•") else item for item in model.mvp]
    sec8 = _sec("8. MVP — FONCTIONNALITÉS INDISPENSABLES", mvp_items)
    if sec8:
        sections.append(sec8)

    # 9. ÉVOLUTIONS FUTURES
    fut_items = [f"• {item}" if not item.startswith("•") else item for item in model.future_features]
    if fut_items:
        sections.append(_sec("9. ÉVOLUTIONS FUTURES", fut_items))
    else:
        sections.append(_sec("9. ÉVOLUTIONS FUTURES", ["Aucune évolution secondaire identifiée pour la phase initiale."]))

    # 10. CRITÈRES D'ACCEPTATION
    sec10 = _sec("10. CRITÈRES D'ACCEPTATION", model.acceptance_criteria)
    if sec10:
        sections.append(sec10)

    # 11. POINTS À VALIDER (Optional section for unresolved decisions)
    if model.points_to_validate:
        sec11 = _sec("11. POINTS À VALIDER", model.points_to_validate)
        if sec11:
            sections.append(sec11)

    summary = model.context.get("objective") or f"Cadrage fonctionnel et spécifications du projet {model.project_name}."

    return {
        "title": f"Cahier des Charges — {model.project_name}",
        "summary": summary,
        "completeness_score": completeness,
        "points_to_confirm": model.points_to_validate,
        "sections": sections,
        "project_model": model.__dict__,
    }
