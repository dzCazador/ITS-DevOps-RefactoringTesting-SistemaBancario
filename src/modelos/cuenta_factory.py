"""Factory Method para la creación de cuentas bancarias.

Centraliza la decisión de qué subclase de :class:`src.modelos.cuenta.Cuenta`
instanciar según el tipo de cuenta ("Ahorro", "Corriente", ...).

Antes de este refactor, la lógica de elección estaba dispersa y
duplicada en las vistas (``isinstance(cuenta, CuentaAhorro)``,
``"ahorro" in nombre.lower()``, etc.). Ahora vive en un único lugar:
basta con registrar un nuevo creador para soportar un nuevo tipo de
cuenta (principio Open/Closed).
"""

from src.modelos.cuenta import Cuenta
from src.modelos.cuenta_ahorro import CuentaAhorro

# Tasa de interés por defecto (%) para las cuentas de ahorro nuevas.
TASA_AHORRO_DEFAULT = 1.0


class CuentaFactory:
    """Fábrica de cuentas: crea la subclase correcta según el tipo."""

    # Registro tipo -> función creadora. Cada creador recibe
    # (nro_cuenta, cliente, saldo, **kwargs) y devuelve una Cuenta.
    _creadores = {}

    @classmethod
    def registrar(cls, tipo: str, creador) -> None:
        """Registra una función creadora para un tipo de cuenta (OCP)."""
        cls._creadores[cls._normalizar(tipo)] = creador

    @classmethod
    def crear(
        cls,
        tipo: str,
        nro_cuenta: str,
        cliente,
        saldo: float = 0.0,
        **kwargs,
    ) -> Cuenta:
        """Crea una cuenta del ``tipo`` indicado.

        :param tipo: nombre del tipo ("Ahorro", "Corriente", ...).
        :raises ValueError: si el tipo no está registrado.
        """
        clave = cls._normalizar(tipo)
        creador = cls._creadores.get(clave)
        if creador is None:
            tipos = ", ".join(sorted(cls._creadores)) or "(ninguno)"
            raise ValueError(
                f"Tipo de cuenta desconocido: '{tipo}'. Tipos válidos: {tipos}."
            )
        return creador(nro_cuenta, cliente, saldo, **kwargs)

    @classmethod
    def crear_desde_fila(cls, fila, cliente, nombre_tipo: str = "") -> Cuenta:
        """Reconstruye una cuenta desde una fila de la BD (tupla del DAO).

        La fila tiene el formato ``(id_cuenta, nro_cuenta, id_cliente,
        id_tipo_cuenta, saldo, tasa_interes, fecha_creacion)``.
        """
        (id_cuenta, nro_cuenta, id_cliente, id_tipo_cuenta,
         saldo, tasa_interes, fecha_creacion) = fila

        kwargs = {
            "id_cuenta": id_cuenta,
            "id_cliente": id_cliente,
            "id_tipo_cuenta": id_tipo_cuenta,
            "tasa_interes": tasa_interes or 0.0,
            "fecha_creacion": fecha_creacion,
        }

        if "ahorro" in cls._normalizar(nombre_tipo):
            kwargs["interes"] = tasa_interes or TASA_AHORRO_DEFAULT
            return CuentaAhorro(nro_cuenta, cliente, saldo, **kwargs)
        return Cuenta(nro_cuenta, cliente, saldo, **kwargs)

    @staticmethod
    def _normalizar(tipo: str) -> str:
        return (tipo or "").strip().lower()


def _crear_corriente(nro_cuenta, cliente, saldo, **kwargs) -> Cuenta:
    return Cuenta(nro_cuenta, cliente, saldo, **kwargs)


def _crear_ahorro(nro_cuenta, cliente, saldo, **kwargs) -> CuentaAhorro:
    interes = kwargs.pop("interes", kwargs.pop("tasa_interes", TASA_AHORRO_DEFAULT))
    return CuentaAhorro(nro_cuenta, cliente, saldo, interes=interes, **kwargs)


# Registro de los tipos soportados por defecto.
CuentaFactory.registrar("Corriente", _crear_corriente)
CuentaFactory.registrar("Ahorro", _crear_ahorro)
CuentaFactory.registrar("Caja de ahorro", _crear_ahorro)
