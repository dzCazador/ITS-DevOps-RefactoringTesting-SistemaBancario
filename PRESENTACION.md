---
marp: true
theme: default
paginate: true
header: 'Sistema Bancario — Refactorización y Dockerización'
footer: 'Refactoring & Testing • CI/CD'
backgroundColor: '#f8fafc'
color: '#1e293b'
style: |
  section {
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  }
  h1, h2, h3 {
    color: #0f172a;
  }
  a {
    color: #0284c7;
  }
  strong {
    color: #6d28d9;
  }
  table {
    font-size: 0.85rem;
  }
  .highlight {
    color: #059669;
  }
---

<!-- _class: lead -->
# 🏦 Sistema Bancario
## Arquitectura Limpia, Patrones de Diseño (GoF) y Dockerización Web

**Refactoring y Testing • Integración y Entrega Continua**
✅ 59 Tests Automatizados en Verde | 🐳 Docker & Docker Compose | 🏛️ Principios SOLID

---

## 🎯 Diapositiva 2: Objetivos del Proyecto

### Evolución Arquitectural y Calidad de Software

* **1. Refactorización & Principios SOLID:**
  * Desacoplamiento total entre las vistas de presentación y la persistencia de datos.
  * Implementación de patrones de diseño GoF: **Singleton**, **Factory Method** y **Builder**.
  * Eliminación de duplicación de código (**DRY**) en lógica y componentes de interfaz.

* **2. Testing Automatizado Riguroso:**
  * Cobertura completa de la lógica de negocio y esquemas relacionales existentes.
  * Incorporación de **15 nuevos tests unitarios** para verificar exhaustivamente los patrones.
  * Suite total de **59 pruebas automatizadas** en verde sin regresiones.

* **3. Dockerización & DevOps Moderno:**
  * Empaquetamiento de la aplicación en contenedor con **Flet Web** y **SQLite**.
  * Despliegue y ejecución de tests en un único comando mediante **Docker Compose**.
  * Persistencia garantizada de la base de datos física mediante *bind mounts*.

> **Nota para el presentador:** Enfatizar que no fue solo "hacer andar" el sistema, sino elevar su estándar de calidad arquitectónica y operativa según las mejores prácticas de la industria.

---

## 🔍 Diapositiva 3: Diagnóstico Inicial (Code Smells)

### Deuda Técnica Identificada en la Versión Anterior

| # | Problema Detectado | Módulos Afectados | Principio Violado |
|---|---|---|---|
| **1** | Múltiples instancias de `DAO("sistema_bancario.db")` generando hasta 6 engines independientes de SQLAlchemy | Todas las vistas (`login.py`, `home_personal.py`, etc.) | **DRY**, Alto Acoplamiento |
| **2** | Lógica de bifurcación de tipos de cuenta dispersa (`isinstance(c, CuentaAhorro)`) | `home_cliente.py`, `home_operaciones.py`, `home_historial.py` | **Open/Closed (OCP)** |
| **3** | Constructor telescópico en `Empleado` con **10 parámetros** obligatorios y posicionales | `empleado.py`, `test_autenticacion.py` | Legibilidad, Mantenibilidad |
| **4** | Lógica duplicada de formateo de moneda (`_formatear_monto()`) y barras de notificación | 4 vistas de presentación | **DRY** |
| **5** | Paleta de colores hardcodeada con valores hexadecimales dispersos | Código de presentación | **DRY** |

> **Nota para el presentador:** Señalar el riesgo crítico de SQLite: tener 6 pools de conexiones compitiendo sobre un archivo local podía provocar bloqueos tipo `database is locked`.

---

## 🔒 Diapositiva 4: Patrón Singleton (Conexión a BD)

### Código: Comparativa Antes vs Después

**🔴 ANTES (Dispersión de Conexiones - Hasta 6 engines compitiendo por SQLite):**
```python
# Cada vista creaba su propio DAO con un engine nuevo apuntando al mismo archivo
# login.py
_dao = DAO("sistema_bancario.db")          # engine #1
# home_personal.py
_dao = DAOPersonal("sistema_bancario.db")  # engine #2
# home_operaciones.py
_dao = DAOCliente("sistema_bancario.db")   # engine #3
```

**🟢 DESPUÉS (DatabaseConnection Singleton + app_context.py):**
```python
# src/database.py: Engine único por ruta física
class DatabaseConnection:
    _instances: dict[str, "DatabaseConnection"] = {}
    @classmethod
    def instance(cls, db_path="sistema_bancario.db"):
        if db_path not in cls._instances:
            cls._instances[db_path] = cls(db_path)
        return cls._instances[db_path]

# src/app_context.py: punto único compartido por todas las vistas
dao = DAO(DB_PATH) # dao.engine is dao_personal.engine -> True!
```

---

## 🏭 Diapositiva 5: Patrón Factory Method (Cuentas)

### Código: Comparativa Antes vs Después

**🔴 ANTES (Lógica Dispersa y Pérdida de Subclase):**
```python
# home_cliente.py
def _nombre_tipo(cuenta):
    if isinstance(cuenta, CuentaAhorro): return "Caja de Ahorro"
    if isinstance(cuenta, Cuenta): return "Corriente"

# autenticacion.py (BUG: degradaba todo a Cuenta base, perdiendo aplicar_interes)
return [Cuenta.from_db_row(fila, cliente) for fila in filas]
```

**🟢 DESPUÉS (CuentaFactory Extensible y Reconstrucción Fidedigna):**
```python
# src/modelos/cuenta_factory.py: Extensión abierta sin modificar la fábrica ni vistas (OCP)
class CuentaFactory:
    _creadores = {}
    @classmethod
    def registrar(cls, tipo, creador):
        cls._creadores[cls._normalizar(tipo)] = creador
    @classmethod
    def crear_desde_fila(cls, fila, cliente, tipo_nombre): ...

# Extensión dinámica en runtime:
CuentaFactory.registrar("PlazoFijo", _crear_plazo_fijo)
```

---

## 🔨 Diapositiva 6: Patrón Builder (Personas y Empleados)

### Código: Comparativa Antes vs Después

**🔴 ANTES (Constructor Telescópico con 10 Parámetros Posicionales):**
```python
# empleado.py y tests de autenticación: frágil ante cambios y fácil error de orden
empleado = Empleado(
    "Luis", "Pérez", "23456789", "ClaveSegura3",
    legajo="E-1001", cargo="Analista", departamento="Sistemas",
    fecha_ingreso=datetime(2024, 1, 15), salario=85000, sucursal="Central"
)
```

**🟢 DESPUÉS (Fluent Interface con EmpleadoBuilder):**
```python
# src/modelos/persona_builder.py: Construcción autodocumentada y modular
empleado = (
    EmpleadoBuilder()
    .con_nombre("Luis")
    .con_apellido("Pérez")
    .con_dni("23456789")
    .con_password("ClaveSegura3")
    .con_legajo("E-1001")
    .con_cargo("Analista")
    .con_departamento("Sistemas")
    .con_salario(85000)
    .build()  # ¡Invoca constructor real y ejecuta validaciones de dominio!
)
```

---

## 🎨 Diapositiva 7: Principio DRY y Centralización UI

### Código: Comparativa Antes vs Después

**🔴 ANTES (Lógica Duplicada en Múltiples Vistas de Presentación):**
```python
# Repetido idéntico en home_cliente.py, home_operaciones.py, home_historial.py
def _formatear_monto(monto):
    valor = f"{monto:,.2f}"
    return "$ " + valor.replace(".", "X").replace(",", ".").replace("X", ",")

# Notificaciones con colores arbitrarios e inconsistentes en 4 pantallas
page.snack_bar = ft.SnackBar(ft.Text(texto), bgcolor="red" if es_error else "green")
```

**🟢 DESPUÉS (Módulo Compartido src/vistas/ui_utils.py):**
```python
# src/vistas/ui_utils.py: Fuente única de verdad para estética y formato
class Colores:
    FONDO = "#0a0a0f"; VIOLETA = "#8b2fc9"; VERDE = "#16a34a"; ROJO = "#dc2626"

def formatear_monto(monto: float) -> str: ...
def mostrar_notificacion(page, texto, es_error=False): ...

# En todas las vistas:
from src.vistas.ui_utils import Colores, formatear_monto, mostrar_notificacion
```

---

## 📐 Diapositiva 8: Principios SOLID en Acción

### Resumen de Cumplimiento Arquitectural

| Principio | Aplicación Concreta en el Proyecto |
|---|---|
| **S — Single Responsibility** | Cada módulo con un único motivo de cambio: `database.py` (conexión), `cuenta_factory.py` (creación), `persona_builder.py` (construcción), `ui_utils.py` (formato/estilo), vistas (renderizado). |
| **O — Open/Closed** | `CuentaFactory.registrar()` permite incorporar nuevos tipos de cuenta sin editar código existente. |
| **L — Liskov Substitution** | `CuentaAhorro` sustituye a `Cuenta` respetando su contrato de depósito y saldo. La fábrica garantiza que la instancia sea del subtipo correcto. |
| **I — Interface Segregation** | Builders especializados que exponen únicamente los métodos requeridos para cada rol (`ClienteBuilder` vs `EmpleadoBuilder`). |
| **D — Dependency Inversion** | Las clases de negocio y vistas dependen de abstracciones y DAOs inyectados, no de conexiones físicas directas. |

---

## 🐳 Diapositiva 9: Dockerización — De Desktop a Web

### El Desafío Técnico de Contenedorizar Flet

```
┌───────────────────────────────────────┐
│        Navegador en el Host           │  http://localhost:8550
└──────────────────┬────────────────────┘
                   │ HTTP / WebSockets (:8550)
┌──────────────────▼─────────────────────────────────────────────────┐
│                    Contenedor Docker (Linux)                       │
│                                                                    │
│  [flet-web] (Headless Web Server)                                 │
│       │                                                            │
│       ▼                                                            │
│  [main.py] -> [src/vistas/login.py] -> [SQLAlchemy ORM]            │
│                                       │                            │
└───────────────────────────────────────┼────────────────────────────┘
                                        │ Bind Mount
                                        ▼
                             [./sistema_bancario.db] (Host)
```

* **Reto:** Flet por defecto levanta un binario Flutter Desktop. En contenedores Linux sin entorno gráfico (X11/Wayland), esto falla inmediatamente.
* **Solución:** Servidor web ASGI con `flet-web==0.28.3` escuchando en `0.0.0.0:8550`.

---

## ⚙️ Diapositiva 10: Dockerización — Adaptación de Código y Despliegue

### Código: Comparativa Antes vs Después

**🔴 ANTES (Ejecución Rígida y Despliegue Manual Dependiente del Host):**
```python
# main.py (Original)
def main(page: ft.Page):
    render_login(page)

if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)

# Proceso previo (5 pasos obligatorios en la máquina host):
# 1. python -m venv venv
# 2. .\venv\Scripts\Activate.ps1
# 3. pip install -r requirements.txt
# 4. Error en Linux headless: falta entorno gráfico de escritorio X11
# 5. python main.py
```

**🟢 DESPUÉS (main.py Dinámico y Despliegue en 1 Comando con Docker Compose):**
```python
# main.py (Refactorizado para Docker Web ASGI)
if __name__ == "__main__":
    host = os.getenv("FLET_SERVER_IP")
    port = int(os.getenv("FLET_SERVER_PORT", "0"))
    kwargs = {"target": main, "view": ft.WEB_BROWSER}
    if host: kwargs["host"] = host
    if port: kwargs["port"] = port
    ft.app(**kwargs)

# Despliegue en 1 solo comando (cero instalación en el host):
$ docker compose up --build -d
# -> Disponible de inmediato en http://localhost:8550
```

---

## 📦 Diapositiva 11: Orquestación con Docker Compose

### Despliegue Unificado y Persistencia de Datos

```yaml
services:
  banco-app:
    build: .
    container_name: sistema_bancario_app
    ports: ["8550:8550"]
    environment:
      - FLET_SERVER_IP=0.0.0.0
      - FLET_SERVER_PORT=8550
      - FLET_FORCE_WEB_SERVER=true
    volumes:
      - ./sistema_bancario.db:/app/sistema_bancario.db  # Persistencia física
    restart: unless-stopped

  test:
    build: .
    profiles: [test]
    command: pytest -v
```

* **Persistencia Total:** Los movimientos bancarios sobreviven a reinicios y reconstrucciones de contenedores.
* **Ambiente de Pruebas Aislado:** El servicio `test` corre `pytest` en el mismo runtime que producción.

---

## 🧪 Diapositiva 12: Suite de Pruebas Automatizadas

### Verificación Integral con Pytest (59 Tests en Verde)

```
============================= test session starts =============================
platform win32 / linux -- Python 3.11 / 3.13, pytest-9.2.0
collected 62 items

tests/test_autenticacion.py .....                                        [  8%]
tests/test_cliente.py ........                                           [ 20%]
tests/test_cuenta.py ..........                                          [ 37%]
tests/test_cuenta_ahorro.py ....                                         [ 43%]
tests/test_dao_schema.py ...                                             [ 48%]
tests/test_empleado.py ..                                                [ 51%]
tests/test_navegacion.py .                                               [ 53%]
tests/test_patrones.py ...............                                   [ 77%]
tests/test_persona.py ...                                                [ 82%]
tests/test_propuesta.py ..sss                                            [ 90%]
tests/test_transaccion.py ......                                         [100%]

======================== 59 passed, 3 skipped in 5.25s ========================
```

* **44 Tests de Negocio y Persistencia:** Ningún comportamiento fue alterado durante el refactor.
* **15 Tests Específicos de Patrones (`test_patrones.py`):**
  * `TestSingleton`: unicidad de conexión y aislamiento de `reset()`.
  * `TestCuentaFactory`: extensibilidad OCP, normalización y reconstrucción.
  * `TestBuilders`: fluidez sintáctica y validaciones de dominio.

---

## 🎬 Diapositiva 13: Guion de Demostración en Vivo

### Pasos para la Exposición ante los Profesores

1. **Construir y Levantar en Segundo Plano:**
   ```bash
   docker compose up --build -d
   ```
2. **Comprobar Salud y Logs del Contenedor:**
   ```bash
   docker compose ps
   docker compose logs banco-app
   ```
3. **Navegar en la Interfaz Web:**
   * Abrir `http://localhost:8550`.
   * Iniciar sesión como Personal: DNI `22233344` | Clave `admin` (Carlos Gómez).
   * Mostrar panel de clientes y operaciones monetarias con diseño unificado.
4. **Demostración de Persistencia:**
   * Detener (`docker compose down`) y reiniciar (`docker compose up -d`). Verificar datos intactos.
5. **Ejecutar Suite de Tests en Contenedor:**
   ```bash
   docker compose run --rm banco-app pytest -v
   ```

---

## 🏆 Diapositiva 14: Conclusiones y Valor Agregado

### Logros Técnicos de la Entrega

* **1. Arquitectura Profesional y Limpia:**
  * Eliminación de code smells mediante patrones creacionales canónicos (GoF).
  * Código desacoplado, legible y mantenible con principios SOLID y DRY.

* **2. Portabilidad Inmediata (DevOps):**
  * Despliegue con un único comando: `docker compose up --build -d`.
  * Cero fricción de instalación o diferencias entre sistemas operativos.

* **3. Calidad de Software Contrastada:**
  * 59 tests automatizados pasando al 100% como salvaguarda ante regresiones.

* **4. Preparación para Entornos Cloud:**
  * Contenedor OCI estándar listo para su publicación en AWS ECS, Google Cloud Run o Azure Container Apps.
