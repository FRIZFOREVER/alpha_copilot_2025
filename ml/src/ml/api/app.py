from fastapi import FastAPI

# Create fastapi ASGI importable app function
# Needed for uvicorn to use as an app to setup local http server
def create_app() -> FastAPI:
    """Configure and return the FastAPI application."""
    app = FastAPI(title="Agent Base API")

    # TODO: create "/ReAct" handle. get's json with data, including "messages" open-ai chat-completeion compatable field
    @app.get("/ReAct")
    def react() -> dict[str, str]:
        pass
    
    @app.get("/ping")
    def ping() -> dict[str, str]:
        return {"message": "pong"}

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "healthy"}

    return app
