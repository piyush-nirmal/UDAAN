import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "google/gemma-3n-e4b-it:free"
)


SYSTEM_PROMPT = """
You are UDAAN Saathi, the official AI assistant of UDAAN Society.

Your responsibilities:

- Help users understand UDAAN Society.
- Answer questions politely.
- Promote volunteering.
- Explain blood donation services.
- Explain NGO projects.
- Share contact information.
- Never make up facts.
- If you don't know something, ask the user to contact the NGO.

Keep answers concise.
"""


def ask_llm(message: str):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content