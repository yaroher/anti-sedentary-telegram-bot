from __future__ import annotations

from aiogram import Bot

from ..db.models import Task, User
from ..i18n import t
from .keyboards import main_menu, task_keyboard
from .retry import safe_send


async def notify_new_task(bot: Bot, user: User, task: Task, text: str) -> None:
    await safe_send(
        lambda: bot.send_message(
            user.user_id,
            text,
            reply_markup=task_keyboard(user.language, task.id),
        )
    )


async def notify_nudge(bot: Bot, user: User, task: Task, msg: str) -> None:
    prefix = t(user.language, "task.nudge_prefix")
    await safe_send(
        lambda: bot.send_message(
            user.user_id,
            f"{prefix} {msg}\n\n<b>{task.instruction}</b>",
            reply_markup=task_keyboard(user.language, task.id),
        )
    )


async def notify_fail(bot: Bot, user: User, msg: str) -> None:
    prefix = t(user.language, "task.fail_prefix")
    await safe_send(
        lambda: bot.send_message(
            user.user_id,
            f"{prefix} {msg}",
            reply_markup=main_menu(user.language),
        )
    )


async def notify_simple(bot: Bot, user: User, text: str) -> None:
    """Send a plain message with the main menu keyboard."""
    await safe_send(
        lambda: bot.send_message(
            user.user_id,
            text,
            reply_markup=main_menu(user.language),
        )
    )


async def notify_anti_cheat_followup(bot: Bot, user: User, task: Task) -> None:
    """Send a follow-up message when suspicious activity is detected."""
    text = t(user.language, "anti_cheat.followup")
    await safe_send(
        lambda: bot.send_message(
            user.user_id,
            text,
        )
    )


async def notify_badge(bot: Bot, user: User, code: str) -> None:
    from ..i18n import LOCALES, normalize_locale

    loc = normalize_locale(user.language)
    key = f"badge.{code}"
    badge_text = LOCALES[loc].get(key) or LOCALES["en"].get(key, "")
    unlocked = t(user.language, "badge.unlocked")
    text = f"{unlocked}\n\n{badge_text}" if badge_text else unlocked
    await safe_send(lambda: bot.send_message(user.user_id, text))


async def notify_health(bot: Bot, user: User, kind: str) -> None:
    """Send a health-track reminder with a Done button."""
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    from .callbacks import HealthCb

    b = InlineKeyboardBuilder()
    b.button(text=t(user.language, "health.btn_done"), callback_data=HealthCb(kind=kind))
    markup = b.as_markup()

    msg = t(user.language, f"health.{kind}.message")
    await safe_send(lambda: bot.send_message(user.user_id, msg, reply_markup=markup))
