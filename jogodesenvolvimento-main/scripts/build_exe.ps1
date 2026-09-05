$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$entrypoint = Join-Path $repoRoot "game\python\joguinhoonline.py"
$fonts = Join-Path $repoRoot "game\python\fonts"
$assets = Join-Path $repoRoot "game\python\assets"

if (-not (Test-Path $python)) {
    Write-Host "Garantindo Python 3.12..."
    uv python install 3.12

    Write-Host "Criando ambiente virtual em .venv..."
    uv venv --python 3.12 (Join-Path $repoRoot ".venv")
}

Write-Host "Instalando dependencias..."
uv pip install --python $python -r (Join-Path $repoRoot "requirements.txt")

Write-Host "Gerando executavel..."
& $python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name "RLF" `
    --add-data "$fonts;fonts" `
    --add-data "$assets;assets" `
    --distpath (Join-Path $repoRoot "dist") `
    --workpath (Join-Path $repoRoot "build") `
    --specpath $repoRoot `
    $entrypoint

Write-Host ""
Write-Host "Pronto: dist\RLF.exe"
