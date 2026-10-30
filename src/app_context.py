"""Punto de acceso compartido a los DAO de la aplicación.

Gracias al Singleton :class:`src.database.DatabaseConnection`, todos
los DAO creados aquí comparten la misma conexión física a la base de
datos. Las vistas importan estos objetos en lugar de instanciar su
propio ``DAO("sistema_bancario.db")`` (principio DRY).
"""

import os

from src.dao import DAO
from src.dao_cliente import DAOCliente
from src.dao_personal import DAOPersonal

DB_PATH = os.getenv("DB_PATH", "sistema_bancario.db")

# DAO base (login, gestión de clientes legacy)
dao = DAO(DB_PATH)

# DAO del panel de personal (altas/ediciones de clientes)
dao_personal = DAOPersonal(DB_PATH)

# DAO de operaciones del cliente (depósitos, retiros, historial)
dao_cliente = DAOCliente(DB_PATH)
