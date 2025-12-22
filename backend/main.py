"""
Main - FastAPI приложение для RAG-системы с LangGraph
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from agents.graph import process_query
from config.settings import settings
import os

app = FastAPI(title="RAG Finance Assistant API")

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None  # For chat history

class Source(BaseModel):
    title: str
    filename: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    query_type: Optional[str] = None
    processing_time_ms: Optional[float] = None
    session_id: str  # Return session_id to frontend

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

    LangGraph Pipeline:
    1. Router: определяет тип запроса (documentation/operational)
    2. RAG path: векторный поиск для вопросов о документации
    3. Tools path: вызов API для операционных данных
    4. Generator: генерация финального ответа
    5. LangFuse: автоматический tracing
    """
    if not request.message or len(request.message.strip()) == 0:
        raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")

    try:
        # Выполнение LangGraph pipeline с поддержкой chat history
        user_id = request.user_id or settings.demo_user_id
        session_id = request.session_id  # Can be None, will be auto-generated

        result = process_query(request.message, user_id, session_id)

        return ChatResponse(
            answer=result['answer'],
            sources=[Source(**s) for s in result['sources']],
            query_type=result.get('query_type'),
            processing_time_ms=result.get('processing_time_ms'),
            session_id=result['session_id']
        )
    except Exception as e:
        print(f"Ошибка обработки запроса: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")

@app.get("/health")
async def health():
    """Проверка состояния системы"""
    from observability.langfuse_client import LangFuseClient

    return {
        "status": "ok",
        "service": "RAG Finance Assistant",
        "langfuse_enabled": LangFuseClient.is_enabled(),
        "demo_user_id": settings.demo_user_id
    }

@app.get("/stats")
async def stats():
    """Статистика системы"""
    from agents.nodes.rag import get_rag_service

    try:
        rag_service = get_rag_service()
        stats_data = rag_service.get_stats()
        return {
            **stats_data,
            "langfuse_enabled": settings.langfuse.enabled,
            "rag_config": {
                "top_k": settings.rag.top_k,
                "rerank_enabled": settings.rag.rerank_enabled,
                "query_rewriting_enabled": settings.rag.query_rewriting_enabled
            }
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }

@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str, limit: Optional[int] = 20):
    """
    Получить историю чата для сессии

    Args:
        session_id: ID сессии
        limit: Максимальное количество сообщений
    """
    from services.memory_service import get_memory_service

    try:
        memory_service = get_memory_service()
        history = memory_service.get_history(session_id, limit=limit)
        stats = memory_service.get_session_stats(session_id)

        return {
            "session_id": session_id,
            "messages": history,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Очистить историю чата для сессии

    Args:
        session_id: ID сессии
    """
    from services.memory_service import get_memory_service

    try:
        memory_service = get_memory_service()
        success = memory_service.clear_history(session_id)

        if success:
            return {"message": f"History cleared for session {session_id}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear history")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
