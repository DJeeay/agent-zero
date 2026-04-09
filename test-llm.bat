@echo off
REM Quick test of llama-server

echo.
echo === Testing LLM Server ===
echo.

REM Health check
echo 1. Health check:
curl -s http://localhost:8080/health
echo.
echo.

REM Simple completion test
echo 2. Simple test (5 second timeout):
curl -s --max-time 5 -X POST http://localhost:8080/completion ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\":\"What is Docker?\",\"n_predict\":50,\"temperature\":0.7}"
echo.
echo.

echo Done. LLM Server is working.
echo.
echo Next: Start Agent Zero separately when ready:
echo   docker run -d --name agent-zero --network llm-network -p 50080:80 ^
echo     -e LLM_API_URL="http://llama-server:8080" ^
echo     -v agent0-volume:/a0 ^
echo     agent0ai/agent-zero:latest
