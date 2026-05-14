from __future__ import annotations

STRINGS: dict[str, str] = {
    # menu
    "menu.title": "Главное меню:",
    "menu.day_start": "▶️ Начать/продолжить день",
    "menu.stats": "📊 Статистика",
    "menu.schedule": "⏰ Расписание",
    "menu.flavor": "🎭 Тон бота",
    "menu.interval": "⏱ Интервал заданий",
    "menu.toggle": "⏸ Пауза / включить",
    "menu.language": "🌐 Язык",
    "menu.back": "⬅️ Назад",
    # start
    "start.welcome": (
        "<b>Анти-стул бот готов.</b>\n\n"
        "Я буду выдавать короткие задания в рабочее окно, блокировать кнопку «Готово» "
        "до реалистичного времени и иногда задавать контрольные вопросы.\n\n"
        "Сейчас расписание: <b>{day_start}–{day_end}</b>, интервал: <b>{break_every} мин</b>, "
        "тон: <b>{flavor}</b>."
    ),
    "start.choose_language": "Выбери язык:",
    "start.language_set": "Язык сохранён: <b>{lang}</b>.",
    # day
    "day.in_window": "Рабочий режим активен. Первое задание сейчас.",
    "day.out_of_window": (
        "Рабочий режим включён. Сейчас вне окна. Первое задание будет около <b>{when}</b>."
    ),
    "day.work_mode_on": "Рабочий режим включён.",
    # stats
    "stats.title": "<b>Статистика за сегодня</b>",
    "stats.body": (
        "<b>Статистика за сегодня</b>\n"
        "✅ Выполнено: {completed}\n"
        "⏭ Пропущено: {skipped}\n"
        "❌ Провалено/игнор: {failed}\n"
        "🔥 Streak: {streak}\n"
        "🚨 Давление: {pressure}\n\n"
        "{active_line}"
    ),
    "stats.active": "Активно: {title}, разблокировка через {left}.",
    "stats.no_active": "Нет активного задания.",
    # task
    "task.body": (
        "{intro}\n\n"
        "<b>{title}</b>\n"
        "{instruction}\n\n"
        "🔒 Кнопка «Готово» засчитается через: <b>{left}</b>\n"
        "Если нажмёшь раньше — бот заметит подозрительную попытку."
    ),
    "task.btn_done": "✅ Готово",
    "task.btn_hard": "😵 Слишком тяжело",
    "task.btn_skip": "⏭ Пропустить",
    "task.early": "Рано. Осталось {left}.",
    "task.closed": "Это задание уже закрыто.",
    "task.check_intro": "✅ Зачтено. Контрольный вопрос:\n\n<b>{question}</b>",
    "task.check_prompt": "Напиши коротко ответ на контрольный вопрос одним сообщением.",
    "task.question_answer": "Отвечу текстом",
    "task.question_skip": "Пропустить вопрос",
    "task.skipped_logged": "Записал. {msg}",
    "task.question_skipped": "Окей, вопрос пропущен. Но я это запомнил.",
    "task.fail_prefix": "❌",
    "task.nudge_prefix": "🔔",
    # settings
    "settings.schedule.current": (
        "Текущее расписание: <b>{day_start}–{day_end}</b>\nВыбери вариант или введи своё."
    ),
    "settings.schedule.custom_prompt": "Введи расписание одним сообщением в формате <b>11:00-18:00</b>.",
    "settings.schedule.bad_format": "Не понял. Формат должен быть таким: <b>11:00-18:00</b>.",
    "settings.schedule.saved": "Готово. Рабочее окно: <b>{day_start}–{day_end}</b>.",
    "settings.schedule.custom_button": "✍️ Ввести своё",
    "settings.flavor.prompt": "Выбери тон бота:",
    "settings.flavor.unknown": "Неизвестный тон.",
    "settings.flavor.saved": "Тон изменён: <b>{title}</b>.",
    "settings.interval.prompt": "Как часто выдавать задания в рабочее окно?",
    "settings.interval.saved": "Интервал изменён: <b>{minutes} минут</b>.",
    "settings.interval.minutes": "{n} мин",
    "settings.toggle.enabled": "Бот включён.",
    "settings.toggle.paused": "Бот поставлен на паузу.",
    "settings.language.prompt": "Выбери язык:",
    # daily goal
    "settings.goal.saved": "Дневная цель: <b>{n} заданий</b>.",
    "settings.goal.invalid": "Укажи цель от 1 до 20. Пример: /goal 5",
    # text fallback
    "text.fallback": "Я почти всё делаю кнопками. Открой меню 👇",
    "text.context_lost": "Контекст ответа потерян.",
    # throttle
    "throttle.too_fast": "Слишком часто, подожди немного.",
    # slash command descriptions
    "cmd.menu.desc": "Открыть главное меню",
    "cmd.stats.desc": "Статистика за сегодня",
    "cmd.pause.desc": "Поставить на паузу",
    "cmd.resume.desc": "Возобновить напоминания",
    "cmd.lang.desc": "Сменить язык",
    "cmd.quiet.desc": "Тихие часы",
    "cmd.did.desc": "Отметить как выполненное на N минут (по умолчанию 30)",
    "cmd.busy.desc": "Установить период занятости (приостанавливает задания)",
    "cmd.goal.desc": "Установить дневную цель",
    # weekly summary
    "summary.weekly": (
        "<b>Итоги за неделю</b>\n"
        "✅ Выполнено: {completed}\n"
        "⏭ Пропущено: {skipped}\n"
        "❌ Провалено: {failed}\n"
        "🔥 Лучший streak: {best_streak}"
    ),
    # snooze
    "task.btn_snooze": "⏸ Отложить {n} мин",
    "task.snooze_exhausted": "Больше нельзя откладывать это задание.",
    "task.snoozed": "Отложено на {n} мин. Разблокировка сдвинута.",
    # quiet hours
    "menu.quiet": "🔕 Тихие часы",
    "settings.quiet.prompt": "Выбери пресет тихих часов (задания будут паузироваться в этом окне):",
    "settings.quiet.saved": "Тихие часы: {start}–{end}.",
    "settings.quiet.off": "Тихие часы отключены.",
    # smart silence — /did и /busy
    "silence.did_logged": "Принято. Засчитано как выполненное. Пауза: {minutes} мин.",
    "silence.busy_set": "Режим занятости: задания приостановлены на {minutes} мин.",
    "silence.busy_capped": "Максимум {max} минут.",
    "silence.busy_usage": "Использование: /busy <минуты>. Пример: /busy 60",
    # baseline calibration
    "baseline.graduation": (
        "<b>Калибровка завершена!</b>\n\n"
        "Базовый период закончен. Теперь сложность будет адаптироваться под тебя. "
        "Отличная работа!"
    ),
    "baseline.progress": "Калибровка: выполнено {completed}/10 заданий. Продолжай!",
    # daily goal
    "goal.reached": ("<b>Дневная цель достигнута!</b>\n\n{msg}\n\nНа сегодня всё. До завтра!"),
    # streak insurance
    "streak.insurance_used": (
        "Streak спасён! Один бесплатный пропуск на этой неделе использован — серия сохранена."
    ),
    # anti-cheat
    "anti_cheat.followup": (
        "Уточни — опиши одну конкретную деталь из задания, которое ты только что сделал? "
        "(например: сколько повторений, где почувствовал нагрузку, куда смотрел)"
    ),
    "anti_cheat.hard_check_1": ("Перед началом — что первым бросилось тебе в глаза в комнате?"),
    "anti_cheat.hard_check_2": ("Во время задания — какой звук ты слышал на фоне?"),
    "anti_cheat.hard_check_3": ("Какой цвет или предмет был на уровне глаз во время упражнения?"),
}
