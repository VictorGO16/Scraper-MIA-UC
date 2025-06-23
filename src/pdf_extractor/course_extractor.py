"""
Extractor principal para cursos UC - VERSIÓN COMPLETA
"""

import re
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

import pdfplumber

from .models import Course, CourseMetadata, Bibliography, BibliographyEntry
from .parsers import MetadataParser, BibliographyParser, ContentParser, InstitutionalParser


class CourseExtractor:
    """
    Extractor principal para información completa de cursos UC desde PDFs
    """

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.logger = logging.getLogger(__name__)

        # Inicializar parsers especializados
        self.metadata_parser = MetadataParser()
        self.bibliography_parser = BibliographyParser()
        self.content_parser = ContentParser()
        self.institutional_parser = InstitutionalParser()

        if debug:
            logging.basicConfig(level=logging.DEBUG)

    def extract_from_file(self, pdf_path: Path) -> Course:
        """
        Extrae información completa de un archivo PDF

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            Course: Objeto con toda la información extraída
        """
        course = Course(filename=pdf_path.name)

        try:
            # Extraer texto del PDF
            text = self._extract_text_from_pdf(pdf_path)
            if not text:
                course.add_error("No se pudo extraer texto del PDF")
                return course

            # Extraer información usando parsers especializados
            self.logger.info(f"Extrayendo metadatos de {pdf_path.name}")
            course.metadata = self.metadata_parser.parse(text)

            self.logger.info(f"Extrayendo descripción de {pdf_path.name}")
            course.descripcion = self.content_parser.extract_descripcion(text)

            self.logger.info(f"Extrayendo resultados de aprendizaje de {pdf_path.name}")
            course.resultados_aprendizaje = self.content_parser.extract_resultados_aprendizaje(text)

            self.logger.info(f"Extrayendo contenidos de {pdf_path.name}")
            course.contenidos = self.content_parser.extract_contenidos(text)

            self.logger.info(f"Extrayendo metodologías de {pdf_path.name}")
            course.metodologias = self.content_parser.extract_metodologias(text)

            self.logger.info(f"Extrayendo evaluación de {pdf_path.name}")
            course.evaluacion = self.content_parser.extract_evaluacion(text)

            self.logger.info(f"Extrayendo bibliografía de {pdf_path.name}")
            course.bibliografia = self.bibliography_parser.parse(text)

            self.logger.info(f"Extrayendo información institucional de {pdf_path.name}")
            course.informacion_institucional = self.institutional_parser.extract_informacion_institucional(text)

            # Logging para debugging
            if self.debug:
                summary = course.get_summary()
                content_stats = course.get_content_stats()
                self.logger.debug(f"Procesado: {summary}")
                self.logger.debug(f"Estadísticas de contenido: {content_stats}")

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

        # Estadísticas de procesamiento completas
        successful = sum(1 for c in courses if c.extraction_success)
        with_bibliography = sum(1 for c in courses if c.has_bibliography)
        with_complete_eval = sum(1 for c in courses if c.has_complete_evaluation)
        with_structured_content = sum(1 for c in courses if c.has_structured_content)

        self.logger.info(f"Procesamiento completado:")
        self.logger.info(f"  - Archivos procesados: {len(courses)}")
        self.logger.info(f"  - Extracciones exitosas: {successful}")
        self.logger.info(f"  - Cursos con bibliografía: {with_bibliography}")
        self.logger.info(f"  - Cursos con evaluación completa: {with_complete_eval}")
        self.logger.info(f"  - Cursos con contenidos estructurados: {with_structured_content}")

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
        Genera un reporte de extracción completo

        Args:
            courses: Lista de cursos extraídos

        Returns:
            Dict: Reporte con estadísticas detalladas
        """
        total = len(courses)
        successful = sum(1 for c in courses if c.extraction_success)
        with_bibliography = sum(1 for c in courses if c.has_bibliography)
        with_complete_eval = sum(1 for c in courses if c.has_complete_evaluation)
        with_structured_content = sum(1 for c in courses if c.has_structured_content)

        total_bib_entries = sum(c.bibliografia.total_entries for c in courses)
        total_contenidos = sum(len(c.contenidos) for c in courses)
        total_resultados = sum(len(c.resultados_aprendizaje) for c in courses)
        total_metodologias = sum(len(c.metodologias) for c in courses)

        # Errores más comunes
        all_errors = []
        for course in courses:
            all_errors.extend(course.extraction_errors)

        error_counts = {}
        for error in all_errors:
            error_counts[error] = error_counts.get(error, 0) + 1

        # Estadísticas por facultad/escuela
        facultades = {}
        for course in courses:
            facultad = course.informacion_institucional.facultad or course.informacion_institucional.escuela or "Sin clasificar"
            if facultad not in facultades:
                facultades[facultad] = 0
            facultades[facultad] += 1

        return {
            "resumen_general": {
                "total_files": total,
                "successful_extractions": successful,
                "success_rate": (successful / total * 100) if total > 0 else 0,
            },
            "cobertura_contenido": {
                "courses_with_bibliography": with_bibliography,
                "bibliography_coverage": (with_bibliography / total * 100) if total > 0 else 0,
                "courses_with_complete_evaluation": with_complete_eval,
                "evaluation_coverage": (with_complete_eval / total * 100) if total > 0 else 0,
                "courses_with_structured_content": with_structured_content,
                "structured_content_coverage": (with_structured_content / total * 100) if total > 0 else 0,
            },
            "estadisticas_contenido": {
                "total_bibliography_entries": total_bib_entries,
                "avg_entries_per_course": (total_bib_entries / with_bibliography) if with_bibliography > 0 else 0,
                "total_contenidos": total_contenidos,
                "avg_contenidos_per_course": (total_contenidos / total) if total > 0 else 0,
                "total_resultados_aprendizaje": total_resultados,
                "avg_resultados_per_course": (total_resultados / total) if total > 0 else 0,
                "total_metodologias": total_metodologias,
                "avg_metodologias_per_course": (total_metodologias / total) if total > 0 else 0,
            },
            "distribucion_facultades": facultades,
            "common_errors": dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5])
        }