from __future__ import annotations

from aiogram import Dispatcher

from . import commands, menu, settings, start, tasks, text


def setup_routers(dp: Dispatcher) -> None:
    dp.include_router(start.router)
    dp.include_router(commands.router)
    dp.include_router(menu.router)
    dp.include_router(tasks.router)
    dp.include_router(settings.router)
    dp.include_router(text.router)
