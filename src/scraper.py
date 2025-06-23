"""
UC Catalog Scraper - Descarga páginas del catálogo UC como PDF
"""

import requests
from bs4 import BeautifulSoup
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

from config import *
from utils import *


class UCCatalogScraper:
    """
    Scraper para descargar páginas del catálogo UC como PDF
    """

    def __init__(self):
        self.logger = setup_logging()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': SCRAPER_CONFIG['user_agent']
        })

    def extract_catalog_links(self):
        """
        Extrae todos los enlaces del catálogo desde la página principal

        Returns:
            list: Lista de URLs del catálogo
        """
        self.logger.info(f"Extrayendo enlaces de: {BASE_URL}")

        try:
            response = self.session.get(
                BASE_URL,
                timeout=SCRAPER_CONFIG['request_timeout']
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', href=True)

            catalog_links = []
            for link in links:
                href = link['href']
                is_catalog, full_url = is_catalog_link(href, BASE_URL, CATALOG_DOMAIN)

                if is_catalog and validate_url(full_url):
                    catalog_links.append(full_url)

            # Eliminar duplicados y ordenar
            catalog_links = sorted(list(set(catalog_links)))

            self.logger.info(f"Se encontraron {len(catalog_links)} enlaces del catálogo")
            return catalog_links

        except Exception as e:
            self.logger.error(f"Error al extraer enlaces: {e}")
            return []

    def download_page_as_pdf(self, url, output_dir):
        """
        Descarga una página web y la convierte a PDF usando Playwright

        Args:
            url (str): URL de la página a descargar
            output_dir (Path): Directorio de salida

        Returns:
            bool: True si la descarga fue exitosa
        """
        try:
            # Generar nombre de archivo
            filename = sanitize_filename(url)
            filepath = output_dir / filename

            # Verificar si el archivo ya existe
            if filepath.exists():
                self.logger.info(f"El archivo {filename} ya existe, omitiendo...")
                return True

            self.logger.info(f"Descargando: {url}")
            self.logger.info(f"Guardando como: {filename}")

            with sync_playwright() as p:
                # Lanzar navegador
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Configurar página
                page.set_viewport_size({"width": 1280, "height": 720})
                page.set_default_timeout(SCRAPER_CONFIG['request_timeout'] * 1000)

                # Navegar y esperar carga completa
                page.goto(url, wait_until="networkidle")
                page.wait_for_timeout(PDF_CONFIG['wait_for_load'])

                # Generar PDF
                page.pdf(
                    path=str(filepath),
                    format=PDF_CONFIG['format'],
                    margin=PDF_CONFIG['margin'],
                    print_background=PDF_CONFIG['print_background']
                )

                browser.close()

            self.logger.info(f"✓ PDF creado exitosamente: {filename}")

            # Pausa entre requests
            time.sleep(SCRAPER_CONFIG['delay_between_requests'])

            return True

        except Exception as e:
            self.logger.error(f"✗ Error al crear PDF para {url}: {e}")
            return False

    def run(self):
        """
        Ejecuta el proceso completo de scraping
        """
        self.logger.info("=== Iniciando UC Catalog Scraper ===")

        # Verificar Playwright
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                browser.close()
        except Exception as e:
            self.logger.error("Playwright/Chromium no está instalado correctamente")
            self.logger.error("Ejecuta: pip install playwright && playwright install chromium")
            return False

        # Extraer enlaces del catálogo
        catalog_links = self.extract_catalog_links()

        if not catalog_links:
            self.logger.warning("No se encontraron enlaces del catálogo")
            return False

        self.logger.info(f"Iniciando descarga de {len(catalog_links)} páginas")
        self.logger.info(f"Los PDFs se guardarán en: {OUTPUT_DIR}")

        # Descargar cada página como PDF
        successful_downloads = 0
        failed_downloads = 0

        for i, url in enumerate(catalog_links, 1):
            progress = format_progress(i, len(catalog_links), sanitize_filename(url))
            self.logger.info(progress)

            if self.download_page_as_pdf(url, OUTPUT_DIR):
                successful_downloads += 1
            else:
                failed_downloads += 1

        # Generar reporte final
        report = create_summary_report(
            successful_downloads,
            failed_downloads,
            len(catalog_links),
            OUTPUT_DIR
        )

        self.logger.info(report)

        # Guardar reporte en archivo
        report_file = LOGS_DIR / "ultimo_reporte.txt"
        report_file.write_text(report, encoding='utf-8')

        return successful_downloads > 0


def main():
    """
    Función principal
    """
    scraper = UCCatalogScraper()
    success = scraper.run()

    if success:
        print(f"\n✓ Scraping completado. Revisa los archivos en: {OUTPUT_DIR}")
        print(f"📄 Reporte detallado en: {LOGS_DIR}/ultimo_reporte.txt")
    else:
        print("\n✗ El scraping falló. Revisa los logs para más detalles.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())