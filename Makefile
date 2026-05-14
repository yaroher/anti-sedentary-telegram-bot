PHONY: install run lint fmt typecheck test migrate upgrade docker down

install:
	uv sync

run:
	uv run python -m anti_sedentary_bot

lint:
	uv run ruff check src tests

fmt:
	uv run ruff format src tests

typecheck:
	uv run mypy src/anti_sedentary_bot

test:
	uv run pytest -q

migrate:
	uv run aerich migrate --name $(name)

upgrade:
	uv run aerich upgrade

docker:
	docker compose up -d --build

down:
	docker compose down
