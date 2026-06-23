from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """What the frontend sends to us."""
    question: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = Field(None)


class SourceInfo(BaseModel):
    """One source citation returned with the answer."""
    source: str
    category: str
    url: str
    score: float


class ChatResponse(BaseModel):
    """What we send back to the frontend."""
    answer: str
    sources: list[SourceInfo]
    chunks_used: int
    session_id: str


class ClearHistoryRequest(BaseModel):
    """Request to clear chat history for a session."""
    session_id: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    message: str