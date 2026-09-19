$ErrorActionPreference = "Stop"

$backendDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$coversDirectory = Join-Path $backendDirectory "static\book-covers"
$placeholderPath = Join-Path $coversDirectory "placeholder_book_cover.jpeg"
$defaultPlaceholderPath = Join-Path $backendDirectory "default-covers\placeholder_book_cover.jpeg"

New-Item -ItemType Directory -Force -Path $coversDirectory | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $backendDirectory "instance") | Out-Null

if (-not (Test-Path $placeholderPath) -and (Test-Path $defaultPlaceholderPath)) {
    Copy-Item $defaultPlaceholderPath $placeholderPath
}

Set-Location $backendDirectory
$venvPython = Join-Path $backendDirectory ".venv\Scripts\python.exe"
$pythonCommand = if (Test-Path $venvPython) { $venvPython } else { "python" }

& $pythonCommand .\app.py