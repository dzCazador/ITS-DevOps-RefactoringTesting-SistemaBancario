from datetime import datetime

import pytest

from src.autenticacion import Autenticacion
from src.cliente import Cliente
from src.cuenta import Cuenta
from src.dao import DAO
from src.persona import Persona
from src.persona_builder import EmpleadoBuilder


@pytest.fixture
def dao():
    instancia = DAO(db_path=":memory:")
    yield instancia
    instancia.cerrar_conexion()


def test_autenticar_cliente_devuelve_identidad_rol_y_cuentas(dao):
    cliente = Cliente("María", "Fernández", "40345678", password="ClaveSegura1")
    id_cliente = dao.guardar_cliente(cliente)
    id_tipo_cuenta = dao.guardar_tipo_cuenta("Ahorro")
    dao.guardar_cuenta("AR-001", id_cliente, id_tipo_cuenta, saldo=1250.0)

    resultado = Autenticacion(dao).autenticar("40345678", "ClaveSegura1")

    assert resultado is not None
    assert set(resultado) == {"dni", "nombre", "apellido", "rol", "cuentas"}
    assert resultado["dni"] == "40345678"
    assert resultado["nombre"] == "María"
    assert resultado["apellido"] == "Fernández"
    assert resultado["rol"] == "cliente"
    assert len(resultado["cuentas"]) == 1
    assert isinstance(resultado["cuentas"][0], Cuenta)
    assert resultado["cuentas"][0].get_nro_cuenta() == "AR-001"
    assert resultado["cuentas"][0].get_saldo() == 1250.0


def test_autenticar_cliente_sin_cuentas_devuelve_lista_vacia(dao):
    dao.guardar_cliente(Cliente("Ana", "Lopez", "12345678", password="ClaveSegura2"))

    resultado = Autenticacion(dao).autenticar("12345678", "ClaveSegura2")

    assert resultado is not None
    assert resultado["rol"] == "cliente"
    assert resultado["cuentas"] == []


def test_autenticar_personal_devuelve_rol_sin_cuentas(dao):
    empleado = (
        EmpleadoBuilder()
        .con_nombre("Luis")
        .con_apellido("Pérez")
        .con_dni("23456789")
        .con_password("ClaveSegura3")
        .con_legajo("E-1001")
        .con_cargo("Analista")
        .con_departamento("Sistemas")
        .con_fecha_ingreso(datetime(2024, 1, 15))
        .con_salario(85000)
        .con_sucursal("Central")
        .build()
    )
    dao.guardar_empleado(
        empleado,
        legajo="E-1001",
        cargo="Analista",
        departamento="Sistemas",
        fecha_ingreso=datetime(2024, 1, 15),
        salario=85000,
        sucursal="Central",
    )

    resultado = Autenticacion(dao).autenticar("23456789", "ClaveSegura3")

    assert resultado is not None
    assert resultado["rol"] == "personal"
    assert resultado["cuentas"] == []


def test_autenticar_falla_con_dni_inexistente_o_clave_incorrecta(dao):
    dao.guardar_cliente(Cliente("Marta", "Sánchez", "34567890", password="ClaveSegura4"))
    servicio = Autenticacion(dao)

    assert servicio.autenticar("99999999", "ClaveSegura4") is None
    assert servicio.autenticar("34567890", "ClaveIncorrecta") is None
    assert servicio.autenticar("", "ClaveSegura4") is None


def test_autenticar_falla_si_la_persona_no_tiene_rol(dao):
    dao.guardar_persona(Persona("Persona", "SinRol", "45678901", password="ClaveSegura5"))

    resultado = Autenticacion(dao).autenticar("45678901", "ClaveSegura5")

    assert resultado is None
