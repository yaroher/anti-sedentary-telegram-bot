from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from ..config import settings
from .handlers import setup_routers
from .middlewares import ThrottlingMiddleware, UserMiddleware


def build_bot() -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    # UserMiddleware first so user is resolved; ThrottlingMiddleware second.
    dp.message.middleware(UserMiddleware())
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(UserMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    setup_routers(dp)
    return dp
