# anti-sedentary-telegram-bot

Telegram accountability bot for sedentary work. Issues short micro-tasks during a configurable work window, locks the «Done» button until a realistic completion time, and occasionally asks a check question to discourage cheating.

## Features

- Configurable work window (e.g. 11:00–18:00) and task interval (30–90 min).
- Adaptive pressure: skips raise pressure, completions lower it, failures raise it more.
- Random check question after completion; suspicious one-letter answers flagged.
- Three tone profiles (`soft`, `normal`, `warden`) with localized phrases.
- LLM-generated copy via OpenAI-compatible endpoint (Groq by default), with deterministic fallbacks if the LLM is unreachable.
- Multilingual UI: English and Russian, language picked on first `/start` (auto-detected from Telegram locale) and changeable from the menu at any time.
- Auto-migrations on service start (aerich), Postgres persistence, Docker-ready.

## Stack

- Python 3.11+
- aiogram 3 — FSM, CallbackData factories
- Tortoise ORM + asyncpg (Postgres) with aerich auto-migrations
- APScheduler — periodic scheduler tick
- loguru — structured logging (stdlib logging intercepted)
- pydantic / pydantic-settings — settings and domain models
- OpenAI Python SDK pointed at Groq

## Layout

```
src/anti_sedentary_bot/
  __main__.py            # entrypoint with graceful shutdown
  config.py              # Settings (pydantic-settings)
  logger.py              # loguru + stdlib intercept
  db/                    # Tortoise init, models, aerich auto-upgrade
  bot/                   # aiogram routers, FSM states, CallbackData, keyboards
    handlers/            # start, menu, tasks, settings, text
  services/              # user, llm, exercises, tasks, scheduler
  domain/                # Flavor and Exercise pydantic models with locales
  i18n/                  # t(locale, key, **kwargs) + en/ru string tables
  utils/                 # time helpers
```

## State machine

User-input FSM (`bot/states.py`):

- `onboarding_language` — first `/start` for a new user
- `waiting_schedule` — custom schedule text input
- `waiting_check_answer` — answering a post-task check question

Task lifecycle (`db.models.TaskStatus`): `active → completed | skipped | failed`. Transitions live in `services/tasks.py` (`complete_task`, `skip_task`, `fail_task`).

## Running locally

```bash
cp .env.example .env   # fill BOT_TOKEN, GROQ_API_KEY (optional), DATABASE_URL

uv sync
uv run python -m anti_sedentary_bot
```

## Running with Docker

```bash
cp .env.example .env
docker compose up -d --build
docker compose logs -f bot
```

`docker-compose.yml` brings up Postgres 16 with a healthcheck and the bot container. The bot waits for Postgres, runs aerich migrations on start, then starts polling.

## Migrations

Migrations are stored in `migrations/` and committed to the repo. On service start `db.init_db()` will:

1. Try to apply pending aerich migrations.
2. If no revisions exist yet, run `aerich init-db` to create the initial schema.
3. If aerich fails for any reason, fall back to `Tortoise.generate_schemas(safe=True)`.

When you change `db/models.py`, generate a new revision locally:

```bash
uv run aerich migrate --name <change_name>
```

Commit the produced file under `migrations/models/`. The next service start applies it automatically.

## Environment variables

| Var | Default | Description |
|-----|---------|-------------|
| `BOT_TOKEN` | — | Telegram bot token (required) |
| `GROQ_API_KEY` | — | Groq / OpenAI-compatible API key (optional — falls back to canned phrases) |
| `DATABASE_URL` | `postgres://bot:bot@localhost:5432/anti_sedentary` | Tortoise connection string |
| `TIMEZONE` | `Europe/Amsterdam` | IANA timezone for work-window calculations |
| `LOG_LEVEL` | `INFO` | loguru level |
| `LLM_ENABLED` | `true` | Toggle LLM globally |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | OpenAI-compatible endpoint |
| `LLM_MODEL` | `groq/compound-mini` | Chat model name |

## License

MIT (or your project's choice).
