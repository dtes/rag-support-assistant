# RAG Quality Improvements

Этот документ описывает улучшения качества RAG системы, включая semantic chunking, re-ranking и автоматическую оценку качества.

## Что было добавлено

### 1. Semantic Chunking (Llama Index SentenceSplitter)

Вместо простого разбиения по размеру, теперь используется семантическое разбиение текста с учетом структуры предложений и параграфов.

**Конфигурация:**
```env
SEMANTIC_CHUNKING_ENABLED=true  # Включить semantic chunking
CHUNK_SIZE=500                  # Размер чанка
CHUNK_OVERLAP=50                # Перекрытие чанков
```

**Переключение на старый метод (для отладки):**
```env
SEMANTIC_CHUNKING_ENABLED=false
```

**Файлы:**
- `backend/loader.py` - логика chunking
- `backend/config/settings.py` - ChunkingSettings

### 2. Re-ranking документов (FlashRank)

Двухэтапный поиск:
1. Извлечение большего количества документов (15) из векторной БД
2. Re-ranking с выбором лучших по смыслу (7)

**Конфигурация:**
```env
RERANK_ENABLED=true        # Включить re-ranking
RAG_INITIAL_TOP_K=15       # Сколько документов извлечь изначально
RAG_FINAL_TOP_K=7          # Сколько оставить после re-ranking
```

**Файлы:**
- `backend/services/reranker_service.py` - RerankerService
- `backend/rag_service.py` - интеграция re-ranking
- `backend/agents/nodes/rag.py` - использование в RAG pipeline

**Как работает:**
1. Vector search извлекает RAG_INITIAL_TOP_K документов (15)
2. FlashRank переранжирует по релевантности к запросу
3. Выбираются топ RAG_FINAL_TOP_K документов (7)

### 3. Автоматическая оценка качества

Система автоматически оценивает качество ответов и отправляет метрики в Langfuse.

**Метрики:**
- **Relevance** - соответствие ответа вопросу пользователя (0-1)
- **Context Precision** - доля релевантных документов среди найденных (0-1)

**Метаданные в Langfuse:**
- `semantic_chunking` - использовался ли semantic chunking
- `reranking_enabled` - был ли включен re-ranking
- `num_docs` - количество документов
- `query_type` - тип запроса

**Файлы:**
- `backend/services/evaluation_service.py` - EvaluationService
- `backend/agents/nodes/generator.py` - вызов оценки после генерации ответа

**Как работает:**
1. После генерации ответа вызывается `evaluate_rag_pipeline()`
2. LLM оценивает качество ответа и релевантность документов
3. Метрики отправляются в Langfuse с trace_id
4. Можно сравнивать метрики для разных конфигураций (semantic chunking ON/OFF, re-ranking ON/OFF)

## Сравнение подходов

### Старый подход (legacy)
```env
SEMANTIC_CHUNKING_ENABLED=false
RERANK_ENABLED=false
```
- Простое разбиение по размеру (RecursiveCharacterTextSplitter)
- Векторный поиск возвращает 3 документа
- Без re-ranking

### Новый подход (рекомендуемый)
```env
SEMANTIC_CHUNKING_ENABLED=true
RERANK_ENABLED=true
RAG_INITIAL_TOP_K=15
RAG_FINAL_TOP_K=7
```
- Семантическое разбиение (LlamaIndex SentenceSplitter)
- Векторный поиск возвращает 15 документов
- Re-ranking выбирает лучшие 7
- Автоматическая оценка качества

## Мониторинг в Langfuse

После внедрения вы можете:
1. Зайти в Langfuse (http://localhost:3000)
2. Открыть Traces
3. Посмотреть метрики для каждого запроса:
   - `relevance` - качество ответа
   - `context_precision` - качество поиска
   - Метаданные показывают какие настройки использовались

## A/B тестирование

Для сравнения качества старого и нового подхода:

1. Запустите систему со старыми настройками:
```env
SEMANTIC_CHUNKING_ENABLED=false
RERANK_ENABLED=false
```

2. Выполните тестовые запросы и сохраните метрики из Langfuse

3. Переключите на новые настройки:
```env
SEMANTIC_CHUNKING_ENABLED=true
RERANK_ENABLED=true
```

4. Выполните те же запросы

5. Сравните метрики в Langfuse Dashboard

## Файлы изменений

### Новые файлы:
- `backend/services/reranker_service.py` - сервис re-ranking
- `backend/services/evaluation_service.py` - сервис оценки качества
- `RAG_IMPROVEMENTS.md` - эта документация

### Измененные файлы:
- `backend/requirements.txt` - добавлен llama-index-core
- `backend/config/settings.py` - ChunkingSettings, обновлен RAGSettings
- `backend/loader.py` - поддержка semantic chunking
- `backend/rag_service.py` - интеграция re-ranking
- `backend/agents/nodes/rag.py` - использование reranked_docs
- `backend/agents/nodes/generator.py` - автоматическая оценка
- `.env.example` - новые переменные конфигурации

## Производительность

**Semantic Chunking:**
- Незначительное увеличение времени индексации
- Качество чанков выше (разбиение по смыслу)

**Re-ranking:**
- Добавляет ~100-300ms к запросу
- Значительно улучшает качество найденных документов
- Можно отключить для low-latency сценариев

**Evaluation:**
- Выполняется асинхронно после ответа пользователю
- Не влияет на latency ответа
- Использует дополнительные LLM вызовы

## Рекомендации

1. **Продакшн:** Используйте semantic chunking + re-ranking
2. **Разработка:** Можно отключить evaluation для экономии токенов
3. **Отладка:** Отключайте features по одному чтобы понять их влияние
4. **Мониторинг:** Регулярно проверяйте метрики в Langfuse

## Troubleshooting

**Ошибка импорта llama-index:**
```bash
cd backend && pip install llama-index-core>=0.10.0
```

**FlashRank не работает:**
```bash
cd backend && pip install flashrank>=0.2.0
```

**Evaluation не отправляется в Langfuse:**
- Проверьте, что LANGFUSE_PUBLIC_KEY и LANGFUSE_SECRET_KEY установлены
- Убедитесь, что Langfuse доступен по LANGFUSE_HOST
