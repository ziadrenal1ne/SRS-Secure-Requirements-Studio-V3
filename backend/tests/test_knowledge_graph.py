import pytest

from app.domain.concept_catalog import CONCEPT_CATALOG
from app.services.knowledge_graph import (
    DEPENDENCY_SATISFACTION_THRESHOLD,
    NODE_SUFFICIENT_THRESHOLD,
    KnowledgeGraphService,
)
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
async def test_project_creation_auto_seeds_graph(client, unique_email):
    project_id = await _create_project(client)

    resp = await client.get(f"/api/v1/projects/{project_id}/knowledge-graph")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["nodes"]) == len(CONCEPT_CATALOG)
    assert len(body["edges"]) > 0
    assert all(n["completion"] == 0 for n in body["nodes"])
    assert all(n["status"] == "not_started" for n in body["nodes"])


@pytest.mark.asyncio
async def test_double_seeding_conflicts(db_session):
    project = await create_project(db_session)
    project_id = project.id
    service = KnowledgeGraphService(db_session)
    await service.seed_project_graph(project_id)
    from app.exceptions import ConflictError

    with pytest.raises(ConflictError):
        await service.seed_project_graph(project_id)


@pytest.mark.asyncio
async def test_next_concept_respects_dependencies(db_session):
    project = await create_project(db_session)
    project_id = project.id
    service = KnowledgeGraphService(db_session)
    await service.seed_project_graph(project_id)

    first = await service.next_concept(project_id)
    assert first is not None
    # The highest-priority concept with no unmet dependencies must itself
    # have no dependencies (every dependency starts at 0 completion).
    assert first.concept_key == "business.objective"

    # Answering it should eventually unblock its dependents.
    await service.apply_update(
        project_id,
        "business.objective",
        captured_data={"answer": "Plateforme de suivi des beneficiaires"},
        completion_delta=DEPENDENCY_SATISFACTION_THRESHOLD + 10,
        confidence_delta=60,
    )

    second = await service.next_concept(project_id)
    assert second is not None
    assert second.concept_key != "business.objective"


@pytest.mark.asyncio
async def test_apply_update_transitions_status_and_clamps(db_session):
    project = await create_project(db_session)
    project_id = project.id
    service = KnowledgeGraphService(db_session)
    await service.seed_project_graph(project_id)

    node = await service.apply_update(
        project_id, "business.objective", completion_delta=30, confidence_delta=20
    )
    assert node.status == "in_progress"
    assert node.completion == 30

    node = await service.apply_update(
        project_id,
        "business.objective",
        completion_delta=NODE_SUFFICIENT_THRESHOLD,  # would overshoot 100
    )
    assert node.completion == 100  # clamped
    assert node.status == "completed"


@pytest.mark.asyncio
async def test_gaps_excludes_sufficiently_completed_nodes(db_session):
    project = await create_project(db_session)
    project_id = project.id
    service = KnowledgeGraphService(db_session)
    await service.seed_project_graph(project_id)

    await service.apply_update(
        project_id, "business.objective", completion_delta=NODE_SUFFICIENT_THRESHOLD
    )

    gaps = await service.compute_gaps(project_id)
    gap_keys = {g.concept_key for g in gaps}
    assert "business.objective" not in gap_keys
    assert len(gaps) == len(CONCEPT_CATALOG) - 1


@pytest.mark.asyncio
async def test_completion_summary_and_kg_endpoints(client, unique_email):
    project_id = await _create_project(client)

    gaps = await client.get(f"/api/v1/projects/{project_id}/knowledge-graph/gaps")
    assert gaps.status_code == 200
    assert len(gaps.json()) == len(CONCEPT_CATALOG)

    next_concept = await client.get(
        f"/api/v1/projects/{project_id}/knowledge-graph/next-concept"
    )
    assert next_concept.status_code == 200
    assert next_concept.json()["concept_key"] == "business.objective"

    completion = await client.get(
        f"/api/v1/projects/{project_id}/knowledge-graph/completion"
    )
    assert completion.status_code == 200
    body = completion.json()
    assert body["total_concepts"] == len(CONCEPT_CATALOG)
    assert body["overall_completion"] == 0.0
    assert "business" in body["by_domain"]


