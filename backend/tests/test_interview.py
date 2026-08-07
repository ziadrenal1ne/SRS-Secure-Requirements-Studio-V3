import pytest

from app.services.interview import InterviewService
from app.services.knowledge_graph import KnowledgeGraphService
from tests.conftest import create_project


async def _create_project(client) -> str:
    """Creates a project through the real no-auth public API. The app has
    no authentication layer, so this is the actual project-creation path,
    not a stand-in for one."""
    create = await client.post(
        "/api/v1/projects",
        json={"name": "Test Project", "short_name": "TP"},
    )
    return create.json()["id"]


@pytest.mark.asyncio
async def test_start_interview_asks_first_question(client, unique_email):
    project_id = await _create_project(client)

    resp = await client.post(f"/api/v1/projects/{project_id}/interview/start")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "active"
    assert body["pending_concept_key"] == "business.objective"
    assert body["pending_question"]
    assert body["turns"] == []


@pytest.mark.asyncio
async def test_start_interview_is_idempotent_resume(client, unique_email):
    project_id = await _create_project(client)

    first = await client.post(f"/api/v1/projects/{project_id}/interview/start")
    second = await client.post(f"/api/v1/projects/{project_id}/interview/start")

    assert first.json()["id"] == second.json()["id"]
    assert first.json()["pending_question"] == second.json()["pending_question"]


@pytest.mark.asyncio
async def test_answer_records_turn_updates_kg_and_advances(client, unique_email):
    project_id = await _create_project(client)

    await client.post(f"/api/v1/projects/{project_id}/interview/start")

    answer = await client.post(
        f"/api/v1/projects/{project_id}/interview/answer",
        json={
            "answer": (
                "Le projet vise a consolider les donnees existantes des beneficiaires du "
                "programme Al Moutmir dans un tableau de bord analytique restreint aux "
                "administrateurs regionaux et nationaux."
            )
        },
    )
    assert answer.status_code == 200
    body = answer.json()
    assert body["concept_key"] == "business.objective"
    assert body["next_concept_key"] is not None
    assert body["next_concept_key"] != "business.objective"
    assert body["interview_status"] == "active"

    kg = await client.get(f"/api/v1/projects/{project_id}/knowledge-graph")
    objective_node = next(
        n for n in kg.json()["nodes"] if n["concept_key"] == "business.objective"
    )
    assert objective_node["completion"] > 0
    assert objective_node["captured_data"].get("raw_answer")

    state = await client.get(f"/api/v1/projects/{project_id}/interview/state")
    assert len(state.json()["turns"]) == 1
    assert state.json()["turns"][0]["concept_key"] == "business.objective"


@pytest.mark.asyncio
async def test_answer_without_active_session_fails(client, unique_email):
    project_id = await _create_project(client)

    resp = await client.post(
        f"/api/v1/projects/{project_id}/interview/answer",
        json={"answer": "Reponse sans session active."},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_interview_state_requires_started_session(client, unique_email):
    project_id = await _create_project(client)

    resp = await client.get(f"/api/v1/projects/{project_id}/interview/state")
    assert resp.status_code == 404


# --- Service-level tests exercising many turns and full completion ---


@pytest.mark.asyncio
async def test_full_interview_completes_and_never_repeats_question(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)

    interview = InterviewService(db_session)
    session = await interview.start_or_resume(project_id)
    assert session.status == "active"

    asked_questions_per_concept: dict[str, set[str]] = {}
    guard = 0
    while session.status == "active" and guard < 200:
        guard += 1
        concept = session.pending_concept_key
        question = session.pending_question
        assert concept is not None and question is not None

        seen = asked_questions_per_concept.setdefault(concept, set())
        assert question not in seen, f"Duplicate question asked for {concept}"
        seen.add(question)

        result = await interview.submit_answer(
            project_id,
            "Reponse detaillee et complete couvrant plusieurs aspects du sujet aborde "
            "avec des exemples concrets et des precisions utiles pour avancer.",
        )
        if result["interview_status"] == "completed":
            break
        session = await interview.get_state(project_id)

    assert guard < 200, "Interview did not converge — possible infinite loop"

    completion = await kg.project_completion(project_id)
    assert completion["overall_completion"] > 70
