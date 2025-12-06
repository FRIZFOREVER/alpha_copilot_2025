FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY config.py .
COPY telegram_user_service.py .
COPY todoist_service.py .

COPY models/ ./models/
COPY handlers/ ./handlers/

EXPOSE 4444

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "4444"]
