@echo off
cd /d "%~dp0services\prompt_manager"
set PROMPT_DATA_DIR=..\..\data\prompts
echo Starting Prompt Manager on port 8002...
python -m uvicorn src.api:app --host 0.0.0.0 --port 8002 --reload 2>&1 | tee ..\..\logs\prompt_manager.log
pause
