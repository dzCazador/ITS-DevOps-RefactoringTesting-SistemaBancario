# 🔧 Refactorización del Sistema Bancario

Documento técnico de la refactorización aplicada al proyecto: patrones de diseño
(**Singleton**, **Factory Method**, **Builder**), principios **SOLID**, **DRY** y
su verificación mediante la suite de tests automatizados.

> **Resultado:** 59 tests en verde (44 originales + 15 nuevos de patrones), 3 skipped.
> Comando de verificación: `pytest tests/ -q`

---

## 📑 Índice

1. [Problemas detectados (antes)](#1-problemas-detectados-antes)
2. [Patrón Singleton — Conexión única a la BD](#2-patrón-singleton--conexión-única-a-la-bd)
3. [Patrón Factory Method — Creación de cuentas](#3-patrón-factory-method--creación-de-cuentas)
4. [Patrón Builder — Construcción de Personas](#4-patrón-builder--construcción-de-personas)
5. [Principio DRY — Utilidades de UI compartidas](#5-principio-dry--utilidades-de-ui-compartidas)
6. [Principios SOLID aplicados](#6-principios-solid-aplicados)
7. [Tests de los patrones](#7-tests-de-los-patrones)
8. [Resumen de archivos](#8-resumen-de-archivos)

---

## 1. Problemas detectados (antes)

| # | Problema | Dónde | Principio violado |
|---|----------|-------|-------------------|
| 1 | Cada vista instanciaba su propio `DAO("sistema_bancario.db")` → múltiples engines de SQLAlchemy a la misma BD | `login.py`, `home_personal.py`, `home_crear_cliente.py`, `home_operaciones.py`, `home_historial.py`, `vista_gestion_clientes.py` | DRY, acoplamiento |
| 2 | La decisión de qué subclase de `Cuenta` crear estaba dispersa: `isinstance(cuenta, CuentaAhorro)`, `"ahorro" in nombre.lower()` repetido en varias vistas | `home_cliente.py`, `home_operaciones.py`, `home_historial.py`, `home_personal.py` | OCP, DRY |
| 3 | Constructor de `Empleado` con **10 parámetros** → llamadas ilegibles y propensas a errores de orden | `empleado.py`, `test_autenticacion.py` | Legibilidad, KISS |
| 4 | `_formatear_monto()` copiada casi idéntica en 3 vistas; SnackBar de notificación duplicado en 4 vistas | `home_cliente.py`, `home_operaciones.py`, `home_historial.py`, `login.py` | DRY |
| 5 | Paleta de colores hardcodeada con valores distintos para lo mismo en cada vista | todas las vistas | DRY |

---

## 2. Patrón Singleton — Conexión única a la BD

**Archivo nuevo:** `src/database.py`
**Archivos modificados:** `src/dao.py`, `src/app_context.py` (nuevo), `src/login.py`,
`src/home_personal.py`, `src/home_crear_cliente.py`, `src/home_operaciones.py`,
`src/home_historial.py`, `src/vista_gestion_clientes.py`

### Problema

Cada módulo de vista creaba su propia instancia del DAO, y cada DAO creaba su propio
`Engine` de SQLAlchemy (pool de conexiones) apuntando al mismo archivo SQLite:

```python
# ANTES — src/login.py
_dao = DAO("sistema_bancario.db")          # engine #1

# ANTES — src/home_personal.py
_dao = DAOPersonal("sistema_bancario.db")  # engine #2

# ANTES — src/home_operaciones.py
_dao = DAOCliente("sistema_bancario.db")   # engine #3
# ... y así hasta 6 engines distintos para la MISMA base de datos
```

### Solución

`DatabaseConnection` garantiza **una única instancia del Engine por ruta de BD**
durante toda la vida del proceso:

```python
# DESPUÉS — src/database.py
class DatabaseConnection:
    _instances: dict[str, "DatabaseConnection"] = {}

    @classmethod
    def instance(cls, db_path="sistema_bancario.db"):
        if db_path not in cls._instances:
            cls._instances[db_path] = cls(db_path)
        return cls._instances[db_path]
```

El `DAO` ahora obtiene el engine del Singleton en lugar de crearlo:

```python
# DESPUÉS — src/dao.py
def __init__(self, db_path: str = "sistema_bancario.db"):
    self.engine = DatabaseConnection.instance(db_path).engine
    ...
```

Y las vistas importan los DAO compartidos desde un único punto (`src/app_context.py`):

```python
# DESPUÉS — src/app_context.py
dao = DAO(DB_PATH)
dao_personal = DAOPersonal(DB_PATH)
dao_cliente = DAOCliente(DB_PATH)

# DESPUÉS — src/login.py
from src.app_context import dao as _dao
```

### Verificación

```python
>>> dao.engine is dao_personal.engine is dao_cliente.engine
True   # un solo Engine compartido por toda la app
```

**Beneficios:** una sola conexión física, configuración de `PRAGMA foreign_keys=ON`
en un solo lugar, y `DatabaseConnection.reset()` permite aislar los tests.

---

## 3. Patrón Factory Method — Creación de cuentas

**Archivo nuevo:** `src/cuenta_factory.py`
**Archivos modificados:** `src/autenticacion.py`, `src/cuenta_ahorro.py`

### Problema

La elección de la subclase de `Cuenta` estaba dispersa y duplicada en las vistas:

```python
# ANTES — src/home_cliente.py
def _nombre_tipo(cuenta):
    if isinstance(cuenta, CuentaAhorro):
        return "Caja de Ahorro"
    if isinstance(cuenta, Cuenta):
        return "Corriente"

# ANTES — src/home_operaciones.py
if etiqueta == "Caja de ahorro" and "ahorro" in nombre_tipo.lower():
    return c

# ANTES — src/autenticacion.py: siempre reconstruía Cuenta base,
# perdiendo el comportamiento de CuentaAhorro (aplicar_interes)
return [Cuenta.from_db_row(fila, cliente) for fila in filas]
```

Agregar un nuevo tipo de cuenta obligaba a tocar **todos** esos puntos
(violación del principio Open/Closed).

### Solución

`CuentaFactory` centraliza la creación. Cada tipo registra su función creadora;
la fábrica decide cuál invocar:

```python
# DESPUÉS — src/cuenta_factory.py
class CuentaFactory:
    _creadores = {}

    @classmethod
    def registrar(cls, tipo, creador):
        cls._creadores[cls._normalizar(tipo)] = creador

    @classmethod
    def crear(cls, tipo, nro_cuenta, cliente, saldo=0.0, **kwargs):
        creador = cls._creadores.get(cls._normalizar(tipo))
        if creador is None:
            raise ValueError(f"Tipo de cuenta desconocido: '{tipo}'.")
        return creador(nro_cuenta, cliente, saldo, **kwargs)

CuentaFactory.registrar("Corriente", _crear_corriente)
CuentaFactory.registrar("Ahorro", _crear_ahorro)
```

Uso en la autenticación (reconstrucción desde la BD):

```python
# DESPUÉS — src/autenticacion.py
return [
    CuentaFactory.crear_desde_fila(fila, cliente, nombres_tipo.get(fila[3], ""))
    for fila in filas
]
```

### Beneficios

- **Open/Closed:** un nuevo tipo de cuenta se soporta con
  `CuentaFactory.registrar("PlazoFijo", creador)` — sin modificar código existente
  (hay un test que lo demuestra: `test_registrar_nuevo_tipo_ocp`).
- **Corrección de bug latente:** al loguear, una cuenta de ahorro ahora se
  reconstruye como `CuentaAhorro` real (con `aplicar_interes()`), no como `Cuenta` base.

---

## 4. Patrón Builder — Construcción de Personas

**Archivo nuevo:** `src/persona_builder.py`
**Archivos modificados:** `tests/test_autenticacion.py`

### Problema

`Empleado` tiene un constructor de 10 parámetros. Las llamadas eran difíciles de
leer y de mantener:

```python
# ANTES — tests/test_autenticacion.py
empleado = Empleado(
    "Luis", "Pérez", "23456789",
    legajo="E-1001", cargo="Analista", departamento="Sistemas",
    fecha_ingreso=datetime(2024, 1, 15), salario=85000,
    sucursal="Central", password="ClaveSegura3",
)
```

### Solución

Jerarquía de builders con interfaz fluida. `PersonaBuilder` define los datos comunes;
`ClienteBuilder` y `EmpleadoBuilder` lo extienden (reutilización por herencia):

```python
# DESPUÉS
empleado = (
    EmpleadoBuilder()
    .con_nombre("Luis")
    .con_apellido("Pérez")
    .con_dni("23456789")
    .con_password("ClaveSegura3")
    .con_legajo("E-1001")
    .con_cargo("Analista")
    .con_departamento("Sistemas")
    .con_fecha_ingreso(datetime(2024, 1, 15))
    .con_salario(85000)
    .con_sucursal("Central")
    .build()
)
```

**Punto clave de diseño:** `build()` delega en el constructor de dominio, por lo que
**todas las validaciones siguen en un solo lugar** (los constructores de `Persona`,
`Cliente`, `Empleado`). Hay tests que verifican que el builder no saltea validaciones
(`test_builder_respeta_validaciones_de_dominio`).

---

## 5. Principio DRY — Utilidades de UI compartidas

**Archivo nuevo:** `src/ui_utils.py`
**Archivos modificados:** `src/home_cliente.py`, `src/home_operaciones.py`,
`src/home_historial.py`, `src/login.py`

### Problema

```python
# ANTES — copiada en home_cliente.py, home_operaciones.py y home_historial.py
def _formatear_monto(monto):
    valor = f"{monto:,.2f}"
    return "$ " + valor.replace(".", "X").replace(",", ".").replace("X", ",")

# ANTES — el SnackBar de notificación se repetía en 4 vistas con colores distintos
page.snack_bar = ft.SnackBar(ft.Text(texto), bgcolor="red" if es_error else "green")
```

### Solución

Un único módulo con la fuente de verdad:

```python
# DESPUÉS — src/ui_utils.py
class Colores:
    FONDO = "#0a0a0f"
    VIOLETA = "#8b2fc9"
    VERDE = "#16a34a"
    ROJO = "#dc2626"
    ...

def formatear_monto(monto: float) -> str: ...
def formatear_monto_con_signo(monto: float) -> str: ...
def mostrar_notificacion(page, texto, es_error=False): ...
```

Las vistas ahora importan:

```python
# DESPUÉS — src/home_cliente.py
from src.ui_utils import Colores, formatear_monto as _formatear_monto
```

---

## 6. Principios SOLID aplicados

| Principio | Aplicación concreta |
|-----------|---------------------|
| **S — Single Responsibility** | La conexión a la BD (`database.py`), la creación de cuentas (`cuenta_factory.py`), la construcción de personas (`persona_builder.py`) y las utilidades de UI (`ui_utils.py`) tienen cada una **una única razón para cambiar**. Antes, `DAO` creaba el engine *y* persistía entidades; las vistas formateaban montos *y* renderizaban. |
| **O — Open/Closed** | `CuentaFactory.registrar()` permite agregar tipos de cuenta **sin modificar** la fábrica ni las vistas. Demostrado en `test_registrar_nuevo_tipo_ocp`. |
| **L — Liskov Substitution** | `CuentaAhorro` respeta el contrato de `Cuenta` (ya existía y se preservó: `aplicar_interes()` reutiliza `depositar()`). El Factory ahora garantiza que las cuentas de ahorro se reconstruyan como `CuentaAhorro` real, haciendo efectiva la sustituibilidad. |
| **I — Interface Segregation** | Los builders especializados (`ClienteBuilder`, `EmpleadoBuilder`) exponen solo los métodos relevantes a cada entidad, heredando los comunes de `PersonaBuilder`. |
| **D — Dependency Inversion** | `Autenticacion` recibe el `DAO` por inyección de dependencias (constructor), no lo instancia. Las vistas dependen de `app_context` (abstracción del acceso a datos), no de la creación concreta de engines. |

### Otros principios y prácticas

- **DRY:** formateo de montos, notificaciones, paleta de colores y acceso al DAO
  unificados (secciones 2 y 5).
- **KISS:** el Builder convierte llamadas de 10 parámetros en pasos legibles.
- **Encapsulamiento:** los atributos privados (`__saldo`, `__dni`, etc.) se
  mantuvieron; los patrones no rompen la encapsulación existente.
- **Separación de capas:** dominio (`cuenta.py`, `cliente.py`...) / persistencia
  (`dao.py`, `models.py`, `database.py`) / presentación (vistas Flet + `ui_utils.py`).

---

## 7. Tests de los patrones

**Archivo nuevo:** `tests/test_patrones.py` — 15 tests nuevos:

| Grupo | Tests | Qué verifica |
|-------|-------|--------------|
| `TestSingleton` | 3 | Misma instancia por ruta, DAOs comparten engine, `reset()` descarta |
| `TestCuentaFactory` | 7 | Subclase correcta por tipo, case-insensitive, error en tipo desconocido, reconstrucción desde fila BD, extensibilidad OCP |
| `TestBuilders` | 5 | Construcción válida de Persona/Cliente/Empleado, validaciones de dominio no se saltean |

```bash
$ pytest tests/ -q
.....................................................sss......  [100%]
59 passed, 3 skipped in 5.34s
```

> Los 44 tests originales siguen pasando **sin modificar su lógica de negocio**:
> la refactorización no cambió comportamiento observable (refactor de verdad).

---

## 8. Resumen de archivos

### Archivos nuevos (5)

| Archivo | Patrón / Principio |
|---------|--------------------|
| `src/database.py` | **Singleton** — conexión única a la BD |
| `src/app_context.py` | **DRY** — punto de acceso compartido a los DAO |
| `src/cuenta_factory.py` | **Factory Method** — creación de cuentas por tipo |
| `src/persona_builder.py` | **Builder** — construcción fluida de Persona/Cliente/Empleado |
| `src/ui_utils.py` | **DRY** — formateo de montos, notificaciones, paleta |
| `tests/test_patrones.py` | Tests de los 3 patrones (15 casos) |

### Archivos modificados (9)

| Archivo | Cambio |
|---------|--------|
| `src/dao.py` | Usa `DatabaseConnection` (Singleton) en vez de crear su engine |
| `src/autenticacion.py` | Usa `CuentaFactory.crear_desde_fila()` |
| `src/cuenta_ahorro.py` | Acepta `**kwargs` para integrarse con la factory |
| `src/login.py` | DAO compartido + `mostrar_notificacion` de `ui_utils` |
| `src/home_cliente.py` | `formatear_monto` y `Colores` de `ui_utils` |
| `src/home_operaciones.py` | DAO compartido + utilidades de `ui_utils` |
| `src/home_historial.py` | DAO compartido + `formatear_monto_con_signo` |
| `src/home_personal.py` / `src/home_crear_cliente.py` / `src/vista_gestion_clientes.py` | DAO compartido desde `app_context` |
| `tests/test_autenticacion.py` | Usa `EmpleadoBuilder` |

---

## 🎤 Puntos clave para la presentación

1. **Singleton:** de 6 engines duplicados a 1 solo compartido — verificable con
   `dao.engine is dao_personal.engine` → `True`.
2. **Factory Method:** agregar un tipo de cuenta = 1 línea (`registrar()`),
   sin tocar código existente (Open/Closed demostrado con test).
3. **Builder:** constructor de 10 parámetros → pasos fluidos y legibles;
   las validaciones de dominio se respetan porque `build()` delega en el constructor.
4. **DRY:** `_formatear_monto` existía 3 veces; el SnackBar, 4 veces; la paleta,
   con valores distintos en cada vista. Ahora todo vive en `ui_utils.py`.
5. **Sin regresiones:** 59 tests en verde; los 44 originales pasan sin cambios
   de comportamiento.

---

## 📖 Glosario de abreviaturas

| Abreviatura | Significado | Descripción |
|-------------|-------------|-------------|
| **SOLID** | *Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion* | Conjunto de 5 principios de diseño orientado a objetos que buscan código mantenible, flexible y escalable. |
| **SRP** | *Single Responsibility Principle* (Principio de Responsabilidad Única) | Cada clase o módulo debe tener una única razón para cambiar. |
| **OCP** | *Open/Closed Principle* (Principio de Abierto/Cerrado) | El código debe estar abierto a extensión pero cerrado a modificación: se agrega comportamiento nuevo sin tocar el existente. |
| **LSP** | *Liskov Substitution Principle* (Principio de Sustitución de Liskov) | Una subclase debe poder usarse en lugar de su clase base sin alterar el comportamiento esperado. |
| **ISP** | *Interface Segregation Principle* (Principio de Segregación de Interfaces) | Es mejor tener varias interfaces específicas que una general: ningún cliente debe depender de métodos que no usa. |
| **DIP** | *Dependency Inversion Principle* (Principio de Inversión de Dependencias) | Los módulos de alto nivel no deben depender de los de bajo nivel; ambos deben depender de abstracciones. |
| **DRY** | *Don't Repeat Yourself* (No te repitas) | Cada pieza de conocimiento o lógica debe existir en un único lugar del sistema. |
| **KISS** | *Keep It Simple, Stupid* (Mantenlo simple) | La simplicidad debe ser un objetivo de diseño: evitar complejidad innecesaria. |
| **DAO** | *Data Access Object* (Objeto de Acceso a Datos) | Patrón que encapsula toda la lógica de persistencia, separándola de la lógica de negocio. |
| **ORM** | *Object-Relational Mapping* (Mapeo Objeto-Relacional) | Técnica que convierte datos entre el sistema de tipos de la BD relacional y los objetos del lenguaje (aquí: SQLAlchemy). |
| **BD** | *Base de Datos* | Sistema de almacenamiento persistente (en este proyecto: SQLite). |
| **UI** | *User Interface* (Interfaz de Usuario) | Capa de presentación con la que interactúa el usuario (en este proyecto: vistas Flet). |
| **CI/CD** | *Continuous Integration / Continuous Delivery* (Integración y Entrega Continua) | Práctica de automatizar tests y despliegues en cada cambio del repositorio (aquí: GitHub Actions). |
| **AAA** | *Arrange-Act-Assert* (Organizar-Actuar-Afirmar) | Estructura estándar de un test: preparar el escenario, ejecutar la acción, verificar el resultado. |
| **PR** | *Pull Request* | Solicitud de revisión e integración de cambios en un repositorio Git. |
