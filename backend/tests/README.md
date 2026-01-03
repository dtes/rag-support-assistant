# RAG System Tests

Тесты для оценки качества RAG-системы.

## Структура

```
tests/
├── README.md                 # Эта документация
└── test_rag_metrics.py      # Тесты качества RAG с RAGAS метриками
```

## RAG Metrics Testing

### Назначение

Файл `test_rag_metrics.py` предназначен для **ручного запуска оценки качества RAG-системы**.

**ВАЖНО:** Эти тесты НЕ должны запускаться в production! Они предназначены для:
- Ручной оценки качества после изменений
- Интеграции в CI/CD pipeline (опционально)
- Периодического мониторинга качества
- Тестирования на evaluation датасетах

### Быстрый старт

```bash
# 1. Запустить RAG API (в отдельном терминале)
cd backend
python main.py

# 2. В другом терминале запустить тесты
cd backend
python -m pytest tests/test_rag_metrics.py -v
```

**Важно:** Тесты по умолчанию используют `/chat/debug` endpoint для получения полных документов с content через поле `retrieved_docs`. Это необходимо для корректного расчета RAGAS метрик. Каждый запрос использует случайные `user_id` и `session_id`.

### Использование

#### Вариант 1: Pytest (рекомендуется)

```bash
# Все тесты метрик RAG
python -m pytest tests/test_rag_metrics.py -v

# Тест на конкретном датасете
python -m pytest tests/test_rag_metrics.py -v --dataset evaluation/dataset-2.json

# Только быстрый smoke test (один пример)
python -m pytest tests/test_rag_metrics.py::test_single_rag_example -v

# Полный тест с детальным выводом
python -m pytest tests/test_rag_metrics.py -v -s
```

#### Вариант 2: Standalone скрипт

```bash
# Запуск как обычный Python скрипт (использует /chat/debug по умолчанию)
python tests/test_rag_metrics.py --dataset evaluation/dataset.json

# С кастомным API URL
python tests/test_rag_metrics.py \
  --dataset evaluation/dataset.json \
  --api-url http://localhost:8000/chat

# Без сохранения результатов
python tests/test_rag_metrics.py \
  --dataset evaluation/dataset.json \
  --no-save

# Использовать стандартный /chat endpoint вместо /chat/debug
python tests/test_rag_metrics.py \
  --dataset evaluation/dataset.json \
  --no-debug
```

**Примечание:** Опция `--no-debug` переключает на стандартный `/chat` endpoint, но метрики будут менее точными, так как contexts не будут содержать полный content документов.

### Что делают тесты

**test_rag_metrics_on_dataset** - основной тест:
- Загружает evaluation датасет
- Отправляет каждый вопрос в RAG API (`/chat/debug`)
- Получает answer, sources и retrieved_docs с полным content
- Извлекает contexts из retrieved_docs для RAGAS evaluation
- Запускает RAGAS evaluation с метриками (faithfulness, answer_relevancy, context_precision, context_recall)
- Проверяет минимальные пороги качества (закомментированы по умолчанию)
- Сохраняет детальный отчет в `tests/results/`

**Примечание:** Тест `test_single_rag_example` (smoke test на одном примере) закомментирован в текущей версии.

### Результаты

Результаты сохраняются в:
```
tests/results/
├── dataset_results_20260103_120000.json
├── dataset_results_20260103_130000.json
└── ...
```

Формат результата:
```json
{
  "metadata": {
    "dataset_path": "tests/dataset.json",
    "api_url": "http://localhost:8000/chat/debug",
    "timestamp": "20260103_120000",
    "total_examples": 10,
    "successful": 9,
    "failed": 1
  },
  "aggregate_scores": {
    "answer_relevancy": {"average": 0.75, "min": 0.60, "max": 0.85, "count": 9},
    "faithfulness": {"average": 0.82, "min": 0.70, "max": 0.95, "count": 9},
    "context_precision": {"average": 0.78, "min": 0.65, "max": 0.89, "count": 9},
    "context_recall": {"average": 0.80, "min": 0.68, "max": 0.92, "count": 9},
    "overall": {"average": 0.79, "min": 0.66, "max": 0.90, "count": 9}
  },
  "detailed_results": [
    {
      "question": "...",
      "answer": "...",
      "ground_truth": "...",
      "query_type": "documentation",
      "sources_count": 3,
      "contexts_count": 3,
      "contexts": ["...", "...", "..."],
      "scores": {
        "answer_relevancy": 0.85,
        "faithfulness": 0.90,
        "context_precision": 0.88,
        "context_recall": 0.82,
        "overall": 0.86
      },
      "status": "success"
    }
  ]
}
```

### Метрики

Тесты измеряют следующие RAGAS метрики:

- **faithfulness** - отсутствие галлюцинаций (0-1)
- **answer_relevancy** - релевантность ответа вопросу (0-1)
- **context_precision** - точность поиска документов (0-1)
- **context_recall** - полнота извлеченной информации (0-1, требует ground_truth)
- **overall** - среднее значение всех метрик

### Пороги качества

**ВАЖНО:** В текущей версии проверки порогов качества **закомментированы** (строки 397-398, 405, 411 в `test_rag_metrics.py`).

Тест выполнит evaluation и выведет результаты, но не будет падать при низких scores.

Если вы хотите включить проверку качества, раскомментируйте соответствующие assert'ы:

```python
# В test_rag_metrics.py, строки 396-411
MIN_QUALITY_THRESHOLD = 0.5  # Overall quality >= 50%
assert overall_avg >= MIN_QUALITY_THRESHOLD, \
    f"RAG quality ({overall_avg:.4f}) below threshold ({MIN_QUALITY_THRESHOLD})"

# Faithfulness check
assert faithfulness_avg >= 0.6, "Faithfulness score too low (possible hallucinations)"

# Relevancy check
assert relevancy_avg >= 0.6, "Answer relevancy too low"
```

### Интеграция в CI/CD

Пример для GitHub Actions:

```yaml
# .github/workflows/rag-quality.yml
name: RAG Quality Tests

on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 1'  # Каждый понедельник

jobs:
  test-rag-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Start RAG API
        run: |
          cd backend
          python main.py &
          sleep 10  # Wait for API to start

      - name: Run RAG metrics tests
        run: |
          cd backend
          python -m pytest tests/test_rag_metrics.py -v

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: rag-metrics-results
          path: backend/tests/results/
```

### Debug Endpoint

Тесты используют специальный `/chat/debug` endpoint для получения полной информации о RAG pipeline:

**Что возвращает debug endpoint:**
- `retrieved_docs` - полные документы с content, scores, chunk_id
- `reranked_docs` - документы после reranking (если включен)
- `rewritten_query` - переписанный запрос (если использовалось query rewriting)
- `routing_reason` - причина выбора маршрута (RAG/Tools)

**Почему это важно:**
- RAGAS метрики требуют полный content документов для оценки `faithfulness`, `context_precision`, `context_recall`
- Стандартный `/chat` endpoint возвращает только metadata (`title`, `filename`) для экономии трафика
- Debug endpoint предоставляет всю необходимую информацию для evaluation

**Пример использования вручную:**

```bash
# Тест через debug endpoint (требует user_id и session_id)
curl -X POST http://localhost:8000/chat/debug \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How to use the system?",
    "user_id": "user-12345",
    "session_id": "session-67890"
  }'

# Ответ содержит retrieved_docs с content:
{
  "answer": "You can import bank statements...",
  "sources": [{"title": "Operations", "filename": "operations.md"}],
  "retrieved_docs": [
    {
      "content": "Method 1: Import bank statements...",
      "title": "Operations",
      "filename": "operations.md",
      "chunk_id": 5,
      "score": 0.89
    }
  ],
  "query_type": "documentation",
  "routing_reason": "Question about documentation/features"
}
```

**ВАЖНО:** Debug endpoint НЕ должен использоваться в production! Он возвращает большие объемы данных и предназначен только для тестирования/evaluation.

### Troubleshooting

#### Тесты падают с "API request failed"

**Проблема:** RAG API не запущен или недоступен

**Решение:**
```bash
# Проверить что API работает
curl http://localhost:8000/health

# Запустить API
cd backend
python main.py
```

#### Низкие scores (тест fails)

**Проблема:** RAG система не достигает минимальных порогов качества

**Решение:**
1. Проверить качество документов в базе
2. Настроить retrieval параметры (top_k, reranking)
3. Улучшить промпты для генерации
4. Понизить пороги в тестах (если текущие слишком строгие)

#### "No module named 'pytest'"

**Проблема:** pytest не установлен

**Решение:**
```bash
pip install -r requirements.txt
```

## Дальнейшее развитие

Планы по улучшению тестирования:

1. ✅ Тесты RAG метрик (сделано)
2. ⏳ Unit тесты для отдельных компонентов
3. ⏳ Integration тесты для nodes
4. ⏳ Performance тесты (latency, throughput)
5. ⏳ E2E тесты через UI

## Полезные ссылки

- [RAGAS Documentation](https://docs.ragas.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Evaluation README](../evaluation/README.md)
