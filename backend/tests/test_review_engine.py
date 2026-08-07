import pytest

from app.domain.concept_catalog import CONCEPT_CATALOG
from app.domain.requirement_types import REQUIREMENT_TYPES
from app.domain.security_frameworks import SECURITY_CONTROLS
from app.services.knowledge_graph import KnowledgeGraphService
from app.services.requirement import RequirementService
from app.services.review_engine import EXPORT_APPROVAL_THRESHOLD, ReviewEngineService
from app.services.security_engine import SecurityEngineService
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
async def test_review_on_fresh_graph_runs_over_100_rules_and_fails_everything(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)

    review = await ReviewEngineService(db_session).run_review(project_id)

    assert review.rule_count > 100
    assert review.failed_count == review.rule_count  # nothing answered yet
    assert review.overall_score < EXPORT_APPROVAL_THRESHOLD
    assert review.approved_for_export is False


@pytest.mark.asyncio
async def test_rule_count_includes_all_expected_categories(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)

    review = await ReviewEngineService(db_session).run_review(project_id)
    rule_ids = {f["rule_id"] for f in review.findings}

    assert any(rid.startswith("CONCEPT-") for rid in rule_ids)
    assert len([rid for rid in rule_ids if rid.startswith("CONCEPT-")]) == len(CONCEPT_CATALOG)
    assert any(rid.startswith("DOMAIN-") for rid in rule_ids)
    assert len([rid for rid in rule_ids if rid.startswith("REQTYPE-")]) == len(REQUIREMENT_TYPES)
    assert len([rid for rid in rule_ids if rid.startswith("SECCTL-")]) == len(SECURITY_CONTROLS)
    for gap in (
        "GAP-stakeholders", "GAP-apis", "GAP-workflows", "GAP-reports", "GAP-notifications",
        "GAP-legal", "GAP-business-rules", "GAP-security-controls", "GAP-mobile",
        "GAP-deployment", "GAP-testing",
    ):
        assert gap in rule_ids


@pytest.mark.asyncio
async def test_review_improves_as_project_is_documented(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)
    review_service = ReviewEngineService(db_session)

    first = await review_service.run_review(project_id)
    first_score = first.overall_score

    await kg.apply_update(
        project_id, "business.objective", completion_delta=90,
        captured_data={"raw_answer": "Consolider les donnees beneficiaires du programme Al Moutmir."},
    )
    await kg.apply_update(
        project_id, "stakeholders.sponsor", completion_delta=90,
        captured_data={"raw_answer": "Le Directeur de la Transformation Digitale."},
    )
    await RequirementService(db_session).generate_missing(project_id)
    await SecurityEngineService(db_session).analyze(project_id)

    second = await review_service.run_review(project_id)

    assert second.overall_score > first_score
    findings_by_id = {f["rule_id"]: f for f in second.findings}
    assert findings_by_id["GAP-stakeholders"]["passed"] is True
    assert findings_by_id["GAP-business-rules"]["passed"] is True


@pytest.mark.asyncio
async def test_requirement_dependency_validity_rule_catches_dangling_reference(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)

    node = await kg.apply_update(project_id, "business.objective", completion_delta=90)
    req = await RequirementService(db_session).generate_for_node(project_id, node)
    # Corrupt the dependency list to point at a requirement that doesn't exist.
    req.dependencies = ["BR-999"]
    await db_session.commit()

    review = await ReviewEngineService(db_session).run_review(project_id)
    dep_finding = next(
        f for f in review.findings if f["rule_id"] == f"REQQ-{req.requirement_key}-deps-valid"
    )
    assert dep_finding["passed"] is False


@pytest.mark.asyncio
async def test_review_is_idempotent_upsert(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)
    service = ReviewEngineService(db_session)

    first = await service.run_review(project_id)
    first_id = first.id
    second = await service.run_review(project_id)
    assert first_id == second.id


@pytest.mark.asyncio
async def test_get_review_without_prior_run_raises(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)

    from app.exceptions import NotFoundError

    with pytest.raises(NotFoundError):
        await ReviewEngineService(db_session).get_review(project_id)


# --- API-level tests ---


@pytest.mark.asyncio
async def test_review_api_run_and_get(client, unique_email):
    project_id = await _create_project(client)

    run = await client.post(f"/api/v1/projects/{project_id}/review/run")
    assert run.status_code == 200
    body = run.json()
    assert body["rule_count"] > 100
    assert body["approved_for_export"] is False
    for key in (
        "completeness_score", "confidence_score", "security_score",
        "architecture_score", "business_score", "testing_score", "overall_score",
    ):
        assert key in body

    fetched = await client.get(f"/api/v1/projects/{project_id}/review")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == body["id"]


@pytest.mark.asyncio
async def test_review_get_without_run_returns_404(client, unique_email):
    project_id = await _create_project(client)

    resp = await client.get(f"/api/v1/projects/{project_id}/review")
    assert resp.status_code == 404


