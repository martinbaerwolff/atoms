"""FastAPI dependencies. Re-exports `get_session` for routers."""

from __future__ import annotations

from app.db import get_session

__all__ = ["get_session"]
