"""Smoke tests for the health endpoint."""

from __future__ import annotations

from httpx import AsyncClient


async def test_health_endpoint_reports_ok(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["db"] == "ok"
    assert body["version"]


async def test_root_returns_app_name(client: AsyncClient) -> None:
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"name": "atoms", "docs": "/docs"}
