"""Demostración del DAO actual con restauración del estado original al finalizar."""

import argparse
import shutil
from datetime import datetime
from pathlib import Path

from src.autenticacion import Autenticacion
from src.modelos.cliente import Cliente
from src.dao import DAO
from src.modelos.empleado import Empleado


def copiar_estado_original(ruta_bd: Path):
    """Guarda una copia del archivo de base de datos antes de hacer cambios."""
    copia = ruta_bd.with_suffix(".bak")
    if ruta_bd.exists():
        shutil.copy2(ruta_bd, copia)
        return copia
    return None


def restaurar_estado_original(ruta_bd: Path, copia: Path | None) -> None:
    """Restaura la base de datos al estado previo a la demo."""
    if copia and copia.exists():
        if ruta_bd.exists():
            ruta_bd.unlink()
        shutil.copy2(copia, ruta_bd)
        copia.unlink()
    elif ruta_bd.exists():
        ruta_bd.unlink()


def generar_dni_unico(sufijo: str) -> str:
    """Genera un DNI de 8 dígitos para esta ejecución sin colisionar con la base actual."""
    valor = int(datetime.now().timestamp() * 1000)
    return str((valor + sum(ord(ch) for ch in sufijo)) % 90000000 + 10000000)


def mostrar_estado(dao: DAO, dni: str) -> None:
    """Muestra los datos relevantes generados en la demo."""
    print(f"\n--- Consulta para {dni} ---")
    print("Persona:", dao.obtener_persona_por_dni(dni))
    print("Cliente:", dao.obtener_cliente_por_dni(dni))

    cliente = dao.obtener_cliente_por_dni(dni)
    if cliente:
        id_cliente = cliente[0]
        print("Cuentas del cliente:", dao.obtener_cuentas_por_cliente(id_cliente))


def ejecutar_demo(restaurar: bool = True) -> None:
    """Ejecuta todas las operaciones principales del DAO y devuelve la BD al estado original."""
    ruta_bd = Path("sistema_bancario.db")
    copia_backup = copiar_estado_original(ruta_bd)
    dao = DAO(str(ruta_bd))

    try:
        print("=== DEMOSTRACIÓN DEL DAO ===")
        print(f"Base de datos: {ruta_bd}")

        dni_cliente = generar_dni_unico("cliente")
        dni_empleado = generar_dni_unico("empleado")

        cliente = Cliente("Lucia", "Gomez", dni_cliente, categoria="NORMAL", estado="ACTIVO", password="miPassword123")
        id_cliente = dao.guardar_cliente(cliente)
        persona_creada = dao.obtener_persona_por_dni(dni_cliente)
        cliente_creado = dao.obtener_cliente_por_dni(dni_cliente)

        print("\nRESULTADO CLIENTE:")
        print(f"- Persona creada: {persona_creada}")
        print(f"- Cliente guardado con ID: {id_cliente}")
        print(f"- Cliente recuperado: {cliente_creado}")

        empleado = Empleado(
            "Pedro",
            "Lopez",
            dni_empleado,
            legajo="EMP-001",
            cargo="Analista",
            departamento="Administración",
            fecha_ingreso=datetime(2024, 1, 15),
            salario=65000.0,
            sucursal="Sucursal Central",
            password="empleado123",
        )
        id_empleado = dao.guardar_empleado(
            empleado,
            legajo=empleado.get_legajo(),
            cargo=empleado.get_cargo(),
            departamento=empleado.get_departamento(),
            fecha_ingreso=empleado.get_fecha_ingreso(),
            salario=empleado.get_salario(),
            sucursal=empleado.get_sucursal(),
        )
        print("\nRESULTADO EMPLEADO:")
        print(f"- Empleado guardado con ID: {id_empleado}")
        print(f"- Persona del empleado: {dao.obtener_persona_por_dni(dni_empleado)}")

        id_tipo_cuenta = dao.guardar_tipo_cuenta("Ahorro", "Cuenta de ahorro")
        id_tipo_transaccion = dao.guardar_tipo_transaccion("pagoIntereses", "Pago por intereses")
        print("Tipos guardados:", id_tipo_cuenta, id_tipo_transaccion)

        id_cuenta = dao.guardar_cuenta(
            nro_cuenta="CA-0001",
            id_cliente=id_cliente,
            id_tipo_cuenta=id_tipo_cuenta,
            saldo=1200.0,
            tasa_interes=2.5,
        )
        cuenta_guardada = dao.obtener_cuenta_por_numero("CA-0001")
        print("\nRESULTADO CUENTA:")
        print(f"- Cuenta guardada con ID: {id_cuenta}")
        print(f"- Cuenta recuperada: {cuenta_guardada}")
        print(f"- Cuentas del cliente: {dao.obtener_cuentas_por_cliente(id_cliente)}")

        id_transaccion1 = dao.guardar_transaccion(id_cuenta, "deposito", 500.0)
        id_transaccion2 = dao.guardar_transaccion(id_cuenta, "retiro", 150.0)
        id_transaccion3 = dao.guardar_transaccion(id_cuenta, "pagoIntereses", 60.0)
        historial = dao.obtener_transacciones_por_cuenta(id_cuenta)

        print("\nRESULTADO TRANSACCIONES:")
        print(f"- Transacciones creadas: {id_transaccion1}, {id_transaccion2}, {id_transaccion3}")
        print(f"- Historial completo: {historial}")

        saldo_actualizado = dao.actualizar_saldo_cuenta(id_cuenta, 1850.0)
        login_valido = dao.validar_login_por_dni(dni_cliente, "miPassword123")
        autenticacion = Autenticacion(dao)
        sesion_cliente = autenticacion.autenticar(dni_cliente, "miPassword123")
        sesion_personal = autenticacion.autenticar(dni_empleado, "empleado123")
        login_invalido = autenticacion.autenticar(dni_cliente, "claveIncorrecta")

        print("\nVALIDACIONES:")
        print(f"- Saldo actualizado: {saldo_actualizado}")
        print(f"- Login válido: {login_valido}")
        print(f"- Sesión de cliente: {sesion_cliente}")
        print(f"- Sesión de personal: {sesion_personal}")
        print(f"- Login con clave incorrecta: {login_invalido}")

        dao.limpiar_base_datos()
        print("\nBase vaciada temporalmente con limpiar_base_datos().")

        if restaurar:
            dao.cerrar_conexion()
            restaurar_estado_original(ruta_bd, copia_backup)
            print("Estado original restaurado: la base quedó como estaba antes de empezar.")
        else:
            print("Se conserva el estado actual de la base (sin restauración).")
    finally:
        dao.cerrar_conexion()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demostración completa del DAO con restauración final del estado original.")
    parser.add_argument(
        "--no-restaurar",
        action="store_true",
        help="deja la base en el estado generado por la demo sin volver al estado anterior",
    )
    args = parser.parse_args()
    ejecutar_demo(restaurar=not args.no_restaurar)
