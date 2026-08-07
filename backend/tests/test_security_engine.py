import pytest

from app.domain.security_frameworks import SECURITY_CONTROLS
from app.services.knowledge_graph import KnowledgeGraphService
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
async def test_analyze_on_freshly_seeded_graph_flags_everything_missing(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)

    analysis = await SecurityEngineService(db_session).analyze(project_id)

    assert len(analysis.security_checklist) == len(SECURITY_CONTROLS)
    assert all(c["status"] == "missing" for c in analysis.security_checklist)
    assert analysis.security_score == 0
    assert len(analysis.threat_model) > 0
    assert all(t["status"] == "gap" for t in analysis.threat_model)


@pytest.mark.asyncio
async def test_mfa_detection_requires_keyword_not_just_completion(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)

    # Authentication is thoroughly answered, but without mentioning MFA.
    await kg.apply_update(
        project_id,
        "security.authentication_method",
        captured_data={"raw_answer": "Authentification par identifiant et mot de passe via LDAP."},
        completion_delta=90,
    )

    analysis = await SecurityEngineService(db_session).analyze(project_id)
    checklist_by_key = {c["control_key"]: c for c in analysis.security_checklist}

    assert checklist_by_key["authentication"]["status"] == "present"
    assert checklist_by_key["mfa"]["status"] == "missing"


@pytest.mark.asyncio
async def test_mfa_detected_present_when_mentioned(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)

    await kg.apply_update(
        project_id,
        "security.authentication_method",
        captured_data={
            "raw_answer": "SSO d'entreprise avec authentification multifacteur obligatoire pour les administrateurs."
        },
        completion_delta=90,
    )

    analysis = await SecurityEngineService(db_session).analyze(project_id)
    checklist_by_key = {c["control_key"]: c for c in analysis.security_checklist}
    assert checklist_by_key["mfa"]["status"] == "present"


@pytest.mark.asyncio
async def test_analyze_is_idempotent_upsert_not_duplicate(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)
    service = SecurityEngineService(db_session)

    first = await service.analyze(project_id)
    first_id = first.id
    first_score = first.security_score
    await kg.apply_update(
        project_id, "security.authentication_method", completion_delta=90,
        captured_data={"raw_answer": "SSO avec MFA."},
    )
    second = await service.analyze(project_id)

    assert first_id == second.id
    assert second.security_score > first_score


@pytest.mark.asyncio
async def test_risk_register_only_includes_high_and_critical_risk_nodes(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)

    analysis = await SecurityEngineService(db_session).analyze(project_id)
    nodes, _ = await kg.get_graph(project_id)
    by_key = {n.concept_key: n for n in nodes}

    for entry in analysis.risk_register:
        node = by_key[entry["source_concept_key"]]
        assert node.risk in ("high", "critical")


@pytest.mark.asyncio
async def test_rbac_matrix_reflects_requirement_actors(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)

    from app.services.requirement import RequirementService

    node = await kg.apply_update(project_id, "security.authentication_method", completion_delta=90)
    await RequirementService(db_session).generate_for_node(project_id, node)

    analysis = await SecurityEngineService(db_session).analyze(project_id)
    assert "Utilisateur" in analysis.rbac_matrix["roles"]
    assert "Administrateur systeme" in analysis.rbac_matrix["roles"]
    assert analysis.rbac_matrix["roles"]["Administrateur systeme"]["administer"] is True


@pytest.mark.asyncio
async def test_privacy_impact_assessment_never_invents_legal_basis(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)

    analysis = await SecurityEngineService(db_session).analyze(project_id)
    pia = analysis.privacy_impact_assessment
    assert "juridique" in pia["legal_basis"].lower() or "validation" in pia["legal_basis"].lower()


@pytest.mark.asyncio
async def test_analyze_syncs_project_security_score(db_session):
    project = await create_project(db_session)
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)

    analysis = await SecurityEngineService(db_session).analyze(project_id)
    await db_session.refresh(project)
    assert project.security_score == analysis.security_score


# --- API-level tests ---


@pytest.mark.asyncio
async def test_security_analyze_and_get_api(client, unique_email):
    project_id = await _create_project(client)

    analyze = await client.post(f"/api/v1/projects/{project_id}/security/analyze")
    assert analyze.status_code == 200
    body = analyze.json()
    assert len(body["security_checklist"]) == len(SECURITY_CONTROLS)
    assert "security_score" in body

    fetched = await client.get(f"/api/v1/projects/{project_id}/security")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == body["id"]


@pytest.mark.asyncio
async def test_security_get_without_prior_analyze_returns_404(client, unique_email):
    project_id = await _create_project(client)

    resp = await client.get(f"/api/v1/projects/{project_id}/security")
    assert resp.status_code == 404


