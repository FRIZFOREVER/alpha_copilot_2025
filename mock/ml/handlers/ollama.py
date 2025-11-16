"""Обработчики для Ollama endpoints"""
import asyncio
import httpx
import logging
from datetime import datetime
from typing import Any

from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse
from ollama import Client

from config import OLLAMA_HOST, DEFAULT_MODEL
from utils.ollama_utils import get_ollama_client, check_ollama_available

logger = logging.getLogger(__name__)


async def health_check(models_ready: asyncio.Event):
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "models_ready": models_ready.is_set()}


async def ping():
    """Эндпоинт для проверки доступности сервиса"""
    return {"status": "ok", "message": "pong"}


async def check_ollama():
    """Эндпоинт для проверки подключения к Ollama"""
    http_check = {"status": "unknown", "error": None}
    try:
        check_url = f"{OLLAMA_HOST}/api/tags"
        async with httpx.AsyncClient(timeout=10.0) as http_client:
            response = await http_client.get(check_url)
            if response.status_code == 200:
                http_check = {"status": "ok", "response": response.json()}
            else:
                http_check = {
                    "status": "error",
                    "status_code": response.status_code,
                    "text": response.text[:200],
                }
    except Exception as e:
        http_check = {"status": "error", "error": str(e)}

    try:
        client = get_ollama_client()
        models_response = client.list()

        models_list = []
        if isinstance(models_response, dict) and "models" in models_response:
            models_list = [
                model.get("name", "unknown") for model in models_response["models"]
            ]
        elif isinstance(models_response, list):
            models_list = [
                model.get("name", "unknown") if isinstance(model, dict) else str(model)
                for model in models_response
            ]

        model_available = any(
            DEFAULT_MODEL in model
            or model == DEFAULT_MODEL
            or model.startswith(DEFAULT_MODEL.split(":")[0])
            for model in models_list
        )

        return {
            "status": "ok",
            "ollama_host": OLLAMA_HOST,
            "available": True,
            "http_check": http_check,
            "models": models_list,
            "default_model": DEFAULT_MODEL,
            "model_available": model_available,
        }
    except Exception as e:
        logger.error(f"Ollama check failed: {e}", exc_info=True)
        return {
            "status": "error",
            "ollama_host": OLLAMA_HOST,
            "available": False,
            "http_check": http_check,
            "error": str(e),
            "error_type": type(e).__name__,
        }


async def pull_model(request: Request):
    """Эндпоинт для загрузки модели в Ollama"""
    try:
        payload: dict[str, Any] = await request.json()
        model_name = payload.get("model", DEFAULT_MODEL)

        logger.info(f"Pulling model '{model_name}'...")
        client = get_ollama_client()

        client.pull(model=model_name)

        return {
            "status": "ok",
            "message": f"Model '{model_name}' successfully pulled",
            "model": model_name,
        }
    except Exception as e:
        logger.error(f"Failed to pull model: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
        }


async def generate_message(request: Request):
    """Альтернативный endpoint для не-потокового ответа"""
    payload: dict[str, Any] = await request.json()
    logger.info(f"Handling /generate request with payload: {payload}")

    await asyncio.sleep(0.1)

    return {
        "model": payload.get("model", "qwen3:0.6b"),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "message": {
            "role": "assistant",
            "content": "Это моковый ответ от ML сервиса для не-потокового запроса.",
            "thinking": "Completed mock thinking process",
            "images": None,
            "tool_name": None,
            "tool_calls": None,
        },
        "done": True,
        "done_reason": "stop",
        "total_duration": 500000000,
        "load_duration": 100000000,
        "prompt_eval_count": 1,
        "prompt_eval_duration": 100000000,
        "eval_count": 10,
        "eval_duration": 300000000,
    }

