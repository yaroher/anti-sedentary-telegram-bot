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
    # badges / achievements
    "badge.unlocked": "🏅 Badge unlocked!",
    "badge.streak_3": "🔥 3-task streak — you're on a roll!",
    "badge.streak_7": "🔥 7-task streak — a full week of momentum!",
    "badge.streak_30": "🔥 30-task streak — unstoppable!",
    "badge.streak_100": "🔥 100-task streak — legendary!",
    "badge.completed_50": "✅ 50 tasks done — solid foundation!",
    "badge.completed_200": "✅ 200 tasks done — committed!",
    "badge.completed_1000": "✅ 1000 tasks done — elite mover!",
    "badge.early_bird": "🌅 Early bird — completing tasks before 10 AM on 5+ days!",
    "badge.night_owl": "🦉 Night owl — active after 6 PM on 5+ days!",
    "badge.goal_streak_7": "🎯 Goal streak — hit your daily goal 7 days in a row!",
    # daily summary
    "summary.daily": (
        "<b>Today's wrap-up</b>\n"
        "✅ Completed: {completed}\n"
        "⏭ Skipped: {skipped}\n"
        "❌ Failed: {failed}\n"
        "🔥 Streak: {streak}  |  Best: {best_streak}\n\n"
        "{goal_status}"
    ),
    "summary.goal_yes": "🎯 Daily goal reached — great work!",
    "summary.goal_no": "📌 Daily goal not reached — try again tomorrow.",
    # insights
    "insights.header": "<b>Your personal insights</b>",
    "insights.best_hour": "⭐ Best hour: {hour}",
    "insights.worst_hour": "⚠️ Toughest hour: {hour}",
    "insights.trends_header": "<b>Exercise trends (difficulty)</b>",
    "insights.easier": "getting easier ↓",
    "insights.harder": "getting harder ↑",
    "insights.same": "stable →",
    "insights.no_data": "Not enough data yet — keep completing tasks!",
    # re-engagement
    "reengage.silent": "Hey! It's been a while. Ready to get back on track? 💪",
    # talk / coach mode
    "talk.intro": (
        "Coach mode on. Ask me anything about your routine, struggles, or goals.\n"
        "I'll keep it short and practical."
    ),
    "talk.end_btn": "End chat",
    "talk.ended": "Chat ended. Back to business! 💪",
    "talk.timeout": "We've been chatting a while — let's pick it up another time. Back to moving!",
    # slash command descriptions (new)
    "cmd.insights.desc": "Personal heatmap and trends",
    "cmd.talk.desc": "Chat with your coach",
    # health / partner additions
    "menu.health": "🏥 Health tracks",
    "settings.health.prompt": "Toggle health track reminders:",
    "health.on": "ON",
    "health.off": "OFF",
    "health.eye.label": "👁 Eye breaks",
    "health.hydration.label": "💧 Hydration",
    "health.posture.label": "🪑 Posture",
    "health.eye.message": "👁 <b>Eye break!</b>\n\nLook at something 20 feet (6 m) away for 20 seconds.\nTap Done when finished.",
    "health.hydration.message": "💧 <b>Hydration check!</b>\n\nDrink a glass of water now.\nTap Done when finished.",
    "health.posture.message": "🪑 <b>Posture check!</b>\n\nSit up straight, relax your shoulders, feet flat on the floor.\nTap Done when finished.",
    "health.eye.ack": "👁 Eye break logged. Great job!",
    "health.hydration.ack": "💧 Hydration logged. Stay hydrated!",
    "health.posture.ack": "🪑 Posture check logged. Keep it up!",
    "health.hydration.count": "💧 Water today: <b>{count}</b> glasses.",
    "health.btn_done": "✅ Done",
    "partner.paired": "Partner set: <b>{name}</b>. They will be notified if you skip hard or fail tasks.",
    "partner.added_by": "🤝 <b>{name}</b> added you as their accountability partner.",
    "partner.not_found": "User @{username} not found. They must have started the bot first.",
    "partner.self": "You can't partner with yourself.",
    "partner.current": "Your current partner: <b>{name}</b>.",
    "partner.help": "Usage: /partner @username — set an accountability partner.",
    "partner.none": "You don't have a partner set.",
    "partner.unpaired": "Partner removed.",
    "partner.partner_unpaired": "<b>{name}</b> removed you as their accountability partner.",
    "partner.notify_fail": "❌ Your partner <b>{name}</b> failed a task: <i>{title}</i>.",
    "partner.notify_skip": "⏭ Your partner <b>{name}</b> hard-skipped a task: <i>{title}</i>.",
    "cmd.water.desc": "Log a glass of water",
    "cmd.partner.desc": "Set accountability partner",
    "cmd.unpartner.desc": "Remove accountability partner",
    # partner pending + admin
    "partner.requested": "Pairing request sent to {name}. Waiting for them to accept.",
    "partner.request_incoming": "🤝 {name} wants to be your accountability partner.",
    "partner.btn_accept": "✅ Accept",
    "partner.btn_decline": "❌ Decline",
    "partner.accepted": "Partnership accepted with {name}.",
    "partner.accepted_by": "✅ {name} accepted your partnership request.",
    "partner.declined": "Partnership declined.",
    "partner.declined_by": "❌ {name} declined your partnership request.",
    "partner.no_pending": "No pending request from this user.",
    "admin.menu": "🔧 <b>Admin</b>\nProvider: <code>{provider}</code>\nModel: <code>{model}</code>",
    "admin.btn_test_llm": "🧪 Test LLM",
    "admin.llm_disabled": "LLM is disabled or no API key set.\nProvider: <code>{provider}</code>, Model: <code>{model}</code>",
    "admin.llm_ok": "✅ <b>LLM OK</b>\nProvider: <code>{provider}</code>\nModel: <code>{model}</code>\nBase URL: <code>{base_url}</code>\nLatency: {latency_ms} ms\nReply: <code>{reply}</code>",
    "admin.llm_error": "❌ <b>LLM error</b>\nProvider: <code>{provider}</code>\nModel: <code>{model}</code>\n<pre>{error}</pre>",
}
