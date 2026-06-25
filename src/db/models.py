from sqlalchemy import Column, String, Boolean, Integer, Date, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from src.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    uid = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    name = Column(String)
    photo_url = Column(String)
    university = Column(String)
    program = Column(String)
    program_start_date = Column(Date)
    program_end_date = Column(Date)
    opt_start_date = Column(Date)
    stem_eligible = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    uid = Column(String, ForeignKey("users.uid", ondelete="CASCADE"), nullable=False)
    title = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    intent = Column(String)
    chunks_used = Column(Integer, default=0)
    guardrail_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())