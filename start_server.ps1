Write-Host ""
Write-Host "========================================"
Write-Host "  GT SNIPER - Multi-Broker System"
Write-Host "========================================"
Write-Host ""

# Encontrar Python
$pythonCmd = $null

if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
    Write-Host "[OK] Python encontrado"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
    Write-Host "[OK] Python3 encontrado"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
    Write-Host "[OK] Py launcher encontrado"
} else {
    Write-Host "[ERRO] Python não encontrado!"
    Write-Host ""
    Write-Host "Por favor instale Python 3.11+ de:"
    Write-Host "https://www.python.org/downloads/"
    Write-Host ""
    Write-Host "Ou instale via Microsoft Store"
    Read-Host "Pressione ENTER para sair"
    exit 1
}

Write-Host ""
Write-Host "Iniciando servidor..."
Write-Host ""

# Ir para diretório correto
Set-Location -Path $PSScriptRoot

# Executar main.py
& $pythonCmd main.py

# Se houver erro
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERRO] Servidor falhou ao iniciar"
    Read-Host "Pressione ENTER para sair"
}
