"""
Limpiador inteligente de bibliografía con múltiples estrategias
"""

import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class CleanBibEntry:
    """Entrada bibliográfica limpia"""
    authors: List[str]
    title: Optional[str] = None
    year: Optional[int] = None
    publisher: Optional[str] = None
    journal: Optional[str] = None
    pages: Optional[str] = None
    url: Optional[str] = None
    doi: Optional[str] = None
    raw_text: Optional[str] = None
    confidence: float = 1.0  # Confianza en la extracción (0-1)


class BibliographyCleaner:
    """
    Limpiador inteligente de referencias bibliográficas
    Combina reglas heurísticas con patrones comunes académicos
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Patrones comunes de publishers
        self.publishers = {
            'springer', 'wiley', 'elsevier', 'mit press', 'cambridge university press',
            'oxford university press', 'ieee', 'acm', 'pearson', "o'reilly",
            'crc press', 'taylor & francis', 'sage', 'academic press'
        }

        # Palabras que indican título
        self.title_indicators = [
            'machine learning', 'data mining', 'artificial intelligence',
            'pattern recognition', 'statistical learning', 'deep learning',
            'introduction to', 'handbook of', 'fundamentals of'
        ]

    def clean_entry(self, raw_text: str) -> CleanBibEntry:
        """
        Limpia una entrada bibliográfica usando múltiples estrategias

        Args:
            raw_text: Texto crudo de la referencia

        Returns:
            CleanBibEntry: Entrada limpia
        """
        if not raw_text or len(raw_text.strip()) < 10:
            return CleanBibEntry(authors=[], raw_text=raw_text, confidence=0.0)

        # Normalizar texto
        text = self._normalize_text(raw_text)

        # Intentar diferentes estrategias de parsing
        strategies = [
            self._parse_ieee_style,
            self._parse_apa_style,
            self._parse_author_year_style,
            self._parse_fallback
        ]

        best_result = None
        best_confidence = 0.0

        for strategy in strategies:
            try:
                result = strategy(text)
                if result.confidence > best_confidence:
                    best_result = result
                    best_confidence = result.confidence

                # Si tenemos muy buena confianza, usar este resultado
                if result.confidence > 0.9:
                    break

            except Exception as e:
                self.logger.debug(f"Strategy failed: {strategy.__name__}: {e}")
                continue

        if best_result:
            best_result.raw_text = raw_text
            return best_result

        # Fallback: crear entrada básica
        return CleanBibEntry(
            authors=self._extract_basic_authors(text),
            raw_text=raw_text,
            confidence=0.1
        )

    def _normalize_text(self, text: str) -> str:
        """Normaliza el texto de entrada"""
        # Remover caracteres extraños
        text = re.sub(r'[""''„"]', '"', text)  # Normalizar comillas
        text = re.sub(r'[–—]', '-', text)  # Normalizar guiones
        text = re.sub(r'\s+', ' ', text)  # Normalizar espacios
        text = text.strip()

        # Corregir patrones comunes de OCR
        text = re.sub(r'\?\s*([A-Z])', r'"\1', text)  # ? seguido de mayúscula -> "
        text = re.sub(r'([a-z])\?\s*,', r'\1",', text)  # letra? -> letra",

        return text

    def _parse_ieee_style(self, text: str) -> CleanBibEntry:
        """
        Parsea estilo IEEE: Author, "Title", Publisher, Year.
        """
        confidence = 0.0

        # Patrón IEEE típico
        pattern = r'^([^"]+),\s*"([^"]+)",\s*([^,]+),\s*(\d{4})'
        match = re.search(pattern, text)

        if match:
            authors_str = match.group(1).strip()
            title = match.group(2).strip()
            publisher = match.group(3).strip()
            year = int(match.group(4))

            authors = self._parse_authors(authors_str)
            confidence = 0.95

            return CleanBibEntry(
                authors=authors,
                title=title,
                year=year,
                publisher=publisher,
                confidence=confidence
            )

        # Si no coincide exactamente, baja la confianza
        return CleanBibEntry(authors=[], confidence=0.0)

    def _parse_apa_style(self, text: str) -> CleanBibEntry:
        """
        Parsea estilo APA: Author (Year). Title. Publisher.
        """
        confidence = 0.0

        # Patrón APA típico
        pattern = r'^([^(]+)\s*\((\d{4})\)\.\s*([^.]+)\.\s*(.+)'
        match = re.search(pattern, text)

        if match:
            authors_str = match.group(1).strip()
            year = int(match.group(2))
            title = match.group(3).strip()
            publisher = match.group(4).strip()

            authors = self._parse_authors(authors_str)
            confidence = 0.9

            return CleanBibEntry(
                authors=authors,
                title=title,
                year=year,
                publisher=publisher,
                confidence=confidence
            )

        return CleanBibEntry(authors=[], confidence=0.0)

    def _parse_author_year_style(self, text: str) -> CleanBibEntry:
        """
        Parsea patrones autor-año más flexibles
        """
        # Extraer año
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        year = int(year_match.group()) if year_match else None

        # Extraer título (texto entre comillas)
        title_match = re.search(r'"([^"]+)"', text)
        title = title_match.group(1) if title_match else None

        # Si no hay título entre comillas, buscar patrones de título
        if not title:
            for indicator in self.title_indicators:
                if indicator.lower() in text.lower():
                    # Extraer texto alrededor del indicador
                    pattern = f'([^,.]*{re.escape(indicator)}[^,.]*)'
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        title = match.group(1).strip()
                        break

        # Extraer publisher
        publisher = self._extract_publisher(text)

        # Extraer autores (texto antes del año o título)
        authors_text = text
        if year_match:
            authors_text = text[:year_match.start()]
        elif title_match:
            authors_text = text[:title_match.start()]

        authors = self._parse_authors(authors_text)

        # Calcular confianza
        confidence = 0.3
        if year: confidence += 0.2
        if title: confidence += 0.3
        if publisher: confidence += 0.1
        if authors: confidence += 0.1

        return CleanBibEntry(
            authors=authors,
            title=title,
            year=year,
            publisher=publisher,
            confidence=min(confidence, 1.0)
        )

    def _parse_fallback(self, text: str) -> CleanBibEntry:
        """
        Estrategia de fallback que extrae lo que puede
        """
        # Extraer año
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        year = int(year_match.group()) if year_match else None

        # Extraer autores básicos
        authors = self._extract_basic_authors(text)

        # Extraer publisher
        publisher = self._extract_publisher(text)

        confidence = 0.2 if (year or authors or publisher) else 0.1

        return CleanBibEntry(
            authors=authors,
            year=year,
            publisher=publisher,
            confidence=confidence
        )

    def _parse_authors(self, authors_str: str) -> List[str]:
        """
        Parsea string de autores de manera inteligente
        """
        if not authors_str:
            return []

        # Limpiar
        authors_str = authors_str.strip(' .,;')

        # Patrones de separación de autores
        patterns = [
            r'\s+and\s+',  # " and "
            r'\s*,\s*(?=[A-Z])',  # coma seguida de mayúscula
            r'\s*;\s*',  # punto y coma
            r'\s*&\s*',  # ampersand
        ]

        authors = [authors_str]  # Empezar con texto completo

        for pattern in patterns:
            new_authors = []
            for author in authors:
                new_authors.extend(re.split(pattern, author))
            authors = new_authors

        # Limpiar y filtrar autores
        cleaned_authors = []
        for author in authors:
            author = author.strip(' .,;()')
            # Filtrar autores muy cortos o que parecen errores
            if len(author) > 2 and not re.match(r'^\d+$', author):
                # Remover títulos y años del nombre
                author = re.sub(r'\s*\(\d{4}\).*', '', author)
                author = re.sub(r'^(Dr|Prof|Mr|Ms|Mrs)\.?\s*', '', author, re.IGNORECASE)
                if author:
                    cleaned_authors.append(author)

        return cleaned_authors[:5]  # Máximo 5 autores

    def _extract_basic_authors(self, text: str) -> List[str]:
        """
        Extracción básica de autores del inicio del texto
        """
        # Tomar primeras palabras que parecen nombres
        words = text.split()[:10]  # Primeras 10 palabras

        authors = []
        current_author = []

        for word in words:
            # Si parece apellido + inicial (ej: "Smith, J.")
            if re.match(r'^[A-Z][a-z]+,?$', word):
                if current_author:
                    authors.append(' '.join(current_author))
                current_author = [word.rstrip(',')]
            # Si parece inicial (ej: "J.")
            elif re.match(r'^[A-Z]\.?$', word):
                current_author.append(word)
            # Si empieza con mayúscula y no es muy larga
            elif word[0].isupper() and len(word) < 15:
                current_author.append(word)
            else:
                # Probablemente ya no es parte del nombre
                break

        if current_author:
            authors.append(' '.join(current_author))

        return authors[:3]  # Máximo 3 autores en modo básico

    def _extract_publisher(self, text: str) -> Optional[str]:
        """
        Extrae publisher del texto
        """
        text_lower = text.lower()

        # Buscar publishers conocidos
        for publisher in self.publishers:
            if publisher in text_lower:
                # Extraer contexto alrededor del publisher
                start = text_lower.find(publisher)
                # Tomar desde el publisher hasta la siguiente coma o punto
                end = start + len(publisher)
                while end < len(text) and text[end] not in '.,;\n':
                    end += 1

                # Expandir hacia atrás para capturar prefijos
                while start > 0 and text[start - 1] not in '.,;\n':
                    start -= 1

                return text[start:end].strip(' .,;')

        # Si no encuentra publisher conocido, buscar patrones
        # Texto después de coma que parece editorial
        publisher_match = re.search(r',\s*([A-Z][^,]*(?:Press|Publishers?|Books?|Ltd|Inc))', text)
        if publisher_match:
            return publisher_match.group(1).strip()

        return None


class CSVBibliographyCleaner:
    """
    Limpiador específico para datos CSV ya extraídos
    """

    def __init__(self):
        self.cleaner = BibliographyCleaner()
        self.logger = logging.getLogger(__name__)

    def clean_csv_data(self, csv_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Limpia datos de bibliografía ya extraídos en formato CSV

        Args:
            csv_data: Lista de diccionarios con datos CSV

        Returns:
            Lista de diccionarios con datos limpios
        """
        cleaned_data = []

        for row in csv_data:
            try:
                # Usar el texto raw como fuente de verdad
                raw_text = row.get('raw_text', '')
                if not raw_text:
                    continue

                # Limpiar con el algoritmo inteligente
                clean_entry = self.cleaner.clean_entry(raw_text)

                # Crear nueva fila con datos limpios
                cleaned_row = {
                    'curso_codigo': row.get('curso_codigo', ''),
                    'curso_nombre': row.get('curso_nombre', ''),
                    'tipo_bibliografia': row.get('tipo_bibliografia', ''),
                    'raw_text': raw_text,
                    'authors_clean': '; '.join(clean_entry.authors) if clean_entry.authors else '',
                    'title_clean': clean_entry.title or '',
                    'year_clean': clean_entry.year or '',
                    'publisher_clean': clean_entry.publisher or '',
                    'confidence': clean_entry.confidence,
                    # Mantener datos originales para comparación
                    'authors_original': row.get('authors', ''),
                    'title_original': row.get('title', ''),
                    'year_original': row.get('year', ''),
                    'publisher_original': row.get('publisher', '')
                }

                cleaned_data.append(cleaned_row)

            except Exception as e:
                self.logger.error(f"Error cleaning row: {e}")
                continue

        self.logger.info(f"Cleaned {len(cleaned_data)} bibliography entries")
        return cleaned_data