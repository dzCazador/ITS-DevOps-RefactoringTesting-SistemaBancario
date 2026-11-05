import pytest
from src.modelos.transaccion import Transaccion


def test_crear_transaccion_deposito():
    t = Transaccion("deposito", 100.0)
    assert t.get_tipo() == "deposito"
    assert t.get_monto() == 100.0
    assert t.get_fecha() is not None
    assert "deposito" in str(t)


def test_crear_transaccion_retiro():
    t = Transaccion("retiro", 50.0)
    assert t.get_tipo() == "retiro"
    assert t.get_monto() == 50.0
    assert t.get_fecha() is not None
    assert "retiro" in str(t)


def test_tipo_invalido():
    with pytest.raises(ValueError):
        Transaccion("transferencia", 100.0)


def test_monto_invalido():
    with pytest.raises(ValueError):
        Transaccion("deposito", -50.0)


def test_monto_no_numerico():
    with pytest.raises(TypeError):
        Transaccion("deposito", "cien")
