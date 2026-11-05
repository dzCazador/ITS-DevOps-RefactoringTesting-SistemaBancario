"""DAO temporal de operaciones del cliente (integración).

Hereda del DAO definitivo de Cristian (`src.dao.DAO`) y agrega solo las
operaciones compuestas que home_operaciones/home_historial necesitan y el
DAO base aún no tiene:

- `depositar(cuenta, monto)` / `retirar(cuenta, monto)`: validan en la
  entidad y persisten saldo + transacción
- `historial_cuentas(cuentas)`: une transacciones de todas las cuentas

Las vistas usan este DAO directo, sin capa de servicios intermedia.
Cuando BE-10/11 se entreguen (Daniel) y el DAO base incorpore estas
operaciones, este archivo se elimina y las vistas vuelven a usar `DAO`.
"""

from src.modelos.cuenta import SaldoInsuficienteError
from src.dao import DAO
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

    def historial_cuentas(self, cuentas) -> list:
        """[(fecha, nro_cuenta, Transaccion), ...] ordenado por fecha desc."""
        todas = []
        for cuenta in cuentas:
            for fila in self.obtener_transacciones_por_cuenta(cuenta.get_id_cuenta()):
                todas.append((fila[4], cuenta.get_nro_cuenta(), Transaccion.from_db_row(fila)))
        todas.sort(key=lambda x: x[0], reverse=True)
        return todas


__all__ = ["DAOCliente", "SaldoInsuficienteError"]
