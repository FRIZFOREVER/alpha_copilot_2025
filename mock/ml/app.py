import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from ollama import Client
from pydantic import BaseModel
from telegram_user_service import TelegramUserService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
if OLLAMA_HOST.endswith("/v1"):
    OLLAMA_HOST = OLLAMA_HOST[:-3]
elif OLLAMA_HOST.endswith("/"):
    OLLAMA_HOST = OLLAMA_HOST[:-1]

TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")

ollama_client = None


def get_ollama_client():
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
                    port = host_for_client.split(":")[1] if ":" in host_for_client else "11434"
                    ollama_client = Client(host=f"{host_only}:{port}")
                    logger.info(f"Ollama client created with host: {host_only}:{port}")
                else:
                    raise e
            except Exception as e2:
                logger.error(f"All attempts to create client failed: {e2}")
                raise
    return ollama_client


def check_ollama_available(max_retries=5, retry_delay=2):
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
                logger.error("  1. Ollama requires authentication (check OLLAMA_API_KEY)")
                logger.error(f"  2. Incorrect host format (current: {OLLAMA_HOST})")
                logger.error("  3. Network connectivity issue")

            if attempt < max_retries - 1:
                logger.warning(f"Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Ollama is not available after {max_retries} attempts: {error_str}")
                return False
    return False


app = FastAPI(title="Mock ML Service")

app.state.models_ready = asyncio.Event()
app.state.telegram_user_service = TelegramUserService()


@app.on_event("startup")
async def startup_event():
    """Проверяем доступность Ollama при старте приложения"""
    logger.info("Starting up Mock ML Service...")
    logger.info(f"OLLAMA_HOST environment variable: {os.getenv('OLLAMA_HOST', 'not set')}")
    logger.info(f"Using OLLAMA_HOST: {OLLAMA_HOST}")

    await asyncio.sleep(5)

    if check_ollama_available(max_retries=10, retry_delay=3):
        app.state.models_ready.set()
        logger.info("Mock ML Service is ready and Ollama is available")
    else:
        logger.warning("Ollama is not available, but service will continue. Requests may fail.")
        app.state.models_ready.set()


class Message(BaseModel):
    role: str = "assistant"
    content: str = ""
    thinking: str | None = None
    images: str | None = None
    tool_name: str | None = None
    tool_calls: str | None = None


class StreamChunk(BaseModel):
    model: str = "qwen3:0.6b"
    created_at: str = None
    done: bool = False
    done_reason: str | None = None
    total_duration: int | None = None
    load_duration: int | None = None
    prompt_eval_count: int | None = None
    prompt_eval_duration: int | None = None
    eval_count: int | None = None
    eval_duration: int | None = None
    message: Message = None


class TelegramAuthStartRequest(BaseModel):
    user_id: str
    phone_number: str


class TelegramAuthVerifyRequest(BaseModel):
    user_id: str
    phone_code: str
    password: str | None = None


class TelegramUserSendRequest(BaseModel):
    user_id: str
    recipient_id: str
    text: str


def ensure_model_available(client: Client, model_name: str):
    """Проверяет наличие модели и загружает её, если нужно"""
    try:
        models_response = client.list()
        available_models = []

        if isinstance(models_response, dict) and "models" in models_response:
            available_models = [m.get("name", "") for m in models_response["models"]]
        elif isinstance(models_response, list):
            available_models = [
                m.get("name", "") if isinstance(m, dict) else str(m) for m in models_response
            ]

        model_found = any(
            model_name in model or model == model_name or model.startswith(model_name.split(":")[0])
            for model in available_models
        )

        if not model_found:
            logger.info(f"Model '{model_name}' not found. Available models: {available_models}")
            logger.info(f"Attempting to pull model '{model_name}'...")
            try:
                client.pull(model=model_name)
                logger.info(f"Model '{model_name}' successfully pulled")
            except Exception as pull_error:
                logger.error(f"Failed to pull model '{model_name}': {pull_error}")
                if available_models:
                    logger.warning(f"Using first available model instead: {available_models[0]}")
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


def mock_workflow(payload: dict[str, Any], streaming: bool = True):
    """Функция workflow, которая обращается к локальной Ollama и использует модель gpt-oss:120b-cloud"""
    default_model = "gpt-oss:120b-cloud"
    model = payload.get("model", default_model)
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
                user_id = payload.get("user_id")
                send_to_telegram = payload.get("send_to_telegram", False)

                for line in response.iter_lines():
                    if not line:
                        continue

                    if not line.strip().startswith("{"):
                        continue

                    try:
                        json_data = json.loads(line)

                        message_data = json_data.get("message", {})
                        chunk_content = message_data.get("content", "") if message_data else ""
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
                                prompt_eval_duration=json_data.get("prompt_eval_duration"),
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
                                    prompt_eval_duration=json_data.get("prompt_eval_duration"),
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


@app.get("/")
async def root():
    return {"message": "Mock ML Service is running"}


@app.get("/health")
async def health():
    return {"status": "healthy", "models_ready": app.state.models_ready.is_set()}


@app.get("/ping")
async def ping():
    """Эндпоинт для проверки доступности сервиса"""
    return {"status": "ok", "message": "pong"}


@app.get("/ollama/check")
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
            models_list = [model.get("name", "unknown") for model in models_response["models"]]
        elif isinstance(models_response, list):
            models_list = [
                model.get("name", "unknown") if isinstance(model, dict) else str(model)
                for model in models_response
            ]

        default_model = "gpt-oss:120b-cloud"
        model_available = any(
            default_model in model
            or model == default_model
            or model.startswith(default_model.split(":")[0])
            for model in models_list
        )

        return {
            "status": "ok",
            "ollama_host": OLLAMA_HOST,
            "available": True,
            "http_check": http_check,
            "models": models_list,
            "default_model": default_model,
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


@app.post("/ollama/pull")
async def pull_model(request: Request):
    """Эндпоинт для загрузки модели в Ollama"""
    try:
        payload: dict[str, Any] = await request.json()
        model_name = payload.get("model", "gpt-oss:120b-cloud")

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


@app.post("/message_stream")
async def message_stream(request: Request) -> StreamingResponse:
    models_ready = app.state.models_ready

    if not models_ready.is_set():
        raise HTTPException(status_code=503, detail="Models are still initialising")

    payload: dict[str, Any] = await request.json()
    logger.info(f"Handling /message_stream request with payload: {payload}")

    for item in payload:
        if item != "messages":
            logger.info("Got item: %s", item)

    # Нормализуем send_to_telegram - может прийти как строка "true"/"false" или булево значение
    send_to_telegram_raw = payload.get("send_to_telegram", False)
    if isinstance(send_to_telegram_raw, str):
        send_to_telegram = send_to_telegram_raw.lower() in ("true", "1", "yes")
    else:
        send_to_telegram = bool(send_to_telegram_raw)

    logger.info(
        f"Parsed send_to_telegram: raw={send_to_telegram_raw}, type={type(send_to_telegram_raw).__name__}, normalized={send_to_telegram}"
    )

    user_id = payload.get("user_id")
    recipient_id = payload.get("recipient_id")  # Telegram user ID получателя
    tg_user_id = payload.get("tg_user_id")  # Альтернативное поле для recipient_id

    def event_generator():
        # Логируем значения переменных в начале генератора
        logger.info(
            f"event_generator started. send_to_telegram={send_to_telegram}, "
            f"type={type(send_to_telegram).__name__}, "
            f"recipient_id={recipient_id}, phone_number={payload.get('phone_number')}"
        )

        stream = mock_workflow(payload, streaming=True)
        accumulated_content = ""

        for chunk in stream:
            chunk_data = chunk.model_dump_json()
            # Сохраняем накопленный контент для возможной отправки в Telegram
            if chunk.message and chunk.message.content:
                accumulated_content += chunk.message.content
            yield f"data: {chunk_data}\n\n"

        # Логируем состояние перед проверкой отправки в Telegram
        logger.info(
            f"Stream completed. send_to_telegram={send_to_telegram}, "
            f"type={type(send_to_telegram).__name__}, "
            f"accumulated_content length={len(accumulated_content)}, "
            f"accumulated_content preview={accumulated_content[:100] if accumulated_content else 'empty'}"
        )

        # Отправляем в Telegram после завершения стрима, если указано
        if send_to_telegram and accumulated_content:
            logger.info("Entering Telegram send block")
            try:
                logger.info(
                    f"Starting Telegram send process. send_to_telegram={send_to_telegram}, content_length={len(accumulated_content)}"
                )
                target_recipient = recipient_id or tg_user_id
                phone_number = payload.get("phone_number")  # Номер телефона для поиска user_id
                telegram_user_service: TelegramUserService = app.state.telegram_user_service

                logger.info(
                    f"Attempting to send Telegram message. "
                    f"send_to_telegram={send_to_telegram}, "
                    f"recipient_id={recipient_id}, "
                    f"tg_user_id={tg_user_id}, "
                    f"target_recipient={target_recipient}, "
                    f"phone_number={phone_number}, "
                    f"accumulated_content length={len(accumulated_content)}"
                )

                if not target_recipient:
                    logger.warning("recipient_id required for sending Telegram message")
                    logger.warning(
                        f"target_recipient={target_recipient}, recipient_id={recipient_id}, tg_user_id={tg_user_id}"
                    )
                elif not phone_number:
                    logger.warning("phone_number required for sending Telegram message")
                    logger.warning(f"phone_number={phone_number}")
                else:
                    # Находим user_id по номеру телефона
                    found_user_id = telegram_user_service.find_user_by_phone(phone_number)
                    logger.info(f"Found user_id={found_user_id} for phone_number={phone_number}")
                    if not found_user_id:
                        logger.warning(f"User not found by phone number: {phone_number}")
                    else:
                        try:
                            loop = asyncio.get_event_loop()
                        except RuntimeError:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)

                        # Преобразуем recipient_id в строку для передачи
                        recipient_id_str = str(target_recipient)

                        if loop.is_running():

                            async def send_telegram_with_logging():
                                try:
                                    result = await telegram_user_service.send_message(
                                        user_id=found_user_id,
                                        recipient_id=recipient_id_str,
                                        text=accumulated_content,
                                    )
                                    if result.get("success"):
                                        logger.info(
                                            f"Telegram message sent successfully as user {found_user_id} "
                                            f"(phone: {phone_number}) to {target_recipient}"
                                        )
                                    else:
                                        logger.error(
                                            f"Failed to send Telegram message: {result.get('error')}"
                                        )
                                except Exception as e:
                                    logger.error(
                                        f"Exception while sending Telegram message: {e}",
                                        exc_info=True,
                                    )

                            task = asyncio.create_task(send_telegram_with_logging())
                            logger.info(
                                f"Telegram message task created for user {found_user_id} "
                                f"(phone: {phone_number}) to {target_recipient}"
                            )
                        else:
                            result = loop.run_until_complete(
                                telegram_user_service.send_message(
                                    user_id=found_user_id,
                                    recipient_id=recipient_id_str,
                                    text=accumulated_content,
                                )
                            )
                            if result.get("success"):
                                logger.info(
                                    f"Telegram message sent successfully as user {found_user_id} "
                                    f"(phone: {phone_number}) to {target_recipient}"
                                )
                            else:
                                logger.error(
                                    f"Failed to send Telegram message: {result.get('error')}"
                                )
            except Exception as tg_error:
                logger.error(f"Failed to send Telegram message: {tg_error}", exc_info=True)
        else:
            if not send_to_telegram:
                logger.info("send_to_telegram is False, skipping Telegram send")
            elif not accumulated_content:
                logger.warning(
                    f"accumulated_content is empty (length={len(accumulated_content)}), skipping Telegram send"
                )

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
        },
    )


@app.post("/generate")
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


@app.post("/telegram/user/auth/start")
async def start_telegram_user_auth(request: TelegramAuthStartRequest):
    """Начинает процесс авторизации Telegram пользователя"""
    try:
        if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
            raise HTTPException(
                status_code=500,
                detail="Telegram API credentials not configured. Please contact administrator.",
            )

        telegram_user_service: TelegramUserService = app.state.telegram_user_service
        result = await telegram_user_service.start_auth(
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


@app.post("/telegram/user/auth/verify")
async def verify_telegram_user_auth(request: TelegramAuthVerifyRequest):
    """Подтверждает код авторизации Telegram пользователя"""
    try:
        telegram_user_service: TelegramUserService = app.state.telegram_user_service
        result = await telegram_user_service.verify_code(
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


@app.post("/telegram/user/status")
async def get_telegram_user_status(request: Request):
    """Получает статус авторизации Telegram пользователя по номеру телефона"""
    try:
        payload: dict[str, Any] = await request.json()
        phone_number = payload.get("phone_number")

        if not phone_number:
            raise HTTPException(status_code=400, detail="phone_number is required")

        telegram_user_service: TelegramUserService = app.state.telegram_user_service
        is_authorized = telegram_user_service.is_authorized_by_phone(phone_number)

        result = {
            "status": "ok",
            "authorized": is_authorized,
        }

        if is_authorized:
            user_info = await telegram_user_service.get_user_info_by_phone(phone_number)
            if user_info:
                result["user_info"] = user_info

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Telegram user status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/telegram/user/contacts")
async def get_telegram_user_contacts(request: Request):
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

        telegram_user_service: TelegramUserService = app.state.telegram_user_service

        # Приоритет: сначала пробуем по tg_user_id, потом по phone_number
        if tg_user_id:
            try:
                tg_id = int(tg_user_id)
                result = await telegram_user_service.get_contacts_by_tg_id(tg_id)
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail="tg_user_id must be a valid integer")
        else:
            result = await telegram_user_service.get_contacts_by_phone(phone_number)

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("error"))

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Telegram contacts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/telegram/user/send")
async def send_telegram_user_message(request: TelegramUserSendRequest):
    """Отправляет сообщение от имени пользователя в Telegram"""
    try:
        telegram_user_service: TelegramUserService = app.state.telegram_user_service
        result = await telegram_user_service.send_message(
            user_id=request.user_id,
            recipient_id=request.recipient_id,
            text=request.text,
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


@app.post("/telegram/user/disconnect")
async def disconnect_telegram_user(request: Request):
    """Отключает Telegram пользователя"""
    try:
        payload: dict[str, Any] = await request.json()
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")

        telegram_user_service: TelegramUserService = app.state.telegram_user_service
        success = await telegram_user_service.disconnect(user_id)

        if success:
            return {"status": "ok", "message": "Telegram user disconnected"}
        else:
            raise HTTPException(status_code=404, detail="Telegram user connection not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disconnecting Telegram user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
