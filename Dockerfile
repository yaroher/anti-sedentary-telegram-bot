# ── builder ──────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv

WORKDIR /build

COPY pyproject.toml uv.lock ./

# Export prod deps to a plain requirements.txt, then install into /install
RUN uv export --no-dev --no-emit-project --format requirements-txt --no-hashes -o requirements.txt \
 && pip install --no-cache-dir --target /install -r requirements.txt

# ── runtime ───────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/install:/app/src

RUN apt-get update \
 && apt-get install -y --no-install-recommends tini \
 && rm -rf /var/lib/apt/lists/*

RUN groupadd -r app \
 && useradd -r -g app -d /app -s /usr/sbin/nologin app

# Copy vendored dependencies from builder
COPY --from=builder /install /install

WORKDIR /app

COPY src ./src
COPY migrations ./migrations
COPY config ./config

RUN chown -R app:app /app

USER app

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz').read()" || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "-m", "anti_sedentary_bot"]
