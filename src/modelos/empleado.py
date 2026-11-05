from src.modelos.persona import Persona


class Empleado(Persona):
    def __init__(
        self,
        nombre,
        apellido,
        dni,
        legajo,
        cargo,
        departamento,
        fecha_ingreso,
        salario,
        sucursal,
        password=None,
    ):
        super().__init__(nombre, apellido, dni, password=password)

        if not legajo or not cargo or not departamento or not sucursal:
            raise ValueError("Los datos del empleado son obligatorios.")

        if salario is None or salario < 0:
            raise ValueError("El salario debe ser un valor no negativo.")

        self.__legajo = legajo.strip()
        self.__cargo = cargo.strip()
        self.__departamento = departamento.strip()
        self.__fecha_ingreso = fecha_ingreso
        self.__salario = salario
        self.__sucursal = sucursal.strip()

    def get_legajo(self):
        return self.__legajo

    def get_cargo(self):
        return self.__cargo

    def get_departamento(self):
        return self.__departamento

    def get_fecha_ingreso(self):
        return self.__fecha_ingreso

    def get_salario(self):
        return self.__salario

    def get_sucursal(self):
        return self.__sucursal
