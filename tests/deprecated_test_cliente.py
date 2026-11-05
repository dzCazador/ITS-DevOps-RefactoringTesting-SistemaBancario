import pytest
from src.modelos.cliente import Cliente


def test_crear_cliente_valido():
    cliente = Cliente("Ana", "López", "12345678")
    assert cliente.get_nombre() == "Ana"
    assert cliente.get_apellido() == "López"
    assert cliente.get_dni() == "12345678"


def test_cliente_nombre_vacio():
    with pytest.raises(ValueError, match="Todos los campos del cliente son obligatorios."):
        Cliente("", "López", "12345678")


def test_cliente_dni_vacio():
    with pytest.raises(ValueError, match="Todos los campos del cliente son obligatorios."):
        Cliente("Ana", "López", "")


def test_cliente_nombre_con_numeros():
    # No debe permitir números en el nombre
    with pytest.raises(ValueError, match="solo letras"):
        Cliente("Ana123", "López", "12345678")


def test_cliente_apellido_con_simbolos():
    # No debe permitir símbolos en el apellido
    with pytest.raises(ValueError, match="solo letras"):
        Cliente("Ana", "López@", "12345678")


def test_cliente_dni_con_letras():
    # No debe permitir letras en el DNI
    with pytest.raises(ValueError, match="solo números"):
        Cliente("Ana", "López", "12A45B78")
