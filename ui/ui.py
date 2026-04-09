from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import httpx
import os

app = FastAPI()

AGENT_API_URL = os.getenv("AGENT_API_URL", "http://agent-adapter:9000/query")

@app.get("/")
async def index():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agent UI</title>
        <style>
            body { font-family: sans-serif; max-width: 800px; margin: 50px auto; }
            textarea { width: 100%; height: 100px; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
            #response { margin-top: 20px; padding: 10px; background: #f5f5f5; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Hermes Agent</h1>
        <textarea id="prompt" placeholder="Écris ta question..."></textarea>
        <br><br>
        <button onclick="queryAgent()">Envoyer</button>
        <div id="response"></div>
        
        <script>
            async function queryAgent() {
                const prompt = document.getElementById('prompt').value;
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt, max_tokens: 200, temp: 0.7})
                });
                const data = await response.json();
                document.getElementById('response').textContent = data.response || 'Pas de réponse';
            }
        </script>
    </body>
    </html>
    """)

@app.post("/api/query")
async def query(data: dict):
    """Proxy les requêtes vers l'agent adapter"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            AGENT_API_URL,
            json=data,
            timeout=30
        )
        return response.json()
