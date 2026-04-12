@echo off
echo ========================================
echo Batch Optimize MMSS Prompts
echo ========================================
echo.
echo Usage: batch_optimize.bat ^<folder^> [population] [iterations]
echo Example: batch_optimize.bat extract\prompt-db-local\database 10 20
echo.

if "%~1"=="" (
    echo ❌ Error: No folder specified
    echo.
    echo Usage: batch_optimize.bat ^<folder^>
    exit /b 1
)

set FOLDER=%~1
set POPULATION=%~2
if "%POPULATION%"=="" set POPULATION=10

set ITERATIONS=%~3
if "%ITERATIONS%"=="" set ITERATIONS=20

echo 📁 Folder: %FOLDER%
echo ⚙️  Population: %POPULATION%
echo ⚙️  Iterations: %ITERATIONS%
echo.

cd /d "%~dp0.."
python examples\batch_optimize.py "%FOLDER%" --population %POPULATION% --iterations %ITERATIONS%

echo.
pause
