"""
Сервис для отправки email сообщений от имени пользователя
"""

import os
import json
import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_DIR = Path(os.getenv("TELEGRAM_DATA_DIR", "/app/data"))
EMAIL_AUTH_DATA_FILE = DATA_DIR / "email_auth.json"

# Автоматическое определение SMTP настроек по домену
SMTP_CONFIGS = {
    "gmail.com": {
        "host": "smtp.gmail.com",
        "port": 587,
        "start_tls": True,  # STARTTLS для порта 587
        "use_tls": False,
    },
    "outlook.com": {
        "host": "smtp-mail.outlook.com",
        "port": 587,
        "start_tls": True,
        "use_tls": False,
    },
    "hotmail.com": {
        "host": "smtp-mail.outlook.com",
        "port": 587,
        "start_tls": True,
        "use_tls": False,
    },
    "yahoo.com": {
        "host": "smtp.mail.yahoo.com",
        "port": 587,
        "start_tls": True,
        "use_tls": False,
    },
    "mail.ru": {
        "host": "smtp.mail.ru",
        "port": 587,
        "start_tls": True,
        "use_tls": False,
    },
    "yandex.ru": {
        "host": "smtp.yandex.ru",
        "port": 587,
        "start_tls": True,
        "use_tls": False,
    },
}

# Значения по умолчанию
DEFAULT_SMTP_CONFIG = {
    "host": "smtp.gmail.com",
    "port": 587,
    "start_tls": True,
    "use_tls": False,
}


class EmailService:
    """Сервис для отправки email сообщений от имени пользователя"""

    def __init__(self):
        self._ensure_data_files()

    def _ensure_data_files(self):
        """Создает необходимые файлы и директории"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not EMAIL_AUTH_DATA_FILE.exists():
            with open(EMAIL_AUTH_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load_auth_data(self) -> Dict[str, Dict[str, Any]]:
        """Загружает данные авторизации email"""
        try:
            if EMAIL_AUTH_DATA_FILE.exists():
                with open(EMAIL_AUTH_DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.debug(f"Loaded email auth data: {list(data.keys())}")
                    return data
            return {}
        except Exception as e:
            logger.error(f"Error loading email auth data: {e}")
            return {}

    def _save_auth_data(self, auth_data: Dict[str, Dict[str, Any]]):
        """Сохраняет данные авторизации email"""
        try:
            with open(EMAIL_AUTH_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(auth_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving email auth data: {e}")
            raise

    def _get_smtp_config(self, email: str) -> Dict[str, Any]:
        """
        Автоматически определяет SMTP настройки по домену email

        Args:
            email: Email адрес

        Returns:
            SMTP конфигурация
        """
        domain = email.split("@")[-1].lower() if "@" in email else ""
        config = SMTP_CONFIGS.get(domain, DEFAULT_SMTP_CONFIG)
        logger.info(f"Using SMTP config for {domain}: {config}")
        return config

    def save_email_credentials(
        self,
        user_id: str,
        email: str,
        password: str,
    ) -> Dict[str, Any]:
        """
        Сохраняет учетные данные email пользователя
        SMTP настройки определяются автоматически по домену email

        Args:
            user_id: ID пользователя в системе
            email: Email адрес пользователя
            password: Пароль или токен приложения

        Returns:
            Результат сохранения
        """
        try:
            # Нормализуем email (приводим к lowercase)
            email_normalized = email.lower().strip()
            
            # Автоматически определяем SMTP настройки
            smtp_config = self._get_smtp_config(email_normalized)

            auth_data = self._load_auth_data()
            auth_data[user_id] = {
                "email": email_normalized,  # Сохраняем нормализованный email
                "password": password,  # В продакшене лучше шифровать
                "smtp_host": smtp_config["host"],
                "smtp_port": smtp_config["port"],
                "smtp_start_tls": smtp_config.get("start_tls", False),
                "smtp_use_tls": smtp_config.get("use_tls", False),
                "authorized": True,
            }
            self._save_auth_data(auth_data)
            logger.info(
                f"Email credentials saved for user {user_id} (email: {email_normalized}) with auto-detected SMTP: {smtp_config['host']}"
            )
            logger.debug(f"Current auth data keys: {list(auth_data.keys())}")
            return {
                "status": "ok",
                "message": "Email credentials saved",
                "smtp_host": smtp_config["host"],
            }
        except Exception as e:
            logger.error(f"Error saving email credentials: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    def find_user_by_email(self, email: str) -> Optional[str]:
        """
        Находит user_id по email адресу

        Args:
            email: Email адрес

        Returns:
            user_id или None
        """
        email_normalized = email.lower().strip()
        auth_data = self._load_auth_data()
        logger.debug(f"Searching for email: {email_normalized}")
        logger.debug(f"Available user_ids: {list(auth_data.keys())}")
        
        for user_id, user_data in auth_data.items():
            stored_email = user_data.get("email", "").lower()
            logger.debug(f"Checking user_id {user_id} with email: {stored_email}")
            if stored_email == email_normalized:
                logger.info(f"Found user_id {user_id} for email {email_normalized}")
                return user_id
        
        logger.warning(f"User not found for email: {email_normalized}")
        return None

    def is_authorized_by_email(self, email: str) -> bool:
        """Проверяет, авторизован ли пользователь по email"""
        user_id = self.find_user_by_email(email)
        if not user_id:
            logger.debug(f"No user_id found for email: {email}")
            return False
        auth_data = self._load_auth_data()
        is_authorized = auth_data.get(user_id, {}).get("authorized", False)
        logger.debug(f"User {user_id} authorized status: {is_authorized}")
        return is_authorized

    async def send_message(
        self,
        user_id: str,
        to_email: str,
        subject: str,
        text: str,
        html: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Отправляет email сообщение от имени пользователя

        Args:
            user_id: ID пользователя в системе (отправитель)
            to_email: Email получателя
            subject: Тема письма
            text: Текст сообщения (plain text)
            html: HTML версия сообщения (опционально)

        Returns:
            Результат отправки
        """
        try:
            auth_data = self._load_auth_data()
            user_credentials = auth_data.get(user_id)

            if not user_credentials:
                return {
                    "success": False,
                    "error": "User email credentials not found. Please authorize your email first.",
                }

            if not user_credentials.get("authorized"):
                return {
                    "success": False,
                    "error": "User email not authorized. Please authorize your email first.",
                }

            email = user_credentials.get("email")
            password = user_credentials.get("password")
            smtp_host = user_credentials.get("smtp_host")
            smtp_port = user_credentials.get("smtp_port")
            smtp_start_tls = user_credentials.get("smtp_start_tls", False)
            smtp_use_tls = user_credentials.get("smtp_use_tls", False)

            if not email or not password:
                return {
                    "success": False,
                    "error": "Email credentials incomplete",
                }

            # Создаем сообщение
            if html:
                message = MIMEMultipart("alternative")
                message["From"] = email
                message["To"] = to_email
                message["Subject"] = subject

                part1 = MIMEText(text, "plain", "utf-8")
                part2 = MIMEText(html, "html", "utf-8")

                message.attach(part1)
                message.attach(part2)
            else:
                message = MIMEText(text, "plain", "utf-8")
                message["From"] = email
                message["To"] = to_email
                message["Subject"] = subject

            # Отправляем через SMTP используя учетные данные пользователя
            # Для порта 587 используем STARTTLS, для 465 - TLS
            await aiosmtplib.send(
                message,
                hostname=smtp_host,
                port=smtp_port,
                username=email,
                password=password,
                start_tls=smtp_start_tls,
                use_tls=smtp_use_tls,
            )

            logger.info(f"Email sent successfully from {email} to {to_email}")
            return {
                "success": True,
                "message": f"Email sent from {email} to {to_email}",
            }

        except Exception as e:
            logger.error(f"Error sending email: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to send email: {str(e)}",
            }

