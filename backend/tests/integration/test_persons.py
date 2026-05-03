"""TDD tests for /persons CRUD."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_person(client: AsyncClient) -> None:
    resp = await client.post(
        "/persons",
        json={"slug": "mueller-thomas", "name": "Thomas Müller", "email": "t@example.com"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["slug"] == "mueller-thomas"
    assert data["email"] == "t@example.com"


@pytest.mark.asyncio
async def test_list_persons(client: AsyncClient) -> None:
    await client.post("/persons", json={"slug": "person-list-a", "name": "Alpha"})
    await client.post("/persons", json={"slug": "person-list-b", "name": "Beta"})
    resp = await client.get("/persons")
    assert resp.status_code == 200
    slugs = {p["slug"] for p in resp.json()}
    assert "person-list-a" in slugs
    assert "person-list-b" in slugs


@pytest.mark.asyncio
async def test_get_person_by_id(client: AsyncClient) -> None:
    create = await client.post("/persons", json={"slug": "person-get", "name": "Get Me"})
    pid = create.json()["id"]
    resp = await client.get(f"/persons/{pid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == pid


@pytest.mark.asyncio
async def test_update_person(client: AsyncClient) -> None:
    create = await client.post("/persons", json={"slug": "person-upd", "name": "Old Name"})
    pid = create.json()["id"]
    resp = await client.patch(f"/persons/{pid}", json={"name": "New Name"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_person_soft(client: AsyncClient) -> None:
    create = await client.post("/persons", json={"slug": "person-del", "name": "Delete Me"})
    pid = create.json()["id"]
    resp = await client.delete(f"/persons/{pid}")
    assert resp.status_code == 204
    get_resp = await client.get(f"/persons/{pid}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_person_returns_404(client: AsyncClient) -> None:
    resp = await client.get("/persons/00000000-0000-7000-8000-000000000001")
    assert resp.status_code == 404
