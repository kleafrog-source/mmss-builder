@echo off
cd /d "%~dp0services\optimizer"
echo Starting Optimizer Service on port 8000...
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
pause
