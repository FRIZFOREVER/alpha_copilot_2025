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

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mock ML Service")

# Состояние приложения
app.state.models_ready = asyncio.Event()
app.state.models_ready.set()  # Модели всегда готовы в моке

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
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow().isoformat() + "Z"
        if 'message' not in data:
            data['message'] = Message()
        super().__init__(**data)

def mock_workflow(payload: Dict[str, Any], streaming: bool = True):
    """Моковая функция workflow, которая генерирует поток данных посимвольно"""
    model = payload.get("model", "qwen3:0.6b")
    messages = payload.get("messages", [])
    
    # Полный текст ответа
    full_response = "Это моковый ответ от ML сервиса для тестирования потоковой передачи."
    
    # Генерируем чанки по одному символу
    for i, char in enumerate(full_response):
        # Каждое сообщение содержит только текущий символ
        chunk = StreamChunk(
            model=model,
            done=False,
            message=Message(
                role="assistant",
                content=char,  # Только один символ!
                thinking=f"Генерация символа {i+1} из {len(full_response)}" if i % 10 == 0 else None
            ),
            eval_count=i+1,
            prompt_eval_count=len(messages) if messages else 1,
            total_duration=int((i + 1) * 100),
            eval_duration=int((i + 1) * 80)
        )
        yield chunk
        time.sleep(0.02)  # Задержка 0.02 секунды между символами
    
    # Финальный чанк с полным текстом (или можно оставить пустым)
    final_chunk = StreamChunk(
        model=model,
        done=True,
        done_reason="stop",
        message=Message(
            role="assistant",
            content=""  # Пустой контент в финальном чанке, так как все символы уже отправлены
        ),
        eval_count=len(full_response),
        prompt_eval_count=len(messages) if messages else 1,
        total_duration=int(len(full_response) * 100),
        eval_duration=int(len(full_response) * 80)
    )
    yield final_chunk

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
            "Access-Control-Allow-Headers": "Content-Type"
        }
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
            "tool_calls": None
        },
        "done": True,
        "done_reason": "stop",
        "total_duration": 500000000,
        "load_duration": 100000000,
        "prompt_eval_count": 1,
        "prompt_eval_duration": 100000000,
        "eval_count": 10,
        "eval_duration": 300000000
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