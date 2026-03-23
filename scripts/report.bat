@echo off
REM Universal Entry Point - Forensic Vault Edition
REM Usage: report.bat input_file [--insight "Your findings"] [--model model_name]

setlocal

if "%~1"=="" goto usage

if not exist "%~1" (
    echo Error: File not found: "%~1" 
    exit /b 1
)

echo.
echo ==========================================
echo SOC AGENT: FORENSIC PIPELINE (v2026)
echo ==========================================
echo.

REM --- AUTOMATIC VENV ACTIVATION ---
if exist "..\.venv\Scripts\activate.bat" (
    echo [System] Activating Virtual Environment...
    call "..\.venv\Scripts\activate.bat"
) else (
    echo [Warning] Virtual environment (.venv) not found. Using global Python.
)

REM Pass all arguments to pipeline.py to support --insight and --model
python "..\src\pipeline.py" %*

echo.
echo Pipeline Complete.
echo ------------------------------------------
echo Check "data\output\" for synchronized Run ID files.
echo ------------------------------------------
echo.
pause
goto :eof

:usage
echo Usage: report.bat input_file [--insight "Text"] [--model name]
exit /b 1