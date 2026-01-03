"""
Loader - автоматическая загрузка документации в Weaviate при старте системы
"""
import os
import time
from weaviate.classes.config import Configure, Property, DataType
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from pathlib import Path
from infra.weaviate_client import WeaviateClient
from config.settings import settings

# Конфигурация
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Lightweight and fast local model
DATA_DIR = "/app/data"

def wait_for_weaviate(max_retries=30):
    """Ожидание готовности Weaviate"""
    print("Ожидание запуска Weaviate...")
    for i in range(max_retries):
        try:
            weaviate_client = WeaviateClient(
                url=settings.weaviate.url,
                collection_name=settings.weaviate.collection_name
            )
            weaviate_client.connect()

            if weaviate_client.client.is_ready():
                print("✓ Weaviate готов к работе")
                weaviate_client.close()
                return True
            weaviate_client.close()
        except Exception as e:
            print(f"Попытка {i+1}/{max_retries}: Weaviate еще не готов - {e}")
            time.sleep(2)
    return False

def create_schema(client):
    """Создание схемы в Weaviate"""
    collection_name = "Documentation"
    
    try:
        # Проверяем существует ли коллекция
        if client.collections.exists(collection_name):
            print(f"✓ Коллекция '{collection_name}' уже существует")
            return True
        
        # Создаем новую коллекцию
        client.collections.create(
            name=collection_name,
            properties=[
                Property(name="content", data_type=DataType.TEXT),
                Property(name="filename", data_type=DataType.TEXT),
                Property(name="chunk_id", data_type=DataType.NUMBER),
                Property(name="title", data_type=DataType.TEXT),
            ],
            vectorizer_config=Configure.Vectorizer.none(),
        )
        print(f"✓ Коллекция '{collection_name}' создана")
        return True
    except Exception as e:
        print(f"✗ Ошибка создания схемы: {e}")
        return False

def get_embedding(text: str, embedding_model) -> list[float]:
    """Создание эмбеддинга для текста с использованием локальной модели"""
    try:
        embedding = embedding_model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    except Exception as e:
        print(f"✗ Ошибка создания эмбеддинга: {e}")
        return None

def create_text_splitter():
    """
    Создание text splitter на основе конфигурации

    Returns:
        Text splitter (RecursiveCharacterTextSplitter или SemanticChunker)
    """
    chunking_method = settings.chunking.method.lower()

    if chunking_method == "semantic":
        print(f"Using SemanticChunker (breakpoint_type={settings.chunking.semantic_breakpoint_type}, threshold={settings.chunking.semantic_breakpoint_threshold})")

        # Создание HuggingFace embeddings для SemanticChunker
        # Используем ту же модель, что и для основной системы
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding.model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        # Создание SemanticChunker с настройками из конфига
        text_splitter = SemanticChunker(
            embeddings=embeddings,
            breakpoint_threshold_type=settings.chunking.semantic_breakpoint_type,
            breakpoint_threshold_amount=settings.chunking.semantic_breakpoint_threshold
        )

        return text_splitter

    else:
        # По умолчанию используем RecursiveCharacterTextSplitter
        print(f"Using RecursiveCharacterTextSplitter (chunk_size={settings.chunking.chunk_size}, chunk_overlap={settings.chunking.chunk_overlap})")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunking.chunk_size,
            chunk_overlap=settings.chunking.chunk_overlap,
            length_function=len,
        )

        return text_splitter

def load_documents():
    """Загрузка и индексация документов из папки data/"""

    if not wait_for_weaviate():
        print("✗ Не удалось подключиться к Weaviate")
        return False

    # Подключение к Weaviate
    weaviate_client = WeaviateClient(
        url=settings.weaviate.url,
        collection_name=settings.weaviate.collection_name
    )
    weaviate_client.connect()
    client = weaviate_client.client

    # Создание схемы
    if not create_schema(client):
        weaviate_client.close()
        return False

    # Инициализация локальной модели эмбеддингов
    print(f"Loading local embedding model: {EMBEDDING_MODEL}")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    print("✓ Local embedding model loaded")
    
    # Получение коллекции
    documentation = client.collections.get("Documentation")

    # Очистка коллекции перед загрузкой
    existing_count = len(documentation)
    if existing_count > 0:
        print(f"Найдено {existing_count} существующих документов. Очистка коллекции...")
        # Удаляем коллекцию и создаем заново
        client.collections.delete("Documentation")
        if not create_schema(client):
            client.close()
            return False
        documentation = client.collections.get("Documentation")
        print("✓ Коллекция очищена")
    
    # Инициализация текстового сплиттера на основе конфигурации
    text_splitter = create_text_splitter()
    
    # Проверка наличия файлов
    data_path = Path(DATA_DIR)
    if not data_path.exists():
        print(f"✗ Папка {DATA_DIR} не найдена")
        client.close()
        return False
    
    md_files = list(data_path.glob("*.md"))
    if not md_files:
        print(f"⚠ В папке {DATA_DIR} нет .md файлов")
        print("⚠ Добавьте файлы документации в папку data/ и перезапустите систему")
        client.close()
        return True
    
    print(f"Найдено {len(md_files)} .md файлов для индексации")
    
    # Обработка каждого файла
    total_chunks = 0
    for md_file in md_files:
        print(f"Обработка: {md_file.name}")
        
        try:
            # Чтение файла
            content = md_file.read_text(encoding='utf-8')
            
            # Извлечение заголовка (первая строка с #)
            title = md_file.stem
            for line in content.split('\n'):
                if line.startswith('#'):
                    title = line.lstrip('#').strip()
                    break
            
            # Разбиение на чанки
            chunks = text_splitter.split_text(content)
            print(f"  → Создано {len(chunks)} чанков")
            
            # Индексация чанков
            for chunk_id, chunk in enumerate(chunks):
                # Создание эмбеддинга
                embedding = get_embedding(chunk, embedding_model)
                if embedding is None:
                    print(f"  ✗ Пропуск чанка {chunk_id} из-за ошибки эмбеддинга")
                    continue

                if chunk_id == 0:
                    print(f"  → Embedding dimension: {len(embedding)}")

                # Добавление в Weaviate
                documentation.data.insert(
                    properties={
                        "content": chunk,
                        "filename": md_file.name,
                        "chunk_id": chunk_id,
                        "title": title,
                    },
                    vector=embedding
                )
                total_chunks += 1
            
            print(f"  ✓ Файл {md_file.name} проиндексирован")
            
        except Exception as e:
            print(f"  ✗ Ошибка обработки файла {md_file.name}: {e}")
    
    print(f"\n✓ Индексация завершена: {total_chunks} чанков из {len(md_files)} файлов")

    weaviate_client.close()
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Загрузка документации в векторную базу данных")
    print("=" * 60)
    
    success = load_documents()
    
    if success:
        print("\n✓ Система готова к работе")
    else:
        print("\n✗ Возникли ошибки при загрузке")
        exit(1)
