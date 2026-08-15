$ErrorActionPreference = "Stop"
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $projectDir ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw ".venv がありません。先に .\setup.ps1 を実行してください。"
}

Push-Location $projectDir
try {
    & $venvPython "tennis_analyzer.py"
}
finally {
    Pop-Location
}
