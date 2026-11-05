"""Unit tests for the MVC controllers (src/controladores).

Controllers receive their DAO through the constructor and must not depend
on Flet. Persistence tests use a temporary SQLite file per test.
"""

import pytest

from src.modelos.cliente import Cliente
from src.controladores.auth_controller import (
    AuthController,
    CamposIncompletosError,
    CredencialesInvalidasError,
)
from src.controladores.cliente_controller import ClienteController
from src.controladores.historial_controller import HistorialController
from src.controladores.operacion_controller import (
    CuentaNoEncontradaError,
    FormatoMontoError,
    MontoNoPositivoError,
    MontoVacioError,
    OperacionController,
)
from src.modelos.cuenta import SaldoInsuficienteError
from src.modelos.cuenta_factory import CuentaFactory
from src.modelos.errores import TransferenciaInvalidaError
from src.modelos.models import TipoTransaccionModel
from src.dao_cliente import DAOCliente
from src.dao_personal import DAOPersonal
from src.database import DatabaseConnection
from src.sesion import Sesion


@pytest.fixture(autouse=True)
def _limpiar_conexiones():
    yield
    DatabaseConnection.reset()


@pytest.fixture
def dao_personal(tmp_path):
    return DAOPersonal(str(tmp_path / "controladores_personal.db"))


@pytest.fixture
def dao_cliente(tmp_path):
    return DAOCliente(str(tmp_path / "controladores_cliente.db"))


def _sembrar_cliente(dao, dni="40345678", clave="ClaveSegura1"):
    return dao.guardar_cliente(Cliente("Maria", "Fernandez", dni, password=clave))


def _cuenta_de_dominio(dao, id_cliente, dni, nro, tipo, saldo):
    """Persist an account and rebuild it as a domain object (as Sesion holds it)."""
    id_tipo = dao.guardar_tipo_cuenta(tipo)
    id_cuenta = dao.guardar_cuenta(nro, id_cliente, id_tipo, saldo=saldo)
    fila = next(f for f in dao.obtener_cuentas_por_cliente(id_cliente) if f[0] == id_cuenta)
    cliente = Cliente("Maria", "Fernandez", dni)
    return CuentaFactory.crear_desde_fila(fila, cliente, tipo)


# ============================================================
# AuthController
# ============================================================

def test_iniciar_sesion_devuelve_identidad_con_credenciales_validas(dao_personal):
    _sembrar_cliente(dao_personal)

    usuario = AuthController(dao_personal).iniciar_sesion("40345678", "ClaveSegura1")

    assert usuario["rol"] == "cliente"
    assert usuario["dni"] == "40345678"


def test_iniciar_sesion_rechaza_campos_vacios(dao_personal):
    with pytest.raises(CamposIncompletosError):
        AuthController(dao_personal).iniciar_sesion("  ", "ClaveSegura1")


def test_iniciar_sesion_rechaza_clave_incorrecta(dao_personal):
    _sembrar_cliente(dao_personal)

    with pytest.raises(CredencialesInvalidasError):
        AuthController(dao_personal).iniciar_sesion("40345678", "otra-clave")


# ============================================================
# ClienteController (panel de personal y gestion de clientes)
# ============================================================

def test_crear_cliente_persiste_y_devuelve_id(dao_personal):
    controlador = ClienteController(dao_personal)

    id_cliente = controlador.crear_cliente("Ana", "Lopez", "12345678", "ClaveSegura2")

    assert controlador.obtener_cliente_por_dni("12345678")[0] == id_cliente


def test_crear_cliente_duplicado_lanza_value_error(dao_personal):
    controlador = ClienteController(dao_personal)
    controlador.crear_cliente("Ana", "Lopez", "12345678", "ClaveSegura2")

    with pytest.raises(ValueError):
        controlador.crear_cliente("Ana", "Lopez", "12345678", "ClaveSegura2")


def test_actualizar_cliente_aplica_title_case_y_devuelve_true(dao_personal):
    controlador = ClienteController(dao_personal)
    controlador.crear_cliente("ana", "lopez", "12345678", None)

    ok = controlador.actualizar_cliente("12345678", "ana", "lopez", "12345678", None)

    assert ok is True
    datos = controlador.obtener_cliente_por_dni("12345678")
    assert (datos[1], datos[2]) == ("Ana", "Lopez")


def test_actualizar_cliente_inexistente_devuelve_false(dao_personal):
    ok = ClienteController(dao_personal).actualizar_cliente("99999999", "A", "B", "99999999", None)

    assert ok is False


def test_agregar_cuenta_reutiliza_tipo_existente_y_rechaza_segundo_del_mismo_tipo(dao_personal):
    controlador = ClienteController(dao_personal)
    id_cliente = controlador.crear_cliente("Ana", "Lopez", "12345678", None)

    id_cuenta = controlador.agregar_cuenta(id_cliente, "AR-100", "Ahorro", "250")
    assert isinstance(id_cuenta, int)

    with pytest.raises(ValueError, match="ya posee una cuenta de ese tipo"):
        controlador.agregar_cuenta(id_cliente, "AR-101", "Ahorro", "10")


def test_agregar_cuenta_valida_saldo_y_campos(dao_personal):
    controlador = ClienteController(dao_personal)
    id_cliente = controlador.crear_cliente("Ana", "Lopez", "12345678", None)

    with pytest.raises(ValueError, match="no puede ser negativo"):
        controlador.agregar_cuenta(id_cliente, "AR-200", "Corriente", "-1")
    with pytest.raises(ValueError, match="debe ser un número"):
        controlador.agregar_cuenta(id_cliente, "AR-201", "Corriente", "abc")
    with pytest.raises(ValueError, match="Completá número y tipo"):
        controlador.agregar_cuenta(id_cliente, "", "Corriente", "1")


def test_etiquetas_cuentas_sigue_la_regla_de_la_vista_original(dao_personal):
    controlador = ClienteController(dao_personal)
    id_cliente = controlador.crear_cliente("Ana", "Lopez", "12345678", None)
    controlador.agregar_cuenta(id_cliente, "ahorro-1", "Ahorro", "5")
    controlador.agregar_cuenta(id_cliente, "CC-1", "Corriente", "5")

    etiquetas = controlador.etiquetas_cuentas(id_cliente)

    assert sorted(etiquetas) == ["Caja de ahorro", "Corriente"]


def test_etiquetas_cuentas_sin_cuentas_devuelve_lista_vacia(dao_personal):
    controlador = ClienteController(dao_personal)
    id_cliente = controlador.crear_cliente("Ana", "Lopez", "12345678", None)

    assert controlador.etiquetas_cuentas(id_cliente) == []


def test_nombre_tipo_cuenta_distingue_ahorro_de_corriente(dao_personal):
    cliente = Cliente("Maria", "Fernandez", "40345678")
    ahorro = CuentaFactory.crear("Ahorro", "A-1", cliente, 10.0)
    corriente = CuentaFactory.crear("Corriente", "C-1", cliente, 10.0)

    assert ClienteController.nombre_tipo_cuenta(ahorro) == "Caja de Ahorro"
    assert ClienteController.nombre_tipo_cuenta(corriente) == "Corriente"


# ============================================================
# OperacionController
# ============================================================

def test_parsear_monto_acepta_formato_argentino(dao_cliente):
    assert OperacionController(dao_cliente).parsear_monto("1.500,50") == 1500.5


@pytest.mark.parametrize(
    "texto, error",
    [
        ("", MontoVacioError),
        ("abc", FormatoMontoError),
        ("0", MontoNoPositivoError),
        ("-5", MontoNoPositivoError),
    ],
)
def test_parsear_monto_rechaza_entradas_invalidas(dao_cliente, texto, error):
    with pytest.raises(error):
        OperacionController(dao_cliente).parsear_monto(texto)


def test_ejecutar_deposito_persiste_saldo_nuevo(dao_cliente):
    id_cliente = _sembrar_cliente(dao_cliente)
    cuenta = _cuenta_de_dominio(dao_cliente, id_cliente, "40345678", "CC-9", "Corriente", 100.0)
    controlador = OperacionController(dao_cliente)

    resultado = controlador.ejecutar_operacion([cuenta], "Corriente", "Depositar", "50")

    assert resultado.monto == 50.0
    assert resultado.nro_cuenta == "CC-9"
    assert dao_cliente.obtener_cuentas_por_cliente(id_cliente)[0][4] == 150.0


def test_ejecutar_sin_cuenta_del_tipo_lanza_cuenta_no_encontrada(dao_cliente):
    id_cliente = _sembrar_cliente(dao_cliente)
    cuenta = _cuenta_de_dominio(dao_cliente, id_cliente, "40345678", "CC-9", "Corriente", 100.0)

    with pytest.raises(CuentaNoEncontradaError):
        OperacionController(dao_cliente).ejecutar_operacion(
            [cuenta], "Caja de ahorro", "Depositar", "10"
        )


def test_ejecutar_retiro_con_saldo_insuficiente_propaga_error_de_dominio(dao_cliente):
    id_cliente = _sembrar_cliente(dao_cliente)
    cuenta = _cuenta_de_dominio(dao_cliente, id_cliente, "40345678", "CC-9", "Corriente", 10.0)

    with pytest.raises(SaldoInsuficienteError):
        OperacionController(dao_cliente).ejecutar_operacion([cuenta], "Corriente", "Retirar", "999")


# ============================================================
# HistorialController
# ============================================================

def test_movimientos_mapea_depositos_y_retiros(dao_cliente):
    id_cliente = _sembrar_cliente(dao_cliente)
    cuenta = _cuenta_de_dominio(dao_cliente, id_cliente, "40345678", "CC-9", "Corriente", 100.0)
    OperacionController(dao_cliente).ejecutar_operacion([cuenta], "Corriente", "Depositar", "50")
    OperacionController(dao_cliente).ejecutar_operacion([cuenta], "Corriente", "Retirar", "20")

    movimientos = HistorialController(dao_cliente).movimientos([cuenta])

    assert len(movimientos) == 2
    por_operacion = {m["operacion"]: m for m in movimientos}
    assert por_operacion["Depositar"]["monto"] == 50.0
    assert por_operacion["Retiro"]["monto"] == -20.0
    assert por_operacion["Depositar"]["cuenta"] == "Corriente"


def test_filtrar_todas_devuelve_todo_y_filtra_por_cuenta(dao_cliente):
    movimientos = [
        {"cuenta": "Corriente", "monto": 1.0},
        {"cuenta": "Caja de ahorro", "monto": 2.0},
    ]

    assert HistorialController.filtrar(movimientos, "Todas") == movimientos
    assert HistorialController.filtrar(movimientos, "Corriente") == [movimientos[0]]
    assert HistorialController.filtrar(movimientos, "caja de ahorro") == [movimientos[1]]


# ============================================================
# T3: regresion de home_operaciones (monto <= 0 sin page)
# ============================================================

def test_home_operaciones_notifica_monto_no_positivo_sin_error_interno(monkeypatch):
    pytest.importorskip("flet")
    import flet as ft

    import src.vistas.home_operaciones as vista

    notificaciones = []

    def registrar(page, texto, es_error=False):
        notificaciones.append((texto, es_error))

    monkeypatch.setattr(vista, "_mostrar_notificacion", registrar)

    class _PageStub:
        def __init__(self):
            self.controls = []
            self.title = ""

        def add(self, *controles):
            self.controls.extend(controles)

        def update(self):
            pass

        def clean(self):
            self.controls.clear()

    def hijos(control):
        if control is None:
            return
        yield control
        for hijo in getattr(control, "controls", None) or []:
            yield from hijos(hijo)
        yield from hijos(getattr(control, "content", None))

    page = _PageStub()
    Sesion.iniciar({"dni": "40345678", "rol": "cliente", "nombre": "Maria", "cuentas": []})
    try:
        vista.render_home_operaciones(page)
        todos = [c for raiz in page.controls for c in hijos(raiz)]
        campo = next(c for c in todos if isinstance(c, ft.TextField))
        boton = next(
            c for c in todos
            if getattr(getattr(c, "on_click", None), "__name__", "") == "_ejecutar_operacion"
        )
        campo.value = "0"

        boton.on_click(None)
    finally:
        Sesion.cerrar()

    assert notificaciones == [("Ingrese un monto mayor a 0", True)]


# ============================================================
# Transferencias entre clientes distintos
# ============================================================

def _dos_clientes_con_cuentas(dao, saldo_origen=100.0, saldo_destino=20.0):
    id_a = _sembrar_cliente(dao, dni="40345678")
    id_b = _sembrar_cliente(dao, dni="30111222")
    id_tipo = dao.guardar_tipo_cuenta("Corriente")
    dao.guardar_cuenta("CC-ORIGEN", id_a, id_tipo, saldo=saldo_origen)
    dao.guardar_cuenta("CC-DESTINO", id_b, id_tipo, saldo=saldo_destino)
    return id_a, id_b


def _saldo(dao, nro):
    return dao.obtener_cuenta_por_numero(nro)[4]


def _nombre_tipo_transaccion(dao, id_tipo):
    with dao.connect() as session:
        return session.get(TipoTransaccionModel, id_tipo).nombre


def _cuenta_dominio_por_numero(dao, nro, dni):
    fila = dao.obtener_cuenta_por_numero(nro)
    return CuentaFactory.crear_desde_fila(fila, Cliente("Maria", "Fernandez", dni), "Corriente")


def test_transferir_mueve_saldo_entre_clientes_distintos(dao_cliente):
    _dos_clientes_con_cuentas(dao_cliente)

    saldo = dao_cliente.transferir("CC-ORIGEN", "CC-DESTINO", 30.0)

    assert saldo == 70.0
    assert _saldo(dao_cliente, "CC-ORIGEN") == 70.0
    assert _saldo(dao_cliente, "CC-DESTINO") == 50.0


def test_transferir_registra_enviada_en_origen_y_recibida_en_destino(dao_cliente):
    _dos_clientes_con_cuentas(dao_cliente)

    dao_cliente.transferir("CC-ORIGEN", "CC-DESTINO", 30.0)

    enviadas = dao_cliente.obtener_transacciones_por_cuenta(dao_cliente.obtener_cuenta_por_numero("CC-ORIGEN")[0])
    recibidas = dao_cliente.obtener_transacciones_por_cuenta(dao_cliente.obtener_cuenta_por_numero("CC-DESTINO")[0])
    assert len(enviadas) == 1 and len(recibidas) == 1
    assert _nombre_tipo_transaccion(dao_cliente, enviadas[0][2]) == "transferencia_enviada"
    assert _nombre_tipo_transaccion(dao_cliente, recibidas[0][2]) == "transferencia_recibida"
    assert enviadas[0][3] == 30.0 and recibidas[0][3] == 30.0


def test_transferir_con_saldo_insuficiente_no_modifica_saldos(dao_cliente):
    _dos_clientes_con_cuentas(dao_cliente, saldo_origen=10.0)

    with pytest.raises(SaldoInsuficienteError):
        dao_cliente.transferir("CC-ORIGEN", "CC-DESTINO", 50.0)

    assert _saldo(dao_cliente, "CC-ORIGEN") == 10.0
    assert _saldo(dao_cliente, "CC-DESTINO") == 20.0


def test_transferir_a_cuenta_inexistente_lanza_cuenta_no_encontrada(dao_cliente):
    _dos_clientes_con_cuentas(dao_cliente)

    with pytest.raises(CuentaNoEncontradaError):
        dao_cliente.transferir("CC-ORIGEN", "CC-NO-EXISTE", 10.0)

    assert _saldo(dao_cliente, "CC-ORIGEN") == 100.0


def test_transferir_origen_inexistente_lanza_cuenta_no_encontrada(dao_cliente):
    _dos_clientes_con_cuentas(dao_cliente)

    with pytest.raises(CuentaNoEncontradaError):
        dao_cliente.transferir("CC-NO-EXISTE", "CC-DESTINO", 10.0)

    assert _saldo(dao_cliente, "CC-DESTINO") == 20.0


def test_transferir_entre_cuentas_del_mismo_cliente_se_rechaza(dao_cliente):
    id_a, _ = _dos_clientes_con_cuentas(dao_cliente)
    id_tipo_ahorro = dao_cliente.guardar_tipo_cuenta("Ahorro")
    dao_cliente.guardar_cuenta("AH-PROPIA", id_a, id_tipo_ahorro, saldo=5.0)

    with pytest.raises(TransferenciaInvalidaError):
        dao_cliente.transferir("CC-ORIGEN", "AH-PROPIA", 10.0)

    assert _saldo(dao_cliente, "CC-ORIGEN") == 100.0
    assert _saldo(dao_cliente, "AH-PROPIA") == 5.0


def test_transferir_a_la_misma_cuenta_se_rechaza(dao_cliente):
    _dos_clientes_con_cuentas(dao_cliente)

    with pytest.raises(TransferenciaInvalidaError):
        dao_cliente.transferir("CC-ORIGEN", "CC-ORIGEN", 10.0)

    assert _saldo(dao_cliente, "CC-ORIGEN") == 100.0


@pytest.mark.parametrize("monto", [0, -5])
def test_transferir_monto_no_positivo_se_rechaza(dao_cliente, monto):
    _dos_clientes_con_cuentas(dao_cliente)

    with pytest.raises(ValueError):
        dao_cliente.transferir("CC-ORIGEN", "CC-DESTINO", monto)

    assert _saldo(dao_cliente, "CC-ORIGEN") == 100.0


def test_transferir_si_falla_el_credito_no_queda_debito(dao_cliente, monkeypatch):
    _dos_clientes_con_cuentas(dao_cliente)
    registrar_original = DAOCliente._registrar_transaccion

    def falla_al_registrar_recibida(self, session, id_cuenta, nombre, monto):
        if nombre == "transferencia_recibida":
            raise RuntimeError("fallo simulado en el crédito")
        return registrar_original(self, session, id_cuenta, nombre, monto)

    monkeypatch.setattr(DAOCliente, "_registrar_transaccion", falla_al_registrar_recibida)

    with pytest.raises(RuntimeError):
        dao_cliente.transferir("CC-ORIGEN", "CC-DESTINO", 30.0)

    assert _saldo(dao_cliente, "CC-ORIGEN") == 100.0
    assert _saldo(dao_cliente, "CC-DESTINO") == 20.0
    assert dao_cliente.obtener_transacciones_por_cuenta(dao_cliente.obtener_cuenta_por_numero("CC-ORIGEN")[0]) == []


def test_controlador_transferir_devuelve_resultado_y_saldo_origen(dao_cliente):
    _dos_clientes_con_cuentas(dao_cliente)
    origen = _cuenta_dominio_por_numero(dao_cliente, "CC-ORIGEN", "40345678")

    resultado = OperacionController(dao_cliente).transferir([origen], "Corriente", "CC-DESTINO", "30")

    assert resultado.tipo == "Transferir"
    assert resultado.monto == 30.0
    assert resultado.nro_cuenta == "CC-ORIGEN"
    assert resultado.saldo == 70.0


def test_controlador_transferir_valida_monto_antes_de_operar(dao_cliente):
    _dos_clientes_con_cuentas(dao_cliente)
    origen = _cuenta_dominio_por_numero(dao_cliente, "CC-ORIGEN", "40345678")

    with pytest.raises(MontoVacioError):
        OperacionController(dao_cliente).transferir([origen], "Corriente", "CC-DESTINO", "")
    assert _saldo(dao_cliente, "CC-ORIGEN") == 100.0


def test_controlador_transferir_sin_cuenta_origen_del_tipo_lanza_cuenta_no_encontrada(dao_cliente):
    _dos_clientes_con_cuentas(dao_cliente)
    origen = _cuenta_dominio_por_numero(dao_cliente, "CC-ORIGEN", "40345678")

    with pytest.raises(CuentaNoEncontradaError):
        OperacionController(dao_cliente).transferir([origen], "Caja de ahorro", "CC-DESTINO", "10")


def test_movimientos_mapea_transferencias_con_signo_correcto(dao_cliente):
    _dos_clientes_con_cuentas(dao_cliente)
    origen = _cuenta_dominio_por_numero(dao_cliente, "CC-ORIGEN", "40345678")
    destino = _cuenta_dominio_por_numero(dao_cliente, "CC-DESTINO", "30111222")
    dao_cliente.transferir("CC-ORIGEN", "CC-DESTINO", 30.0)

    enviada = HistorialController(dao_cliente).movimientos([origen])
    recibida = HistorialController(dao_cliente).movimientos([destino])

    assert [(m["operacion"], m["monto"]) for m in enviada] == [("Transferencia enviada", -30.0)]
    assert [(m["operacion"], m["monto"]) for m in recibida] == [("Transferencia recibida", 30.0)]


# ============================================================
# N1/N2: feedback de operaciones (SnackBar abierto con page.open)
# ============================================================

class _PageStub:
    """Minimal Flet page: records opened controls and ignores updates."""

    def __init__(self):
        self.abiertos = []
        self.controls = []
        self.title = ""
        self.snack_bar = None

    def open(self, control):
        self.abiertos.append(control)

    def add(self, *controles):
        self.controls.extend(controles)

    def update(self):
        pass

    def clean(self):
        self.controls.clear()


def _todos_los_controles(raiz):
    if raiz is None:
        return
    yield raiz
    for hijo in getattr(raiz, "controls", None) or []:
        yield from _todos_los_controles(hijo)
    yield from _todos_los_controles(getattr(raiz, "content", None))


def test_mostrar_notificacion_error_abre_snackbar_rojo_con_page_open():
    pytest.importorskip("flet")
    import flet as ft

    from src.vistas.ui_utils import Colores, mostrar_notificacion

    page = _PageStub()

    mostrar_notificacion(page, "Ingrese un monto a operar", es_error=True)

    assert len(page.abiertos) == 1
    snack = page.abiertos[0]
    assert isinstance(snack, ft.SnackBar)
    assert snack.content.value == "Ingrese un monto a operar"
    assert snack.content.color == Colores.BLANCO
    assert snack.bgcolor == Colores.ROJO


def test_mostrar_notificacion_exito_abre_snackbar_verde_con_page_open():
    pytest.importorskip("flet")

    from src.vistas.ui_utils import Colores, mostrar_notificacion

    page = _PageStub()

    mostrar_notificacion(page, "Depositar de $ 50,00 realizado con éxito.")

    assert len(page.abiertos) == 1
    assert page.abiertos[0].content.value == "Depositar de $ 50,00 realizado con éxito."
    assert page.abiertos[0].bgcolor == Colores.VERDE


@pytest.fixture
def abrir_operaciones(monkeypatch):
    """Render home_operaciones with a temporary DAO and a session holding ``cuentas``."""
    pytest.importorskip("flet")
    import src.vistas.home_operaciones as vista

    def abrir(dao, cuentas):
        monkeypatch.setattr(vista, "_operaciones", OperacionController(dao))
        page = _PageStub()
        Sesion.iniciar({"dni": "40345678", "rol": "cliente", "nombre": "Maria", "cuentas": cuentas})
        vista.render_home_operaciones(page)
        return page

    yield abrir
    Sesion.cerrar()


def _boton_ejecutar(page):
    return next(
        c for c in _todos_los_controles(page.controls[0])
        if getattr(getattr(c, "on_click", None), "__name__", "") == "_ejecutar_operacion"
    )


def _boton_operacion(page, texto):
    import flet as ft

    return next(
        c for c in _todos_los_controles(page.controls[0])
        if isinstance(c, ft.Container) and isinstance(c.content, ft.Row)
        and any(isinstance(h, ft.Text) and h.value == texto for h in c.content.controls)
    )


def _campo_monto(page):
    import flet as ft

    return next(c for c in _todos_los_controles(page.controls[0]) if isinstance(c, ft.TextField))


def _dropdown_destino(page):
    import flet as ft

    return next(c for c in _todos_los_controles(page.controls[0]) if isinstance(c, ft.Dropdown))


def test_operacion_con_monto_vacio_muestra_error_via_page_open(dao_cliente, abrir_operaciones):
    from src.vistas.ui_utils import Colores

    id_cliente = _sembrar_cliente(dao_cliente)
    cuenta = _cuenta_de_dominio(dao_cliente, id_cliente, "40345678", "CC-9", "Corriente", 100.0)
    page = abrir_operaciones(dao_cliente, [cuenta])
    _campo_monto(page).value = ""

    _boton_ejecutar(page).on_click(None)

    assert len(page.abiertos) == 1
    assert page.abiertos[0].content.value == "Ingrese un monto a operar"
    assert page.abiertos[0].bgcolor == Colores.ROJO


def test_deposito_valido_muestra_confirmacion_via_page_open(dao_cliente, abrir_operaciones):
    from src.vistas.ui_utils import Colores

    id_cliente = _sembrar_cliente(dao_cliente)
    cuenta = _cuenta_de_dominio(dao_cliente, id_cliente, "40345678", "CC-9", "Corriente", 100.0)
    page = abrir_operaciones(dao_cliente, [cuenta])
    _boton_operacion(page, "Depositar").on_click(None)
    _campo_monto(page).value = "50"

    _boton_ejecutar(page).on_click(None)

    assert len(page.abiertos) == 1
    texto = page.abiertos[0].content.value
    assert "realizado con éxito" in texto and "CC-9" in texto
    assert page.abiertos[0].bgcolor == Colores.VERDE


def test_transferencia_valida_muestra_confirmacion_via_page_open(dao_cliente, abrir_operaciones):
    _dos_clientes_con_cuentas(dao_cliente)
    origen = _cuenta_dominio_por_numero(dao_cliente, "CC-ORIGEN", "40345678")
    page = abrir_operaciones(dao_cliente, [origen])
    _boton_operacion(page, "Transferir").on_click(None)
    _dropdown_destino(page).value = "CC-DESTINO"
    _campo_monto(page).value = "30"

    _boton_ejecutar(page).on_click(None)

    assert len(page.abiertos) == 1
    assert page.abiertos[0].content.value == (
        "Transferencia de $ 30,00 desde cuenta CC-ORIGEN a cuenta CC-DESTINO realizada con éxito."
    )
    assert _saldo(dao_cliente, "CC-ORIGEN") == 70.0


# ============================================================
# D1/D2: listado de cuentas destino y selector Dropdown
# ============================================================

def test_listar_cuentas_destino_devuelve_titular_tipo_y_numero(dao_cliente):
    _dos_clientes_con_cuentas(dao_cliente)

    destinos = {d.nro_cuenta: d for d in OperacionController(dao_cliente).listar_cuentas_destino()}

    assert set(destinos) == {"CC-ORIGEN", "CC-DESTINO"}
    destino = destinos["CC-DESTINO"]
    assert (destino.nombre, destino.apellido, destino.tipo) == ("Maria", "Fernandez", "Corriente")


def test_listar_cuentas_destino_usa_una_sola_consulta(dao_cliente):
    from sqlalchemy import event

    _dos_clientes_con_cuentas(dao_cliente)
    sentencias = []

    def contar(conn, cursor, statement, parameters, context, executemany):
        sentencias.append(statement)

    event.listen(dao_cliente.engine, "before_cursor_execute", contar)
    try:
        dao_cliente.listar_cuentas_destino()
    finally:
        event.remove(dao_cliente.engine, "before_cursor_execute", contar)

    assert len(sentencias) == 1


def test_selector_destino_solo_visible_en_transferir_y_con_etiquetas(dao_cliente, abrir_operaciones):
    import flet as ft

    _dos_clientes_con_cuentas(dao_cliente)
    origen = _cuenta_dominio_por_numero(dao_cliente, "CC-ORIGEN", "40345678")
    page = abrir_operaciones(dao_cliente, [origen])

    assert isinstance(_dropdown_destino(page), ft.Dropdown)
    assert _dropdown_destino(page).visible is False
    _boton_operacion(page, "Transferir").on_click(None)
    assert _dropdown_destino(page).visible is True
    _boton_operacion(page, "Depositar").on_click(None)
    assert _dropdown_destino(page).visible is False

    opciones = {op.key: op.text for op in _dropdown_destino(page).options}
    assert opciones == {
        "CC-ORIGEN": "Maria Fernandez — Corriente — CC-ORIGEN",
        "CC-DESTINO": "Maria Fernandez — Corriente — CC-DESTINO",
    }
