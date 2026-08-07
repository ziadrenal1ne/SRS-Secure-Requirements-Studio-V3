"""Covers the actual project endpoints exposed by public_projects.py.

The application has no authentication layer: every project is owned by an
internal, auto-created FOCP organization/user record (see
`_internal_context` in app/routers/public_projects.py). These tests reflect
that reality rather than a login flow that no longer exists.
"""
import uuid

import pytest


@pytest.mark.asyncio
async def test_project_crud_lifecycle(client):
    create = await client.post(
        "/api/v1/projects",
        json={
            "name": "Plateforme de Gestion des Bénéficiaires",
            "short_name": "PGB Al Moutmir",
            "department": "Direction Agriculture",
            "description": "Suivi des bénéficiaires du programme Al Moutmir.",
        },
    )
    assert create.status_code == 201
    project = create.json()
    assert project["status"] == "en_cours"
    assert project["progress"] == 5

    listed = await client.get("/api/v1/projects")
    assert listed.status_code == 200
    assert any(p["id"] == project["id"] for p in listed.json())

    project_id = project["id"]
    fetched = await client.get(f"/api/v1/projects/{project_id}")
    assert fetched.status_code == 200

    updated = await client.patch(
        f"/api/v1/projects/{project_id}",
        json={"status": "en_revue", "progress": 42},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "en_revue"
    assert updated.json()["progress"] == 42

    deleted = await client.delete(f"/api/v1/projects/{project_id}")
    assert deleted.status_code == 204

    gone = await client.get(f"/api/v1/projects/{project_id}")
    assert gone.status_code == 404


@pytest.mark.asyncio
async def test_create_project_seeds_knowledge_graph(client):
    create = await client.post(
        "/api/v1/projects",
        json={"name": "Test Project", "short_name": "TP"},
    )
    assert create.status_code == 201
    project_id = create.json()["id"]

    kg = await client.get(f"/api/v1/projects/{project_id}/knowledge-graph")
    assert kg.status_code == 200
    assert len(kg.json()["nodes"]) > 0


@pytest.mark.asyncio
async def test_get_unknown_project_returns_404(client):
    resp = await client.get(f"/api/v1/projects/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_all_projects_share_the_internal_focp_organization(client):
    """There is no per-tenant isolation by design — every project created
    through this no-auth API belongs to the same internal FOCP org/owner."""
    first = await client.post("/api/v1/projects", json={"name": "A", "short_name": "A"})
    second = await client.post("/api/v1/projects", json={"name": "B", "short_name": "B"})
    assert first.json()["organization_id"] == second.json()["organization_id"]
    assert first.json()["owner_id"] == second.json()["owner_id"]
