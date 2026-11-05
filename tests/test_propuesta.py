import pytest
from src.modelos.cliente import Cliente
from src.modelos.cuenta import Cuenta, SaldoInsuficienteError
from src.modelos.cuenta_ahorro import CuentaAhorro
from src.dao import DAO

def test_infraestructura_tests_activa():
    """Verifica que la suite de pruebas y pytest están funcionando correctamente."""
    assert True

def test_depositos_y_retiros():
    """T-04 (BE-10/BE-11): Verifica depósitos, retiros e intereses con persistencia en SQLite."""
    # 1. DAO en memoria para pruebas aisladas
    dao = DAO(":memory:")
    
    # Registramos los tipos de cuenta para obtener sus IDs (SQLite Foreign Key)
    id_tipo_cc = dao.guardar_tipo_cuenta("Corriente", "Cuenta Corriente")
    id_tipo_ca = dao.guardar_tipo_cuenta("Ahorro", "Cuenta de Ahorro")
    
    # Registramos los tipos de transacción para el catálogo
    id_tipo_dep = dao.guardar_tipo_transaccion("deposito", "Depósito de dinero")
    id_tipo_ret = dao.guardar_tipo_transaccion("retiro", "Retiro de dinero")
    id_tipo_int = dao.guardar_tipo_transaccion("interes", "Pago de intereses")
    
    # 2. Registrar cliente y cuentas
    cliente = Cliente("Daniel", "DevOps", "30999888")
    id_cliente = dao.guardar_cliente(cliente)
    
    # Usamos los IDs enteros devueltos por guardar_tipo_cuenta
    id_cc = dao.guardar_cuenta("CC-101", id_cliente, id_tipo_cc, saldo=500.0)
    cuenta_cc = Cuenta("CC-101", cliente, saldo=500.0, id_cuenta=id_cc)
    
    id_ca = dao.guardar_cuenta("CA-202", id_cliente, id_tipo_ca, saldo=1000.0, tasa_interes=5.0)
    cuenta_ca = CuentaAhorro("CA-202", cliente, saldo=1000.0, interes=5.0, id_cuenta=id_ca)
    
    # 3. Comprobar Depósito
    cuenta_cc.depositar(200.0)
    dao.actualizar_saldo_cuenta(id_cc, cuenta_cc.get_saldo())
    dao.guardar_transaccion(id_cc, id_tipo_dep, 200.0)
    assert cuenta_cc.get_saldo() == 700.0
    cuenta_db = dao.obtener_cuenta_por_numero("CC-101")
    assert cuenta_db[4] == 700.0  # El saldo en BD se actualizó
    
    # 4. Comprobar Retiro
    cuenta_cc.retirar(150.0)
    dao.actualizar_saldo_cuenta(id_cc, cuenta_cc.get_saldo())
    dao.guardar_transaccion(id_cc, id_tipo_ret, 150.0)
    assert cuenta_cc.get_saldo() == 550.0
    cuenta_db = dao.obtener_cuenta_por_numero("CC-101")
    assert cuenta_db[4] == 550.0  # El saldo en BD se actualizó
    
    # 5. Comprobar Saldo Insuficiente (no altera BD)
    with pytest.raises(SaldoInsuficienteError):
        cuenta_cc.retirar(9000.0)
    assert dao.obtener_cuenta_por_numero("CC-101")[4] == 550.0
    
    # 6. Comprobar Interés en Cuenta Ahorro
    cuenta_ca.aplicar_interes()  # 1000 + 5% = 1050.0
    dao.actualizar_saldo_cuenta(id_ca, cuenta_ca.get_saldo())
    dao.guardar_transaccion(id_ca, id_tipo_int, 50.0)
    assert cuenta_ca.get_saldo() == 1050.0
    ca_db = dao.obtener_cuenta_por_numero("CA-202")
    assert ca_db[4] == 1050.0
    
    # 7. Comprobar Persistencia de Transacciones
    txs_cc = dao.obtener_transacciones_por_cuenta(id_cc)
    assert len(txs_cc) == 2
    assert txs_cc[0][2] == id_tipo_dep and txs_cc[0][3] == 200.0
    assert txs_cc[1][2] == id_tipo_ret and txs_cc[1][3] == 150.0
    
    txs_ca = dao.obtener_transacciones_por_cuenta(id_ca)
    assert len(txs_ca) == 1
    assert txs_ca[0][2] == id_tipo_int and txs_ca[0][3] == 50.0
    
    dao.cerrar_conexion()

@pytest.mark.skip(reason="T-01: Esperando merge de Cristian (BE-01/BE-05) para probar PersonaModel y Login.")
def test_autenticacion_persona(db_session):
    pass

@pytest.mark.skip(reason="T-02: Esperando merge de Cristian (BE-03) para probar constraint una cuenta por tipo.")
def test_constraint_una_cuenta_por_tipo(db_session):
    pass

@pytest.mark.skip(reason="T-03: Esperando merge de Andrés (BE-07/BE-09) para probar alta y edición de cliente.")
def test_alta_y_edicion_cliente(db_session):
    pass