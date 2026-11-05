@echo off
title Formula 1 Full-Stack Platform Launcher (Backend API + Frontend UI)
echo =====================================================================
echo    STARTING FORMULA 1 FULL-STACK PLATFORM (BACKEND + FRONTEND)
echo =====================================================================
echo.
cd /d "G:\DAV\F1_Race_Strategy_Dashboard"

set PYTHON_EXE=G:\DAV\.venv\Scripts\python.exe
set STREAMLIT_EXE=G:\DAV\.venv\Scripts\streamlit.exe

if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python
    set STREAMLIT_EXE=streamlit
)

echo [1/2] Launching FastAPI Backend Server on http://localhost:8000 ...
start "F1 Backend API (Port 8000)" "%PYTHON_EXE%" -m uvicorn api_server:app --host 0.0.0.0 --port 8000

echo [2/2] Launching Streamlit Frontend Dashboard on http://localhost:8501 ...
start "F1 Frontend UI (Port 8501)" "%STREAMLIT_EXE%" run app.py --server.port 8501 --client.toolbarMode minimal --client.showSidebarNavigation false

echo.
echo =====================================================================
echo   SUCCESS! BOTH SERVICES ARE NOW ACTIVE:
echo.
echo   * Backend REST API:        http://localhost:8000
echo   * Swagger API Docs:        http://localhost:8000/docs
echo   * Frontend UI Dashboard:   http://localhost:8501
echo =====================================================================
echo.
pause
