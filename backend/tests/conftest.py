"""Shared pytest fixtures.

Phase 0: a minimal `client` that overrides the DB session with a fake
that handles `SELECT 1`. Real testcontainers-based fixtures land in
Phase 1 once we have a schema worth running migrations against.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any

import pytest
from app.deps import get_session
from app.main import app as fastapi_app
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


class _FakeResult:
    def __init__(self, value: int) -> None:
        self._value = value

    def scalar_one(self) -> int:
        return self._value


class _FakeSession:
    """Stand-in for AsyncSession that only knows SELECT 1."""

    async def execute(self, *_args: Any, **_kwargs: Any) -> _FakeResult:
        return _FakeResult(1)

    async def __aenter__(self) -> _FakeSession:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        return None


async def _override_session() -> AsyncIterator[_FakeSession]:
    yield _FakeSession()


@pytest.fixture
def app() -> Iterator[FastAPI]:
    fastapi_app.dependency_overrides[get_session] = _override_session
    try:
        yield fastapi_app
    finally:
        fastapi_app.dependency_overrides.pop(get_session, None)


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
