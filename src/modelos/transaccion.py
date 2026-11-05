from datetime import datetime


class Transaccion:
    def __init__(
        self,
        tipo: str,
        monto: float,
        id_transaccion: int | None = None,
        id_cuenta: int | None = None,
        id_tipo_transaccion: int | None = None,
        fecha: datetime | str | None = None,
    ):
        if not isinstance(tipo, str) or not tipo.strip():
            raise ValueError("El tipo de transacción es obligatorio.")
        if not isinstance(monto, (int, float)):
            raise TypeError("El monto debe ser un número.")
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a cero.")

        self.__id_transaccion = id_transaccion
        self.__id_cuenta = id_cuenta
        self.__id_tipo_transaccion = id_tipo_transaccion
        self.__tipo = tipo.strip()
        self.__monto = float(monto)
        self.__fecha = self._normalizar_fecha(fecha) if fecha is not None else datetime.now()

    @staticmethod
    def _normalizar_fecha(fecha):
        if isinstance(fecha, datetime):
            return fecha
        if isinstance(fecha, str):
            return datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
        raise TypeError("La fecha debe ser datetime o un string ISO.")

    @classmethod
    def from_db_row(cls, row, tipo: str | None = None):
        """Crea una instancia a partir de una fila de la tabla transaccion."""
        if len(row) == 5:
            id_transaccion, id_cuenta, id_tipo_transaccion, monto, fecha = row
        elif len(row) == 6:
            id_transaccion, id_cuenta, id_tipo_transaccion, monto, fecha, tipo = row
        else:
            raise ValueError("La fila de transacción debe tener 5 o 6 elementos.")

        tipo_nombre = tipo or cls._tipo_por_id(id_tipo_transaccion)

        return cls(
            tipo=tipo_nombre,
            monto=monto,
            id_transaccion=id_transaccion,
            id_cuenta=id_cuenta,
            id_tipo_transaccion=id_tipo_transaccion,
            fecha=fecha,
        )

    @staticmethod
    def _tipo_por_id(id_tipo_transaccion: int | None) -> str:
        if id_tipo_transaccion is None:
            return "sin_tipo"
        mapping = {
            1: "deposito",
            2: "retiro",
            3: "pagoIntereses",
            4: "transferencia",
        }
        return mapping.get(id_tipo_transaccion, f"tipo_{id_tipo_transaccion}")

    # Getters
    def get_id_transaccion(self):
        return self.__id_transaccion

    def get_id_cuenta(self):
        return self.__id_cuenta

    def get_id_tipo_transaccion(self):
        return self.__id_tipo_transaccion

    def get_tipo(self):
        return self.__tipo

    def get_monto(self):
        return self.__monto

    def get_fecha(self):
        return self.__fecha

    def __str__(self):
        return f"{self.__fecha.strftime('%Y-%m-%d %H:%M:%S')} - {self.__tipo}: ${self.__monto:.2f}"