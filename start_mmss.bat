@echo off
cd /d "%~dp0services\mmss"
echo Starting MMSS Service on port 8001...
python -m uvicorn src.api:app --host 0.0.0.0 --port 8001 --reload
pause
