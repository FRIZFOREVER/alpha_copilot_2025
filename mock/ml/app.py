from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
import logging
import os
from typing import Dict, Any, Optional, List
import time
import uuid
from datetime import datetime
from ollama import Client
import httpx

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройка адреса Ollama из переменной окружения или используем значение по умолчанию
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
# Убираем /v1 из конца, если есть, так как библиотека ollama добавляет его сама
if OLLAMA_HOST.endswith("/v1"):
    OLLAMA_HOST = OLLAMA_HOST[:-3]
elif OLLAMA_HOST.endswith("/"):
    OLLAMA_HOST = OLLAMA_HOST[:-1]

# Глобальная переменная для клиента (создается лениво)
ollama_client = None


def get_ollama_client():
    """Получает или создает клиент Ollama (ленивая инициализация)"""
    global ollama_client
    if ollama_client is None:
        # Библиотека ollama ожидает host в формате "hostname:port" без протокола
        # Извлекаем host и port из OLLAMA_HOST
        host_for_client = OLLAMA_HOST

        # Убираем протокол если есть
        if host_for_client.startswith("http://"):
            host_for_client = host_for_client.replace("http://", "")
        elif host_for_client.startswith("https://"):
            host_for_client = host_for_client.replace("https://", "")

        # Убираем trailing slash
        host_for_client = host_for_client.rstrip("/")

        try:
            # Создаем клиент с host в формате "hostname:port"
            ollama_client = Client(host=host_for_client)
            logger.info(
                f"Ollama client created with host: {host_for_client} (from OLLAMA_HOST: {OLLAMA_HOST})"
            )
        except Exception as e:
            logger.error(f"Failed to create Ollama client: {e}")
            # Пробуем альтернативный вариант - только имя хоста
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


def check_ollama_available(max_retries=5, retry_delay=2):
    """Проверяет доступность Ollama с повторными попытками"""
    import time

    for attempt in range(max_retries):
        try:
            client = get_ollama_client()
            # Пробуем простой запрос для проверки доступности
            response = client.list()
            logger.info(f"Ollama is available. Response type: {type(response)}")
            return True
        except Exception as e:
            error_str = str(e)
            error_type = type(e).__name__
            logger.warning(
                f"Ollama not available yet (attempt {attempt + 1}/{max_retries}): {error_type}: {error_str}"
            )

            # Если это ошибка 401, это может быть проблема с форматом подключения
            if "401" in error_str or "unauthorized" in error_str.lower():
                logger.error(f"401 Unauthorized error detected. This might indicate:")
                logger.error(
                    f"  1. Ollama requires authentication (check OLLAMA_API_KEY)"
                )
                logger.error(f"  2. Incorrect host format (current: {OLLAMA_HOST})")
                logger.error(f"  3. Network connectivity issue")

            if attempt < max_retries - 1:
                logger.warning(f"Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                logger.error(
                    f"Ollama is not available after {max_retries} attempts: {error_str}"
                )
                return False
    return False


app = FastAPI(title="Mock ML Service")

# Состояние приложения
app.state.models_ready = asyncio.Event()


@app.on_event("startup")
async def startup_event():
    """Проверяем доступность Ollama при старте приложения"""
    logger.info("Starting up Mock ML Service...")
    logger.info(
        f"OLLAMA_HOST environment variable: {os.getenv('OLLAMA_HOST', 'not set')}"
    )
    logger.info(f"Using OLLAMA_HOST: {OLLAMA_HOST}")

    # Даем Ollama больше времени на запуск (healthcheck может пройти, но API еще не готов)
    await asyncio.sleep(5)

    # Проверяем доступность Ollama с несколькими попытками
    if check_ollama_available(max_retries=10, retry_delay=3):
        app.state.models_ready.set()
        logger.info("Mock ML Service is ready and Ollama is available")
    else:
        logger.warning(
            "Ollama is not available, but service will continue. Requests may fail."
        )
        # Устанавливаем флаг готовности в любом случае, чтобы не блокировать сервис
        app.state.models_ready.set()


class Message(BaseModel):
    role: str = "assistant"
    content: str = ""
    thinking: Optional[str] = None
    images: Optional[str] = None
    tool_name: Optional[str] = None
    tool_calls: Optional[str] = None


class StreamChunk(BaseModel):
    model: str = "qwen3:0.6b"
    created_at: str = None
    done: bool = False
    done_reason: Optional[str] = None
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None
    message: Message = None

    def __init__(self, **data):
        if "created_at" not in data:
            data["created_at"] = datetime.utcnow().isoformat() + "Z"
        if "message" not in data:
            data["message"] = Message()
        super().__init__(**data)


def ensure_model_available(client: Client, model_name: str):
    """Проверяет наличие модели и загружает её, если нужно"""
    try:
        # Получаем список доступных моделей
        models_response = client.list()
        available_models = []

        if isinstance(models_response, dict) and "models" in models_response:
            available_models = [m.get("name", "") for m in models_response["models"]]
        elif isinstance(models_response, list):
            available_models = [
                m.get("name", "") if isinstance(m, dict) else str(m)
                for m in models_response
            ]

        # Проверяем, есть ли модель (может быть с тегом или без)
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
                # Пытаемся загрузить модель
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


def mock_workflow(payload: Dict[str, Any], streaming: bool = True):
    """Функция workflow, которая обращается к локальной Ollama и использует модель gpt-oss:120b-cloud"""
    # Используем модель из payload, если указана, иначе используем модель по умолчанию
    default_model = "gpt-oss:120b-cloud"
    model = payload.get("model", default_model)
    messages = payload.get("messages", [])

    # Преобразуем messages в формат для Ollama
    ollama_messages = []
    for msg in messages:
        if isinstance(msg, dict):
            ollama_messages.append(
                {"role": msg.get("role", "user"), "content": msg.get("content", "")}
            )
        else:
            # Если это объект, пытаемся получить атрибуты
            ollama_messages.append(
                {
                    "role": getattr(msg, "role", "user"),
                    "content": getattr(msg, "content", str(msg)),
                }
            )

    try:
        # Получаем клиент Ollama для проверки модели
        client = get_ollama_client()

        # Проверяем и загружаем модель, если нужно
        model = ensure_model_available(client, model)

        # Используем прямой HTTP запрос вместо client.chat() из-за проблемы с 401
        # Убеждаемся, что URL правильный (без двойного /api)
        base_url = OLLAMA_HOST.rstrip("/")
        if not base_url.endswith("/api"):
            chat_url = f"{base_url}/api/chat"
        else:
            chat_url = f"{base_url}/chat"

        # Формируем payload для запроса (как в NestJS примере - простой формат)
        chat_payload = {"model": model, "messages": ollama_messages, "stream": True}

        logger.info(f"Making chat request to {chat_url}")
        logger.info(f"Base OLLAMA_HOST: {OLLAMA_HOST}")
        logger.info(f"Payload model: {model}, messages count: {len(ollama_messages)}")

        # Выполняем потоковый HTTP запрос
        # Используем stream() метод для потоковых запросов в httpx
        with httpx.Client(timeout=300.0, follow_redirects=True) as http_client:
            # Используем stream() метод для потоковой передачи
            # Используем минимальные заголовки, как в NestJS примере
            with http_client.stream(
                "POST",
                chat_url,
                json=chat_payload,
                headers={"Content-Type": "application/json"},
            ) as response:
                logger.info(f"Chat response status: {response.status_code}")
                logger.info(f"Response headers: {dict(response.headers)}")

                if response.status_code != 200:
                    # Пытаемся прочитать текст ошибки
                    error_text = f"Status {response.status_code}"
                    try:
                        # Читаем ответ построчно для потокового ответа
                        error_lines = []
                        for line in response.iter_lines():
                            error_lines.append(line)
                            if len(error_lines) >= 5:  # Читаем первые 5 строк
                                break
                        if error_lines:
                            error_text = " ".join(error_lines)[:500]
                    except Exception as e:
                        error_text = f"Status {response.status_code}, could not read error: {str(e)}"
                    logger.error(f"Chat request failed: {error_text}")
                    raise Exception(
                        f"Ollama API returned status {response.status_code}: {error_text}"
                    )

                # Если статус OK, обрабатываем потоковые ответы
                accumulated_content = ""
                eval_count = 0
                chunk = None

                # Обрабатываем потоковые ответы
                for line in response.iter_lines():
                    if not line:
                        continue

                    # Пропускаем строки, которые не являются JSON
                    if not line.strip().startswith("{"):
                        continue

                    try:
                        json_data = json.loads(line)

                        # Извлекаем данные из ответа Ollama
                        message_data = json_data.get("message", {})
                        chunk_content = (
                            message_data.get("content", "") if message_data else ""
                        )
                        done = json_data.get("done", False)
                        done_reason = json_data.get("done_reason")

                        # Если есть контент, добавляем его
                        if chunk_content:
                            accumulated_content += chunk_content
                            eval_count += 1

                            # Создаем StreamChunk из ответа Ollama
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

                        # Если это финальный чанк (даже без контента)
                        if done:
                            # Если это финальный чанк, но мы еще не отправили его, отправляем
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
                        # Пропускаем некорректные JSON строки
                        continue

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error calling Ollama: {error_msg}", exc_info=True)
        logger.error(f"OLLAMA_HOST: {OLLAMA_HOST}")
        logger.error(f"Model: {model}")
        logger.error(f"Messages count: {len(ollama_messages)}")

        # В случае ошибки возвращаем сообщение об ошибке
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
    # Сначала проверяем через прямой HTTP запрос
    http_check = {"status": "unknown", "error": None}
    try:
        # Формируем URL для прямого HTTP запроса
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

    # Теперь проверяем через библиотеку ollama
    try:
        client = get_ollama_client()
        models_response = client.list()

        # Извлекаем список моделей
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
        payload: Dict[str, Any] = await request.json()
        model_name = payload.get("model", "gpt-oss:120b-cloud")

        logger.info(f"Pulling model '{model_name}'...")
        client = get_ollama_client()

        # Загружаем модель (это может занять много времени)
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

    payload: Dict[str, Any] = await request.json()
    logger.info(f"Handling /message_stream request with payload: {payload}")

    def event_generator():
        stream = mock_workflow(payload, streaming=True)
        for chunk in stream:
            # Преобразуем в JSON и отправляем в формате SSE
            chunk_data = chunk.model_dump_json()
            yield f"data: {chunk_data}\n\n"

        # Отправляем [DONE] в конце стрима
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
    payload: Dict[str, Any] = await request.json()
    logger.info(f"Handling /generate request with payload: {payload}")

    # Имитация обработки
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


# Добавляем CORS middleware если нужно тестировать из браузера
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
