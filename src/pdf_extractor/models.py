"""
Modelos de datos para el extractor de PDFs UC - VERSIÓN COMPLETA
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
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
class ContenidoItem:
    """Item individual de contenido con posible jerarquía"""
    numero: str  # "1", "1.1", "1.2.1", etc.
    titulo: str
    descripcion: Optional[str] = None
    subsecciones: Dict[str, 'ContenidoItem'] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        result = {
            "numero": self.numero,
            "titulo": self.titulo
        }
        if self.descripcion:
            result["descripcion"] = self.descripcion
        if self.subsecciones:
            result["subsecciones"] = {k: v.to_dict() for k, v in self.subsecciones.items()}
        return result


@dataclass
class Evaluacion:
    """Información de evaluación del curso"""
    items: Dict[str, Union[int, float]] = field(default_factory=dict)  # {"Controles": 30, "Proyecto": 40}
    total_verificado: bool = False
    suma_porcentajes: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            "items": self.items,
            "total_verificado": self.total_verificado,
            "suma_porcentajes": self.suma_porcentajes
        }

    def verificar_total(self) -> None:
        """Verifica que los porcentajes sumen 100%"""
        self.suma_porcentajes = sum(self.items.values())
        self.total_verificado = abs(self.suma_porcentajes - 100.0) < 0.1  # Tolerancia para errores de redondeo


@dataclass
class InformacionInstitucional:
    """Información institucional del curso"""
    universidad: Optional[str] = None
    facultad: Optional[str] = None
    escuela: Optional[str] = None
    instituto: Optional[str] = None
    fecha: Optional[str] = None
    mes: Optional[str] = None
    año: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario, excluyendo valores None"""
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class CourseMetadata:
    """Metadatos básicos del curso - EXPANDIDO"""
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
    """Representación completa de un curso - VERSIÓN EXPANDIDA"""
    # Información de procesamiento
    filename: str
    extracted_at: datetime = field(default_factory=datetime.now)
    extraction_success: bool = True
    extraction_errors: List[str] = field(default_factory=list)

    # Datos básicos del curso
    metadata: CourseMetadata = field(default_factory=CourseMetadata)
    descripcion: Optional[str] = None

    # Datos académicos detallados
    resultados_aprendizaje: List[str] = field(default_factory=list)
    contenidos: Dict[str, ContenidoItem] = field(default_factory=dict)
    metodologias: List[str] = field(default_factory=list)
    evaluacion: Evaluacion = field(default_factory=Evaluacion)
    bibliografia: Bibliography = field(default_factory=Bibliography)

    # Información institucional
    informacion_institucional: InformacionInstitucional = field(default_factory=InformacionInstitucional)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el curso completo a diccionario"""
        return {
            "filename": self.filename,
            "extracted_at": self.extracted_at.isoformat(),
            "extraction_success": self.extraction_success,
            "extraction_errors": self.extraction_errors,
            "metadata": self.metadata.to_dict(),
            "descripcion": self.descripcion,
            "resultados_aprendizaje": self.resultados_aprendizaje,
            "contenidos": {k: v.to_dict() for k, v in self.contenidos.items()},
            "metodologias": self.metodologias,
            "evaluacion": self.evaluacion.to_dict(),
            "bibliografia": self.bibliografia.to_dict(),
            "informacion_institucional": self.informacion_institucional.to_dict()
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
        return self.bibliografia.total_entries > 0

    @property
    def has_complete_evaluation(self) -> bool:
        """Verifica si tiene evaluación completa"""
        return len(self.evaluacion.items) > 0 and self.evaluacion.total_verificado

    @property
    def has_structured_content(self) -> bool:
        """Verifica si tiene contenidos estructurados"""
        return len(self.contenidos) > 0

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
            "bibliography_entries": self.bibliografia.total_entries,
            "contenidos_count": len(self.contenidos),
            "resultados_aprendizaje_count": len(self.resultados_aprendizaje),
            "metodologias_count": len(self.metodologias),
            "evaluacion_complete": self.has_complete_evaluation,
            "errors": len(self.extraction_errors)
        }

    def get_content_stats(self) -> Dict[str, Any]:
        """Estadísticas detalladas del contenido extraído"""
        total_subsecciones = 0
        max_depth = 0

        for contenido in self.contenidos.values():
            # Contar subsecciones recursivamente
            def count_subsections(item: ContenidoItem, depth: int = 1) -> int:
                nonlocal max_depth
                max_depth = max(max_depth, depth)
                count = len(item.subsecciones)
                for sub in item.subsecciones.values():
                    count += count_subsections(sub, depth + 1)
                return count

            total_subsecciones += count_subsections(contenido)

        return {
            "total_contenidos_principales": len(self.contenidos),
            "total_subsecciones": total_subsecciones,
            "profundidad_maxima": max_depth,
            "tiene_estructura_jerarquica": max_depth > 1
        }