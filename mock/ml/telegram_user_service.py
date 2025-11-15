"""
Сервис для работы с Telegram Client API (отправка сообщений от имени пользователя)
"""

import os
import json
import logging
import asyncio
from typing import Dict, Optional, Any
from pathlib import Path
from pyrogram import Client
from pyrogram.errors import (
    SessionPasswordNeeded,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    AuthKeyUnregistered,
)

logger = logging.getLogger(__name__)

# Путь к файлу для хранения сессий
DATA_DIR = Path(os.getenv("TELEGRAM_DATA_DIR", "/app/data"))
SESSIONS_DIR = DATA_DIR / "telegram_sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

# Файл для хранения данных авторизации
AUTH_DATA_FILE = DATA_DIR / "telegram_auth.json"


class TelegramUserService:
    """Сервис для работы с Telegram Client API (от имени пользователя)"""

    def __init__(self):
        self._ensure_data_files()
        self._active_clients: Dict[str, Client] = {}

    def _ensure_data_files(self):
        """Создает необходимые файлы и директории"""
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        if not AUTH_DATA_FILE.exists():
            with open(AUTH_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load_auth_data(self) -> Dict[str, Dict[str, Any]]:
        """Загружает данные авторизации"""
        try:
            if AUTH_DATA_FILE.exists():
                with open(AUTH_DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.debug(f"Loaded auth data: {list(data.keys())}")
                    return data
            return {}
        except Exception as e:
            logger.error(f"Error loading auth data: {e}")
            return {}

    def _save_auth_data(self, auth_data: Dict[str, Dict[str, Any]]):
        """Сохраняет данные авторизации"""
        try:
            with open(AUTH_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(auth_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving auth data: {e}")
            raise

    async def start_auth(
        self, user_id: str, api_id: int, api_hash: str, phone_number: str
    ) -> Dict[str, Any]:
        """
        Начинает процесс авторизации

        Args:
            user_id: ID пользователя в системе
            api_id: Telegram API ID (получить на https://my.telegram.org)
            api_hash: Telegram API Hash
            phone_number: Номер телефона в международном формате

        Returns:
            Информация о статусе авторизации
        """
        try:
            session_name = f"{SESSIONS_DIR}/{user_id}"
            client = Client(
                name=session_name,
                api_id=api_id,
                api_hash=api_hash,
                phone_number=phone_number,
            )

            await client.connect()

            # Проверяем, авторизован ли уже (в Pyrogram 2.0 используем get_me)
            try:
                me = await client.get_me()
                # Если get_me успешно выполнился, значит уже авторизован
                await client.disconnect()
                # Сохраняем данные
                auth_data = self._load_auth_data()
                auth_data[user_id] = {
                    "api_id": api_id,
                    "api_hash": api_hash,
                    "phone_number": phone_number,
                    "authorized": True,
                }
                self._save_auth_data(auth_data)
                return {
                    "status": "authorized",
                    "message": "Already authorized",
                    "user": {
                        "id": me.id,
                        "first_name": me.first_name,
                        "last_name": me.last_name,
                        "username": me.username,
                        "phone_number": me.phone_number,
                    },
                }
            except Exception:
                # Если get_me не удался, значит не авторизован - продолжаем процесс
                pass

            # Отправляем код
            sent_code = await client.send_code(phone_number)
            phone_code_hash = sent_code.phone_code_hash

            logger.info(
                f"Code sent to {phone_number}, phone_code_hash: {phone_code_hash[:10] if phone_code_hash else 'None'}..."
            )

            # Сохраняем промежуточные данные и клиент для последующего использования
            auth_data = self._load_auth_data()
            auth_data[user_id] = {
                "api_id": api_id,
                "api_hash": api_hash,
                "phone_number": phone_number,
                "phone_code_hash": phone_code_hash,
                "authorized": False,
            }
            self._save_auth_data(auth_data)
            logger.info(f"Auth data saved for user {user_id}")

            # Сохраняем клиент для использования в verify_code
            # НЕ отключаем клиент, так как phone_code_hash привязан к этой сессии
            self._active_clients[user_id] = client

            return {
                "status": "code_sent",
                "phone_code_hash": phone_code_hash,
                "message": "Code sent to Telegram",
            }
        except Exception as e:
            logger.error(f"Error starting auth: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
            }

    async def verify_code(
        self, user_id: str, phone_code: str, password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Подтверждает код авторизации

        Args:
            user_id: ID пользователя в системе
            phone_code: Код подтверждения из Telegram
            password: Пароль двухфакторной аутентификации (если требуется)

        Returns:
            Результат авторизации
        """
        try:
            auth_data = self._load_auth_data()
            user_auth = auth_data.get(user_id)

            if not user_auth:
                return {
                    "status": "error",
                    "error": "Auth session not found. Please start auth first.",
                }

            # Проверяем phone_code_hash до создания клиента
            phone_code_hash = user_auth.get("phone_code_hash")
            if not phone_code_hash:
                logger.error(f"Phone code hash not found for user {user_id}")
                return {
                    "status": "error",
                    "error": "Phone code hash not found. Please start auth again.",
                }

            # Используем сохраненный клиент, если он есть (из start_auth)
            # Это важно, так как phone_code_hash привязан к конкретной сессии
            client = self._active_clients.get(user_id)

            if not client:
                # Если клиент не найден, создаем новый (но это может не сработать)
                session_name = f"{SESSIONS_DIR}/{user_id}"
                client = Client(
                    name=session_name,
                    api_id=user_auth["api_id"],
                    api_hash=user_auth["api_hash"],
                    phone_number=user_auth["phone_number"],
                )
                await client.connect()
                logger.warning(
                    f"Using new client for user {user_id}, phone_code_hash may not work"
                )
            else:
                # Проверяем, что клиент подключен
                if not client.is_connected:
                    await client.connect()
                logger.info(f"Using existing client for user {user_id}")

            logger.info(
                f"Attempting to sign in user {user_id} with phone_code_hash: {phone_code_hash[:10] if len(phone_code_hash) > 10 else phone_code_hash}..."
            )
            logger.info(
                f"Phone number: {user_auth['phone_number']}, API ID: {user_auth['api_id']}"
            )

            try:
                # В Pyrogram sign_in требует все три параметра как именованные аргументы
                # Важно: используем тот же phone_code_hash, который был получен при send_code
                result = await client.sign_in(
                    phone_number=user_auth["phone_number"],
                    phone_code_hash=phone_code_hash,
                    phone_code=phone_code,
                )
                logger.info(f"Sign in successful for user {user_id}")
            except PhoneCodeExpired as e:
                logger.error(f"Phone code expired for user {user_id}: {e}")
                # Удаляем устаревший phone_code_hash, чтобы пользователь мог запросить новый код
                if user_id in auth_data:
                    auth_data[user_id].pop("phone_code_hash", None)
                    self._save_auth_data(auth_data)
                # Отключаем клиент только если подключен
                if client.is_connected:
                    try:
                        await client.disconnect()
                    except Exception:
                        pass
                # Удаляем из активных клиентов
                if user_id in self._active_clients:
                    del self._active_clients[user_id]
                return {
                    "status": "error",
                    "error": "Phone code expired. Please request a new code by calling /telegram/user/auth/start again.",
                }
            except SessionPasswordNeeded:
                if not password:
                    if client.is_connected:
                        try:
                            await client.disconnect()
                        except Exception:
                            pass
                    return {
                        "status": "password_required",
                        "message": "Two-factor authentication password required",
                    }
                await client.check_password(password)
            except PhoneCodeInvalid:
                if client.is_connected:
                    try:
                        await client.disconnect()
                    except Exception:
                        pass
                return {
                    "status": "error",
                    "error": "Invalid phone code",
                }
            except AuthKeyUnregistered:
                if client.is_connected:
                    try:
                        await client.disconnect()
                    except Exception:
                        pass
                # Удаляем из активных клиентов
                if user_id in self._active_clients:
                    del self._active_clients[user_id]
                return {
                    "status": "error",
                    "error": "Session expired. Please start auth again.",
                }

            # Авторизация успешна
            user_auth["authorized"] = True
            user_auth.pop("phone_code_hash", None)
            self._save_auth_data(auth_data)

            # Получаем информацию о пользователе
            me = await client.get_me()

            # Удаляем клиент из активных после успешной авторизации
            # Сессия сохранена в файл, можно переподключиться позже
            # Проверяем, что клиент из активных - это тот же объект, что и текущий
            if user_id in self._active_clients:
                # Если это тот же клиент, отключаем только один раз
                if self._active_clients[user_id] is client:
                    if client.is_connected:
                        try:
                            await client.disconnect()
                        except Exception:
                            pass
                else:
                    # Если разные клиенты, отключаем оба
                    if self._active_clients[user_id].is_connected:
                        try:
                            await self._active_clients[user_id].disconnect()
                        except Exception:
                            pass
                    if client.is_connected:
                        try:
                            await client.disconnect()
                        except Exception:
                            pass
                del self._active_clients[user_id]
            elif client.is_connected:
                # Если клиента нет в активных, но он подключен, отключаем
                try:
                    await client.disconnect()
                except Exception:
                    pass

            return {
                "status": "authorized",
                "message": "Successfully authorized",
                "user": {
                    "id": me.id,
                    "first_name": me.first_name,
                    "last_name": me.last_name,
                    "username": me.username,
                    "phone_number": me.phone_number,
                },
            }
        except Exception as e:
            logger.error(f"Error verifying code: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
            }

    async def get_client(self, user_id: str) -> Optional[Client]:
        """
        Получает или создает клиент для пользователя

        Args:
            user_id: ID пользователя в системе

        Returns:
            Pyrogram Client или None
        """
        # Проверяем кэш
        if user_id in self._active_clients:
            client = self._active_clients[user_id]
            if client.is_connected:
                return client

        auth_data = self._load_auth_data()
        user_auth = auth_data.get(user_id)

        if not user_auth or not user_auth.get("authorized"):
            return None

        try:
            session_name = f"{SESSIONS_DIR}/{user_id}"
            client = Client(
                name=session_name,
                api_id=user_auth["api_id"],
                api_hash=user_auth["api_hash"],
            )

            await client.start()
            self._active_clients[user_id] = client
            return client
        except Exception as e:
            logger.error(f"Error getting client for user {user_id}: {e}")
            return None

    async def send_message(
        self, user_id: str, recipient_id: str, text: str
    ) -> Dict[str, Any]:
        """
        Отправляет сообщение от имени пользователя

        Args:
            user_id: ID пользователя в системе (отправитель)
            recipient_id: Telegram user ID или username получателя
            text: Текст сообщения

        Returns:
            Результат отправки
        """
        try:
            client = await self.get_client(user_id)
            if not client:
                return {
                    "success": False,
                    "error": "User not authorized. Please complete authorization first.",
                }

            # Пытаемся отправить сообщение
            try:
                # Преобразуем recipient_id в нужный формат
                # recipient_id может быть числом (int) или строкой
                if isinstance(recipient_id, (int, str)):
                    # Если это строка и состоит из цифр, преобразуем в int
                    if isinstance(recipient_id, str) and recipient_id.isdigit():
                        recipient = int(recipient_id)
                    elif isinstance(recipient_id, int):
                        recipient = recipient_id
                    else:
                        # Иначе считаем username
                        recipient = recipient_id

                    logger.info(
                        f"Sending message to recipient: {recipient} (type: {type(recipient).__name__})"
                    )
                    message = await client.send_message(recipient, text)
                else:
                    raise ValueError(f"Invalid recipient_id type: {type(recipient_id)}")

                return {
                    "success": True,
                    "message_id": message.id,
                    "date": message.date.isoformat() if message.date else None,
                }
            except Exception as send_error:
                logger.error(f"Error sending message: {send_error}")
                return {
                    "success": False,
                    "error": f"Failed to send message: {str(send_error)}",
                }
        except Exception as e:
            logger.error(f"Error in send_message: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    def is_authorized(self, user_id: str) -> bool:
        """Проверяет, авторизован ли пользователь"""
        auth_data = self._load_auth_data()
        user_auth = auth_data.get(user_id)
        return user_auth is not None and user_auth.get("authorized", False)

    def find_user_by_phone(self, phone_number: str) -> Optional[str]:
        """
        Находит user_id по номеру телефона в сохраненных данных

        Args:
            phone_number: Номер телефона в любом формате

        Returns:
            user_id или None если не найден
        """
        auth_data = self._load_auth_data()

        # Нормализуем номер телефона (убираем пробелы, скобки, дефисы)
        normalized_phone = (
            phone_number.replace(" ", "")
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
            .replace("+", "")
        )

        for user_id, user_auth in auth_data.items():
            saved_phone = user_auth.get("phone_number", "")
            # Нормализуем сохраненный номер
            normalized_saved = (
                saved_phone.replace(" ", "")
                .replace("(", "")
                .replace(")", "")
                .replace("-", "")
                .replace("+", "")
            )

            # Сравниваем нормализованные номера
            if normalized_phone == normalized_saved or saved_phone == phone_number:
                return user_id

        return None

    def is_authorized_by_phone(self, phone_number: str) -> bool:
        """Проверяет, авторизован ли пользователь по номеру телефона"""
        user_id = self.find_user_by_phone(phone_number)
        if not user_id:
            return False
        return self.is_authorized(user_id)

    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Получает информацию о пользователе"""
        try:
            client = await self.get_client(user_id)
            if not client:
                return None

            me = await client.get_me()
            return {
                "id": me.id,
                "first_name": me.first_name,
                "last_name": me.last_name,
                "username": me.username,
                "phone_number": me.phone_number,
            }
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None

    async def get_user_info_by_phone(
        self, phone_number: str
    ) -> Optional[Dict[str, Any]]:
        """Получает информацию о пользователе по номеру телефона"""
        user_id = self.find_user_by_phone(phone_number)
        if not user_id:
            return None
        return await self.get_user_info(user_id)

    async def get_contacts_by_phone(self, phone_number: str) -> Dict[str, Any]:
        """
        Получает список контактов Telegram пользователя по номеру телефона

        Args:
            phone_number: Номер телефона пользователя

        Returns:
            Список контактов с информацией о пользователях
        """
        try:
            user_id = self.find_user_by_phone(phone_number)
            if not user_id:
                return {
                    "status": "error",
                    "error": "User not found by phone number",
                    "contacts": [],
                }

            client = await self.get_client(user_id)
            if not client:
                return {
                    "status": "error",
                    "error": "User not authorized. Please complete authorization first.",
                    "contacts": [],
                }

            return await self._get_contacts_from_client(client, user_id)
        except Exception as e:
            logger.error(f"Error getting contacts: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "contacts": [],
            }

    async def get_contacts_by_tg_id(self, tg_user_id: int) -> Dict[str, Any]:
        """
        Получает список контактов Telegram пользователя по Telegram user ID

        Args:
            tg_user_id: Telegram user ID

        Returns:
            Список контактов с информацией о пользователях
        """
        try:
            # Ищем user_id по tg_user_id через все сессии
            auth_data = self._load_auth_data()
            found_user_id = None

            for user_id, user_auth in auth_data.items():
                if not user_auth.get("authorized"):
                    continue

                try:
                    client = await self.get_client(user_id)
                    if client:
                        me = await client.get_me()
                        if me.id == tg_user_id:
                            found_user_id = user_id
                            break
                except:
                    continue

            if not found_user_id:
                return {
                    "status": "error",
                    "error": "User not found by Telegram user ID",
                    "contacts": [],
                }

            client = await self.get_client(found_user_id)
            if not client:
                return {
                    "status": "error",
                    "error": "User not authorized. Please complete authorization first.",
                    "contacts": [],
                }

            return await self._get_contacts_from_client(client, found_user_id)
        except Exception as e:
            logger.error(f"Error getting contacts by tg_id: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "contacts": [],
            }

    async def _get_contacts_from_client(
        self, client: Client, user_id: str
    ) -> Dict[str, Any]:
        """
        Внутренний метод для получения контактов из адресной книги текущей сессии

        Args:
            client: Pyrogram Client (уже авторизованная сессия)
            user_id: ID пользователя в системе

        Returns:
            Список контактов с информацией о пользователях из адресной книги
        """
        # Проверяем, что клиент подключен
        if not client.is_connected:
            await client.connect()

        logger.info(f"Getting contacts for user {user_id}")
        logger.info(f"Client is connected: {client.is_connected}")

        # Получаем контакты из адресной книги текущей авторизованной сессии
        contacts = []

        try:
            # Используем только get_contacts() - получаем контакты из адресной книги
            logger.info("Fetching contacts from Telegram address book...")
            contact_count = 0

            # В Pyrogram get_contacts() возвращает список, а не асинхронный итератор
            contacts_list = await client.get_contacts()

            for contact in contacts_list:
                contact_count += 1
                contacts.append(
                    {
                        "id": contact.id,
                        "first_name": contact.first_name or "",
                        "last_name": contact.last_name or "",
                        "username": contact.username or "",
                        "phone_number": contact.phone_number or "",
                        "is_contact": True,
                    }
                )
                logger.debug(
                    f"Contact {contact_count}: {contact.first_name or 'Unknown'} "
                    f"(ID: {contact.id}, username: {contact.username or 'N/A'})"
                )

            logger.info(f"Found {contact_count} contacts in address book")

            if contact_count == 0:
                logger.warning(
                    f"No contacts found in address book for user {user_id}. "
                    f"This means the Telegram account has no saved contacts."
                )
        except Exception as e:
            logger.error(
                f"Error getting contacts from address book: {e}", exc_info=True
            )
            return {
                "status": "error",
                "error": f"Failed to get contacts: {str(e)}",
                "contacts": [],
            }

        # Сортируем контакты по имени
        contacts.sort(key=lambda x: (x.get("first_name", "") or "").lower())

        logger.info(f"Returning {len(contacts)} contacts for user {user_id}")

        return {
            "status": "ok",
            "contacts": contacts,
        }

    async def disconnect(self, user_id: str) -> bool:
        """Отключает клиент пользователя"""
        try:
            if user_id in self._active_clients:
                client = self._active_clients[user_id]
                if client.is_connected:
                    await client.stop()
                del self._active_clients[user_id]

            # Удаляем данные авторизации
            auth_data = self._load_auth_data()
            if user_id in auth_data:
                del auth_data[user_id]
                self._save_auth_data(auth_data)

            # Удаляем файл сессии
            session_file = SESSIONS_DIR / f"{user_id}.session"
            if session_file.exists():
                session_file.unlink()

            return True
        except Exception as e:
            logger.error(f"Error disconnecting user {user_id}: {e}")
            return False
