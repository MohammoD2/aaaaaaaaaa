import os
import re
import json
import asyncio
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# ------------------------------
# Load environment variables
# ------------------------------
load_dotenv()  # Only needed for local testing
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY environment variable is not set!")

API_URL = "https://openrouter.ai/api/v1/chat/completions"

# ------------------------------
# FastAPI app
# ------------------------------
app = FastAPI(title="AllOfTech AI Chatbot API")

# ------------------------------
# Chatbot personality
# ------------------------------
AGENCY_SYSTEM_PROMPT = """
You are ALLOFTECH AI — the official intelligent assistant of AllOfTech, an innovative technology solutions agency.

AllOfTech provides:
- AI & Machine Learning Development
- Blockchain Development
- Web Development
- Mobile App Development
- UX/UI Design
- Graphics & Branding
- Automation using n8n
- Full Digital Transformation Systems

Mission:
Transform ideas into powerful digital solutions through innovation, efficiency, and scalable technology.

Contact:
Website: www.alloftech.site
Email: contact.alloftech@gmail.com
Facebook: facebook.com/AllOfTech.official
Reddit: reddit.com/user/Rare-Philosophy387
Project Form: www.alloftech.site

Rules:
- Respond clearly and professionally.
- Never show <think> or hidden reasoning.
- Promote AllOfTech services where relevant.
"""

# ------------------------------
# Request schema
# ------------------------------
class ChatRequest(BaseModel):
    message: str

# ------------------------------
# Clean output
# ------------------------------
def clean_output(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

# ------------------------------
# Async OpenRouter request
# ------------------------------
async def ask_bot(user_message: str) -> str:
    loop = asyncio.get_event_loop()

    def sync_request():
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mistralai/devstral-2512:free",
            "messages": [
                {"role": "system", "content": AGENCY_SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 500
        }

        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        data = response.json()
        return data["choices"][0]["message"]["content"]

    return await loop.run_in_executor(None, sync_request)

# ------------------------------
# API endpoint
# ------------------------------
@app.post("/chat")
async def chat(request: ChatRequest):
    reply = await ask_bot(request.message)
    return {"reply": clean_output(reply)}

# ------------------------------
# Run server
# ------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
