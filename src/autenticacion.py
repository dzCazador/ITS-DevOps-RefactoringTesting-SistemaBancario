from sqlalchemy import select

from src.cliente import Cliente
from src.cuenta import Cuenta
from src.cuenta_factory import CuentaFactory
from src.dao import DAO
from src.models import EmpleadoModel, TipoCuentaModel


class Autenticacion:
    def __init__(self, dao: DAO):
        self.dao = dao

    def autenticar(self, dni: str, clave: str) -> dict | None:
        if not dni or not clave:
            return None

        persona = self.dao.obtener_persona_por_dni(dni)
        if persona is None or not self.dao.validar_login_por_dni(dni, clave):
            return None

        rol_y_cuentas = self._resolver_rol_y_cuentas(dni, persona[0])
        if rol_y_cuentas is None:
            return None

        rol, cuentas = rol_y_cuentas
        return {
            "dni": persona[3],
            "nombre": persona[1],
            "apellido": persona[2],
            "rol": rol,
            "cuentas": cuentas,
        }

    def _resolver_rol_y_cuentas(
        self, dni: str, id_persona: int
    ) -> tuple[str, list[Cuenta]] | None:
        datos_cliente = self.dao.obtener_cliente_por_dni(dni)
        if datos_cliente is not None:
            return "cliente", self._obtener_cuentas(datos_cliente)

        if self._es_personal(id_persona):
            return "personal", []

        return None

    def _obtener_cuentas(self, datos_cliente: tuple) -> list[Cuenta]:
        id_cliente, nombre, apellido, dni, _ = datos_cliente
        cliente = Cliente(nombre, apellido, dni)
        filas = self.dao.obtener_cuentas_por_cliente(id_cliente)
        nombres_tipo = self._nombres_tipo_cuenta()
        return [
            CuentaFactory.crear_desde_fila(
                fila, cliente, nombres_tipo.get(fila[3], "")
            )
            for fila in filas
        ]

    def _nombres_tipo_cuenta(self) -> dict[int, str]:
        with self.dao.connect() as session:
            return {
                row.id_tipo_cuenta: row.nombre
                for row in session.scalars(select(TipoCuentaModel)).all()
            }

    def _es_personal(self, id_persona: int) -> bool:
        with self.dao.connect() as session:
            id_empleado = session.scalar(
                select(EmpleadoModel.id_empleado).where(
                    EmpleadoModel.id_persona == id_persona
                )
            )
            return id_empleado is not None
