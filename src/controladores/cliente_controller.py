"""Use cases for client and account management.

Serves both the personal panel (home_personal, home_crear_cliente) and the
legacy management screen (vista_gestion_clientes) through the same DAO.
"""

from sqlalchemy import select

from src import gestion_clientes
from src.cliente import Cliente
from src.cuenta import Cuenta
from src.cuenta_ahorro import CuentaAhorro
from src.models import TipoCuentaModel


def nombres_tipo_cuenta(dao) -> dict[int, str]:
    """Map id_tipo_cuenta -> nombre, read from the database."""
    with dao.connect() as session:
        return {
            fila.id_tipo_cuenta: fila.nombre
            for fila in session.scalars(select(TipoCuentaModel)).all()
        }


class ClienteController:
    def __init__(self, dao):
        self._dao = dao

    # ---- Panel de personal ------------------------------------------------

    def listar_clientes(self) -> list:
        return self._dao.obtener_todos_clientes()

    def obtener_cliente_por_dni(self, dni: str):
        return self._dao.obtener_cliente_por_dni(dni)

    def listar_cuentas(self, id_cliente: int) -> list:
        return self._dao.obtener_cuentas_por_cliente(id_cliente)

    def etiquetas_cuentas(self, id_cliente: int) -> list[str]:
        """Labels ("Caja de ahorro" / "Corriente") for the client's accounts.

        Keeps the rule the original view used on DAO tuples: the label is
        derived from the account number text. Errors yield no labels.
        """
        try:
            cuentas = self._dao.obtener_cuentas_por_cliente(id_cliente)
        except Exception:
            cuentas = []

        etiquetas = []
        for cuenta in cuentas:
            if isinstance(cuenta, (list, tuple)) and len(cuenta) > 1:
                etiquetas.append(
                    "Caja de ahorro" if "ahorro" in str(cuenta[1]).lower() else "Corriente"
                )
            else:
                etiquetas.append("Corriente")
        return etiquetas

    @staticmethod
    def nombre_tipo_cuenta(cuenta) -> str:
        """Display name for a domain account object (client home)."""
        if isinstance(cuenta, CuentaAhorro):
            return "Caja de Ahorro"
        if isinstance(cuenta, Cuenta):
            return "Corriente"
        return "Cuenta"

    def crear_cliente(self, nombre: str, apellido: str, dni: str, clave: str | None) -> int:
        return self._dao.guardar_cliente(Cliente(nombre, apellido, dni, password=clave))

    def actualizar_cliente(
        self, dni_actual: str, nombre: str, apellido: str, nuevo_dni: str, clave: str | None
    ) -> bool:
        """Update a client's personal data. Validates the new data first."""
        Cliente(nombre, apellido, nuevo_dni)  # validates the entity fields
        return self._dao.actualizar_persona_por_dni(
            dni_actual,
            nombre.title(),
            apellido.title(),
            nuevo_dni,
            password=clave,
        )

    def resolver_id_tipo_cuenta(self, nombre_tipo: str) -> int | None:
        try:
            return self._dao.guardar_tipo_cuenta(nombre_tipo)
        except ValueError:
            with self._dao.connect() as session:
                fila = session.scalar(
                    select(TipoCuentaModel).where(TipoCuentaModel.nombre == nombre_tipo)
                )
                return fila.id_tipo_cuenta if fila is not None else None

    def agregar_cuenta(self, id_cliente: int, nro: str, nombre_tipo: str | None, saldo_texto: str | None) -> int:
        """Create an account for a stored client.

        :raises ValueError: with the user-facing message on invalid input.
        """
        nro = (nro or "").strip()
        if not nro or not nombre_tipo:
            raise ValueError("Completá número y tipo.")

        try:
            saldo = float((saldo_texto or "0").strip() or 0)
        except ValueError:
            raise ValueError("El saldo debe ser un número.")

        if saldo < 0:
            raise ValueError("El saldo no puede ser negativo.")

        id_tipo = self.resolver_id_tipo_cuenta(nombre_tipo)
        if id_tipo is None:
            raise ValueError("No se pudo resolver el tipo de cuenta.")

        return self._dao.guardar_cuenta(nro, id_cliente, id_tipo, saldo=saldo)

    # ---- Gestion de clientes (BE-07 / BE-08 / BE-09) ----------------------

    def alta_cliente(self, nombre, apellido, dni, password=None) -> int:
        return gestion_clientes.alta_cliente(self._dao, nombre, apellido, dni, password=password)

    def alta_cuenta(self, dni, nro_cuenta, tipo_cuenta, saldo_inicial=0.0) -> int:
        return gestion_clientes.alta_cuenta(
            self._dao,
            dni=dni,
            nro_cuenta=nro_cuenta,
            tipo_cuenta=tipo_cuenta,
            saldo_inicial=saldo_inicial,
        )

    def editar_cliente(self, dni_actual, nuevo_nombre, nuevo_apellido, nuevo_dni, password=None) -> bool:
        return gestion_clientes.editar_cliente(
            self._dao,
            dni_actual=dni_actual,
            nuevo_nombre=nuevo_nombre,
            nuevo_apellido=nuevo_apellido,
            nuevo_dni=nuevo_dni,
            password=password,
        )
