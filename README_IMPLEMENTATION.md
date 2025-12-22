# RAG Finance Assistant - Implementation Guide

## Обзор архитектуры

Система построена на **LangGraph + LangChain** с интеграцией LangFuse для observability.

### Компоненты системы

```
┌──────────────┐
│   User Query │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────┐
│            FastAPI Backend               │
│  ┌────────────────────────────────────┐  │
│  │        LangGraph Pipeline          │  │
│  │                                    │  │
│  │  1. Router Node                   │  │
│  │     └─> Documentation/Operational │  │
│  │                                    │  │
│  │  2a. RAG Node          2b. Tools  │  │
│  │      └─> Weaviate          └─> API│  │
│  │                                    │  │
│  │  3. Generator Node                │  │
│  │     └─> Final Answer              │  │
│  └────────────────────────────────────┘  │
│                                          │
│  LangFuse Tracing ──────────────────────┐│
└──────────────────────────────────────────┘│
                                           ││
┌──────────────────────────────────────────┘│
│ Infrastructure:                           │
│ • Weaviate (vector DB)                   │
│ • Redis (caching)                        │
│ • LangFuse (observability)               │
│ • PostgreSQL (LangFuse DB)               │
└──────────────────────────────────────────┘
```

## Структура проекта

```
backend/
├── agents/               # LangGraph компоненты
│   ├── graph.py         # Главный граф (state machine)
│   ├── state.py         # AgentState schema
│   └── nodes/           # Узлы графа
│       ├── router.py    # Классификация запросов
│       ├── rag.py       # Векторный поиск
│       ├── tools.py     # Tool calling для API
│       └── generator.py # Генерация ответов
│
├── tools/               # API и tools
│   ├── mock_finance_api.py    # Mock финансовые API
│   └── tool_definitions.py    # LangChain tools
│
├── services/            # Сервисы (будущее: cache, reranker)
├── config/
│   └── settings.py      # Конфигурация (Pydantic)
│
├── observability/
│   └── langfuse_client.py     # LangFuse integration
│
└── main.py              # FastAPI endpoints
```

## Запуск системы

### 1. Настройка окружения

```bash
# Скопируйте .env.example в .env
cp .env.example .env

# Отредактируйте .env и добавьте ваш API ключ
nano .env
```

### 2. Запуск через Docker Compose

```bash
docker-compose up --build
```

Сервисы будут доступны по адресам:
- **Backend API**: http://localhost:8000
- **LangFuse UI**: http://localhost:3000
- **Weaviate**: http://localhost:8080
- **Redis**: localhost:6379

### 3. Настройка LangFuse (опционально)

1. Откройте http://localhost:3000
2. Создайте аккаунт (первый пользователь = admin)
3. Создайте новый проект
4. Скопируйте Public Key и Secret Key
5. Добавьте их в `.env`:

```bash
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
```

6. Перезапустите контейнер:

```bash
docker-compose restart backend
```

## API Endpoints

### POST /chat
Основной endpoint для чата

**Request:**
```json
{
  "message": "Какой у меня баланс?",
  "user_id": "user_123"  // optional
}
```

**Response:**
```json
{
  "answer": "Ваш общий баланс составляет...",
  "sources": [
    {"title": "API: get_account_balance", "filename": "Operational Data"}
  ],
  "query_type": "operational",
  "processing_time_ms": 1523.45
}
```

### GET /health
Проверка состояния системы

### GET /stats
Статистика системы (количество документов, конфигурация)

## Примеры использования

### 1. Вопрос о документации (RAG path)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Как работает система отчетов?"
  }'
```

**Путь выполнения:** Router → RAG → Generator

### 2. Вопрос об операционных данных (Tools path)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Покажи мои расходы за месяц"
  }'
```

**Путь выполнения:** Router → Tools → Generator

Система автоматически вызовет `get_transactions(period="month", transaction_type="expense")`

### 3. Комбинированные запросы

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Какой у меня баланс и как его посмотреть в системе?"
  }'
```

## Доступные финансовые API (Mock)

1. **get_transactions** - получить транзакции за период
   - `period`: "week", "month", "quarter", "year"
   - `transaction_type`: "income", "expense", или None

2. **get_cash_flow_report** - отчет ДДС
   - `period`: "month", "quarter", "year"

3. **get_account_balance** - баланс счетов
   - `account_id`: ID счета или None для всех

4. **get_profit_loss_report** - отчет ОПиУ
   - `period`: "month", "quarter", "year"

5. **get_expense_categories** - справочник статей расходов/доходов

6. **get_counterparties** - справочник контрагентов

## Observability с LangFuse

### Что отслеживается

- **Traces**: полный путь выполнения запроса через все узлы
- **Spans**: каждый узел LangGraph (router, rag, tools, generator)
- **Metrics**:
  - Latency каждого узла
  - Токены использованные LLM
  - Cost estimation
  - Cache hit rates (планируется)

### Просмотр трейсов

1. Откройте LangFuse UI: http://localhost:3000
2. Перейдите в ваш проект
3. Раздел "Traces" покажет все запросы
4. Кликните на trace для детального просмотра

### Метрики и дашборды

LangFuse автоматически собирает:
- Среднее время ответа
- P95/P99 latency
- Количество токенов
- Стоимость запросов (если настроены цены)

## Следующие шаги развития

### Фаза 2: Caching (Redis)

- [ ] Semantic caching для похожих вопросов
- [ ] Кэширование результатов API (TTL по типу данных)
- [ ] Prompt caching для Azure OpenAI
- [ ] Метрики cache hit rate в LangFuse

### Фаза 3: Accuracy Improvements

- [ ] Query rewriting node (улучшение формулировки)
- [ ] Reranking с FlashRank
- [ ] Hypothetical document embeddings
- [ ] Security guardrails (input/output validation)

### Фаза 4: Security

- [ ] Input guardrails (проверка домена вопроса)
- [ ] Output guardrails (защита от утечки данных)
- [ ] JWT authentication вместо hardcoded user_id
- [ ] Row-level security для доступа к данным

## Конфигурация (settings.py)

Все настройки в `config/settings.py`:

```python
from config.settings import settings

# RAG settings
settings.rag.top_k  # сколько документов извлекать
settings.rag.rerank_enabled  # включить reranking
settings.rag.query_rewriting_enabled  # включить query rewriting

# Redis cache TTL
settings.redis.ttl_transactions  # 60 sec
settings.redis.ttl_reports  # 300 sec
settings.redis.ttl_dictionaries  # 3600 sec

# Demo user
settings.demo_user_id  # "user_123"
```

## Troubleshooting

### LangFuse не работает
```bash
# Проверьте логи
docker-compose logs langfuse

# Проверьте подключение к PostgreSQL
docker-compose logs langfuse-db
```

### Weaviate пустая база
```bash
# Перезапустите loader
docker-compose restart backend

# Или вручную
docker-compose exec backend python loader.py
```

### Ошибки импорта
```bash
# Пересоберите контейнер
docker-compose build backend
docker-compose up backend
```

## Контакты

Для вопросов и предложений создавайте issues в репозитории.
