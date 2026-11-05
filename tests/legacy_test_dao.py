import pytest
from src.dao import DAO
from src.modelos.cliente import Cliente


# ==============================================================================
# FIXTURES (Aislamiento de Persistencia con SQLite en memoria)
# ==============================================================================

@pytest.fixture
def dao_en_memoria():
    """Instancia un DAO usando una base de datos SQLite en memoria y la limpia tras la prueba."""
    dao = DAO(":memory:")
    yield dao
    dao.limpiar_base_datos()
    dao.cerrar_conexion()


@pytest.fixture
def cliente_base():
    """Retorna un objeto de dominio Cliente para pruebas de persistencia."""
    return Cliente(nombre="Esteban", apellido="Quito", dni="40123456")


# ==============================================================================
# PRUEBAS DE INTEGRACIÓN: PERSISTENCIA DE CLIENTE
# ==============================================================================

def test_guardar_y_obtener_cliente_por_dni(dao_en_memoria, cliente_base):
    """Verifica que un cliente se guarde en la BD y pueda recuperarse mediante su DNI."""
    # Act
    id_cliente = dao_en_memoria.guardar_cliente(cliente_base)
    cliente_recuperado = dao_en_memoria.obtener_cliente_por_dni("40123456")

    # Assert
    assert id_cliente is not None
    assert cliente_recuperado is not None
    assert cliente_recuperado[0] == id_cliente  # id_cliente
    assert cliente_recuperado[1] == "Esteban"     # nombre
    assert cliente_recuperado[2] == "Quito"       # apellido
    assert cliente_recuperado[3] == "40123456"    # dni


def test_lanza_excepcion_al_guardar_cliente_con_dni_duplicado(dao_en_memoria, cliente_base):
    """Valida la restricción UNIQUE del DNI en la base de datos (IntegrityError mapeado a ValueError)."""
    # Arrange
    dao_en_memoria.guardar_cliente(cliente_base)

    # Act & Assert
    with pytest.raises(ValueError, match="Ya existe un cliente con DNI 40123456"):
        dao_en_memoria.guardar_cliente(cliente_base)


def test_obtener_cliente_por_dni_inexistente_devuelve_none(dao_en_memoria):
    """Verifica que devuelva None al buscar un DNI no registrado."""
    assert dao_en_memoria.obtener_cliente_por_dni("99999999") is None


# ==============================================================================
# PRUEBAS DE INTEGRACIÓN: PERSISTENCIA DE CUENTA Y TRANSACCIONES
# ==============================================================================

def test_guardar_cuenta_y_registrar_transaccion(dao_en_memoria, cliente_base):
    """Verifica la relación de clave foránea entre Cliente, Cuenta y Transacción."""
    # Arrange
    id_cliente = dao_en_memoria.guardar_cliente(cliente_base)

    # Act
    id_cuenta = dao_en_memoria.guardar_cuenta(
        nro_cuenta="CTA-MEM-01",
        id_cliente=id_cliente,
        tipo_cuenta="Ahorro",
        saldo=5000.0
    )
    id_transaccion = dao_en_memoria.guardar_transaccion(
        id_cuenta=id_cuenta,
        tipo_transaccion="deposito",
        monto=2000.0
    )

    # Assert
    cuenta = dao_en_memoria.obtener_cuenta_por_numero("CTA-MEM-01")
    transacciones = dao_en_memoria.obtener_transacciones_por_cuenta(id_cuenta)

    assert id_cuenta is not None
    assert cuenta[4] == 5000.0  # saldo
    assert len(transacciones) == 1
    assert transacciones[0][0] == id_transaccion
    assert transacciones[0][2] == "deposito"


def test_actualizar_saldo_cuenta(dao_en_memoria, cliente_base):
    """Verifica la actualización de saldo mediante UPDATE en la base de datos."""
    # Arrange
    id_cliente = dao_en_memoria.guardar_cliente(cliente_base)
    id_cuenta = dao_en_memoria.guardar_cuenta("CTA-MEM-02", id_cliente, "Corriente", saldo=1000.0)

    # Act
    resultado = dao_en_memoria.actualizar_saldo_cuenta(id_cuenta, 3500.0)
    cuenta_actualizada = dao_en_memoria.obtener_cuenta_por_numero("CTA-MEM-02")

    # Assert
    assert resultado is True
    assert cuenta_actualizada[4] == 3500.0


# ==============================================================================
# PRUEBAS DE INTEGRACIÓN: PERSISTENCIA DE TARJETAS Y MOVIMIENTOS
# ==============================================================================

def test_guardar_tarjeta_y_movimiento(dao_en_memoria, cliente_base):
    """Verifica el flujo completo de guardado y consulta de tarjetas y movimientos."""
    # Arrange
    id_cliente = dao_en_memoria.guardar_cliente(cliente_base)

    # Act
    id_tarjeta = dao_en_memoria.guardar_tarjeta("5500-0000-1111-2222", id_cliente, limite_credito=15000.0)
    id_mov = dao_en_memoria.guardar_movimiento_tarjeta(id_tarjeta, "Compra", 1200.0)

    # Assert
    tarjetas = dao_en_memoria.obtener_tarjetas_por_cliente(id_cliente)
    movimientos = dao_en_memoria.obtener_movimientos_por_tarjeta(id_tarjeta)

    assert len(tarjetas) == 1
    assert tarjetas[0][1] == "5500-0000-1111-2222"
    assert len(movimientos) == 1
    assert movimientos[0][0] == id_mov
    assert movimientos[0][3] == 1200.0