import os
import sys

import flet as ft

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app_context import cliente_controller as _clientes
from src.vistas.navegacion import ir_a, crear_bottom_nav
from src.sesion import Sesion
from src.vistas.ui_utils import Colores, formatear_monto as _formatear_monto

BG_FONDO = Colores.FONDO
BG_TARJETA = Colores.TARJETA
BORDE_NEON = Colores.VIOLETA
NEON_CLARO = Colores.VIOLETA_CLARO
BORDE_TARJETA = Colores.BORDE_TARJETA
GRIS = Colores.TEXTO_SUAVE
GRIS_OSCURO = Colores.TEXTO_MUTED


def render_home_cliente(page: ft.Page):
    page.title = "Capital Bank - Home Cliente"
    page.window_width = 420
    page.window_height = 680
    page.window_resizable = False
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = BG_FONDO

    usuario = Sesion.actual()
    nombre = usuario.get("nombre", "Cliente")
    cuentas = usuario.get("cuentas", [])

    oculto_total = [True]
    ocultos_individuales = [False] * len(cuentas)
    tarjetas = []

    def _saldo_visible(indice):
        return not oculto_total[0] and not ocultos_individuales[indice]

    def _texto_saldo(monto, visible):
        return _formatear_monto(monto) if visible else "••••••"

    lbl_total = ft.Text(
        _texto_saldo(sum(c.get_saldo() for c in cuentas), False),
        size=20,
        weight=ft.FontWeight.BOLD,
        color="#ffffff",
    )

    btn_ojo_total = ft.IconButton(
        icon=ft.Icons.VISIBILITY_OFF,
        icon_color=NEON_CLARO,
        icon_size=18,
        bgcolor=BORDE_TARJETA,
        style=ft.ButtonStyle(shape=ft.CircleBorder()),
        tooltip="Mostrar/ocultar saldos",
        on_click=lambda e: _alternar_total(),
    )

    def _actualizar_visibilidad():
        lbl_total.value = _texto_saldo(
            sum(c.get_saldo() for c in cuentas), not oculto_total[0]
        )
        btn_ojo_total.icon = (
            ft.Icons.VISIBILITY_OFF if oculto_total[0] else ft.Icons.VISIBILITY
        )
        for i, tarjeta in enumerate(tarjetas):
            visible = _saldo_visible(i)
            tarjeta["lbl_saldo"].value = _texto_saldo(cuentas[i].get_saldo(), visible)
            tarjeta["btn_ojo"].icon = (
                ft.Icons.VISIBILITY_OFF if not visible else ft.Icons.VISIBILITY
            )
        page.update()

    def _alternar_total():
        oculto_total[0] = not oculto_total[0]
        _actualizar_visibilidad()

    def _alternar_individual(indice):
        ocultos_individuales[indice] = not ocultos_individuales[indice]
        _actualizar_visibilidad()

    def _cerrar_sesion(e):
        Sesion.cerrar()
        from src.vistas.login import render_login
        ir_a(page, render_login)

    def _aviso_construccion(mensaje):
        page.snack_bar = ft.SnackBar(
            ft.Text(mensaje, color="#ffffff"),
            bgcolor=BORDE_TARJETA,
        )
        page.snack_bar.open = True
        page.update()

    def _construir_tarjeta(cuenta, indice):
        lbl_saldo = ft.Text(
            _texto_saldo(cuenta.get_saldo(), False),
            size=26,
            weight=ft.FontWeight.BOLD,
            color="#ffffff",
        )
        btn_ojo = ft.IconButton(
            icon=ft.Icons.VISIBILITY_OFF,
            icon_color=NEON_CLARO,
            icon_size=16,
            bgcolor=BORDE_TARJETA,
            style=ft.ButtonStyle(shape=ft.CircleBorder()),
            tooltip="Mostrar/ocultar saldo",
            on_click=lambda e, i=indice: _alternar_individual(i),
        )
        tarjeta = ft.Container(
            padding=20,
            bgcolor=BG_TARJETA,
            border_radius=15,
            border=ft.border.all(1, BORDE_TARJETA),
            shadow=ft.BoxShadow(
                blur_radius=15,
                color=BORDE_NEON,
                offset=ft.Offset(0, 0),
            ),
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        f"{_clientes.nombre_tipo_cuenta(cuenta)} · tipo {indice + 1}",
                                        size=13,
                                        weight=ft.FontWeight.BOLD,
                                        color=GRIS,
                                    ),
                                    ft.Text(
                                        f"Nro. {cuenta.get_nro_cuenta()}",
                                        size=11,
                                        color=GRIS_OSCURO,
                                    ),
                                ],
                            ),
                            ft.Container(
                                content=ft.Text(
                                    "activa",
                                    size=10,
                                    weight=ft.FontWeight.BOLD,
                                    color=NEON_CLARO,
                                ),
                                padding=ft.Padding(10, 3, 10, 3),
                                bgcolor=BORDE_TARJETA,
                                border_radius=12,
                            ),
                        ],
                    ),
                    ft.Container(height=6),
                    lbl_saldo,
                    ft.Text(
                        "SALDO DISPONIBLE",
                        size=10,
                        color=GRIS_OSCURO,
                    ),
                    ft.Row(
                        controls=[btn_ojo],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                ],
            ),
        )
        tarjetas.append({"lbl_saldo": lbl_saldo, "btn_ojo": btn_ojo})
        return tarjeta

    # ---- Encabezado superior ----
    header = ft.Row(
        vertical_alignment=ft.CrossAxisAlignment.START,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Column(
                spacing=3,
                controls=[
                    ft.Text(
                        f"Hola, {nombre} 👋",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color="#ffffff",
                    ),
                    ft.Text(
                        "Estas son tus cuentas en Capital Bank",
                        size=13,
                        color=GRIS,
                    ),
                ],
            ),
            ft.OutlinedButton(
                content=ft.Text("Cerrar sesión", size=12, color=NEON_CLARO),
                style=ft.ButtonStyle(
                    side=ft.BorderSide(width=1, color=BORDE_NEON),
                    shape=ft.RoundedRectangleBorder(radius=18),
                    padding=ft.Padding(14, 6, 14, 6),
                ),
                on_click=_cerrar_sesion,
            ),
        ],
    )

    # ---- Control global de saldo ----
    control_total = ft.Container(
        padding=ft.Padding(18, 14, 18, 14),
        bgcolor=BG_TARJETA,
        border_radius=15,
        border=ft.border.all(1, BORDE_TARJETA),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Total en tus cuentas", size=14, color=GRIS),
                ft.Row(
                    spacing=6,
                    controls=[lbl_total, btn_ojo_total],
                ),
            ],
        ),
    )

    # ---- Tarjetas de cuentas ----
    if cuentas:
        tarjetas_col = ft.Column(
            spacing=16,
            controls=[_construir_tarjeta(c, i) for i, c in enumerate(cuentas)],
        )
    else:
        tarjetas_col = ft.Text(
            "No tenés cuentas cargadas.",
            size=13,
            color=GRIS_OSCURO,
            text_align=ft.TextAlign.CENTER,
        )

    leyenda_demo = ft.TextButton(
        content=ft.Text(
            "(demo) ver caso sin cuentas",
            size=11,
            color=GRIS_OSCURO,
        ),
        on_click=lambda e: _aviso_construccion("Caso demo: sin cuentas por mostrar."),
    )

    # ---- Barra de navegación inferior ----
    bottom_nav = crear_bottom_nav(page, "inicio")

    contenido_central = ft.Column(
        scroll=ft.ScrollMode.ADAPTIVE,
        spacing=16,
        controls=[tarjetas_col, leyenda_demo],
    )

    layout = ft.Column(
        expand=True,
        spacing=18,
        controls=[
            header,
            control_total,
            contenido_central,
            bottom_nav,
        ],
    )

    page.add(ft.Container(content=layout, padding=24, expand=True))


if __name__ == "__main__":
    from src.sesion import Sesion
    Sesion.iniciar({
        "dni": "40345678",
        "rol": "cliente",
        "nombre": "María",
        "apellido": "Fernández",
        "cuentas": [],
    })
    ft.run(render_home_cliente)