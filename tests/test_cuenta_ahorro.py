import pytest
from src.modelos.cuenta_ahorro import CuentaAhorro
from src.modelos.cuenta import Cuenta
from src.modelos.cliente import Cliente


# ==============================================================================
# FIXTURES (Liskov Substitution Principle & DRY)
# ==============================================================================

@pytest.fixture
def cliente_valido():
    """Retorna un cliente válido para pruebas de dominio."""
    return Cliente(nombre="Carlos", apellido="Mendoza", dni="30111222")


@pytest.fixture
def cuenta_ahorro_default(cliente_valido):
    """Retorna una cuenta de ahorro con saldo inicial de 1000.0 e interés por defecto (1.0%)."""
    return CuentaAhorro(nro_cuenta="CA-001", cliente=cliente_valido, saldo=1000.0)


# ==============================================================================
# PRUEBAS UNITARIAS: HERENCIA Y LISKOV SUBSTITUTION (LSP)
# ==============================================================================

def test_cuenta_ahorro_es_subclase_de_cuenta(cuenta_ahorro_default):
    """LSP: Verifica que CuentaAhorro sea una instancia válida de Cuenta."""
    assert isinstance(cuenta_ahorro_default, Cuenta)
    assert cuenta_ahorro_default.get_nro_cuenta() == "CA-001"
    assert cuenta_ahorro_default.get_interes() == 1.0


def test_lanza_excepcion_interes_negativo(cliente_valido):
    """Valida la regla de negocio: la tasa de interés no puede ser negativa."""
    with pytest.raises(ValueError, match="La tasa de interés no puede ser negativa."):
        CuentaAhorro(nro_cuenta="CA-002", cliente=cliente_valido, saldo=500.0, interes=-2.5)


# ==============================================================================
# PRUEBAS UNITARIAS: LÓGICA DE NEGOCIO (Aplicar Interés)
# ==============================================================================

def test_aplicar_interes_calcula_y_actualiza_saldo_correctamente(cuenta_ahorro_default):
    """Verifica que el interés (1%) se aplique sobre el saldo inicial (1000.0) resultando en 1010.0."""
    # Act
    nuevo_saldo = cuenta_ahorro_default.aplicar_interes()

    # Assert
    assert nuevo_saldo == 1010.0
    assert cuenta_ahorro_default.get_saldo() == 1010.0


def test_aplicar_interes_con_tasa_personalizada(cliente_valido):
    """Verifica el cálculo de interés con una tasa distinta (ej. 5.0%)."""
    # Arrange
    cuenta = CuentaAhorro(nro_cuenta="CA-003", cliente=cliente_valido, saldo=2000.0, interes=5.0)

    # Act
    nuevo_saldo = cuenta.aplicar_interes()

    # Assert
    assert nuevo_saldo == 2100.0
    assert cuenta.get_saldo() == 2100.0