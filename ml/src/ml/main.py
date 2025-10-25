import logging

from ml.api.app import create_app

root_logger = logging.getLogger()

# Uvicorn expects an ASGI application object at this path (`ml.main:app`).
app = create_app()
