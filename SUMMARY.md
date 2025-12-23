# RAG Finance Assistant - Полная сводка реализации

## Core Idea

Продвинутая RAG-система для финансового SaaS-сервиса с поддержкой:

- 🔍 Multi-sourcing (документация + оперативные данные через API)
- 💬 Chat Memory (помнит всю беседу)
- 📊 Observability (LangFuse для трейсинга и метрик)
- 🤖 LangGraph для интеллектуального роутинга

## 📋 Обзор проекта

Разработана с использованием:

- **LangGraph** - оркестрация multi-step reasoning
- **LangChain** - интеграция LLM и tools
- **LangFuse** - observability и трейсинг
- **Redis** - кэширование и chat memory
- **Weaviate** - векторная база данных

---

## 🎯 Реализованные бизнесс значения

### 1. Multi-sourcing (Два источника данных)

#### A. Статическая документация (RAG Path)
- Векторный поиск в Weaviate
- Chunking и эмбеддинги (all-MiniLM-L6-v2)
- Top-K retrieval с метаданными

#### B. Оперативные данные (Tool Calling Path)
- **6 Mock Finance API endpoints:**
  1. `get_transactions` - транзакции за период
  2. `get_cash_flow_report` - отчет ДДС
  3. `get_account_balance` - балансы счетов
  4. `get_profit_loss_report` - ОПиУ
  5. `get_expense_categories` - справочник категорий
  6. `get_counterparties` - справочник контрагентов

### 2. Интеллектуальный роутинг

**Router Node** автоматически определяет тип запроса:
```
"Как создать отчет?" → Documentation (RAG)
"Какой у меня баланс?" → Operational (Tools)
```

LLM анализирует вопрос и выбирает правильный путь обработки.

### 3. Chat Memory (Память диалогов)

#### Backend (Redis)
- Хранение истории в Redis с TTL 24 часа
- Автоматическое управление сессиями
- API endpoints для работы с историей

#### Frontend (localStorage)
- Автоматическое сохранение session_id
- Восстановление сессии при перезагрузке
- Кнопка "New Chat" для начала нового диалога
- Визуальный индикатор "● Chat memory active"

#### Примеры контекстных диалогов:
```
User: Покажи мои расходы за месяц
Bot: За месяц ваши расходы составили 450,000 тенге...

User: А сколько из них на аренду?
Bot: На аренду было потрачено 150,000 тенге (помнит контекст!)
```

### 4. Observability (LangFuse)

- Self-hosted LangFuse в Docker
- Автоматический трейсинг всех LangGraph узлов
- Метрики: latency, tokens, cost
- UI доступен на http://localhost:3000

**Что отслеживается:**
- Полный путь выполнения запроса
- Время работы каждого узла
- Использование токенов LLM
- Стоимость запросов

### 5. Security

- **User Context**: user_id передается во все API calls
- **Input Validation**: проверка пустых сообщений
- **Demo Mode**: hardcoded user_id для тестирования
- **Session Isolation**: каждый пользователь имеет свою историю

---

## 🏗️ Архитектура системы

### LangGraph Pipeline

```
┌─────────────────────────────────────────────────────┐
│                    User Query                       │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │    Router Node        │
         │  (LLM Classification) │
         └───────┬───────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌───────────────┐   ┌──────────────┐
│   RAG Node    │   │  Tools Node  │
│  (Weaviate)   │   │  (API Calls) │
└───────┬───────┘   └──────┬───────┘
        │                  │
        └────────┬─────────┘
                 │
                 ▼
      ┌──────────────────┐
      │  Generator Node  │
      │  (Final Answer)  │
      └──────────────────┘
                 │
                 ▼
      ┌──────────────────┐
      │  Save to Redis   │
      │  (Chat Memory)   │
      └──────────────────┘
                 │
                 ▼
      ┌──────────────────┐
      │  LangFuse Trace  │
      │  (Observability) │
      └──────────────────┘
```

### Компоненты системы

```
┌─────────────────────────────────────────────────┐
│              Docker Compose Stack               │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐  ┌──────────────┐           │
│  │   Weaviate   │  │    Redis     │           │
│  │ Vector Store │  │  Chat Memory │           │
│  └──────────────┘  └──────────────┘           │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐           │
│  │  PostgreSQL  │  │   LangFuse   │           │
│  │ LangFuse DB  │  │   UI:3000    │           │
│  └──────────────┘  └──────────────┘           │
│                                                 │
│  ┌─────────────────────────────────────────┐  │
│  │         FastAPI Backend :8000           │  │
│  │  ┌───────────────────────────────────┐  │  │
│  │  │       LangGraph Pipeline          │  │  │
│  │  │  - Router                         │  │  │
│  │  │  - RAG                            │  │  │
│  │  │  - Tools                          │  │  │
│  │  │  - Generator                      │  │  │
│  │  └───────────────────────────────────┘  │  │
│  │                                          │  │
│  │  Services:                               │  │
│  │  - Memory Service (Redis)                │  │
│  │  - LangFuse Client                       │  │
│  │  - Mock Finance API                      │  │
│  └─────────────────────────────────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 📁 Структура проекта

```
rag-support-assistant/
├── backend/
│   ├── agents/                    # LangGraph компоненты
│   │   ├── graph.py              # ⭐ Главный граф
│   │   ├── state.py              # AgentState schema
│   │   └── nodes/
│   │       ├── router.py         # Классификация запросов
│   │       ├── rag.py            # Векторный поиск
│   │       ├── tools.py          # Tool calling
│   │       └── generator.py      # Генерация ответов
│   │
│   ├── tools/                     # API и tools
│   │   ├── mock_finance_api.py   # ⭐ Mock финансовые API
│   │   └── tool_definitions.py   # LangChain tools
│   │
│   ├── services/                  # Сервисы
│   │   └── memory_service.py     # ⭐ Redis chat memory
│   │
│   ├── config/
│   │   └── settings.py           # ⭐ Pydantic настройки
│   │
│   ├── observability/
│   │   └── langfuse_client.py    # LangFuse integration
│   │
│   ├── middleware/
│   │   └── auth.py               # User context (future)
│   │
│   ├── main.py                   # ⭐ FastAPI endpoints
│   ├── rag_service.py            # RAG logic
│   ├── llm_client.py             # LLM initialization
│   ├── db_client.py              # Weaviate connection
│   ├── loader.py                 # Data indexing
│   └── requirements.txt          # ⭐ Dependencies
│
├── frontend/
│   └── index.html                # ⭐ UI с chat memory
│
├── data/                         # Документация для RAG
│   └── *.md
│
├── docker-compose.yml            # ⭐ Инфраструктура
├── .env.example                  # ⭐ Конфигурация
│
└── Документация:
    ├── README_IMPLEMENTATION.md  # Основная документация
    ├── CHAT_MEMORY_GUIDE.md      # Руководство по памяти
    ├── FRONTEND_MEMORY_TEST.md   # Тестирование frontend
    └── SUMMARY.md                # Этот файл
```

---

## 🔧 Технологический стек

### Backend
- **Python 3.11+**
- **FastAPI** - Web framework
- **LangGraph** - State machine для агентов
- **LangChain** - LLM orchestration
- **LangFuse** - Observability
- **Redis** - Кэширование и chat memory
- **Weaviate** - Векторная БД
- **Sentence Transformers** - Локальные эмбеддинги
- **Pydantic** - Валидация и настройки

### Frontend
- **Vanilla JavaScript** - Без фреймворков
- **Marked.js** - Markdown рендеринг
- **localStorage API** - Сохранение session_id

### Infrastructure
- **Docker Compose** - Оркестрация сервисов
- **PostgreSQL 15** - LangFuse database
- **Azure OpenAI** - LLM provider

---

## 🚀 Быстрый старт

### 1. Настройка окружения

```bash
# Скопировать конфигурацию
cp .env.example .env

# Отредактировать .env
nano .env
# Добавить: AZURE_OPENAI_API_KEY=your_key_here
```

### 2. Запуск системы

```bash
# Запустить все сервисы
docker-compose up --build

# Сервисы запустятся на портах:
# - Backend API: http://localhost:8000
# - LangFuse UI: http://localhost:3000
# - Weaviate: http://localhost:8080
# - Redis: localhost:6379
```

### 3. Настройка LangFuse (опционально)

```bash
# 1. Открыть http://localhost:3000
# 2. Создать аккаунт и проект
# 3. Скопировать Public Key и Secret Key
# 4. Добавить в .env:
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...

# 5. Перезапустить backend
docker-compose restart backend
```

### 4. Тестирование

**Ручное тестирование**:

```bash
# Открыть UI
http://localhost:8000

# Тест памяти
1. "Привет! Меня зовут Dias"
2. "Как меня зовут?" → "Вас зовут Dias" ✅

# Тест роутинга
1. "Какой у меня баланс?" → Tools Path
2. "Как восстановить пароль?" → RAG Path
```

**С помощью скрипа**:

```bash
# Запуск теста
python test_cache_quick.py
# В просмотр лога
```

---

## 📈 Метрики и мониторинг

Открываем LangFuse UI http://localhost:3000

Вход:

- Login: admin@example.com
- Password: supersecret

### LangFuse Dashboard

1. **Traces** - полный путь запроса
2. **Latency** - время выполнения
3. **Tokens** - использование токенов
4. **Cost** - стоимость запросов
5. **Success Rate** - процент успешных запросов

![langfuse-metrics.png](images/screenshot-langfuse-metrics.png)

В метриках видно как кэширование помогает:

- Уменьшить latency. Скрость +, UX +
- Уменшить сost. Экономика +

---

## 📊 API Endpoints

### Chat Endpoints

#### POST /chat

Основной endpoint для диалога

**Request:**

```json
{
  "message": "Какой у меня баланс?",
  "session_id": "session_user_123"  // optional
}
```

**Response:**

```json
{
  "answer": "Ваш общий баланс составляет 2,100,000 тенге...",
  "sources": [
    {"title": "API: get_account_balance", "filename": "Operational Data"}
  ],
  "query_type": "operational",
  "processing_time_ms": 1523.45,
  "session_id": "session_user_123"
}
```

#### GET /chat/history/{session_id}

Получить историю чата

```bash
curl http://localhost:8000/chat/history/session_user_123?limit=20
```

#### DELETE /chat/history/{session_id}

Очистить историю

```bash
curl -X DELETE http://localhost:8000/chat/history/session_user_123
```

### System Endpoints

#### GET /health

Проверка состояния

#### GET /stats

Статистика системы

---

## 💡 Ключевые особенности

### 1. Автоматический роутинг

LLM сам определяет куда направить запрос:

- **Documentation questions** → RAG (Weaviate)
- **Operational questions** → Tools (API calls)

### 2. Контекстная память

Система помнит всю беседу:

```
User: Покажи расходы за месяц
Bot: [данные о расходах]

User: А сколько из них на маркетинг?
Bot: [анализирует расходы за месяц - помнит контекст!]
```

### 3. Персистентность

- История сохраняется в Redis (24 часа)
- Session_id в localStorage браузера
- Сессия восстанавливается при перезагрузке

### 4. Observability

Полный трейсинг в LangFuse:

- Какой путь выбран (RAG/Tools)
- Сколько времени на каждый узел
- Сколько токенов использовано
- Стоимость запроса

### 5. Security

- User context в каждом API call
- Session isolation
- TTL для автоматической очистки данных

---

## 🎨 Frontend Features

### UI Компоненты

- **Chat Interface** - современный дизайн
- **Markdown Support** - форматированные ответы
- **Typing Indicator** - индикация обработки
- **Sources Display** - показ источников данных
- **Session Indicator** - "● Chat memory active"
- **New Chat Button** - быстрый старт нового диалога

### UX Улучшения

- Автосохранение сессии
- Восстановление при перезагрузке
- Подсказки с примерами вопросов
- Smooth scrolling к новым сообщениям

---

## 🔮 Roadmap (Следующие шаги)

### Фаза 2: Advanced Caching
- [ ] Semantic caching (векторный поиск похожих вопросов)
- [ ] Redis для кэширования API results
- [ ] Prompt caching для Azure OpenAI
- [ ] Cache hit rate metrics

### Фаза 3: Accuracy Improvements
- [ ] Query rewriting node (улучшение вопросов)
- [ ] FlashRank reranking для документов
- [ ] Hypothetical document embeddings
- [ ] Security guardrails (input/output validation)

### Фаза 4: Production Features
- [ ] JWT authentication (реальная авторизация)
- [ ] Real Finance API integration (замена mock)
- [ ] Rate limiting
- [ ] Monitoring & alerting (Prometheus + Grafana)
- [ ] A/B testing для экспериментов

### Фаза 5: Advanced Features
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Document upload и индексация
- [ ] Scheduled reports
- [ ] Export chat history

---

## 📚 Документация

### Основные документы
1. **README_IMPLEMENTATION.md** - Полное руководство по архитектуре
2. **CHAT_MEMORY_GUIDE.md** - Работа с памятью диалогов
3. **FRONTEND_MEMORY_TEST.md** - Тестирование frontend
4. **SUMMARY.md** - Этот документ

### API Documentation
- OpenAPI спецификация: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

---

