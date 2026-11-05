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

    def movimientos(self, cuentas) -> list[dict]:
        """Movements of all accounts, newest first, in the view's row format."""
        tipos = nombres_tipo_cuenta(self._dao)
        nombres = {c.get_id_cuenta(): self._etiqueta_cuenta(c, tipos) for c in cuentas}
        return [
            {
                "fecha": fecha.strftime("%d/%m/%Y"),
                "operacion": "Depositar" if tx.get_tipo() == "deposito"
                             else ("Retiro" if tx.get_tipo() == "retiro" else tx.get_tipo()),
                "cuenta": nombres.get(tx.get_id_cuenta(), ""),
                "monto": tx.get_monto() if tx.get_tipo() == "deposito" else -tx.get_monto(),
            }
            for fecha, _, tx in self._dao.historial_cuentas(cuentas)
        ]

    @staticmethod
    def filtrar(movimientos: list[dict], filtro: str) -> list[dict]:
        """Keep movements of the given account label ("Todas" keeps all)."""
        return [
            m for m in movimientos
            if filtro == "Todas" or m.get("cuenta", "").lower() == filtro.lower()
        ]
