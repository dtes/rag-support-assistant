"""
RAG Service - основная логика поиска и генерации ответов
"""
import os
import weaviate
from anthropic import Anthropic
from sentence_transformers import SentenceTransformer

# Конфигурация
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Lightweight and fast local model

class RAGService:
    def __init__(self):
        """Инициализация сервиса"""
        self.weaviate_client = None
        self.anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

        # Load local embedding model
        print(f"Loading local embedding model: {EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        print("✓ Local embedding model loaded")

        self.connect_weaviate()

    def connect_weaviate(self):
        """Подключение к Weaviate"""
        try:
            self.weaviate_client = weaviate.connect_to_custom(
                http_host="weaviate",
                http_port=8080,
                http_secure=False,
                grpc_host="weaviate",
                grpc_port=50051,
                grpc_secure=False,
            )
            print("✓ Подключение к Weaviate установлено")
        except Exception as e:
            print(f"✗ Ошибка подключения к Weaviate: {e}")
            self.weaviate_client = None

    def get_embedding(self, text: str) -> list[float]:
        """Создание эмбеддинга для текста с использованием локальной модели"""
        try:
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            print(f"✗ Ошибка создания эмбеддинга: {e}")
            return None
    
    def search_documents(self, query: str, top_k: int = 3):
        """Поиск релевантных документов"""
        if not self.weaviate_client:
            self.connect_weaviate()
        
        if not self.weaviate_client:
            return []
        
        try:
            # Создание эмбеддинга для запроса
            query_embedding = self.get_embedding(query)
            if query_embedding is None:
                return []
            
            # Получение коллекции
            documentation = self.weaviate_client.collections.get("Documentation")
            
            # Векторный поиск
            response = documentation.query.near_vector(
                near_vector=query_embedding,
                limit=top_k,
                return_metadata=['distance']
            )
            
            # Формирование результатов
            results = []
            for item in response.objects:
                results.append({
                    'content': item.properties['content'],
                    'filename': item.properties['filename'],
                    'title': item.properties['title'],
                    'chunk_id': item.properties['chunk_id'],
                    'distance': item.metadata.distance if item.metadata else None
                })
            
            return results
            
        except Exception as e:
            print(f"✗ Ошибка поиска: {e}")
            return []
    
    def generate_answer(self, query: str, context_docs: list) -> dict:
        """Генерация ответа с использованием Claude"""
        if not context_docs:
            return {
                'answer': 'Извините, не удалось найти релевантную информацию в документации.',
                'sources': []
            }
        
        # Формирование контекста из найденных документов
        context = "\n\n---\n\n".join([
            f"Документ: {doc['title']} ({doc['filename']})\n{doc['content']}"
            for doc in context_docs
        ])
        
        # Промпт для Claude
        prompt = f"""Ты - AI-ассистент технической поддержки. Твоя задача - отвечать на вопросы пользователей на основе предоставленной документации сайта.

Документация:
{context}

Вопрос пользователя: {query}

Инструкции:
1. Дай точный и полезный ответ на основе ТОЛЬКО предоставленной документации
2. Если информации недостаточно, честно скажи об этом
3. Отвечай на русском языке
4. Будь кратким и конкретным
5. Используй дружелюбный тон

Ответ:"""
        
        try:
            # Запрос к Claude API
            message = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            answer = message.content[0].text
            
            # Формирование источников
            sources = [
                {
                    'title': doc['title'],
                    'filename': doc['filename']
                }
                for doc in context_docs
            ]
            
            # Удаление дубликатов источников
            unique_sources = []
            seen = set()
            for source in sources:
                key = (source['title'], source['filename'])
                if key not in seen:
                    seen.add(key)
                    unique_sources.append(source)
            
            return {
                'answer': answer,
                'sources': unique_sources
            }
            
        except Exception as e:
            print(f"✗ Ошибка генерации ответа: {e}")
            return {
                'answer': f'Произошла ошибка при генерации ответа: {str(e)}',
                'sources': []
            }
    
    def process_query(self, query: str) -> dict:
        """Полный RAG pipeline: поиск + генерация"""
        # Шаг 1: Поиск релевантных документов
        print(f"Запрос: {query}")
        docs = self.search_documents(query, top_k=3)
        print(f"Найдено документов: {len(docs)}")
        
        # Шаг 2: Генерация ответа
        result = self.generate_answer(query, docs)
        
        return result
    
    def get_stats(self) -> dict:
        """Получение статистики БД"""
        if not self.weaviate_client:
            self.connect_weaviate()
        
        try:
            documentation = self.weaviate_client.collections.get("Documentation")
            count = len(documentation)
            
            return {
                'total_chunks': count,
                'status': 'ok'
            }
        except Exception as e:
            return {
                'total_chunks': 0,
                'status': f'error: {str(e)}'
            }
    
    def close(self):
        """Закрытие соединений"""
        if self.weaviate_client:
            self.weaviate_client.close()
