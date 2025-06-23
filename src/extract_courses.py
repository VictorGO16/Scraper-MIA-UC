#!/usr/bin/env python3
"""
Script principal para extraer información de PDFs del catálogo UC

Este script procesa todos los PDFs en el directorio 'output/' (donde están
los PDFs descargados por el scraper) y extrae información estructurada,
con especial énfasis en la bibliografía.

Uso:
    python src/extract_courses.py
    python src/extract_courses.py --debug
    python src/extract_courses.py --input-dir /ruta/personalizada
"""

import argparse
import logging
from pathlib import Path
from datetime import datetime

from pdf_extractor import CourseExtractor, JSONExporter, CSVExporter, ReportExporter


def setup_logging(debug: bool = False) -> None:
    """Configura el sistema de logging"""
    level = logging.DEBUG if debug else logging.INFO
    format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Configurar logging a consola
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/extraction.log', encoding='utf-8')
        ]
    )


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Extrae información de PDFs del catálogo UC'
    )
    parser.add_argument(
        '--input-dir',
        type=Path,
        default=Path('output'),
        help='Directorio con los PDFs a procesar (default: output/)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('data/extracted'),
        help='Directorio para guardar resultados (default: data/extracted/)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Activar modo debug con logging detallado'
    )
    parser.add_argument(
        '--export-format',
        choices=['json', 'csv', 'both'],
        default='both',
        help='Formato de exportación (default: both)'
    )

    args = parser.parse_args()

    # Configurar logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)

    # Validar directorios
    if not args.input_dir.exists():
        logger.error(f"Directorio de entrada no existe: {args.input_dir}")
        return 1

    # Crear directorio de salida
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Timestamp para archivos de salida
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    logger.info("=== EXTRACTOR DE CURSOS UC ===")
    logger.info(f"Directorio de entrada: {args.input_dir}")
    logger.info(f"Directorio de salida: {args.output_dir}")
    logger.info(f"Formato de exportación: {args.export_format}")

    try:
        # Inicializar extractor
        extractor = CourseExtractor(debug=args.debug)

        # Procesar PDFs
        logger.info("Iniciando extracción de cursos...")
        courses = extractor.extract_from_directory(args.input_dir)

        if not courses:
            logger.warning("No se encontraron cursos para procesar")
            return 1

        # Generar reporte de extracción
        extraction_report = extractor.get_extraction_report(courses)

        # Logging de resultados
        logger.info("=== RESULTADOS DE EXTRACCIÓN ===")
        logger.info(f"Archivos procesados: {extraction_report['total_files']}")
        logger.info(f"Extracciones exitosas: {extraction_report['successful_extractions']}")
        logger.info(f"Tasa de éxito: {extraction_report['success_rate']:.1f}%")
        logger.info(f"Cursos con bibliografía: {extraction_report['courses_with_bibliography']}")
        logger.info(f"Cobertura bibliográfica: {extraction_report['bibliography_coverage']:.1f}%")
        logger.info(f"Total entradas bibliográficas: {extraction_report['total_bibliography_entries']}")

        # Exportar resultados
        logger.info("Exportando resultados...")

        # JSON
        if args.export_format in ['json', 'both']:
            json_exporter = JSONExporter()

            # Archivo completo
            json_path = args.output_dir / f"cursos_completo_{timestamp}.json"
            json_exporter.export_batch(courses, json_path)

            # Solo bibliografía
            bib_path = args.output_dir / f"bibliografia_{timestamp}.json"
            json_exporter.export_bibliography_summary(courses, bib_path)

        # CSV
        if args.export_format in ['csv', 'both']:
            csv_exporter = CSVExporter()

            # Metadatos
            metadata_path = args.output_dir / f"metadatos_{timestamp}.csv"
            csv_exporter.export_metadata(courses, metadata_path)

            # Bibliografía
            bib_csv_path = args.output_dir / f"bibliografia_{timestamp}.csv"
            csv_exporter.export_bibliography(courses, bib_csv_path)

        # Reporte de extracción
        report_exporter = ReportExporter()
        report_path = args.output_dir / f"reporte_extraccion_{timestamp}.json"
        report_exporter.export_extraction_report(courses, extraction_report, report_path)

        logger.info("=== EXTRACCIÓN COMPLETADA ===")
        logger.info(f"Resultados guardados en: {args.output_dir}")

        # Mostrar cursos con más bibliografía (top 5)
        courses_with_bib = [c for c in courses if c.has_bibliography]
        if courses_with_bib:
            top_courses = sorted(courses_with_bib, key=lambda c: c.bibliography.total_entries, reverse=True)[:5]
            logger.info("\nTop 5 cursos con más bibliografía:")
            for i, course in enumerate(top_courses, 1):
                logger.info(f"  {i}. {course.codigo} - {course.nombre}: {course.bibliography.total_entries} entradas")

        return 0

    except Exception as e:
        logger.error(f"Error durante la extracción: {e}", exc_info=args.debug)
        return 1


if __name__ == "__main__":
    exit(main())