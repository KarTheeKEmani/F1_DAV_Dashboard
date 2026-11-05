@echo off
title Formula 1 Race Telemetry & Strategy Analytics Platform
echo ============================================================================
echo   Starting Formula 1 Race Telemetry ^& Strategy Analytics Platform
echo   - 14 Kaggle F1 Race Analytics Repositories (1950-2026)
echo   - Clean Motorsport UI (No Deploy Button, Year/Team/Driver Filters)
echo ============================================================================

cd /d "G:\DAV\F1_Race_Strategy_Dashboard"

echo [1/2] Launching FastAPI Backend Server on http://localhost:8000 ...
start "F1 FastAPI Backend" "G:\DAV\.venv\Scripts\python.exe" -m uvicorn api_server:app --host 0.0.0.0 --port 8000

echo [2/2] Launching Streamlit Frontend Dashboard on http://localhost:8501 ...
"G:\DAV\.venv\Scripts\streamlit.exe" run "app.py" --server.port 8501 --client.toolbarMode minimal --client.showSidebarNavigation false

