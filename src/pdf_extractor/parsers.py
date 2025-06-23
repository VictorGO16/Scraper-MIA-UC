"""
Parsers especializados para diferentes secciones de los PDFs UC - VERSIÓN COMPLETA
"""

import re
from typing import List, Optional, Dict, Any, Tuple
import logging

from .models import (
    CourseMetadata, Bibliography, BibliographyEntry, ContenidoItem,
    Evaluacion, InformacionInstitucional
)


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


class ContentParser:
    """Parser expandido para contenido descriptivo y estructurado del curso"""

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

    def extract_resultados_aprendizaje(self, text: str) -> List[str]:
        """
        Extrae resultados de aprendizaje estructurados

        Args:
            text: Texto completo del PDF

        Returns:
            List[str]: Lista de resultados de aprendizaje
        """
        resultados = []

        # Buscar sección "II.RESULTADOS DE APRENDIZAJE"
        section_match = re.search(
            r'II\s*\.\s*RESULTADOS\s+DE\s+APRENDIZAJE\s*\n(.*?)(?=III\s*\.\s*CONTENIDOS|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if section_match:
            section_text = section_match.group(1).strip()

            # Buscar elementos numerados (1., 2., 3., etc.)
            pattern = r'^(\d+)\s*\.\s*([^\n]+(?:\n(?!\d+\s*\.)[^\n]*)*)'
            matches = re.findall(pattern, section_text, re.MULTILINE)

            for num, content in matches:
                # Limpiar contenido
                content = re.sub(r'\s+', ' ', content.strip())
                if content:
                    resultados.append(f"{num}.{content}")

        return resultados

    def extract_contenidos(self, text: str) -> Dict[str, ContenidoItem]:
        """
        Extrae contenidos estructurados con jerarquía

        Args:
            text: Texto completo del PDF

        Returns:
            Dict[str, ContenidoItem]: Contenidos organizados jerárquicamente
        """
        contenidos = {}

        # Buscar sección "III.CONTENIDOS"
        section_match = re.search(
            r'III\s*\.\s*CONTENIDOS\s*\n(.*?)(?=IV\s*\.\s*ESTRATEGIAS|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if not section_match:
            return contenidos

        section_text = section_match.group(1).strip()

        # Patrones para diferentes niveles de numeración
        patterns = [
            r'^(\d+)\s*\.\s*([^\n]+)',  # 1. Título principal
            r'^(\d+\.\d+)\s*\.\s*([^\n]+)',  # 1.1. Subtítulo
            r'^(\d+\.\d+\.\d+)\s*\.\s*([^\n]+)',  # 1.1.1. Sub-subtítulo
        ]

        lines = section_text.split('\n')
        current_main = None
        current_sub = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Verificar cada patrón
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    numero = match.group(1)
                    titulo = match.group(2).strip()

                    # Determinar nivel jerárquico
                    parts = numero.split('.')

                    if len(parts) == 1:  # Nivel principal (1., 2., etc.)
                        item = ContenidoItem(numero=numero, titulo=titulo)
                        contenidos[numero] = item
                        current_main = numero
                        current_sub = None

                    elif len(parts) == 2 and current_main:  # Nivel 2 (1.1., 1.2., etc.)
                        main_num = parts[0]
                        if main_num in contenidos:
                            item = ContenidoItem(numero=numero, titulo=titulo)
                            contenidos[main_num].subsecciones[numero] = item
                            current_sub = numero

                    elif len(parts) == 3 and current_main and current_sub:  # Nivel 3 (1.1.1., etc.)
                        main_num = parts[0]
                        sub_num = f"{parts[0]}.{parts[1]}"
                        if (main_num in contenidos and
                            sub_num in contenidos[main_num].subsecciones):
                            item = ContenidoItem(numero=numero, titulo=titulo)
                            contenidos[main_num].subsecciones[sub_num].subsecciones[numero] = item

                    break  # Solo un patrón por línea

        return contenidos

    def extract_metodologias(self, text: str) -> List[str]:
        """
        Extrae estrategias metodológicas

        Args:
            text: Texto completo del PDF

        Returns:
            List[str]: Lista de metodologías
        """
        metodologias = []

        # Buscar sección "IV.ESTRATEGIAS METODOLÓGICAS"
        section_match = re.search(
            r'IV\s*\.\s*ESTRATEGIAS\s+METODOL[OÓ]GICAS\s*\n(.*?)(?=V\s*\.\s*ESTRATEGIAS|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if section_match:
            section_text = section_match.group(1).strip()

            # Buscar elementos con guiones o viñetas
            lines = section_text.split('\n')
            for line in lines:
                line = line.strip()
                # Remover guiones, asteriscos, viñetas al inicio
                cleaned_line = re.sub(r'^[-•*]\s*', '', line)
                if cleaned_line and len(cleaned_line) > 3:
                    metodologias.append(cleaned_line)

        return metodologias

    def extract_evaluacion(self, text: str) -> Evaluacion:
        """
        Extrae información de evaluación con porcentajes

        Args:
            text: Texto completo del PDF

        Returns:
            Evaluacion: Información de evaluación estructurada
        """
        evaluacion = Evaluacion()

        # Buscar sección "V.ESTRATEGIAS EVALUATIVAS"
        section_match = re.search(
            r'V\s*\.\s*ESTRATEGIAS\s+EVALUATIVAS\s*\n(.*?)(?=VI\s*\.\s*BIBLIOGRAF|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if section_match:
            section_text = section_match.group(1).strip()

            # Patrones para extraer evaluaciones con porcentajes
            patterns = [
                r'-\s*([^:]+):\s*(\d+)%',  # -Controles: 30%
                r'•\s*([^:]+):\s*(\d+)%',  # •Controles: 30%
                r'^([^:]+):\s*(\d+)%',     # Controles: 30%
            ]

            for pattern in patterns:
                matches = re.findall(pattern, section_text, re.MULTILINE)
                for nombre, porcentaje in matches:
                    nombre_limpio = nombre.strip()
                    try:
                        porcentaje_num = float(porcentaje)
                        evaluacion.items[nombre_limpio] = porcentaje_num
                    except ValueError:
                        self.logger.warning(f"No se pudo convertir porcentaje: {porcentaje}")

            # Verificar total
            evaluacion.verificar_total()

        return evaluacion


class InstitutionalParser:
    """Parser para información institucional"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def extract_informacion_institucional(self, text: str) -> InformacionInstitucional:
        """
        Extrae información institucional del final del documento

        Args:
            text: Texto completo del PDF

        Returns:
            InformacionInstitucional: Información institucional
        """
        info = InformacionInstitucional()

        # Buscar la sección institucional (generalmente al final)
        institutional_match = re.search(
            r'(PONTIFICIA\s+UNIVERSIDAD\s+CATOLICA\s+DE\s+CHILE.*?)$',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if institutional_match:
            institutional_text = institutional_match.group(1)

            # Universidad
            if 'PONTIFICIA UNIVERSIDAD CATOLICA DE CHILE' in institutional_text.upper():
                info.universidad = "PONTIFICIA UNIVERSIDAD CATOLICA DE CHILE"

            # Facultad
            facultad_match = re.search(r'FACULTAD\s+DE\s+([^\n/]+)', institutional_text, re.IGNORECASE)
            if facultad_match:
                info.facultad = facultad_match.group(1).strip()

            # Escuela
            escuela_match = re.search(r'ESCUELA\s+DE\s+([^\n/]+)', institutional_text, re.IGNORECASE)
            if escuela_match:
                info.escuela = escuela_match.group(1).strip()

            # Instituto
            instituto_match = re.search(r'INSTITUTO\s+DE\s+([^\n/]+)', institutional_text, re.IGNORECASE)
            if instituto_match:
                info.instituto = instituto_match.group(1).strip()

            # Fecha
            fecha_match = re.search(r'([A-Z]+)\s+(\d{4})', institutional_text)
            if fecha_match:
                mes = fecha_match.group(1)
                año = int(fecha_match.group(2))
                info.mes = mes
                info.año = año
                info.fecha = f"{mes} {año}"

        return info


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

    def _split_bibliography_types(self, bib_text: str) -> Tuple[Optional[str], Optional[str]]:
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