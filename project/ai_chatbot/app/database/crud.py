from sqlalchemy.orm import Session
from . import models
import uuid

def get_or_create_session(db: Session, session_id: str = None):
    """Fetch an existing session or create a new one with a UUID."""
    if session_id:
        session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
        if session:
            return session
    
    # Create new session if none found or no ID provided
    new_id = str(uuid.uuid4())
    db_session = models.ChatSession(id=new_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def add_message(db: Session, session_id: str, role: str, content: str):
    """Save a single chat message to the database."""
    db_message = models.ChatMessage(session_id=session_id, role=role, content=content)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_session_history(db: Session, session_id: str):
    """Retrieve all messages for a given session in chronological order."""
    return db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).order_by(models.ChatMessage.created_at.asc()).all()
