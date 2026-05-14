from __future__ import annotations

import asyncio
import contextlib
import signal

from loguru import logger

from .bot import build_bot, build_dispatcher
from .bot.commands_setup import setup_bot_commands
from .config import settings
from .db import close_db, init_db
from .logger import setup_logging
from .services.scheduler import build_scheduler


async def _main() -> None:
    setup_logging()
    logger.info("Starting anti-sedentary bot")

    await init_db()
    bot = build_bot()
    dp = build_dispatcher()
    scheduler = build_scheduler(bot)
    await setup_bot_commands(bot)

    # --- health server (optional) -------------------------------------------
    health_runner = None
    if settings.health_enabled:
        try:
            from .health import start_health

            health_runner = await start_health(bot, settings.health_host, settings.health_port)
        except Exception as exc:
            logger.warning("Health server failed to start (continuing without it): {}", exc)

    stop_event = asyncio.Event()

    def _stop(*_: object) -> None:
        logger.info("Shutdown signal received")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError):
            loop.add_signal_handler(sig, _stop)

    scheduler.start()
    polling_task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
    stop_task = asyncio.create_task(stop_event.wait())

    try:
        done, _pending = await asyncio.wait(
            {polling_task, stop_task},
            return_when=asyncio.FIRST_COMPLETED,
        )
        for t in done:
            if t is polling_task and t.exception() is not None:
                raise t.exception()  # type: ignore[misc]
    finally:
        logger.info("Stopping...")
        scheduler.shutdown(wait=False)
        await dp.stop_polling()
        if not polling_task.done():
            polling_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await polling_task
        if not stop_task.done():
            stop_task.cancel()
        if health_runner is not None:
            with contextlib.suppress(Exception):
                await health_runner.cleanup()
        await bot.session.close()
        await close_db()
        logger.info("Stopped")


def run() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    run()
