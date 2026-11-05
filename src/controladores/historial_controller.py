"""Use cases for the client's movement history."""

from src.controladores.cliente_controller import nombres_tipo_cuenta


class HistorialController:
    def __init__(self, dao):
        self._dao = dao

    def _etiqueta_cuenta(self, cuenta, tipos: dict) -> str:
        nombre_tipo = tipos.get(cuenta.get_id_tipo_cuenta(), "")
        if "ahorro" in nombre_tipo.lower():
            return "Caja de ahorro"
        return nombre_tipo or "Cuenta"

    # tipo de transacción -> (texto de la operación, signo: +1 ingreso, -1 egreso)
    _OPERACIONES = {
        "deposito": ("Depositar", 1),
        "retiro": ("Retiro", -1),
        "transferencia_enviada": ("Transferencia enviada", -1),
        "transferencia_recibida": ("Transferencia recibida", 1),
    }

    def movimientos(self, cuentas) -> list[dict]:
        """Movements of all accounts, newest first, in the view's row format."""
        tipos = nombres_tipo_cuenta(self._dao)
        nombres = {c.get_id_cuenta(): self._etiqueta_cuenta(c, tipos) for c in cuentas}
        filas = []
        for fecha, _, tx in self._dao.historial_cuentas(cuentas):
            operacion, signo = self._OPERACIONES.get(tx.get_tipo(), (tx.get_tipo(), -1))
            filas.append({
                "fecha": fecha.strftime("%d/%m/%Y"),
                "operacion": operacion,
                "cuenta": nombres.get(tx.get_id_cuenta(), ""),
                "monto": signo * tx.get_monto(),
            })
        return filas

    @staticmethod
    def filtrar(movimientos: list[dict], filtro: str) -> list[dict]:
        """Keep movements of the given account label ("Todas" keeps all)."""
        return [
            m for m in movimientos
            if filtro == "Todas" or m.get("cuenta", "").lower() == filtro.lower()
        ]
