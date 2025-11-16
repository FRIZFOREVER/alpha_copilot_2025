"""Обработчики для Telegram endpoints"""
import logging
from typing import Any

from fastapi import HTTPException, Request
from telegram_user_service import TelegramUserService

from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
from models.schemas import (
    TelegramAuthStartRequest,
    TelegramAuthVerifyRequest,
)

logger = logging.getLogger(__name__)


async def start_telegram_user_auth(
    request: TelegramAuthStartRequest, telegram_service: TelegramUserService
):
    """Начинает процесс авторизации Telegram пользователя"""
    try:
        if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
            raise HTTPException(
                status_code=500,
                detail="Telegram API credentials not configured. Please contact administrator.",
            )

        result = await telegram_service.start_auth(
            user_id=request.user_id,
            api_id=TELEGRAM_API_ID,
            api_hash=TELEGRAM_API_HASH,
            phone_number=request.phone_number,
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("error"))

        return {"status": "ok", **result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting Telegram user auth: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def verify_telegram_user_auth(
    request: TelegramAuthVerifyRequest, telegram_service: TelegramUserService
):
    """Подтверждает код авторизации Telegram пользователя"""
    try:
        result = await telegram_service.verify_code(
            user_id=request.user_id,
            phone_code=request.phone_code,
            password=request.password,
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("error"))

        return {"status": "ok", **result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying Telegram user auth: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def get_telegram_user_status(request: Request, telegram_service: TelegramUserService):
    """Получает статус авторизации Telegram пользователя по номеру телефона"""
    try:
        payload: dict[str, Any] = await request.json()
        phone_number = payload.get("phone_number")

        if not phone_number:
            raise HTTPException(status_code=400, detail="phone_number is required")

        is_authorized = telegram_service.is_authorized_by_phone(phone_number)

        result = {
            "status": "ok",
            "authorized": is_authorized,
        }

        if is_authorized:
            user_info = await telegram_service.get_user_info_by_phone(phone_number)
            if user_info:
                result["user_info"] = user_info

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Telegram user status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def get_telegram_user_contacts(request: Request, telegram_service: TelegramUserService):
    """Получает список контактов Telegram пользователя по номеру телефона или Telegram user ID"""
    try:
        payload: dict[str, Any] = await request.json()
        phone_number = payload.get("phone_number")
        tg_user_id = payload.get("tg_user_id")

        if not phone_number and not tg_user_id:
            raise HTTPException(
                status_code=400,
                detail="phone_number or tg_user_id is required",
            )

        if tg_user_id:
            try:
                tg_id = int(tg_user_id)
                result = await telegram_service.get_contacts_by_tg_id(tg_id)
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=400, detail="tg_user_id must be a valid integer"
                )
        else:
            result = await telegram_service.get_contacts_by_phone(phone_number)

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("error"))

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Telegram contacts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def send_telegram_user_message(request: Request, telegram_service: TelegramUserService):
    """Отправляет сообщение от имени пользователя в Telegram"""
    try:
        payload: dict[str, Any] = await request.json()
        phone_number = payload.get("phone_number")
        recipient_id = payload.get("recipient_id")
        text = payload.get("text")

        if not phone_number:
            raise HTTPException(status_code=400, detail="phone_number is required")
        if not recipient_id:
            raise HTTPException(status_code=400, detail="recipient_id is required")
        if not text:
            raise HTTPException(status_code=400, detail="text is required")

        found_user_id = telegram_service.find_user_by_phone(phone_number)
        if not found_user_id:
            raise HTTPException(
                status_code=404, detail="User not found by phone number"
            )

        recipient_id_str = str(recipient_id)

        result = await telegram_service.send_message(
            user_id=found_user_id,
            recipient_id=recipient_id_str,
            text=text,
        )

        if result.get("success"):
            return {"status": "ok", **result}
        else:
            raise HTTPException(
                status_code=400, detail=result.get("error", "Failed to send message")
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending Telegram user message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def disconnect_telegram_user(request: Request, telegram_service: TelegramUserService):
    """Отключает Telegram пользователя"""
    try:
        payload: dict[str, Any] = await request.json()
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")

        success = await telegram_service.disconnect(user_id)

        if success:
            return {"status": "ok", "message": "Telegram user disconnected"}
        else:
            raise HTTPException(
                status_code=404, detail="Telegram user connection not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disconnecting Telegram user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

