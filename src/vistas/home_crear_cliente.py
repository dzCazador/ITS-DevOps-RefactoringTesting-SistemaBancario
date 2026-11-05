import os
import sys

import flet as ft

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app_context import cliente_controller as _clientes
from src.vistas.navegacion import ir_a
from src.sesion import Sesion


# ============================================================
# PALETA CAPITAL BANK
# ============================================================

FONDO = "#08080D"
PANEL = "#11111A"
PANEL_SECUNDARIO = "#171722"

VIOLETA = "#A020F0"
VIOLETA_CLARO = "#C06CFF"
VIOLETA_OSCURO = "#6F00B8"

BLANCO = "#F8F8FF"
TEXTO = "#E7E3EF"
TEXTO_SUAVE = "#A99AB9"
LINEA = "#49305E"

VERDE = "#22C55E"
ROJO = "#EF4444"


def render_gestion_cliente(page: ft.Page, dni=None):
    """
    Crear/editar cliente con sus cuentas.
    Mantiene la lógica original y aplica el diseño visual de Capital Bank.
    """

    # Imports diferidos: home_personal importa este módulo a nivel superior,
    # así se evita el ciclo home_personal <-> home_crear_cliente.
    from src.vistas.home_personal import _aviso, _es_personal, _ir_login

    # =====================================================
    # CONFIGURACIÓN GENERAL
    # =====================================================

    page.title = "Capital Bank - Gestión cliente"
    page.bgcolor = FONDO
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 0

    if not _es_personal():
        _ir_login(page)
        return

    es_nuevo = dni is None
    datos = None if es_nuevo else _clientes.obtener_cliente_por_dni(dni)

    if not es_nuevo and datos is None:
        _aviso(page, "No existe un cliente con ese DNI.", ok=False)
        from src.vistas.home_personal import render_home_personal
        ir_a(page, render_home_personal)
        return

    id_cliente = None if es_nuevo else datos[0]

    # =====================================================
    # COMPONENTES VISUALES
    # =====================================================

    def campo(
        label,
        value="",
        password=False,
        hint_text=None,
        expand=False,
        width=None,
    ):
        return ft.TextField(
            label=label,
            value=value,
            password=password,
            can_reveal_password=password,
            hint_text=hint_text,
            width=width,
            expand=expand,
            label_style=ft.TextStyle(
                color=VIOLETA_CLARO,
                size=13,
            ),
            hint_style=ft.TextStyle(
                color="#7F748C",
                size=13,
            ),
            text_style=ft.TextStyle(
                color=BLANCO,
                size=14,
            ),
            bgcolor=PANEL_SECUNDARIO,
            border_color=VIOLETA_OSCURO,
            focused_border_color=VIOLETA_CLARO,
            border_width=1.3,
            focused_border_width=1.8,
            border_radius=8,
            cursor_color=VIOLETA_CLARO,
            content_padding=ft.Padding(
                16,
                12,
                16,
                12,
            ),
        )

    def boton_principal(texto, funcion):
        return ft.ElevatedButton(
            content=ft.Text(
                texto,
                size=15,
                weight=ft.FontWeight.BOLD,
            ),
            on_click=funcion,
            height=48,
            expand=True,
            bgcolor=VIOLETA,
            color=BLANCO,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                overlay_color="#25FFFFFF",
            ),
        )

    def boton_secundario(texto, funcion):
        return ft.OutlinedButton(
            content=ft.Text(
                texto,
                size=14,
                weight=ft.FontWeight.BOLD,
                color=VIOLETA_CLARO,
            ),
            on_click=funcion,
            height=48,
            expand=True,
            style=ft.ButtonStyle(
                side=ft.BorderSide(
                    width=1.4,
                    color=VIOLETA,
                ),
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

    def etiqueta(texto):
        return ft.Text(
            texto,
            size=13,
            weight=ft.FontWeight.W_500,
            color=VIOLETA_CLARO,
        )

    def texto_secundario(texto, size=13):
        return ft.Text(
            texto,
            size=size,
            color=TEXTO_SUAVE,
        )

    def linea():
        return ft.Divider(
            height=1,
            thickness=1,
            color=LINEA,
        )

    # =====================================================
    # DATOS DEL CLIENTE
    # =====================================================

    txt_nombre = campo(
        "Nombre",
        value="" if es_nuevo else datos[1],
        hint_text="ej. Alejandro",
        expand=True,
    )

    txt_apellido = campo(
        "Apellido",
        value="" if es_nuevo else datos[2],
        hint_text="ej. Morales",
        expand=True,
    )

    txt_dni = campo(
        "DNI",
        value="" if es_nuevo else datos[3],
        hint_text="Sin puntos, ej. 42345678",
        expand=True,
    )

    txt_clave = campo(
        "Clave nueva (vacío = no cambia)"
        if not es_nuevo
        else "Clave",
        password=True,
        hint_text="••••••••",
        expand=True,
    )

    titulo_cliente = ft.Text(
        "Alta de Cliente"
        if es_nuevo
        else f"Editar Cliente",
        size=34,
        weight=ft.FontWeight.BOLD,
        color=BLANCO,
    )

    subtitulo_cliente = ft.Text(
        "Paso a paso para registrar un nuevo usuario."
        if es_nuevo
        else f"Modificá los datos de {datos[1]} {datos[2]}.",
        size=15,
        color=VIOLETA_CLARO,
    )

    def _guardar_cliente(e):
        nonlocal es_nuevo, id_cliente, datos

        try:
            nombre = (txt_nombre.value or "").strip()
            apellido = (txt_apellido.value or "").strip()
            nuevo_dni = (txt_dni.value or "").strip()
            clave = (txt_clave.value or "").strip() or None

            if es_nuevo:
                id_cliente = _clientes.crear_cliente(
                    nombre,
                    apellido,
                    nuevo_dni,
                    clave,
                )
                _aviso(
                    page,
                    f"Cliente creado con id {id_cliente}.",
                )

            else:
                ok = _clientes.actualizar_cliente(
                    datos[3],
                    nombre,
                    apellido,
                    nuevo_dni,
                    clave,
                )

                if not ok:
                    _aviso(
                        page,
                        "El cliente ya no existe.",
                        ok=False,
                    )
                    return

                _aviso(
                    page,
                    "Cliente actualizado.",
                )

            txt_clave.value = ""
            es_nuevo = False
            datos = _clientes.obtener_cliente_por_dni(nuevo_dni)
            id_cliente = datos[0]

            titulo_cliente.value = "Editar Cliente"
            subtitulo_cliente.value = (
                f"Modificá los datos de {datos[1]} {datos[2]}."
            )
            txt_clave.label = "Clave nueva (vacío = no cambia)"

            _recargar_cuentas()
            page.update()

        except ValueError as ex:
            _aviso(
                page,
                str(ex),
                ok=False,
            )

    # =====================================================
    # CUENTAS DEL CLIENTE
    # =====================================================

    col_cuentas = ft.Column(
        spacing=10,
    )

    txt_nro = campo(
        "Número de cuenta",
        hint_text="ej. 100001",
        expand=True,
    )

    txt_saldo = campo(
        "Saldo inicial",
        hint_text="$ 0,00",
        expand=True,
    )

    dd_tipo = ft.Dropdown(
        label="Tipo de cuenta",
        expand=True,
        options=[
            ft.dropdown.Option("Ahorro", text_style=ft.TextStyle(color=BLANCO, size=14)),
            ft.dropdown.Option("Corriente", text_style=ft.TextStyle(color=BLANCO, size=14)),
        ],
        label_style=ft.TextStyle(
            color=VIOLETA_CLARO,
            size=13,
        ),
        text_style=ft.TextStyle(
            color=BLANCO,
            size=14,
        ),
        bgcolor=PANEL_SECUNDARIO,
        border_color=VIOLETA_OSCURO,
        focused_border_color=VIOLETA_CLARO,
        border_width=1.3,
        focused_border_width=1.8,
        border_radius=8,
        color=BLANCO,
        content_padding=ft.Padding(
            16,
            12,
            16,
            12,
        ),
    )

    def _recargar_cuentas():
        col_cuentas.controls.clear()

        if id_cliente is None:
            col_cuentas.controls.append(
                texto_secundario(
                    "Guardá el cliente para poder agregar cuentas."
                )
            )
            return

        cuentas = _clientes.listar_cuentas(
            id_cliente
        )

        if not cuentas:
            col_cuentas.controls.append(
                texto_secundario(
                    "Este cliente todavía no tiene cuentas registradas."
                )
            )
            return

        for id_cta, nro, _, id_tipo, saldo, tasa, _ in cuentas:
            col_cuentas.controls.append(
                ft.Container(
                    padding=ft.Padding(14, 11, 14, 11),
                    bgcolor="#14141E",
                    border_radius=8,
                    border=ft.border.all(
                        1,
                        "#3B2250",
                    ),
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                width=24,
                                height=24,
                                border_radius=6,
                                bgcolor=VIOLETA,
                                alignment=ft.alignment.center,
                                content=ft.Icon(
                                    ft.Icons.CHECK,
                                    color=BLANCO,
                                    size=16,
                                ),
                                shadow=ft.BoxShadow(
                                    blur_radius=10,
                                    color="#7AA020F0",
                                ),
                            ),
                            ft.Text(
                                str(nro),
                                color=BLANCO,
                                size=14,
                                weight=ft.FontWeight.W_500,
                                expand=True,
                            ),
                            ft.Text(
                                f"$ {saldo}",
                                color=VIOLETA_CLARO,
                                size=14,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                )
            )

    def _agregar_cuenta(e):
        try:
            if id_cliente is None:
                _aviso(
                    page,
                    "Guardá el cliente primero.",
                    ok=False,
                )
                return

            nro = (txt_nro.value or "").strip()

            id_cta = _clientes.agregar_cuenta(
                id_cliente,
                txt_nro.value,
                dd_tipo.value,
                txt_saldo.value,
            )

            _aviso(
                page,
                f"Cuenta {nro} creada con id {id_cta}.",
            )

            txt_nro.value = ""
            txt_saldo.value = ""
            dd_tipo.value = None

            _recargar_cuentas()
            page.update()

        except ValueError as ex:
            _aviso(
                page,
                str(ex),
                ok=False,
            )

    def _volver(e):
        from src.vistas.home_personal import render_home_personal
        ir_a(
            page,
            render_home_personal,
        )

    _recargar_cuentas()

    # =====================================================
    # ENCABEZADO
    # =====================================================

    logo = ft.Row(
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=54,
                height=54,
                border_radius=14,
                border=ft.border.all(2, VIOLETA),
                bgcolor="#15101D",
                alignment=ft.alignment.center,
                shadow=ft.BoxShadow(
                    blur_radius=18,
                    color="#90A020F0",
                ),
                content=ft.Icon(
                    ft.Icons.ACCOUNT_BALANCE,
                    color=VIOLETA_CLARO,
                    size=30,
                ),
            ),
            ft.Text(
                "CAPITAL\nBANK",
                size=17,
                weight=ft.FontWeight.BOLD,
                color=BLANCO,
            ),
            ft.Container(
                width=1,
                height=22,
                bgcolor=LINEA,
                margin=ft.Margin(6, 0, 6, 0),
            ),
            ft.Text(
                "VISTA PERSONAL",
                size=13,
                weight=ft.FontWeight.W_500,
                color=VIOLETA_CLARO,
            ),
        ],
    )

    # =====================================================
    # PANEL PRINCIPAL
    # =====================================================

    panel = ft.Container(
        width=850,
        padding=ft.Padding(34, 28, 34, 28),
        bgcolor=PANEL,
        border_radius=16,
        border=ft.border.all(
            2,
            VIOLETA,
        ),
        shadow=ft.BoxShadow(
            blur_radius=24,
            spread_radius=1,
            color="#70A020F0",
            offset=ft.Offset(0, 4),
        ),
        content=ft.Column(
            spacing=18,
            controls=[
                titulo_cliente,
                subtitulo_cliente,

                ft.Container(height=2),

                # Fila Nombre / Apellido
                ft.Row(
                    spacing=18,
                    controls=[
                        txt_nombre,
                        txt_apellido,
                    ],
                ),

                # Fila DNI / Clave
                ft.Row(
                    spacing=18,
                    controls=[
                        txt_dni,
                        txt_clave,
                    ],
                ),

                ft.Row(
                    controls=[
                        ft.Container(expand=True),
                        ft.Text(
                            "Mínimo 4 caracteres",
                            size=11,
                            color=TEXTO_SUAVE,
                        ),
                    ],
                ),

                linea(),

                ft.Text(
                    "Cuentas del cliente",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=VIOLETA_CLARO,
                ),

                col_cuentas,

                ft.Row(
                    spacing=14,
                    controls=[
                        txt_nro,
                        dd_tipo,
                        txt_saldo,
                    ],
                ),

                ft.ElevatedButton(
                    content=ft.Text(
                        "AGREGAR CUENTA",
                        weight=ft.FontWeight.BOLD,
                    ),
                    on_click=_agregar_cuenta,
                    bgcolor="#23142E",
                    color=VIOLETA_CLARO,
                    height=44,
                    width=220,
                    style=ft.ButtonStyle(
                        side=ft.BorderSide(
                            1.2,
                            VIOLETA,
                        ),
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),

                linea(),

                ft.Row(
                    spacing=20,
                    controls=[
                        boton_secundario(
                            "Cancelar",
                            _volver,
                        ),
                        boton_principal(
                            "Guardar cliente",
                            _guardar_cliente,
                        ),
                    ],
                ),
            ],
        ),
    )

    # =====================================================
    # PANTALLA
    # =====================================================

    page.add(
        ft.Container(
            width=float("inf"),
            padding=ft.Padding(40, 26, 40, 40),
            alignment=ft.alignment.top_center,
            content=ft.Column(
                width=850,
                spacing=18,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    logo,
                    panel,
                ],
            ),
        )
    )


if __name__ == "__main__":
    Sesion.iniciar(
        {
            "dni": "22233344",
            "rol": "personal",
            "nombre": "Carlos",
            "apellido": "Gómez",
            "cuentas": [],
        }
    )

    ft.run(render_gestion_cliente)
