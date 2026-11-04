# Formula 1 Race Strategy & Telemetry Analytics Platform Launcher
Write-Host "=====================================================================" -ForegroundColor Red
Write-Host "   STARTING FORMULA 1 RACE STRATEGY & TELEMETRY PLATFORM" -ForegroundColor White
Write-Host "=====================================================================" -ForegroundColor Red

Set-Location -Path "G:\DAV\F1_Race_Strategy_Dashboard"

$VenvStreamlit = "G:\DAV\.venv\Scripts\streamlit.exe"
$LocalStreamlit = ".\.venv\Scripts\streamlit.exe"

if (Test-Path $VenvStreamlit) {
    Write-Host "Launching via G:\DAV\.venv..." -ForegroundColor Green
    & $VenvStreamlit run app.py
} elseif (Test-Path $LocalStreamlit) {
    Write-Host "Launching via local .venv..." -ForegroundColor Green
    & $LocalStreamlit run app.py
} else {
    Write-Host "Launching via system streamlit..." -ForegroundColor Yellow
    streamlit run app.py
}
