import asyncio
import logging
import logging.config
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
import ollama
import yaml

from ml.agent.router import init_models, workflow_collect, workflow_stream
from ml.configs.message import RequestPayload
from ml.utils.fetch_model import delete_models, fetch_models, prune_unconfigured_models
from ml.utils.warmup import warmup_models


_LOGGING_CONFIGURED = False
_PIPELINE_LOG_PATH: Optional[Path] = None


def get_pipeline_log_path() -> Optional[Path]:
    """Return the resolved filesystem path for pipeline log output.

    The path is determined during :func:`_configure_logging` and reflects the
    best writable location discovered at runtime. ``None`` signals that file
    logging is disabled or that no writable directory was available, in which
    case pipeline events will only appear in the container stdout stream.
    """

    return _PIPELINE_LOG_PATH


def _configure_logging() -> None:
    global _LOGGING_CONFIGURED
    global _PIPELINE_LOG_PATH

    if _LOGGING_CONFIGURED:
        return

    config_path = Path(__file__).resolve().parents[1] / "configs" / "logging.yaml"

    if not config_path.is_file():
        logging.getLogger(__name__).warning(
            "Logging configuration file '%s' could not be found", config_path
        )
        return

    with config_path.open("r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream)

    pipeline_handler = config.get("handlers", {}).get("pipeline_file")
    pipeline_logging_disabled_reason: Optional[str] = None
    _PIPELINE_LOG_PATH = None
    if pipeline_handler:
        filename = pipeline_handler.get("filename")
        if filename:
            log_path = Path(filename)
            if not log_path.is_absolute():
                # Place logs alongside the ml package root by default.
                log_path = (config_path.parents[1] / "logs" / log_path.name).resolve()

            resolved_path: Optional[Path]
            try:
                log_path.parent.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                logger = logging.getLogger(__name__)
                logger.warning(
                    "Unable to create pipeline log directory '%s': %s", log_path.parent, exc
                )
                fallback_dir = Path("/tmp/ml-logs")
                try:
                    fallback_dir.mkdir(parents=True, exist_ok=True)
                except OSError as fallback_exc:
                    logger.warning(
                        "Disabling pipeline file logging; failed to create fallback directory '%s': %s",
                        fallback_dir,
                        fallback_exc,
                    )
                    pipeline_logger = config.get("loggers", {}).get("app.pipeline")
                    if pipeline_logger:
                        pipeline_logger["handlers"] = []
                    pipeline_handler.clear()
                    pipeline_handler["class"] = "logging.NullHandler"
                    resolved_path = None
                else:
                    logger.info(
                        "Pipeline logs will be written to fallback directory '%s'", fallback_dir
                    )
                    resolved_path = fallback_dir / log_path.name
            else:
                resolved_path = log_path

            if resolved_path is not None:
                pipeline_handler["filename"] = str(resolved_path)

    logging.config.dictConfig(config)

    from ml.configs.runtime_flags import PIPELINE_LOGGING_ENABLED

    pipeline_logger = logging.getLogger("app.pipeline")
    pipeline_logger.disabled = not PIPELINE_LOGGING_ENABLED
    status_logger = logging.getLogger(__name__)
    if pipeline_logger.disabled:
        if PIPELINE_LOGGING_ENABLED:
            status_logger.info(
                "Pipeline file logging is disabled; see previous startup warnings for details"
            )
        else:
            status_logger.info(
                "Pipeline file logging disabled via PIPELINE_LOGGING_ENABLED environment flag"
            )
        if _PIPELINE_LOG_PATH is not None:
            status_logger.info(
                "Last resolved pipeline log path was '%s'", _PIPELINE_LOG_PATH
            )
    elif _PIPELINE_LOG_PATH is not None:
        status_logger.info("Pipeline logs will be written to '%s'", _PIPELINE_LOG_PATH)
    elif pipeline_logging_disabled_reason:
        status_logger.info(
            "Pipeline file logging is unavailable because %s", pipeline_logging_disabled_reason
        )

    _LOGGING_CONFIGURED = True


_configure_logging()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def lifespan(app: FastAPI):
    app.state.models = None
    app.state.models_ready = asyncio.Event()
    
    async def _init():
        try:
            await fetch_models()
        except Exception:
            logger.warning("Failed to prefetch models via Ollama", exc_info=True)
        else:
            try:
                await prune_unconfigured_models()
            except Exception:
                logger.warning("Failed to prune extraneous Ollama models", exc_info=True)
        models = await init_models()
        try:
            await warmup_models(list(models.values()))
        except Exception:
            logger.warning("Failed to warmup models", exc_info=True)
        app.state.models = models
        app.state.models_ready.set()

    app.state.models_task = asyncio.create_task(_init())

    yield

    try:
        await delete_models()
    except Exception:
        logger.warning("Failed to prune Ollama models during shutdown", exc_info=True)

    


def create_app() -> FastAPI:
    """Configure and return the FastAPI application."""
    app = FastAPI(title="Agent Base API", lifespan=lifespan)
    logger.info("FastAPI application initialised")

    @app.post("/message")
    async def message(payload: RequestPayload) -> Dict[str, str]:
        models_ready = app.state.models_ready

        if not models_ready.is_set():
            raise HTTPException(status_code=503, detail="Models are still initialising")

        logger.info("Handling /message request with payload")

        try:
            message_text = workflow_collect(payload.model_dump())
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("Failed to generate response from workflow")
            raise HTTPException(
                status_code=500, detail="Failed to generate response from workflow"
            ) from exc

        return {"message": message_text}
    
    @app.post("/message_stream")
    async def message_stream(payload: RequestPayload) -> StreamingResponse:
        models_ready = app.state.models_ready

        if not models_ready.is_set():
            raise HTTPException(status_code=503, detail="Models are still initialising")

        logger.info("Handling /message_stream request with payload")

        def event_generator():
            stream = workflow_stream(payload.model_dump())
            for chunk in stream:
                yield f"data: {chunk.model_dump_json()}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    
    @app.post("/mock")
    def mock():
        return {"message": "No, you"}

    @app.get("/ping")
    def ping() -> dict[str, str]:
        logger.debug("Handling /ping request")
        return {"message": "pong"}

    @app.get("/ollama")
    async def ollama_models() -> Dict[str, Any]:
        logger.debug("Handling /ollama request")
        try:
            models = await asyncio.to_thread(ollama.list)
        except Exception as exc:
            logger.exception("Failed to fetch ollama models")
            raise HTTPException(
                status_code=503,
                detail="Failed to fetch ollama models",
            ) from exc

        return jsonable_encoder(models)

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        logger.debug("Handling /health request")
        return {"status": "healthy"}

    return app
