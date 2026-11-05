from src.modelos.cliente import Cliente
from src.dao import DAO
from src.modelos.persona import Persona


def test_cliente_hereda_de_persona():
    cliente = Cliente("Ana", "García", "12345678")

    assert isinstance(cliente, Persona)
    assert cliente.get_nombre() == "Ana"
    assert cliente.get_apellido() == "García"
    assert cliente.get_dni() == "12345678"


def test_persona_hash_y_verificacion_password():
    persona = Persona("Luis", "Pérez", "23456789", password="MiPassword123")

    assert persona.get_password_hash() != ""
    assert persona.verificar_password("MiPassword123") is True
    assert persona.verificar_password("OtraClave") is False


def test_validar_login_por_dni_y_password_encriptada():
    dao = DAO(db_path=":memory:")
    cliente = Cliente("Marta", "López", "34567890", password="Secreto456")

    id_cliente = dao.guardar_cliente(cliente)
    assert id_cliente > 0
    assert dao.validar_login_por_dni("34567890", "Secreto456") is True
    assert dao.validar_login_por_dni("34567890", "ClaveIncorrecta") is False

    dao.cerrar_conexion()
