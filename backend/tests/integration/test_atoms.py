"""TDD tests for /atoms CRUD + views."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_atom(client: AsyncClient) -> None:
    resp = await client.post(
        "/atoms",
        json={"slug": "atom-create-1", "content": "Hello world", "type": "note"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["slug"] == "atom-create-1"
    assert data["content"] == "Hello world"
    assert data["type"] == "note"
    assert data["inbox"] is True
    assert data["status"] == "open"


@pytest.mark.asyncio
async def test_list_atoms(client: AsyncClient) -> None:
    await client.post("/atoms", json={"slug": "atom-list-x", "content": "X"})
    await client.post("/atoms", json={"slug": "atom-list-y", "content": "Y"})
    resp = await client.get("/atoms")
    assert resp.status_code == 200
    slugs = {a["slug"] for a in resp.json()}
    assert "atom-list-x" in slugs
    assert "atom-list-y" in slugs


@pytest.mark.asyncio
async def test_get_atom_by_id(client: AsyncClient) -> None:
    create = await client.post("/atoms", json={"slug": "atom-get-1", "content": "Get me"})
    aid = create.json()["id"]
    resp = await client.get(f"/atoms/{aid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == aid


@pytest.mark.asyncio
async def test_update_atom_content(client: AsyncClient) -> None:
    create = await client.post("/atoms", json={"slug": "atom-upd-1", "content": "Old"})
    aid = create.json()["id"]
    resp = await client.patch(f"/atoms/{aid}", json={"content": "New", "inbox": False})
    assert resp.status_code == 200
    data = resp.json()
    assert data["content"] == "New"
    assert data["inbox"] is False


@pytest.mark.asyncio
async def test_delete_atom_soft(client: AsyncClient) -> None:
    create = await client.post("/atoms", json={"slug": "atom-del-1", "content": "Bye"})
    aid = create.json()["id"]
    resp = await client.delete(f"/atoms/{aid}")
    assert resp.status_code == 204
    get_resp = await client.get(f"/atoms/{aid}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_atom_returns_404(client: AsyncClient) -> None:
    resp = await client.get("/atoms/00000000-0000-7000-8000-000000000003")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_view_inbox(client: AsyncClient) -> None:
    await client.post("/atoms", json={"slug": "atom-inbox-1", "content": "Inbox", "inbox": True})
    await client.post(
        "/atoms", json={"slug": "atom-not-inbox-1", "content": "Not inbox", "inbox": False}
    )
    resp = await client.get("/views/inbox")
    assert resp.status_code == 200
    atoms = resp.json()
    slugs = {a["slug"] for a in atoms}
    assert "atom-inbox-1" in slugs
    assert "atom-not-inbox-1" not in slugs


@pytest.mark.asyncio
async def test_fulltext_search(client: AsyncClient) -> None:
    await client.post(
        "/atoms", json={"slug": "atom-search-unique", "content": "Suchbegriff Zeppelin"}
    )
    resp = await client.get("/atoms?q=Zeppelin")
    assert resp.status_code == 200
    slugs = {a["slug"] for a in resp.json()}
    assert "atom-search-unique" in slugs
