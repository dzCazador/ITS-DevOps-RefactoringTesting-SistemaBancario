from src.modelos.cuenta_ahorro import CuentaAhorro
from src.modelos.cliente import Cliente


def test_crear_cuenta_ahorro():
    cliente = Cliente("Lucía", "Martinez", "44556677")
    cuenta_ahorro = CuentaAhorro("005", cliente, saldo=1000, interes=2.0)
    assert cuenta_ahorro.get_interes() == 2.0
    assert cuenta_ahorro.get_saldo() == 1000


def test_aplicar_interes():
    cliente = Cliente("Mario", "Diaz", "99887766")
    cuenta_ahorro = CuentaAhorro("006", cliente, saldo=1000, interes=5.0)
    nuevo_saldo = cuenta_ahorro.aplicar_interes()
    assert round(nuevo_saldo, 2) == 1050.00
