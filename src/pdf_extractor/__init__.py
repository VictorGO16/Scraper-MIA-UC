"""
UC PDF Extractor - Extracción de información de PDFs del catálogo UC

Este módulo proporciona herramientas para extraer información estructurada
de los PDFs del catálogo de cursos de la UC, con enfoque especial en bibliografía.
"""

from .course_extractor import CourseExtractor
from .models import Course, Bibliography, BibliographyEntry
from .exporters import JSONExporter, CSVExporter, ReportExporter

__version__ = "1.0.0"
__all__ = ["CourseExtractor", "Course", "Bibliography", "BibliographyEntry", "JSONExporter", "CSVExporter", "ReportExporter"]