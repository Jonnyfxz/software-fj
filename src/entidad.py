"""Clase abstracta que representa las entidades generales del sistema."""

from abc import ABC, abstractmethod
from datetime import datetime
from itertools import count


class Entidad(ABC):
    """Abstracción base: toda entidad tiene un identificador y una descripción."""

    # Generador de consecutivos compartido por todas las entidades
    _consecutivo = count(1)

    def __init__(self):
        # Identificador único autoincremental (encapsulado)
        self._id = next(Entidad._consecutivo)
        # Marca de tiempo de creación
        self._creado_en = datetime.now()

    @property
    def id(self) -> int:
        """Identificador de solo lectura."""
        return self._id

    @property
    def creado_en(self) -> datetime:
        """Fecha de creación de solo lectura."""
        return self._creado_en

    @abstractmethod
    def describir(self) -> str:
        """Cada entidad concreta debe describirse a sí misma (polimorfismo)."""

    def __str__(self) -> str:
        # Representación textual delegada al método polimórfico
        return self.describir()
