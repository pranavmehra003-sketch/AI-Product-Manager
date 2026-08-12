@echo off
REM ============================================================
REM   AI Product Manager — One-Click Launcher
REM   Double-click this file to start the app anytime.
REM ============================================================
setlocal

cd /d "%~dp0"

REM --- Which Python to use (the one that has streamlit installed
set PYTHON_EXE=C:\Users\prana\AppData\Local\Programs\Python\Python310\python.exe

REM --- Fallback 1: Try venv in project (if you set one up later)
if not exist "%PYTHON_EXE%" set PYTHON_EXE=%~dp0.venv\Scripts\python.exe

REM --- Fallback 2: Use whatever `py` launcher points to
if not exist "%PYTHON_EXE%" set PYTHON_EXE=py -3.10

echo.
echo [AI Product Manager] Starting up...
echo [AI Product Manager] Using Python: %PYTHON_EXE%
echo [AI Product Manager] Tip: keep this window open while using the app.
echo [AI Product Manager] Close it (or press Ctrl+C here when you're done)
echo.

"%PYTHON_EXE%" run.py

REM --- If it crashed instead of `python -m streamlit directly, uncomment the following:
REM "%PYTHON_EXE%" -m streamlit run ui\app.py --server.headless false --browser.gatherUsageStats false

echo.
echo [AI Product Manager] Server stopped. Press any key to close...
pause >nul
endlocal
