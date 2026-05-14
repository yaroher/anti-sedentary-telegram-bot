# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- **Clean architecture refactor** — repositories, services, and domain layers separated; raw ORM access removed from handlers.
- **i18n / multilingual UI** — `t()` helper with EN/RU locales; `normalize_locale` for Telegram language codes; per-user language setting.
- **Scheduler & retry** — APScheduler-based periodic tick with configurable concurrency; exponential-back-off retry for Telegram sends.
- **Throttling middleware** — per-user rate limit using in-memory timestamps.
- **Soft delete** — `User.is_deleted` flag with `soft_delete` / `restore` helpers; deleted users excluded from scheduler.
- **ChatMessage TTL** — cleanup job purges messages older than `message_retention_days` (default 30 days).
- **YAML exercise catalogue** — exercises loaded from `config/exercises.yaml`; hot-reloadable without code changes.
- **Slash commands** — `/menu`, `/stats`, `/pause`, `/resume`, `/lang`, `/quiet` registered via `set_my_commands`.
- **Snooze** — users can defer the unlock timer up to `MAX_SNOOZE_COUNT` times per task.
- **Quiet hours** — configurable window during which new tasks and nudges are suppressed.
- **Weekly summary** — scheduled Monday-morning digest of completed/skipped/failed counts and best streak.
- **Developer tooling** — pre-commit (ruff + standard hooks), GitHub Actions CI (lint / test / docker-build), pytest test scaffolding with in-memory SQLite, mypy config, Makefile, `.editorconfig`, VS Code settings, `docker-compose.override.yml` for hot-reload dev.

[Unreleased]: https://github.com/yaroher/anti-sedentary-telegram-bot/compare/HEAD...HEAD
