"""
Сервис для работы с Todoist API
"""

import os
import json
import logging
import httpx
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import date

logger = logging.getLogger(__name__)

DATA_DIR = Path(os.getenv("TELEGRAM_DATA_DIR", "/app/data"))
TODOIST_AUTH_DATA_FILE = DATA_DIR / "todoist_auth.json"
TODOIST_API_BASE = "https://api.todoist.com/rest/v2"


class TodoistService:
    """Сервис для работы с Todoist API"""

    def __init__(self):
        self._ensure_data_files()

    def _ensure_data_files(self):
        """Создает необходимые файлы и директории"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not TODOIST_AUTH_DATA_FILE.exists():
            with open(TODOIST_AUTH_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load_auth_data(self) -> Dict[str, Dict[str, Any]]:
        """Загружает данные авторизации Todoist"""
        try:
            logger.debug(f"Loading Todoist auth data from: {TODOIST_AUTH_DATA_FILE}")
            logger.debug(f"File exists: {TODOIST_AUTH_DATA_FILE.exists()}")

            if TODOIST_AUTH_DATA_FILE.exists():
                with open(TODOIST_AUTH_DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.debug(f"Loaded Todoist auth data: {list(data.keys())}")
                    logger.debug(f"Data content: {data}")
                    return data
            else:
                logger.warning(
                    f"Todoist auth file does not exist: {TODOIST_AUTH_DATA_FILE}"
                )
            return {}
        except Exception as e:
            logger.error(f"Error loading Todoist auth data: {e}", exc_info=True)
            return {}

    def _save_auth_data(self, auth_data: Dict[str, Dict[str, Any]]):
        """Сохраняет данные авторизации Todoist"""
        try:
            logger.debug(f"Saving Todoist auth data to: {TODOIST_AUTH_DATA_FILE}")
            logger.debug(f"Data to save: {list(auth_data.keys())}")

            TODOIST_AUTH_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

            with open(TODOIST_AUTH_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(auth_data, f, indent=2, ensure_ascii=False)

            logger.debug(
                f"Todoist auth data saved successfully. File exists: {TODOIST_AUTH_DATA_FILE.exists()}"
            )
        except Exception as e:
            logger.error(f"Error saving Todoist auth data: {e}", exc_info=True)
            raise

    def save_todoist_token(
        self,
        user_id: str,
        token: str,
    ) -> Dict[str, Any]:
        """
        Сохраняет токен Todoist пользователя

        Args:
            user_id: ID пользователя в системе
            token: Todoist API токен

        Returns:
            Результат сохранения
        """
        try:
            auth_data = self._load_auth_data()
            logger.info(f"Saving Todoist token for user {user_id}")
            logger.debug(
                f"Current auth data keys before save: {list(auth_data.keys())}"
            )

            auth_data[user_id] = {
                "token": token,
                "authorized": True,
            }
            self._save_auth_data(auth_data)

            verify_data = self._load_auth_data()
            logger.info(f"Todoist token saved for user {user_id}")
            logger.debug(f"Auth data keys after save: {list(verify_data.keys())}")
            logger.debug(
                f"User {user_id} authorized: {verify_data.get(user_id, {}).get('authorized', False)}"
            )

            return {
                "status": "ok",
                "message": "Todoist token saved",
            }
        except Exception as e:
            logger.error(f"Error saving Todoist token: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    def is_authorized(self, user_id: str) -> bool:
        """Проверяет, авторизован ли пользователь в Todoist"""
        auth_data = self._load_auth_data()
        logger.debug(f"Checking authorization for user {user_id}")
        logger.debug(f"Available user_ids: {list(auth_data.keys())}")
        is_auth = auth_data.get(user_id, {}).get("authorized", False)
        logger.debug(f"User {user_id} authorized: {is_auth}")
        return is_auth

    async def create_task(
        self,
        user_id: str,
        content: str,
        description: Optional[str] = None,
        labels: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """
        Создает задачу в Todoist

        Args:
            user_id: ID пользователя в системе
            content: Текст задачи (обязательно)
            description: Описание задачи
            labels: Список меток

        Returns:
            Результат создания задачи
        """
        try:
            auth_data = self._load_auth_data()
            logger.debug(f"Creating task for user {user_id}")
            logger.debug(f"Available user_ids in auth_data: {list(auth_data.keys())}")

            user_credentials = auth_data.get(user_id)
            logger.debug(f"User credentials found: {user_credentials is not None}")

            if not user_credentials:
                logger.warning(
                    f"User {user_id} not found in auth_data. Available users: {list(auth_data.keys())}"
                )
                return {
                    "success": False,
                    "error": "User Todoist token not found. Please authorize Todoist first.",
                }

            if not user_credentials.get("authorized"):
                return {
                    "success": False,
                    "error": "User Todoist not authorized. Please authorize Todoist first.",
                }

            token = user_credentials.get("token")

            if not token:
                return {
                    "success": False,
                    "error": "Todoist token incomplete",
                }

            task_data = {
                "content": content,
                "priority": 3,
                "due_date": date.today().isoformat(),
            }

            if description:
                task_data["description"] = description

            if labels:
                task_data["labels"] = labels

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{TODOIST_API_BASE}/tasks",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    json=task_data,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    task = response.json()
                    logger.info(
                        f"Task created successfully in Todoist for user {user_id}: {task.get('id')}"
                    )
                    return {
                        "success": True,
                        "task_id": task.get("id"),
                        "content": task.get("content"),
                        "url": task.get("url"),
                        "message": "Task created in Todoist",
                    }
                else:
                    error_text = response.text
                    logger.error(
                        f"Todoist API error: {response.status_code} - {error_text}"
                    )
                    return {
                        "success": False,
                        "error": f"Todoist API error: {response.status_code} - {error_text}",
                    }

        except Exception as e:
            logger.error(f"Error creating Todoist task: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to create task: {str(e)}",
            }

    async def get_projects(self, user_id: str) -> Dict[str, Any]:
        """
        Получает список проектов пользователя

        Args:
            user_id: ID пользователя в системе

        Returns:
            Список проектов
        """
        try:
            auth_data = self._load_auth_data()
            user_credentials = auth_data.get(user_id)

            if not user_credentials or not user_credentials.get("authorized"):
                return {
                    "status": "error",
                    "error": "User not authorized",
                    "projects": [],
                }

            token = user_credentials.get("token")

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{TODOIST_API_BASE}/projects",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0,
                )

                if response.status_code == 200:
                    projects = response.json()
                    return {
                        "status": "ok",
                        "projects": projects,
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"Failed to get projects: {response.status_code}",
                        "projects": [],
                    }

        except Exception as e:
            logger.error(f"Error getting Todoist projects: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "projects": [],
            }
