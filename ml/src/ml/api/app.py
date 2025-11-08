import logging
from typing import Any, Dict

from fastapi import FastAPI, Request

from ml.agent.router import workflow

logger = logging.getLogger(__name__)

# Create fastapi ASGI importable app function
# Needed for uvicorn to use as an app to setup local http server
def create_app() -> FastAPI:
    """Configure and return the FastAPI application."""
    app = FastAPI(title="Agent Base API")
    logger.info("FastAPI application initialised")

    @app.post("/message")
    async def message(request: Request) -> Dict[str, str]:
        payload: Dict[str, Any] = await request.json()
        logger.info("Handling /message request with payload")
        answer = workflow(payload)
        return {"message": answer}
    
    @app.post("/mock")
    def workflow():
        return {"message": "No, you"}

    @app.get("/ping")
    def ping() -> dict[str, str]:
        logger.debug("Handling /ping request")
        return {"message": "pong"}

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        logger.debug("Handling /health request")
        return {"status": "healthy"}

    return app
