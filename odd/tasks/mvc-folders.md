# Feature: mvc-folders

## Objetivo
Reorganizar `src/` en carpetas MVC: vistas en `src/vistas/` y modelos en `src/modelos/`. Los controladores ya están en `src/controladores/`.

## Mapa de clasificación
- Vistas (`src/vistas/`): `login.py`, `navegacion.py`, `home_personal.py`, `home_cliente.py`, `home_operaciones.py`, `home_historial.py`, `home_crear_cliente.py`, `vista_gestion_clientes.py`, `ui_utils.py`.
- Renombrado (no es vista; no se mueve): `src/exportar_datos_a_pdf.py` ya no existe; su nombre actual es `src/legacy_exportar_pdf.py`.
- Modelos (`src/modelos/`): `persona.py`, `cliente.py`, `empleado.py`, `cuenta.py`, `cuenta_ahorro.py`, `transaccion.py`, `persona_builder.py`, `cuenta_factory.py`, `models.py` (ORM).
- Sin mover (no son vista ni modelo): `dao*.py`, `database.py`, `app_context.py`, `autenticacion.py`, `sesion.py`, `gestion_clientes.py`, `servicios_movimientos.py`, `controladores/`, `legacy_*.py`.

## Alcance
- `git mv` para conservar historial.
- Actualizar TODOS los imports (`src.X` → `src.vistas.X` o `src.modelos.X`) en src/, tests/ y raíz.
- Agregar `__init__.py` a cada carpeta nueva.
- Verificar que no quedan imports rotos.

## Fuera de alcance
- No cambiar lógica ni nombres de clases.
- `main.py`, `README.md` y `requirements.txt` tienen cambios sin commitear del usuario: solo tocar sus líneas de import si es necesario, y reportarlo; no commitear esos archivos.
- No commitear `.pyc` ni los `.pptx`/lock de PowerPoint.

## Criterios de aceptación
- [ ] F1 Archivos movidos con git mv a src/vistas y src/modelos.
- [x] F2 Imports actualizados en todo el repo (grep sin referencias viejas).
- [x] F3 `python -m pytest tests/ -q` = 82 passed, 3 skipped.
- [x] F4 Importar cada módulo nuevo sin error (`python -c "import src.vistas.login"`, etc.).
- [x] F5 Docs `.md` y `.pptx` con rutas nuevas (grep sin referencias viejas; pptx abren con python-pptx).

## Progreso
- [ ] F1 · [x] F2 · [x] F3 · [x] F4 · [x] F5

## Notas de ejecución
- F1 PENDIENTE: 18 de 19 vistas/modelos movidos con git mv. `src/exportar_datos_a_pdf.py` NO existe en el working tree ni en git (solo queda un .pyc huérfano en src/__pycache__); no se inventó. Decisión del padre requerida.
- F5 (verificado): rutas de módulos actualizadas en REFACTORIZACION.md, PRESENTACION.md, INTEGRACION_DAO.md, README.md (solo líneas de ruta) y en presentacion_sistema_bancario.pptx / presentacion_sistema_bancario_actualizada.pptx. En prosa "ANTES" se conserva la ruta vieja con "(ahora ...)". Respaldos de pptx con SHA256 en el directorio temporal de sesión.
