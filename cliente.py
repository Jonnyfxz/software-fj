"""Clase Cliente con validaciones robustas y datos personales encapsulados."""

import re

from entidad import Entidad
from excepciones import ClienteInvalidoError, DatoInvalidoError, ParametroFaltanteError

# Expresión regular simple para validar correos electrónicos
_PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


class Cliente(Entidad):
    """Cliente de Software FJ. Sus datos personales son atributos privados."""

    def __init__(self, nombre=None, correo=None, telefono=None, documento=None):
        super().__init__()
        try:
            # Se asignan mediante los setters, que validan cada dato
            self.nombre = nombre
            self.correo = correo
            self.telefono = telefono
            self.documento = documento
        except (DatoInvalidoError, ParametroFaltanteError) as error:
            # Encadenamiento de excepciones: se conserva la causa original (__cause__)
            raise ClienteInvalidoError("No fue posible registrar al cliente") from error

    # ------------------------- nombre -------------------------
    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("El nombre es obligatorio")
        valor = str(valor).strip()
        # Solo letras (incluye tildes y ñ) y espacios, mínimo 3 caracteres
        if len(valor) < 3 or not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+", valor):
            raise DatoInvalidoError(f"Nombre inválido: '{valor}'")
        self.__nombre = valor.title()

    # ------------------------- correo -------------------------
    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("El correo es obligatorio")
        valor = str(valor).strip().lower()
        if not _PATRON_CORREO.match(valor):
            raise DatoInvalidoError(f"Correo inválido: '{valor}'")
        self.__correo = valor

    # ------------------------- teléfono -------------------------
    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("El teléfono es obligatorio")
        valor = str(valor).strip()
        # Celular colombiano: 10 dígitos
        if not re.fullmatch(r"\d{10}", valor):
            raise DatoInvalidoError(f"Teléfono inválido (se esperan 10 dígitos): '{valor}'")
        self.__telefono = valor

    # ------------------------- documento -------------------------
    @property
    def documento(self) -> str:
        return self.__documento

    @documento.setter
    def documento(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("El documento es obligatorio")
        valor = str(valor).strip()
        if not re.fullmatch(r"\d{6,12}", valor):
            raise DatoInvalidoError(f"Documento inválido (6 a 12 dígitos): '{valor}'")
        self.__documento = valor

    def describir(self) -> str:
        # El documento se enmascara para proteger datos personales
        oculto = "*" * (len(self.documento) - 3) + self.documento[-3:]
        return f"Cliente #{self.id}: {self.nombre} | {self.correo} | Doc: {oculto}"
