from __future__ import annotations

from aiogram import Dispatcher

from . import admin, commands, health, menu, settings, start, tasks, text


def setup_routers(dp: Dispatcher) -> None:
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(commands.router)
    dp.include_router(menu.router)
    dp.include_router(tasks.router)
    dp.include_router(settings.router)
    dp.include_router(health.router)
    dp.include_router(text.router)
