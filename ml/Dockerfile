# downloading uv-compatable image from astral-sh
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# setting up non-root user, who will run the app
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

# working directory inside pulled VM for our app (target for COPY)
WORKDIR /app

# Python ENV's for efficient building
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:${PATH}"

# transfering uv.lock and pyproject.toml for dependency's instead of requirement.txt
RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml

# Transfering app from dockerfile into our image
COPY . /app

# mounting installation cache folder and running uv sync to build dependency's
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Setting up Entrypoint, aka "What command will we run inside the terminal ?"
ENTRYPOINT ["uvicorn"]

# Switcing to nonroot user before launching an app
USER nonroot

# Running our entrypoint command with arguments
CMD ["ml.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "/app/src/ml/configs/logging.yaml", "--access-log"]

# Metadata
LABEL org.opencontainers.image.title="agent-base" \
      org.opencontainers.image.description="agent-base api service with calls to local LLM's. Build using uv, deployment via uvicorn+fastapi" \
      org.opencontainers.image.base.name="ghcr.io/astral-sh/uv:python3.13-bookworm-slim"
