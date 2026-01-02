
. (Join-Path $PSScriptRoot "config.ps1")

Write-Host ""
Write-Host "Activating Python virtual environment" -ForegroundColor Yellow
& $sVenvActivate
Write-Host "done" -ForegroundColor Green

Write-Host ""
Write-Host "Local LLM chat ..." -ForegroundColor Yellow

& $sVenvPython $sLlmScript --textFile "${sVideoFile}.ocr.txt" --provider openai --modelName "openai/gpt-oss-20b" --apiUrl http://localhost:1234/v1

Write-Host ""
