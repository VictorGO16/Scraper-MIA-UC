"""
Extractor principal para cursos UC
"""

import re
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

import pdfplumber

from .models import Course, CourseMetadata, Bibliography, BibliographyEntry
from .parsers import MetadataParser, BibliographyParser, ContentParser


class CourseExtractor:
    """
    Extractor principal para información de cursos UC desde PDFs
    """

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.logger = logging.getLogger(__name__)

        # Inicializar parsers especializados
        self.metadata_parser = MetadataParser()
        self.bibliography_parser = BibliographyParser()
        self.content_parser = ContentParser()

        if debug:
            logging.basicConfig(level=logging.DEBUG)

    def extract_from_file(self, pdf_path: Path) -> Course:
        """
        Extrae información de un archivo PDF

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            Course: Objeto con la información extraída
        """
        course = Course(filename=pdf_path.name)

        try:
            # Extraer texto del PDF
            text = self._extract_text_from_pdf(pdf_path)
            if not text:
                course.add_error("No se pudo extraer texto del PDF")
                return course

            # Extraer información usando parsers especializados
            course.metadata = self.metadata_parser.parse(text)
            course.descripcion = self.content_parser.extract_descripcion(text)
            course.bibliography = self.bibliography_parser.parse(text)

            # Logging para debugging
            if self.debug:
                self.logger.debug(f"Procesado: {course.get_summary()}")

        except Exception as e:
            error_msg = f"Error procesando {pdf_path.name}: {str(e)}"
            course.add_error(error_msg)
            self.logger.error(error_msg, exc_info=self.debug)

        return course

    def extract_from_directory(self, directory_path: Path, pattern: str = "*.pdf") -> List[Course]:
        """
        Extrae información de todos los PDFs en un directorio

        Args:
            directory_path: Ruta al directorio
            pattern: Patrón de archivos a procesar

        Returns:
            List[Course]: Lista de cursos extraídos
        """
        courses = []
        pdf_files = list(directory_path.glob(pattern))

        self.logger.info(f"Procesando {len(pdf_files)} archivos PDF en {directory_path}")

        for pdf_file in pdf_files:
            self.logger.info(f"Procesando: {pdf_file.name}")
            course = self.extract_from_file(pdf_file)
            courses.append(course)

        # Estadísticas de procesamiento
        successful = sum(1 for c in courses if c.extraction_success)
        with_bibliography = sum(1 for c in courses if c.has_bibliography)

        self.logger.info(f"Procesamiento completado:")
        self.logger.info(f"  - Archivos procesados: {len(courses)}")
        self.logger.info(f"  - Extracciones exitosas: {successful}")
        self.logger.info(f"  - Cursos con bibliografía: {with_bibliography}")

        return courses

    def _extract_text_from_pdf(self, pdf_path: Path) -> Optional[str]:
        """
        Extrae texto completo de un PDF usando pdfplumber

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            str: Texto extraído o None si hay error
        """
        try:
            text_parts = []

            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                    else:
                        self.logger.warning(f"No se pudo extraer texto de la página {page_num}")

            if not text_parts:
                return None

            # Unir todas las páginas con separador
            full_text = "\n\n--- PÁGINA {} ---\n\n".join(text_parts)

            # Limpiar texto básico
            full_text = self._clean_text(full_text)

            return full_text

        except Exception as e:
            self.logger.error(f"Error extrayendo texto de {pdf_path}: {e}")
            return None

    def _clean_text(self, text: str) -> str:
        """
        Limpieza básica del texto extraído

        Args:
            text: Texto raw extraído

        Returns:
            str: Texto limpio
        """
        # Normalizar espacios y líneas
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Múltiples líneas vacías -> doble línea
        text = re.sub(r' +', ' ', text)  # Múltiples espacios -> un espacio
        text = text.strip()

        return text

    def get_extraction_report(self, courses: List[Course]) -> Dict[str, Any]:
        """
        Genera un reporte de extracción

        Args:
            courses: Lista de cursos extraídos

        Returns:
            Dict: Reporte con estadísticas
        """
        total = len(courses)
        successful = sum(1 for c in courses if c.extraction_success)
        with_bibliography = sum(1 for c in courses if c.has_bibliography)
        total_bib_entries = sum(c.bibliography.total_entries for c in courses)

        # Errores más comunes
        all_errors = []
        for course in courses:
            all_errors.extend(course.extraction_errors)

        error_counts = {}
        for error in all_errors:
            error_counts[error] = error_counts.get(error, 0) + 1

        return {
            "total_files": total,
            "successful_extractions": successful,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "courses_with_bibliography": with_bibliography,
            "bibliography_coverage": (with_bibliography / total * 100) if total > 0 else 0,
            "total_bibliography_entries": total_bib_entries,
            "avg_entries_per_course": (total_bib_entries / with_bibliography) if with_bibliography > 0 else 0,
            "common_errors": dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5])
        }