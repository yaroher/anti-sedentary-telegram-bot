from __future__ import annotations

import time

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger

from ...config import settings
from ...db.models import User
from ...i18n import t
from ...services.llm import get_client
from ..callbacks import AdminCb

router = Router(name="admin")


def _is_admin(user: User) -> bool:
    return user.user_id in settings.admin_ids


def _admin_keyboard(locale: str):
    b = InlineKeyboardBuilder()
    b.button(text=t(locale, "admin.btn_test_llm"), callback_data=AdminCb(action="test_llm"))
    b.adjust(1)
    return b.as_markup()


@router.message(Command("admin"))
async def cmd_admin(message: Message, user: User) -> None:
    if not _is_admin(user):
        return  # silent — non-admins shouldn't even see the command exists
    await message.answer(
        t(user.language, "admin.menu", provider=settings.llm_provider, model=settings.llm_model),
        reply_markup=_admin_keyboard(user.language),
    )


@router.callback_query(AdminCb.filter(F.action == "test_llm"))
async def cb_test_llm(query: CallbackQuery, user: User) -> None:
    if not _is_admin(user):
        await query.answer()
        return

    client = get_client()
    if client is None:
        await query.message.answer(
            t(
                user.language,
                "admin.llm_disabled",
                provider=settings.llm_provider,
                model=settings.llm_model,
            )
        )
        await query.answer()
        return

    started = time.monotonic()
    try:
        resp = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": "Reply with exactly: pong"},
                {"role": "user", "content": "ping"},
            ],
            temperature=0.0,
            max_tokens=10,
        )
        elapsed_ms = int((time.monotonic() - started) * 1000)
        content = (resp.choices[0].message.content or "").strip()
        await query.message.answer(
            t(
                user.language,
                "admin.llm_ok",
                provider=settings.llm_provider,
                model=settings.llm_model,
                base_url=settings.llm_base_url,
                latency_ms=elapsed_ms,
                reply=content[:120],
            )
        )
    except Exception as exc:
        logger.exception("Admin LLM test failed")
        await query.message.answer(
            t(
                user.language,
                "admin.llm_error",
                provider=settings.llm_provider,
                model=settings.llm_model,
                error=str(exc)[:300],
            )
        )
    await query.answer()
