from __future__ import annotations

from urllib.parse import urlparse

from ..config import settings

_url = settings.database_url

if _url.startswith("sqlite"):
    # SQLite: plain DSN string, no pool tuning.
    _connection: str | dict = _url
else:
    # asyncpg / PostgreSQL: parse URL into discrete credentials so we can pass pool options.
    # Tortoise's asyncpg backend treats `dsn` as a forbidden duplicate of the positional arg,
    # so we hand it explicit host/port/user/password/database.
    parsed = urlparse(_url)
    _connection = {
        "engine": "tortoise.backends.asyncpg",
        "credentials": {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 5432,
            "user": parsed.username or "",
            "password": parsed.password or "",
            "database": (parsed.path or "/").lstrip("/") or "postgres",
            "minsize": settings.db_pool_minsize,
            "maxsize": settings.db_pool_maxsize,
        },
    }

TORTOISE_ORM: dict = {
    "connections": {"default": _connection},
    "apps": {
        "models": {
            "models": ["anti_sedentary_bot.db.models", "aerich.models"],
            "default_connection": "default",
        }
    },
    "use_tz": True,
    "timezone": settings.timezone,
}
