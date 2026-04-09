""" adapter-fixed.py - Version corrigée avec calcul de tokens correct """
import os
import json
import time
import uuid
import logging
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Configuration
LLAMA_BASE_URL = os.getenv("LLAMA_URL", "http://llama-server:8080")
ADAPTER_PORT = int(os.getenv("ADAPTER_PORT", "9000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MODEL_NAME = os.getenv("MODEL_NAME", "hermes-3")

# Logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger("openai-adapter")

# FastAPI App
app = FastAPI(title="OpenAI-Compatible Adapter (Fixed)", version="1.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = MODEL_NAME
    messages: List[Message]
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(512, ge=1, le=32768)
    stream: Optional[bool] = False
    top_p: Optional[float] = Field(0.9, ge=0.0, le=1.0)
    stop: Optional[List[str]] = None

# Helper: estimate tokens (approximate: 1 token ~ 4 chars)
def estimate_tokens(text: str) -> int:
    """Estimate tokens using simple character-based approximation."""
    return max(1, len(text) // 4)

# Helper: messages to prompt
def messages_to_prompt(messages: List[Message]) -> str:
    """Convert OpenAI messages to llama.cpp prompt."""
    parts = []
    for msg in messages:
        if msg.role == "system":
            parts.append(f"<|im_start|>system\n{msg.content}<|im_end|>")
        elif msg.role == "user":
            parts.append(f"<|im_start|>user\n{msg.content}<|im_end|>")
        elif msg.role == "assistant":
            parts.append(f"<|im_start|>assistant\n{msg.content}<|im_end|>")
    parts.append("<|im_start|>assistant\n")
    return "\n".join(parts)

# Helper: build llama payload
def build_llama_payload(prompt: str, temperature: float, max_tokens: int, top_p: float = 0.9) -> Dict[str, Any]:
    return {
        "prompt": prompt,
        "temperature": temperature,
        "n_predict": max_tokens,
        "top_p": top_p,
        "stream": False,
        "cache_prompt": True,
        "stop": ["<|im_end|>", "</s>"],
    }

# Helper: wrap response in OpenAI format
def openai_chat_response(content: str, model: str, prompt_text: str) -> Dict:
    """Wrap response with correct token calculation."""
    completion_tokens = estimate_tokens(content)
    prompt_tokens = estimate_tokens(prompt_text)
    total_tokens = prompt_tokens + completion_tokens
    
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop",
        }],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        },
    }

# Routes
@app.get("/health")
async def health():
    """Health check."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{LLAMA_BASE_URL}/health")
            llama_ok = r.status_code == 200
    except Exception:
        llama_ok = False
    return {
        "status": "ok",
        "llama_server": "reachable" if llama_ok else "unreachable",
        "llama_url": LLAMA_BASE_URL,
    }

@app.get("/v1/models")
async def list_models():
    """List available models."""
    return {
        "object": "list",
        "data": [{
            "id": MODEL_NAME,
            "object": "model",
            "created": 1700000000,
            "owned_by": "local",
            "permission": [],
        }],
    }

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    """Chat completions endpoint with correct token counting."""
    try:
        # Convert messages to prompt
        prompt = messages_to_prompt(req.messages)
        
        # Build llama payload
        payload = build_llama_payload(
            prompt=prompt,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            top_p=req.top_p,
        )
        
        # Call llama.cpp
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(f"{LLAMA_BASE_URL}/completion", json=payload)
            response.raise_for_status()
            llama_result = response.json()
        
        # Extract content
        content = llama_result.get("content", "")
        
        # Return OpenAI format with correct tokens
        return openai_chat_response(content, req.model, prompt)
        
    except httpx.RequestError as e:
        log.error("Request error: %s", e)
        raise HTTPException(502, f"llama.cpp unreachable: {e}")
    except Exception as e:
        log.error("Unexpected error: %s", e)
        raise HTTPException(500, f"Internal server error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=ADAPTER_PORT)
