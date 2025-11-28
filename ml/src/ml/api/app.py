import asyncio

from fastapi import FastAPI

from ml.api.routes.health import router as health_router
from ml.api.routes.workflow import router as workflow_router


async def lifespan(app: FastAPI):
    app.state.model_ready = asyncio.Event()

    async def _init() -> None:
        # TODO: Models init
        raise NotImplementedError()

    app.state.models_task = asyncio.create_task(_init())

    yield

    # TODO: await init on shutdown


def app() -> FastAPI:
    app = FastAPI(title="ml service")

    # /ping
    app.include_router(health_router)

    # /message_stream and /message
    app.include_router(workflow_router)

    return app
