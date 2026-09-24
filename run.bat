@echo off
echo =======================================================
echo   MimicLLM - Zero-GPU Modern LLM Simulator
echo   100%% Deterministic, Zero Neural Weights, Zero GPUs
echo =======================================================
echo.
echo Starting FastAPI Web Server at http://127.0.0.1:8000 ...
uv run uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause
