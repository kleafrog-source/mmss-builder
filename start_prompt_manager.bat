@echo off
cd /d "%~dp0services\prompt_manager"
echo Starting Prompt Manager on port 8002...
echo.
echo Web UI will be available at: http://localhost:8002
echo.
python -m uvicorn src.api:app --host 0.0.0.0 --port 8002 --reload
pause
