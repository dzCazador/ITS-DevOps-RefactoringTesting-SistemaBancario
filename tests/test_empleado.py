from src.modelos.empleado import Empleado


def test_crear_empleado_valido():
    empleado = Empleado(
        "Carlos",
        "Ruiz",
        "11223344",
        legajo="E-1001",
        cargo="Analista",
        departamento="Sistemas",
        fecha_ingreso="2024-01-15",
        salario=85000,
        sucursal="Caballito",
        password="Clave123",
    )

    assert empleado.get_nombre() == "Carlos"
    assert empleado.get_apellido() == "Ruiz"
    assert empleado.get_dni() == "11223344"
    assert empleado.get_legajo() == "E-1001"
    assert empleado.verificar_password("Clave123") is True


def test_empleado_datos_obligatorios():
    try:
        Empleado("", "Ruiz", "11223344", legajo="E-1001", cargo="Analista", departamento="Sistemas", fecha_ingreso="2024-01-15", salario=85000, sucursal="Caballito")
        assert False
    except ValueError:
        assert True
