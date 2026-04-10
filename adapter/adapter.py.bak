""" adapter.py — Adaptateur OpenAI-compatible pour llama.cpp
Expose /v1/chat/completions, /v1/models, /v1/completions
"""
import os
import json
import time
import uuid
import logging
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, AsyncIterator

# ─── Configuration ────────────────────────────────────────────────────────────
LLAMA_BASE_URL = os.getenv("LLAMA_URL", "http://llama-server:8080")
ADAPTER_PORT = int(os.getenv("ADAPTER_PORT", "9000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MODEL_NAME = os.getenv("MODEL_NAME", "hermes-3")

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger("openai-adapter")

# ─── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="OpenAI-Compatible Adapter",
    description="Adaptateur FastAPI pour exposer llama.cpp comme API OpenAI",
    version="1.0.0",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Pydantic Models ──────────────────────────────────────────────────────────
class Message(BaseModel):
    role: str  # "system" | "user" | "assistant"
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = MODEL_NAME
    messages: List[Message]
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(512, ge=1, le=32768)
    stream: Optional[bool] = False
    top_p: Optional[float] = Field(0.9, ge=0.0, le=1.0)
    stop: Optional[List[str]] = None

class CompletionRequest(BaseModel):
    model: str = MODEL_NAME
    prompt: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 512
    stream: Optional[bool] = False

# ─── Helper: messages → prompt (format ChatML pour Hermes-3) ─────────────────────
def messages_to_prompt(messages: List[Message]) -> str:
    """Convertit un tableau messages OpenAI en prompt texte pour llama.cpp."""
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

# ─── Helper: build llama.cpp payload ─────────────────────────────────────────
def build_llama_payload(
    prompt: str,
    temperature: float,
    max_tokens: int,
    top_p: float = 0.9,
    stop: Optional[List[str]] = None,
    stream: bool = False,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "prompt": prompt,
        "temperature": temperature,
        "n_predict": max_tokens,
        "top_p": top_p,
    "stream": stream,
}

# Streaming generator
async def stream_chat_chunks(
    prompt: str,
    req: ChatCompletionRequest,
) -> AsyncIterator[str]:
    """Génère des chunks SSE au format OpenAI depuis le stream llama.cpp."""
    payload = build_llama_payload(
        prompt=prompt,
        temperature=req.temperature,
        max_tokens=req.max_tokens,
        top_p=req.top_p,
        stop=req.stop,
        stream=True,
    )
    chunk_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    created = int(time.time())
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST", f"{LLAMA_BASE_URL}/completion", json=payload
            ) as resp:
                resp.raise_for_status()
                async for raw_line in resp.aiter_lines():
                    if not raw_line.startswith("data:"):
                        continue
                    data_str = raw_line[5:].strip()
                    if not data_str:
                        continue
                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
                    # Extraction du token (support llama.cpp et format OpenAI/LM Studio)
                    token = data.get("content", "")
                    is_last = data.get("stop", False)

                    if not token and "choices" in data:
                        choices = data.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            token = delta.get("content", "")
                            is_last = choices[0].get("finish_reason") is not None

                    if not token and not is_last:
                        continue

                    chunk = {
                        "id": chunk_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": req.model,
                        "choices": [{
                            "index": 0,
                            "delta": {"content": token} if token else {},
                            "finish_reason": "stop" if is_last else None,
                        }],
                    }
                    yield f"data: {json.dumps(chunk)}\n\n"
                    if is_last:
                        break
    except httpx.RequestError as e:
        log.error("Streaming error: %s", e)
        raise HTTPException(502, f"llama.cpp unreachable: {e}")
    yield "data: [DONE]\n\n"

# ─── Routes ───────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    """Health-check de l'adaptateur."""
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
    """Liste les modèles disponibles (format OpenAI)."""
    return {
        "object": "list",
        "data": [{
            "id": MODEL_NAME,
            "object": "model",
            "created": 1700000000,
            "owned_by": "local",
            "permission": [],
            "root": MODEL_NAME,
            "parent": None,
        }],
    }

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    """
    Endpoint OpenAI /v1/chat/completions.
    Supporte streaming et non-streaming.
    """
    prompt = messages_to_prompt(req.messages)
    log.info("Chat request | model=%s stream=%s msgs=%d", req.model, req.stream, len(req.messages))
    if req.stream:
        return StreamingResponse(
            stream_chat_chunks(prompt, req),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )
    # Non-streaming
    payload = build_llama_payload(
        prompt=prompt,
        temperature=req.temperature,
        max_tokens=req.max_tokens,
        top_p=req.top_p,
        stop=req.stop,
        stream=False,
    )
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{LLAMA_BASE_URL}/completion", json=payload)
            resp.raise_for_status()
    except httpx.RequestError as e:
        log.error("llama.cpp request error: %s", e)
        raise HTTPException(502, f"llama.cpp server unreachable: {e}")
    except httpx.HTTPStatusError as e:
        log.error("llama.cpp HTTP error %s: %s", e.response.status_code, e.response.text)
        raise HTTPException(e.response.status_code, e.response.text)
    data = resp.json()
    content = data.get("content", "").strip()
    log.info("Chat response | tokens_approx=%d", len(content.split()))
    return openai_chat_response(content, req.model)

@app.post("/v1/completions")
async def completions(req: CompletionRequest):
    """Endpoint OpenAI /v1/completions (text completion legacy)."""
    log.info("Completion request | model=%s stream=%s", req.model, req.stream)
    payload = build_llama_payload(
        prompt=req.prompt,
        temperature=req.temperature,
        max_tokens=req.max_tokens,
        stream=False,
    )
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{LLAMA_BASE_URL}/completion", json=payload)
            resp.raise_for_status()
    except httpx.RequestError as e:
        raise HTTPException(502, f"llama.cpp server unreachable: {e}")
    content = resp.json().get("content", "").strip()
    return {
        "id": f"cmpl-{uuid.uuid4().hex[:12]}",
        "object": "text_completion",
        "created": int(time.time()),
        "model": req.model,
        "choices": [{"text": content, "index": 0, "logprobs": None, "finish_reason": "stop"}],
    }

# ─── Legacy /query endpoint (compatibilité arrière) ──────────────────────────
class LegacyQueryRequest(BaseModel):
    prompt: str
    max_tokens: int = 512
    temp: float = 0.7

@app.post("/query")
async def legacy_query(request: Request):
    """Endpoint legacy /query — conservé pour compatibilité."""
    body = await request.json()
    prompt = body.get("prompt", "")
    log.warning("Legacy /query used — prefer /v1/chat/completions")
    payload = {
        "prompt": prompt,
        "n_predict": body.get("max_tokens", 512),
        "temperature": body.get("temp", 0.7),
        "stream": False,
    }
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{LLAMA_BASE_URL}/completion", json=payload)
            resp.raise_for_status()
    except httpx.RequestError as e:
        raise HTTPException(502, str(e))
    return {"response": resp.json().get("content", "").strip()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=ADAPTER_PORT)
