"""Tiny UI helpers shared by handlers."""

from __future__ import annotations

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, Message


async def edit_or_send(
    message: Message,
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Edit the message in-place when possible; otherwise post a fresh one.

    Prevents the chat from filling up with menu copies on every click.
    """
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        # "message is not modified" / "message can't be edited" — fall back.
        await message.answer(text, reply_markup=reply_markup)
    except Exception:
        await message.answer(text, reply_markup=reply_markup)
