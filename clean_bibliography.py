#!/usr/bin/env python3
"""
Script para limpiar bibliografía ya extraída
"""

import sys
import pandas as pd
from pathlib import Path
import logging

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf_extractor.bibliography_cleaner import CSVBibliographyCleaner


def debug_csv_structure(csv_path):
    """Debug para entender la estructura del CSV"""
    print(f"🔍 DEBUGGING CSV: {csv_path.name}")

    # Leer primeras líneas raw
    with open(csv_path, 'r', encoding='utf-8') as f:
        first_lines = [f.readline().strip() for _ in range(3)]

    print("📄 Primeras 3 líneas raw:")
    for i, line in enumerate(first_lines):
        print(f"  {i + 1}: {repr(line)}")

    # Detectar separador
    separators = [',', '\t', ';', '|']
    for sep in separators:
        count = first_lines[0].count(sep)
        print(f"Separador '{sep}': {count} ocurrencias")

    # Intentar leer con diferentes separadores
    for sep_name, sep_char in [("coma", ","), ("tab", "\t"), ("punto_coma", ";")]:
        try:
            df_test = pd.read_csv(csv_path, sep=sep_char, nrows=5)
            print(f"\n✅ Lectura exitosa con separador {sep_name}:")
            print(f"   Columnas ({len(df_test.columns)}): {list(df_test.columns)}")
            print(f"   Forma: {df_test.shape}")
            if len(df_test) > 0:
                print(f"   Primera fila: {dict(df_test.iloc[0])}")
            return sep_char, df_test.columns.tolist()
        except Exception as e:
            print(f"❌ Error con separador {sep_name}: {e}")

    return None, []


def main():
    """Función principal para limpiar bibliografía"""

    logging.basicConfig(level=logging.INFO)

    # Buscar archivo CSV de bibliografía más reciente
    data_dir = Path("data/extracted")
    csv_files = list(data_dir.glob("bibliografia_*.csv"))

    if not csv_files:
        print("❌ No se encontraron archivos CSV de bibliografía")
        print("💡 Ejecuta primero: python src/extract_courses.py")
        return 1

    # Tomar el más reciente
    latest_csv = max(csv_files, key=lambda p: p.stat().st_mtime)
    print(f"📄 Procesando: {latest_csv.name}")

    # Debug de la estructura
    separator, columns = debug_csv_structure(latest_csv)

    if not separator:
        print("❌ No se pudo detectar el formato del CSV")
        return 1

    # Leer datos con el separador correcto
    try:
        df = pd.read_csv(latest_csv, sep=separator)
        print(f"\n📊 Cargadas {len(df)} entradas bibliográficas")
        print(f"📋 Columnas disponibles: {list(df.columns)}")

        # Mostrar muestra de datos
        if len(df) > 0:
            print(f"\n📝 Muestra de primera entrada:")
            for col in df.columns:
                value = df.iloc[0][col]
                print(f"   {col}: {repr(value)}")

    except Exception as e:
        print(f"❌ Error leyendo CSV: {e}")
        return 1

    # Verificar columnas necesarias
    required_columns = ['raw_text']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        print(f"❌ Faltan columnas requeridas: {missing_columns}")
        print(f"💡 Columnas disponibles: {list(df.columns)}")

        # Intentar mapear columnas
        print("\n🔄 Intentando mapear columnas...")
        column_mapping = {}

        # Buscar columna que contenga texto bibliográfico
        for col in df.columns:
            sample_values = df[col].dropna().head(3).tolist()
            avg_length = sum(len(str(val)) for val in sample_values) / len(sample_values) if sample_values else 0

            if avg_length > 50:  # Texto largo, probablemente bibliografía
                print(f"   Posible raw_text: {col} (longitud promedio: {avg_length:.1f})")
                column_mapping['raw_text'] = col
                break

        if 'raw_text' not in column_mapping:
            print("❌ No se pudo encontrar columna con texto bibliográfico")
            return 1

        # Renombrar columnas
        df = df.rename(columns={v: k for k, v in column_mapping.items()})
        print(f"✅ Columna mapeada: {column_mapping}")

    # Limpiar datos
    print("\n🧹 Limpiando datos bibliográficos...")
    cleaner = CSVBibliographyCleaner()

    # Convertir DataFrame a lista de diccionarios
    data_dict = df.to_dict('records')

    # Debug: mostrar primera entrada
    if data_dict:
        print(f"🔍 Primera entrada a limpiar:")
        first_entry = data_dict[0]
        for key, value in first_entry.items():
            print(f"   {key}: {repr(value)}")

    # Limpiar
    cleaned_data = cleaner.clean_csv_data(data_dict)

    if not cleaned_data:
        print("❌ No se pudieron limpiar los datos")
        print("🔍 Esto puede ser porque:")
        print("   - Los datos raw_text están vacíos")
        print("   - Hay un error en el algoritmo de limpieza")
        print("   - El formato no es reconocido")
        return 1

    # Crear DataFrame limpio
    cleaned_df = pd.DataFrame(cleaned_data)

    # Guardar resultado
    timestamp = latest_csv.stem.split('_')[-1]  # Extraer timestamp original
    output_path = data_dir / f"bibliografia_clean_{timestamp}.csv"

    cleaned_df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"💾 Datos limpios guardados en: {output_path}")

    # Mostrar estadísticas de mejora
    print("\n📈 ESTADÍSTICAS DE LIMPIEZA:")
    print(f"Entradas procesadas: {len(cleaned_data)}")

    # Contar mejoras
    high_confidence = sum(1 for row in cleaned_data if row['confidence'] > 0.8)
    medium_confidence = sum(1 for row in cleaned_data if 0.5 < row['confidence'] <= 0.8)
    low_confidence = sum(1 for row in cleaned_data if row['confidence'] <= 0.5)

    print(f"Alta confianza (>80%): {high_confidence}")
    print(f"Media confianza (50-80%): {medium_confidence}")
    print(f"Baja confianza (<50%): {low_confidence}")

    # Mostrar ejemplos de mejora
    print("\n📚 EJEMPLOS DE MEJORA:")
    for i, row in enumerate(cleaned_data[:3]):
        if row['confidence'] > 0.3:  # Bajar threshold para ver ejemplos
            print(f"\n{i + 1}. {row['curso_codigo']} - Confianza: {row['confidence']:.2f}")
            print(f"   Raw: {row['raw_text'][:100]}...")
            print(f"   Autores: {row['authors_clean']}")
            print(f"   Título: {row['title_clean']}")
            print(f"   Año: {row['year_clean']}")
            print(f"   Editorial: {row['publisher_clean']}")

    print(f"\n✨ Limpieza completada. Archivo disponible en: {output_path}")
    return 0


if __name__ == "__main__":
    exit(main())