from datetime import datetime

from src.modelos.transaccion import Transaccion


class SaldoInsuficienteError(Exception):
    """Excepción personalizada para saldo insuficiente."""
    pass


class Cuenta:
    def __init__(
        self,
        nro_cuenta: str,
        cliente,
        saldo: float = 0.0,
        id_cuenta: int | None = None,
        id_cliente: int | None = None,
        id_tipo_cuenta: int | None = None,
        tasa_interes: float = 0.0,
        fecha_creacion: datetime | None = None,
    ):
        if not nro_cuenta or not isinstance(nro_cuenta, str):
            raise ValueError("El número de cuenta debe ser una cadena no vacía.")
        if saldo < 0:
            raise ValueError("El saldo inicial no puede ser negativo.")
        if cliente is None:
            raise ValueError("Debe asignarse un cliente válido a la cuenta.")

        self.__id_cuenta = id_cuenta
        self.__id_cliente = id_cliente
        self.__id_tipo_cuenta = id_tipo_cuenta
        self.__nro_cuenta = nro_cuenta
        self.__cliente = cliente
        self.__saldo = saldo
        self.__tasa_interes = tasa_interes
        self.__fecha_creacion = fecha_creacion or datetime.now()
        self.__transacciones = []

    @classmethod
    def from_db_row(cls, row, cliente):
        """Crea una instancia de Cuenta a partir de la fila de la tabla cuenta."""
        return cls(
            nro_cuenta=row[1],
            cliente=cliente,
            saldo=row[4],
            id_cuenta=row[0],
            id_cliente=row[2],
            id_tipo_cuenta=row[3],
            tasa_interes=row[5] or 0.0,
            fecha_creacion=row[6],
        )

    # Métodos getters
    def get_id_cuenta(self):
        return self.__id_cuenta

    def get_id_cliente(self):
        return self.__id_cliente

    def get_id_tipo_cuenta(self):
        return self.__id_tipo_cuenta

    def get_nro_cuenta(self):
        return self.__nro_cuenta

    def get_saldo(self):
        return self.__saldo

    def get_cliente(self):
        return self.__cliente

    def get_tasa_interes(self):
        return self.__tasa_interes

    def get_fecha_creacion(self):
        return self.__fecha_creacion

    def get_transacciones(self):
        return self.__transacciones

    # Operaciones
    def depositar(self, monto: float, tipo: str = "deposito"):
        """Agrega dinero a la cuenta."""
        if not isinstance(monto, (int, float)):
            raise TypeError("El monto del depósito debe ser un número.")
        if monto <= 0:
            raise ValueError("El monto del depósito debe ser mayor a cero.")
        nombre_tipo = str(tipo).strip() if tipo is not None else "deposito"
        self.__saldo += monto
        self.__transacciones.append(Transaccion(nombre_tipo, monto))

    def retirar(self, monto: float, tipo: str = "retiro"):
        """Retira dinero de la cuenta si hay saldo suficiente."""
        if not isinstance(monto, (int, float)):
            raise TypeError("El monto del retiro debe ser un número.")
        if monto <= 0:
            raise ValueError("El monto del retiro debe ser mayor a cero.")
        if monto > self.__saldo:
            raise SaldoInsuficienteError(
                "Saldo insuficiente para realizar el retiro.")
        nombre_tipo = str(tipo).strip() if tipo is not None else "retiro"
        self.__saldo -= monto
        self.__transacciones.append(Transaccion(nombre_tipo, monto))

    def mostrar_transacciones(self):
        if not self.__transacciones:
            return ["No hay transacciones registradas."]
        return [str(t) for t in self.__transacciones]