import uuid
from fastapi import APIRouter, HTTPException
from src.api.models.chat import ChatRequest, ChatResponse, ClearHistoryRequest, SourceInfo
from src.rag.pipeline import Pipeline


router = APIRouter()


class SessionManager:
    """
    Holds one Pipeline per session_id.
    Each session has its own independent chat history.
    """

    def __init__(self):
        self._sessions: dict[str, Pipeline] = {}

    def get_or_create(self, session_id: str) -> Pipeline:
        if session_id not in self._sessions:
            self._sessions[session_id] = Pipeline()
        return self._sessions[session_id]

    def clear(self, session_id: str):
        if session_id in self._sessions:
            self._sessions[session_id].clear_history()


session_manager = SessionManager()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint — takes question, returns answer with sources."""
    session_id = request.session_id or str(uuid.uuid4())

    try:
        pipeline = session_manager.get_or_create(session_id)
        result = pipeline.chat(request.question)

        sources = [
            SourceInfo(
                source=s["source"],
                category=s["category"],
                url=s["url"],
                score=s["score"],
            )
            for s in result["sources"]
        ]

        return ChatResponse(
            answer=result["answer"],
            sources=sources,
            chunks_used=result["chunks_used"],
            session_id=session_id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/clear")
async def clear_history(request: ClearHistoryRequest):
    """Clear chat history for a session — called when user clicks New Chat."""
    session_manager.clear(request.session_id)
    return {"message": f"History cleared for session {request.session_id}"}