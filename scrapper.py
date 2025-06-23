import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import time
import re
from playwright.sync_api import sync_playwright


def extract_catalog_links(base_url):
    """
    Extrae todos los enlaces que contienen 'catalogo.uc.cl' de la página principal
    """
    try:
        response = requests.get(base_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Buscar todos los enlaces
        links = soup.find_all('a', href=True)
        catalog_links = []

        for link in links:
            href = link['href']
            # Convertir enlaces relativos a absolutos
            full_url = urljoin(base_url, href)

            # Filtrar solo enlaces que contengan 'catalogo.uc.cl'
            if 'catalogo.uc.cl' in full_url:
                catalog_links.append(full_url)

        # Eliminar duplicados
        catalog_links = list(set(catalog_links))

        print(f"Se encontraron {len(catalog_links)} enlaces del catálogo")
        return catalog_links

    except Exception as e:
        print(f"Error al extraer enlaces: {e}")
        return []


def sanitize_filename(url):
    """
    Crea un nombre de archivo válido basado en la URL
    """
    # Extraer parámetros relevantes de la URL
    if 'sigla=' in url:
        sigla_match = re.search(r'sigla=([^&]+)', url)
        if sigla_match:
            return f"{sigla_match.group(1)}.pdf"

    # Si no hay sigla, usar el hash de la URL
    url_hash = str(hash(url))[-8:]
    return f"catalogo_{url_hash}.pdf"


def download_page_as_pdf_playwright(url, output_folder):
    """
    Descarga una página web y la convierte a PDF usando Playwright
    """
    try:
        # Crear el directorio si no existe
        os.makedirs(output_folder, exist_ok=True)

        # Generar nombre de archivo
        filename = sanitize_filename(url)
        filepath = os.path.join(output_folder, filename)

        # Verificar si el archivo ya existe
        if os.path.exists(filepath):
            print(f"El archivo {filename} ya existe, omitiendo...")
            return True

        print(f"Descargando: {url}")
        print(f"Guardando como: {filename}")

        with sync_playwright() as p:
            # Lanzar navegador
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Configurar viewport y timeouts
            page.set_viewport_size({"width": 1280, "height": 720})
            page.set_default_timeout(30000)  # 30 segundos

            # Navegar a la página
            page.goto(url, wait_until="networkidle")

            # Esperar un poco más para que cargue completamente
            page.wait_for_timeout(3000)

            # Generar PDF
            page.pdf(
                path=filepath,
                format='A4',
                margin={
                    "top": "0.75in",
                    "right": "0.75in",
                    "bottom": "0.75in",
                    "left": "0.75in"
                },
                print_background=True
            )

            browser.close()

        print(f"✓ PDF creado exitosamente: {filename}")

        # Pausa para evitar sobrecargar el servidor
        time.sleep(2)

        return True

    except Exception as e:
        print(f"✗ Error al crear PDF para {url}: {e}")
        return False


def main():
    """
    Función principal
    """
    # URL base
    base_url = "https://mia.uc.cl/malla-curricular"

    # Carpeta de salida
    output_folder = "catalogo_uc_pdfs"

    print("=== Scraper UC Catálogo (Playwright) ===")
    print(f"Extrayendo enlaces de: {base_url}")

    # Extraer enlaces del catálogo
    catalog_links = extract_catalog_links(base_url)

    if not catalog_links:
        print("No se encontraron enlaces del catálogo.")
        return

    print(f"\nIniciando descarga de {len(catalog_links)} páginas...")
    print(f"Los PDFs se guardarán en: {output_folder}/")

    # Descargar cada página como PDF
    successful_downloads = 0
    failed_downloads = 0

    for i, url in enumerate(catalog_links, 1):
        print(f"\n[{i}/{len(catalog_links)}]", end=" ")

        if download_page_as_pdf_playwright(url, output_folder):
            successful_downloads += 1
        else:
            failed_downloads += 1

    # Resumen final
    print(f"\n=== Resumen ===")
    print(f"Descargas exitosas: {successful_downloads}")
    print(f"Descargas fallidas: {failed_downloads}")
    print(f"Total de enlaces procesados: {len(catalog_links)}")
    print(f"Los archivos PDF se encuentran en: {output_folder}/")


if __name__ == "__main__":
    print("=== Verificando Playwright ===")

    try:
        from playwright.sync_api import sync_playwright

        print("✓ Playwright está instalado")

        # Verificar si Chromium está instalado
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
                print("✓ Chromium está instalado y funcionando")
            except Exception as e:
                print("✗ Chromium no está instalado o no funciona")
                print("Ejecuta: playwright install chromium")
                exit(1)

    except ImportError:
        print("✗ Playwright no está instalado")
        print("Ejecuta estos comandos:")
        print("pip install playwright")
        print("playwright install chromium")
        exit(1)

    print("\n" + "=" * 50)
    main()