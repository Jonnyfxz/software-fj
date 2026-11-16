"""Módulo de excepciones personalizadas del sistema Software FJ.

Todas las excepciones heredan de ErrorSoftwareFJ, de modo que el programa
principal puede capturar cualquier error propio del dominio con una sola
cláusula `except ErrorSoftwareFJ`.
"""


class ErrorSoftwareFJ(Exception):
    """Excepción base de todo el sistema (raíz de la jerarquía)."""

    def __init__(self, mensaje: str, codigo: str = "FJ-000"):
        # Se invoca al constructor de Exception con el mensaje legible
        super().__init__(mensaje)
        # Código interno que facilita la búsqueda en el archivo de logs
        self.codigo = codigo
        # Texto del error guardado como atributo público de solo lectura lógica
        self.mensaje = mensaje

    def __str__(self) -> str:
        # Formato estándar: [CODIGO] mensaje
        return f"[{self.codigo}] {self.mensaje}"


class DatoInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando un dato (nombre, correo, teléfono, etc.) es inválido."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "FJ-101")


class ParametroFaltanteError(ErrorSoftwareFJ):
    """Se lanza cuando falta un parámetro obligatorio."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "FJ-102")


class ClienteInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando no es posible crear o usar un cliente."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "FJ-201")


class ServicioInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando los parámetros de un servicio son incorrectos."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "FJ-301")


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """Se lanza cuando se intenta reservar un servicio no disponible."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "FJ-302")


class ReservaInvalidaError(ErrorSoftwareFJ):
    """Se lanza ante intentos de reserva incorrectos."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "FJ-401")


class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """Se lanza cuando se pide una transición de estado no permitida."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "FJ-402")


class CalculoInconsistenteError(ErrorSoftwareFJ):
    """Se lanza cuando un cálculo de costos produce un resultado inválido."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "FJ-501")
