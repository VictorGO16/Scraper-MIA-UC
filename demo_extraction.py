#!/usr/bin/env python3
"""
Demo script para probar el extractor con un PDF específico

Este script demuestra cómo usar el extractor de manera programática
y muestra los resultados en formato legible.
"""

import sys
from pathlib import Path

# Agregar src al path para importar nuestros módulos
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf_extractor import CourseExtractor, JSONExporter


def demo_single_pdf():
    """Demuestra extracción de un solo PDF"""
    print("=== DEMO: Extracción de PDF Individual ===")

    # Buscar un PDF de ejemplo
    output_dir = Path("output")
    pdf_files = list(output_dir.glob("*.pdf"))

    if not pdf_files:
        print("❌ No se encontraron PDFs en output/")
        print("💡 Ejecuta primero el scraper para descargar PDFs")
        return

    # Tomar el primer PDF como ejemplo
    sample_pdf = pdf_files[0]
    print(f"📄 Procesando: {sample_pdf.name}")

    # Crear extractor
    extractor = CourseExtractor(debug=True)

    # Extraer información
    course = extractor.extract_from_file(sample_pdf)

    # Mostrar resultados
    print("\n" + "=" * 50)
    print("RESULTADOS DE EXTRACCIÓN")
    print("=" * 50)

    print(f"✅ Extracción exitosa: {course.extraction_success}")
    print(f"📁 Archivo: {course.filename}")

    if course.extraction_errors:
        print(f"⚠️  Errores: {course.extraction_errors}")

    # Metadatos
    print(f"\n📊 METADATOS:")
    print(f"  Código: {course.codigo}")
    print(f"  Nombre: {course.nombre}")
    print(f"  Créditos: {course.metadata.creditos}")
    print(f"  Tipo: {', '.join(course.metadata.tipo) if course.metadata.tipo else 'N/A'}")
    print(f"  Disciplina: {course.metadata.disciplina}")

    # Descripción
    if course.descripcion:
        print(f"\n📝 DESCRIPCIÓN:")
        desc_preview = course.descripcion[:200] + "..." if len(course.descripcion) > 200 else course.descripcion
        print(f"  {desc_preview}")

    # Bibliografía
    print(f"\n📚 BIBLIOGRAFÍA:")
    print(f"  Entradas mínimas: {len(course.bibliography.minima)}")
    print(f"  Entradas complementarias: {len(course.bibliography.complementaria)}")
    print(f"  Total: {course.bibliography.total_entries}")

    if course.bibliography.minima:
        print(f"\n📖 MUESTRA DE BIBLIOGRAFÍA MÍNIMA:")
        for i, entry in enumerate(course.bibliography.minima[:2], 1):
            print(f"  {i}. {entry.raw_text[:100]}...")
            if entry.authors:
                print(f"     Autores: {', '.join(entry.authors)}")
            if entry.year:
                print(f"     Año: {entry.year}")
            if entry.title:
                print(f"     Título: {entry.title}")

    # Guardar resultado como JSON para inspección
    output_path = Path("data/demo_result.json")
    output_path.parent.mkdir(exist_ok=True)

    exporter = JSONExporter()
    exporter.export_single(course, output_path)

    print(f"\n💾 Resultado completo guardado en: {output_path}")
    print(f"🔍 Puedes abrir el archivo JSON para ver todos los detalles extraídos")


def demo_bibliography_analysis():
    """Demuestra análisis de bibliografía en múltiples PDFs"""
    print("\n=== DEMO: Análisis de Bibliografía ===")

    output_dir = Path("output")
    pdf_files = list(output_dir.glob("*.pdf"))

    if len(pdf_files) < 2:
        print("❌ Se necesitan al menos 2 PDFs para este demo")
        return

    # Procesar primeros 3 PDFs
    sample_pdfs = pdf_files[:3]
    extractor = CourseExtractor(debug=False)

    print(f"📄 Procesando {len(sample_pdfs)} PDFs...")

    bibliography_stats = []

    for pdf_path in sample_pdfs:
        course = extractor.extract_from_file(pdf_path)

        stats = {
            'codigo': course.codigo,
            'nombre': course.nombre,
            'filename': course.filename,
            'minima': len(course.bibliography.minima),
            'complementaria': len(course.bibliography.complementaria),
            'total': course.bibliography.total_entries,
            'success': course.extraction_success
        }
        bibliography_stats.append(stats)

    # Mostrar estadísticas
    print("\n📊 ESTADÍSTICAS DE BIBLIOGRAFÍA:")
    print("-" * 80)
    print(f"{'Código':<10} {'Nombre':<30} {'Mín':<5} {'Comp':<5} {'Total':<6} {'OK'}")
    print("-" * 80)

    for stats in bibliography_stats:
        nombre_short = (stats['nombre'][:27] + "...") if stats['nombre'] and len(stats['nombre']) > 30 else (
                    stats['nombre'] or 'N/A')
        print(
            f"{stats['codigo'] or 'N/A':<10} {nombre_short:<30} {stats['minima']:<5} {stats['complementaria']:<5} {stats['total']:<6} {'✅' if stats['success'] else '❌'}")

    # Estadísticas generales
    total_entries = sum(s['total'] for s in bibliography_stats)
    successful = sum(1 for s in bibliography_stats if s['success'])

    print("-" * 80)
    print(f"Total entradas bibliográficas encontradas: {total_entries}")
    print(f"Archivos procesados exitosamente: {successful}/{len(bibliography_stats)}")

    # Mostrar curso con más bibliografía
    max_bib = max(bibliography_stats, key=lambda x: x['total'])
    if max_bib['total'] > 0:
        print(f"📚 Curso con más bibliografía: {max_bib['codigo']} ({max_bib['total']} entradas)")


if __name__ == "__main__":
    print("🎯 UC PDF EXTRACTOR - DEMO")
    print("=" * 40)

    try:
        demo_single_pdf()
        demo_bibliography_analysis()

        print("\n✨ Demo completado exitosamente!")
        print("💡 Para procesar todos los PDFs, ejecuta:")
        print("   python src/extract_courses.py")

    except KeyboardInterrupt:
        print("\n🛑 Demo interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error en el demo: {e}")
        print("🔧 Asegúrate de haber ejecutado setup-extraction.bat primero")