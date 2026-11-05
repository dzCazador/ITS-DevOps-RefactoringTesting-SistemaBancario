import pytest
from src.tarjeta import Tarjeta, LimiteExcedidoError
from src.modelos.cliente import Cliente


# ==============================================================================
# FIXTURES (DRY & Reusabilidad)
# ==============================================================================

@pytest.fixture
def cliente_valido():
    """Retorna un cliente válido para vincular a la tarjeta."""
    return Cliente(nombre="Lucia", apellido="Torres", dni="35999888")


@pytest.fixture
def tarjeta_credito(cliente_valido):
    """Retorna una tarjeta con límite predeterminado de 10000.0 y saldo en 0.0."""
    return Tarjeta(numero="4509-1234-5678-9012", cliente=cliente_valido, limite=10000.0)


# ==============================================================================
# PRUEBAS UNITARIAS: INICIALIZACIÓN Y VALIDACIONES DEL CONSTRUCTOR
# ==============================================================================

def test_inicializacion_tarjeta_exitosa(tarjeta_credito, cliente_valido):
    """Verifica que la tarjeta se instancie con los atributos iniciales correctos."""
    assert tarjeta_credito.get_numero() == "4509-1234-5678-9012"
    assert tarjeta_credito.get_cliente() == cliente_valido
    assert tarjeta_credito.get_limite() == 10000.0
    assert tarjeta_credito.get_saldo_actual() == 0.0
    assert tarjeta_credito.get_movimientos() == []


def test_representacion_cadena_tarjeta(tarjeta_credito):
    """Verifica el método __str__ de la tarjeta."""
    esperado = "Tarjeta 4509-1234-5678-9012 - Cliente: Lucia Torres"
    assert str(tarjeta_credito) == esperado


def test_lanza_excepcion_numero_tarjeta_vacio(cliente_valido):
    """Valida la regla de negocio: el número de tarjeta no puede estar vacío."""
    with pytest.raises(ValueError, match="El número de tarjeta no puede estar vacío."):
        Tarjeta(numero="", cliente=cliente_valido)


def test_lanza_excepcion_limite_invalido(cliente_valido):
    """Valida que el límite de crédito deba ser estrictamente mayor a cero."""
    with pytest.raises(ValueError, match="El límite debe ser mayor a cero."):
        Tarjeta(numero="1234", cliente=cliente_valido, limite=0)

    with pytest.raises(ValueError, match="El límite debe ser mayor a cero."):
        Tarjeta(numero="1234", cliente=cliente_valido, limite=-500.0)


# ==============================================================================
# PRUEBAS UNITARIAS: OPERACIÓN REALIZAR COMPRA (Happy Path y Excepciones)
# ==============================================================================

def test_realizar_compra_exitosa_incrementa_saldo_y_movimiento(tarjeta_credito):
    """Verifica que una compra válida incremente el saldo actual y agregue el movimiento."""
    # Act
    tarjeta_credito.realizar_compra(2500.0)

    # Assert
    assert tarjeta_credito.get_saldo_actual() == 2500.0
    assert len(tarjeta_credito.get_movimientos()) == 1
    
    # Valida el tipo de movimiento guardado en la tupla
    fecha, monto, tipo = tarjeta_credito.get_movimientos()[0]
    assert monto == 2500.0
    assert tipo == "Compra"


def test_lanza_excepcion_compra_monto_invalido(tarjeta_credito):
    """Valida que el monto de la compra deba ser mayor a cero."""
    with pytest.raises(ValueError, match="El monto de la compra debe ser mayor a cero."):
        tarjeta_credito.realizar_compra(0)

    with pytest.raises(ValueError, match="El monto de la compra debe ser mayor a cero."):
        tarjeta_credito.realizar_compra(-100.0)


def test_lanza_excepcion_limite_excedido(tarjeta_credito):
    """Valida que se lance LimiteExcedidoError al intentar superar el límite de crédito."""
    with pytest.raises(LimiteExcedidoError, match="Se excede el límite de crédito."):
        tarjeta_credito.realizar_compra(10000.1)


# ==============================================================================
# PRUEBAS UNITARIAS: OPERACIÓN PAGAR TARJETA
# ==============================================================================

def test_pagar_tarjeta_reduce_saldo_actual_y_registra_movimiento(tarjeta_credito):
    """Verifica que un pago reduzca la deuda consumida."""
    # Arrange
    tarjeta_credito.realizar_compra(4000.0)

    # Act
    tarjeta_credito.pagar_tarjeta(1500.0)

    # Assert
    assert tarjeta_credito.get_saldo_actual() == 2500.0
    assert len(tarjeta_credito.get_movimientos()) == 2
    
    # Valida que el último movimiento sea de tipo 'Pago'
    _, monto, tipo = tarjeta_credito.get_movimientos()[1]
    assert monto == 1500.0
    assert tipo == "Pago"


def test_lanza_excepcion_pago_monto_invalido(tarjeta_credito):
    """Valida que el monto del pago deba ser mayor a cero."""
    with pytest.raises(ValueError, match="El monto del pago debe ser mayor a cero."):
        tarjeta_credito.pagar_tarjeta(0)