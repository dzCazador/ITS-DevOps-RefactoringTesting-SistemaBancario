import flet as ft

# Estilo unificado de la botonera (diseño de Zafiro): pill con borde neón.
NEON_BORDER = "#8c1eff"
NEON_BG_BTN = "#9d00ff"
TEXT_MUTED = "#a0a0a0"


def ir_a(page: ft.Page, render_vista):
    """Limpia la página y renderiza la vista indicada (navegación entre vistas)."""
    page.clean()
    page.update()
    render_vista(page)
    page.update()


def nombre_cuenta_para_header(nombre_cuenta=None):
    """Devuelve el nombre visible de la cuenta para el encabezado."""
    nombre = (nombre_cuenta or "").strip()
    if not nombre or nombre.lower() == "todas":
        return "Mercado Pago"
    texto = nombre.lower()
    if any(token in texto for token in ("mercado", "pago", "corriente", "ahorro")):
        return "Mercado Pago"
    return nombre.title()


def _nav_btn(icono, etiqueta, activo=False, on_click=None):
    color = "#ffffff" if activo else TEXT_MUTED
    return ft.Container(
        expand=True,
        padding=ft.Padding(0, 8, 0, 8),
        bgcolor=NEON_BG_BTN if activo else None,
        border_radius=25,
        on_click=on_click,
        content=ft.Column(
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(icono, color=color, size=20),
                ft.Text(etiqueta, size=10, color=color),
            ],
        ),
    )


def crear_bottom_nav(page: ft.Page, activo: str):
    """Barra de navegación inferior compartida (Inicio/Operar/Historial).

    `activo` es una de: "inicio", "operar", "historial".
    """
    def ir_inicio(e):
        from src.vistas.home_cliente import render_home_cliente
        ir_a(page, render_home_cliente)
    def ir_operar(e):
        from src.vistas.home_operaciones import render_home_operaciones
        ir_a(page, render_home_operaciones)
    def ir_historial(e):
        from src.vistas.home_historial import render_home_historial
        ir_a(page, render_home_historial)

    return ft.Container(
        padding=4,
        border=ft.border.all(1.5, NEON_BORDER),
        border_radius=30,
        content=ft.Row(
            controls=[
                _nav_btn(ft.Icons.HOME_OUTLINED, "Inicio", activo == "inicio", on_click=ir_inicio),
                _nav_btn(ft.Icons.SWAP_HORIZ, "Operar", activo == "operar", on_click=ir_operar),
                _nav_btn(ft.Icons.SCHEDULE, "Historial", activo == "historial", on_click=ir_historial),
            ],
        ),
    )
