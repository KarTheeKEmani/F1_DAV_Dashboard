@echo off
title Formula 1 Race Strategy & Telemetry Analytics Platform
echo =====================================================================
echo    STARTING FORMULA 1 RACE STRATEGY & TELEMETRY PLATFORM
echo =====================================================================
echo.
cd /d "G:\DAV\F1_Race_Strategy_Dashboard"

if exist "..\.venv\Scripts\streamlit.exe" (
    echo Using virtual environment at G:\DAV\.venv...
    "..\.venv\Scripts\streamlit.exe" run app.py
) else if exist ".venv\Scripts\streamlit.exe" (
    echo Using local virtual environment...
    ".venv\Scripts\streamlit.exe" run app.py
) else (
    echo Using system Python Streamlit...
    streamlit run app.py
)
pause
