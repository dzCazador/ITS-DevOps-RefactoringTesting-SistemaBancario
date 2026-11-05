import pytest
from datetime import datetime

from src.modelos.cliente import Cliente
from src.modelos.cuenta import Cuenta, SaldoInsuficienteError
from src.modelos.cliente import Cliente


# ==============================================================================
# FIXTURES (Aislamiento de dependencias y Reusabilidad)
# ==============================================================================

@pytest.fixture
def cliente_valido():
    """Retorna un cliente válido para asignar a la cuenta."""
    return Cliente(nombre="Laura", apellido="Gomez", dni="12345678")


@pytest.fixture
def cuenta_con_saldo(cliente_valido):
    """Retorna una cuenta con un saldo inicial predeterminado de 1000.0."""
    return Cuenta(nro_cuenta="CTA-001", cliente=cliente_valido, saldo=1000.0)


# ==============================================================================
# PRUEBAS UNITARIAS: INICIALIZACIÓN Y VALIDACIONES DEL CONSTRUCTOR
# ==============================================================================

def test_inicializacion_cuenta_exitosa(cliente_valido):
    """Verifica la creación correcta de la cuenta con sus atributos getters."""
    # Act
    cuenta = Cuenta(nro_cuenta="CTA-123", cliente=cliente_valido, saldo=500.0)

    # Assert
    assert cuenta.get_nro_cuenta() == "CTA-123"
    assert cuenta.get_saldo() == 500.0
    assert cuenta.get_cliente().get_nombre() == "Laura"


def test_cuenta_se_relaciona_con_la_tabla_cuenta_de_db():
    cliente = Cliente("Ana", "Lopez", "22222222")
    fecha = datetime(2024, 1, 10, 12, 30)

    cuenta = Cuenta(
        "002",
        cliente,
        saldo=1000.0,
        id_cuenta=7,
        id_cliente=3,
        id_tipo_cuenta=2,
        tasa_interes=2.5,
        fecha_creacion=fecha,
    )

    assert cuenta.get_id_cuenta() == 7
    assert cuenta.get_id_cliente() == 3
    assert cuenta.get_id_tipo_cuenta() == 2
    assert cuenta.get_tasa_interes() == 2.5
    assert cuenta.get_fecha_creacion() == fecha


def test_cuenta_from_db_row():
    cliente = Cliente("Carlos", "Diaz", "33333333")
    fecha = datetime(2024, 2, 5, 9, 0)
    row = (8, "003", 5, 1, 1500.0, 3.0, fecha)

    cuenta = Cuenta.from_db_row(row, cliente)

    assert cuenta.get_id_cuenta() == 8
    assert cuenta.get_id_cliente() == 5
    assert cuenta.get_id_tipo_cuenta() == 1
    assert cuenta.get_nro_cuenta() == "003"
    assert cuenta.get_saldo() == 1500.0
    assert cuenta.get_tasa_interes() == 3.0


def test_no_permitir_saldo_negativo_inicial():
    cliente = Cliente("Juan", "Perez", "11111111")
    with pytest.raises(ValueError):
        Cuenta("002", cliente, saldo=-100)


def test_deposito_valido():
    cliente = Cliente("Ana", "Lopez", "22222222")
    cuenta = Cuenta("002", cliente)
    cuenta.depositar(100)
    assert cuenta.get_saldo() == 100.0


def test_retiro_valido():
    cliente = Cliente("Carlos", "Diaz", "33333333")
    cuenta = Cuenta("003", cliente, saldo=200)
    cuenta.retirar(50)
    assert cuenta.get_saldo() == 150.0


def test_saldo_insuficiente():
    cliente = Cliente("Pedro", "Gomez", "44444444")
    cuenta = Cuenta("004", cliente, saldo=10)
    with pytest.raises(SaldoInsuficienteError):
        cuenta.retirar(50)


def test_monto_no_numerico_en_deposito():
    cliente = Cliente("Laura", "Mendez", "55555555")
    cuenta = Cuenta("005", cliente)
    with pytest.raises(TypeError):
        cuenta.depositar("cien")


def test_retiro_monto_no_numerico():
    cliente = Cliente("Mario", "Suarez", "66666666")
    cuenta = Cuenta("006", cliente, saldo=100)
    with pytest.raises(TypeError):
        cuenta.retirar("veinte")


def test_retiro_monto_negativo():
    cliente = Cliente("Sofia", "Ramos", "77777777")
    cuenta = Cuenta("007", cliente, saldo=100)
    with pytest.raises(ValueError):
        cuenta.retirar(-50)
