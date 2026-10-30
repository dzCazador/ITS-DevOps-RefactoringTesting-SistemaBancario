import os
import sys
from datetime import datetime

import flet as ft

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app_context import dao_cliente as _dao
from src.navegacion import crear_bottom_nav, nombre_cuenta_para_header
from src.sesion import Sesion
from src.ui_utils import formatear_monto as _formatear_monto
from src.ui_utils import mostrar_notificacion as _mostrar_notificacion

BG_FONDO = "#07040d"
BG_TARJETA = "#0f081d"
NEON_PURPLE = "#b026ff"
NEON_BORDER = "#8c1eff"
NEON_BG_BTN = "#9d00ff"
TEXT_MUTED = "#a0a0a0"


def render_home_operaciones(page: ft.Page):
    page.title = "Capital Bank - Operaciones"
    # Aumentado el ancho a 520
    page.window_width = 520
    page.window_height = 700
    page.window_resizable = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = BG_FONDO

    usuario = Sesion.actual()
    cuentas = usuario.get("cuentas", []) if usuario else []
    nombre_usuario = usuario.get("nombre", "Cliente") if usuario else "Cliente"

    # Nombres de tipo desde la BD para mapear el toggle a la cuenta real.
    with _dao.connect() as _s:
        from sqlalchemy import select
        from src.models import TipoCuentaModel
        _tipos = {r.id_tipo_cuenta: r.nombre for r in
                  _s.scalars(select(TipoCuentaModel)).all()}

    def _cuenta_para_toggle(etiqueta):
        for c in cuentas:
            nombre_tipo = _tipos.get(c.get_id_tipo_cuenta(), "")
            if etiqueta == "Caja de ahorro" and "ahorro" in nombre_tipo.lower():
                return c
            if etiqueta == "Corriente" and "corriente" in nombre_tipo.lower():
                return c
        return None

    cuenta_seleccionada = ["Corriente"]
    tipo_operacion = ["Depositar"]

    # --- Filtros de Selección de Cuenta ---
    btn_cuenta_corriente = ft.Container(
        expand=True,
        padding=ft.Padding(0, 10, 0, 10),
        bgcolor=NEON_BG_BTN,
        border_radius=20,
        alignment=ft.Alignment(0, 0),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.ACCOUNT_BALANCE, color="#ffffff", size=18),
                ft.Text("Corriente", color="#ffffff", weight=ft.FontWeight.W_500, size=13),
            ],
        ),
    )

    btn_cuenta_caja = ft.Container(
        expand=True,
        padding=ft.Padding(0, 10, 0, 10),
        border=ft.border.all(1, NEON_BORDER),
        border_radius=20,
        alignment=ft.Alignment(0, 0),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.SAVINGS_OUTLINED, color="#ffffff", size=18),
                ft.Text("Caja de ahorro", color="#ffffff", size=13),
            ],
        ),
    )

    lbl_titulo_cuenta = ft.Text(
        nombre_cuenta_para_header(cuenta_seleccionada[0]),
        size=12,
        color=NEON_PURPLE,
        weight=ft.FontWeight.W_600,
    )

    def _seleccionar_cuenta(tipo, btn_sel):
        cuenta_seleccionada[0] = tipo
        lbl_titulo_cuenta.value = nombre_cuenta_para_header(tipo)
        btn_cuenta_corriente.bgcolor = None
        btn_cuenta_corriente.border = ft.border.all(1, NEON_BORDER)
        btn_cuenta_caja.bgcolor = None
        btn_cuenta_caja.border = ft.border.all(1, NEON_BORDER)

        btn_sel.bgcolor = NEON_BG_BTN
        btn_sel.border = None
        page.update()

    btn_cuenta_corriente.on_click = lambda e: _seleccionar_cuenta("Corriente", btn_cuenta_corriente)
    btn_cuenta_caja.on_click = lambda e: _seleccionar_cuenta("Caja de ahorro", btn_cuenta_caja)

    # --- Texto del botón ejecutar ---
    lbl_btn_ejecutar = ft.Text("Depositar", color="#ffffff", size=16, weight=ft.FontWeight.BOLD)

    # --- Filtros de Tipo de Operación ---
    btn_op_depositar = ft.Container(
        expand=True,
        padding=ft.Padding(0, 10, 0, 10),
        bgcolor=NEON_BG_BTN,
        border_radius=20,
        alignment=ft.Alignment(0, 0),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.ARROW_DOWNWARD_ROUNDED, color="#ffffff", size=18),
                ft.Text("Depositar", color="#ffffff", weight=ft.FontWeight.W_500, size=13),
            ],
        ),
    )

    btn_op_retirar = ft.Container(
        expand=True,
        padding=ft.Padding(0, 10, 0, 10),
        border=ft.border.all(1, NEON_BORDER),
        border_radius=20,
        alignment=ft.Alignment(0, 0),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.ARROW_UPWARD_ROUNDED, color="#ffffff", size=18),
                ft.Text("Retirar", color="#ffffff", size=13),
            ],
        ),
    )

    def _seleccionar_operacion(tipo, btn_sel):
        tipo_operacion[0] = tipo
        btn_op_depositar.bgcolor = None
        btn_op_depositar.border = ft.border.all(1, NEON_BORDER)
        btn_op_retirar.bgcolor = None
        btn_op_retirar.border = ft.border.all(1, NEON_BORDER)

        btn_sel.bgcolor = NEON_BG_BTN
        btn_sel.border = None
        lbl_btn_ejecutar.value = tipo
        page.update()

    btn_op_depositar.on_click = lambda e: _seleccionar_operacion("Depositar", btn_op_depositar)
    btn_op_retirar.on_click = lambda e: _seleccionar_operacion("Retirar", btn_op_retirar)

    # Campo de Monto
    txt_monto = ft.TextField(
        value="",
        hint_text="0,00",
        prefix=ft.Text("$  ", color="#ffffff", size=18, weight=ft.FontWeight.BOLD),
        border_color=NEON_BORDER,
        focused_border_color=NEON_PURPLE,
        border_radius=12,
        text_size=18,
        color="#ffffff",
        height=50,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    def _ejecutar_operacion(e):
        if not txt_monto.value:
            _mostrar_notificacion(page, "Ingrese un monto a operar", es_error=True)
            return

        try:
            monto_str = txt_monto.value.replace(".", "").replace(",", ".")
            monto = float(monto_str)
            if monto <= 0:
                _mostrar_notificacion("Ingrese un monto mayor a 0", es_error=True)
                return

            op = tipo_operacion[0]
            cuenta = _cuenta_para_toggle(cuenta_seleccionada[0])
            if cuenta is None:
                _mostrar_notificacion(
                    page, f"No tenés cuenta {cuenta_seleccionada[0]}.", es_error=True)
                return

            # Persiste en BD (saldo + transacción) vía DAO temporal.
            if op == "Depositar":
                _dao.depositar(cuenta, monto)
            else:
                _dao.retirar(cuenta, monto)

            txt_monto.value = ""
            _mostrar_notificacion(
                page,
                f"{op} de {_formatear_monto(monto)} en cuenta "
                f"{cuenta.get_nro_cuenta()} realizado con éxito.")
            page.update()

        except ValueError:
            _mostrar_notificacion(page, "Formato de monto inválido", es_error=True)
        except Exception as ex:
            _mostrar_notificacion(page, f"Error: {ex}", es_error=True)

    btn_ejecutar = ft.Container(
        padding=ft.Padding(0, 12, 0, 12),
        bgcolor=NEON_BG_BTN,
        border_radius=25,
        alignment=ft.Alignment(0, 0),
        on_click=_ejecutar_operacion,
        content=lbl_btn_ejecutar,
    )

    card_operar = ft.Container(
        padding=20,
        bgcolor=BG_TARJETA,
        border_radius=20,
        border=ft.border.all(1.5, NEON_BORDER),
        shadow=ft.BoxShadow(blur_radius=15, color=NEON_BORDER, offset=ft.Offset(0, 0)),
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Column(
                    spacing=2,
                    controls=[
                        lbl_titulo_cuenta,
                        ft.Text(f"Hola, {nombre_usuario}", size=22, weight=ft.FontWeight.BOLD, color="#ffffff"),
                        ft.Text("OPERAR", size=14, color="#ffffff", weight=ft.FontWeight.BOLD),
                        ft.Text("Depositar o retirar", size=13, color=NEON_PURPLE),
                    ],
                ),
                ft.Row(controls=[btn_cuenta_corriente, btn_cuenta_caja], spacing=10),
                ft.Row(controls=[btn_op_depositar, btn_op_retirar], spacing=10),
                txt_monto,
                btn_ejecutar,
            ],
        ),
    )

    # --- Navegación Inferior (compartida, estilo de Zafiro) ---
    bottom_nav = crear_bottom_nav(page, "operar")

    layout = ft.Column(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        expand=True,
        controls=[
            ft.Container(),  # Espaciador superior
            card_operar,
            bottom_nav,
        ],
    )

    page.add(ft.Container(content=layout, padding=16, expand=True))


if __name__ == "__main__":
    Sesion.iniciar({
        "dni": "40345678",
        "rol": "cliente",
        "nombre": "María",
        "apellido": "Fernández",
        "cuentas": [],
    })
    ft.run(render_home_operaciones)