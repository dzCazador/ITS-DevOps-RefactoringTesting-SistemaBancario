from passlib.context import CryptContext


class Persona:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, nombre, apellido, dni, password=None):
        if not nombre or not apellido or not dni:
            raise ValueError("Todos los campos de la persona son obligatorios.")

        if not nombre.replace(" ", "").isalpha() or not apellido.replace(" ", "").isalpha():
            raise ValueError("El nombre y apellido deben contener solo letras.")

        if not dni.isdigit():
            raise ValueError("El DNI debe contener solo números.")

        self.__nombre = nombre.strip().title()
        self.__apellido = apellido.strip().title()
        self.__dni = dni.strip()
        self.__password_hash = self.pwd_context.hash(password) if password else ""

    def get_nombre(self):
        return self.__nombre

    def get_apellido(self):
        return self.__apellido

    def get_dni(self):
        return self.__dni

    def get_password_hash(self):
        return self.__password_hash

    def verificar_password(self, password: str) -> bool:
        if not self.__password_hash:
            return False
        return self.pwd_context.verify(password, self.__password_hash)

    def mostrar_datos(self):
        return f"{self.__nombre} {self.__apellido} (DNI: {self.__dni})"

    def __str__(self):
        return self.mostrar_datos()
