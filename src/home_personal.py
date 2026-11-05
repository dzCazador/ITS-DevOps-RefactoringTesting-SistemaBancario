import os
import sys

import flet as ft

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app_context import cliente_controller as _clientes
from src.home_crear_cliente import render_gestion_cliente
from src.navegacion import ir_a
from src.sesion import Sesion

# Paleta de colores - Capital Bank Desktop Neon
BG_FONDO = "#0c0b11"
BG_TABLA = "#121118"
BORDE_NEON = "#9333ea"
BORDE_NEON_BRIGHT = "#a855f7"
LINEA_DIVISORIA = "#232130"
COLOR_ENCABEZADO = "#7e7894"
COLOR_BLANCO = "#ffffff"


def _es_personal():
    usuario = Sesion.actual()
    return usuario is not None and usuario.get("rol") == "personal"


def _ir_login(page):
    from src.login import render_login
    ir_a(page, render_login)


def _aviso(page, texto, ok=True):
    page.snack_bar = ft.SnackBar(
        ft.Text(texto),
        bgcolor=ft.Colors.GREEN_700 if ok else ft.Colors.RED_700,
    )
    page.snack_bar.open = True
    page.update()


def _formatear_cuentas_badges(id_cliente):
    """Renderiza las etiquetas de cuentas del cliente como badges."""
    etiquetas = _clientes.etiquetas_cuentas(id_cliente)

    if not etiquetas:
        return [ft.Text("Sin cuentas", size=11, color=COLOR_ENCABEZADO)]

    return [
        ft.Container(
            padding=ft.Padding(10, 4, 10, 4),
            border=ft.border.all(1, BORDE_NEON_BRIGHT),
            border_radius=8,
            content=ft.Text(label, size=11, color=COLOR_BLANCO),
        )
        for label in etiquetas
    ]


def render_home_personal(page: ft.Page):
    """Home del personal con diseño Capital Bank Desktop Neon."""
    page.title = "Capital Bank - Personal"
    page.window_width = 980
    page.window_height = 640
    page.window_resizable = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = BG_FONDO

    if not _es_personal():
        _ir_login(page)
        return

    nombre = Sesion.actual().get("nombre", "Personal")
    clientes = _clientes.listar_clientes()

    def _nuevo(e):
        ir_a(page, render_gestion_cliente)

    def _cerrar(e):
        Sesion.cerrar()
        _ir_login(page)

    # ---- Encabezado: Logo, Título y Acciones ----
    logo_widget = ft.Row(
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=46,
                height=52,
                border_radius=8,
                border=ft.border.all(2, BORDE_NEON_BRIGHT),
                shadow=ft.BoxShadow(
                    blur_radius=12,
                    color=BORDE_NEON,
                    offset=ft.Offset(0, 0),
                ),
                alignment=ft.alignment.center,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=1,
                    controls=[
                        ft.Icon(ft.Icons.SHIELD_OUTLINED, color=BORDE_NEON_BRIGHT, size=24),
                        ft.Text("CB", size=9, weight=ft.FontWeight.BOLD, color=BORDE_NEON_BRIGHT),
                    ],
                ),
            ),
            ft.Column(
                spacing=0,
                controls=[
                    ft.Text("CAPITAL", size=13, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO),
                    ft.Text("BANK", size=13, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO),
                ],
            ),
        ],
    )

    header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                spacing=24,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    logo_widget,
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                "VISTA PERSONAL",
                                size=11,
                                weight=ft.FontWeight.BOLD,
                                color=BORDE_NEON_BRIGHT,
                            ),
                            ft.Text(
                                "Clientes",
                                size=32,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BLANCO,
                            ),
                            ft.Text(
                                "Dale de alta a los clientes y a sus cuentas",
                                size=13,
                                color=COLOR_ENCABEZADO,
                            ),
                        ],
                    ),
                ],
            ),
            ft.Row(
                spacing=12,
                controls=[
                    ft.ElevatedButton(
                        content=ft.Text(
                            "+ Alta cliente",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=COLOR_BLANCO,
                        ),
                        bgcolor=BORDE_NEON,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=ft.Padding(20, 14, 20, 14),
                            shadow_color=BORDE_NEON_BRIGHT,
                            elevation=6,
                        ),
                        on_click=_nuevo,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.LOGOUT_ROUNDED,
                        icon_color=COLOR_ENCABEZADO,
                        icon_size=20,
                        tooltip="Cerrar sesión",
                        on_click=_cerrar,
                    ),
                ],
            ),
        ],
    )

    # ---- Tabla: Encabezados ----
    tabla_header = ft.Container(
        padding=ft.Padding(24, 16, 24, 12),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    expand=3,
                    content=ft.Text("CLIENTE", size=11, weight=ft.FontWeight.BOLD, color=COLOR_ENCABEZADO),
                ),
                ft.Container(
                    expand=2,
                    content=ft.Text("DNI", size=11, weight=ft.FontWeight.BOLD, color=COLOR_ENCABEZADO),
                ),
                ft.Container(
                    expand=3,
                    content=ft.Text("CUENTAS", size=11, weight=ft.FontWeight.BOLD, color=COLOR_ENCABEZADO),
                ),
                ft.Container(
                    expand=1,
                    alignment=ft.alignment.center_right,
                    content=ft.Text("ACCIÓN", size=11, weight=ft.FontWeight.BOLD, color=COLOR_ENCABEZADO),
                ),
            ],
        ),
    )

    # ---- Construcción de filas conservando la lógica del for ----
    filas_controles = []
    for id_cliente, nom, ape, dni, categoria, estado in clientes:
        def _abrir(e, d=dni):
            ir_a(page, lambda p: render_gestion_cliente(p, dni=d))

        fila = ft.Container(
            padding=ft.Padding(24, 14, 24, 14),
            border=ft.Border(bottom=ft.BorderSide(1, LINEA_DIVISORIA)),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # CLIENTE
                    ft.Container(
                        expand=3,
                        content=ft.Text(
                            f"{nom} {ape}",
                            size=14,
                            weight=ft.FontWeight.W_500,
                            color=COLOR_BLANCO,
                        ),
                    ),
                    # DNI
                    ft.Container(
                        expand=2,
                        content=ft.Text(
                            str(dni),
                            size=14,
                            color=COLOR_BLANCO,
                        ),
                    ),
                    # CUENTAS
                    ft.Container(
                        expand=3,
                        content=ft.Row(
                            wrap=True,
                            spacing=6,
                            controls=_formatear_cuentas_badges(id_cliente),
                        ),
                    ),
                    # ACCIÓN (Gestionar / Ver)
                    ft.Container(
                        expand=1,
                        alignment=ft.alignment.center_right,
                        content=ft.OutlinedButton(
                            content=ft.Text("Ver", size=12, color=COLOR_BLANCO),
                            style=ft.ButtonStyle(
                                side=ft.BorderSide(1, BORDE_NEON_BRIGHT),
                                shape=ft.RoundedRectangleBorder(radius=10),
                                padding=ft.Padding(18, 8, 18, 8),
                            ),
                            on_click=_abrir,
                        ),
                    ),
                ],
            ),
        )
        filas_controles.append(fila)

    if not filas_controles:
        filas_controles.append(
            ft.Container(
                padding=40,
                alignment=ft.alignment.center,
                content=ft.Text(
                    f"No hay clientes registrados en el sistema (Total: {len(clientes)}).",
                    size=13,
                    color=COLOR_ENCABEZADO,
                ),
            )
        )

    # ---- Contenedor principal de la tabla con resplandor neón ----
    tabla_contenedor = ft.Container(
        bgcolor=BG_TABLA,
        border_radius=18,
        border=ft.border.all(1.5, BORDE_NEON),
        shadow=ft.BoxShadow(
            blur_radius=18,
            color="#581c87",
            offset=ft.Offset(0, 0),
        ),
        content=ft.Column(
            spacing=0,
            controls=[
                tabla_header,
                ft.Container(height=1, bgcolor=LINEA_DIVISORIA),
                ft.Column(
                    spacing=0,
                    scroll=ft.ScrollMode.ADAPTIVE,
                    controls=filas_controles,
                ),
            ],
        ),
    )

    page.clean()
    page.add(
        ft.Container(
            padding=ft.Padding(36, 28, 36, 28),
            expand=True,
            content=ft.Column(
                expand=True,
                spacing=24,
                controls=[
                    header,
                    tabla_contenedor,
                ],
            ),
        )
    )


if __name__ == "__main__":
    from src.sesion import Sesion
    Sesion.iniciar({
        "dni": "22233344",
        "rol": "personal",
        "nombre": "Carlos",
        "apellido": "Gómez",
        "cuentas": [],
    })
    ft.app(target=render_home_personal)