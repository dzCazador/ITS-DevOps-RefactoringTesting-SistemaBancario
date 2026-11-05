# Integración del DAO

## Estado actual

El proyecto usa SQLite con SQLAlchemy para persistir el esquema bancario actual:

- `persona` y sus subtipos `cliente` y `empleado`
- `tipo_cuenta` y `cuenta`
- `tipo_transaccion` y `transaccion`

El DAO crea automáticamente las tablas al inicializarse y se usa principalmente para:

- registrar clientes y empleados
- autenticar por DNI y password
- crear cuentas asociadas a clientes
- registrar transacciones por tipo
- consultar el esquema y los datos persistidos

La base de datos usada por la aplicación es `sistema_bancario.db`.

## Operaciones disponibles en el DAO

### Conexión y tablas

```python
dao = DAO("sistema_bancario.db")
dao.create_tables()
session = dao.connect()
session.close()
dao.cerrar_conexion()
```


### Clientes

```python
from src.modelos.cliente import Cliente

id_cliente = dao.guardar_cliente(Cliente("Lucia", "Gomez", "30123456", categoria="NORMAL", estado="ACTIVO"))
cliente = dao.obtener_cliente_por_dni("30123456")
```

### Empleados

```python
from src.modelos.empleado import Empleado

id_empleado = dao.guardar_empleado(
    Persona("Pedro", "López", "28765432", "pass123"),
    legajo="E-001",
    cargo="Analista",
    departamento="Atención al cliente",
    fecha_ingreso="2024-01-15",
    salario=65000.0,
    sucursal="Sucursal Central",
)
```

### Tipos y cuentas

```python
id_tipo_cuenta = dao.guardar_tipo_cuenta("Ahorro", "Cuenta de ahorro")
id_tipo_transaccion = dao.guardar_tipo_transaccion("pagoIntereses", "Pago de intereses")

id_cuenta = dao.guardar_cuenta(
    nro_cuenta="CA-0001",
    id_cliente=id_cliente,
    id_tipo_cuenta=id_tipo_cuenta,
    saldo=1200.0,
    tasa_interes=2.5,
)

cuentas = dao.obtener_cuentas_por_cliente(id_cliente)
cuenta = dao.obtener_cuenta_por_numero("CA-0001")
dao.actualizar_saldo_cuenta(id_cuenta, 1600.0)
```

### Transacciones

```python
id_transaccion = dao.guardar_transaccion(id_cuenta, "deposito", 500.0)
transacciones = dao.obtener_transacciones_por_cuenta(id_cuenta)
```

También es válido pasar el tipo por nombre desde el catálogo:

```python
id_transaccion = dao.guardar_transaccion(id_cuenta, "pagoIntereses", 150.0)
```

### Autenticación

La clase `Autenticacion` combina la validación de credenciales con la resolución del rol y de los datos asociados a la persona. Se instancia con el mismo DAO que utiliza la aplicación:

```python
from src.autenticacion import Autenticacion

autenticacion = Autenticacion(dao)
sesion = autenticacion.autenticar("30123456", "miPassword123")
```

`autenticar(dni, clave)` devuelve `None` cuando el DNI o la clave están vacíos, la persona no existe, la clave no coincide o la persona no tiene rol de cliente ni de personal. La clave se verifica contra su hash mediante `dao.validar_login_por_dni()`; no se almacena ni se compara en texto plano.

Cuando la autenticación es correcta, devuelve un diccionario con esta estructura:

```python
{
    "dni": "30123456",
    "nombre": "Lucia",
    "apellido": "Gomez",
    "rol": "cliente",
    "cuentas": [Cuenta(...)],
}
```

- Para un cliente, `rol` es `"cliente"` y `cuentas` contiene objetos `Cuenta` reconstruidos desde la base de datos. Si no tiene cuentas, la lista es `[]`.
- Para un empleado, `rol` es `"personal"` y `cuentas` es una lista vacía.
- Para una persona sin rol asignado, la autenticación falla y devuelve `None`.

Si solo se necesita comprobar las credenciales, sin construir la sesión, puede utilizarse directamente el DAO:

```python
login_ok = dao.validar_login_por_dni("30123456", "miPassword123")
```

### Limpieza

`limpiar_base_datos()` elimina todos los registros respetando el orden de las relaciones. Es una operación destructiva y no se usa en el flujo normal de la app.

## Modelo actual del dominio

El proyecto se organiza con la siguiente separación:

- `Persona`: validación y hashing compartidos
- `Cliente(Persona)`: datos propios del cliente
- `Empleado(Persona)`: datos propios del empleado
- `Cuenta`: lógica de operación bancaria y estado de saldo
- `CuentaAhorro(Cuenta)`: comportamiento específico de cuenta de ahorro
- `Transaccion`: representa una operación del catálogo `tipo_transaccion`

La capa ORM queda en `src/modelos/models.py` y refleja exactamente el esquema de la base de datos.

## Pendientes de integración

La aplicación puede seguir usando el DAO como fuente principal para:

1. registrar personas y clientes
2. crear cuentas asociadas a clientes
3. guardar transacciones con el tipo correcto
4. leer historial de movimientos desde `obtener_transacciones_por_cuenta()`
5. validar autenticación con DNI y password hash

El flujo recomendado es que cada operación de negocio persista en SQLite a través del DAO, y que los objetos de dominio se usen para mostrar información y lógica local, pero nunca como única fuente de verdad.

## Ejemplos ejecutables

Comprobar el esquema y API del DAO:

```powershell
python -m pytest tests/test_dao_schema.py -q
```

Ejecutar un ejemplo básico de persistencia:

```powershell
python main.py
```
