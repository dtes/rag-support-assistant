"""
Main - FastAPI приложение для RAG-системы
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from rag_service import RAGService
import os

app = FastAPI(title="RAG Support Assistant API")

# Инициализация RAG сервиса
rag_service = RAGService()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    sources: list

@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница с чатом"""
    try:
        with open("/app/frontend/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"<html><body><h1>Ошибка загрузки UI</h1><p>{str(e)}</p></body></html>"

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Основной endpoint для обработки вопросов пользователя
    
    RAG Pipeline:
    1. Получение вопроса
    2. Создание эмбеддинга
    3. Векторный поиск в Weaviate
    4. Генерация ответа через Claude
    5. Возврат ответа с источниками
    """
    if not request.message or len(request.message.strip()) == 0:
        raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")
    
    try:
        # Выполнение RAG pipeline
        result = rag_service.process_query(request.message)
        
        return ChatResponse(
            answer=result['answer'],
            sources=result['sources']
        )
    except Exception as e:
        print(f"Ошибка обработки запроса: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")

@app.get("/health")
async def health():
    """Проверка состояния системы"""
    return {
        "status": "ok",
        "service": "RAG Support Assistant",
        "weaviate": "connected" if rag_service.weaviate_client else "disconnected"
    }

@app.get("/stats")
async def stats():
    """Статистика базы данных"""
    try:
        stats_data = rag_service.get_stats()
        return stats_data
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }

@app.on_event("shutdown")
async def shutdown_event():
    """Закрытие соединений при остановке"""
    rag_service.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
