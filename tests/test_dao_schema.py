from src.modelos.cliente import Cliente
from src.dao import DAO
from src.modelos.models import Base


def test_metadata_incluye_todas_las_tablas_del_esquema():
    tablas = set(Base.metadata.tables.keys())

    esperadas = {
        "persona",
        "cliente",
        "empleado",
        "tipo_cuenta",
        "tipo_transaccion",
        "cuenta",
        "transaccion",
    }

    assert esperadas.issubset(tablas)


def test_dao_tiene_metodos_para_persona_y_catalogos():
    dao = DAO(db_path=":memory:")

    assert hasattr(dao, "guardar_persona")
    assert hasattr(dao, "obtener_persona_por_dni")
    assert hasattr(dao, "guardar_cliente")
    assert hasattr(dao, "guardar_empleado")
    assert hasattr(dao, "guardar_tipo_cuenta")
    assert hasattr(dao, "guardar_tipo_transaccion")
    assert hasattr(dao, "guardar_cuenta")
    assert hasattr(dao, "guardar_transaccion")
    assert hasattr(dao, "validar_login_por_dni")

    dao.cerrar_conexion()


def test_guardar_transaccion_acepta_tipo_real_del_catalogo():
    dao = DAO(db_path=":memory:")

    id_cliente = dao.guardar_cliente(Cliente("Ana", "García", "12345678"))
    id_tipo_cuenta = dao.guardar_tipo_cuenta("Ahorro", "Cuenta de ahorro")
    id_tipo_transaccion = dao.guardar_tipo_transaccion("pagoIntereses", "Pago por intereses")
    id_cuenta = dao.guardar_cuenta("ABC-001", id_cliente, id_tipo_cuenta, saldo=1000.0)

    id_transaccion = dao.guardar_transaccion(id_cuenta, "pagoIntereses", 150.0)

    assert id_transaccion > 0
    assert dao.obtener_transacciones_por_cuenta(id_cuenta)[0][2] == id_tipo_transaccion

    dao.cerrar_conexion()
