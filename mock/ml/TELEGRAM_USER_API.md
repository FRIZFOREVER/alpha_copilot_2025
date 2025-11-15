# Telegram User API Integration

Интеграция для отправки сообщений от имени пользователя через Telegram Client API (MTProto).

## Отличия от Bot API

- **Bot API**: Сообщения отправляются от имени бота (требуется создание бота через @BotFather)
- **User API**: Сообщения отправляются от вашего имени (как обычный пользователь Telegram)

## Настройка API credentials

API ID и API Hash настраиваются администратором один раз через переменные окружения:

- `TELEGRAM_API_ID` - Telegram API ID (число)
- `TELEGRAM_API_HASH` - Telegram API Hash (строка)

**Как получить API ID и API Hash:**

1. Перейдите на https://my.telegram.org
2. Войдите используя ваш номер телефона
3. Перейдите в раздел "API development tools"
4. Создайте приложение и получите credentials

**Важно:** Эти credentials общие для всех пользователей и настраиваются администратором при развертывании сервиса.

## Процесс авторизации

### Шаг 1: Начало авторизации

**POST** `/telegram/user/auth/start`

```json
{
  "user_id": "user123",
  "phone_number": "+79991234567"
}
```

**Примечание:** API ID и API Hash больше не требуются от пользователя - они берутся из конфигурации сервера.

**Response:**

```json
{
  "status": "ok",
  "status": "code_sent",
  "phone_code_hash": "abc123...",
  "message": "Code sent to Telegram"
}
```

### Шаг 2: Подтверждение кода

**POST** `/telegram/user/auth/verify`

```json
{
  "user_id": "user123",
  "phone_code": "12345"
}
```

Если включена двухфакторная аутентификация:

```json
{
  "user_id": "user123",
  "phone_code": "12345",
  "password": "your_2fa_password"
}
```

**Response:**

```json
{
  "status": "ok",
  "status": "authorized",
  "message": "Successfully authorized",
  "user": {
    "id": 987654321,
    "first_name": "Иван",
    "last_name": "Иванов",
    "username": "ivan_ivanov",
    "phone_number": "+79991234567"
  }
}
```

## Отправка сообщений

### Через endpoint

**POST** `/telegram/user/send`

```json
{
  "user_id": "user123",
  "recipient_id": "987654321", // Telegram user ID или username
  "text": "Привет от ассистента!"
}
```

**Response:**

```json
{
  "status": "ok",
  "success": true,
  "message_id": 123,
  "date": "2024-01-15T12:00:00"
}
```

### Через workflow ассистента

В payload запроса `/message_stream` добавьте:

```json
{
  "user_id": "user123",
  "send_to_telegram": true,
  "send_as_user": true,  // Отправка от имени пользователя
  "recipient_id": "987654321",  // Telegram user ID получателя
  "messages": [...]
}
```

## Проверка статуса

**GET** `/telegram/user/status/{user_id}`

**Response:**

```json
{
  "status": "ok",
  "authorized": true,
  "user_info": {
    "id": 987654321,
    "first_name": "Иван",
    "last_name": "Иванов",
    "username": "ivan_ivanov",
    "phone_number": "+79991234567"
  }
}
```

## Отключение

**POST** `/telegram/user/disconnect`

```json
{
  "user_id": "user123"
}
```

## Важные моменты

1. **Безопасность**: API ID и API Hash - это секретные данные. Не передавайте их в открытом виде.

2. **Сессии**: После авторизации создается файл сессии (`.session`), который хранит токен авторизации. Этот файл позволяет не проходить авторизацию заново при каждом запуске.

3. **Ограничения Telegram**:

   - Вы можете отправлять сообщения только тем пользователям, которые есть в ваших контактах или которым вы уже писали
   - Telegram может ограничить отправку сообщений при подозрительной активности

4. **Получение recipient_id**:
   - Если знаете username: используйте `@username`
   - Если знаете user ID: используйте числовой ID (например, `987654321`)
   - Можно использовать бота @userinfobot для получения вашего user ID

## Хранение данных

- Сессии сохраняются в `/app/data/telegram_sessions/{user_id}.session`
- Данные авторизации в `/app/data/telegram_auth.json`

## Пример использования

```python
# 1. Начало авторизации (только номер телефона!)
POST /telegram/user/auth/start
{
  "user_id": "user123",
  "phone_number": "+79991234567"
}

# 2. Получение кода в Telegram, затем подтверждение
POST /telegram/user/auth/verify
{
  "user_id": "user123",
  "phone_code": "12345"
}

# 3. Отправка сообщения
POST /telegram/user/send
{
  "user_id": "user123",
  "recipient_id": "987654321",
  "text": "Привет!"
}
```

## Настройка для администратора

Для настройки API credentials добавьте в переменные окружения или `.env` файл:

```bash
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
```

Или в `docker-compose.yml`:

```yaml
environment:
  - TELEGRAM_API_ID=12345678
  - TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
```
