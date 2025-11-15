from fastapi.applications import FastAPI

from ml.api.app import create_app

# Uvicorn expects an ASGI application object at this path (`ml.main:app`).
app: FastAPI = create_app()
