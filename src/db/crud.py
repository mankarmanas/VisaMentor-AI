from sqlalchemy.orm import Session
from sqlalchemy import desc
from src.db.models import User, Session as SessionModel, Message
from datetime import date
from typing import Optional


class UserCRUD:

    @staticmethod
    def get_by_uid(db: Session, uid: str) -> Optional[User]:
        return db.query(User).filter(User.uid == uid).first()

    @staticmethod
    def create(db: Session, uid: str, email: str, name: str, photo_url: str) -> User:
        user = User(uid=uid, email=email, name=name, photo_url=photo_url)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_profile(
        db: Session,
        uid: str,
        university: str,
        program: str,
        program_start_date: date,
        program_end_date: date,
        stem_eligible: bool,
    ) -> Optional[User]:
        user = db.query(User).filter(User.uid == uid).first()
        if not user:
            return None
        user.university = university
        user.program = program
        user.program_start_date = program_start_date
        user.program_end_date = program_end_date
        user.stem_eligible = stem_eligible
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def has_profile(db: Session, uid: str) -> bool:
        user = db.query(User).filter(User.uid == uid).first()
        if not user:
            return False
        return user.university is not None and user.program is not None
    
    @staticmethod
    def update_opt_start_date(db: Session, uid: str, opt_start_date: date) -> Optional[User]:
        user = db.query(User).filter(User.uid == uid).first()
        if not user:
            return None
        user.opt_start_date = opt_start_date
        db.commit()
        db.refresh(user)
        return user


class SessionCRUD:

    @staticmethod
    def create(db: Session, session_id: str, uid: str, title: str) -> SessionModel:
        session = SessionModel(id=session_id, uid=uid, title=title)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_all_by_uid(db: Session, uid: str) -> list[SessionModel]:
        return (
            db.query(SessionModel)
            .filter(SessionModel.uid == uid)
            .order_by(desc(SessionModel.updated_at))
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, session_id: str) -> Optional[SessionModel]:
        return db.query(SessionModel).filter(SessionModel.id == session_id).first()

    @staticmethod
    def update_timestamp(db: Session, session_id: str):
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if session:
            from datetime import datetime, timezone
            session.updated_at = datetime.now(timezone.utc)
            db.commit()

    @staticmethod
    def get_last_n(db: Session, session_id: str, n: int = 10) -> list[Message]:
        return (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at)
            .all()[-n:]
        )


class MessageCRUD:

    @staticmethod
    def create(
        db: Session,
        session_id: str,
        role: str,
        content: str,
        intent: str = None,
        chunks_used: int = 0,
        guardrail_blocked: bool = False,
    ) -> Message:
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
            intent=intent,
            chunks_used=chunks_used,
            guardrail_blocked=guardrail_blocked,
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_by_session(db: Session, session_id: str) -> list[Message]:
        return (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at)
            .all()
        )
    
    @staticmethod
    def get_last_n(db: Session, session_id: str, n: int = 10) -> list[Message]:
        messages = (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at)
            .all()
        )
        return messages[-n:]