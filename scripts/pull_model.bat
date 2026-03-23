@echo off
REM Model Manager - Forensic Intelligence Loader
REM Usage: pull_model.bat model_name

if "%1"=="" (
    echo Usage: pull_model.bat model_name
    echo.
    echo Recommended for Laptop (8GB RAM):
    echo   pull_model.bat qwen2.5-coder:3b   (Current Master Model)
    echo   pull_model.bat mistral            (Fast, accurate)
    echo.
    echo Recommended for Office GPU (Ubuntu):
    echo   pull_model.bat llama3:8b          (Superior reasoning)
    echo   pull_model.bat dolphin-mixtral    (Complex analysis)
    exit /b 1
)

echo.
echo ==========================================
echo Pulling Forensic Intelligence: %1
echo ==========================================
echo.

ollama pull %1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ OK: %1 is vaulted and ready.
    echo Use in report.bat with: --model %1
) else (
    echo.
    echo ✗ ERROR: Failed to pull %1. Check internet connection.
)

echo.
pause