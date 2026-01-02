
. (Join-Path $PSScriptRoot "config.ps1")

Write-Host ""
Write-Host "Activating Python virtual environment" -ForegroundColor Yellow
& $sVenvActivate
Write-Host "done" -ForegroundColor Green

Write-Host ""
Write-Host "Online LLM chat, DE prompt template ..." -ForegroundColor Yellow

& $sVenvPython $sLlmScript --textFile "${sVideoFile}.ocr.txt" --template de

Write-Host ""
