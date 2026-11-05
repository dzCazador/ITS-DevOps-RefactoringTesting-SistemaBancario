"""Tests de los patrones de diseño aplicados en la refactorización.

Cubre:
- Singleton: DatabaseConnection comparte el Engine entre instancias.
- Factory Method: CuentaFactory crea la subclase correcta según el tipo.
- Builder: PersonaBuilder/ClienteBuilder/EmpleadoBuilder construyen
  objetos válidos paso a paso.
"""

from datetime import datetime

import pytest

from src.modelos.cliente import Cliente
from src.modelos.cuenta import Cuenta
from src.modelos.cuenta_ahorro import CuentaAhorro
from src.modelos.cuenta_factory import CuentaFactory
from src.dao import DAO
from src.database import DatabaseConnection
from src.modelos.empleado import Empleado
from src.modelos.persona_builder import ClienteBuilder, EmpleadoBuilder, PersonaBuilder


# ============================================================
# SINGLETON
# ============================================================

class TestSingleton:
    def setup_method(self):
        DatabaseConnection.reset()

    def teardown_method(self):
        DatabaseConnection.reset()

    def test_misma_ruta_devuelve_la_misma_instancia(self):
        conn1 = DatabaseConnection.instance(":memory:")
        conn2 = DatabaseConnection.instance(":memory:")
        assert conn1 is conn2

    def test_daos_comparten_el_mismo_engine(self):
        dao1 = DAO(":memory:")
        dao2 = DAO(":memory:")
        assert dao1.engine is dao2.engine

    def test_reset_descarta_la_instancia(self):
        conn1 = DatabaseConnection.instance(":memory:")
        DatabaseConnection.reset()
        conn2 = DatabaseConnection.instance(":memory:")
        assert conn1 is not conn2


# ============================================================
# FACTORY METHOD
# ============================================================

class TestCuentaFactory:
    def setup_method(self):
        self.cliente = Cliente("Ana", "García", "12345678")

    def test_crear_cuenta_corriente(self):
        cuenta = CuentaFactory.crear("Corriente", "CC-001", self.cliente, saldo=500.0)
        assert isinstance(cuenta, Cuenta)
        assert not isinstance(cuenta, CuentaAhorro)
        assert cuenta.get_nro_cuenta() == "CC-001"
        assert cuenta.get_saldo() == 500.0

    def test_crear_cuenta_ahorro(self):
        cuenta = CuentaFactory.crear("Ahorro", "CA-001", self.cliente, saldo=1000.0, interes=5.0)
        assert isinstance(cuenta, CuentaAhorro)
        assert cuenta.get_interes() == 5.0

    def test_tipo_es_case_insensitive(self):
        cuenta = CuentaFactory.crear("ahorro", "CA-002", self.cliente)
        assert isinstance(cuenta, CuentaAhorro)

    def test_tipo_desconocido_lanza_error(self):
        with pytest.raises(ValueError, match="Tipo de cuenta desconocido"):
            CuentaFactory.crear("PlazoFijo", "PF-001", self.cliente)

    def test_crear_desde_fila_ahorro(self):
        fila = (1, "CA-100", 10, 2, 1500.0, 3.5, datetime(2024, 5, 1))
        cuenta = CuentaFactory.crear_desde_fila(fila, self.cliente, "Ahorro")
        assert isinstance(cuenta, CuentaAhorro)
        assert cuenta.get_id_cuenta() == 1
        assert cuenta.get_saldo() == 1500.0
        assert cuenta.get_interes() == 3.5

    def test_crear_desde_fila_corriente(self):
        fila = (2, "CC-200", 10, 1, 800.0, None, datetime(2024, 5, 1))
        cuenta = CuentaFactory.crear_desde_fila(fila, self.cliente, "Corriente")
        assert type(cuenta) is Cuenta
        assert cuenta.get_nro_cuenta() == "CC-200"

    def test_registrar_nuevo_tipo_ocp(self):
        """Open/Closed: se puede extender sin modificar la factory."""
        CuentaFactory.registrar("Sueldo", lambda nro, cli, saldo, **kw: Cuenta(nro, cli, saldo))
        cuenta = CuentaFactory.crear("Sueldo", "SU-001", self.cliente, saldo=100.0)
        assert isinstance(cuenta, Cuenta)


# ============================================================
# BUILDER
# ============================================================

class TestBuilders:
    def test_persona_builder(self):
        persona = (
            PersonaBuilder()
            .con_nombre("Juan")
            .con_apellido("Pérez")
            .con_dni("30111222")
            .con_password("Clave123")
            .build()
        )
        assert persona.get_nombre() == "Juan"
        assert persona.get_apellido() == "Pérez"
        assert persona.get_dni() == "30111222"
        assert persona.verificar_password("Clave123")

    def test_cliente_builder(self):
        cliente = (
            ClienteBuilder()
            .con_nombre("María")
            .con_apellido("López")
            .con_dni("27333444")
            .con_password("Clave456")
            .con_categoria("PREMIUM")
            .build()
        )
        assert isinstance(cliente, Cliente)
        assert cliente.get_categoria() == "PREMIUM"
        assert cliente.get_estado() == "ACTIVO"

    def test_empleado_builder(self):
        empleado = (
            EmpleadoBuilder()
            .con_nombre("Luis")
            .con_apellido("Pérez")
            .con_dni("23456789")
            .con_password("Clave789")
            .con_legajo("E-1001")
            .con_cargo("Analista")
            .con_departamento("Sistemas")
            .con_fecha_ingreso(datetime(2024, 1, 15))
            .con_salario(85000)
            .con_sucursal("Central")
            .build()
        )
        assert isinstance(empleado, Empleado)
        assert empleado.get_legajo() == "E-1001"
        assert empleado.get_salario() == 85000
        assert empleado.get_sucursal() == "Central"

    def test_builder_respeta_validaciones_de_dominio(self):
        """build() delega en el constructor: las validaciones no se saltean."""
        with pytest.raises(ValueError):
            ClienteBuilder().con_nombre("").con_apellido("López").con_dni("123").build()

    def test_builder_dni_invalido(self):
        with pytest.raises(ValueError, match="DNI"):
            PersonaBuilder().con_nombre("Ana").con_apellido("García").con_dni("abc123").build()
