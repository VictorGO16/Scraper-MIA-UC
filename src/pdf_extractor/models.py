"""
Modelos de datos para el extractor de PDFs UC
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json


@dataclass
class BibliographyEntry:
    """Entrada individual de bibliografía"""
    raw_text: str
    authors: Optional[List[str]] = None
    title: Optional[str] = None
    year: Optional[int] = None
    publisher: Optional[str] = None
    edition: Optional[str] = None
    pages: Optional[str] = None
    url: Optional[str] = None
    entry_type: Optional[str] = None  # 'book', 'article', 'web', etc.

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la entrada a diccionario, excluyendo valores None"""
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class Bibliography:
    """Bibliografía completa de un curso"""
    minima: List[BibliographyEntry] = field(default_factory=list)
    complementaria: List[BibliographyEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la bibliografía a diccionario"""
        return {
            "minima": [entry.to_dict() for entry in self.minima],
            "complementaria": [entry.to_dict() for entry in self.complementaria]
        }

    @property
    def total_entries(self) -> int:
        """Número total de entradas bibliográficas"""
        return len(self.minima) + len(self.complementaria)


@dataclass
class CourseMetadata:
    """Metadatos básicos del curso"""
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    traduccion: Optional[str] = None
    creditos: Optional[int] = None
    modulos: Optional[int] = None
    caracter: Optional[str] = None
    tipo: List[str] = field(default_factory=list)
    calificacion: Optional[str] = None
    disciplina: Optional[str] = None
    palabras_clave: List[str] = field(default_factory=list)
    nivel_formativo: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte los metadatos a diccionario, excluyendo valores None y listas vacías"""
        result = {}
        for k, v in self.__dict__.items():
            if v is not None and v != []:
                result[k] = v
        return result


@dataclass
class Course:
    """Representación completa de un curso"""
    # Información de procesamiento
    filename: str
    extracted_at: datetime = field(default_factory=datetime.now)
    extraction_success: bool = True
    extraction_errors: List[str] = field(default_factory=list)

    # Datos del curso
    metadata: CourseMetadata = field(default_factory=CourseMetadata)
    descripcion: Optional[str] = None
    bibliography: Bibliography = field(default_factory=Bibliography)

    # Datos adicionales (para futuras expansiones)
    resultados_aprendizaje: List[str] = field(default_factory=list)
    contenidos: Dict[str, str] = field(default_factory=dict)
    metodologias: List[str] = field(default_factory=list)
    evaluacion: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el curso completo a diccionario"""
        return {
            "filename": self.filename,
            "extracted_at": self.extracted_at.isoformat(),
            "extraction_success": self.extraction_success,
            "extraction_errors": self.extraction_errors,
            "metadata": self.metadata.to_dict(),
            "descripcion": self.descripcion,
            "bibliography": self.bibliography.to_dict(),
            "resultados_aprendizaje": self.resultados_aprendizaje,
            "contenidos": self.contenidos,
            "metodologias": self.metodologias,
            "evaluacion": self.evaluacion
        }

    def to_json(self, indent: int = 2) -> str:
        """Convierte el curso a JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @property
    def codigo(self) -> Optional[str]:
        """Acceso directo al código del curso"""
        return self.metadata.codigo

    @property
    def nombre(self) -> Optional[str]:
        """Acceso directo al nombre del curso"""
        return self.metadata.nombre

    @property
    def has_bibliography(self) -> bool:
        """Verifica si el curso tiene bibliografía"""
        return self.bibliography.total_entries > 0

    def add_error(self, error: str) -> None:
        """Agrega un error de extracción"""
        self.extraction_errors.append(error)
        self.extraction_success = False

    def get_summary(self) -> Dict[str, Any]:
        """Retorna un resumen del curso para logging/debugging"""
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "filename": self.filename,
            "extraction_success": self.extraction_success,
            "bibliography_entries": self.bibliography.total_entries,
            "errors": len(self.extraction_errors)
        }