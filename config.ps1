$sVideoFile   = "TLC_DataLogs_1080.mkv"
$sVideoHeight = 1080
$sVideoFps    = 1

$sProjectDir = $PSScriptRoot

$sPythonDir  = Join-Path $sProjectDir "python"
$sFfmpegDir  = Join-Path $sProjectDir "ffmpeg"
$sVenvDir    = Join-Path $sProjectDir ".venv"

$sPythonVrs  = "3.13.11"
$sPythonUrl  = "https://www.python.org/ftp/python/${sPythonVrs}/python-${sPythonVrs}-embed-amd64.zip"

$sPythonExe    = Join-Path $sPythonDir "python.exe"
$sPipModule    = Join-Path $sPythonDir "Scripts\pip.exe"
$sVenvActivate = Join-Path $sVenvDir "Scripts\Activate.ps1"
$sVenvPython   = Join-Path $sVenvDir "Scripts\python.exe"

$sPipReqFile = Join-Path $sProjectDir "requirements.txt"
$sOcrScript  = Join-Path $sProjectDir "ocr_local.py"
$sLlmScript  = Join-Path $sProjectDir "llm_chat.py"

$sFfmpegUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
