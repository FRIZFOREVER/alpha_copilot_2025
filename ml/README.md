# ML Service Notes

## Pipeline logging

Pipeline activity is now emitted through a dedicated logger (`app.pipeline`) so
that long-running agent workflows do not pollute the FastAPI/Uvicorn output.
The logger writes to a rotating file handler configured via
`ml/src/ml/configs/logging.yaml`; by default log files are stored under
`ml/logs/pipeline.log` (10 MiB per file, 5 backups).

Set the `PIPELINE_LOGGING_ENABLED` environment variable to control whether the
pipeline handler should receive events:

- unset or `true`/`1`/`yes`/`on` – pipeline events are written to the dedicated
  log file.
- `false`/`0`/`no`/`off` – the `app.pipeline` logger is disabled and no
  dedicated pipeline log file will be created.

The toggle can be applied without restarting Uvicorn by exporting the variable
before launching the service (e.g. `PIPELINE_LOGGING_ENABLED=false uvicorn ...`).
