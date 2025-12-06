"""Основной файл приложения FastAPI для Integration API"""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from handlers import (
    telegram as telegram_handlers,
)
from handlers import (
    todoist as todoist_handlers,
)
from models.schemas import TelegramAuthStartRequest, TelegramAuthVerifyRequest
from telegram_user_service import TelegramUserService
from todoist_service import TodoistService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Integration API")

app.state.telegram_user_service = TelegramUserService()
app.state.todoist_service = TodoistService()


@app.on_event("startup")
async def startup_event():
    """Инициализация при старте приложения"""
    logger.info("Starting up Integration API...")


@app.get("/")
async def root():
    return {"message": "Integration API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/telegram/user/auth/start")
async def start_telegram_user_auth(request: TelegramAuthStartRequest):
    return await telegram_handlers.start_telegram_user_auth(
        request, app.state.telegram_user_service
    )


@app.post("/telegram/user/auth/verify")
async def verify_telegram_user_auth(request: TelegramAuthVerifyRequest):
    return await telegram_handlers.verify_telegram_user_auth(
        request, app.state.telegram_user_service
    )


@app.post("/telegram/user/status")
async def get_telegram_user_status(request: Request):
    return await telegram_handlers.get_telegram_user_status(
        request, app.state.telegram_user_service
    )


@app.post("/telegram/user/contacts")
async def get_telegram_user_contacts(request: Request):
    return await telegram_handlers.get_telegram_user_contacts(
        request, app.state.telegram_user_service
    )


@app.post("/telegram/user/send/message")
async def send_telegram_user_message(request: Request):
    return await telegram_handlers.send_telegram_user_message(
        request, app.state.telegram_user_service
    )


@app.post("/telegram/user/disconnect")
async def disconnect_telegram_user(request: Request):
    return await telegram_handlers.disconnect_telegram_user(
        request, app.state.telegram_user_service
    )


@app.post("/todoist/auth/save")
async def save_todoist_token(request: Request):
    return await todoist_handlers.save_todoist_token(request, app.state.todoist_service)


@app.post("/todoist/status")
async def get_todoist_status(request: Request):
    return await todoist_handlers.get_todoist_status(request, app.state.todoist_service)


@app.post("/todoist/projects")
async def get_todoist_projects(request: Request):
    return await todoist_handlers.get_todoist_projects(request, app.state.todoist_service)


@app.post("/todoist/create/task")
async def create_todoist_task(request: Request):
    return await todoist_handlers.create_todoist_task(request, app.state.todoist_service)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=4444)
