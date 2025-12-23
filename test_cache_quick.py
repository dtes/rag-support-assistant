#!/usr/bin/env python3
"""
Быстрый тест кэша - делает несколько запросов от разных пользователей
"""

import requests
import json
import time

API_URL = "http://localhost:8000/chat"

def test_cache():
    """Быстрый тест работы кэша"""

    print("=" * 80)
    print("БЫСТРЫЙ ТЕСТ КЭША".center(80))
    print("=" * 80)

    # Проверка доступности
    try:
        health = requests.get("http://localhost:8000/health", timeout=5)
        print(f"\n✓ API доступен: {health.json()}\n")
    except Exception as e:
        print(f"✗ API недоступен: {e}")
        return

    # Тест 1: Один пользователь, одна сессия
    print("\n--- ТЕСТ 1: Один пользователь ---")
    user1 = "alice"
    session1 = None

    for i in range(3):
        question = "What is RAG?" if i != 1 else "How does it work?"
        print(f"\n[{user1}] Запрос {i+1}: {question}")

        start = time.time()
        response = requests.post(API_URL, json={
            "message": question,
            "user_id": user1,
            "session_id": session1
        })
        elapsed = (time.time() - start) * 1000

        if response.ok:
            data = response.json()
            session1 = data['session_id']
            print(f"  ✓ Ответ получен за {elapsed:.0f}мс (сервер: {data.get('processing_time_ms', 0):.0f}мс)")
            print(f"  Session: {session1}")
            print(f"  Тип: {data.get('query_type')}")
            print(f"  Ответ: {data['answer'][:150]}...")
        else:
            print(f"  ✗ Ошибка: {response.status_code}")

        time.sleep(0.5)

    # Тест 2: Разные пользователи
    print("\n\n--- ТЕСТ 2: Разные пользователи ---")
    users = ["bob", "charlie", "diana"]

    for user in users:
        print(f"\n[{user}] Запрос: What are embeddings?")

        start = time.time()
        response = requests.post(API_URL, json={
            "message": "What are embeddings?",
            "user_id": user
        })
        elapsed = (time.time() - start) * 1000

        if response.ok:
            data = response.json()
            print(f"  ✓ Ответ получен за {elapsed:.0f}мс (сервер: {data.get('processing_time_ms', 0):.0f}мс)")
            print(f"  Session: {data['session_id']}")
            print(f"  Источников: {len(data.get('sources', []))}")
        else:
            print(f"  ✗ Ошибка: {response.status_code}")

        time.sleep(0.5)

    # Тест 3: Один пользователь, разные сессии
    print("\n\n--- ТЕСТ 3: Один пользователь, разные сессии ---")
    user3 = "eve"
    sessions = ["work", "personal"]

    for session in sessions:
        print(f"\n[{user3}/{session}] Запрос: Tell me about vector search")

        start = time.time()
        response = requests.post(API_URL, json={
            "message": "Tell me about vector search",
            "user_id": user3,
            "session_id": session
        })
        elapsed = (time.time() - start) * 1000

        if response.ok:
            data = response.json()
            print(f"  ✓ Ответ получен за {elapsed:.0f}мс (сервер: {data.get('processing_time_ms', 0):.0f}мс)")
            print(f"  Session: {data['session_id']}")
        else:
            print(f"  ✗ Ошибка: {response.status_code}")

        time.sleep(0.5)

    # Проверка истории для первого пользователя
    if session1:
        print("\n\n--- ПРОВЕРКА ИСТОРИИ ---")
        print(f"Получаем историю для сессии: {session1}")

        try:
            history = requests.get(f"http://localhost:8000/chat/history/{session1}")
            if history.ok:
                data = history.json()
                print(f"  ✓ Всего сообщений: {len(data.get('messages', []))}")
                print(f"  Статистика: {json.dumps(data.get('stats', {}), indent=2)}")
        except Exception as e:
            print(f"  ✗ Ошибка получения истории: {e}")

    print("\n" + "=" * 80)
    print("ТЕСТ ЗАВЕРШЁН".center(80))
    print("=" * 80)

if __name__ == "__main__":
    test_cache()
