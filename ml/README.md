# ml

FastAPI service for the agent-base project.

## Running the API

Use the project script, which wraps the uvicorn CLI:

```bash
uv run ml
```

Pass additional uvicorn flags after `--`, for example:

```bash
uv run ml -- --reload --port 9000
```

By default the server listens on `0.0.0.0:8000`; override via `ML_HOST` and `ML_PORT` environment variables if needed.
