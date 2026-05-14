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
    # badges / achievements
    "badge.unlocked": "🏅 Значок получен!",
    "badge.streak_3": "🔥 Серия 3 задания — ты в ударе!",
    "badge.streak_7": "🔥 Серия 7 заданий — целая неделя momentum!",
    "badge.streak_30": "🔥 Серия 30 заданий — неудержимый!",
    "badge.streak_100": "🔥 Серия 100 заданий — легенда!",
    "badge.completed_50": "✅ 50 заданий выполнено — прочный фундамент!",
    "badge.completed_200": "✅ 200 заданий — ты серьёзен!",
    "badge.completed_1000": "✅ 1000 заданий — элитный двигатель!",
    "badge.early_bird": "🌅 Ранняя пташка — задания до 10:00 в 5+ дней!",
    "badge.night_owl": "🦉 Сова — активен после 18:00 в 5+ дней!",
    "badge.goal_streak_7": "🎯 Цель выполнена 7 дней подряд!",
    # daily summary
    "summary.daily": (
        "<b>Итоги дня</b>\n"
        "✅ Выполнено: {completed}\n"
        "⏭ Пропущено: {skipped}\n"
        "❌ Провалено: {failed}\n"
        "🔥 Streak: {streak}  |  Лучший: {best_streak}\n\n"
        "{goal_status}"
    ),
    "summary.goal_yes": "🎯 Цель дня достигнута — молодец!",
    "summary.goal_no": "📌 Цель дня не достигнута — попробуй завтра.",
    # insights
    "insights.header": "<b>Твоя персональная аналитика</b>",
    "insights.best_hour": "⭐ Лучший час: {hour}",
    "insights.worst_hour": "⚠️ Самый сложный час: {hour}",
    "insights.trends_header": "<b>Тренды по упражнениям (сложность)</b>",
    "insights.easier": "становится легче ↓",
    "insights.harder": "становится сложнее ↑",
    "insights.same": "стабильно →",
    "insights.no_data": "Данных пока недостаточно — выполняй задания!",
    # re-engagement
    "reengage.silent": "Привет! Давно не виделись. Готов вернуться в строй? 💪",
    # talk / coach mode
    "talk.intro": (
        "Режим тренера включён. Задавай вопросы о своей рутине, трудностях или целях.\n"
        "Ответы будут короткими и по делу."
    ),
    "talk.end_btn": "Завершить чат",
    "talk.ended": "Чат завершён. Вперёд, двигаться! 💪",
    "talk.timeout": "Долго болтаем — продолжим в другой раз. Пора двигаться!",
    # slash command descriptions (new)
    "cmd.insights.desc": "Тепловая карта и тренды",
    "cmd.talk.desc": "Чат с тренером",
    # health / partner additions
    "menu.health": "🏥 Здоровье",
    "settings.health.prompt": "Включи или выключи напоминания о здоровье:",
    "health.on": "ВКЛ",
    "health.off": "ВЫКЛ",
    "health.eye.label": "👁 Глаза",
    "health.hydration.label": "💧 Вода",
    "health.posture.label": "🪑 Осанка",
    "health.eye.message": "👁 <b>Перерыв для глаз!</b>\n\nПосмотри на предмет в 6 метрах от тебя в течение 20 секунд.\nНажми «Готово» когда закончишь.",
    "health.hydration.message": "💧 <b>Время пить воду!</b>\n\nВыпей стакан воды прямо сейчас.\nНажми «Готово» когда закончишь.",
    "health.posture.message": "🪑 <b>Проверь осанку!</b>\n\nСядь прямо, расслабь плечи, поставь стопы на пол.\nНажми «Готово» когда закончишь.",
    "health.eye.ack": "👁 Перерыв для глаз засчитан. Отлично!",
    "health.hydration.ack": "💧 Вода засчитана. Не забывай пить!",
    "health.posture.ack": "🪑 Осанка проверена. Так держать!",
    "health.hydration.count": "💧 Вода сегодня: <b>{count}</b> стак.",
    "health.btn_done": "✅ Готово",
    "partner.paired": "Партнёр установлен: <b>{name}</b>. Он получит уведомление, если ты пропустишь или провалишь задание.",
    "partner.added_by": "🤝 <b>{name}</b> добавил тебя как своего партнёра по ответственности.",
    "partner.not_found": "Пользователь @{username} не найден. Он должен сначала запустить бота.",
    "partner.self": "Нельзя добавить самого себя в партнёры.",
    "partner.current": "Твой текущий партнёр: <b>{name}</b>.",
    "partner.help": "Использование: /partner @username — установить партнёра по ответственности.",
    "partner.none": "У тебя нет партнёра.",
    "partner.unpaired": "Партнёр удалён.",
    "partner.partner_unpaired": "<b>{name}</b> удалил тебя из своих партнёров.",
    "partner.notify_fail": "❌ Твой партнёр <b>{name}</b> провалил задание: <i>{title}</i>.",
    "partner.notify_skip": "⏭ Твой партнёр <b>{name}</b> пропустил задание: <i>{title}</i>.",
    "cmd.water.desc": "Записать стакан воды",
    "cmd.partner.desc": "Установить партнёра по ответственности",
    "cmd.unpartner.desc": "Убрать партнёра по ответственности",
}
