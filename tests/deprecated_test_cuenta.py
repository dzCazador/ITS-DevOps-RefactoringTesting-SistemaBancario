import pytest
from src.modelos.cliente import Cliente
from src.modelos.cuenta import Cuenta, SaldoInsuficienteError


def test_crear_cuenta_valida():
    cliente = Cliente("Juan", "Perez", "11111111")
    cuenta = Cuenta("001", cliente, saldo=500.0)
    assert cuenta.get_saldo() == 500.0
    assert cuenta.get_cliente().get_nombre() == "Juan"


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
