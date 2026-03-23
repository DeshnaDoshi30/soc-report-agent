@echo off
REM Simple: Start Ollama
REM Just run: start_ollama.bat

echo.
echo ==========================================
echo Starting Ollama...
echo ==========================================
echo.

REM Check if Ollama is already running
tasklist | find /i "ollama" >nul
if %ERRORLEVEL% EQU 0 (
    echo Ollama is already running!
    echo.
    pause
    exit /b 0
)

REM Start Ollama
echo Starting Ollama service...
ollama serve

REM If it gets here, ollama failed
echo.
echo ERROR: Ollama did not start
echo Make sure Ollama is installed from https://ollama.ai
echo.
pause
exit /b 1
