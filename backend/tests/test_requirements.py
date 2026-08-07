import pytest

from app.services.interview import InterviewService
from app.services.knowledge_graph import NODE_SUFFICIENT_THRESHOLD, KnowledgeGraphService
from app.services.requirement import RequirementService
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


# --- Service-level tests ---


@pytest.mark.asyncio
async def test_generate_for_node_is_idempotent_and_gated_by_threshold(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)
    req_service = RequirementService(db_session)

    node = await kg.apply_update(project_id, "business.objective", completion_delta=30)
    result = await req_service.generate_for_node(project_id, node)
    assert result is None  # below threshold, nothing generated

    node = await kg.apply_update(
        project_id, "business.objective", completion_delta=NODE_SUFFICIENT_THRESHOLD
    )
    first = await req_service.generate_for_node(project_id, node)
    assert first is not None
    assert first.requirement_key == "BR-001"
    assert first.requirement_type == "business"
    assert first.source_concept_key == "business.objective"

    second = await req_service.generate_for_node(project_id, node)
    assert second.id == first.id  # idempotent, no duplicate


@pytest.mark.asyncio
async def test_requirement_keys_increment_per_type(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)
    req_service = RequirementService(db_session)

    n1 = await kg.apply_update(project_id, "business.objective", completion_delta=90)
    n2 = await kg.apply_update(project_id, "business.success_metrics", completion_delta=90)
    n3 = await kg.apply_update(project_id, "stakeholders.sponsor", completion_delta=90)

    r1 = await req_service.generate_for_node(project_id, n1)
    r2 = await req_service.generate_for_node(project_id, n2)
    r3 = await req_service.generate_for_node(project_id, n3)  # also maps to "business"

    assert {r1.requirement_key, r2.requirement_key, r3.requirement_key} == {
        "BR-001", "BR-002", "BR-003",
    }


@pytest.mark.asyncio
async def test_dependency_requirement_keys_populated_when_available(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)
    req_service = RequirementService(db_session)

    objective_node = await kg.apply_update(project_id, "business.objective", completion_delta=90)
    objective_req = await req_service.generate_for_node(project_id, objective_node)

    metrics_node = await kg.apply_update(
        project_id, "business.success_metrics", completion_delta=90
    )
    metrics_req = await req_service.generate_for_node(project_id, metrics_node)

    assert objective_req.requirement_key in metrics_req.dependencies


@pytest.mark.asyncio
async def test_generate_missing_scans_whole_graph(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)
    req_service = RequirementService(db_session)

    await kg.apply_update(project_id, "business.objective", completion_delta=90)
    await kg.apply_update(project_id, "stakeholders.sponsor", completion_delta=90)
    await kg.apply_update(project_id, "users.primary_personas", completion_delta=50)  # below threshold

    created = await req_service.generate_missing(project_id)
    keys = {r.source_concept_key for r in created}
    assert "business.objective" in keys
    assert "stakeholders.sponsor" in keys
    assert "users.primary_personas" not in keys


@pytest.mark.asyncio
async def test_interview_answer_auto_generates_requirement_on_sufficiency(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)
    interview = InterviewService(db_session)

    await interview.start_or_resume(project_id)
    result = await interview.submit_answer(
        project_id,
        "Le projet vise a donner aux administrateurs regionaux une vue consolidee "
        "des beneficiaires du programme avec des indicateurs exportables, ce qui "
        "resout le probleme actuel de suivi manuel disperse entre plusieurs fichiers.",
    )
    assert result["interview_status"] == "active"

    req_service = RequirementService(db_session)
    requirements = await req_service.list_requirements(project_id)
    # Whether a requirement was created depends on whether the deterministic
    # heuristic pushed completion past threshold in one turn — assert on the
    # underlying mechanism instead of assuming a specific delta.
    objective_node_completion = next(
        n for n in (await kg.get_graph(project_id))[0] if n.concept_key == "business.objective"
    ).completion
    keys = {r.source_concept_key for r in requirements}
    if objective_node_completion >= NODE_SUFFICIENT_THRESHOLD:
        assert "business.objective" in keys
    else:
        assert "business.objective" not in keys


# --- API-level tests ---


@pytest.mark.asyncio
async def test_requirements_api_generate_list_update_and_matrix(client, unique_email):
    project_id = await _create_project(client)

    # Drive the KG directly to sufficiency via repeated long answers so we
    # don't depend on how many turns the heuristic needs.
    await client.post(f"/api/v1/projects/{project_id}/interview/start")
    for _ in range(3):
        state = await client.get(
            f"/api/v1/projects/{project_id}/interview/state"
        )
        if state.json()["status"] == "completed":
            break
        await client.post(
            f"/api/v1/projects/{project_id}/interview/answer",
            json={
                "answer": (
                    "Reponse longue et tres detaillee couvrant plusieurs aspects du sujet "
                    "aborde ici, avec des exemples concrets, des chiffres precis, un "
                    "contexte complet et des precisions supplementaires permettant de "
                    "bien cerner le besoin exprime, incluant les contraintes associees, "
                    "les acteurs concernes et les objectifs mesurables vises par ce point "
                    "precis du projet actuellement en cours de cadrage."
                )
            },
        )

    gen = await client.post(
        f"/api/v1/projects/{project_id}/requirements/generate"
    )
    assert gen.status_code == 200

    listed = await client.get(f"/api/v1/projects/{project_id}/requirements")
    assert listed.status_code == 200
    requirements = listed.json()
    assert len(requirements) >= 1
    first = requirements[0]
    for field in (
        "requirement_key", "priority", "business_goal", "actors", "acceptance_criteria",
        "dependencies", "security_controls", "database_tables", "api_endpoints",
        "test_cases", "risk", "owner", "status",
    ):
        assert field in first

    req_id = first["id"]
    updated = await client.patch(
        f"/api/v1/projects/{project_id}/requirements/{req_id}",
        json={"status": "approved", "owner": "Ziad Bennani"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "approved"
    assert updated.json()["owner"] == "Ziad Bennani"

    matrix = await client.get(
        f"/api/v1/projects/{project_id}/requirements/traceability-matrix"
    )
    assert matrix.status_code == 200
    assert len(matrix.json()) == len(requirements)


