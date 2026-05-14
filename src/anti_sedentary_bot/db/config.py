from __future__ import annotations

from ..config import settings

_url = settings.database_url

if _url.startswith("sqlite"):
    # SQLite does not support pool options — use plain DSN string.
    _connection: str | dict = _url
else:
    # asyncpg / PostgreSQL: pass credential dict with pool tuning.
    _connection = {
        "engine": "tortoise.backends.asyncpg",
        "credentials": {
            "dsn": _url,
            "minsize": settings.db_pool_minsize,
            "maxsize": settings.db_pool_maxsize,
            "connect_timeout": settings.db_connect_timeout,
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
