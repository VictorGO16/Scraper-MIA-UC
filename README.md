# UC Catalog Scraper & Data Extractor

Herramienta completa para descargar páginas del catálogo UC como PDFs y extraer información estructurada, con especial énfasis en bibliografía académica.

## 🚀 Características

### 📥 Scraper Web
- ✅ Extrae automáticamente todos los enlaces del catálogo UC
- ✅ Convierte páginas web a PDF de alta calidad
- ✅ Nombres de archivo inteligentes basados en códigos de curso
- ✅ Manejo robusto de errores y reintentos
- ✅ Evita descargas duplicadas

### 📊 Extractor de Datos
- ✅ Extrae metadatos estructurados de los PDFs
- ✅ **Enfoque especial en bibliografía** (mínima y complementaria)
- ✅ Parser inteligente para autores, títulos, años y URLs
- ✅ Exportación múltiple: JSON, CSV y reportes detallados
- ✅ Validación y limpieza automática de datos

### 🔧 Características Técnicas
- ✅ Logging detallado y reportes de ejecución
- ✅ Configuración centralizada y personalizable
- ✅ Arquitectura modular y escalable

## 📁 Estructura del proyecto

```
uc-catalog-scraper/
├── README.md                    # Este archivo
├── requirements.txt             # Dependencias de Python
├── setup.ps1                    # Script de instalación principal
├── setup-extraction.ps1         # Setup adicional para extracción
├── run.ps1                      # Script de ejecución del scraper
├── demo_extraction.py           # Demo del extractor
│
├── src/
│   ├── scraper.py              # Scraper principal
│   ├── extract_courses.py      # Extractor principal
│   ├── config.py               # Configuraciones del scraper
│   ├── utils.py                # Funciones auxiliares
│   └── pdf_extractor/          # Módulo de extracción
│       ├── __init__.py
│       ├── course_extractor.py # Extractor principal
│       ├── models.py           # Modelos de datos
│       ├── parsers.py          # Parsers especializados
│       └── exporters.py        # Exportadores JSON/CSV
│
├── output/                     # PDFs descargados
├── data/                       # Datos extraídos
│   ├── extracted/              # Archivos de salida
│   └── reports/                # Reportes de extracción
└── logs/                       # Logs de ejecución
```

## 🛠️ Instalación

### Instalación completa (Recomendado)

**1. Setup inicial del scraper:**
```powershell
.\setup.ps1
```

**2. Setup adicional para extracción de datos:**
```powershell
.\setup-extraction.ps1
```

### Instalación manual

**1. Crear entorno virtual:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**2. Instalar dependencias:**
```powershell
pip install -r requirements.txt
playwright install chromium
```

## 🏃‍♂️ Uso

### 1. Descargar PDFs del catálogo

```powershell
# Ejecutar scraper
.\run.ps1

# O manualmente
python src/scraper.py
```

### 2. Extraer información de los PDFs

```powershell
# Demo con un PDF
python demo_extraction.py

# Procesar todos los PDFs
python src/extract_courses.py

# Con logging detallado
python src/extract_courses.py --debug

# Personalizar directorios
python src/extract_courses.py --input-dir mi_carpeta --output-dir resultados
```

## 📊 Datos Extraídos

### 🎯 Información Principal
- **Metadatos del curso**: código, nombre, créditos, tipo, disciplina
- **Contenido académico**: descripción, resultados de aprendizaje
- **Metodología y evaluación**: estrategias y porcentajes
- **📚 Bibliografía detallada**: mínima y complementaria

### 📈 Formatos de Salida

**JSON Completo** (`cursos_completo_YYYYMMDD_HHMMSS.json`):
```json
{
  "EPG4005": {
    "metadata": {
      "codigo": "EPG4005",
      "nombre": "METODOS BAYESIANOS",
      "creditos": 5,
      "disciplina": "ESTADISTICA"
    },
    "bibliografia": {
      "minima": [
        {
          "raw_text": "Andrew Gelman, John B. Carlin...",
          "authors": ["Andrew Gelman", "John B. Carlin"],
          "title": "Bayesian Data Analysis",
          "year": 2013,
          "publisher": "CRC Press"
        }
      ]
    }
  }
}
```

**JSON de Bibliografía** (`bibliografia_YYYYMMDD_HHMMSS.json`):
```json
{
  "EPG4005": {
    "codigo": "EPG4005",
    "nombre": "METODOS BAYESIANOS",
    "bibliografia": {...},
    "total_entradas": 5
  }
}
```

**CSV de Metadatos** (`metadatos_YYYYMMDD_HHMMSS.csv`):
```csv
codigo,nombre,creditos,disciplina,has_bibliography,total_bib_entries
EPG4005,METODOS BAYESIANOS,5,ESTADISTICA,true,5
```

**CSV de Bibliografía** (`bibliografia_YYYYMMDD_HHMMSS.csv`):
```csv
curso_codigo,tipo_bibliografia,authors,title,year,publisher
EPG4005,minima,"Andrew Gelman; John B. Carlin",Bayesian Data Analysis,2013,CRC Press
```

## ⚙️ Configuración

### Configuración del Scraper (`src/config.py`)
```python
SCRAPER_CONFIG = {
    "delay_between_requests": 2,  # segundos entre descargas
    "request_timeout": 30,        # timeout de requests
    "max_retries": 3,            # reintentos por página
}

PDF_CONFIG = {
    "format": "A4",
    "margin": {"top": "0.75in", "right": "0.75in", "bottom": "0.75in", "left": "0.75in"}
}
```

### Configuración del Extractor
```powershell
# Solo JSON
python src/extract_courses.py --export-format json

# Solo CSV  
python src/extract_courses.py --export-format csv

# Ambos (default)
python src/extract_courses.py --export-format both
```

## 📈 Casos de Uso

### 🔍 Investigación Bibliográfica
- **Análisis de tendencias**: Autores y obras más citadas
- **Mapeo disciplinario**: Bibliografía por área de conocimiento
- **Evolución temporal**: Cambios en referencias a lo largo del tiempo

### 📊 Análisis Curricular
- **Distribución de créditos** por facultad y disciplina
- **Tipos de evaluación** más comunes
- **Palabras clave** y tendencias temáticas
- **Carga académica** y balanceo curricular

### 🎯 Búsquedas Inteligentes
```python
# Ejemplos de consultas posibles con los datos extraídos
"Cursos de 5 créditos con laboratorio"
"Bibliografía de IA y Machine Learning"
"Cursos sin prerrequisitos por facultad"
"Evolución de metodologías de evaluación"
```

## 🔧 Solución de problemas

### Problemas del Scraper
- **"Playwright no está instalado"**: `pip install playwright && playwright install chromium`
- **"No se encontraron enlaces"**: Verificar conexión y estructura de la página UC
- **PDFs vacíos**: Aumentar `wait_for_load` en config.py

### Problemas del Extractor
- **"Error importando módulos"**: Ejecutar `setup-extraction.ps1`
- **"No se encontraron PDFs"**: Asegurar que `/output` contiene PDFs
- **"Bibliografía incompleta"**: El parser maneja variaciones de formato automáticamente

### Problemas de Rendimiento
- **Memoria**: El procesamiento es secuencial para optimizar uso de memoria
- **Velocidad**: Ajustar `delay_between_requests` según capacidad del servidor UC

## 📊 Ejemplo de Resultados

```
=== RESULTADOS DE EXTRACCIÓN ===
Archivos procesados: 47
Extracciones exitosas: 45
Tasa de éxito: 95.7%
Cursos con bibliografía: 42
Cobertura bibliográfica: 89.4%
Total entradas bibliográficas: 312

Top 5 cursos con más bibliografía:
  1. EPG4005 - METODOS BAYESIANOS: 8 entradas
  2. FIL2000 - ETICA APLICADA A INTELIGENCIA ARTIFICIAL: 7 entradas
  3. IMT3870 - COMPUTACION DE ALTO RENDIMIENTO: 6 entradas
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/DataExtraction`)
3. Commit tus cambios (`git commit -m 'Add PDF data extraction'`)
4. Push a la rama (`git push origin feature/DataExtraction`)
5. Abre un Pull Request

## 📝 Notas Técnicas

### Scraper
- Respeta servidores UC con pausas entre requests
- Evita descargas duplicadas automáticamente
- Usa Playwright para renderizado completo de JavaScript

### Extractor
- Parser robusto para formatos variados de bibliografía
- Validación automática de datos extraídos
- Manejo inteligente de caracteres especiales y encoding