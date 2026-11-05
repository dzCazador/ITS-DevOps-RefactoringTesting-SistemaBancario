"""DAO temporal de operaciones del cliente (integración).

Hereda del DAO definitivo de Cristian (`src.dao.DAO`) y agrega solo las
operaciones compuestas que home_operaciones/home_historial necesitan y el
DAO base aún no tiene:

- `depositar(cuenta, monto)` / `retirar(cuenta, monto)`: validan en la
  entidad y persisten saldo + transacción
- `transferir(nro_origen, nro_destino, monto)`: débito y crédito atómicos
  en una sola transacción
- `historial_cuentas(cuentas)`: une transacciones de todas las cuentas

Las vistas usan este DAO directo, sin capa de servicios intermedia.
Cuando BE-10/11 se entreguen (Daniel) y el DAO base incorpore estas
operaciones, este archivo se elimina y las vistas vuelven a usar `DAO`.
"""

from sqlalchemy import select

from src.modelos.cuenta import SaldoInsuficienteError
from src.dao import DAO
from src.modelos.errores import CuentaNoEncontradaError, TransferenciaInvalidaError
from src.modelos.models import (
    ClienteModel,
    CuentaModel,
    PersonaModel,
    TipoCuentaModel,
    TipoTransaccionModel,
    TransaccionModel,
)
from src.modelos.transaccion import Transaccion


class DAOCliente(DAO):
    """Extensión temporal para operar como cliente. Ver docstring del módulo."""

    def depositar(self, cuenta, monto: float) -> float:
        cuenta.depositar(monto)  # valida en entidad (monto > 0)
        self.actualizar_saldo_cuenta(cuenta.get_id_cuenta(), cuenta.get_saldo())
        self.guardar_transaccion(cuenta.get_id_cuenta(), "deposito", monto)
        return cuenta.get_saldo()

    def retirar(self, cuenta, monto: float) -> float:
        cuenta.retirar(monto)  # valida en entidad (monto > 0, saldo suficiente)
        self.actualizar_saldo_cuenta(cuenta.get_id_cuenta(), cuenta.get_saldo())
        self.guardar_transaccion(cuenta.get_id_cuenta(), "retiro", monto)
        return cuenta.get_saldo()

    def transferir(self, nro_origen: str, nro_destino: str, monto: float) -> float:
        """Move ``monto`` from the origin account to the destination account.

        Reads, validations, balance updates and both movements share one
        session, so a failure at any step rolls back every change.

        :returns: the new balance of the origin account.
        :raises ValueError: ``monto`` is not greater than zero.
        :raises CuentaNoEncontradaError: origin or destination does not exist.
        :raises TransferenciaInvalidaError: same account, or same holder.
        :raises SaldoInsuficienteError: origin balance is below ``monto``.
        """
        if monto <= 0:
            raise ValueError("El monto de la transferencia debe ser mayor a cero.")
        with self.session_factory.begin() as session:
            origen = self._cuenta_por_numero_en_sesion(session, nro_origen)
            destino = self._cuenta_por_numero_en_sesion(session, nro_destino)
            if origen.id_cuenta == destino.id_cuenta:
                raise TransferenciaInvalidaError("No se puede transferir a la misma cuenta.")
            if origen.id_cliente == destino.id_cliente:
                raise TransferenciaInvalidaError("La cuenta destino pertenece al mismo cliente.")
            if monto > origen.saldo:
                raise SaldoInsuficienteError("Saldo insuficiente para realizar la transferencia.")
            origen.saldo -= monto
            destino.saldo += monto
            self._registrar_transaccion(session, origen.id_cuenta, "transferencia_enviada", monto)
            self._registrar_transaccion(session, destino.id_cuenta, "transferencia_recibida", monto)
            return origen.saldo

    @staticmethod
    def _cuenta_por_numero_en_sesion(session, nro_cuenta: str) -> CuentaModel:
        cuenta = session.scalar(select(CuentaModel).where(CuentaModel.nro_cuenta == nro_cuenta))
        if cuenta is None:
            raise CuentaNoEncontradaError(nro_cuenta)
        return cuenta

    def _registrar_transaccion(self, session, id_cuenta: int, nombre_tipo: str, monto: float) -> None:
        """Add a movement inside ``session``, creating its type name if missing."""
        tipo = session.scalar(select(TipoTransaccionModel).where(TipoTransaccionModel.nombre == nombre_tipo))
        if tipo is None:
            tipo = TipoTransaccionModel(nombre=nombre_tipo, descripcion=None)
            session.add(tipo)
            session.flush()
        session.add(
            TransaccionModel(id_cuenta=id_cuenta, id_tipo_transaccion=tipo.id_tipo_transaccion, monto=monto)
        )

    def listar_cuentas_destino(self) -> list:
        """[(nro_cuenta, tipo, nombre, apellido), ...] for every account, in one query."""
        with self.connect() as session:
            filas = session.execute(
                select(
                    CuentaModel.nro_cuenta,
                    TipoCuentaModel.nombre,
                    PersonaModel.nombre,
                    PersonaModel.apellido,
                )
                .select_from(CuentaModel)
                .join(ClienteModel, CuentaModel.id_cliente == ClienteModel.id_cliente)
                .join(PersonaModel, ClienteModel.id_persona == PersonaModel.id_persona)
                .join(TipoCuentaModel, CuentaModel.id_tipo_cuenta == TipoCuentaModel.id_tipo_cuenta)
                .order_by(PersonaModel.apellido, PersonaModel.nombre, CuentaModel.nro_cuenta)
            ).all()
            return [tuple(fila) for fila in filas]

    def _nombres_tipos_transaccion(self) -> dict:
        with self.connect() as session:
            tipos = session.scalars(select(TipoTransaccionModel)).all()
            return {tipo.id_tipo_transaccion: tipo.nombre for tipo in tipos}

    def historial_cuentas(self, cuentas) -> list:
        """[(fecha, nro_cuenta, Transaccion), ...] ordenado por fecha desc."""
        # Names come from the database: types created at runtime (e.g.
        # "transferencia_enviada") are not in Transaccion's static id mapping.
        nombres = self._nombres_tipos_transaccion()
        todas = []
        for cuenta in cuentas:
            for fila in self.obtener_transacciones_por_cuenta(cuenta.get_id_cuenta()):
                tx = Transaccion.from_db_row(fila, tipo=nombres.get(fila[2]))
                todas.append((fila[4], cuenta.get_nro_cuenta(), tx))
        todas.sort(key=lambda x: x[0], reverse=True)
        return todas


__all__ = ["DAOCliente", "SaldoInsuficienteError"]
