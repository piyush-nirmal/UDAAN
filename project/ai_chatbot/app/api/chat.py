from fastapi import APIRouter, HTTPException, Depends, Form, Response
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.chatbot.gemini_client import GeminiChatbot
from app.database import crud, database

router = APIRouter()
chatbot = GeminiChatbot()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    status: str = "success"

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest, db: Session = Depends(database.get_db)):
    """
    Handle incoming chat messages, save to DB, and return contextual AI responses.
    """
    if not chat_request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    try:
        # 1. Get or Create Session
        session = crud.get_or_create_session(db, chat_request.session_id)
        
        # 2. Save User Message
        crud.add_message(db, session.id, "user", chat_request.message)
        
        # 3. Get Chat History (includes the new message we just added)
        history = crud.get_session_history(db, session.id)
        
        # 4. Generate Response using history context
        response_text = await chatbot.generate_response(chat_request.message, history)
        
        # 5. Save AI Response
        crud.add_message(db, session.id, "model", response_text)
        
        return ChatResponse(response=response_text, session_id=session.id)
    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/whatsapp")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    db: Session = Depends(database.get_db)
):
    """
    Handle incoming WhatsApp messages from Twilio, returning TwiML response.
    """
    try:
        # Use phone number as the session ID
        session_id = f"wa_{From}"
        session = crud.get_or_create_session(db, session_id)
        
        # Save User Message
        crud.add_message(db, session.id, "user", Body)
        
        # Get Chat History
        history = crud.get_session_history(db, session.id)
        
        # Generate Response using history context
        response_text = await chatbot.generate_response(Body, history)
        
        # Save AI Response
        crud.add_message(db, session.id, "model", response_text)
        
        # Format response for Twilio (TwiML)
        xml_response = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response_text}</Message>
</Response>'''
        return Response(content=xml_response, media_type="application/xml")
        
    except Exception as e:
        print(f"WhatsApp Error: {e}")
        fallback = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>We are experiencing a temporary issue. Please try again later or contact UDAAN Society directly.</Message>
</Response>'''
        return Response(content=fallback, media_type="application/xml")
