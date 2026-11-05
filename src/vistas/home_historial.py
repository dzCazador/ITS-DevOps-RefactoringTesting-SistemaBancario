import os
import sys
import flet as ft

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.app_context import historial_controller as _historial
from src.vistas.navegacion import crear_bottom_nav, ir_a, nombre_cuenta_para_header
from src.sesion import Sesion
from src.vistas.ui_utils import formatear_monto_con_signo as _formatear_monto_mov

# Paleta de colores
BG_FONDO = "#07040d"
BG_TARJETA = "#0f081d"
NEON_PURPLE = "#b026ff"
NEON_BORDER = "#8c1eff"
NEON_BG_BTN = "#9d00ff"
GREEN_NEON = "#4ade80"
RED_NEON = "#f87171"
TEXT_MUTED = "#a0a0a0"


def render_home_historial(page: ft.Page):
    page.title = "Capital Bank - Historial"
    # Aumentado el ancho a 520
    page.window_width = 520
    page.window_height = 700
    page.window_resizable = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = BG_FONDO

    usuario = Sesion.actual()
    if not usuario:
        from src.vistas.login import render_login
        ir_a(page, render_login)
        return
    nombre = usuario.get("nombre", "Cliente")
    cuentas = usuario.get("cuentas", [])

    # Transacciones reales de la BD, adaptadas al formato de esta vista.
    historial_lista = _historial.movimientos(cuentas)

    filtro_activo = ["Todas"]
    col_filas = ft.Column(spacing=14)

    def _cerrar_sesion(e):
        Sesion.cerrar()
        from src.vistas.login import render_login
        ir_a(page, render_login)

    def _actualizar_tabla():
        col_filas.controls.clear()
        filtrados = _historial.filtrar(historial_lista, filtro_activo[0])

        if not filtrados:
            col_filas.controls.append(
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text("Sin movimientos registrados", color=TEXT_MUTED, size=13),
                )
            )
        else:
            for item in filtrados:
                es_positivo = item.get("monto", 0) > 0
                color_monto = GREEN_NEON if es_positivo else RED_NEON

                col_filas.controls.append(
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(item.get("fecha", ""), size=12, color="#ffffff", expand=2),
                            ft.Text(item.get("operacion", ""), size=12, color="#ffffff", expand=2),
                            ft.Text(item.get("cuenta", ""), size=12, color="#ffffff", expand=3),
                            ft.Text(
                                _formatear_monto_mov(item.get("monto", 0)),
                                size=12,
                                weight=ft.FontWeight.W_500,
                                color=color_monto,
                                text_align=ft.TextAlign.RIGHT,
                                expand=3,
                            ),
                        ],
                    )
                )
        page.update()

    lbl_titulo_cuenta = ft.Text(
        nombre_cuenta_para_header("Mercado Pago"),
        size=12,
        color=NEON_PURPLE,
        weight=ft.FontWeight.W_600,
    )

    btn_todas = ft.Container(
        expand=True,
        padding=ft.Padding(0, 8, 0, 8),
        bgcolor=NEON_BG_BTN,
        border_radius=20,
        alignment=ft.Alignment(0, 0),
        content=ft.Text("Todas", color="#ffffff", weight=ft.FontWeight.W_500, size=12),
    )
    btn_corriente = ft.Container(
        expand=True,
        padding=ft.Padding(0, 8, 0, 8),
        border=ft.border.all(1, NEON_BORDER),
        border_radius=20,
        alignment=ft.Alignment(0, 0),
        content=ft.Text("Corriente", color="#ffffff", size=12),
    )
    btn_caja = ft.Container(
        expand=True,
        padding=ft.Padding(0, 8, 0, 8),
        border=ft.border.all(1, NEON_BORDER),
        border_radius=20,
        alignment=ft.Alignment(0, 0),
        content=ft.Text("Caja de ahorro", color="#ffffff", size=12),
    )

    def _aplicar_filtro(nombre_filtro, btn_sel):
        filtro_activo[0] = nombre_filtro
        lbl_titulo_cuenta.value = nombre_cuenta_para_header(nombre_filtro)
        for b in [btn_todas, btn_corriente, btn_caja]:
            b.bgcolor = None
            b.border = ft.border.all(1, NEON_BORDER)

        btn_sel.bgcolor = NEON_BG_BTN
        btn_sel.border = None
        _actualizar_tabla()

    btn_todas.on_click = lambda e: _aplicar_filtro("Todas", btn_todas)
    btn_corriente.on_click = lambda e: _aplicar_filtro("Corriente", btn_corriente)
    btn_caja.on_click = lambda e: _aplicar_filtro("Caja de ahorro", btn_caja)

    header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                spacing=12,
                controls=[
                    ft.Container(
                        width=46,
                        height=46,
                        border_radius=14,
                        border=ft.border.all(1.5, NEON_PURPLE),
                        alignment=ft.Alignment(0, 0),
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=0,
                            controls=[
                                ft.Icon(ft.Icons.ACCOUNT_BALANCE, size=18, color=NEON_PURPLE),
                                ft.Text("C|B", color=NEON_PURPLE, weight=ft.FontWeight.BOLD, size=9),
                            ],
                        ),
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            lbl_titulo_cuenta,
                            ft.Text(f"Hola, {nombre}", size=24, weight=ft.FontWeight.BOLD, color="#ffffff"),
                        ],
                    ),
                ],
            ),
            ft.Container(
                padding=ft.Padding(12, 6, 12, 6),
                border=ft.border.all(1, NEON_BORDER),
                border_radius=20,
                on_click=_cerrar_sesion,
                content=ft.Row(
                    spacing=6,
                    controls=[
                        ft.Icon(ft.Icons.LOGOUT, size=14, color=NEON_PURPLE),
                        ft.Text("Cerrar sesión", size=11, color=NEON_PURPLE),
                    ],
                ),
            ),
        ],
    )

    card_historial = ft.Container(
        padding=18,
        bgcolor=BG_TARJETA,
        border_radius=20,
        border=ft.border.all(1.5, NEON_BORDER),
        shadow=ft.BoxShadow(blur_radius=12, color=NEON_BORDER, offset=ft.Offset(0, 0)),
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("FECHA", size=11, color=NEON_PURPLE, expand=2),
                        ft.Text("OPERACIÓN", size=11, color=NEON_PURPLE, expand=2),
                        ft.Text("CUENTA", size=11, color=NEON_PURPLE, expand=3),
                        ft.Text("MONTO", size=11, color=NEON_PURPLE, text_align=ft.TextAlign.RIGHT, expand=3),
                    ],
                ),
                ft.Divider(height=1, color="#261b3e"),
                ft.Container(
                    height=250,
                    content=ft.Column(scroll=ft.ScrollMode.ADAPTIVE, controls=[col_filas]),
                ),
            ],
        ),
    )

    # --- Navegación Inferior (compartida, estilo de Zafiro) ---
    bottom_nav = crear_bottom_nav(page, "historial")

    layout = ft.Column(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        expand=True,
        controls=[
            header,
            ft.Column(
                spacing=14,
                controls=[
                    ft.Column(
                        spacing=0,
                        controls=[
                            ft.Text("HISTORIAL", size=12, color=NEON_PURPLE, weight=ft.FontWeight.W_600),
                            ft.Text("Movimientos", size=24, weight=ft.FontWeight.BOLD, color="#ffffff"),
                        ],
                    ),
                    ft.Row(controls=[btn_todas, btn_corriente, btn_caja], spacing=8),
                    card_historial,
                ],
            ),
            bottom_nav,
        ],
    )

    page.add(ft.Container(content=layout, padding=16, expand=True))
    _actualizar_tabla()