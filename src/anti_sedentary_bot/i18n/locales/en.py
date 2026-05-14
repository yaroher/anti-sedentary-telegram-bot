from __future__ import annotations

STRINGS: dict[str, str] = {
    # menu
    "menu.title": "Main menu:",
    "menu.day_start": "▶️ Start / continue day",
    "menu.stats": "📊 Stats",
    "menu.schedule": "⏰ Schedule",
    "menu.flavor": "🎭 Bot tone",
    "menu.interval": "⏱ Task interval",
    "menu.toggle": "⏸ Pause / enable",
    "menu.language": "🌐 Language",
    "menu.back": "⬅️ Back",
    # start
    "start.welcome": (
        "<b>Anti-sedentary bot ready.</b>\n\n"
        "I'll send short tasks during your work window, lock the «Done» button until a realistic time, "
        "and sometimes ask a check question.\n\n"
        "Now: schedule <b>{day_start}–{day_end}</b>, interval <b>{break_every} min</b>, "
        "tone <b>{flavor}</b>."
    ),
    "start.choose_language": "Choose your language:",
    "start.language_set": "Language set: <b>{lang}</b>.",
    # day
    "day.in_window": "Work mode active. First task now.",
    "day.out_of_window": ("Work mode enabled. Outside window now. First task around <b>{when}</b>."),
    "day.work_mode_on": "Work mode on.",
    # stats
    "stats.title": "<b>Today's stats</b>",
    "stats.body": (
        "<b>Today's stats</b>\n"
        "✅ Completed: {completed}\n"
        "⏭ Skipped: {skipped}\n"
        "❌ Failed/ignored: {failed}\n"
        "🔥 Streak: {streak}\n"
        "🚨 Pressure: {pressure}\n\n"
        "{active_line}"
    ),
    "stats.active": "Active: {title}, unlock in {left}.",
    "stats.no_active": "No active task.",
    # task message
    "task.body": (
        "{intro}\n\n"
        "<b>{title}</b>\n"
        "{instruction}\n\n"
        "🔒 «Done» counts in: <b>{left}</b>\n"
        "Press too early and the bot will flag a suspicious attempt."
    ),
    "task.btn_done": "✅ Done",
    "task.btn_hard": "😵 Too hard",
    "task.btn_skip": "⏭ Skip",
    "task.early": "Too early. {left} left.",
    "task.closed": "This task is already closed.",
    "task.check_intro": "✅ Counted. Check question:\n\n<b>{question}</b>",
    "task.check_prompt": "Reply briefly to the check question in one message.",
    "task.question_answer": "I'll answer in text",
    "task.question_skip": "Skip question",
    "task.skipped_logged": "Logged. {msg}",
    "task.question_skipped": "OK, question skipped. But I noticed.",
    "task.fail_prefix": "❌",
    "task.nudge_prefix": "🔔",
    # settings
    "settings.schedule.current": (
        "Current schedule: <b>{day_start}–{day_end}</b>\nPick a preset or enter your own."
    ),
    "settings.schedule.custom_prompt": "Send schedule in one message, format <b>11:00-18:00</b>.",
    "settings.schedule.bad_format": "Didn't get it. Format must be <b>11:00-18:00</b>.",
    "settings.schedule.saved": "Done. Work window: <b>{day_start}–{day_end}</b>.",
    "settings.schedule.custom_button": "✍️ Enter custom",
    "settings.flavor.prompt": "Pick bot tone:",
    "settings.flavor.unknown": "Unknown tone.",
    "settings.flavor.saved": "Tone changed: <b>{title}</b>.",
    "settings.interval.prompt": "How often should tasks come during the work window?",
    "settings.interval.saved": "Interval changed: <b>{minutes} minutes</b>.",
    "settings.interval.minutes": "{n} min",
    "settings.toggle.enabled": "Bot enabled.",
    "settings.toggle.paused": "Bot paused.",
    "settings.language.prompt": "Pick language:",
    # daily goal
    "settings.goal.saved": "Daily goal set: <b>{n} tasks</b>.",
    "settings.goal.invalid": "Please set a goal between 1 and 20. Usage: /goal <N>",
    # text fallback
    "text.fallback": "I mostly use buttons. Open the menu 👇",
    "text.context_lost": "Answer context lost.",
    # throttle
    "throttle.too_fast": "Too fast, slow down.",
    # slash command descriptions
    "cmd.menu.desc": "Open main menu",
    "cmd.stats.desc": "Show today's stats",
    "cmd.pause.desc": "Pause reminders",
    "cmd.resume.desc": "Resume reminders",
    "cmd.lang.desc": "Change language",
    "cmd.quiet.desc": "Set quiet hours",
    "cmd.did.desc": "Mark as done for N minutes (default 30)",
    "cmd.busy.desc": "Set busy period (pauses tasks)",
    "cmd.goal.desc": "Set daily task goal",
    # weekly summary
    "summary.weekly": (
        "<b>Weekly summary</b>\n"
        "✅ Completed: {completed}\n"
        "⏭ Skipped: {skipped}\n"
        "❌ Failed: {failed}\n"
        "🔥 Best streak: {best_streak}"
    ),
    # snooze
    "task.btn_snooze": "⏸ Snooze {n}m",
    "task.snooze_exhausted": "No more snoozes for this task.",
    "task.snoozed": "Snoozed {n} min. Unlock pushed back.",
    # quiet hours
    "menu.quiet": "🔕 Quiet hours",
    "settings.quiet.prompt": "Choose quiet hours preset (tasks will be paused in this window):",
    "settings.quiet.saved": "Quiet hours set: {start}–{end}.",
    "settings.quiet.off": "Quiet hours disabled.",
    # smart silence — /did and /busy
    "silence.did_logged": "Got it. I've logged that as done. Busy period: {minutes} min.",
    "silence.busy_set": "Busy mode: no tasks for {minutes} min.",
    "silence.busy_capped": "Capped at {max} minutes maximum.",
    "silence.busy_usage": "Usage: /busy <minutes>. Example: /busy 60",
    # baseline calibration
    "baseline.graduation": (
        "<b>Baseline complete!</b>\n\n"
        "You've finished the calibration phase. "
        "Difficulty will now adapt to your performance. Keep it up!"
    ),
    "baseline.progress": "Calibration phase: {completed}/10 tasks done. Keep going!",
    # daily goal
    "goal.reached": ("<b>Daily goal reached!</b>\n\n{msg}\n\nYou're free for today. See you tomorrow!"),
    # streak insurance
    "streak.insurance_used": ("Streak saved! One free pass used this week — your streak stays intact."),
    # anti-cheat
    "anti_cheat.followup": (
        "Quick check — can you describe one specific detail from the exercise you just did? "
        "(e.g. how many reps, where you felt it, what you were looking at)"
    ),
    "anti_cheat.hard_check_1": (
        "Before starting, what was the first thing you noticed in the room around you?"
    ),
    "anti_cheat.hard_check_2": ("During the exercise, what sound could you hear in the background?"),
    "anti_cheat.hard_check_3": ("What color or object was at eye level while you did the exercise?"),
}
