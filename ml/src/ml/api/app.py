from fastapi import FastAPI


def create_app() -> FastAPI:
    """Configure and return the FastAPI application."""
    app = FastAPI(title="Agent Base API")

    @app.get("/ping")
    def ping() -> dict[str, str]:
        return {"message": "pong"}

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "healthy"}

    return app
