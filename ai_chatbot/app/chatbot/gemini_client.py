import os
import time
import hashlib
import google.generativeai as genai

from collections import OrderedDict

from app.chatbot.retriever import Retriever


# ============================================================
# GEMINI API KEY
# ============================================================

api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    print("✅ Gemini API Key Loaded")
else:
    print("❌ Gemini API Key NOT Found")


# ============================================================
# GEMINI CHATBOT
# ============================================================

class GeminiChatbot:
    """Handles communication with the Google Gemini API using RAG."""

    def __init__(self):

        # ----------------------------------------------------
        # API KEY
        # ----------------------------------------------------

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            print("WARNING: GEMINI_API_KEY environment variable not set.")
        else:
            genai.configure(api_key=api_key)

        # ----------------------------------------------------
        # UDAAN SYSTEM PROMPT
        # ----------------------------------------------------

        from app.chatbot.udaan_context import UDAAN_SYSTEM_PROMPT

        # ----------------------------------------------------
        # INITIALIZE GEMINI MODEL
        # ----------------------------------------------------

        try:

            self.model = genai.GenerativeModel(
                "gemini-2.5-flash",
                system_instruction=UDAAN_SYSTEM_PROMPT
            )

            print("✅ Gemini model initialized")

        except Exception as e:

            print(f"❌ Error initializing Gemini model: {e}")

            self.model = None

        # ----------------------------------------------------
        # LRU CACHE
        # ----------------------------------------------------

        self.cache = OrderedDict()

        self.MAX_CACHE_SIZE = 500

        # ----------------------------------------------------
        # RAG RETRIEVER
        # ----------------------------------------------------

        # IMPORTANT:
        # Retriever is initialized only once.
        # This prevents the embedding model from loading
        # again for every user question.

        self.retriever = Retriever()

        print("✅ Retriever initialized")


    # ========================================================
    # GENERATE RESPONSE
    # ========================================================

    async def generate_response(
        self,
        message: str,
        history_records=None
    ) -> str:

        """
        Generate a response using:

        1. RAG
        2. Conversation history
        3. Gemini
        4. LRU caching
        """

        # ----------------------------------------------------
        # START TOTAL TIMER
        # ----------------------------------------------------

        start = time.time()

        # ----------------------------------------------------
        # CHECK GEMINI MODEL
        # ----------------------------------------------------

        if not self.model:

            return (
                "Error: Gemini model not initialized. "
                "Please check your API key."
            )

        # ====================================================
        # CACHE
        # ====================================================

        history_str = ""

        if history_records:

            for record in history_records[-10:]:

                history_str += (
                    f"{record.role}:{record.content}|"
                )

        cache_key_raw = (
            f"{message.lower().strip()}|{history_str}"
        )

        cache_key = hashlib.sha256(
            cache_key_raw.encode()
        ).hexdigest()

        # ----------------------------------------------------
        # CACHE HIT
        # ----------------------------------------------------

        if cache_key in self.cache:

            self.cache.move_to_end(cache_key)

            print("🟢 CACHE HIT")

            print(
                f"TOTAL TIME: "
                f"{time.time() - start:.2f}s"
            )

            return self.cache[cache_key]

        # ====================================================
        # MAIN PROCESS
        # ====================================================

        try:

            # =================================================
            # RAG SEARCH
            # =================================================

            rag_start = time.time()

            results = self.retriever.search(
                message
            )

            rag_time = time.time() - rag_start

            print(
                f"RAG TIME: {rag_time:.2f}s"
            )

            # -------------------------------------------------
            # NO RESULTS
            # -------------------------------------------------

            if not results:

                return (
                    "I couldn't find reliable information "
                    "in the UDAAN knowledge base. "
                    "Please contact UDAAN Society through "
                    "the Contact Us page."
                )

            # =================================================
            # BUILD CONTEXT
            # =================================================

            context = "\n\n".join(
                doc["text"]
                for doc in results
            )

            # -------------------------------------------------
            # DEBUG CONTEXT
            # -------------------------------------------------

            print("=" * 80)
            print("CONTEXT SENT TO GEMINI")
            print(context)
            print("=" * 80)

            # -------------------------------------------------
            # SOURCES
            # -------------------------------------------------

            sources = ", ".join(
                sorted(
                    set(
                        doc["source"]
                        for doc in results
                    )
                )
            )

            print(
                f"RAG SOURCES: {sources}"
            )

            # =================================================
            # CONVERSATION MEMORY
            # =================================================

            conversation = ""

            if history_records:

                for record in history_records[-5:]:

                    speaker = (
                        "User"
                        if record.role == "user"
                        else "Assistant"
                    )

                    conversation += (
                        f"{speaker}: "
                        f"{record.content}\n"
                    )

            # =================================================
            # BUILD PROMPT
            # =================================================

            prompt = f"""
You are UDAAN Saathi, the official AI assistant of UDAAN Society.

Answer ONLY using the knowledge provided below.

IMPORTANT RULES:
1. Use the provided knowledge as the primary source of truth.
2. Do not invent information.
3. If the answer is available in the knowledge, answer clearly.
4. Combine multiple knowledge snippets when necessary.
5. Keep the answer concise but complete.
6. Do not stop after one sentence if the question requires more information.
7. For simple factual questions, give a short direct answer.
8. For questions asking "how", provide the relevant steps or process.
9. Do not mention RAG, embeddings, Gemini, context, or internal systems.

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

            # -------------------------------------------------
            # DEBUG PROMPT
            # -------------------------------------------------

            print("=" * 80)
            print("PROMPT SENT TO GEMINI")
            print(prompt)
            print("=" * 80)

            # =================================================
            # GEMINI GENERATION
            # =================================================

            gemini_start = time.time()

            response = self.model.generate_content(
                prompt
            )

            gemini_time = time.time() - gemini_start

            print(
                f"GEMINI TIME: "
                f"{gemini_time:.2f}s"
            )

            # =================================================
            # GET RESPONSE
            # =================================================

            response_text = response.text

            # -------------------------------------------------
            # RESPONSE DEBUG
            # -------------------------------------------------

            print("=" * 80)
            print("GEMINI RESPONSE")
            print(response_text)
            print("=" * 80)

            print(
                "RESPONSE LENGTH:",
                len(response_text)
            )

            # -------------------------------------------------
            # FINISH REASON
            # -------------------------------------------------

            try:

                print(
                    "FINISH REASON:",
                    response.candidates[0].finish_reason
                )

            except Exception:

                print(
                    "FINISH REASON: "
                    "Unable to determine"
                )

            # =================================================
            # CACHE RESPONSE
            # =================================================

            self.cache[cache_key] = response_text

            self.cache.move_to_end(cache_key)

            # -------------------------------------------------
            # LIMIT CACHE SIZE
            # -------------------------------------------------

            if len(self.cache) > self.MAX_CACHE_SIZE:

                self.cache.popitem(
                    last=False
                )

            # =================================================
            # TOTAL TIME
            # =================================================

            total_time = time.time() - start

            print("=" * 80)
            print(
                f"TOTAL TIME: {total_time:.2f}s"
            )
            print("=" * 80)

            # =================================================
            # RETURN RESPONSE
            # =================================================

            return response_text

        # ====================================================
        # ERROR HANDLING
        # ====================================================

        except Exception as e:

            print("=" * 80)
            print("❌ CHATBOT ERROR")
            print(str(e))
            print("=" * 80)

            return (
                f"Error generating response from Gemini: "
                f"{str(e)}"
            )