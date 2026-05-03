"""TDD tests for /meetings CRUD."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_meeting(client: AsyncClient) -> None:
    resp = await client.post(
        "/meetings",
        json={"slug": "meet-kickoff", "title": "Kickoff", "date": "2026-05-03T10:00:00Z"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["slug"] == "meet-kickoff"
    assert data["title"] == "Kickoff"


@pytest.mark.asyncio
async def test_list_meetings(client: AsyncClient) -> None:
    await client.post("/meetings", json={"slug": "meet-list-a", "title": "A"})
    await client.post("/meetings", json={"slug": "meet-list-b", "title": "B"})
    resp = await client.get("/meetings")
    assert resp.status_code == 200
    slugs = {m["slug"] for m in resp.json()}
    assert "meet-list-a" in slugs
    assert "meet-list-b" in slugs


@pytest.mark.asyncio
async def test_get_meeting_by_id(client: AsyncClient) -> None:
    create = await client.post("/meetings", json={"slug": "meet-get", "title": "Get Me"})
    mid = create.json()["id"]
    resp = await client.get(f"/meetings/{mid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == mid


@pytest.mark.asyncio
async def test_update_meeting(client: AsyncClient) -> None:
    create = await client.post("/meetings", json={"slug": "meet-upd", "title": "Old"})
    mid = create.json()["id"]
    resp = await client.patch(f"/meetings/{mid}", json={"title": "New"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "New"


@pytest.mark.asyncio
async def test_delete_meeting_soft(client: AsyncClient) -> None:
    create = await client.post("/meetings", json={"slug": "meet-del", "title": "Delete Me"})
    mid = create.json()["id"]
    resp = await client.delete(f"/meetings/{mid}")
    assert resp.status_code == 204
    get_resp = await client.get(f"/meetings/{mid}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_meeting_returns_404(client: AsyncClient) -> None:
    resp = await client.get("/meetings/00000000-0000-7000-8000-000000000002")
    assert resp.status_code == 404
