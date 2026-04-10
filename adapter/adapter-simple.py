"""Simple adapter test"""
import os
import json
import time
import uuid
import logging
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Configuration
LLAMA_BASE_URL = os.getenv("LLAMA_URL", "http://llama-server:8080")
MODEL_NAME = os.getenv("MODEL_NAME", "hermes-3")

# Logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("adapter")

# FastAPI
app = FastAPI(title="Hermes Adapter", version="1.0.0")

# Models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = MODEL_NAME
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 512

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "llama_url": LLAMA_BASE_URL}

# Models list
@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [{"id": MODEL_NAME, "object": "model", "owned_by": "local"}]
    }

# Chat completions
@app.post("/v1/chat/completions")
async def chat(req: ChatRequest):
    log.info(f"Chat request: {len(req.messages)} messages")
    
    # Convert messages to prompt
    prompt_parts = []
    for msg in req.messages:
        if msg.role == "system":
            prompt_parts.append(f"System: {msg.content}")
        elif msg.role == "user":
            prompt_parts.append(f"User: {msg.content}")
        elif msg.role == "assistant":
            prompt_parts.append(f"Assistant: {msg.content}")
    prompt_parts.append("Assistant:")
    prompt = "\n".join(prompt_parts)
    
    # Build payload
    payload = {
        "prompt": prompt,
        "temperature": req.temperature,
        "n_predict": req.max_tokens,
        "stream": False
    }
    
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{LLAMA_BASE_URL}/completion", json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data.get("content", "").strip()
    except Exception as e:
        log.error(f"Error: {e}")
        raise HTTPException(502, f"llama.cpp error: {e}")
    
    token_count = len(content.split())
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": req.model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": -1,
            "completion_tokens": token_count,
            "total_tokens": token_count
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
