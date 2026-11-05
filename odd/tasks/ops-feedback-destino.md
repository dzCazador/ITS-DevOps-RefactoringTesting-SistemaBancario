# Feature: feedback de operaciones y selector de cuenta destino

## Problemas
1. En la pantalla de operaciones (depositar, retirar, transferir) no aparece ningún mensaje de error ni de confirmación.
2. Transferir pide el número de cuenta destino a mano; debe ser un selector.

## Diseño
### A. Mensajes
- `src/vistas/ui_utils.py::mostrar_notificacion` asigna `page.snack_bar` y `open=True`. En Flet 0.28.3 la forma soportada es `page.open(snack)` (`Page.open` existe; `Page.show_dialog` no).
- Cambiar el helper para crear el SnackBar y llamar `page.open(snack)`, sin depender de `page.snack_bar`.
- Test RED: con un page stub que registre `open()`, `mostrar_notificacion` debe abrir un SnackBar con el texto y el color correcto.
- Test de integración de la vista: `_ejecutar_operacion` con monto vacío y con transferencia válida debe llamar al helper con el mensaje esperado.

### B. Selector de cuenta destino
- Opciones: todas las cuentas de todos los clientes, con etiqueta `Nombre Apellido — Tipo — Nº cuenta`.
- Valor interno: el número de cuenta (`nro_cuenta`), que es lo que consume `OperacionController.transferir`.
- Datos: nuevo método de lectura en el DAO o controlador (`listar_cuentas_destino()`) que devuelva nombre, apellido, tipo y número en una sola consulta. No usar N+1 si se puede evitar.
- Reemplazar `txt_destino` (TextField) por `ft.Dropdown`. Visible solo en "Transferir". Mantener la validación del dominio (mismo cliente, saldo, etc.).
- La vista no debe importar DAO ni ORM: el listado sale del controlador.

## Criterios de aceptación
- [x] N1 Test RED del helper de notificaciones; GREEN con `page.open`.
- [x] N2 Errores y confirmaciones de depositar/retirar/transferir visibles (test de la vista con page stub).
- [x] D1 Test RED del listado de destinos (nombre, tipo, número; una sola consulta). Origen no excluido (ver nota).
- [x] D2 Dropdown de destino reemplaza el TextField.
- [x] V1 `python -m pytest tests/ -q` verde (104 passed, 3 skipped).

## Progreso
- [x] N1 · [x] N2 · [x] D1 · [x] D2 · [x] V1
- Nota: el listado no excluye la cuenta origen (D2 dice que no hace falta; la validación de dominio rechaza mismo cliente). Pendiente de confirmar con el padre si el criterio D1 "sin repetir la cuenta origen" debe aplicarse.
