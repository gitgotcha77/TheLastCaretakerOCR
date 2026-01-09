
. (Join-Path $PSScriptRoot "config.ps1")


function Download-File
{
    param (
        [string]$sUrl,
        [string]$sOutputPath
    )
    
    try
    {
        Write-Host "Downloading from: ${sUrl}" -ForegroundColor Yellow
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($sUrl, $sOutputPath)
        Write-Host "Download complete: ${sOutputPath}" -ForegroundColor Green
        return $true
    }
    catch
    {
        Write-Host "Download failed: $_" -ForegroundColor Red
        return $false
    }
}


Write-Host ""
Write-Host "=============" -ForegroundColor Cyan
Write-Host "Project Setup" -ForegroundColor Cyan
Write-Host "=============" -ForegroundColor Cyan

Write-Host ""
Write-Host "[1/4] Setting up Python ${sPythonVrs} ..." -ForegroundColor Cyan
if (Test-Path $sPythonDir)
{
    Write-Host "Python directory already exists. Skipping download." -ForegroundColor Yellow
}
else
{
    $pythonZip = Join-Path $sProjectDir "python.zip"
    
    if (Download-File -sUrl $sPythonUrl -sOutputPath $pythonZip)
    {
        Write-Host "Extracting Python ${sPythonVrs} into ${sPythonDir} ..." -ForegroundColor Yellow
        Expand-Archive -Path $pythonZip -DestinationPath $sPythonDir -Force
        Remove-Item $pythonZip
        
        $sPthFile = Get-ChildItem -Path $sPythonDir -Filter "*._pth" | Select-Object -First 1
        if ($sPthFile)
        {
            $sContent = Get-Content $sPthFile.FullName
            $sContent = $sContent -replace "#import site", "import site"
            $sContent | Set-Content $sPthFile.FullName
            Write-Host "Python ${sPythonVrs} setup complete" -ForegroundColor Green
        }
    }
    else
    {
        Write-Host "Failed to download Python. Exiting." -ForegroundColor Red
        exit 1
    }
}


Write-Host ""
Write-Host "[2/4] Installing UV ..." -ForegroundColor Cyan

if (-not (Test-Path $sPipModule))
{
    Write-Host "Installing pip first ..." -ForegroundColor Yellow
    $sGetPipScript = Join-Path $sProjectDir "get-pip.py"
    Download-File -sUrl "https://bootstrap.pypa.io/get-pip.py" -sOutputPath $sGetPipScript
    & $sPythonExe $sGetPipScript
    Remove-Item $sGetPipScript
}


try
{
    Write-Host "Installing UV package manager ..." -ForegroundColor Yellow
    & $sPythonExe -m pip install uv --quiet
    Write-Host "UV installed successfully" -ForegroundColor Green
}
catch
{
    Write-Host "Failed to install UV: $_" -ForegroundColor Red
    exit 2
}


Write-Host ""
Write-Host "[3/4] Installing Python packages with UV ..." -ForegroundColor Cyan

if (-not (Test-Path $sVenvDir))
{
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    & $sPythonExe -m uv venv $sVenvDir
}

Write-Host "Installing packages from requirements.txt ..." -ForegroundColor Yellow
$venvPython = Join-Path $sVenvDir "Scripts\python.exe"
& $sPythonExe -m uv pip install -r $sPipReqFile --python $venvPython

if ($LASTEXITCODE -eq 0)
{
    Write-Host "All packages installed successfully" -ForegroundColor Green
}
else
{
    Write-Host "Failed to install some packages" -ForegroundColor Red
    exit 3
}


Write-Host ""
Write-Host "[4/4] Setting up FFMPEG ..." -ForegroundColor Cyan

if (Test-Path $sFfmpegDir)
{
    Write-Host "FFMPEG directory already exists. Skipping download." -ForegroundColor Yellow
}
else
{
    $sFfmpegZip = Join-Path $sProjectDir "ffmpeg.zip"
    
    if (Download-File -sUrl $sFfmpegUrl -sOutputPath $sFfmpegZip)
    {
        Write-Host "Extracting FFMPEG into ${sFfmpegDir} ..." -ForegroundColor Yellow
        Expand-Archive -Path $sFfmpegZip -DestinationPath $sProjectDir -Force
        
        $obExtractedFolder = Get-ChildItem -Path $sProjectDir -Directory | Where-Object { $_.Name -like "ffmpeg-*" } | Select-Object -First 1
        if ($obExtractedFolder)
        {
            Move-Item $obExtractedFolder.FullName $sFfmpegDir -Force
        }
        
        Remove-Item $sFfmpegZip
        Write-Host "FFMPEG setup complete" -ForegroundColor Green
    }
    else
    {
        Write-Host "Failed to download FFMPEG" -ForegroundColor Red
    }
}


Write-Host ""
Write-Host "===============" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "===============" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project structure:" -ForegroundColor White
Write-Host "  - Python: ${sPythonDir} (${sPythonVrs})" -ForegroundColor Gray
Write-Host "  - VENV  : ${sVenvDir}" -ForegroundColor Gray
Write-Host "  - FFMPEG: ${sFfmpegDir}" -ForegroundColor Gray

Write-Host ""
Write-Host "Frames extraction and OCR process: '2 Run OCR.ps1'" -ForegroundColor Green

Write-Host ""
Write-Host "THEN" -ForegroundColor Yellow
Write-Host ""
Write-Host "Chat with an LLM: '3 LLM chat.ps1'" -ForegroundColor Green
Write-Host ""
Write-Host "For more details check README.md"

Write-Host ""
