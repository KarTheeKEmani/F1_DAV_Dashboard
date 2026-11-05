# Formula 1 Dual Service Launcher: Backend (FastAPI) + Frontend (Streamlit)
Write-Host "=====================================================================" -ForegroundColor Red
Write-Host "   STARTING FORMULA 1 FULL-STACK PLATFORM (BACKEND + FRONTEND)" -ForegroundColor White
Write-Host "=====================================================================" -ForegroundColor Red

Set-Location -Path "G:\DAV\F1_Race_Strategy_Dashboard"

$PythonExe = "G:\DAV\.venv\Scripts\python.exe"
$StreamlitExe = "G:\DAV\.venv\Scripts\streamlit.exe"

if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
    $StreamlitExe = "streamlit"
}

Write-Host "`n[1/2] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Cyan
Start-Process -FilePath $PythonExe -ArgumentList "-m uvicorn api_server:app --host 0.0.0.0 --port 8000"

Write-Host "[2/2] Starting Streamlit Frontend on http://localhost:8501..." -ForegroundColor Green
Start-Process -FilePath $StreamlitExe -ArgumentList "run app.py --server.port 8501 --client.toolbarMode minimal --client.showSidebarNavigation false"

Write-Host "`n=====================================================================" -ForegroundColor Red
Write-Host "   SERVICES ACTIVE:" -ForegroundColor White
Write-Host "   * Backend API:        http://localhost:8000" -ForegroundColor Cyan
Write-Host "   * Swagger API Docs:   http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   * Frontend Dashboard: http://localhost:8501" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Red
