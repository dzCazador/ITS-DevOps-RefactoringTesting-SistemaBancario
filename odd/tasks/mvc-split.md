# Feature: mvc-split

## Objetivo
Separar el sistema en Modelo, Vista y Controlador (MVC) sin cambiar el comportamiento observable.

## Problema
- Modelo: existe (`cliente.py`, `cuenta.py`, `cuenta_ahorro.py`, `persona.py`, `empleado.py`, `transaccion.py`).
- Vista: existe (`login.py`, `home_*.py`, `vista_gestion_clientes.py`), pero contiene lógica de negocio y acceso ORM directo.
- Controlador: NO existe. Hay servicios sueltos (`gestion_clientes.py`, `servicios_movimientos.py`, `autenticacion.py`) sin uso uniforme.

## Alcance autorizado
- Crear `src/controladores/` con un controlador por caso de uso: `auth_controller.py`, `cliente_controller.py`, `operacion_controller.py`, `historial_controller.py`.
- Mover la lógica de negocio/persistencia de las vistas a esos controladores. Las vistas solo renderizan y delegan.
- Eliminar ORM directo en vistas (`TipoCuentaModel`, `connect()` en `home_operaciones.py`, `home_historial.py`, `home_crear_cliente.py`).
- Corregir bug: `home_operaciones.py:184` llama `_mostrar_notificacion` sin `page`.
- Actualizar `REFACTORIZACION.md` con una sección MVC.
- Actualizar `generar_presentacion.py` con diapositivas MVC y regenerar `presentacion_sistema_bancario_actualizada.pptx`.

## Fuera de alcance
- No tocar `legacy_*.py`, `deprecated_test_*.py`, `legacy_test_*.py`.
- No commitear cambios de README.md, main.py, requirements.txt ni los archivos `.pyc` que ya estaban modificados antes de esta rama.
- No hacer push, PR ni merge.

## Restricciones
- Comportamiento observable sin cambios; los 59 tests actuales deben seguir pasando.
- Estado: 59 passed, 3 skipped en baseline (`python -m pytest tests/ -q`).
- Código y textos técnicos en inglés; textos de UI en el idioma actual de la app (español).

## Criterios de aceptación
- [x] T1 Controladores creados y con tests unitarios (RED → GREEN). Verificado: RED por `ModuleNotFoundError: src.controladores`; GREEN 22 passed en `tests/test_controladores.py`.
- [x] T2 Vistas `home_*`, `login.py`, `vista_gestion_clientes.py` sin imports de `dao`/`models`/`connect()`. Verificado por grep (sin coincidencias) y smoke de render de las 7 vistas.
- [x] T3 Bug de `_mostrar_notificacion` corregido con test. Verificado: RED con mensaje `Error: ... missing 1 required positional argument: 'texto'`; GREEN tras pasar `page` y mapear errores a controlador.
- [x] T4 `pytest tests/ -q` verde. Verificado: `82 passed, 3 skipped` (baseline 59 passed, 3 skipped + 23 nuevos).
- [ ] T5 `REFACTORIZACION.md` con sección MVC.
- [ ] T6 Presentación regenerada con diapositivas MVC.

## Rutas por tarea
- T1, T2, T3: inline no aplica (2+ archivos). Delegado: un writer.
- Exploración ya hecha por explorer (ver handoff en Engram).

## Commits de unidad de trabajo
(se registran al cerrar cada tarea)

## Progreso
- [x] T1 · [x] T2 · [x] T3 · [x] T4 · [ ] T5 · [ ] T6

## Siguiente paso
Delegar writer para T1-T4; luego docs/pptx (T5-T6).
