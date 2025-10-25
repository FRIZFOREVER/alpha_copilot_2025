import logging

from ml.api.app import create_app

root_logger = logging.getLogger()
if root_logger.handlers:
    print(
        f"Warning: Root logger already has {len(root_logger.handlers)} handler(s) configured. "
        f"basicConfig() will be ignored. Current level: {logging.getLevelName(root_logger.level)}"
    )
# Uvicorn expects an ASGI application object at this path (`ml.main:app`).
app = create_app()
