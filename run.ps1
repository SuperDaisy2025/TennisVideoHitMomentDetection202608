$ErrorActionPreference = "Stop"
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $projectDir ".venv\python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Python environment not found. Run setup.ps1 first."
}

Push-Location $projectDir
try {
    & $venvPython "tennis_analyzer.py"
}
finally {
    Pop-Location
}
