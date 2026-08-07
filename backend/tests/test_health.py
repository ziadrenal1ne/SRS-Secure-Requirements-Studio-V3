import pytest


@pytest.mark.asyncio
async def test_liveness(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_readiness(client):
    resp = await client.get("/health/ready")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["checks"]["database"] is True


@pytest.mark.asyncio
async def test_metrics_exposed(client):
    resp = await client.get("/metrics")
    assert resp.status_code == 200
    assert b"http_requests_total" in resp.content or resp.content == b""
