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

**Важно:** Тесты по умолчанию используют `/chat/debug` endpoint для получения полных документов с content. Это необходимо для корректного расчета RAGAS метрик.

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

1. **test_rag_metrics_on_dataset** - основной тест:
   - Загружает evaluation датасет
   - Отправляет каждый вопрос в RAG API
   - Получает answer и sources
   - Запускает RAGAS evaluation
   - Проверяет минимальные пороги качества
   - Сохраняет детальный отчет

2. **test_single_rag_example** - smoke test:
   - Быстрый тест на одном примере
   - Проверяет что RAG pipeline работает
   - Полезен для отладки

### Результаты

Результаты сохраняются в:
```
evaluation/results/
├── dataset_results_20260101_120000.json
├── dataset-2_results_20260101_130000.json
└── ...
```

Формат результата:
```json
{
  "metadata": {
    "dataset_path": "evaluation/dataset.json",
    "timestamp": "20260101_120000",
    "total_examples": 10,
    "successful": 9,
    "failed": 1
  },
  "aggregate_scores": {
    "overall": {"average": 0.78, "min": 0.65, "max": 0.89},
    "faithfulness": {"average": 0.82, "min": 0.70, "max": 0.95},
    "answer_relevancy": {"average": 0.75, "min": 0.60, "max": 0.85}
  },
  "detailed_results": [...]
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

По умолчанию в тестах установлены минимальные пороги:

```python
MIN_QUALITY_THRESHOLD = 0.5  # Overall quality >= 50%
MIN_FAITHFULNESS = 0.6       # No hallucinations >= 60%
MIN_RELEVANCY = 0.6          # Relevancy >= 60%
```

Вы можете изменить их в файле `test_rag_metrics.py` под ваши требования.

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
          path: backend/evaluation/results/
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
# Тест через debug endpoint
curl -X POST http://localhost:8000/chat/debug \
  -H "Content-Type: application/json" \
  -d '{"message": "How to import bank statements?"}'

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
