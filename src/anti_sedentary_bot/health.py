"""Lightweight aiohttp health-check server.

/healthz  — liveness: DB connection open + bot session alive.
/readyz   — readiness: Telegram getMe() reachable (cached 60 s).
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from aiogram import Bot

try:
    from aiohttp.web import Application, AppRunner, Request, Response, TCPSite

    _AIOHTTP_AVAILABLE = True
except ImportError:  # pragma: no cover
    _AIOHTTP_AVAILABLE = False


# Cache for /readyz
_last_ready_ok: float = 0.0
_READY_TTL = 60.0


def _db_ok() -> bool:
    """Return True when Tortoise has at least one registered connection."""
    try:
        from tortoise import connections  # type: ignore[import-untyped]

        conn = connections.get("default")
        return conn is not None
    except Exception:
        return False


def _bot_session_ok(bot: Bot) -> bool:
    """Return True when the aiogram bot session has not been closed."""
    try:
        session = bot.session
        # AiogramSession exposes a `closed` attribute; fall back to True on error.
        return not getattr(session, "closed", False)
    except Exception:
        return False


def build_health_app(bot: Bot) -> Application:
    """Build and return the aiohttp application (not yet started)."""
    if not _AIOHTTP_AVAILABLE:
        raise RuntimeError("aiohttp is not installed — cannot build health app")

    app = Application()

    async def healthz(request: Request) -> Response:
        db_up = _db_ok()
        session_up = _bot_session_ok(bot)
        if db_up and session_up:
            return Response(text="ok", status=200)
        reason = []
        if not db_up:
            reason.append("db_down")
        if not session_up:
            reason.append("session_closed")
        return Response(text=",".join(reason), status=503)

    async def readyz(request: Request) -> Response:
        global _last_ready_ok
        now = time.monotonic()
        if now - _last_ready_ok < _READY_TTL:
            return Response(text="ready", status=200)
        try:
            await bot.get_me()
            _last_ready_ok = time.monotonic()
            return Response(text="ready", status=200)
        except Exception as exc:
            logger.warning("readyz: bot.get_me() failed: {}", exc)
            return Response(text="not_ready", status=503)

    app.router.add_get("/healthz", healthz)
    app.router.add_get("/readyz", readyz)
    return app


async def start_health(bot: Bot, host: str, port: int) -> AppRunner:
    """Start the health HTTP server; return the runner so the caller can stop it."""
    app = build_health_app(bot)
    runner = AppRunner(app, access_log=None)
    await runner.setup()
    site = TCPSite(runner, host, port)
    await site.start()
    logger.info("Health server listening on {}:{}", host, port)
    return runner
