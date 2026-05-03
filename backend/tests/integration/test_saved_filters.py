"""TDD tests for /saved-filters CRUD."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_saved_filter(client: AsyncClient) -> None:
    resp = await client.post(
        "/saved-filters",
        json={"slug": "filter-inbox", "name": "Inbox", "filter_json": {"inbox": True}},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["slug"] == "filter-inbox"
    assert data["filter_json"] == {"inbox": True}


@pytest.mark.asyncio
async def test_list_saved_filters(client: AsyncClient) -> None:
    await client.post("/saved-filters", json={"slug": "filter-a", "name": "A"})
    await client.post("/saved-filters", json={"slug": "filter-b", "name": "B"})
    resp = await client.get("/saved-filters")
    assert resp.status_code == 200
    slugs = {f["slug"] for f in resp.json()}
    assert "filter-a" in slugs
    assert "filter-b" in slugs


@pytest.mark.asyncio
async def test_get_saved_filter_by_id(client: AsyncClient) -> None:
    create = await client.post("/saved-filters", json={"slug": "filter-get", "name": "Get"})
    fid = create.json()["id"]
    resp = await client.get(f"/saved-filters/{fid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == fid


@pytest.mark.asyncio
async def test_update_saved_filter(client: AsyncClient) -> None:
    create = await client.post("/saved-filters", json={"slug": "filter-upd", "name": "Old"})
    fid = create.json()["id"]
    resp = await client.patch(f"/saved-filters/{fid}", json={"name": "New"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "New"


@pytest.mark.asyncio
async def test_delete_saved_filter_soft(client: AsyncClient) -> None:
    create = await client.post("/saved-filters", json={"slug": "filter-del", "name": "Del"})
    fid = create.json()["id"]
    resp = await client.delete(f"/saved-filters/{fid}")
    assert resp.status_code == 204
    get_resp = await client.get(f"/saved-filters/{fid}")
    assert get_resp.status_code == 404
