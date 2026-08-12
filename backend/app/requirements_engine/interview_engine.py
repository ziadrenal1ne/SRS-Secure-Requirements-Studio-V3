from app.requirements_engine.question_bank import MAX_QUESTIONS, QUESTIONS


def _answer_says_no(answer: str) -> bool:
    lowered = answer.lower()
    return any(value in lowered for value in ["non", "aucun", "pas besoin", "sans document", "pas de carte"])


def should_skip(question: dict, answers: dict[str, str]) -> bool:
    qid = question["id"]
    if qid == "documents" and "document" in answers.get("main_features", "").lower():
        return False
    if qid in {"search", "dashboards", "maps", "reports", "exports", "notifications"}:
        features = answers.get("main_features", "").lower()
        if qid == "maps" and ("carte" in features or "cartographie" in features):
            return False
        if qid == "notifications" and "notification" in features:
            return False
    if qid == "maps" and _answer_says_no(answers.get("main_features", "")):
        return True
    return False


def next_question(answers: dict[str, str], asked_ids: set[str]) -> dict | None:
    if len(asked_ids) >= MAX_QUESTIONS:
        return None
    for question in QUESTIONS:
        if question["id"] in asked_ids:
            continue
        if should_skip(question, answers):
            continue
        return question
    return None
