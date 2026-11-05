from src.modelos.cuenta import Cuenta


class CuentaAhorro(Cuenta):
    def __init__(self, nro_cuenta: str, cliente, saldo: float = 0.0, interes: float = 1.0, id_cuenta: int = None, **kwargs):
        super().__init__(nro_cuenta, cliente, saldo, id_cuenta=id_cuenta, **kwargs)
        if interes < 0:
            raise ValueError("La tasa de interés no puede ser negativa.")
        self.__interes = float(interes)

    def get_interes(self):
        return self.__interes

    def aplicar_interes(self):
        """Aplica el interés al saldo actual reutilizando depositar para que persista."""
        saldo_actual = self.get_saldo()
        monto_interes = saldo_actual * (self.__interes / 100)
        if monto_interes > 0:
            self.depositar(monto_interes, tipo="interes")
        return self.get_saldo()