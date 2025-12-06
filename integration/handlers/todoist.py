"""Обработчики для Todoist endpoints"""
import logging
from typing import Any

from fastapi import HTTPException, Request
from todoist_service import TodoistService

logger = logging.getLogger(__name__)


async def save_todoist_token(request: Request, todoist_service: TodoistService):
    """Сохраняет токен Todoist пользователя"""
    try:
        payload: dict[str, Any] = await request.json()
        user_id = payload.get("user_id")
        token = payload.get("token")

        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        if not token:
            raise HTTPException(status_code=400, detail="token is required")

        logger.info(f"Saving Todoist token for user_id: {user_id}")

        result = todoist_service.save_todoist_token(
            user_id=user_id,
            token=token,
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("error"))

        logger.info(f"Todoist token saved successfully for user_id: {user_id}")
        return {"status": "ok", **result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving Todoist token: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def get_todoist_status(request: Request, todoist_service: TodoistService):
    """Получает статус авторизации Todoist"""
    try:
        payload: dict[str, Any] = await request.json()
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")

        logger.info(f"Checking Todoist status for user_id: {user_id}")

        is_authorized = todoist_service.is_authorized(user_id)

        logger.info(f"Todoist status for user_id {user_id}: authorized={is_authorized}")

        return {
            "status": "ok",
            "authorized": is_authorized,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Todoist status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def get_todoist_projects(request: Request, todoist_service: TodoistService):
    """Получает список проектов Todoist пользователя"""
    try:
        payload: dict[str, Any] = await request.json()
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")

        result = await todoist_service.get_projects(user_id)

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("error"))

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Todoist projects: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def create_todoist_task(request: Request, todoist_service: TodoistService):
    """Создает задачу в Todoist"""
    try:
        payload: dict[str, Any] = await request.json()
        user_id = payload.get("user_id")
        content = payload.get("content")
        description = payload.get("description")
        labels = payload.get("labels")

        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        if not content:
            raise HTTPException(status_code=400, detail="content is required")

        logger.info(
            f"Creating Todoist task for user_id: {user_id}, content: {content[:50]}..."
        )

        result = await todoist_service.create_task(
            user_id=user_id,
            content=content,
            description=description,
            labels=labels,
        )

        if result.get("success"):
            return {"status": "ok", **result}
        else:
            raise HTTPException(
                status_code=400, detail=result.get("error", "Failed to create task")
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating Todoist task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

