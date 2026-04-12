@echo off
echo ========================================
echo Launch ALL Services (LOCAL with REAL GEPA)
echo ========================================
echo.
echo This will start:
echo   - Optimizer (:8000) with Mistral API
echo   - Prompt Manager (:8002)
echo.
echo Press any key to start...
pause >nul

:: Kill existing python processes
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

:: Set Mistral API Key and Data Dir (absolute path)
set MISTRAL_API_KEY=188W4mPcZuJC3Nu9TjuxscZyRvSmqLGq
set PROMPT_DATA_DIR=%~dp0data\prompts

echo.
echo [1/2] Starting Optimizer Service with REAL GEPA...
start "Optimizer :8000 (REAL GEPA)" cmd /k "cd /d %~dp0services\optimizer && python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Prompt Manager...
start "Prompt Manager :8002" cmd /k "cd /d %~dp0services\prompt_manager && set PROMPT_DATA_DIR=%~dp0data\prompts && set OPTIMIZER_URL=http://localhost:8000 && python -m uvicorn src.api:app --host 0.0.0.0 --port 8002 --reload"

timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo Check health:
echo   curl http://localhost:8000/health
echo   curl http://localhost:8002/health
echo.
echo Open UI:
echo   start http://localhost:8002
echo.
echo Press any key to exit this window...
pause >nul
