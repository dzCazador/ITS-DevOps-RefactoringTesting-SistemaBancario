# Feature: transferencias

## Objetivo
Permitir transferir dinero desde una cuenta de un cliente a una cuenta de OTRO cliente, validando saldo.

## Diseño
- DAO (`src/dao_cliente.py`): `transferir(nro_origen, nro_destino, monto)` en UNA sola sesión/transacción: débito y crédito atómicos.
- Validaciones (en orden): monto > 0; origen y destino existen; origen != destino; destino pertenece a OTRO cliente; saldo del origen >= monto.
- Errores de dominio nuevos: `TransferenciaInvalidaError` (misma familia que `CuentaNoEncontradaError`). Saldo insuficiente usa `SaldoInsuficienteError` existente.
- Registro: dos filas en `transacciones`: `transferencia_enviada` (monto negativo en historial) y `transferencia_recibida` (positivo).
- Controlador (`src/controladores/operacion_controller.py`): `transferir(origen_etiqueta, nro_destino, texto_monto)` reutiliza `parsear_monto`.
- Historial (`src/controladores/historial_controller.py`): mapear los dos tipos nuevos a textos legibles y signos correctos.
- Vista (`src/vistas/home_operaciones.py`): opción "Transferir" y campo "Cuenta destino (nro)".

## Fuera de alcance
- No cambiar el comportamiento de depositar/retirar.
- No hacer push ni merge.
- Sin commit de .pyc ni de archivos del usuario sin trackear.

## Criterios de aceptación
- [x] X1 Tests RED: transferencia válida; saldo insuficiente no modifica saldos; destino inexistente; mismo cliente rechazado; origen == destino rechazado; monto inválido; atomicidad (si falla el crédito no queda débito).
  RED observado (antes de implementar): 14 failed, 23 passed en tests/test_controladores.py (`AttributeError: 'DAOCliente' object has no attribute 'transferir'`, idem controlador).
- [x] X2 DAO `transferir` atómico, GREEN (una sola sesión; test de atomicidad por inyección de fallo en el crédito).
- [x] X3 Controlador `transferir(cuentas, etiqueta_origen, nro_destino, texto_monto)` y mensajes de error.
- [x] X4 Historial muestra enviada/recibida con signo correcto.
- [x] X5 Vista con opción Transferir y campo destino. Sin imports de DAO/ORM (verificado por grep; la vista importa solo el controlador y `src.modelos.errores`).
- [x] X6 `python -m pytest tests/ -q` → `96 passed, 3 skipped in 15.56s` (82 previos + 14 nuevos).

## Progreso
- [x] X1 · [x] X2 · [x] X3 · [x] X4 · [x] X5 · [x] X6
