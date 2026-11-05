from typing import List, Optional, Tuple

from passlib.context import CryptContext
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from src.modelos.cliente import Cliente
from src.database import DatabaseConnection
from src.modelos.models import (
    Base,
    ClienteModel,
    CuentaModel,
    EmpleadoModel,
    PersonaModel,
    TipoCuentaModel,
    TipoTransaccionModel,
    TransaccionModel,
)
from src.modelos.persona import Persona

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class DAO:
    """Data Access Object para la persistencia bancaria con SQLAlchemy y SQLite.

    La conexión (``Engine``) se obtiene del Singleton
    :class:`src.database.DatabaseConnection`, por lo que todos los DAO
    creados con el mismo ``db_path`` comparten la misma conexión física.
    """

    def __init__(self, db_path: str = "sistema_bancario.db"):
        self.db_path = db_path
        self.engine = DatabaseConnection.instance(db_path).engine
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.create_tables()

    def connect(self):
        return self.session_factory()

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    @staticmethod
    def _persona_tuple(item: PersonaModel) -> Tuple:
        return (
            item.id_persona,
            item.nombre,
            item.apellido,
            item.dni,
            item.hashedpassword,
            item.email,
            item.telefono,
            item.direccion,
            item.fecha_registro,
        )

    @staticmethod
    def _cliente_tuple(item: ClienteModel) -> Tuple:
        return item.id_cliente, item.id_persona, item.categoria, item.estado

    @staticmethod
    def _empleado_tuple(item: EmpleadoModel) -> Tuple:
        return (
            item.id_empleado,
            item.id_persona,
            item.legajo,
            item.cargo,
            item.departamento,
            item.fecha_ingreso,
            item.salario,
            item.sucursal,
        )

    @staticmethod
    def _tipo_cuenta_tuple(item: TipoCuentaModel) -> Tuple:
        return item.id_tipo_cuenta, item.nombre, item.descripcion

    @staticmethod
    def _tipo_transaccion_tuple(item: TipoTransaccionModel) -> Tuple:
        return item.id_tipo_transaccion, item.nombre, item.descripcion

    @staticmethod
    def _cuenta_tuple(item: CuentaModel) -> Tuple:
        return (
            item.id_cuenta,
            item.nro_cuenta,
            item.id_cliente,
            item.id_tipo_cuenta,
            item.saldo,
            item.tasa_interes,
            item.fecha_creacion,
        )

    @staticmethod
    def _transaccion_tuple(item: TransaccionModel) -> Tuple:
        return item.id_transaccion, item.id_cuenta, item.id_tipo_transaccion, item.monto, item.fecha

    def guardar_persona(self, persona: Persona) -> int:
        try:
            with self.session_factory.begin() as session:
                item = PersonaModel(
                    nombre=persona.get_nombre(),
                    apellido=persona.get_apellido(),
                    dni=persona.get_dni(),
                    hashedpassword=persona.get_password_hash(),
                    email=getattr(persona, "get_email", lambda: None)(),
                    telefono=getattr(persona, "get_telefono", lambda: None)(),
                    direccion=getattr(persona, "get_direccion", lambda: None)(),
                )
                session.add(item)
                session.flush()
                return item.id_persona
        except IntegrityError as error:
            raise ValueError(f"Ya existe una persona con DNI {persona.get_dni()}") from error

    def obtener_persona_por_dni(self, dni: str) -> Optional[Tuple]:
        with self.session_factory() as session:
            item = session.scalar(select(PersonaModel).where(PersonaModel.dni == dni))
            return self._persona_tuple(item) if item else None

    def guardar_cliente(self, cliente: Cliente, categoria: str = "NORMAL", estado: str = "ACTIVO") -> int:
        id_persona = self.guardar_persona(cliente)
        try:
            with self.session_factory.begin() as session:
                item = ClienteModel(id_persona=id_persona, categoria=categoria, estado=estado)
                session.add(item)
                session.flush()
                return item.id_cliente
        except IntegrityError as error:
            raise ValueError(f"Ya existe un cliente para la persona DNI {cliente.get_dni()}") from error

    def obtener_cliente_por_dni(self, dni: str) -> Optional[Tuple]:
        with self.session_factory() as session:
            persona = session.scalar(select(PersonaModel).where(PersonaModel.dni == dni))
            if not persona:
                return None
            cliente = session.scalar(select(ClienteModel).where(ClienteModel.id_persona == persona.id_persona))
            if not cliente:
                return None
            return (
                cliente.id_cliente,
                persona.nombre,
                persona.apellido,
                persona.dni,
                persona.fecha_registro,
            )

    def guardar_empleado(
        self,
        persona: Persona,
        legajo: str,
        cargo: str,
        departamento: str,
        fecha_ingreso,
        salario: float,
        sucursal: str,
    ) -> int:
        id_persona = self.guardar_persona(persona)
        try:
            with self.session_factory.begin() as session:
                item = EmpleadoModel(
                    id_persona=id_persona,
                    legajo=legajo,
                    cargo=cargo,
                    departamento=departamento,
                    fecha_ingreso=fecha_ingreso,
                    salario=salario,
                    sucursal=sucursal,
                )
                session.add(item)
                session.flush()
                return item.id_empleado
        except IntegrityError as error:
            raise ValueError(f"Ya existe un empleado con legajo {legajo}") from error

    def guardar_tipo_cuenta(self, nombre: str, descripcion: str | None = None) -> int:
        try:
            with self.session_factory.begin() as session:
                item = TipoCuentaModel(nombre=nombre, descripcion=descripcion)
                session.add(item)
                session.flush()
                return item.id_tipo_cuenta
        except IntegrityError as error:
            raise ValueError(f"Ya existe un tipo de cuenta con nombre {nombre}") from error

    def guardar_tipo_transaccion(self, nombre: str, descripcion: str | None = None) -> int:
        try:
            with self.session_factory.begin() as session:
                item = TipoTransaccionModel(nombre=nombre, descripcion=descripcion)
                session.add(item)
                session.flush()
                return item.id_tipo_transaccion
        except IntegrityError as error:
            raise ValueError(f"Ya existe un tipo de transacción con nombre {nombre}") from error

    def guardar_cuenta(
        self,
        nro_cuenta: str,
        id_cliente: int,
        id_tipo_cuenta: int,
        saldo: float = 0.0,
        tasa_interes: float | None = None,
    ) -> int:
        try:
            with self.session_factory.begin() as session:
                item = CuentaModel(
                    nro_cuenta=nro_cuenta,
                    id_cliente=id_cliente,
                    id_tipo_cuenta=id_tipo_cuenta,
                    saldo=saldo,
                    tasa_interes=tasa_interes,
                )
                session.add(item)
                session.flush()
                return item.id_cuenta
        except IntegrityError as error:
            raise ValueError(f"Ya existe una cuenta con número {nro_cuenta}") from error

    def obtener_cuentas_por_cliente(self, id_cliente: int) -> List[Tuple]:
        with self.session_factory() as session:
            items = session.scalars(
                select(CuentaModel).where(CuentaModel.id_cliente == id_cliente).order_by(CuentaModel.fecha_creacion.desc())
            ).all()
            return [self._cuenta_tuple(item) for item in items]

    def obtener_cuenta_por_numero(self, nro_cuenta: str) -> Optional[Tuple]:
        with self.session_factory() as session:
            item = session.scalar(select(CuentaModel).where(CuentaModel.nro_cuenta == nro_cuenta))
            return self._cuenta_tuple(item) if item else None

    def actualizar_saldo_cuenta(self, id_cuenta: int, nuevo_saldo: float) -> bool:
        try:
            with self.session_factory.begin() as session:
                session.execute(
                    update(CuentaModel).where(CuentaModel.id_cuenta == id_cuenta).values(saldo=nuevo_saldo)
                )
            return True
        except SQLAlchemyError:
            return False

    def guardar_transaccion(
        self,
        id_cuenta: int,
        id_tipo_transaccion: int | str,
        monto: float,
    ) -> int:
        with self.session_factory.begin() as session:
            tipo_id = id_tipo_transaccion

            if isinstance(id_tipo_transaccion, str):
                nombre = id_tipo_transaccion.strip()
                tipo_existente = session.scalar(
                    select(TipoTransaccionModel).where(TipoTransaccionModel.nombre == nombre)
                )
                if tipo_existente is None:
                    tipo_existente = TipoTransaccionModel(nombre=nombre, descripcion=None)
                    session.add(tipo_existente)
                    session.flush()
                tipo_id = tipo_existente.id_tipo_transaccion

            item = TransaccionModel(
                id_cuenta=id_cuenta,
                id_tipo_transaccion=int(tipo_id),
                monto=monto,
            )
            session.add(item)
            session.flush()
            return item.id_transaccion

    def obtener_transacciones_por_cuenta(self, id_cuenta: int) -> List[Tuple]:
        with self.session_factory() as session:
            items = session.scalars(
                select(TransaccionModel).where(TransaccionModel.id_cuenta == id_cuenta).order_by(TransaccionModel.fecha.desc())
            ).all()
            return [self._transaccion_tuple(item) for item in items]

    def validar_login_por_dni(self, dni: str, password: str) -> bool:
        with self.session_factory() as session:
            item = session.scalar(select(PersonaModel).where(PersonaModel.dni == dni))
            if not item or not item.hashedpassword:
                return False
            return pwd_context.verify(password, item.hashedpassword)

    def limpiar_base_datos(self):
        with self.session_factory.begin() as session:
            for model in (TransaccionModel, CuentaModel, ClienteModel, EmpleadoModel, TipoTransaccionModel, TipoCuentaModel, PersonaModel):
                session.execute(delete(model))

    def cerrar_conexion(self):
        DatabaseConnection.reset()

    def __del__(self):
        # La conexión la administra el Singleton DatabaseConnection;
        # el DAO no la cierra individualmente.
        pass
