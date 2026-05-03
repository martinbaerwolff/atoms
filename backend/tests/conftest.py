"""Pytest fixtures for Phase 1+: real Postgres via testcontainers + Alembic."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from app.deps import get_session
from app.main import app as fastapi_app
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

_BACKEND_DIR = Path(__file__).parent.parent


def _run_alembic(async_url: str) -> None:
    cfg = Config(str(_BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", async_url)
    cfg.set_main_option("script_location", str(_BACKEND_DIR / "alembic"))
    command.upgrade(cfg, "head")


@pytest.fixture(scope="session")
def pg_url() -> Iterator[str]:
    """Start a Postgres 17 container, run Alembic migrations, yield the async URL."""
    with PostgresContainer("postgres:17-alpine", driver="asyncpg") as pg:
        url = pg.get_connection_url()
        _run_alembic(url)
        yield url


@pytest.fixture
async def client(pg_url: str) -> AsyncIterator[AsyncClient]:
    """Per-test HTTPX client wired to a real Postgres session."""
    engine = create_async_engine(pg_url, echo=False)
    maker = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

    async def _override() -> AsyncIterator[AsyncSession]:
        async with maker() as session:
            yield session

    fastapi_app.dependency_overrides[get_session] = _override
    try:
        async with AsyncClient(
            transport=ASGITransport(app=fastapi_app), base_url="http://testserver"
        ) as c:
            yield c
    finally:
        fastapi_app.dependency_overrides.pop(get_session, None)
        await engine.dispose()
