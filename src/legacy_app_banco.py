import flet as ft
import threading
from src.modelos.cliente import Cliente
from src.modelos.cuenta import Cuenta, SaldoInsuficienteError
from src.tarjeta import Tarjeta
from src.modelos.transaccion import Transaccion
from src.modelos.cuenta_ahorro import CuentaAhorro
from src.legacy_exportar_pdf import generar_pdf_reporte
from src.dao import DAO

class SaldoInsuficienteError(Exception): pass
class LimiteExcedidoError(Exception): pass 

# ====== INICIALIZAR DAO ======
dao = DAO("sistema_bancario.db")

# --- Función Principal (main)---
def main(page: ft.Page):
    page.title = "Registro Financiero POO"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 30
    page.scroll = ft.ScrollMode.ADAPTIVE

    
    estado = {"id_cliente": None, "id_cuenta": None, "id_tarjeta": None}
    
    # Cargar clientes desde BD
    clientes_db = dao.obtener_todos_clientes()

    lista_clientes_column = ft.Column(scroll=ft.ScrollMode.ALWAYS, spacing=5, height=200)
    btn_nuevo_cliente = ft.ElevatedButton(text="➕ Registrar Nuevo Cliente", icon=ft.Icons.PERSON_ADD)

    # Botón para exportar datos a PDF
    btn_exportar_pdf = ft.ElevatedButton(
        text="Exportar datos en PDF",
        icon=ft.Icons.PICTURE_AS_PDF,

        bgcolor=ft.Colors.RED_700,
        color=ft.Colors.WHITE
    )
    exportar_container = ft.Container(
        content=btn_exportar_pdf,
        alignment=ft.alignment.center,
        padding=ft.padding.only(top=30)
    )

    # --- Funciones Auxiliares ---
    def mostrar_notificacion(texto, color=ft.Colors.GREEN_700, duracion=3000):
        page.snack_bar = ft.SnackBar(ft.Text(texto), bgcolor=color, duration=duracion)
        page.snack_bar.open = True
        page.update()

        
    def actualizar_historial_transacciones():
        historial_column.controls.clear()
        if estado["cuenta"]:
            transacciones = estado["cuenta"].get_transacciones()
            if not transacciones:
                 historial_column.controls.append(ft.Text("No hay transacciones registradas.", italic=True))
            else:
                for t in reversed(transacciones):
                    color = ft.Colors.GREEN_700 if t.get_tipo() in ["deposito", "interes"] else ft.Colors.RED_700
                    historial_column.controls.append(ft.Text(t.__str__(), size=12, color=color, font_family="monospace"))
        page.update()

    def actualizar_historial_tarjeta():
    
        historial_tarjeta_column.controls.clear()
        
        if estado["tarjeta"]:
            # Obtener movimientos de la tarjeta
            movimientos = estado["tarjeta"].get_movimientos()
            if not movimientos:
                historial_tarjeta_column.controls.append(ft.Text("No hay movimientos registrados.", italic=True))
            else:
                # Mostrar movimientos en orden inverso (más reciente primero)
                for fecha, monto, tipo in reversed(movimientos):
                    
                    color = ft.Colors.RED_700 if tipo == "Compra" else ft.Colors.GREEN_700
                    
                    movimiento_str = f"{fecha.strftime('%Y-%m-%d %H:%M:%S')} | {tipo.upper():<10} | ${monto:.2f}"
                    
                    historial_tarjeta_column.controls.append(
                        ft.Text(movimiento_str, size=12, color=color, font_family="monospace")
                    )
        page.update()
    def actualizar_saldo_cuenta():
        if estado["cuenta"]:
            lbl_saldo_cuenta.value = f"Saldo Actual: ${estado['cuenta'].get_saldo():.2f}"
            actualizar_historial_transacciones()
            toggle_retiro_button()
        page.update()
        
    def actualizar_saldo_tarjeta():
        if estado["tarjeta"]:
            lbl_limite_tarjeta.value = f"Límite Total: ${estado['tarjeta'].get_limite():.2f}"
            lbl_saldo_tarjeta.value = f"Deuda Actual: ${estado['tarjeta'].get_saldo_actual():.2f}"
            toggle_compra_button() 
        page.update()

    def toggle_retiro_button(e=None):
        """Habilita o deshabilita el botón de retiro basado en el saldo y el monto ingresado."""
        if estado["cuenta"] is None:
            # Si no hay cuenta, siempre debe estar deshabilitado
            btn_retirar.disabled = True
            return
        # Solo si hay cuenta, intentamos obtener el monto
        try:
            monto_ingresado = float(txt_monto_cuenta.value)
            saldo_actual = estado["cuenta"].get_saldo()

            # La lógica clave:
            if monto_ingresado > 0 and monto_ingresado <= saldo_actual:
                btn_retirar.disabled = False  # Habilitar
            else:
                btn_retirar.disabled = True  # Deshabilitar
                
        except ValueError:
            # Si el valor no es un número válido (ej. está vacío o es solo un '.'), deshabilitar
            btn_retirar.disabled = True
            
        page.update() # Reflejar el cambio en la interfaz

    def toggle_compra_button(e=None):
        """Habilita o deshabilita el botón de compra basado en el límite disponible y el monto ingresado."""
        if estado["tarjeta"] is None:
            # Si no hay tarjeta, siempre debe estar deshabilitado
            btn_comprar.disabled = True
            return

        try:
            monto_ingresado = float(txt_monto_tarjeta.value)
            
            limite_disponible = estado["tarjeta"].get_limite() 

            # La lógica clave:
            if monto_ingresado > 0 and monto_ingresado <= limite_disponible:
                btn_comprar.disabled = False  # Habilitar
            else:
                btn_comprar.disabled = True  # Deshabilitar
                
        except ValueError:
            # Si el valor no es un número válido (ej. está vacío), deshabilitar
            btn_comprar.disabled = True
            
        page.update()

    def exportar_datos_a_pdf(e):
        
        if estado["cliente"] is None:
            mostrar_notificacion("❌ Error: Primero registre y seleccione un cliente.", ft.Colors.RED_700)
            return
        cliente_actual = estado["cliente"]
        cuenta_actual = estado["cuenta"]
        tarjeta_actual = estado["tarjeta"]

        mostrar_notificacion(f"💾 Generando PDF para {cliente_actual.get_nombre()}...", ft.Colors.AMBER_700, 5000)

        # Inicia un hilo para la exportación a PDF
        threading.Thread(
            # El hilo ejecuta la función de manejo de resultados, pasándole la función FPDF
            target=lambda: _manejar_resultado_pdf(
                _generar_y_guardar_pdf(cliente_actual, cuenta_actual, tarjeta_actual)
            )
        ).start()
    def mostrar_notificacion(texto, color=ft.Colors.GREEN_700, duracion_ms=3000):
    
        page.snack_bar = ft.SnackBar(
            ft.Text(texto),
            bgcolor=color,
            duration=duracion_ms 
        )
        page.snack_bar.open = True
        page.update()
    def _manejar_resultado_pdf(resultado):

        
        exito, mensaje = resultado
        if exito:
            mostrar_notificacion(f"✅ Exportación exitosa. Archivo '{mensaje}' creado.", ft.Colors.GREEN_700, 7000)
        else:
            mostrar_notificacion(f"❌ Error al guardar PDF: {mensaje}", ft.Colors.RED_700, 7000)   

    def _generar_y_guardar_pdf(cliente_actual, cuenta_actual, tarjeta_actual):
       
        # --- Validación inicial ---
        if cliente_actual is None:
             return False, "No hay cliente seleccionado para exportar."
        
        from src.modelos.cuenta_ahorro import CuentaAhorro 
        
        # --- Generación del PDF ---
        return generar_pdf_reporte(
            cliente_actual, 
            cuenta_actual, 
            tarjeta_actual, 
            CuentaAhorro, 
            ft.Colors      
        )

    # --- Interfaz Cliente ---
    txt_nombre = ft.TextField(
        label="Nombre", 
        input_filter=ft.InputFilter(r"[a-zA-Z\s]"),
        width=300
        )
    
    txt_apellido = ft.TextField(
        input_filter=ft.InputFilter(r"[a-zA-Z\s]"),
        label="Apellido", 
        width=300
        )

    txt_dni = ft.TextField(label="DNI", keyboard_type=ft.KeyboardType.NUMBER , width=300,)
    btn_registrar_cliente = ft.ElevatedButton(text="Registrar Cliente", icon=ft.Icons.PERSON_ADD)
    
    # --- Interfaz Cuenta ---
    txt_nro_cuenta = ft.TextField(
        label="Número de Cuenta", 
        width=300, 
        input_filter=ft.InputFilter(r"[0-9]"),
        )

    txt_saldo_inicial = ft.TextField(
        label="Saldo Inicial", 
        width=300, value="0.0", 
        keyboard_type=ft.KeyboardType.NUMBER
        )

    txt_interes = ft.TextField(
        label="Tasa de Interés (%)", 
        width=300, value="1.0", 
        visible=False, 
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(r"[0-9\.]")
        )
    
    dropdown_tipo_cuenta = ft.Dropdown(
        width=300, label="Tipo de Cuenta", 
        options=[ft.dropdown.Option("Cuenta Corriente"), 
                 ft.dropdown.Option("Ahorro")], 
        value="Cuenta Corriente"
        )
    
    btn_crear_cuenta = ft.ElevatedButton(
        text="Crear Cuenta", 
        icon=ft.Icons.ACCOUNT_BALANCE
        )
    
    # Operaciones Cuenta
    lbl_saldo_cuenta = ft.Text("Saldo Actual: $0.00", 
        size=16, 
        weight=ft.FontWeight.BOLD
        )

    txt_monto_cuenta = ft.TextField(
        label="Monto (Depósito/Retiro)", 
        width=300,
        keyboard_type=ft.KeyboardType.NUMBER,

        on_change=toggle_retiro_button,
        )
    
    btn_depositar = ft.ElevatedButton(
        text="Depositar", 
        icon=ft.Icons.ARROW_UPWARD, 
        disabled=True
        )
    
    btn_retirar = ft.ElevatedButton(
        text="Retirar", 
        icon=ft.Icons.ARROW_DOWNWARD, 
        disabled=True
        )
    
    btn_aplicar_interes = ft.ElevatedButton(
        text="Aplicar Interés", 
        icon=ft.Icons.REPLAY_10, 
        disabled=True, 
        visible=False
        )

    # --- Interfaz Tarjeta ---

    txt_nro_tarjeta = ft.TextField(
        label="Número de Tarjeta", 
        width=300, 
        keyboard_type=ft.KeyboardType.NUMBER
        )
  
    txt_limite_tarjeta = ft.TextField(
        label="Límite de Crédito", 
        width=300, value="10000.0", 
        input_filter=ft.InputFilter(r"[0-9\.]")
        )
    
    btn_crear_tarjeta = ft.ElevatedButton(text="Emitir Tarjeta", icon=ft.Icons.CREDIT_CARD)

    # Operaciones Tarjeta

    lbl_limite_tarjeta = ft.Text("Límite Total: $0.00", size=16, weight=ft.FontWeight.BOLD)
    
    lbl_saldo_tarjeta = ft.Text("Deuda Actual: $0.00", size=16, weight=ft.FontWeight.BOLD)
    
    txt_monto_tarjeta = ft.TextField(
        label="Monto (Compra/Pago)", 
        width=300, 
        keyboard_type=ft.KeyboardType.NUMBER,
        on_change=toggle_compra_button
        )
    
    btn_comprar = ft.ElevatedButton(
        text="Realizar Compra", 
        icon=ft.Icons.SHOPPING_CART, 
        disabled=True
        )
    
    btn_pagar = ft.ElevatedButton(
        text="Pagar Tarjeta", 
        icon=ft.Icons.PAYMENT, 
        disabled=True
        )
    
    # --- Historial de Transacciones ---
    historial_column = ft.Column(
        [ft.Text("No hay transacciones registradas.", italic=True)], 
                 scroll=ft.ScrollMode.ADAPTIVE, 
                 height=150
                 )
    
    historial_container = ft.Container(
        content=ft.Column(
            [ft.Text("Historial de Transacciones", size=18, weight=ft.FontWeight.BOLD), 
                     historial_column], 
                     horizontal_alignment=ft.CrossAxisAlignment.START, 
                     spacing=10
                     ),
        padding=10, border_radius=10, width=350, visible=False
    )

    # --- Historial de Movimientos de Tarjeta ---
    historial_tarjeta_column = ft.Column(
        [ft.Text("No hay movimientos registrados.", italic=True)], 
                 scroll=ft.ScrollMode.ADAPTIVE, 
                 height=150
                 )
    
    historial_tarjeta_container = ft.Container(
        content=ft.Column(
            [ft.Text("Historial de Tarjeta", size=18, weight=ft.FontWeight.BOLD), 
                     historial_tarjeta_column], 
                     horizontal_alignment=ft.CrossAxisAlignment.START, 
                     spacing=10
                     ),
        padding=10, border_radius=10, width=350, visible=False
    )

    # Contenedores de Formulario y Operaciones

    cuenta_form_container = ft.Column(
        [ft.Text("2. Crear Cuenta", size=20, weight=ft.FontWeight.BOLD), 
                 dropdown_tipo_cuenta, 
                 txt_nro_cuenta, 
                 txt_saldo_inicial, 
                 txt_interes, 
                 btn_crear_cuenta
                 ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10, disabled=True,
    )

    tarjeta_form_container = ft.Column(
        [ft.Text("3. Emitir Tarjeta", size=20, weight=ft.FontWeight.BOLD), 
                 txt_nro_tarjeta, 
                 txt_limite_tarjeta, 
                 btn_crear_tarjeta
                 ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10, disabled=True,
    )

    gestion_clientes_container = ft.Container(
        content=ft.Column(
            [
                ft.Text("4. Clientes Registrados", size=20, weight=ft.FontWeight.BOLD),
                btn_nuevo_cliente,
                ft.Divider(),
                lista_clientes_column, 
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        ),
        padding=20,
        border_radius=10,
        width=350,
        height=380 
    )
    operaciones_cuenta_contenido = ft.Container(
        content=ft.Column(
            [lbl_saldo_cuenta, 
             txt_monto_cuenta, 
             ft.Row([btn_depositar, btn_retirar], 
                    alignment=ft.MainAxisAlignment.CENTER), 
                    btn_aplicar_interes], 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                    spacing=10
                    ), 
                    visible=False, width=350, padding=10
    )
    operaciones_tarjeta_contenido = ft.Container(
        content=ft.Column(
            [
                lbl_limite_tarjeta, 
                lbl_saldo_tarjeta, 
                txt_monto_tarjeta, 
                ft.Row([btn_comprar, btn_pagar], alignment=ft.MainAxisAlignment.CENTER),
                historial_tarjeta_container
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        ),  
        visible=False, width=350, padding=10
    )

    contenedor_operaciones_cuenta_final = ft.Container(
        content=ft.Column(
            [
                ft.Text("Operaciones Cuenta", size=18, weight=ft.FontWeight.BOLD),
                
                operaciones_cuenta_contenido,  
                historial_container
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=20, border_radius=10, width=370, visible=False,
    )

    contenedor_operaciones_tarjeta_final = ft.Container(
        content=ft.Column(
            [
                ft.Text("Operaciones Tarjeta", size=18, weight=ft.FontWeight.BOLD),

                operaciones_tarjeta_contenido 
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=20, border_radius=10, width=370, visible=False,
    )

    # ----------------- Lógica del Negocio de la Aplicación -----------------
    def actualizar_tarjeta_clientes():
        lista_clientes_column.controls.clear()
        
        if not clientes_registrados:
            lista_clientes_column.controls.append(ft.Text("No hay clientes registrados.", italic=True))
        else:
            for cliente in clientes_registrados:
                cliente_row = ft.Row(
                    [
                        ft.Text(f"{cliente.get_nombre()} {cliente.get_apellido()} (DNI: {cliente._Cliente__dni})", size=14),
                        
                        ft.ElevatedButton(
                            "Seleccionar",
                            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                            
                            on_click=lambda e, c=cliente: seleccionar_cliente(c), 
                        
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
                lista_clientes_column.controls.append(cliente_row)
        page.update()

    def seleccionar_cliente(cliente_seleccionado):
    
        # Restablece la cuenta y tarjeta antiguas
        estado["cuenta"] = None
        estado["tarjeta"] = None
        estado["cliente"] = cliente_seleccionado # 1. Establece el cliente seleccionado
        
        # Restablece visualmente el formulario de registro 
        txt_nombre.value = cliente_seleccionado.get_nombre()
        txt_apellido.value = cliente_seleccionado.get_apellido()
        
        txt_dni.value = cliente_seleccionado._Cliente__dni 
    
        # Habilita las secciones de productos (Cuenta/Tarjeta) y deshabilita el registro
        btn_registrar_cliente.disabled = True
        cuenta_form_container.disabled = False
        tarjeta_form_container.disabled = False
        
        # Oculta las operaciones hasta que se creen productos para este cliente
        operaciones_cuenta_contenido.visible = False
        operaciones_tarjeta_contenido.visible = False
        historial_container.visible = False
        
        mostrar_notificacion(f"👤 Cliente '{cliente_seleccionado.get_nombre()}' seleccionado. Cree su Cuenta y Tarjeta.", ft.Colors.AMBER_700)
        page.update()

    # Resetea el formulario para crear un nuevo cliente
    def reset_formulario_cliente(e):
        
        estado["cliente"] = None
        estado["cuenta"] = None
        estado["tarjeta"] = None
        
        txt_nombre.value = ""; txt_apellido.value = ""; txt_dni.value = ""
        btn_registrar_cliente.disabled = False # Habilita el registro
        
        # Deshabilita productos/operaciones
        cuenta_form_container.disabled = True
        tarjeta_form_container.disabled = True
        operaciones_cuenta_contenido.visible = False
        operaciones_tarjeta_contenido.visible = False
        
        mostrar_notificacion("Formulario listo. Ingrese los datos del nuevo cliente.", ft.Colors.CYAN_700)
        page.update()
        
    btn_nuevo_cliente.on_click = reset_formulario_cliente 
    def registrar_cliente(e):
        nombre, apellido, dni = txt_nombre.value.strip(), txt_apellido.value.strip(), txt_dni.value.strip()
        try:
            nuevo_cliente = Cliente(nombre, apellido, dni)
            clientes_registrados.append(nuevo_cliente)
            estado["cliente"] = nuevo_cliente
            mostrar_notificacion(f"Cliente registrado: {nuevo_cliente.__str__()}", ft.Colors.BLUE_700)
            btn_registrar_cliente.disabled = True
            cuenta_form_container.disabled = False
            tarjeta_form_container.disabled = False
            
            #  ACTUALIZAR LA TARJETA DE CLIENTES
            actualizar_tarjeta_clientes()
            page.update()
            
        except ValueError as ex:
            mostrar_notificacion(f"Error Cliente: {ex}", ft.Colors.RED_700)
            
    def crear_cuenta(e):
        nro_cuenta, tipo_cuenta = txt_nro_cuenta.value.strip(), dropdown_tipo_cuenta.value
        if not estado["cliente"]:
            mostrar_notificacion("❌ Primero debe registrar un cliente.", ft.Colors.RED_700)
            return

        try:
            saldo_inicial = float(txt_saldo_inicial.value)
            if tipo_cuenta == "Ahorro":
                interes = float(txt_interes.value)
                nueva_cuenta = CuentaAhorro(nro_cuenta, estado["cliente"], saldo_inicial, interes)
                btn_aplicar_interes.visible = True

            else:
                nueva_cuenta = Cuenta(nro_cuenta, estado["cliente"], saldo_inicial)
                btn_aplicar_interes.visible = False

            estado["cuenta"] = nueva_cuenta
            mostrar_notificacion(f"✅ Cuenta creada con éxito.", ft.Colors.GREEN_700)

            cuenta_form_container.disabled = True
            operaciones_cuenta_contenido.visible = True
            historial_container.visible = True
            btn_depositar.disabled = btn_retirar.disabled = False
            actualizar_saldo_cuenta()
        except ValueError as ex:
            mostrar_notificacion(f"⚠️ Error en cuenta: {ex}", ft.Colors.RED_700)
        except TypeError as ex:
            mostrar_notificacion(f"⚠️ Error en tipo de dato: {ex}", ft.Colors.RED_700)

    def crear_tarjeta(e):
        nro_tarjeta = txt_nro_tarjeta.value
        if estado["cliente"] is None: mostrar_notificacion(" Error: Primero debe registrar un cliente.", ft.Colors.RED_700); return
        try:
            limite = float(txt_limite_tarjeta.value)
            nueva_tarjeta = Tarjeta(numero=nro_tarjeta, cliente=estado["cliente"], limite=limite)
            estado["tarjeta"] = nueva_tarjeta
            historial_tarjeta_container.visible = True
            
            mostrar_notificacion(f" Tarjeta emitida: Nro {nueva_tarjeta.get_numero()}", ft.Colors.INDIGO_700)
            tarjeta_form_container.disabled = True
            operaciones_tarjeta_contenido.visible = True
            btn_comprar.disabled = btn_pagar.disabled = False
            actualizar_saldo_tarjeta()

        except ValueError as ex: mostrar_notificacion(f" Error Tarjeta: {ex}", ft.Colors.RED_700)
            
    def depositar(e):
        try:
            monto = float(txt_monto_cuenta.value)
            estado["cuenta"].depositar(monto)
            mostrar_notificacion(f"💰 Depósito de ${monto:.2f} realizado.", ft.Colors.GREEN_700)
            actualizar_saldo_cuenta()
        except (ValueError, TypeError) as ex:
            mostrar_notificacion(f"❌ Error depósito: {ex}", ft.Colors.RED_700)


    def retirar(e):
        try:
            monto = float(txt_monto_cuenta.value)
            estado["cuenta"].retirar(monto)
            mostrar_notificacion(f"💸 Retiro de ${monto:.2f} realizado.", ft.Colors.AMBER_700)
            actualizar_saldo_cuenta()
        except (SaldoInsuficienteError, ValueError, TypeError) as ex:
            mostrar_notificacion(f"⚠️ Error retiro: {ex}", ft.Colors.RED_700)


    def aplicar_interes(e):
        if isinstance(estado["cuenta"], CuentaAhorro):
            saldo_anterior = estado["cuenta"].get_saldo()
            estado["cuenta"].aplicar_interes()
            interes_aplicado = estado["cuenta"].get_saldo() - saldo_anterior
            mostrar_notificacion(f" Interés aplicado (${interes_aplicado:.2f}).", ft.Colors.YELLOW_700)
            actualizar_saldo_cuenta()
        else: mostrar_notificacion(" Esta cuenta no admite la aplicación de intereses.", ft.Colors.RED_700)

    def realizar_compra(e):
        try:
            monto = float(txt_monto_tarjeta.value)
            estado["tarjeta"].realizar_compra(monto)
            mostrar_notificacion(f"Compra de ${monto:.2f} realizada.", ft.Colors.ORANGE_700)
            actualizar_saldo_tarjeta()
            actualizar_historial_tarjeta()
        except LimiteExcedidoError as ex: 
            mostrar_notificacion(f" Error Compra: {ex}", ft.Colors.RED_700)
        except ValueError as ex: 
            mostrar_notificacion(f" Error Compra: {ex}", ft.Colors.RED_700)

    def pagar_tarjeta(e):
        try:
            monto = float(txt_monto_tarjeta.value)
            estado["tarjeta"].pagar_tarjeta(monto)
            mostrar_notificacion(f" Pago de ${monto:.2f} realizado.", ft.Colors.GREEN_700)
            actualizar_saldo_tarjeta()
            actualizar_historial_tarjeta()
        except ValueError as ex: mostrar_notificacion(f" Error Pago: {ex}", ft.Colors.RED_700)

    # Asignar eventos
    dropdown_tipo_cuenta.on_change = lambda e: txt_interes.set_value(txt_interes.value) if e.control.value == "Ahorro" and txt_interes.visible == True else setattr(txt_interes, 'visible', e.control.value == "Ahorro")
    btn_depositar.on_click = depositar
    btn_retirar.on_click = retirar
    btn_aplicar_interes.on_click = aplicar_interes
    btn_comprar.on_click = realizar_compra
    btn_pagar.on_click = pagar_tarjeta
    btn_exportar_pdf.on_click = exportar_datos_a_pdf
    def update_operaciones_row_visibility(e=None):
        operaciones_row = page.controls[-1].content
        if estado["cuenta"]: 
            contenedor_operaciones_cuenta_final.visible = True
        if estado["tarjeta"]: 
            contenedor_operaciones_tarjeta_final.visible = True
        page.update()

    btn_crear_cuenta.on_click = lambda e: (crear_cuenta(e), update_operaciones_row_visibility(e))
    btn_crear_tarjeta.on_click = lambda e: (crear_tarjeta(e), update_operaciones_row_visibility(e))
    btn_registrar_cliente.on_click = registrar_cliente
    
    # ----------------- Estructura de la Interfaz -----------------

    cliente_container = ft.Container(
        content=ft.Column([ft.Text("1. Datos del Cliente", size=20, weight=ft.FontWeight.BOLD), txt_nombre, txt_apellido, txt_dni, btn_registrar_cliente], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
        padding=20, border_radius=10, width=350,
    )
    
    page.add(
        ft.Row(
            [
                
                # COLUMNA 1: Datos del Cliente (Formulario de Registro)
                ft.Column([cliente_container], spacing=30, alignment=ft.MainAxisAlignment.START), 
                ft.VerticalDivider(),
                
                # COLUMNA 2: Creación de Productos (Cuenta y Tarjeta)
                ft.Column([cuenta_form_container, tarjeta_form_container], spacing=30, alignment=ft.MainAxisAlignment.START),
                ft.VerticalDivider(),

                # COLUMNA 3: Gestión de Clientes (La nueva tarjeta de selección)
                gestion_clientes_container

            ],
            vertical_alignment=ft.CrossAxisAlignment.START, spacing=30
        ),
        ft.Container(
            content=ft.Row( 
                [
                    contenedor_operaciones_cuenta_final, 
                    ft.VerticalDivider(visible=False),
                    contenedor_operaciones_tarjeta_final, 
                ],
                spacing=30
            ),
            margin=ft.margin.only(top=30)
        ),   
            exportar_container
    )

if __name__ == "__main__":
    ft.app(target=main)