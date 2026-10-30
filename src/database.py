"""Conexión única a la base de datos (patrón Singleton).

Garantiza que toda la aplicación comparta un único ``Engine`` de
SQLAlchemy por ruta de base de datos, en lugar de que cada vista o
módulo cree el suyo propio (como ocurría antes, con 4+ instancias de
``DAO("sistema_bancario.db")`` repartidas por el código).

Uso típico en la aplicación::

    from src.database import DatabaseConnection

    engine = DatabaseConnection.instance().engine

Uso en tests (cada test puede pedir una conexión aislada en memoria)::

    conn = DatabaseConnection.instance(":memory:")
    ...
    DatabaseConnection.reset()  # limpia el singleton entre tests
"""

from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine


class DatabaseConnection:
    """Singleton que encapsula el ``Engine`` de SQLAlchemy.

    Solo existe una instancia por ``db_path`` durante toda la vida del
    proceso. La primera llamada a :meth:`instance` crea la conexión;
    las siguientes devuelven la misma.
    """

    _instances: dict[str, "DatabaseConnection"] = {}

    def __init__(self, db_path: str = "sistema_bancario.db"):
        self.db_path = db_path
        url = (
            "sqlite://"
            if db_path == ":memory:"
            else f"sqlite:///{Path(db_path).resolve()}"
        )
        self._engine: Engine = create_engine(url, future=True)
        event.listen(self._engine, "connect", self._enable_foreign_keys)

    @classmethod
    def instance(cls, db_path: str = "sistema_bancario.db") -> "DatabaseConnection":
        """Devuelve la instancia única para ``db_path`` (la crea si no existe)."""
        if db_path not in cls._instances:
            cls._instances[db_path] = cls(db_path)
        return cls._instances[db_path]

    @classmethod
    def reset(cls) -> None:
        """Cierra y descarta todas las instancias (pensado para tests)."""
        for instancia in cls._instances.values():
            instancia.dispose()
        cls._instances.clear()

    @property
    def engine(self) -> Engine:
        return self._engine

    def dispose(self) -> None:
        self._engine.dispose()

    @staticmethod
    def _enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
