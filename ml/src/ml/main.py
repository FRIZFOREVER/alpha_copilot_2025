"""Expose the FastAPI application for the uvicorn CLI."""

from ml.api.app import create_app

app = create_app()
