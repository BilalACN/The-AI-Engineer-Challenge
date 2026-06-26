from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

SYSTEM_PROMPT = (
    "You are a supportive mental coach. Help users with stress, motivation, "
    "habits, and confidence. Be empathetic, encouraging, and practical."
)

APIM_ENDPOINT = "https://lgts1tetamapi01.azure-api.net/gpt51/openai/responses"


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat")
def chat(request: ChatRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                APIM_ENDPOINT,
                params={"subscription-key": api_key},
                json={
                    "model": "gpt-5.1",
                    "input": request.message,
                    "instructions": SYSTEM_PROMPT,
                },
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()

        reply = data["output"][0]["content"][0]["text"]
        return {"reply": reply}

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=500, detail=f"API error: {e.response.text}")
    except (KeyError, IndexError) as e:
        raise HTTPException(status_code=500, detail=f"Unexpected response format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
