from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PersonaModel(Base):
    __tablename__ = "persona"

    id_persona: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    apellido: Mapped[str] = mapped_column(String, nullable=False)
    dni: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashedpassword: Mapped[str] = mapped_column(String, nullable=False, default="")
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    telefono: Mapped[str | None] = mapped_column(String, nullable=True)
    direccion: Mapped[str | None] = mapped_column(String, nullable=True)
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )


class ClienteModel(Base):
    __tablename__ = "cliente"

    id_cliente: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_persona: Mapped[int] = mapped_column(
        ForeignKey("persona.id_persona"), unique=True, nullable=False
    )
    categoria: Mapped[str | None] = mapped_column(String, nullable=True)
    estado: Mapped[str] = mapped_column(String, nullable=False, default="ACTIVO")


class EmpleadoModel(Base):
    __tablename__ = "empleado"

    id_empleado: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_persona: Mapped[int] = mapped_column(
        ForeignKey("persona.id_persona"), unique=True, nullable=False
    )
    legajo: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    cargo: Mapped[str] = mapped_column(String, nullable=False)
    departamento: Mapped[str] = mapped_column(String, nullable=False)
    fecha_ingreso: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    salario: Mapped[float] = mapped_column(Float, nullable=False)
    sucursal: Mapped[str] = mapped_column(String, nullable=False)


class TipoCuentaModel(Base):
    __tablename__ = "tipo_cuenta"

    id_tipo_cuenta: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String, nullable=True)


class TipoTransaccionModel(Base):
    __tablename__ = "tipo_transaccion"

    id_tipo_transaccion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String, nullable=True)


class CuentaModel(Base):
    __tablename__ = "cuenta"
    __table_args__ = (
        UniqueConstraint("id_cliente", "id_tipo_cuenta", name="uq_cuenta_cliente_tipo"),
    )

    id_cuenta: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nro_cuenta: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    id_cliente: Mapped[int] = mapped_column(
        ForeignKey("cliente.id_cliente"), nullable=False
    )
    id_tipo_cuenta: Mapped[int] = mapped_column(
        ForeignKey("tipo_cuenta.id_tipo_cuenta"), nullable=False
    )
    saldo: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    tasa_interes: Mapped[float | None] = mapped_column(Float, nullable=True)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )


class TransaccionModel(Base):
    __tablename__ = "transaccion"

    id_transaccion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_cuenta: Mapped[int] = mapped_column(
        ForeignKey("cuenta.id_cuenta"), nullable=False
    )
    id_tipo_transaccion: Mapped[int] = mapped_column(
        ForeignKey("tipo_transaccion.id_tipo_transaccion"), nullable=False
    )
    monto: Mapped[float] = mapped_column(Float, nullable=False)
    fecha: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )
