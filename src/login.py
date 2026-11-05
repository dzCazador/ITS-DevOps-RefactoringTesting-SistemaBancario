import base64
import os
import sys

import flet as ft

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app_context import auth_controller as _auth
from src.controladores.auth_controller import (
    CamposIncompletosError,
    CredencialesInvalidasError,
)
from src.sesion import Sesion
from src.ui_utils import mostrar_notificacion

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, "img", "logo_clean.png")
if os.path.exists(LOGO_PATH):
    with open(LOGO_PATH, "rb") as f:
        LOGO_SRC = "data:image/png;base64," + base64.b64encode(f.read()).decode()
else:
    LOGO_SRC = ""

def render_login(page: ft.Page):
    page.title = "Capital Bank - Login"
    page.window_width = 420
    page.window_height = 680
    page.window_resizable = False
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = "#0a0a0f"
    page.scroll = ft.ScrollMode.ADAPTIVE

    dni_input = ft.TextField(
        label="DNI",
        label_style=ft.TextStyle(color="#a0a0a0"),
        hint_text="Sin puntos, ej. 40345678",
        hint_style=ft.TextStyle(color="#7a7a7a"),
        text_style=ft.TextStyle(color="#ffffff"),
        bgcolor="#121212",
        border_color="#8b2fc9",
        focused_border_color="#a855f7",
        border_radius=25,
        content_padding=ft.Padding(20, 12, 20, 12),
        text_align=ft.TextAlign.CENTER,
    )

    clave_input = ft.TextField(
        label="Clave",
        label_style=ft.TextStyle(color="#a0a0a0"),
        hint_text="Tu clave",
        password=True,
        can_reveal_password=True,
        hint_style=ft.TextStyle(color="#7a7a7a"),
        text_style=ft.TextStyle(color="#ffffff"),
        bgcolor="#121212",
        border_color="#8b2fc9",
        focused_border_color="#a855f7",
        border_radius=25,
        content_padding=ft.Padding(20, 12, 20, 12),
        text_align=ft.TextAlign.CENTER,
    )

    def on_login_click(e):
        try:
            usuario = _auth.iniciar_sesion(dni_input.value, clave_input.value)
        except CamposIncompletosError:
            mostrar_mensaje("Por favor ingresa tu DNI y Clave", es_error=True)
            return
        except CredencialesInvalidasError:
            mostrar_mensaje("DNI o clave incorrectos", es_error=True)
            return

        Sesion.iniciar(usuario)
        mostrar_mensaje(f"Sesión iniciada como {usuario['rol']}", es_error=False)

        from src.home_cliente import render_home_cliente
        from src.home_personal import render_home_personal
        from src.navegacion import ir_a

        if usuario["rol"] == "cliente":
            ir_a(page, render_home_cliente)
        else:
            ir_a(page, render_home_personal)

    def mostrar_mensaje(texto, es_error=False):
        mostrar_notificacion(page, texto, es_error)

    btn_ingresar = ft.Button(
        content=ft.Text("INGRESAR", size=15, weight=ft.FontWeight.BOLD, color="#ffffff"),
        on_click=on_login_click,
        style=ft.ButtonStyle(
            bgcolor="#8b2fc9",
            padding=ft.Padding(0, 15, 0, 15),
            shape=ft.RoundedRectangleBorder(radius=25),
            elevation=5
        ),
        width=300
    )

    btn_olvido = ft.TextButton(
        content=ft.Text("¿Olvidaste tu clave?", size=12, color="#a855f7"),
        on_click=lambda _: mostrar_mensaje("Contacta a soporte técnico", es_error=False)
    )

    login_card = ft.Container(
        width=340,
        padding=30,
        bgcolor="#181820",
        border_radius=20,
        border=ft.border.all(1, "#2d1b4e"),
        shadow=ft.BoxShadow(
            blur_radius=25,
            color="#8b2fc9",
            offset=ft.Offset(0, 0)
        ),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,
            controls=[
                ft.Container(
                    content=ft.Image(
                        src=LOGO_SRC or LOGO_PATH,
                        width=140,
                        height=140,
                        fit="contain",
                    ),
                    alignment=ft.Alignment(0, 0),
                    width=280
                ),
                ft.Container(height=2),
                ft.Text(
                    "Ingresá con tu DNI para ver tus cuentas",
                    size=13,
                    color="#a0a0a0",
                    text_align=ft.TextAlign.CENTER,
                ),
                dni_input,
                clave_input,
                ft.Container(height=2),
                btn_ingresar,
                btn_olvido,
                ft.Text(
                    "Personal: DNI 22233344 / clave admin123",
                    size=11,
                    color="#7a7a7a",
                    text_align=ft.TextAlign.CENTER,
                ),
            ]
        )
    )

    footer = ft.Text(
        "© 2026 Capital Bank • Sistema Bancario Seguro",
        size=11,
        color="#555566",
        text_align=ft.TextAlign.CENTER
    )

    main_layout = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=25,
        controls=[
            login_card,
            footer
        ]
    )

    page.add(main_layout)

if __name__ == "__main__":
    ft.run(render_login)