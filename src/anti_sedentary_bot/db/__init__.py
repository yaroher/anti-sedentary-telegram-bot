from __future__ import annotations

from pathlib import Path

from loguru import logger
from tortoise import Tortoise

from .config import TORTOISE_ORM

MIGRATIONS_DIR = Path("migrations")
APP_NAME = "models"


async def _run_aerich() -> bool:
    """Run aerich upgrade. Auto-init if first run. Returns True on success."""
    try:
        from aerich import Command
    except ImportError:
        logger.warning("aerich not installed, falling back to generate_schemas")
        return False

    cmd = Command(tortoise_config=TORTOISE_ORM, app=APP_NAME, location=str(MIGRATIONS_DIR))
    await cmd.init()

    app_dir = MIGRATIONS_DIR / APP_NAME
    has_revisions = app_dir.exists() and any(p.suffix == ".py" for p in app_dir.iterdir())

    if not has_revisions:
        logger.info("No aerich revisions, running init-db")
        await cmd.init_db(safe=True)
        return True

    logger.info("Applying aerich migrations")
    pending = await cmd.upgrade(run_in_transaction=True)
    if pending:
        logger.info("Applied migrations: {}", pending)
    else:
        logger.info("Schema up to date")
    return True


async def init_db() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    if not await _run_aerich():
        await Tortoise.generate_schemas(safe=True)
        logger.info("Schemas generated (no aerich)")


async def close_db() -> None:
    await Tortoise.close_connections()
