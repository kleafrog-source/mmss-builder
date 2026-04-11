@echo off
echo ========================================
echo Launching GEPA-Pezzo-MMSS Services
echo ========================================
echo.
echo Opening Optimizer Service in new window...
start "Optimizer Service :8000" cmd /k "cd /d %~dp0services\optimizer && echo Starting Optimizer on port 8000... && python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 2 /nobreak >nul

echo Opening MMSS Service in new window...
start "MMSS Service :8001" cmd /k "cd /d %~dp0services\mmss && echo Starting MMSS on port 8001... && python -m uvicorn src.api:app --host 0.0.0.0 --port 8001 --reload"

timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo Services launched!
echo ========================================
echo.
echo Wait 10 seconds for services to start...
timeout /t 10 /nobreak >nul

echo Running API test...
python %~dp0test_api_only.py

echo.
echo Press any key to exit...
pause >nul
