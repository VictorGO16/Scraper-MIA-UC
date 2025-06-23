"""
Funciones auxiliares para el UC Catalog Scraper
"""

import re
import logging
from pathlib import Path
from urllib.parse import urljoin
from config import LOGGING_CONFIG


def setup_logging():
    """
    Configura el sistema de logging
    """
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG["level"]),
        format=LOGGING_CONFIG["format"],
        handlers=[
            logging.FileHandler(LOGGING_CONFIG["file"], encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def sanitize_filename(url):
    """
    Crea un nombre de archivo válido basado en la URL

    Args:
        url (str): URL de la página del catálogo

    Returns:
        str: Nombre de archivo sanitizado
    """
    # Extraer sigla del curso si existe
    sigla_match = re.search(r'sigla=([^&]+)', url)
    if sigla_match:
        sigla = sigla_match.group(1).upper()
        # Limpiar caracteres especiales
        sigla = re.sub(r'[^\w\-_]', '_', sigla)
        return f"{sigla}.pdf"

    # Si no hay sigla, usar hash de la URL
    url_hash = str(abs(hash(url)))[-8:]
    return f"catalogo_{url_hash}.pdf"


def is_catalog_link(url, base_url, catalog_domain):
    """
    Verifica si un enlace pertenece al catálogo UC

    Args:
        url (str): URL a verificar
        base_url (str): URL base para resolver enlaces relativos
        catalog_domain (str): Dominio del catálogo a buscar

    Returns:
        tuple: (es_catalogo, url_completa)
    """
    # Convertir enlaces relativos a absolutos
    full_url = urljoin(base_url, url)

    # Verificar si contiene el dominio del catálogo
    is_catalog = catalog_domain in full_url

    return is_catalog, full_url


def format_progress(current, total, filename=""):
    """
    Formatea el progreso de descarga

    Args:
        current (int): Número actual
        total (int): Total de elementos
        filename (str): Nombre del archivo actual

    Returns:
        str: Cadena formateada del progreso
    """
    percentage = (current / total) * 100 if total > 0 else 0
    return f"[{current}/{total}] ({percentage:.1f}%) {filename}"


def validate_url(url):
    """
    Valida si una URL es válida

    Args:
        url (str): URL a validar

    Returns:
        bool: True si es válida, False si no
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// o https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # dominio
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # puerto opcional
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return url_pattern.match(url) is not None


def create_summary_report(successful, failed, total_links, output_dir):
    """
    Crea un reporte resumen de la ejecución

    Args:
        successful (int): Número de descargas exitosas
        failed (int): Número de descargas fallidas
        total_links (int): Total de enlaces procesados
        output_dir (Path): Directorio de salida

    Returns:
        str: Reporte formateado
    """
    success_rate = (successful / total_links * 100) if total_links > 0 else 0

    report = f"""
=== REPORTE DE EJECUCIÓN ===
Fecha: {Path(__file__).stat().st_mtime}
Descargas exitosas: {successful}
Descargas fallidas: {failed}
Total de enlaces: {total_links}
Tasa de éxito: {success_rate:.1f}%
Directorio de salida: {output_dir}

Archivos generados:
"""

    # Listar archivos PDF generados
    if output_dir.exists():
        pdf_files = list(output_dir.glob("*.pdf"))
        for pdf_file in sorted(pdf_files):
            file_size = pdf_file.stat().st_size / 1024  # KB
            report += f"  - {pdf_file.name} ({file_size:.1f} KB)\n"

    return report