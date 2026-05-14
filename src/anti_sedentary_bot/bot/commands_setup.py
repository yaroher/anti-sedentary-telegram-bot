from __future__ import annotations

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats
from loguru import logger

from ..i18n import t


async def setup_bot_commands(bot: Bot) -> None:
    """Register bot command list for Telegram autocomplete in both supported languages."""
    command_keys = ["menu", "stats", "pause", "resume", "lang", "quiet"]

    for lang_code in ("en", "ru"):
        commands = [
            BotCommand(command=key, description=t(lang_code, f"cmd.{key}.desc")) for key in command_keys
        ]
        await bot.set_my_commands(
            commands,
            scope=BotCommandScopeAllPrivateChats(),
            language_code=lang_code,
        )

    logger.info("Bot commands registered for en/ru")
