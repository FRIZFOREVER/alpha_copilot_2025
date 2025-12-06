from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
import time
import uuid
from datetime import datetime
import random

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mock ML Service")

# Состояние приложения
app.state.models_ready = asyncio.Event()
app.state.models_ready.set()  # Модели всегда готовы в моке

class StreamChunk(BaseModel):
    id: str
    choices: List[Dict[str, Any]]
    created: int
    model: str
    object: str = "chat.completion.chunk"
    service_tier: Optional[str] = None
    system_fingerprint: Optional[str] = ""
    usage: Optional[Dict[str, Any]] = None
    provider: str = "SiliconFlow"

def generate_stream_id() -> str:
    """Генерация ID для стрима"""
    timestamp = int(time.time())
    random_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=20))
    return f"gen-{timestamp}-{random_id}"

def create_initial_chunk(stream_id: str, model: str) -> Dict[str, Any]:
    """Создание первого чанка"""
    return {
        "id": stream_id,
        "choices": [
            {
                "delta": {
                    "content": "",
                    "function_call": None,
                    "refusal": None,
                    "role": "assistant",
                    "tool_calls": None,
                    "reasoning": None,
                    "reasoning_details": []
                },
                "finish_reason": None,
                "index": 0,
                "logprobs": None,
                    "native_finish_reason": None
            }
        ],
        "created": int(time.time()),
        "model": model,
        "provider": "SiliconFlow"
    }

def create_reasoning_chunk(stream_id: str, model: str, reasoning_text: str) -> Dict[str, Any]:
    """Создание чанка с reasoning"""
    return {
        "id": stream_id,
        "choices": [
            {
                "delta": {
                    "content": "",
                    "function_call": None,
                    "refusal": None,
                    "role": "assistant",
                    "tool_calls": None,
                    "reasoning": reasoning_text,
                    "reasoning_details": [
                        {
                            "type": "reasoning.text",
                            "text": reasoning_text,
                            "format": "unknown",
                            "index": 0
                        }
                    ]
                },
                "finish_reason": None,
                "index": 0,
                "logprobs": None,
                "native_finish_reason": None
            }
        ],
        "created": int(time.time()),
        "model": model,
        "provider": "SiliconFlow"
    }

def create_content_chunk(stream_id: str, model: str, content: str) -> Dict[str, Any]:
    """Создание чанка с контентом"""
    return {
        "id": stream_id,
        "choices": [
            {
                "delta": {
                    "content": content,
                    "function_call": None,
                    "refusal": None,
                    "role": "assistant",
                    "tool_calls": None,
                    "reasoning": None,
                    "reasoning_details": []
                },
                "finish_reason": None,
                "index": 0,
                "logprobs": None,
                "native_finish_reason": None
            }
        ],
        "created": int(time.time()),
        "model": model,
        "provider": "SiliconFlow"
    }

def create_final_chunk(stream_id: str, model: str, prompt_tokens: int, completion_tokens: int, reasoning_tokens: int = 0) -> Dict[str, Any]:
    """Создание финального чанка с usage статистикой"""
    total_tokens = prompt_tokens + completion_tokens
    
    # Расчет стоимости (примерные значения)
    cost = 0.0005  # Примерная стоимость
    
    return {
        "id": stream_id,
        "choices": [
            {
                "delta": {
                    "content": "",
                    "function_call": None,
                    "refusal": None,
                    "role": "assistant",
                    "tool_calls": None
                },
                "finish_reason": None,
                "index": 0,
                "logprobs": None,
                "native_finish_reason": None
            }
        ],
        "created": int(time.time()),
        "model": model,
        "system_fingerprint": None,
        "usage": {
            "completion_tokens": completion_tokens,
            "prompt_tokens": prompt_tokens,
            "total_tokens": total_tokens,
            "completion_tokens_details": {
                "accepted_prediction_tokens": None,
                "audio_tokens": None,
                "reasoning_tokens": reasoning_tokens,
                "rejected_prediction_tokens": None,
                "image_tokens": 0
            },
            "prompt_tokens_details": {
                "audio_tokens": 0,
                "cached_tokens": 0,
                "video_tokens": 0
            },
            "cost": cost,
            "is_byok": False,
            "cost_details": {
                "upstream_inference_cost": None,
                "upstream_inference_prompt_cost": 0.00006,
                "upstream_inference_completions_cost": 0.00044
            }
        },
        "provider": "SiliconFlow"
    }

def mock_streaming_response(payload: Dict[str, Any]):
    """Генерация потокового ответа в формате SiliconFlow/Qwen"""
    model = payload.get("model", "qwen/qwen3-235b-a22b-thinking-2507")
    messages = payload.get("messages", [])
    stream_id = generate_stream_id()
    
    # Полный текст ответа
    full_response = "Это моковый ответ от ML сервиса для тестирования потоковой передачи. Эта конфигурация используется для тестирования бэкенда, фронтенда и деплоя."
    
    # 1. Первый чанк
    yield create_initial_chunk(stream_id, model)
    time.sleep(0.05)
    
    # 2. Reasoning чанки (разбиваем на части)
    reasoning_parts = ["Рассуждаю", " над", " вопросом", " пользователя", " и", " генерирую", " ответ..."]
    for part in reasoning_parts:
        yield create_reasoning_chunk(stream_id, model, part)
        time.sleep(0.03)
    
    # 3. Контент чанки (по словам)
    words = full_response.split()
    for word in words:
        content = word + (" " if word != words[-1] else "")
        # Иногда добавляем знаки препинания как отдельные чанки
        if word.endswith(('.', ',', '!', '?')):
            yield create_content_chunk(stream_id, model, word[:-1])
            time.sleep(0.02)
            yield create_content_chunk(stream_id, model, word[-1] + " ")
            time.sleep(0.02)
        else:
            yield create_content_chunk(stream_id, model, content)
            time.sleep(0.03)
    
    # 4. Финальный чанк с usage
    prompt_tokens = sum(len(str(msg)) // 4 for msg in messages) if messages else 462
    completion_tokens = len(full_response) // 2
    reasoning_tokens = sum(len(part) // 2 for part in reasoning_parts)
    
    yield create_final_chunk(stream_id, model, prompt_tokens, completion_tokens, reasoning_tokens)

@app.get("/")
async def root():
    return {"message": "Mock ML Service is running (SiliconFlow/Qwen format)"}

@app.get("/health")
async def health():
    return {"status": "healthy", "models_ready": app.state.models_ready.is_set()}

@app.get("/ping")
async def ping():
    """Эндпоинт для проверки доступности сервиса"""
    return {"status": "ok", "message": "pong"}

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """Эндпоинт совместимый с OpenAI API format"""
    
    if not app.state.models_ready.is_set():
        raise HTTPException(status_code=503, detail="Models are still initialising")
    
    payload: Dict[str, Any] = await request.json()
    logger.info(f"Handling /v1/chat/completions request with payload keys: {list(payload.keys())}")
    
    stream = payload.get("stream", False)
    
    if stream:
        def event_generator():
            for chunk in mock_streaming_response(payload):
                chunk_data = json.dumps(chunk, ensure_ascii=False)
                yield f"data: {chunk_data}\n\n"
            
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            event_generator(), 
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )
    else:
        # Не-потоковый ответ
        await asyncio.sleep(0.5)
        
        model = payload.get("model", "qwen/qwen3-235b-a22b-thinking-2507")
        messages = payload.get("messages", [])
        full_response = "Это моковый ответ от ML сервиса для не-потокового запроса."
        
        return {
            "id": generate_stream_id(),
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": full_response,
                        "reasoning": "Рассуждаю над вопросом пользователя и генерирую ответ..."
                    },
                    "finish_reason": "stop",
                    "logprobs": None
                }
            ],
            "usage": {
                "prompt_tokens": sum(len(str(msg)) // 4 for msg in messages) if messages else 100,
                "completion_tokens": len(full_response) // 2,
                "total_tokens": 150,
                "completion_tokens_details": {
                    "reasoning_tokens": 50
                }
            },
            "provider": "SiliconFlow"
        }

# Сохранение старого endpoint для обратной совместимости
@app.post("/message_stream")
async def message_stream(request: Request):
    models_ready = app.state.models_ready
    
    if not models_ready.is_set():
        raise HTTPException(status_code=503, detail="Models are still initialising")
    
    payload: Dict[str, Any] = await request.json()
    logger.info(f"Handling /message_stream request with payload: {payload}")
    
    def event_generator():
        for chunk in mock_streaming_response(payload):
            chunk_data = json.dumps(chunk, ensure_ascii=False)
            yield f"data: {chunk_data}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )

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