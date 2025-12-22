# 🤖 RAG Finance Assistant

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://github.com/langchain-ai/langchain)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)

## Project Description

### Core Idea
Продвинутая RAG-система для финансового SaaS-сервиса с поддержкой:
- 🔍 Multi-sourcing (документация + оперативные данные через API)
- 💬 Chat Memory (помнит всю беседу)
- 📊 Observability (LangFuse для трейсинга и метрик)
- 🤖 LangGraph для интеллектуального роутинга

### ✨ Key Features

#### 🎯 Multi-sourcing (Dual Data Sources)
Система автоматически определяет источник данных:
- **Статическая документация** → RAG (Weaviate)
- **Оперативные данные** → Finance API (транзакции, балансы, отчеты)

```
"Как создать отчет?" → Documentation (RAG Path)
"Какой у меня баланс?" → API Call (Tools Path)
```

#### 💭 Chat Memory
Полноценная память диалогов:
- Backend: Redis с TTL 24 часа
- Frontend: localStorage с автосохранением session_id
- Контекстные ответы на основе истории беседы

```
Вы: Покажи мои расходы за месяц
Бот: За месяц ваши расходы составили 450,000 тенге...

Вы: А сколько из них на аренду?
Бот: На аренду было потрачено 150,000 тенге ✅ (помнит контекст!)
```

#### 📈 LangFuse Observability
- Полный трейсинг всех LangGraph узлов
- Метрики: latency, tokens, cost
- Dashboard: http://localhost:3000

#### 🛠️ Mock Finance API
6 готовых endpoints:
- `get_transactions` - транзакции за период
- `get_cash_flow_report` - отчет ДДС
- `get_account_balance` - балансы счетов
- `get_profit_loss_report` - отчет ОПиУ
- `get_expense_categories` - справочник категорий
- `get_counterparties` - справочник контрагентов

### Technical Stack

#### System Architecture
- **LangGraph** - Multi-step reasoning state machine
- **LangChain** - LLM orchestration
- **LangFuse** - Observability platform
- **Redis** - Chat memory & caching
- **Weaviate** - Vector database
- **FastAPI** - Backend framework
- **Azure OpenAI** - LLM provider (или Ollama для локального)

#### Components
1. **LangGraph Pipeline** - Router → RAG/Tools → Generator
2. **Memory Service** - Redis для хранения истории
3. **Mock Finance API** - Эмуляция финансовых данных
4. **LangFuse** - Self-hosted observability
5. **Frontend** - Chat UI с session management

### Dataset Concept
- **Data Type**: Markdown files with site documentation
- **Volume**: 20 documentation articles
- **Storage Format**: Documents are split into chunks (~500 tokens), each chunk is vectorized
- **Metadata**: filename, title, chunk position

### System Requirements
- Docker and Docker Compose
- 8GB RAM (minimum), 16GB RAM (recommended)
- Azure OpenAI API key (или Ollama для локального запуска)

### New in Version 1.0
- ✅ LangGraph multi-step reasoning
- ✅ Chat memory (Redis + localStorage)
- ✅ LangFuse observability
- ✅ Mock Finance API (6 endpoints)
- ✅ Intelligent routing (documentation vs operational)
- ✅ Session management на frontend

## Quick Start

### Prerequisites
1. Docker and Docker Compose
2. Azure OpenAI API key (или Ollama)

### Installation and Launch

```bash
# 1. Настроить окружение
cp .env.example .env
nano .env  # Добавить AZURE_OPENAI_API_KEY

# 2. Запустить систему
docker-compose up --build

# 3. Открыть браузер
http://localhost:8000
```

**Доступные сервисы:**
- 🌐 Frontend UI: http://localhost:8000
- 📊 LangFuse Dashboard: http://localhost:3000
- 🔍 API Docs: http://localhost:8000/docs
- 📡 Weaviate: http://localhost:8080

**On first launch:**
- Weaviate создаст схему для векторов
- Redis запустится для chat memory
- LangFuse + PostgreSQL для observability
- Backend загрузит все .md файлы из `data/`
- Документация будет проиндексирована

### Stopping the system
```bash
docker-compose down
```

### Data cleanup
For complete cleanup (including vector DB):
```bash
docker-compose down -v
```

## Usage & Testing

### 🧪 Тест Chat Memory

```bash
# Откройте http://localhost:8000

# 1. Первое сообщение
"Привет! Меня зовут Dias"

# 2. Проверьте индикатор
Должна появиться надпись: "● Chat memory active" ✅

# 3. Второе сообщение
"Как меня зовут?"

# 4. Ожидаемый результат
"Вас зовут Dias" ✅ (помнит контекст!)
```

### Example Questions

**Documentation (RAG Path):**
- "Как создать отчет в системе?"
- "Что такое ДДС?"
- "Как настроить категории расходов?"

**Operational Data (Tools Path):**
- "Какой у меня баланс?"
- "Покажи мои расходы за месяц"
- "Сколько на резервном счете?"

**Contextual Dialogue:**
```
Вы: Покажи мои расходы за месяц
Бот: За месяц ваши расходы составили 450,000 тенге...

Вы: А сколько из них на маркетинг?
Бот: На маркетинг было потрачено 80,000 тенге ✅
```

## Project Structure
```
rag-support-assistant/
├── docker-compose.yml          # Container orchestration
├── .env                        # API keys (create manually)
├── README.md                   # Documentation
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                 # FastAPI application
│   ├── rag_service.py          # RAG logic
│   └── loader.py               # Documentation loader
├── frontend/
│   └── index.html              # Web chat interface
└── data/                       # Folder for .md files (add yourself)
```

## Technical Implementation

### RAG Pipeline
1. **Indexing** (on startup):
   - Reading .md files from `data/`
   - Splitting into chunks (RecursiveCharacterTextSplitter)
   - Creating embeddings using local sentence-transformers model
   - Saving to Weaviate

2. **Query Processing**:
   - Receiving user question
   - Creating embedding for the question using local model
   - Searching for top-3 relevant chunks in Weaviate
   - Forming context
   - Generating response via local Ollama LLM
   - Returning response with sources

### API Endpoints
- `GET /` - Web interface
- `POST /chat` - Main endpoint for questions
- `GET /health` - System health check
- `GET /stats` - Database statistics

## Troubleshooting

### Issue: Containers not starting
**Solution**: Ensure Docker is running and ports 8000, 8080, 11434 are free

### Issue: Ollama model downloading slowly
**Solution**: First launch requires downloading ~2GB model. This is one-time only.

### Issue: Documentation not loading
**Solution**:
- Ensure .md files are in the `data/` folder
- Check logs: `docker-compose logs backend`

### Issue: Slow responses
**Solution**: First request may be slow (model loading). Subsequent ones are faster.

### Issue: Out of memory
**Solution**: Increase Docker memory limit to at least 8GB in Docker settings.

## Video Demonstration
[Video link to be added after recording]
