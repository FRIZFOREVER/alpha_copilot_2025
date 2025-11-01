import logging

from fastapi import FastAPI

from ..agent.router import react_workflow

logger = logging.getLogger(__name__)

# Create fastapi ASGI importable app function
# Needed for uvicorn to use as an app to setup local http server
def create_app() -> FastAPI:
    """Configure and return the FastAPI application."""
    app = FastAPI(title="Agent Base API")
    logger.info("FastAPI application initialised")

    # TODO: create "/react" handle. 
    # get's json with data, including "messages" open-ai chat-completeion compatable field
    @app.get("/react")
    def react() -> dict[str, str]:
        logger.info("Handling /react request")
        answer = react_workflow()
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
