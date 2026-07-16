import os
import hashlib
import google.generativeai as genai
from typing import List, Dict, Optional
from collections import OrderedDict
from app.chatbot.retriever import Retriever

api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    print("✅ Gemini API Key Loaded")
else:
    print("❌ Gemini API Key NOT Found")

class GeminiChatbot:
    """Handles communication with the Google Gemini API."""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GEMINI_API_KEY environment variable not set.")
        else:
            genai.configure(api_key=api_key)
            
        from app.chatbot.udaan_context import UDAAN_SYSTEM_PROMPT
        
        # Initialize the model
        try:
            self.model = genai.GenerativeModel(
                'gemini-2.5-flash',
                system_instruction=UDAAN_SYSTEM_PROMPT
            )
        except Exception as e:
            print(f"Error initializing Gemini model: {e}")
            self.model = None
            
        # Initialize a simple in-memory LRU cache to save tokens
        self.cache = OrderedDict()
        self.MAX_CACHE_SIZE = 500
        self.retriever = Retriever()

    async def generate_response(self, message: str, history_records=None) -> str:
        """
        Generate a response using RAG + conversation history + caching.
        """

        if not self.model:
            return "Error: Gemini model not initialized. Please check your API key."

        # ---------- CACHE ----------
        history_str = ""
        if history_records:
            for record in history_records[-10:]:
                history_str += f"{record.role}:{record.content}|"

        cache_key_raw = f"{message.lower().strip()}|{history_str}"
        cache_key = hashlib.sha256(cache_key_raw.encode()).hexdigest()

        if cache_key in self.cache:
            self.cache.move_to_end(cache_key)
            print("🟢 CACHE HIT")
            return self.cache[cache_key]

        try:
            # ---------- RAG ----------
            results = self.retriever.search(message)

            if not results:
                return (
                    "I couldn't find reliable information in the UDAAN knowledge base. "
                    "Please contact UDAAN Society through the Contact Us page."
                )

            context = "\n\n".join(doc["text"] for doc in results)

            sources = ", ".join(
                sorted(set(doc["source"] for doc in results))
            )

            # ---------- Conversation Memory ----------
            conversation = ""

            if history_records:
                for record in history_records[-5:]:
                    speaker = "User" if record.role == "user" else "Assistant"
                    conversation += f"{speaker}: {record.content}\n"

            prompt = f"""
    You are UDAAN Saathi, the official AI assistant of UDAAN Society.

    Answer ONLY using the knowledge below.

    =========================
    KNOWLEDGE
    =========================

    {context}

    =========================
    CONVERSATION
    =========================

    {conversation}

    =========================
    QUESTION
    =========================

    {message}
    """

            response = self.model.generate_content(prompt)

            response_text = response.text


            # ---------- SAVE CACHE ----------
            self.cache[cache_key] = response_text

            if len(self.cache) > self.MAX_CACHE_SIZE:
                self.cache.popitem(last=False)

            return response_text

        except Exception as e:
            return f"Error generating response from Gemini: {str(e)}"
        