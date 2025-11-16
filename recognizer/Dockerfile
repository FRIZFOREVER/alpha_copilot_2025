FROM python:3.11-slim

WORKDIR /app

# 1. Устанавливаем ffmpeg до копирования кода, чтобы слой кешировался
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 2. Копируем только requirements и ставим пакеты — это тоже хорошо кешируется
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Копируем остальной код (только этот слой будет пересобираться чаще)
COPY recognizer.py .

CMD ["python", "recognizer.py"]
