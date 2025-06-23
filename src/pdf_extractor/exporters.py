"""
Exportadores para diferentes formatos de salida
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any
import logging

from .models import Course


class JSONExporter:
    """Exportador a formato JSON"""

    def __init__(self, indent: int = 2, ensure_ascii: bool = False):
        self.indent = indent
        self.ensure_ascii = ensure_ascii
        self.logger = logging.getLogger(__name__)

    def export_single(self, course: Course, output_path: Path) -> None:
        """
        Exporta un solo curso a archivo JSON

        Args:
            course: Curso a exportar
            output_path: Ruta del archivo de salida
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(
                    course.to_dict(),
                    f,
                    indent=self.indent,
                    ensure_ascii=self.ensure_ascii
                )

            self.logger.info(f"Curso exportado a: {output_path}")

        except Exception as e:
            self.logger.error(f"Error exportando curso a {output_path}: {e}")
            raise

    def export_batch(self, courses: List[Course], output_path: Path) -> None:
        """
        Exporta múltiples cursos a un archivo JSON

        Args:
            courses: Lista de cursos a exportar
            output_path: Ruta del archivo de salida
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Crear diccionario con cursos indexados por código
            courses_dict = {}
            for course in courses:
                key = course.codigo if course.codigo else f"unknown_{course.filename}"
                courses_dict[key] = course.to_dict()

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(
                    courses_dict,
                    f,
                    indent=self.indent,
                    ensure_ascii=self.ensure_ascii
                )

            self.logger.info(f"{len(courses)} cursos exportados a: {output_path}")

        except Exception as e:
            self.logger.error(f"Error exportando cursos a {output_path}: {e}")
            raise

    def export_bibliography_summary(self, courses: List[Course], output_path: Path) -> None:
        """
        Exporta solo un resumen de bibliografía

        Args:
            courses: Lista de cursos
            output_path: Ruta del archivo de salida
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            bibliography_summary = {}

            for course in courses:
                if course.has_bibliography:
                    key = course.codigo if course.codigo else course.filename
                    bibliography_summary[key] = {
                        "nombre": course.nombre,
                        "codigo": course.codigo,
                        "bibliografia": course.bibliography.to_dict(),
                        "total_entradas": course.bibliography.total_entries
                    }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(
                    bibliography_summary,
                    f,
                    indent=self.indent,
                    ensure_ascii=self.ensure_ascii
                )

            self.logger.info(f"Resumen de bibliografía exportado a: {output_path}")

        except Exception as e:
            self.logger.error(f"Error exportando resumen de bibliografía a {output_path}: {e}")
            raise


class CSVExporter:
    """Exportador a formato CSV"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def export_metadata(self, courses: List[Course], output_path: Path) -> None:
        """
        Exporta metadatos de cursos a CSV

        Args:
            courses: Lista de cursos
            output_path: Ruta del archivo de salida
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Header
                writer.writerow([
                    'codigo', 'nombre', 'creditos', 'modulos', 'caracter', 'tipo',
                    'disciplina', 'palabras_clave', 'filename', 'extraction_success',
                    'has_bibliography', 'total_bib_entries'
                ])

                # Datos
                for course in courses:
                    writer.writerow([
                        course.codigo or '',
                        course.nombre or '',
                        course.metadata.creditos or '',
                        course.metadata.modulos or '',
                        course.metadata.caracter or '',
                        ';'.join(course.metadata.tipo) if course.metadata.tipo else '',
                        course.metadata.disciplina or '',
                        ';'.join(course.metadata.palabras_clave) if course.metadata.palabras_clave else '',
                        course.filename,
                        course.extraction_success,
                        course.has_bibliography,
                        course.bibliography.total_entries
                    ])

            self.logger.info(f"Metadatos exportados a CSV: {output_path}")

        except Exception as e:
            self.logger.error(f"Error exportando metadatos a CSV: {e}")
            raise

    def export_bibliography(self, courses: List[Course], output_path: Path) -> None:
        """
        Exporta bibliografía a CSV (una fila por entrada bibliográfica)

        Args:
            courses: Lista de cursos
            output_path: Ruta del archivo de salida
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Header
                writer.writerow([
                    'curso_codigo', 'curso_nombre', 'tipo_bibliografia', 'raw_text',
                    'authors', 'title', 'year', 'publisher', 'url'
                ])

                # Datos
                for course in courses:
                    if not course.has_bibliography:
                        continue

                    # Bibliografía mínima
                    for entry in course.bibliography.minima:
                        writer.writerow([
                            course.codigo or '',
                            course.nombre or '',
                            'minima',
                            entry.raw_text,
                            '; '.join(entry.authors) if entry.authors else '',
                            entry.title or '',
                            entry.year or '',
                            entry.publisher or '',
                            entry.url or ''
                        ])

                    # Bibliografía complementaria
                    for entry in course.bibliography.complementaria:
                        writer.writerow([
                            course.codigo or '',
                            course.nombre or '',
                            'complementaria',
                            entry.raw_text,
                            '; '.join(entry.authors) if entry.authors else '',
                            entry.title or '',
                            entry.year or '',
                            entry.publisher or '',
                            entry.url or ''
                        ])

            self.logger.info(f"Bibliografía exportada a CSV: {output_path}")

        except Exception as e:
            self.logger.error(f"Error exportando bibliografía a CSV: {e}")
            raise


class ReportExporter:
    """Exportador de reportes y estadísticas"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def export_extraction_report(self, courses: List[Course], extractor_report: Dict[str, Any], output_path: Path) -> None:
        """
        Exporta reporte de extracción

        Args:
            courses: Lista de cursos procesados
            extractor_report: Reporte del extractor
            output_path: Ruta del archivo de salida
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            report = {
                "resumen_general": extractor_report,
                "cursos_procesados": [course.get_summary() for course in courses],
                "cursos_con_errores": [
                    {
                        "filename": course.filename,
                        "codigo": course.codigo,
                        "errores": course.extraction_errors
                    }
                    for course in courses if not course.extraction_success
                ],
                "bibliografia_detallada": [
                    {
                        "codigo": course.codigo,
                        "nombre": course.nombre,
                        "entradas_minima": len(course.bibliography.minima),
                        "entradas_complementaria": len(course.bibliography.complementaria),
                        "total": course.bibliography.total_entries
                    }
                    for course in courses if course.has_bibliography
                ]
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Reporte de extracción exportado a: {output_path}")

        except Exception as e:
            self.logger.error(f"Error exportando reporte: {e}")
            raise