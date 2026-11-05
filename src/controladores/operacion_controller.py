"""Use cases for deposits and withdrawals of the client."""

from dataclasses import dataclass

from src.controladores.cliente_controller import nombres_tipo_cuenta


class MontoVacioError(ValueError):
    """No amount was entered."""


class FormatoMontoError(ValueError):
    """The amount text is not a number."""


class MontoNoPositivoError(ValueError):
    """The amount is zero or negative."""


class CuentaNoEncontradaError(LookupError):
    """The client has no account for the selected type."""

    def __init__(self, etiqueta: str):
        super().__init__(etiqueta)
        self.etiqueta = etiqueta


@dataclass(frozen=True)
class ResultadoOperacion:
    tipo: str
    monto: float
    nro_cuenta: str
    saldo: float


class OperacionController:
    def __init__(self, dao):
        self._dao = dao

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
