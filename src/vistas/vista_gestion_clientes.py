import os
import sys

import flet as ft

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from src.app_context import cliente_controller as _clientes


def main(page: ft.Page):

    # =====================================================
    # CONFIGURACIÓN GENERAL
    # =====================================================

    page.title = "Capital Bank - Gestión de clientes"
    page.bgcolor = "#0a0a0f"
    page.scroll = ft.ScrollMode.ADAPTIVE

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # =====================================================
    # MENSAJES
    # =====================================================

    def mostrar_mensaje(texto, error=False):

        page.snack_bar = ft.SnackBar(
            content=ft.Text(texto),
            bgcolor=(
                ft.Colors.RED_700
                if error
                else ft.Colors.GREEN_700
            ),
        )

        page.snack_bar.open = True
        page.update()

    # =====================================================
    # ESTILO DE CAMPOS
    # =====================================================

    def campo(label, password=False):

        return ft.TextField(
            label=label,
            password=password,
            can_reveal_password=password,

            label_style=ft.TextStyle(
                color="#a0a0a0"
            ),

            text_style=ft.TextStyle(
                color="#ffffff"
            ),

            bgcolor="#121212",

            border_color="#8b2fc9",
            focused_border_color="#a855f7",

            border_radius=18,

            content_padding=ft.Padding(
                18,
                12,
                18,
                12
            ),
        )

    # =====================================================
    # BE-07 - ALTA DE CLIENTE
    # =====================================================

    txt_nombre = campo("Nombre")
    txt_apellido = campo("Apellido")
    txt_dni = campo("DNI")
    txt_password = campo("Contraseña", password=True)

    def crear_cliente(e):

        try:

            id_cliente = _clientes.alta_cliente(
                txt_nombre.value,
                txt_apellido.value,
                txt_dni.value,
                password=txt_password.value
            )

            mostrar_mensaje(
                f"Cliente creado correctamente. ID: {id_cliente}"
            )

            txt_nombre.value = ""
            txt_apellido.value = ""
            txt_dni.value = ""
            txt_password.value = ""

            page.update()

        except ValueError as error:

            mostrar_mensaje(
                str(error),
                error=True
            )

    # =====================================================
    # BE-08 - ALTA DE CUENTA
    # =====================================================

    txt_dni_cuenta = campo("DNI del cliente")
    txt_numero_cuenta = campo("Número de cuenta")
    txt_saldo = campo("Saldo inicial")

    tipo_cuenta = ft.Dropdown(
        label="Tipo de cuenta",

        options=[
            ft.dropdown.Option("Ahorro"),
            ft.dropdown.Option("Corriente"),
        ],

        bgcolor="#121212",
        border_color="#8b2fc9",
        focused_border_color="#a855f7",
        border_radius=18,

        color="#ffffff",
    )

    def crear_cuenta(e):

        try:

            id_cuenta = _clientes.alta_cuenta(
                dni=txt_dni_cuenta.value,
                nro_cuenta=txt_numero_cuenta.value,
                tipo_cuenta=tipo_cuenta.value,
                saldo_inicial=txt_saldo.value
            )

            mostrar_mensaje(
                f"Cuenta creada correctamente. ID: {id_cuenta}"
            )

            txt_dni_cuenta.value = ""
            txt_numero_cuenta.value = ""
            txt_saldo.value = ""
            tipo_cuenta.value = None

            page.update()

        except ValueError as error:

            mostrar_mensaje(
                str(error),
                error=True
            )

    # =====================================================
    # BE-09 - EDITAR CLIENTE
    # =====================================================

    txt_dni_actual = campo("DNI actual")
    txt_nuevo_nombre = campo("Nuevo nombre")
    txt_nuevo_apellido = campo("Nuevo apellido")
    txt_nuevo_dni = campo("Nuevo DNI")

    txt_nueva_password = campo(
        "Nueva contraseña (opcional)",
        password=True
    )

    def modificar_cliente(e):

        try:

            _clientes.editar_cliente(
                dni_actual=txt_dni_actual.value,
                nuevo_nombre=txt_nuevo_nombre.value,
                nuevo_apellido=txt_nuevo_apellido.value,
                nuevo_dni=txt_nuevo_dni.value,
                password=(
                    txt_nueva_password.value
                    if txt_nueva_password.value
                    else None
                )
            )

            mostrar_mensaje(
                "Cliente actualizado correctamente."
            )

            txt_dni_actual.value = ""
            txt_nuevo_nombre.value = ""
            txt_nuevo_apellido.value = ""
            txt_nuevo_dni.value = ""
            txt_nueva_password.value = ""

            page.update()

        except ValueError as error:

            mostrar_mensaje(
                str(error),
                error=True
            )

    # =====================================================
    # TARJETAS
    # =====================================================

    tarjeta_cliente = ft.Container(

        width=450,
        padding=25,

        bgcolor="#181820",

        border_radius=20,

        border=ft.border.all(
            1,
            "#2d1b4e"
        ),

        content=ft.Column(

            spacing=15,

            controls=[

                ft.Text(
                    "Alta de cliente",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#ffffff",
                ),

                ft.Text(
                    "BE-07",
                    size=12,
                    color="#a855f7"
                ),

                txt_nombre,
                txt_apellido,
                txt_dni,
                txt_password,

                ft.ElevatedButton(
                    "CREAR CLIENTE",
                    on_click=crear_cliente,
                    bgcolor="#8b2fc9",
                    color="#ffffff",
                    width=400,
                ),
            ]
        )
    )

    tarjeta_cuenta = ft.Container(

        width=450,
        padding=25,

        bgcolor="#181820",

        border_radius=20,

        border=ft.border.all(
            1,
            "#2d1b4e"
        ),

        content=ft.Column(

            spacing=15,

            controls=[

                ft.Text(
                    "Alta de cuenta",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#ffffff",
                ),

                ft.Text(
                    "BE-08",
                    size=12,
                    color="#a855f7"
                ),

                txt_dni_cuenta,
                txt_numero_cuenta,
                tipo_cuenta,
                txt_saldo,

                ft.ElevatedButton(
                    "CREAR CUENTA",
                    on_click=crear_cuenta,
                    bgcolor="#8b2fc9",
                    color="#ffffff",
                    width=400,
                ),
            ]
        )
    )

    tarjeta_editar = ft.Container(

        width=450,
        padding=25,

        bgcolor="#181820",

        border_radius=20,

        border=ft.border.all(
            1,
            "#2d1b4e"
        ),

        content=ft.Column(

            spacing=15,

            controls=[

                ft.Text(
                    "Editar cliente",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#ffffff",
                ),

                ft.Text(
                    "BE-09",
                    size=12,
                    color="#a855f7"
                ),

                txt_dni_actual,
                txt_nuevo_nombre,
                txt_nuevo_apellido,
                txt_nuevo_dni,
                txt_nueva_password,

                ft.ElevatedButton(
                    "ACTUALIZAR CLIENTE",
                    on_click=modificar_cliente,
                    bgcolor="#8b2fc9",
                    color="#ffffff",
                    width=400,
                ),
            ]
        )
    )

    # =====================================================
    # PANTALLA
    # =====================================================

    page.add(

        ft.Container(

            padding=30,

            content=ft.Column(

                horizontal_alignment=ft.CrossAxisAlignment.CENTER,

                spacing=20,

                controls=[

                    ft.Text(
                        "Gestión de clientes",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color="#ffffff",
                    ),

                    ft.Text(
                        "Capital Bank",
                        size=14,
                        color="#a855f7",
                    ),

                    tarjeta_cliente,

                    tarjeta_cuenta,

                    tarjeta_editar,

                    ft.Text(
                        "© 2026 Capital Bank",
                        size=11,
                        color="#555566",
                    )
                ]
            )
        )
    )


if __name__ == "__main__":

    ft.app(
        target=main,
        view=ft.WEB_BROWSER,
        port=8551
    )