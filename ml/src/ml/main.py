from dotenv import load_dotenv

from ml.api.app import create_app
from ml.configs.logging_config import configure_logging

# Ensure environment variables from .env files are available during startup.
load_dotenv()

# Configure logging early so modules that log at import/runtime use the shared config.
configure_logging()

# Uvicorn expects an ASGI application object at this path (`ml.main:app`).
app = create_app()
