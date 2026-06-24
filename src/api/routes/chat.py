import uuid
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from src.api.models.chat import ChatRequest, ChatResponse, ClearHistoryRequest, SourceInfo
from src.rag.pipeline import Pipeline
from src.db.database import get_db
from src.db.crud import UserCRUD, SessionCRUD, MessageCRUD

router = APIRouter()

pipeline = Pipeline()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, x_user_uid: Optional[str] = Header(None)):
    session_id = request.session_id or str(uuid.uuid4())
    db = next(get_db())

    try:
        # create session in DB if new
        if not request.session_id and x_user_uid:
            user = UserCRUD.get_by_uid(db, x_user_uid)
            if not user:
                user = UserCRUD.create(
                    db=db,
                    uid=x_user_uid,
                    email="",
                    name="",
                    photo_url=""
                )
            title = request.question[:50]
            SessionCRUD.create(db, session_id, x_user_uid, title)

        # fetch last 10 messages from DB for this session
        history = []
        if request.session_id:
            db_messages = MessageCRUD.get_last_n(db, request.session_id, n=10)
            history = [{"role": m.role, "content": m.content} for m in db_messages]

        # run pipeline with DB history
        result = pipeline.chat(request.question, history=history)

        # save messages to DB
        if x_user_uid:
            MessageCRUD.create(
                db=db,
                session_id=session_id,
                role="user",
                content=request.question,
                intent=result["intent"],
                chunks_used=result["chunks_used"],
            )
            MessageCRUD.create(
                db=db,
                session_id=session_id,
                role="assistant",
                content=result["answer"],
                intent=result["intent"],
                chunks_used=result["chunks_used"],
                guardrail_blocked=result["chunks_used"] == 0,
            )
            SessionCRUD.update_timestamp(db, session_id)

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
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()


@router.get("/sessions")
async def get_sessions(x_user_uid: Optional[str] = Header(None)):
    if not x_user_uid:
        return {"sessions": []}

    db = next(get_db())
    try:
        sessions = SessionCRUD.get_all_by_uid(db, x_user_uid)
        return {
            "sessions": [
                {
                    "id": s.id,
                    "title": s.title,
                    "created_at": s.created_at.isoformat(),
                }
                for s in sessions
            ]
        }
    finally:
        db.close()


@router.get("/sessions/{session_id}/messages")
async def get_messages(session_id: str, x_user_uid: Optional[str] = Header(None)):
    db = next(get_db())
    try:
        session = SessionCRUD.get_by_id(db, session_id)
        if not session or session.uid != x_user_uid:
            raise HTTPException(status_code=403, detail="Not authorized")

        messages = MessageCRUD.get_by_session(db, session_id)
        return {
            "messages": [
                {"role": m.role, "content": m.content}
                for m in messages
            ]
        }
    finally:
        db.close()


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, x_user_uid: Optional[str] = Header(None)):
    db = next(get_db())
    try:
        session = SessionCRUD.get_by_id(db, session_id)
        if not session or session.uid != x_user_uid:
            raise HTTPException(status_code=403, detail="Not authorized")
        db.delete(session)
        db.commit()
        return {"message": "Session deleted"}
    finally:
        db.close()


@router.post("/chat/clear")
async def clear_history(request: ClearHistoryRequest):
    return {"message": "History cleared"}