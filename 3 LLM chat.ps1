
. (Join-Path $PSScriptRoot "config.ps1")

Write-Host ""
Write-Host "Activating Python virtual environment" -ForegroundColor Yellow
& $sVenvActivate
Write-Host "done" -ForegroundColor Green

Write-Host ""
Write-Host "Starting LLM chat ..." -ForegroundColor Yellow

& $sVenvPython $sLlmScript

Write-Host ""
