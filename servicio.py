"""Clase abstracta Servicio y tres servicios especializados.

Python no soporta sobrecarga nativa; se emula con parámetros opcionales
(`impuesto`, `descuento`) y con despacho por tipo/cantidad de argumentos.
"""

from abc import abstractmethod

from entidad import Entidad
from excepciones import (
    CalculoInconsistenteError,
    ParametroFaltanteError,
    ServicioInvalidoError,
)

# IVA vigente en Colombia, usado como impuesto por defecto
IVA_POR_DEFECTO = 0.19


class Servicio(Entidad):
    """Abstracción de un servicio ofrecido por Software FJ."""

    def __init__(self, nombre=None, tarifa_hora=None):
        super().__init__()
        if nombre is None or str(nombre).strip() == "":
            raise ParametroFaltanteError("El nombre del servicio es obligatorio")
        # Se valida que la tarifa sea numérica y positiva
        try:
            tarifa = float(tarifa_hora)
        except (TypeError, ValueError) as error:
            raise ServicioInvalidoError(f"Tarifa inválida: {tarifa_hora!r}") from error
        if tarifa <= 0:
            raise ServicioInvalidoError("La tarifa por hora debe ser mayor que cero")
        self._nombre = str(nombre).strip()
        self._tarifa_hora = tarifa
        # Bandera de disponibilidad (encapsulada)
        self._disponible = True

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_hora(self) -> float:
        return self._tarifa_hora

    @property
    def disponible(self) -> bool:
        return self._disponible

    def marcar_disponible(self, valor: bool) -> None:
        """Cambia la disponibilidad del servicio."""
        self._disponible = bool(valor)

    # ---------------- métodos abstractos (polimorfismo) ----------------
    @abstractmethod
    def validar_parametros(self, horas) -> None:
        """Valida los parámetros de uso específicos de cada servicio."""

    @abstractmethod
    def _costo_base(self, horas: float) -> float:
        """Costo antes de impuestos y descuentos; cada subclase lo redefine."""

    # ---------------- sobrecarga emulada ----------------
    def calcular_costo(self, horas, *extras, impuesto=None, descuento=None) -> float:
        """Calcula el costo total. Variantes admitidas:

        - calcular_costo(horas)                       -> costo base
        - calcular_costo(horas, impuesto)             -> base + impuesto
        - calcular_costo(horas, impuesto, descuento)  -> base + impuesto - descuento
        - calcular_costo(horas, impuesto=.., descuento=..) (por nombre)
        """
        # Variante posicional: el 1.º extra es impuesto y el 2.º es descuento
        if len(extras) > 2:
            raise ServicioInvalidoError("Demasiados argumentos para calcular_costo")
        if len(extras) >= 1:
            impuesto = extras[0]
        if len(extras) == 2:
            descuento = extras[1]
        # Validaciones previas al cálculo
        self.validar_parametros(horas)
        impuesto = 0.0 if impuesto is None else impuesto
        descuento = 0.0 if descuento is None else descuento
        if not (0 <= impuesto <= 1):
            raise CalculoInconsistenteError(f"Impuesto fuera de rango [0,1]: {impuesto}")
        if not (0 <= descuento < 1):
            raise CalculoInconsistenteError(f"Descuento fuera de rango [0,1): {descuento}")
        base = self._costo_base(float(horas))
        total = base * (1 - descuento) * (1 + impuesto)
        # Verificación de consistencia del resultado
        if total < 0 or total != total:
            raise CalculoInconsistenteError(f"Resultado inconsistente: {total}")
        return round(total, 2)

    def calcular_costo_con_iva(self, horas) -> float:
        """Atajo: costo con el IVA por defecto."""
        return self.calcular_costo(horas, IVA_POR_DEFECTO)


class ReservaSala(Servicio):
    """Reserva de salas: depende de la capacidad de personas."""

    def __init__(self, nombre=None, tarifa_hora=None, capacidad=None):
        super().__init__(nombre, tarifa_hora)
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or capacidad <= 0:
            raise ServicioInvalidoError(f"Capacidad inválida: {capacidad!r}")
        self._capacidad = capacidad

    def validar_parametros(self, horas) -> None:
        # Las salas se reservan por bloques de 1 a 12 horas
        if not isinstance(horas, (int, float)) or isinstance(horas, bool) or not (1 <= horas <= 12):
            raise ServicioInvalidoError("Una sala se reserva entre 1 y 12 horas")

    def _costo_base(self, horas: float) -> float:
        # Recargo de 10 % si la sala tiene capacidad mayor a 20 personas
        recargo = 1.10 if self._capacidad > 20 else 1.0
        return self.tarifa_hora * horas * recargo

    def describir(self) -> str:
        return f"Sala '{self.nombre}' (capacidad {self._capacidad}) - ${self.tarifa_hora:,.0f}/h"


class AlquilerEquipo(Servicio):
    """Alquiler de equipos: cobra una fianza fija además de la tarifa."""

    def __init__(self, nombre=None, tarifa_hora=None, fianza=None):
        super().__init__(nombre, tarifa_hora)
        try:
            fianza = float(fianza)
        except (TypeError, ValueError) as error:
            raise ServicioInvalidoError(f"Fianza inválida: {fianza!r}") from error
        if fianza < 0:
            raise ServicioInvalidoError("La fianza no puede ser negativa")
        self._fianza = fianza

    def validar_parametros(self, horas) -> None:
        # Los equipos se alquilan de 1 a 72 horas
        if not isinstance(horas, (int, float)) or isinstance(horas, bool) or not (1 <= horas <= 72):
            raise ServicioInvalidoError("Un equipo se alquila entre 1 y 72 horas")

    def _costo_base(self, horas: float) -> float:
        return self.tarifa_hora * horas + self._fianza

    def describir(self) -> str:
        return f"Equipo '{self.nombre}' - ${self.tarifa_hora:,.0f}/h + fianza ${self._fianza:,.0f}"


class Asesoria(Servicio):
    """Asesoría especializada: tarifa según el nivel del experto."""

    # Multiplicadores por nivel de experiencia
    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, nombre=None, tarifa_hora=None, nivel="junior"):
        super().__init__(nombre, tarifa_hora)
        if nivel not in self.NIVELES:
            raise ServicioInvalidoError(f"Nivel inválido: {nivel!r}. Use {list(self.NIVELES)}")
        self._nivel = nivel

    def validar_parametros(self, horas) -> None:
        # Las asesorías admiten de 0.5 a 8 horas
        if not isinstance(horas, (int, float)) or isinstance(horas, bool) or not (0.5 <= horas <= 8):
            raise ServicioInvalidoError("Una asesoría dura entre 0.5 y 8 horas")

    def _costo_base(self, horas: float) -> float:
        return self.tarifa_hora * horas * self.NIVELES[self._nivel]

    def describir(self) -> str:
        return f"Asesoría '{self.nombre}' nivel {self._nivel} - ${self.tarifa_hora:,.0f}/h"
