import flet as ft

from src.vistas.login import render_login


def main(page: ft.Page):
    render_login(page)


if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)
