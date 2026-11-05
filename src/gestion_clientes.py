from sqlalchemy import select, update

from src.modelos.cliente import Cliente
from src.modelos.models import PersonaModel, TipoCuentaModel


# =========================================================
# BE-07 - ALTA DE CLIENTE
# =========================================================

def alta_cliente(dao, nombre, apellido, dni, password=None):
    """
    Crea un nuevo cliente y lo guarda en la base de datos.
    """

    # Comprobar si ya existe un cliente con ese DNI
    cliente_existente = dao.obtener_cliente_por_dni(dni)

    if cliente_existente is not None:
        raise ValueError("Ya existe un cliente con ese DNI.")

    # Crear el cliente
    nuevo_cliente = Cliente(
        nombre,
        apellido,
        dni,
        password=password
    )

    # Guardar el cliente en la base de datos
    id_cliente = dao.guardar_cliente(nuevo_cliente)

    return id_cliente


# =========================================================
# BE-08 - ALTA DE CUENTA
# =========================================================

def alta_cuenta(
    dao,
    dni,
    nro_cuenta,
    tipo_cuenta,
    saldo_inicial=0.0
):
    """
    Crea una cuenta para un cliente existente.
    Cada cliente puede tener una sola cuenta de cada tipo.
    """

    # Validar saldo inicial
    try:
        saldo_inicial = float(saldo_inicial)
    except (ValueError, TypeError):
        raise ValueError("El saldo inicial debe ser un número.")

    if saldo_inicial < 0:
        raise ValueError("El saldo inicial no puede ser negativo.")

    # Validar tipo de cuenta
    if not tipo_cuenta:
        raise ValueError("Debe indicar un tipo de cuenta.")

    tipo_normalizado = tipo_cuenta.strip().lower()

    tipos_validos = {
        "ahorro": "Ahorro",
        "corriente": "Corriente"
    }

    if tipo_normalizado not in tipos_validos:
        raise ValueError(
            "El tipo de cuenta debe ser 'Ahorro' o 'Corriente'."
        )

    nombre_tipo = tipos_validos[tipo_normalizado]

    # Buscar cliente por DNI
    cliente = dao.obtener_cliente_por_dni(dni)

    if cliente is None:
        raise ValueError("No existe un cliente con ese DNI.")

    # La posición 0 contiene id_cliente
    id_cliente = cliente[0]

    # Resolver id_tipo_cuenta
    try:
        id_tipo_cuenta = dao.guardar_tipo_cuenta(nombre_tipo)

    except ValueError:
        with dao.connect() as session:
            tipo_existente = session.scalar(
                select(TipoCuentaModel).where(
                    TipoCuentaModel.nombre == nombre_tipo
                )
            )

            if tipo_existente is None:
                raise ValueError(
                    "No se pudo obtener el tipo de cuenta."
                )

            id_tipo_cuenta = tipo_existente.id_tipo_cuenta

    # Comprobar que el cliente no tenga ese tipo de cuenta
    cuentas = dao.obtener_cuentas_por_cliente(id_cliente)

    for cuenta in cuentas:
        # cuenta[3] contiene id_tipo_cuenta
        tipo_existente = cuenta[3]

        if tipo_existente == id_tipo_cuenta:
            raise ValueError(
                f"El cliente ya posee una cuenta de tipo {nombre_tipo}."
            )

    # Comprobar que el número de cuenta no esté utilizado
    cuenta_existente = dao.obtener_cuenta_por_numero(nro_cuenta)

    if cuenta_existente is not None:
        raise ValueError(
            "Ya existe una cuenta con ese número."
        )

    # Guardar cuenta
    id_cuenta = dao.guardar_cuenta(
        nro_cuenta=nro_cuenta,
        id_cliente=id_cliente,
        id_tipo_cuenta=id_tipo_cuenta,
        saldo=saldo_inicial
    )

    return id_cuenta


# =========================================================
# BE-09 - EDITAR CLIENTE
# =========================================================

def editar_cliente(
    dao,
    dni_actual,
    nuevo_nombre,
    nuevo_apellido,
    nuevo_dni,
    password=None
):
    """
    Modifica los datos personales de un cliente existente.
    """

    # Buscar cliente actual
    cliente_actual = dao.obtener_cliente_por_dni(dni_actual)

    if cliente_actual is None:
        raise ValueError(
            "No existe un cliente con ese DNI."
        )

    # Crear un Cliente temporal para validar los datos nuevos
    datos_nuevos = Cliente(
        nuevo_nombre,
        nuevo_apellido,
        nuevo_dni,
        password=password
    )

    # Si cambia el DNI, comprobar que no esté ocupado
    if datos_nuevos.get_dni() != dni_actual:

        persona_existente = dao.obtener_persona_por_dni(
            datos_nuevos.get_dni()
        )

        if persona_existente is not None:
            raise ValueError(
                "Ya existe otra persona con ese DNI."
            )

    # Preparar los valores a modificar
    nuevos_valores = {
        "nombre": datos_nuevos.get_nombre(),
        "apellido": datos_nuevos.get_apellido(),
        "dni": datos_nuevos.get_dni()
    }

    # La contraseña solo se modifica si se proporciona una nueva
    if password:
        nuevos_valores["hashedpassword"] = (
            datos_nuevos.get_password_hash()
        )

    # Actualizar PersonaModel
    with dao.session_factory.begin() as session:
        session.execute(
            update(PersonaModel)
            .where(PersonaModel.dni == dni_actual)
            .values(**nuevos_valores)
        )

    return True