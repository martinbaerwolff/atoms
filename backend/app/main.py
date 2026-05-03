"""FastAPI application entrypoint."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Any

import structlog
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import dispose_engine, get_session
from app.settings import get_settings

SessionDep = Annotated[AsyncSession, Depends(get_session)]

log = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    log.info("startup", environment=settings.environment)
    try:
        yield
    finally:
        await dispose_engine()
        log.info("shutdown")


app = FastAPI(
    title="Atoms API",
    version="0.1.0",
    description="Personal Second Brain — atoms, people, meetings, projects.",
    lifespan=lifespan,
)

# Dev-only CORS so the Vite dev server (5173) can call the API on 8000.
# In production the frontend is served from the same origin via Caddy.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
async def health(session: SessionDep) -> dict[str, Any]:
    """Liveness + DB ping. Returns 200 with `db: "ok"` on a working stack."""
    db_status = "ok"
    try:
        result = await session.execute(text("SELECT 1"))
        if result.scalar_one() != 1:
            db_status = "unexpected"
    except Exception as exc:
        log.warning("db_ping_failed", error=str(exc))
        db_status = "error"
    return {"status": "ok", "db": db_status, "version": app.version}


@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    return {"name": "atoms", "docs": "/docs"}
