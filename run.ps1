# UC Catalog Scraper - Run Script para PowerShell
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   UC CATALOG SCRAPER - EJECUCION" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si estamos en un entorno virtual
$inVenv = $false
if ($env:VIRTUAL_ENV) {
    Write-Host "[OK] Usando entorno virtual activo: $env:VIRTUAL_ENV" -ForegroundColor Green
    $inVenv = $true
} elseif ($env:CONDA_DEFAULT_ENV) {
    Write-Host "[OK] Usando entorno Conda activo: $env:CONDA_DEFAULT_ENV" -ForegroundColor Green
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
Write-Host "       VERIFICANDO DEPENDENCIAS" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Verificar Python y dependencias
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python no esta disponible" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar dependencias criticas
$dependencies = @("requests", "bs4", "playwright")
$missingDeps = @()

foreach ($dep in $dependencies) {
    try {
        python -c "import $dep" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] $dep disponible" -ForegroundColor Green
        } else {
            $missingDeps += $dep
        }
    } catch {
        $missingDeps += $dep
    }
}

if ($missingDeps.Count -gt 0) {
    Write-Host "[ERROR] Faltan dependencias: $($missingDeps -join ', ')" -ForegroundColor Red
    Write-Host "[SOLUCION] Ejecuta primero: .\setup.ps1" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar que existe el archivo principal
if (-not (Test-Path "src\scraper.py")) {
    Write-Host "[ERROR] No se encontro src\scraper.py" -ForegroundColor Red
    Write-Host "[SOLUCION] Asegurate de estar en el directorio correcto del proyecto" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "        INICIANDO SCRAPER" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Ejecutar el scraper
try {
    python src\scraper.py
    $exitCode = $LASTEXITCODE
} catch {
    $exitCode = 1
}

# Mostrar resultado
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "           RESULTADO" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

if ($exitCode -eq 0) {
    Write-Host "[OK] Scraper ejecutado exitosamente" -ForegroundColor Green
    Write-Host "[ARCHIVOS] Los PDFs estan en: output\" -ForegroundColor Cyan
    if (Test-Path "logs\ultimo_reporte.txt") {
        Write-Host "[REPORTE] Reporte detallado en: logs\ultimo_reporte.txt" -ForegroundColor Cyan
    }
} else {
    Write-Host "[ERROR] El scraper termino con errores" -ForegroundColor Red
    if (Test-Path "logs\scraper.log") {
        Write-Host "[LOGS] Revisa los logs en: logs\scraper.log" -ForegroundColor Yellow
    }
}

Write-Host ""
Read-Host "Presiona Enter para continuar"