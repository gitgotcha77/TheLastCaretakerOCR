
. (Join-Path $PSScriptRoot "config.ps1")

Write-Host ""
Write-Host "Activating Python virtual environment" -ForegroundColor Yellow
& $sVenvActivate
Write-Host "done" -ForegroundColor Green

Write-Host ""
Write-Host "OCR process ..." -ForegroundColor Yellow

# OCR script call
& $sVenvPython $sOcrScript

Write-Host "OCR done!" -ForegroundColor Green

Write-Host ""
Write-Host "Folder 'frames' contains all video frames as JPEG files." -ForegroundColor Green
Write-Host ""
Write-Host "OCR transcribe file: ${sVideoFile}.ocr.txt" -ForegroundColor Green
Write-Host ""
