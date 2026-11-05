"""Utilidades de interfaz compartidas entre las vistas Flet (DRY).

Antes de este refactor, la función de formateo de montos y la lógica
de notificaciones (SnackBar) estaban copiadas casi idénticas en
``home_cliente.py``, ``home_operaciones.py``, ``home_historial.py`` y
``login.py``. Ahora viven en un único lugar.
"""

import flet as ft


# ============================================================
# PALETA CAPITAL BANK (única fuente de verdad para los colores)
# ============================================================

class Colores:
    FONDO = "#0a0a0f"
    TARJETA = "#181820"
    PANEL_SECUNDARIO = "#171722"

    VIOLETA = "#8b2fc9"
    VIOLETA_CLARO = "#a855f7"
    VIOLETA_OSCURO = "#6F00B8"
    BORDE_TARJETA = "#2d1b4e"

    BLANCO = "#ffffff"
    TEXTO = "#E7E3EF"
    TEXTO_SUAVE = "#a0a0a0"
    TEXTO_MUTED = "#7a7a7a"

    VERDE = "#16a34a"
    ROJO = "#dc2626"


def formatear_monto(monto: float) -> str:
    """Formatea 12500.00 -> '$ 12.500,00' (formato argentino)."""
    valor = f"{monto:,.2f}"
    return "$ " + valor.replace(".", "X").replace(",", ".").replace("X", ",")


def formatear_monto_con_signo(monto: float) -> str:
    """Formatea un movimiento: '+ 1.200,00' o '- 300,50'."""
    signo = "+ " if monto > 0 else "- "
    val = f"{abs(monto):,.2f}".replace(".", "X").replace(",", ".").replace("X", ",")
    return f"{signo}{val}"


def mostrar_notificacion(page: ft.Page, texto: str, es_error: bool = False) -> None:
    """Muestra un SnackBar de éxito (verde) o error (rojo).

    Flet 0.28 exposes ``Page.open`` as the supported way to show a
    SnackBar; assigning ``page.snack_bar`` alone does not display it.
    """
    snack = ft.SnackBar(
        ft.Text(texto, color=Colores.BLANCO),
        bgcolor=Colores.ROJO if es_error else Colores.VERDE,
    )
    page.open(snack)
