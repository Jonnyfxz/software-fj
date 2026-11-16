"""Programa principal: simula 12 operaciones (válidas e inválidas) sin base de datos."""

from cliente import Cliente
from excepciones import ErrorSoftwareFJ
from registro import ARCHIVO_LOG, log
from reserva import Reserva
from servicio import Asesoria, AlquilerEquipo, ReservaSala

# Listas internas que reemplazan a una base de datos
clientes, servicios, reservas = [], [], []


def ejecutar(numero: int, titulo: str, operacion) -> None:
    """Ejecuta una operación aislada: ningún error detiene el programa."""
    print(f"\n--- Operación {numero}: {titulo} ---")
    log.info(f"Inicio operación {numero}: {titulo}")
    try:
        resultado = operacion()
    except ErrorSoftwareFJ as error:
        # Error controlado del dominio; se muestra la causa encadenada si existe
        causa = f" | causa: {error.__cause__}" if error.__cause__ else ""
        print(f"  ERROR CONTROLADO: {error}{causa}")
        log.error(f"Operación {numero} falló: {error}{causa}")
    except Exception as error:  # noqa: BLE001 - red de seguridad para errores inesperados
        print(f"  ERROR INESPERADO: {type(error).__name__}: {error}")
        log.critical(f"Operación {numero} error inesperado: {type(error).__name__}: {error}")
    else:
        print(f"  OK: {resultado}")
        log.info(f"Operación {numero} exitosa")
    finally:
        log.info(f"Fin operación {numero}")


def registrar_cliente(**datos):
    c = Cliente(**datos)
    clientes.append(c)
    return c


def registrar_servicio(clase, **datos):
    s = clase(**datos)
    servicios.append(s)
    return s


def crear_reserva(cliente, servicio, horas, confirmar=True):
    r = Reserva(cliente, servicio, horas)
    reservas.append(r)
    if confirmar:
        r.confirmar()
    return r


def main() -> None:
    log.info("===== Inicio de la simulación Software FJ =====")
    # 1. Cliente válido
    ejecutar(1, "Registro de cliente válido", lambda: registrar_cliente(
        nombre="Ana Pérez", correo="ana@correo.com", telefono="3101234567", documento="1020304050"))
    # 2. Cliente con correo inválido
    ejecutar(2, "Cliente con correo inválido", lambda: registrar_cliente(
        nombre="Luis Gómez", correo="luis#correo", telefono="3001234567", documento="987654321"))
    # 3. Cliente con parámetros faltantes
    ejecutar(3, "Cliente sin teléfono (parámetro faltante)", lambda: registrar_cliente(
        nombre="Marta Ruiz", correo="marta@correo.com", documento="123456789"))
    # 4. Segundo cliente válido
    ejecutar(4, "Segundo cliente válido", lambda: registrar_cliente(
        nombre="Carlos Mejía", correo="carlos@correo.com", telefono="3209876543", documento="79456123"))
    # 5. Sala válida
    ejecutar(5, "Creación de sala válida", lambda: registrar_servicio(
        ReservaSala, nombre="Sala Innovación", tarifa_hora=50000, capacidad=25))
    # 6. Equipo con tarifa inválida
    ejecutar(6, "Equipo con tarifa inválida", lambda: registrar_servicio(
        AlquilerEquipo, nombre="Proyector", tarifa_hora="gratis", fianza=100000))
    # 7. Equipo y asesoría válidos
    ejecutar(7, "Creación de equipo válido", lambda: registrar_servicio(
        AlquilerEquipo, nombre="Portátil Pro", tarifa_hora=15000, fianza=200000))
    ejecutar(8, "Creación de asesoría válida", lambda: registrar_servicio(
        Asesoria, nombre="Asesoría en Ciberseguridad", tarifa_hora=120000, nivel="senior"))
    # 9. Reserva exitosa y procesada
    def reserva_exitosa():
        r = crear_reserva(clientes[0], servicios[0], 3)
        r.procesar()
        return r
    ejecutar(9, "Reserva exitosa y procesada", reserva_exitosa)
    # 10. Reserva con duración inválida
    ejecutar(10, "Reserva con duración inválida (20 h en sala)",
             lambda: crear_reserva(clientes[0], servicios[0], 20))
    # 11. Reserva de servicio no disponible
    def reserva_no_disponible():
        servicios[1].marcar_disponible(False)
        return crear_reserva(clientes[1], servicios[1], 5)
    ejecutar(11, "Reserva de servicio no disponible", reserva_no_disponible)
    # 12. Cancelar y luego intentar confirmar (operación no permitida)
    def cancelar_y_confirmar():
        r = crear_reserva(clientes[1], servicios[2], 2, confirmar=False)
        r.cancelar()
        r.confirmar()
    ejecutar(12, "Confirmar una reserva ya cancelada", cancelar_y_confirmar)
    # 13. Sobrecarga del cálculo de costos
    def costos_sobrecargados():
        s = servicios[2]
        return (f"base={s.calcular_costo(4)}, +IVA={s.calcular_costo(4, 0.19)}, "
                f"+IVA-10%={s.calcular_costo(4, 0.19, 0.10)}, "
                f"kw={s.calcular_costo(4, impuesto=0.19, descuento=0.05)}")
    ejecutar(13, "Cálculo de costos sobrecargado", costos_sobrecargados)
    # 14. Descuento inconsistente
    ejecutar(14, "Cálculo con descuento inconsistente (150 %)",
             lambda: servicios[2].calcular_costo(2, 0.19, 1.5))
    # 15. Error inesperado (índice inexistente) para probar la red de seguridad
    ejecutar(15, "Error inesperado (cliente inexistente)", lambda: crear_reserva(clientes[99], servicios[0], 2))

    print("\n===== RESUMEN =====")
    for lista in (clientes, servicios, reservas):
        for item in lista:
            print(" ", item)
    print(f"\nLog de eventos y errores: {ARCHIVO_LOG}")
    log.info("===== Fin de la simulación: el sistema siguió activo =====")


if __name__ == "__main__":
    main()
