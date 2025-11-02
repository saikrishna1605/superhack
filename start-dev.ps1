# PulseOps Local Development Startup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting PulseOps Local Development" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start Backend API
Write-Host "Starting Backend API..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location 'd:\SuperOps-Hackathon\pulseops\services\api'; Write-Host 'Backend API Starting on http://localhost:8000' -ForegroundColor Green; python -m uvicorn main:app --reload --port 8000"
)

Start-Sleep -Seconds 5

# Start Frontend UI
Write-Host "Starting Frontend UI..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location 'd:\SuperOps-Hackathon\pulseops\services\ui'; `$env:BROWSER='none'; Write-Host 'Frontend UI Starting on http://localhost:3000' -ForegroundColor Green; Write-Host 'Please wait 60 seconds for compilation...' -ForegroundColor Yellow; npm start"
)

Write-Host ""
Write-Host "Waiting for servers to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 45

# Open Browser
Write-Host "Opening browser..." -ForegroundColor Yellow
Start-Process chrome "http://localhost:3000"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ PulseOps Servers Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "Frontend UI: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Login Credentials:" -ForegroundColor Yellow
Write-Host "  Email:    it@pulseops.com" -ForegroundColor White
Write-Host "  Password: itadmin123" -ForegroundColor White
Write-Host ""
Write-Host "Note: React may take 30-60 seconds to compile on first start" -ForegroundColor Cyan
Write-Host "      The browser will show 'connecting' until compilation completes" -ForegroundColor Cyan
Write-Host ""
