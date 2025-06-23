"""
Configuraciones para el UC Catalog Scraper
"""

import os
from pathlib import Path

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"

# URLs
BASE_URL = "https://mia.uc.cl/malla-curricular"
CATALOG_DOMAIN = "catalogo.uc.cl"

# Configuración del scraper
SCRAPER_CONFIG = {
    "delay_between_requests": 2,  # segundos
    "request_timeout": 30,        # segundos
    "max_retries": 3,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Configuración de PDF
PDF_CONFIG = {
    "format": "A4",
    "margin": {
        "top": "0.75in",
        "right": "0.75in",
        "bottom": "0.75in",
        "left": "0.75in"
    },
    "print_background": True,
    "wait_for_load": 3000  # milisegundos
}

# Configuración de logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "file": LOGS_DIR / "scraper.log"
}

# Crear directorios si no existen
for directory in [OUTPUT_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)