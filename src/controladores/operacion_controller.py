"""Use cases for deposits and withdrawals of the client."""

from dataclasses import dataclass

from src.controladores.cliente_controller import nombres_tipo_cuenta
from src.modelos.errores import CuentaNoEncontradaError

__all__ = [
    "CuentaDestino",
    "CuentaNoEncontradaError",
    "FormatoMontoError",
    "MontoNoPositivoError",
    "MontoVacioError",
    "OperacionController",
    "ResultadoOperacion",
]


class MontoVacioError(ValueError):
    """No amount was entered."""


class FormatoMontoError(ValueError):
    """The amount text is not a number."""


class MontoNoPositivoError(ValueError):
    """The amount is zero or negative."""


@dataclass(frozen=True)
class ResultadoOperacion:
    tipo: str
    monto: float
    nro_cuenta: str
    saldo: float


@dataclass(frozen=True)
class CuentaDestino:
    """An account offered as transfer destination, with its holder's name."""

    nro_cuenta: str
    tipo: str
    nombre: str
    apellido: str


class OperacionController:
    def __init__(self, dao):
        self._dao = dao

    def listar_cuentas_destino(self) -> list:
        """Every account in the system, ordered by holder, for the destination picker."""
        return [
            CuentaDestino(nro_cuenta=nro, tipo=tipo, nombre=nombre, apellido=apellido)
            for nro, tipo, nombre, apellido in self._dao.listar_cuentas_destino()
        ]

    def cuenta_para_etiqueta(self, cuentas, etiqueta: str):
        """Return the account matching a UI toggle label, or None."""
        tipos = nombres_tipo_cuenta(self._dao)
        for cuenta in cuentas:
            nombre_tipo = tipos.get(cuenta.get_id_tipo_cuenta(), "")
            if etiqueta == "Caja de ahorro" and "ahorro" in nombre_tipo.lower():
                return cuenta
            if etiqueta == "Corriente" and "corriente" in nombre_tipo.lower():
                return cuenta
        return None

    @staticmethod
    def parsear_monto(texto: str) -> float:
        """Parse "1.500,50" style text into a positive float.

        :raises MontoVacioError, FormatoMontoError, MontoNoPositivoError
        """
        if not texto:
            raise MontoVacioError()
        try:
            monto = float(texto.replace(".", "").replace(",", "."))
        except ValueError as error:
            raise FormatoMontoError() from error
        if monto <= 0:
            raise MontoNoPositivoError()
        return monto

    def ejecutar_operacion(self, cuentas, etiqueta: str, tipo: str, texto_monto: str) -> ResultadoOperacion:
        """Validate the input, then deposit or withdraw from the selected account.

        Domain errors from the account (e.g. SaldoInsuficienteError) propagate.
        """
        monto = self.parsear_monto(texto_monto)

        cuenta = self.cuenta_para_etiqueta(cuentas, etiqueta)
        if cuenta is None:
            raise CuentaNoEncontradaError(etiqueta)

        if tipo == "Depositar":
            saldo = self._dao.depositar(cuenta, monto)
        else:
            saldo = self._dao.retirar(cuenta, monto)

        return ResultadoOperacion(
            tipo=tipo,
            monto=monto,
            nro_cuenta=cuenta.get_nro_cuenta(),
            saldo=saldo,
        )

    def transferir(self, cuentas, etiqueta_origen: str, nro_destino: str, texto_monto: str) -> ResultadoOperacion:
        """Transfer from the origin account (chosen by label) to ``nro_destino``.

        Domain errors (unknown destination, same holder, insufficient funds)
        propagate from the DAO.
        """
        monto = self.parsear_monto(texto_monto)

        origen = self.cuenta_para_etiqueta(cuentas, etiqueta_origen)
        if origen is None:
            raise CuentaNoEncontradaError(etiqueta_origen)

        saldo = self._dao.transferir(origen.get_nro_cuenta(), nro_destino, monto)

        return ResultadoOperacion(
            tipo="Transferir",
            monto=monto,
            nro_cuenta=origen.get_nro_cuenta(),
            saldo=saldo,
        )
