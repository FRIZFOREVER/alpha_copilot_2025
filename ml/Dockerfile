FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:${PATH}"

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev \
 && chown -R appuser:app /app

EXPOSE 8000

ENTRYPOINT ["uvicorn"]

USER nonroot

CMD ["ml.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Metadata
LABEL org.opencontainers.image.title="fastapi-demo" \
      org.opencontainers.image.description="FastAPI service (Python 3.13, uv sync, non-root)" \
      org.opencontainers.image.base.name="ghcr.io/astral-sh/uv:python3.13-bookworm-slim"