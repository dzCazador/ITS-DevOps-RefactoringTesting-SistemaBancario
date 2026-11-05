# Feature: mvc-split

## Objetivo
Separar el sistema en Modelo, Vista y Controlador (MVC) sin cambiar el comportamiento observable.

## Problema
- Modelo: existe (`cliente.py`, `cuenta.py`, `cuenta_ahorro.py`, `persona.py`, `empleado.py`, `transaccion.py`).
- Vista: existe (`login.py`, `home_*.py`, `vista_gestion_clientes.py`), pero contiene lÃ³gica de negocio y acceso ORM directo.
- Controlador: NO existe. Hay servicios sueltos (`gestion_clientes.py`, `servicios_movimientos.py`, `autenticacion.py`) sin uso uniforme.

## Alcance autorizado
- Crear `src/controladores/` con un controlador por caso de uso: `auth_controller.py`, `cliente_controller.py`, `operacion_controller.py`, `historial_controller.py`.
- Mover la lÃ³gica de negocio/persistencia de las vistas a esos controladores. Las vistas solo renderizan y delegan.
- Eliminar ORM directo en vistas (`TipoCuentaModel`, `connect()` en `home_operaciones.py`, `home_historial.py`, `home_crear_cliente.py`).
- Corregir bug: `home_operaciones.py:184` llama `_mostrar_notificacion` sin `page`.
- Actualizar `REFACTORIZACION.md` con una secciÃ³n MVC.
- Actualizar `generar_presentacion.py` con diapositivas MVC y regenerar `presentacion_sistema_bancario_actualizada.pptx`.

## Fuera de alcance
- No tocar `legacy_*.py`, `deprecated_test_*.py`, `legacy_test_*.py`.
- No commitear cambios de README.md, main.py, requirements.txt ni los archivos `.pyc` que ya estaban modificados antes de esta rama.
- No hacer push, PR ni merge.

## Restricciones
- Comportamiento observable sin cambios; los 59 tests actuales deben seguir pasando.
- Estado: 59 passed, 3 skipped en baseline (`python -m pytest tests/ -q`).
- CÃ³digo y textos tÃ©cnicos en inglÃ©s; textos de UI en el idioma actual de la app (espaÃ±ol).

## Criterios de aceptaciÃ³n
- [x] T1 Controladores creados y con tests unitarios (RED â†’ GREEN). Verificado: RED por `ModuleNotFoundError: src.controladores`; GREEN 22 passed en `tests/test_controladores.py`.
- [x] T2 Vistas `home_*`, `login.py`, `vista_gestion_clientes.py` sin imports de `dao`/`models`/`connect()`. Verificado por grep (sin coincidencias) y smoke de render de las 7 vistas.
- [x] T3 Bug de `_mostrar_notificacion` corregido con test. Verificado: RED con mensaje `Error: ... missing 1 required positional argument: 'texto'`; GREEN tras pasar `page` y mapear errores a controlador.
- [x] T4 `pytest tests/ -q` verde. Verificado: `82 passed, 3 skipped` (baseline 59 passed, 3 skipped + 23 nuevos).
- [x] T5 `REFACTORIZACION.md` con secciÃ³n MVC. Verificado: secciÃ³n 9 agregada, Ã­ndice y lÃ­nea de Resultado actualizados a 82 passed, fila MVC en el glosario.
- [x] T6 PresentaciÃ³n regenerada con diapositivas MVC. Verificado: actualizado con 17 diapositivas (14 previas + 3 MVC); `presentacion_sistema_bancario.pptx` sin cambios (SHA256 idÃ©ntico antes y despuÃ©s).

## Rutas por tarea
- T1, T2, T3: inline no aplica (2+ archivos). Delegado: un writer.
- ExploraciÃ³n ya hecha por explorer (ver handoff en Engram).

## Commits de unidad de trabajo
(se registran al cerrar cada tarea)

## Progreso
- [x] T1 Â· [x] T2 Â· [x] T3 Â· [x] T4 Â· [ ] T5 Â· [ ] T6

## Siguiente paso
Delegar writer para T1-T4; luego docs/pptx (T5-T6).
