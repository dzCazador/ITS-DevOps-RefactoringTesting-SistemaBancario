"""Patrón Builder para construir entidades del dominio paso a paso.

Las clases ``Empleado`` y ``Cliente`` tienen constructores con muchos
parámetros (el de ``Empleado`` recibe 10), lo que hacía las llamadas
difíciles de leer y propensas a errores de orden. El Builder permite
construir los objetos de forma fluida y legible::

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

Las validaciones siguen viviendo en los constructores de dominio:
``build()`` simplemente delega, por lo que ninguna regla se saltea.
"""

from src.modelos.cliente import Cliente
from src.modelos.empleado import Empleado
from src.modelos.persona import Persona


class PersonaBuilder:
    """Builder base con los datos comunes a toda persona."""

    _clase = Persona

    def __init__(self):
        self._nombre = None
        self._apellido = None
        self._dni = None
        self._password = None

    def con_nombre(self, nombre: str) -> "PersonaBuilder":
        self._nombre = nombre
        return self

    def con_apellido(self, apellido: str) -> "PersonaBuilder":
        self._apellido = apellido
        return self

    def con_dni(self, dni: str) -> "PersonaBuilder":
        self._dni = dni
        return self

    def con_password(self, password: str) -> "PersonaBuilder":
        self._password = password
        return self

    def _datos_base(self) -> dict:
        return {
            "nombre": self._nombre,
            "apellido": self._apellido,
            "dni": self._dni,
            "password": self._password,
        }

    def build(self) -> Persona:
        return self._clase(**self._datos_base())


class ClienteBuilder(PersonaBuilder):
    """Builder de clientes: datos de persona + categoría y estado."""

    _clase = Cliente

    def __init__(self):
        super().__init__()
        self._categoria = None
        self._estado = "ACTIVO"

    def con_categoria(self, categoria: str) -> "ClienteBuilder":
        self._categoria = categoria
        return self

    def con_estado(self, estado: str) -> "ClienteBuilder":
        self._estado = estado
        return self

    def build(self) -> Cliente:
        return Cliente(
            **self._datos_base(),
            categoria=self._categoria,
            estado=self._estado,
        )


class EmpleadoBuilder(PersonaBuilder):
    """Builder de empleados: datos de persona + datos laborales."""

    def __init__(self):
        super().__init__()
        self._legajo = None
        self._cargo = None
        self._departamento = None
        self._fecha_ingreso = None
        self._salario = None
        self._sucursal = None

    def con_legajo(self, legajo: str) -> "EmpleadoBuilder":
        self._legajo = legajo
        return self

    def con_cargo(self, cargo: str) -> "EmpleadoBuilder":
        self._cargo = cargo
        return self

    def con_departamento(self, departamento: str) -> "EmpleadoBuilder":
        self._departamento = departamento
        return self

    def con_fecha_ingreso(self, fecha_ingreso) -> "EmpleadoBuilder":
        self._fecha_ingreso = fecha_ingreso
        return self

    def con_salario(self, salario: float) -> "EmpleadoBuilder":
        self._salario = salario
        return self

    def con_sucursal(self, sucursal: str) -> "EmpleadoBuilder":
        self._sucursal = sucursal
        return self

    def build(self) -> Empleado:
        return Empleado(
            **self._datos_base(),
            legajo=self._legajo,
            cargo=self._cargo,
            departamento=self._departamento,
            fecha_ingreso=self._fecha_ingreso,
            salario=self._salario,
            sucursal=self._sucursal,
        )
