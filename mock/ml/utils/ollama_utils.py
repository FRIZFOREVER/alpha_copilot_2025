"""Утилиты для работы с Ollama"""
import json
import logging
import time
from typing import Any, Generator

import httpx
from ollama import Client

from config import OLLAMA_HOST, DEFAULT_MODEL
from models.schemas import Message, StreamChunk

logger = logging.getLogger(__name__)

ollama_client = None


def get_ollama_client() -> Client:
    """Получает или создает клиент Ollama (ленивая инициализация)"""
    global ollama_client
    if ollama_client is None:
        host_for_client = OLLAMA_HOST

        if host_for_client.startswith("http://"):
            host_for_client = host_for_client.replace("http://", "")
        elif host_for_client.startswith("https://"):
            host_for_client = host_for_client.replace("https://", "")

        host_for_client = host_for_client.rstrip("/")

        try:
            ollama_client = Client(host=host_for_client)
            logger.info(
                f"Ollama client created with host: {host_for_client} (from OLLAMA_HOST: {OLLAMA_HOST})"
            )
        except Exception as e:
            logger.error(f"Failed to create Ollama client: {e}")
            try:
                if ":" in host_for_client:
                    host_only = host_for_client.split(":")[0]
                    port = (
                        host_for_client.split(":")[1]
                        if ":" in host_for_client
                        else "11434"
                    )
                    ollama_client = Client(host=f"{host_only}:{port}")
                    logger.info(f"Ollama client created with host: {host_only}:{port}")
                else:
                    raise e
            except Exception as e2:
                logger.error(f"All attempts to create client failed: {e2}")
                raise
    return ollama_client


def check_ollama_available(max_retries: int = 5, retry_delay: int = 2) -> bool:
    """Проверяет доступность Ollama с повторными попытками"""
    for attempt in range(max_retries):
        try:
            client = get_ollama_client()
            response = client.list()
            logger.info(f"Ollama is available. Response type: {type(response)}")
            return True
        except Exception as e:
            error_str = str(e)
            error_type = type(e).__name__
            logger.warning(
                f"Ollama not available yet (attempt {attempt + 1}/{max_retries}): {error_type}: {error_str}"
            )

            if "401" in error_str or "unauthorized" in error_str.lower():
                logger.error("401 Unauthorized error detected. This might indicate:")
                logger.error(
                    "  1. Ollama requires authentication (check OLLAMA_API_KEY)"
                )
                logger.error(f"  2. Incorrect host format (current: {OLLAMA_HOST})")
                logger.error("  3. Network connectivity issue")

            if attempt < max_retries - 1:
                logger.warning(f"Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                logger.error(
                    f"Ollama is not available after {max_retries} attempts: {error_str}"
                )
                return False
    return False


def ensure_model_available(client: Client, model_name: str) -> str:
    """Проверяет наличие модели и загружает её, если нужно"""
    try:
        models_response = client.list()
        available_models = []

        if isinstance(models_response, dict) and "models" in models_response:
            available_models = [m.get("name", "") for m in models_response["models"]]
        elif isinstance(models_response, list):
            available_models = [
                m.get("name", "") if isinstance(m, dict) else str(m)
                for m in models_response
            ]

        model_found = any(
            model_name in model
            or model == model_name
            or model.startswith(model_name.split(":")[0])
            for model in available_models
        )

        if not model_found:
            logger.info(
                f"Model '{model_name}' not found. Available models: {available_models}"
            )
            logger.info(f"Attempting to pull model '{model_name}'...")
            try:
                client.pull(model=model_name)
                logger.info(f"Model '{model_name}' successfully pulled")
            except Exception as pull_error:
                logger.error(f"Failed to pull model '{model_name}': {pull_error}")
                if available_models:
                    logger.warning(
                        f"Using first available model instead: {available_models[0]}"
                    )
                    return available_models[0]
                else:
                    raise Exception(
                        f"Model '{model_name}' not found and could not be pulled. No models available."
                    )
        else:
            logger.info(f"Model '{model_name}' is available")

        return model_name
    except Exception as e:
        logger.error(f"Error checking model availability: {e}")
        raise


def mock_workflow(
    payload: dict[str, Any], streaming: bool = True
) -> Generator[StreamChunk, None, None]:
    """Функция workflow, которая обращается к локальной Ollama и использует модель"""
    model = payload.get("model", DEFAULT_MODEL)
    messages = payload.get("messages", [])

    ollama_messages = []
    for msg in messages:
        if isinstance(msg, dict):
            ollama_messages.append(
                {"role": msg.get("role", "user"), "content": msg.get("content", "")}
            )
        else:
            ollama_messages.append(
                {
                    "role": getattr(msg, "role", "user"),
                    "content": getattr(msg, "content", str(msg)),
                }
            )

    try:
        client = get_ollama_client()
        model = ensure_model_available(client, model)

        base_url = OLLAMA_HOST.rstrip("/")
        if not base_url.endswith("/api"):
            chat_url = f"{base_url}/api/chat"
        else:
            chat_url = f"{base_url}/chat"

        chat_payload = {"model": model, "messages": ollama_messages, "stream": True}

        logger.info(f"Making chat request to {chat_url}")
        logger.info(f"Base OLLAMA_HOST: {OLLAMA_HOST}")
        logger.info(f"Payload model: {model}, messages count: {len(ollama_messages)}")

        with httpx.Client(timeout=300.0, follow_redirects=True) as http_client:
            with http_client.stream(
                "POST",
                chat_url,
                json=chat_payload,
                headers={"Content-Type": "application/json"},
            ) as response:
                logger.info(f"Chat response status: {response.status_code}")
                logger.info(f"Response headers: {dict(response.headers)}")

                if response.status_code != 200:
                    error_text = f"Status {response.status_code}"
                    try:
                        error_lines = []
                        for line in response.iter_lines():
                            error_lines.append(line)
                            if len(error_lines) >= 5:
                                break
                        if error_lines:
                            error_text = " ".join(error_lines)[:500]
                    except Exception as e:
                        error_text = (
                            f"Status {response.status_code}, could not read error: {str(e)}"
                        )
                    logger.error(f"Chat request failed: {error_text}")
                    raise Exception(
                        f"Ollama API returned status {response.status_code}: {error_text}"
                    )

                accumulated_content = ""
                eval_count = 0
                chunk = None

                for line in response.iter_lines():
                    if not line:
                        continue

                    if not line.strip().startswith("{"):
                        continue

                    try:
                        json_data = json.loads(line)

                        message_data = json_data.get("message", {})
                        chunk_content = (
                            message_data.get("content", "") if message_data else ""
                        )
                        done = json_data.get("done", False)
                        done_reason = json_data.get("done_reason")

                        if chunk_content:
                            accumulated_content += chunk_content
                            eval_count += 1

                            chunk = StreamChunk(
                                model=model,
                                done=done,
                                done_reason=done_reason,
                                message=Message(
                                    role="assistant",
                                    content=chunk_content,
                                    thinking=None,
                                ),
                                eval_count=eval_count,
                                prompt_eval_count=json_data.get(
                                    "prompt_eval_count",
                                    len(messages) if messages else 1,
                                ),
                                total_duration=json_data.get("total_duration"),
                                prompt_eval_duration=json_data.get(
                                    "prompt_eval_duration"
                                ),
                                eval_duration=json_data.get("eval_duration"),
                                load_duration=json_data.get("load_duration"),
                            )
                            yield chunk

                        if done:
                            if chunk is None or not chunk.done:
                                final_chunk = StreamChunk(
                                    model=model,
                                    done=True,
                                    done_reason=done_reason or "stop",
                                    message=Message(role="assistant", content=""),
                                    eval_count=(
                                        eval_count
                                        if eval_count > 0
                                        else json_data.get("eval_count", 0)
                                    ),
                                    prompt_eval_count=json_data.get(
                                        "prompt_eval_count",
                                        len(messages) if messages else 1,
                                    ),
                                    total_duration=json_data.get("total_duration"),
                                    prompt_eval_duration=json_data.get(
                                        "prompt_eval_duration"
                                    ),
                                    eval_duration=json_data.get("eval_duration"),
                                    load_duration=json_data.get("load_duration"),
                                )
                                yield final_chunk

                            break

                    except json.JSONDecodeError:
                        continue

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error calling Ollama: {error_msg}", exc_info=True)
        logger.error(f"OLLAMA_HOST: {OLLAMA_HOST}")
        logger.error(f"Model: {model}")
        logger.error(f"Messages count: {len(ollama_messages)}")

        error_chunk = StreamChunk(
            model=model,
            done=True,
            done_reason="error",
            message=Message(
                role="assistant",
                content=f"Ошибка при обращении к Ollama: {error_msg}. Проверьте, что Ollama запущен и доступен по адресу {OLLAMA_HOST}",
            ),
        )
        yield error_chunk

