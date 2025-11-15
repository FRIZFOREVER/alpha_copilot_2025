FROM python:3.11-slim

# Устанавливаем curl для healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY app.py .
COPY telegram_service.py .
COPY telegram_user_service.py .
COPY email_service.py .

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]