"""TDD tests for /projects CRUD."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient) -> None:
    resp = await client.post("/projects", json={"slug": "proj-1", "name": "Project One"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["slug"] == "proj-1"
    assert data["name"] == "Project One"
    assert data["status"] == "active"
    assert data["deleted_at"] is None


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient) -> None:
    await client.post("/projects", json={"slug": "proj-list-a", "name": "A"})
    await client.post("/projects", json={"slug": "proj-list-b", "name": "B"})
    resp = await client.get("/projects")
    assert resp.status_code == 200
    slugs = {p["slug"] for p in resp.json()}
    assert "proj-list-a" in slugs
    assert "proj-list-b" in slugs


@pytest.mark.asyncio
async def test_get_project_by_id(client: AsyncClient) -> None:
    create = await client.post("/projects", json={"slug": "proj-get", "name": "Get Me"})
    pid = create.json()["id"]
    resp = await client.get(f"/projects/{pid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == pid


@pytest.mark.asyncio
async def test_update_project(client: AsyncClient) -> None:
    create = await client.post("/projects", json={"slug": "proj-upd", "name": "Old"})
    pid = create.json()["id"]
    resp = await client.patch(f"/projects/{pid}", json={"name": "New"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "New"


@pytest.mark.asyncio
async def test_delete_project_soft(client: AsyncClient) -> None:
    create = await client.post("/projects", json={"slug": "proj-del", "name": "Delete Me"})
    pid = create.json()["id"]
    resp = await client.delete(f"/projects/{pid}")
    assert resp.status_code == 204
    # Confirm soft-deleted (not returned in list by default)
    get_resp = await client.get(f"/projects/{pid}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_project_returns_404(client: AsyncClient) -> None:
    resp = await client.get("/projects/00000000-0000-7000-8000-000000000000")
    assert resp.status_code == 404
