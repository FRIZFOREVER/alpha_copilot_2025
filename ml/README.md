# ML Service Notes

## Pipeline logging

Pipeline activity is emitted through a dedicated logger (`app.pipeline`) so that
long-running agent workflows do not pollute the FastAPI/Uvicorn output. The
logger writes to a rotating file handler configured via
`ml/src/ml/configs/logging.yaml`.

At startup the service resolves the most appropriate location for
`pipeline.log`:

- If the application directory is writable the log file will live under
  `/app/src/ml/logs/pipeline.log` (10 MiB per file, 5 backups).
- Otherwise a fallback directory is created at `/tmp/ml-logs/` and the file is
  written there instead.
- If neither location is writable the file handler is disabled and pipeline
  events only appear in the container stdout stream.

The chosen destination is announced in the container logs under the
`ml.api.app` logger during startup. Check it with
`docker compose logs ml-api | grep "Pipeline logs"` when running locally or via
your deployment platform's log streaming tools. Programmatic checks can read the
same information by calling `ml.api.app.get_pipeline_log_path()`.

Set the `PIPELINE_LOGGING_ENABLED` environment variable to control whether the
pipeline handler should receive events:

- unset or `true`/`1`/`yes`/`on` – pipeline events are written to the dedicated
  log file.
- `false`/`0`/`no`/`off` – the `app.pipeline` logger is disabled and no
  dedicated pipeline log file will be created.

The toggle can be applied without restarting Uvicorn by exporting the variable
before launching the service (e.g. `PIPELINE_LOGGING_ENABLED=false uvicorn ...`).
