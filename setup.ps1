# UC Catalog Scraper - Setup Script para PowerShell
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   UC CATALOG SCRAPER - INSTALACION" -ForegroundColor Cyan  
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si estamos en un entorno virtual
$inVenv = $false
if ($env:VIRTUAL_ENV) {
    Write-Host "[INFO] Entorno virtual activo: $env:VIRTUAL_ENV" -ForegroundColor Green
    $inVenv = $true
} elseif ($env:CONDA_DEFAULT_ENV) {
    Write-Host "[INFO] Entorno Conda activo: $env:CONDA_DEFAULT_ENV" -ForegroundColor Green
    $inVenv = $true
} else {
    # Buscar entornos virtuales locales
    $venvDirs = @(".venv", "venv", "env")
    $foundVenv = $null
    
    foreach ($dir in $venvDirs) {
        $activateScript = Join-Path $dir "Scripts\Activate.ps1"
        if (Test-Path $activateScript) {
            Write-Host "[INFO] Encontrado entorno virtual: $dir" -ForegroundColor Yellow
            $foundVenv = $dir
            break
        }
    }
    
    if ($foundVenv) {
        Write-Host "[ACCION] Activando entorno virtual: $foundVenv" -ForegroundColor Blue
        & "$foundVenv\Scripts\Activate.ps1"
        $inVenv = $true
    } else {
        Write-Host "[ACCION] Creando nuevo entorno virtual: .venv" -ForegroundColor Blue
        python -m venv .venv
        & ".venv\Scripts\Activate.ps1"
        $inVenv = $true
    }
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "       INSTALANDO DEPENDENCIAS" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python no esta instalado o no esta en PATH" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar pip
try {
    $pipVersion = pip --version 2>&1
    Write-Host "[OK] pip disponible" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] pip no esta disponible" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Crear requirements.txt si no existe
if (-not (Test-Path "requirements.txt")) {
    Write-Host "[INFO] Creando requirements.txt" -ForegroundColor Yellow
    @"
requests==2.31.0
beautifulsoup4==4.12.2
playwright==1.40.0
lxml==4.9.3
"@ | Out-File -FilePath "requirements.txt" -Encoding UTF8
}

# Actualizar pip
Write-Host "[ACCION] Actualizando pip..." -ForegroundColor Blue
try {
    python -m pip install --upgrade pip --quiet
    Write-Host "[OK] pip actualizado" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] No se pudo actualizar pip" -ForegroundColor Yellow
}

# Instalar dependencias
Write-Host "[ACCION] Instalando dependencias..." -ForegroundColor Blue
try {
    pip install -r requirements.txt
    Write-Host "[OK] Dependencias instaladas" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Error instalando dependencias" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Instalar Chromium para Playwright
Write-Host "[ACCION] Instalando Chromium para Playwright..." -ForegroundColor Blue
try {
    playwright install chromium
    Write-Host "[OK] Chromium instalado" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Error instalando Chromium" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar instalacion
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "        VERIFICANDO INSTALACION" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

try {
    python -c "from playwright.sync_api import sync_playwright; print('[OK] Playwright funciona correctamente')"
    Write-Host "[OK] Verificacion exitosa" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Problema con la instalacion de Playwright" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Crear estructura de directorios
$dirs = @("src", "output", "logs")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "[INFO] Creado directorio: $dir" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "         INSTALACION COMPLETA" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "[OK] Todo instalado correctamente" -ForegroundColor Green
Write-Host "[SIGUIENTE] Para ejecutar el scraper:" -ForegroundColor Cyan
Write-Host "     1. Ejecuta: .\run.ps1" -ForegroundColor White
Write-Host "     2. O manualmente: python src\scraper.py" -ForegroundColor White
Write-Host ""
Read-Host "Presiona Enter para continuar"