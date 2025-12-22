# Chat Memory Guide

## Обзор

Система теперь поддерживает **полноценную память диалогов** через Redis. Чат помнит предыдущие сообщения и может отвечать в контексте беседы.

## Как это работает

### Архитектура

```
User → FastAPI → LangGraph Pipeline
                      ↓
                  Redis Memory
                      ↓
        [Chat History (last 10 msgs)]
                      ↓
                  Generator → LLM
                      ↓
                  Response
                      ↓
              Save to Redis Memory
```

### Компоненты

1. **MemoryService** (`services/memory_service.py`)
   - Управляет хранением истории в Redis
   - TTL: 24 часа
   - Хранит: role, content, timestamp, metadata

2. **AgentState** - добавлены поля:
   - `session_id` - идентификатор сессии
   - `chat_history` - последние 10 сообщений

3. **Generator Node** - использует историю для контекстных ответов

## API Endpoints

### POST /chat - Отправить сообщение

**С автоматическим session_id:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Привет, какой у меня баланс?"
  }'
```

Ответ:
```json
{
  "answer": "Ваш общий баланс...",
  "sources": [...],
  "session_id": "session_user_123",
  "processing_time_ms": 1234.56
}
```

**С явным session_id:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "А за прошлый месяц?",
    "session_id": "session_user_123"
  }'
```

Теперь система помнит предыдущий вопрос о балансе!

### GET /chat/history/{session_id} - Получить историю

```bash
curl http://localhost:8000/chat/history/session_user_123?limit=20
```

Ответ:
```json
{
  "session_id": "session_user_123",
  "messages": [
    {
      "role": "user",
      "content": "Привет, какой у меня баланс?",
      "timestamp": "2025-12-22T10:30:00",
      "metadata": {}
    },
    {
      "role": "assistant",
      "content": "Ваш общий баланс составляет...",
      "timestamp": "2025-12-22T10:30:02",
      "metadata": {
        "query_type": "operational",
        "sources": [...]
      }
    }
  ],
  "stats": {
    "message_count": 4,
    "ttl_seconds": 86340
  }
}
```

### DELETE /chat/history/{session_id} - Очистить историю

```bash
curl -X DELETE http://localhost:8000/chat/history/session_user_123
```

Ответ:
```json
{
  "message": "History cleared for session session_user_123"
}
```

## Примеры использования

### Пример 1: Контекстный диалог

**Запрос 1:**
```json
{
  "message": "Покажи мои расходы за месяц"
}
```

**Ответ 1:**
```json
{
  "answer": "За последний месяц ваши расходы составили 450,000 тенге...",
  "session_id": "session_user_123"
}
```

**Запрос 2 (в той же сессии):**
```json
{
  "message": "А сколько из них на аренду?",
  "session_id": "session_user_123"
}
```

**Ответ 2:**
```json
{
  "answer": "На аренду было потрачено 150,000 тенге из общих расходов за месяц."
}
```

Система понимает контекст ("из них" = из расходов за месяц)!

### Пример 2: Множественные сессии

```bash
# Сессия пользователя 1
curl -X POST http://localhost:8000/chat \
  -d '{"message": "Мой баланс?", "session_id": "session_alice"}'

# Сессия пользователя 2
curl -X POST http://localhost:8000/chat \
  -d '{"message": "Мой баланс?", "session_id": "session_bob"}'
```

Каждый пользователь имеет свою независимую историю!

## Интеграция с Frontend

### JavaScript пример

```javascript
class ChatClient {
  constructor() {
    this.sessionId = null;
  }

  async sendMessage(message) {
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        message: message,
        session_id: this.sessionId  // null при первом запросе
      })
    });

    const data = await response.json();

    // Сохранить session_id для последующих запросов
    this.sessionId = data.session_id;

    return data;
  }

  async clearHistory() {
    if (!this.sessionId) return;

    await fetch(`http://localhost:8000/chat/history/${this.sessionId}`, {
      method: 'DELETE'
    });

    this.sessionId = null;
  }

  async getHistory() {
    if (!this.sessionId) return [];

    const response = await fetch(
      `http://localhost:8000/chat/history/${this.sessionId}?limit=50`
    );
    return await response.json();
  }
}

// Использование
const chat = new ChatClient();

// Первое сообщение
await chat.sendMessage("Привет! Какой у меня баланс?");

// Второе сообщение - помнит контекст
await chat.sendMessage("А сколько на счете в долларах?");

// Получить историю
const history = await chat.getHistory();
console.log(history);

// Очистить и начать новую сессию
await chat.clearHistory();
```

## Настройки

### В `services/memory_service.py`

```python
# TTL сессии (по умолчанию 24 часа)
self.redis_client.expire(key, 86400)

# Количество сообщений для контекста (в generator.py)
messages.extend(chat_history[-10:])  # Последние 10 сообщений
```

### Изменить TTL в Redis

```python
# В memory_service.py, метод add_message()
# Изменить с 86400 (24 часа) на нужное значение
self.redis_client.expire(key, 3600)  # 1 час
```

### Изменить количество сообщений в контексте

```python
# В generator.py
# Изменить с 10 на нужное количество
messages.extend(chat_history[-20:])  # 20 сообщений
```

## Проверка работы

### 1. Запустите систему

```bash
docker-compose up --build
```

### 2. Тестовый диалог

```bash
# Сообщение 1
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет! Меня зовут Dias"}'

# Запомните session_id из ответа, например: "session_user_123"

# Сообщение 2 - проверка памяти
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Как меня зовут?", "session_id": "session_user_123"}'
```

Если система ответит "Вас зовут Dias" - память работает! ✅

### 3. Проверка истории в Redis

```bash
# Подключитесь к Redis
docker-compose exec redis redis-cli

# Просмотрите ключи
KEYS chat_history:*

# Просмотрите содержимое
LRANGE chat_history:session_user_123 0 -1
```

## Troubleshooting

### Память не работает

**Проверка 1: Redis запущен?**
```bash
docker-compose ps redis
```

**Проверка 2: Логи**
```bash
docker-compose logs backend | grep "Redis memory service"
```

Должны увидеть: `✓ Redis memory service initialized`

**Проверка 3: Ручное тестирование Redis**
```bash
docker-compose exec redis redis-cli ping
# Ответ: PONG
```

### Session_id не сохраняется на фронтенде

Убедитесь, что frontend сохраняет `session_id` из ответа и передает его в следующих запросах.

### История слишком короткая

Увеличьте лимит в `generator.py`:
```python
messages.extend(chat_history[-20:])  # вместо -10:
```

## Best Practices

1. **Одна сессия = один пользователь**
   - Не используйте один session_id для разных пользователей

2. **Очистка истории**
   - Предоставьте кнопку "Новый чат" на фронтенде
   - Вызывайте DELETE endpoint для очистки

3. **Мобильные приложения**
   - Сохраняйте session_id в localStorage/AsyncStorage
   - Восстанавливайте сессию при перезапуске приложения

4. **Privacy**
   - История автоматически удаляется через 24 часа
   - Для sensitive данных - уменьшите TTL

## Метрики

LangFuse автоматически отслеживает:
- Количество сообщений в истории
- Влияние истории на latency
- Использование токенов (с историей vs без)

Проверьте в LangFuse UI: http://localhost:3000
