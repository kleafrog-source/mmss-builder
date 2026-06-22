@echo off
echo Starting Optimizer with REAL GEPA (Mistral API)...
echo.
if not defined MISTRAL_API_KEY (
    echo [WARN] MISTRAL_API_KEY is not set. Copy .env.example to .env and set your key.
)
cd /d "%~dp0services\optimizer"
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
pause
