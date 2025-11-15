# Telegram Integration

Интеграция с Telegram Bot API для отправки сообщений от ассистента.

## Как это работает

1. **Подключение Telegram бота**: Пользователь создает бота через @BotFather в Telegram и получает токен
2. **Сохранение токена**: Токен сохраняется через endpoint `/telegram/connect`
3. **Отправка сообщений**: Ассистент может отправлять сообщения в Telegram через endpoint `/telegram/send` или автоматически при указании параметра `send_to_telegram` в запросе

## Endpoints

### POST `/telegram/connect`

Подключает Telegram бота для пользователя.

**Request:**

```json
{
  "user_id": "user123",
  "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
  "chat_id": "123456789" // опционально
}
```

**Response:**

```json
{
  "status": "ok",
  "message": "Telegram successfully connected",
  "bot_info": {
    "id": 123456789,
    "is_bot": true,
    "first_name": "My Bot",
    "username": "my_bot"
  }
}
```

### GET `/telegram/status/{user_id}`

Получает статус подключения Telegram для пользователя.

**Response:**

```json
{
  "status": "ok",
  "connected": true,
  "bot_info": {
    "id": 123456789,
    "is_bot": true,
    "first_name": "My Bot",
    "username": "my_bot"
  },
  "has_chat_id": true
}
```

### POST `/telegram/disconnect`

Отключает Telegram для пользователя.

**Request:**

```json
{
  "user_id": "user123"
}
```

**Response:**

```json
{
  "status": "ok",
  "message": "Telegram disconnected"
}
```

### POST `/telegram/send`

Отправляет сообщение в Telegram.

**Request:**

```json
{
  "user_id": "user123",
  "text": "Привет из ассистента!",
  "chat_id": "123456789" // опционально, если сохранен
}
```

**Response:**

```json
{
  "status": "ok",
  "success": true,
  "message_id": 123
}
```

## Интеграция с ассистентом

Для автоматической отправки сообщений от ассистента в Telegram, добавьте в payload запроса `/message_stream`:

```json
{
  "user_id": "user123",
  "send_to_telegram": true,
  "messages": [...],
  "model": "gpt-oss:120b-cloud"
}
```

После завершения стрима ответа от ассистента, сообщение автоматически отправится в Telegram.

## Как получить Bot Token

1. Откройте Telegram и найдите @BotFather
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Получите токен вида `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

## Как получить Chat ID

1. Откройте чат с вашим ботом в Telegram
2. Отправьте любое сообщение боту
3. Откройте в браузере: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Найдите `"chat":{"id":123456789}` - это ваш chat_id

Или используйте бота @userinfobot для получения вашего chat_id.

## Хранение данных

Токены сохраняются в файл `/app/data/telegram_tokens.json` в формате:

```json
{
  "user123": {
    "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
    "chat_id": "123456789",
    "connected": true
  }
}
```

## Безопасность

⚠️ **Важно**: Токены ботов хранятся в открытом виде. В продакшене рекомендуется:

- Использовать шифрование для хранения токенов
- Использовать переменные окружения или секреты
- Добавить аутентификацию для endpoints
