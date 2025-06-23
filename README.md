# UC Catalog Scraper

Herramienta para descargar automáticamente todas las páginas del catálogo UC como archivos PDF.

## 🚀 Características

- ✅ Extrae automáticamente todos los enlaces del catálogo UC
- ✅ Convierte páginas web a PDF de alta calidad
- ✅ Nombres de archivo inteligentes basados en códigos de curso
- ✅ Manejo robusto de errores y reintentos
- ✅ Logging detallado y reportes de ejecución
- ✅ Evita descargas duplicadas
- ✅ Configuración centralizada y personalizable

## 📁 Estructura del proyecto

```
uc-catalog-scraper/
├── README.md              # Este archivo
├── requirements.txt       # Dependencias de Python
├── setup.ps1              # Scripts de instalación
├── run.ps1                # Scripts de ejecución
├── src/
│   ├── scraper.py        # Código principal
│   ├── config.py         # Configuraciones
│   └── utils.py          # Funciones auxiliares
├── output/               # PDFs generados
└── logs/                 # Logs de ejecución
```

## 🛠️ Instalación

### Método 1: Usando scripts de instalación (Recomendado)

**Windows:**
```powershell
.\setup.ps1
```

### Método 2: Instalación manual

1. **Crear entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate.bat  # Windows
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
playwright install chromium
```

## 🏃‍♂️ Uso

### Ejecución simple

**Windows:**
```powershell
.\run.ps1
```

### Ejecución manual
```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate.bat  # Windows

# Ejecutar scraper
python src/scraper.py
```

## ⚙️ Configuración

Puedes personalizar el comportamiento editando `src/config.py`:

```python
# Configuración del scraper
SCRAPER_CONFIG = {
    "delay_between_requests": 2,  # segundos entre descargas
    "request_timeout": 30,        # timeout de requests
    "max_retries": 3,            # reintentos por página
}

# Configuración de PDF
PDF_CONFIG = {
    "format": "A4",              # tamaño de página
    "margin": {                  # márgenes
        "top": "0.75in",
        "right": "0.75in",
        "bottom": "0.75in",
        "left": "0.75in"
    }
}
```

## 📊 Salida

### Archivos generados:
- **`output/`**: Contiene todos los PDFs descargados
  - Nombres basados en códigos de curso (ej: `EPG4007.pdf`)
  - Fallback a hash para páginas sin código
  
- **`logs/`**: Contiene logs de ejecución
  - `scraper.log`: Log detallado de cada ejecución
  - `ultimo_reporte.txt`: Resumen de la última ejecución

### Ejemplo de salida:
```
=== REPORTE DE EJECUCIÓN ===
Descargas exitosas: 45
Descargas fallidas: 2
Total de enlaces: 47
Tasa de éxito: 95.7%

Archivos generados:
  - EPG4007.pdf (234.5 KB)
  - EPG4008.pdf (198.2 KB)
  - EPG4009.pdf (267.8 KB)
  ...
```

## 🔧 Solución de problemas

### Error: "Playwright no está instalado"
```bash
pip install playwright
playwright install chromium
```

### Error: "No se encontraron enlaces"
- Verifica tu conexión a internet
- La página de la UC podría haber cambiado su estructura
- Revisa los logs en `logs/scraper.log`

### PDFs vacíos o incorrectos
- Algunas páginas pueden requerir JavaScript para cargar
- El scraper espera 3 segundos adicionales, pero puedes aumentar `wait_for_load` en config.py

### Problemas de memoria
- Si tienes muchas páginas, el scraper procesa una por vez para evitar problemas de memoria
- Puedes ajustar `delay_between_requests` para reducir la carga

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Notas

- El scraper respeta los servidores de la UC con pausas entre requests
- Los archivos existentes no se re-descargan (evita duplicados)
- Todas las URLs se validan antes de procesarse
- El proyecto usa logging profesional para debugging