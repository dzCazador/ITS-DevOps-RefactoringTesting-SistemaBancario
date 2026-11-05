"""DAO temporal del panel de personal (integración).

Hereda del DAO definitivo de Cristian (`src.dao.DAO`) y agrega solo lo
que la pantalla de gestión de clientes necesita y el DAO base aún no tiene:

- `obtener_todos_clientes()` (lista para el panel)
- `actualizar_persona_por_dni()` / `actualizar_cliente()` (edición)
- `guardar_cuenta()` con mensaje claro ante duplicado por tipo

Cuando BE-07/08/09 se reescriban (Andrés) y el DAO base incorpore estos
métodos, este archivo se elimina y `home_personal.py` vuelve a usar `DAO`.
"""

from typing import List, Tuple

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.dao import DAO, pwd_context
from src.modelos.models import ClienteModel, CuentaModel, PersonaModel


class DAOPersonal(DAO):
    """Extensión temporal para el panel de personal. Ver docstring del módulo."""

    def obtener_todos_clientes(self) -> List[Tuple]:
        with self.session_factory() as session:
            filas = session.execute(
                select(
                    ClienteModel.id_cliente,
                    PersonaModel.nombre,
                    PersonaModel.apellido,
                    PersonaModel.dni,
                    ClienteModel.categoria,
                    ClienteModel.estado,
                )
                .join(PersonaModel, ClienteModel.id_persona == PersonaModel.id_persona)
                .order_by(PersonaModel.apellido, PersonaModel.nombre)
            ).all()
            return [tuple(f) for f in filas]

    def actualizar_persona_por_dni(
        self,
        dni_actual: str,
        nombre: str,
        apellido: str,
        nuevo_dni: str,
        password: str | None = None,
    ) -> bool:
        try:
            with self.session_factory.begin() as session:
                persona = session.scalar(select(PersonaModel).where(PersonaModel.dni == dni_actual))
                if persona is None:
                    return False
                persona.nombre = nombre
                persona.apellido = apellido
                persona.dni = nuevo_dni
                if password:
                    persona.hashedpassword = pwd_context.hash(password)
            return True
        except IntegrityError as error:
            raise ValueError("Ya existe otra persona con ese DNI.") from error

    def actualizar_cliente(self, id_cliente: int, categoria: str | None, estado: str) -> bool:
        with self.session_factory.begin() as session:
            cliente = session.scalar(select(ClienteModel).where(ClienteModel.id_cliente == id_cliente))
            if cliente is None:
                return False
            cliente.categoria = categoria
            cliente.estado = estado
            return True

    def guardar_cuenta(
        self,
        nro_cuenta: str,
        id_cliente: int,
        id_tipo_cuenta: int,
        saldo: float = 0.0,
        tasa_interes: float | None = None,
    ) -> int:
        with self.session_factory() as session:
            if session.scalar(select(CuentaModel).where(CuentaModel.nro_cuenta == nro_cuenta)) is not None:
                raise ValueError(f"Ya existe una cuenta con número {nro_cuenta}.")
            if session.scalar(select(CuentaModel).where(
                CuentaModel.id_cliente == id_cliente,
                CuentaModel.id_tipo_cuenta == id_tipo_cuenta,
            )) is not None:
                raise ValueError("El cliente ya posee una cuenta de ese tipo.")
        return super().guardar_cuenta(
            nro_cuenta=nro_cuenta,
            id_cliente=id_cliente,
            id_tipo_cuenta=id_tipo_cuenta,
            saldo=saldo,
            tasa_interes=tasa_interes,
        )
