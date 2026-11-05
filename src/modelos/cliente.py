from src.modelos.persona import Persona


class Cliente(Persona):
    def __init__(self, nombre, apellido, dni, categoria=None, estado="ACTIVO", password=None):
        if not nombre or not apellido or not dni:
            raise ValueError("Todos los campos del cliente son obligatorios.")

        super().__init__(nombre, apellido, dni, password=password)

        self.__categoria = categoria.strip() if categoria else None
        self.__estado = estado.strip() if estado else "ACTIVO"

    def get_categoria(self):
        return self.__categoria

    def get_estado(self):
        return self.__estado

    def set_estado(self, estado):
        self.__estado = estado.strip()

