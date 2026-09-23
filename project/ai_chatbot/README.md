# AI Chatbot Platform

A complete production-ready AI chatbot system featuring Website integration, WhatsApp integration, RAG capabilities, and Gemini AI.

## Project Structure
```text
project-root/
│
├── app/
│   ├── api/          # API routes
│   ├── chatbot/      # LLM logic
│   ├── rag/          # RAG pipeline (Phase 3)
│   ├── whatsapp/     # WhatsApp integration (Phase 4)
│   ├── database/     # DB models (Phase 2)
│   ├── static/       # Frontend CSS/JS
│   ├── templates/    # HTML templates
│   └── main.py       # FastAPI application
```

## Phases
- **Phase 1**: FastAPI + Gemini Integration + Basic UI ✅
- **Phase 2**: PostgreSQL + Conversation Memory (Pending)
- **Phase 3**: RAG Architecture + Document Uploads (Pending)
- **Phase 4**: WhatsApp Integration (Pending)
- **Phase 5**: Dockerization + Deployment (Pending)

## Setup (Phase 1)
1. Navigate to this directory.
2. Ensure you have Python 3.12 installed (or compatible Python 3 version).
3. Create a virtual environment: `python -m venv venv`
4. Activate it:
   - Windows: `.\venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Open `.env` and add your `GEMINI_API_KEY`.
7. Run the server: `uvicorn app.main:app --reload`
8. Visit `http://localhost:8000` in your browser.
