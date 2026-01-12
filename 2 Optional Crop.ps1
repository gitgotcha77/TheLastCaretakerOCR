
. (Join-Path $PSScriptRoot "config.ps1")

Write-Host ""
Write-Host "Activating Python virtual environment" -ForegroundColor Yellow
& $sVenvActivate
Write-Host "done" -ForegroundColor Green

Write-Host ""
Write-Host "Cropping video ..." -ForegroundColor Yellow

$sCropScript = Join-Path $sProjectDir "create_cropped.py"

# script call
& $sVenvPython $sCropScript

Write-Host "Cropping video done!" -ForegroundColor Green
Write-Host ""
