"""Clase Reserva: integra cliente, servicio, duración y estado."""

from cliente import Cliente
from entidad import Entidad
from excepciones import (
    ErrorSoftwareFJ,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
)
from registro import log
from servicio import Servicio


class Reserva(Entidad):
    """Reserva con ciclo de vida: PENDIENTE -> CONFIRMADA/CANCELADA -> PROCESADA."""

    PENDIENTE, CONFIRMADA, CANCELADA, PROCESADA = "PENDIENTE", "CONFIRMADA", "CANCELADA", "PROCESADA"

    def __init__(self, cliente=None, servicio=None, horas=None):
        super().__init__()
        # Validación de tipos de los objetos asociados
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un Cliente válido")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un Servicio válido")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible")
        try:
            # Se delega la validación de la duración al servicio (polimorfismo)
            servicio.validar_parametros(horas)
        except ErrorSoftwareFJ as error:
            raise ReservaInvalidaError("Duración inválida para la reserva") from error
        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        self._estado = Reserva.PENDIENTE
        self._costo = None

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo(self):
        return self._costo

    def confirmar(self) -> None:
        """Confirma la reserva si está pendiente."""
        if self._estado != Reserva.PENDIENTE:
            raise OperacionNoPermitidaError(f"No se puede confirmar una reserva {self._estado}")
        self._estado = Reserva.CONFIRMADA
        log.info(f"Reserva #{self.id} confirmada")

    def cancelar(self) -> None:
        """Cancela la reserva si no está cancelada ni procesada."""
        if self._estado in (Reserva.CANCELADA, Reserva.PROCESADA):
            raise OperacionNoPermitidaError(f"No se puede cancelar una reserva {self._estado}")
        self._estado = Reserva.CANCELADA
        log.info(f"Reserva #{self.id} cancelada")

    def procesar(self, impuesto=0.19, descuento=0.0) -> float:
        """Procesa la reserva: calcula el costo con try/except/else/finally."""
        try:
            if self._estado != Reserva.CONFIRMADA:
                raise OperacionNoPermitidaError("Solo se procesan reservas CONFIRMADAS")
            costo = self._servicio.calcular_costo(self._horas, impuesto, descuento)
        except ErrorSoftwareFJ as error:
            # Se registra y se encadena con un error de más alto nivel
            log.error(f"Fallo al procesar reserva #{self.id}: {error}")
            raise ReservaInvalidaError(f"No se pudo procesar la reserva #{self.id}") from error
        else:
            # Solo se ejecuta si no hubo excepción
            self._costo = costo
            self._estado = Reserva.PROCESADA
            log.info(f"Reserva #{self.id} procesada. Costo total: ${costo:,.2f}")
            return costo
        finally:
            # Siempre se ejecuta, haya o no error
            log.debug(f"Fin del intento de procesamiento de la reserva #{self.id}")

    def describir(self) -> str:
        costo = f"${self._costo:,.2f}" if self._costo is not None else "sin calcular"
        return (f"Reserva #{self.id} [{self._estado}] {self._cliente.nombre} -> "
                f"{self._servicio.nombre} x {self._horas}h | costo: {costo}")
