import pytest
from src.modelos.cliente import Cliente
from src.tarjeta import Tarjeta, LimiteExcedidoError


def test_crear_tarjeta_valida():
    cliente = Cliente("Juan", "Perez", "12345678")
    tarjeta = Tarjeta("1111-2222-3333-4444", cliente, limite=5000)
    assert tarjeta.get_numero() == "1111-2222-3333-4444"
    assert tarjeta.get_limite() == 5000
    assert tarjeta.get_saldo_actual() == 0


def test_realizar_compra_valida():
    cliente = Cliente("Ana", "Lopez", "87654321")
    tarjeta = Tarjeta("5555-6666-7777-8888", cliente, limite=2000)
    tarjeta.realizar_compra(500)
    assert tarjeta.get_saldo_actual() == 500


def test_exceder_limite():
    cliente = Cliente("Carlos", "Gomez", "98765432")
    tarjeta = Tarjeta("9999-0000-1111-2222", cliente, limite=1000)
    with pytest.raises(LimiteExcedidoError):
        tarjeta.realizar_compra(2000)


def test_pagar_tarjeta():
    cliente = Cliente("Lucia", "Diaz", "55555555")
    tarjeta = Tarjeta("3333-4444-5555-6666", cliente, limite=3000)
    tarjeta.realizar_compra(1000)
    tarjeta.pagar_tarjeta(500)
    assert tarjeta.get_saldo_actual() == 500


def test_monto_no_numerico():
    cliente = Cliente("Sofia", "Martinez", "99999999")
    tarjeta = Tarjeta("1234-5678-9012-3456", cliente)
    with pytest.raises(TypeError):
        tarjeta.realizar_compra("mil")
