# UC PDF Extractor - Setup Script para PowerShell
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   UC PDF EXTRACTOR - INSTALACION" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si estamos en un entorno virtual
$inVenv = $false
if ($env:VIRTUAL_ENV) {
    Write-Host "[OK] Usando entorno virtual activo: $env:VIRTUAL_ENV" -ForegroundColor Green
    $inVenv = $true
} else {
    # Buscar y activar entorno virtual local
    $venvDirs = @(".venv", "venv", "env")
    $foundVenv = $null

    foreach ($dir in $venvDirs) {
        $activateScript = Join-Path $dir "Scripts\Activate.ps1"
        if (Test-Path $activateScript) {
            Write-Host "[INFO] Activando entorno virtual: $dir" -ForegroundColor Yellow
            & $activateScript
            $foundVenv = $dir
            $inVenv = $true
            break
        }
    }

    if (-not $foundVenv) {
        Write-Host "[ERROR] No se encontro ningun entorno virtual" -ForegroundColor Red
        Write-Host "[SOLUCION] Ejecuta primero: .\setup.ps1" -ForegroundColor Yellow
        Read-Host "Presiona Enter para salir"
        exit 1
    }
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "     INSTALANDO NUEVAS DEPENDENCIAS" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Instalar dependencias para extracción de PDFs
Write-Host "[ACCION] Instalando pdfplumber para extraccion de PDFs..." -ForegroundColor Blue
try {
    pip install pdfplumber==0.10.3 --quiet
    Write-Host "[OK] pdfplumber instalado" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Error instalando pdfplumber" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "[ACCION] Instalando pandas para manipulacion de datos..." -ForegroundColor Blue
try {
    pip install pandas==2.1.4 --quiet
    Write-Host "[OK] pandas instalado" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Error instalando pandas" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "[ACCION] Instalando numpy..." -ForegroundColor Blue
try {
    pip install numpy==1.24.3 --quiet
    Write-Host "[OK] numpy instalado" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Error instalando numpy" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "       CREANDO ESTRUCTURA DE DATOS" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Crear directorios de trabajo
$dirs = @("data", "data\extracted", "data\reports")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "[INFO] Creado directorio: $dir" -ForegroundColor Yellow
    } else {
        Write-Host "[OK] Directorio ya existe: $dir" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "        VERIFICANDO INSTALACION" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Verificar pdfplumber
Write-Host "[TEST] Verificando pdfplumber..." -ForegroundColor Blue
try {
    python -c "import pdfplumber; print('[OK] pdfplumber disponible')"
    Write-Host "[OK] pdfplumber funciona correctamente" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Problema con pdfplumber" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar pandas
Write-Host "[TEST] Verificando pandas..." -ForegroundColor Blue
try {
    python -c "import pandas; print('[OK] pandas disponible')"
    Write-Host "[OK] pandas funciona correctamente" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Problema con pandas" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar numpy
Write-Host "[TEST] Verificando numpy..." -ForegroundColor Blue
try {
    python -c "import numpy; print('[OK] numpy disponible')"
    Write-Host "[OK] numpy funciona correctamente" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Problema con numpy" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "         INSTALACION COMPLETA" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "[OK] Extractor de PDFs listo para usar" -ForegroundColor Green
Write-Host "[SIGUIENTE] Para extraer informacion de PDFs:" -ForegroundColor Cyan
Write-Host "     1. Demo: python demo_extraction.py" -ForegroundColor White
Write-Host "     2. Completo: python src\extract_courses.py" -ForegroundColor White
Write-Host "     3. Debug: python src\extract_courses.py --debug" -ForegroundColor White
Write-Host ""
Read-Host "Presiona Enter para continuar"