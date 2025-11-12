from dotenv import load_dotenv

from ml.api.app import create_app

# Ensure environment variables from .env files are available during startup.
load_dotenv()

# Uvicorn expects an ASGI application object at this path (`ml.main:app`).
app = create_app()
