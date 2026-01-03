"""
Main - FastAPI приложение для RAG-системы с LangGraph
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from context import AppContext
from api.dependencies import set_context, AppContextDep
from agents.graph import process_query
import os

app = FastAPI(title="RAG Finance Assistant API")

# Global app context
app_context: Optional[AppContext] = None


@app.on_event("startup")
async def startup():
    """Initialize application context on startup"""
    global app_context
    app_context = AppContext()
    app_context.startup()
    set_context(app_context)
    print("✅ Application started successfully")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup application context on shutdown"""
    if app_context:
        app_context.shutdown()
    print("✅ Application stopped")

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

class RetrievedDoc(BaseModel):
    """Full document with content for evaluation/debugging"""
    content: str
    title: str
    filename: str
    chunk_id: int
    score: float
    hybrid_score: Optional[float] = None

class DebugChatResponse(BaseModel):
    """Extended response with debug information for testing/evaluation"""
    # Standard fields
    answer: str
    sources: List[Source]
    query_type: Optional[str] = None
    processing_time_ms: Optional[float] = None
    session_id: str

    # Debug fields
    retrieved_docs: List[RetrievedDoc] = []
    reranked_docs: List[RetrievedDoc] = []
    rewritten_query: Optional[str] = None
    routing_reason: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница с чатом"""
    try:
        with open("/app/frontend/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"<html><body><h1>Ошибка загрузки UI</h1><p>{str(e)}</p></body></html>"

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, ctx: AppContextDep):
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
        user_id = request.user_id or ctx.settings.demo_user_id
        session_id = request.session_id  # Can be None, will be auto-generated

        result = process_query(
            graph=ctx.rag_graph,
            memory_service=ctx.memory_service,
            settings=ctx.settings,
            user_query=request.message,
            user_id=user_id,
            session_id=session_id
        )

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

@app.post("/chat/debug", response_model=DebugChatResponse)
async def chat_debug(request: ChatRequest, ctx: AppContextDep):
    """
    Debug endpoint для тестирования и evaluation

    Возвращает расширенную информацию:
    - retrieved_docs: полные документы с content (для RAGAS evaluation)
    - reranked_docs: документы после reranking
    - rewritten_query: переписанный запрос (если использовалось query rewriting)
    - routing_reason: причина выбора маршрута (RAG/Tools)

    Используется в:
    - tests/test_rag_metrics.py для корректного RAGAS evaluation
    - evaluation/evaluate_rag_system.py для оценки качества

    ВАЖНО: Не использовать в production! Endpoint возвращает большие объемы данных.
    """
    if not request.message or len(request.message.strip()) == 0:
        raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")

    try:
        # Выполнение LangGraph pipeline
        user_id = request.user_id or ctx.settings.demo_user_id
        session_id = request.session_id  # Can be None, will be auto-generated

        result = process_query(
            graph=ctx.rag_graph,
            memory_service=ctx.memory_service,
            settings=ctx.settings,
            user_query=request.message,
            user_id=user_id,
            session_id=session_id
        )

        # Helper function to convert docs to RetrievedDoc model
        def to_retrieved_doc(doc: dict) -> RetrievedDoc:
            return RetrievedDoc(
                content=doc.get('content', ''),
                title=doc.get('title', ''),
                filename=doc.get('filename', ''),
                chunk_id=doc.get('chunk_id', 0),
                score=doc.get('score', 0.0),
                hybrid_score=doc.get('hybrid_score')
            )

        # Extract debug information from result
        retrieved_docs = []
        reranked_docs = []

        # Check if we have retrieved_docs in result (from RAG node)
        if 'retrieved_docs' in result and result['retrieved_docs']:
            retrieved_docs = [to_retrieved_doc(doc) for doc in result['retrieved_docs']]

        # Check if we have reranked_docs (only if reranking was used)
        if 'reranked_docs' in result and result['reranked_docs']:
            reranked_docs = [to_retrieved_doc(doc) for doc in result['reranked_docs']]

        return DebugChatResponse(
            # Standard fields
            answer=result['answer'],
            sources=[Source(**s) for s in result['sources']],
            query_type=result.get('query_type'),
            processing_time_ms=result.get('processing_time_ms'),
            session_id=result['session_id'],
            # Debug fields
            retrieved_docs=retrieved_docs,
            reranked_docs=reranked_docs,
            rewritten_query=result.get('rewritten_query'),
            routing_reason=result.get('routing_reason')
        )
    except Exception as e:
        print(f"Ошибка обработки debug запроса: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")

@app.get("/health")
async def health(ctx: AppContextDep):
    """Проверка состояния системы"""
    from observability.langfuse_client import LangFuseClient

    return {
        "status": "ok",
        "service": "RAG Finance Assistant",
        "langfuse_enabled": LangFuseClient.is_enabled(),
        "demo_user_id": ctx.settings.demo_user_id,
        "weaviate_connected": ctx.weaviate_client.is_connected()
    }

@app.get("/stats")
async def stats(ctx: AppContextDep):
    """Статистика системы"""
    try:
        stats_data = ctx.rag_service.get_stats()
        return {
            **stats_data,
            "langfuse_enabled": ctx.settings.langfuse.enabled,
            "rag_config": {
                "top_k": ctx.settings.rag.final_top_k,
                "rerank_enabled": ctx.settings.rag.rerank_enabled,
                "query_rewriting_enabled": ctx.settings.rag.query_rewriting_enabled
            }
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }

@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str, ctx: AppContextDep, limit: Optional[int] = 20):
    """
    Получить историю чата для сессии

    Args:
        session_id: ID сессии
        limit: Максимальное количество сообщений
    """
    try:
        history = ctx.memory_service.get_history(session_id, limit=limit)
        stats = ctx.memory_service.get_session_stats(session_id)

        return {
            "session_id": session_id,
            "messages": history,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str, ctx: AppContextDep):
    """
    Очистить историю чата для сессии

    Args:
        session_id: ID сессии
    """
    try:
        success = ctx.memory_service.clear_history(session_id)

        if success:
            return {"message": f"History cleared for session {session_id}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear history")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
