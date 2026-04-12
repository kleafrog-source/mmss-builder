@echo off
echo Starting Optimizer with REAL GEPA (Mistral API)...
echo.
set MISTRAL_API_KEY=188W4mPcZuJC3Nu9TjuxscZyRvSmqLGq
cd /d "%~dp0services\optimizer"
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
pause
