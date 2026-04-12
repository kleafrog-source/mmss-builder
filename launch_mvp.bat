@echo off
echo ========================================
echo Launching GEPA-Pezzo-MMSS MVP
echo ========================================
echo.
echo This will start:
echo   - Optimizer Service on port 8000
echo   - MMSS Service on port 8001
echo   - Prompt Manager (UI) on port 8002
echo.
echo Press any key to start...
pause >nul

echo.
echo Starting Optimizer Service...
start "Optimizer :8000" cmd /k "cd /d %~dp0services\optimizer && python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 2 /nobreak >nul

echo Starting MMSS Service...
start "MMSS :8001" cmd /k "cd /d %~dp0services\mmss && python -m uvicorn src.api:app --host 0.0.0.0 --port 8001 --reload"

timeout /t 2 /nobreak >nul

echo Starting Prompt Manager (UI)...
start "Prompt Manager :8002" cmd /k "cd /d %~dp0services\prompt_manager && set PROMPT_DATA_DIR=..\..\data\prompts && python -m uvicorn src.api:app --host 0.0.0.0 --port 8002 --reload"

timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo Services started!
echo ========================================
echo.
echo Web UI: http://localhost:8002
echo.
echo Opening browser...
start http://localhost:8002

echo.
echo Press any key to exit this window...
pause >nul
