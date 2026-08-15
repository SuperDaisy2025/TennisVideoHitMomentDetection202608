$ErrorActionPreference = "Stop"
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$condaExe = Join-Path $env:USERPROFILE "miniforge3\Scripts\conda.exe"
$envDir = Join-Path $projectDir ".venv"
$venvPython = Join-Path $envDir "python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    if (-not (Test-Path -LiteralPath $condaExe)) {
        throw "Miniforge was not found at $condaExe"
    }
    & $condaExe create --prefix $envDir python=3.10 pip tk ffmpeg -y
} else {
    & $condaExe install --prefix $envDir tk ffmpeg -y
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r (Join-Path $projectDir "requirements.txt")
Write-Host "Setup completed. Run .\run.ps1 next."
