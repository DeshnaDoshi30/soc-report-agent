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
REM %~dp0 refers to the directory where this batch file is located.
if exist "%~dp0..\.venv\Scripts\activate.bat" (
    echo [System] Activating Virtual Environment...
    call "%~dp0..\.venv\Scripts\activate.bat"
) else (
    echo [Warning] .venv not found at %~dp0..\.venv. Using global Python.
)

REM Execute the pipeline using absolute pathing
python "%~dp0..\src\pipeline.py" %*

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