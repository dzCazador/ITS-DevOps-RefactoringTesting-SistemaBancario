from src.modelos.cliente import Cliente
from src.modelos.cuenta import Cuenta
from src.modelos.cuenta_ahorro import CuentaAhorro


_USUARIOS = None


def _crear_demo():
    """Datos de prueba/demo para la validación del login."""
    cliente_demo = Cliente("María", "Fernández", "40345678")
    cuentas_cliente = [
        Cuenta("200-987654/2", cliente_demo, 5400.00),
        CuentaAhorro("100-123456/1", cliente_demo, 12500.00, 1.5),
    ]

    personal_demo = Cliente("Carlos", "Gómez", "22233344")

    return [
        {
            "dni": "40345678",
            "clave": "1234",
            "rol": "cliente",
            "nombre": cliente_demo.get_nombre(),
            "apellido": cliente_demo.get_apellido(),
            "cuentas": cuentas_cliente,
        },
        {
            "dni": "22233344",
            "clave": "1234",
            "rol": "personal",
            "nombre": personal_demo.get_nombre(),
            "apellido": personal_demo.get_apellido(),
            "cuentas": [],
        },
    ]


def obtener_usuarios():
    global _USUARIOS
    if _USUARIOS is None:
        _USUARIOS = _crear_demo()
    return _USUARIOS


def autenticar(dni, clave):
    """Valida DNI/clave y devuelve el usuario (dict) o None si son incorrectos."""
    for usuario in obtener_usuarios():
        if usuario["dni"] == dni and usuario["clave"] == clave:
            return dict(usuario)
    return None