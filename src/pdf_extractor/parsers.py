"""
Parsers especializados para diferentes secciones de los PDFs UC
"""

import re
from typing import List, Optional, Dict, Any
import logging

from .models import CourseMetadata, Bibliography, BibliographyEntry


class MetadataParser:
    """Parser para metadatos básicos del curso"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Patrones regex para extracción
        self.patterns = {
            'codigo': r'SIGLA\s*:\s*([A-Z0-9]+)',
            'nombre': r'CURSO\s*:\s*([^\n]+)',
            'traduccion': r'TRADUCCION\s*:\s*([^\n]+)',
            'creditos': r'CREDITOS\s*:\s*(\d+)',
            'modulos': r'MODULOS\s*:\s*(\d+)',
            'caracter': r'CARACTER\s*:\s*([^\n]+)',
            'tipo': r'TIPO\s*:\s*([^\n]+)',
            'calificacion': r'CALIFICACION\s*:\s*([^\n]+)',
            'disciplina': r'DISCIPLINA\s*:\s*([^\n]+)',
            'palabras_clave': r'PALABRAS CLAVE\s*:\s*([^\n]+)',
            'nivel_formativo': r'NIVEL FORMATIVO\s*:\s*([^\n]+)'
        }

    def parse(self, text: str) -> CourseMetadata:
        """
        Extrae metadatos del texto del PDF

        Args:
            text: Texto completo del PDF

        Returns:
            CourseMetadata: Metadatos extraídos
        """
        metadata = CourseMetadata()

        for field, pattern in self.patterns.items():
            try:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()

                    # Procesamiento específico por campo
                    if field == 'creditos' or field == 'modulos':
                        # Extraer solo números
                        numbers = re.findall(r'\d+', value)
                        if numbers:
                            setattr(metadata, field, int(numbers[0]))
                    elif field == 'tipo':
                        # Dividir tipos por comas
                        tipos = [t.strip() for t in value.split(',')]
                        metadata.tipo = tipos
                    elif field == 'palabras_clave':
                        # Dividir palabras clave por comas
                        palabras = [p.strip() for p in value.split(',')]
                        metadata.palabras_clave = palabras
                    else:
                        # Campo de texto simple
                        setattr(metadata, field, value)

            except Exception as e:
                self.logger.warning(f"Error extrayendo {field}: {e}")

        return metadata


class BibliographyParser:
    """Parser especializado para bibliografía"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse(self, text: str) -> Bibliography:
        """
        Extrae bibliografía del texto del PDF

        Args:
            text: Texto completo del PDF

        Returns:
            Bibliography: Bibliografía estructurada
        """
        bibliography = Bibliography()

        # Buscar sección de bibliografía
        bib_section = self._extract_bibliography_section(text)
        if not bib_section:
            return bibliography

        # Separar bibliografía mínima y complementaria
        minima_text, complementaria_text = self._split_bibliography_types(bib_section)

        # Parsear cada tipo
        if minima_text:
            bibliography.minima = self._parse_bibliography_entries(minima_text, "minima")

        if complementaria_text:
            bibliography.complementaria = self._parse_bibliography_entries(complementaria_text, "complementaria")

        return bibliography

    def _extract_bibliography_section(self, text: str) -> Optional[str]:
        """Extrae la sección completa de bibliografía"""
        # Buscar inicio de bibliografía
        bib_start = re.search(r'VI\s*\.\s*BIBLIOGRAFIA', text, re.IGNORECASE)
        if not bib_start:
            return None

        # Extraer desde bibliografía hasta el final o hasta siguiente sección principal
        bib_text = text[bib_start.start():]

        # Buscar fin (generalmente información institucional)
        end_patterns = [
            r'PONTIFICIA UNIVERSIDAD',
            r'FACULTAD DE',
            r'ESCUELA DE',
            r'INSTITUTO DE'
        ]

        for pattern in end_patterns:
            end_match = re.search(pattern, bib_text, re.IGNORECASE)
            if end_match:
                bib_text = bib_text[:end_match.start()]
                break

        return bib_text.strip()

    def _split_bibliography_types(self, bib_text: str) -> tuple[Optional[str], Optional[str]]:
        """Separa bibliografía mínima y complementaria"""
        minima_text = None
        complementaria_text = None

        # Buscar "Minima"
        minima_match = re.search(r'M[ií]nima\s*\n', bib_text, re.IGNORECASE)
        if minima_match:
            minima_start = minima_match.end()

            # Buscar "Complementaria"
            comp_match = re.search(r'Complementaria\s*\n', bib_text[minima_start:], re.IGNORECASE)
            if comp_match:
                minima_end = minima_start + comp_match.start()
                minima_text = bib_text[minima_start:minima_end].strip()
                complementaria_text = bib_text[minima_start + comp_match.end():].strip()
            else:
                # Solo hay mínima
                minima_text = bib_text[minima_start:].strip()

        return minima_text, complementaria_text

    def _parse_bibliography_entries(self, text: str, entry_type: str) -> List[BibliographyEntry]:
        """Parsea entradas individuales de bibliografía"""
        entries = []

        if not text:
            return entries

        # Dividir por líneas y agrupar entradas (las entradas pueden ocupar múltiples líneas)
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        current_entry = ""
        for line in lines:
            # Una nueva entrada generalmente empieza con mayúscula o autor
            if self._is_new_entry_start(line, current_entry):
                if current_entry:
                    # Procesar entrada anterior
                    entry = self._parse_single_entry(current_entry, entry_type)
                    if entry:
                        entries.append(entry)
                current_entry = line
            else:
                # Continuar entrada actual
                current_entry += " " + line

        # Procesar última entrada
        if current_entry:
            entry = self._parse_single_entry(current_entry, entry_type)
            if entry:
                entries.append(entry)

        return entries

    def _is_new_entry_start(self, line: str, current_entry: str) -> bool:
        """Determina si una línea es el inicio de una nueva entrada bibliográfica"""
        if not current_entry:
            return True

        # Heurísticas para detectar nueva entrada:
        # 1. Línea empieza con apellido (mayúscula seguida de coma)
        if re.match(r'^[A-Z][a-z]+,', line):
            return True

        # 2. Línea empieza con autor conocido (Apellido, Inicial.)
        if re.match(r'^[A-Z][a-z]+,\s+[A-Z]\.', line):
            return True

        # 3. La entrada actual parece completa (termina con punto, año, etc.)
        if re.search(r'[\.\d{4}]\s*$', current_entry.strip()):
            return True

        return False

    def _parse_single_entry(self, text: str, entry_type: str) -> Optional[BibliographyEntry]:
        """Parsea una entrada bibliográfica individual"""
        if not text or len(text) < 10:  # Muy corta para ser válida
            return None

        entry = BibliographyEntry(raw_text=text.strip())

        try:
            # Extraer año
            year_match = re.search(r'\((\d{4})\)', text)
            if year_match:
                entry.year = int(year_match.group(1))

            # Extraer URL
            url_match = re.search(r'https?://[^\s\)]+', text)
            if url_match:
                entry.url = url_match.group(0)

            # Extraer autores (simplificado - tomar hasta el primer paréntesis o año)
            author_text = text
            if year_match:
                author_text = text[:year_match.start()].strip()

            # Limpiar y extraer autores
            if author_text:
                # Remover puntos finales y limpiar
                author_text = re.sub(r'\.$', '', author_text).strip()

                # Heurística simple: dividir por 'y' o ','
                authors = re.split(r'\s+y\s+|\s*,\s*(?=[A-Z])', author_text)
                authors = [author.strip() for author in authors if author.strip()]
                if authors:
                    entry.authors = authors[:5]  # Máximo 5 autores para evitar errores

            # Extraer título (heurística: texto entre autores y año, o después de autores)
            title_text = text
            if entry.authors and entry.year:
                # Buscar texto entre último autor y año
                author_end = text.find(entry.authors[-1]) + len(entry.authors[-1])
                year_start = year_match.start() if year_match else len(text)
                title_text = text[author_end:year_start]

            # Limpiar título
            title_text = re.sub(r'^[,\.\s]+', '', title_text)  # Remover puntuación inicial
            title_text = re.sub(r'[,\.\s]+$', '', title_text)  # Remover puntuación final
            if title_text and len(title_text) > 3:
                entry.title = title_text.strip()

        except Exception as e:
            self.logger.warning(f"Error parseando entrada bibliográfica: {e}")

        return entry


class ContentParser:
    """Parser para contenido descriptivo del curso"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def extract_descripcion(self, text: str) -> Optional[str]:
        """
        Extrae la descripción del curso

        Args:
            text: Texto completo del PDF

        Returns:
            str: Descripción del curso o None
        """
        # Buscar sección "I.DESCRIPCIÓN DEL CURSO"
        desc_match = re.search(
            r'I\s*\.\s*DESCRIPCI[OÓ]N\s+DEL\s+CURSO\s*\n(.*?)(?=II\s*\.\s*RESULTADOS|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if desc_match:
            descripcion = desc_match.group(1).strip()
            # Limpiar texto
            descripcion = re.sub(r'\n+', ' ', descripcion)  # Múltiples líneas -> espacio
            descripcion = re.sub(r'\s+', ' ', descripcion)  # Múltiples espacios -> un espacio
            return descripcion

        return None