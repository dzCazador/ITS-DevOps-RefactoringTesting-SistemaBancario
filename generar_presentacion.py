"""Script para generar la presentacion PPTX del Sistema Bancario con diseno claro,
alto contraste, tipografia nitida e integracion de imagenes del proyecto.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def build_presentation(output_path="presentacion_sistema_bancario.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # Paleta luminosa, moderna y de alto contraste
    C_BG = RGBColor(248, 250, 252)          # #f8fafc Fondo general claro
    C_CARD = RGBColor(255, 255, 255)        # #ffffff Tarjetas blancas
    C_CARD_BORDER = RGBColor(226, 232, 240) # #e2e8f0 Borde suave
    C_TITLE = RGBColor(15, 23, 42)          # #0f172a Azul marino profundo (max contraste)
    C_TEXT = RGBColor(51, 65, 85)           # #334155 Texto de cuerpo legible
    C_MUTED = RGBColor(100, 116, 139)       # #64748b Texto secundario
    C_PURPLE = RGBColor(124, 58, 237)       # #7c3aed Violeta identidad
    C_EMERALD = RGBColor(5, 150, 105)       # #059669 Verde exito
    C_BLUE = RGBColor(2, 132, 199)          # #0284c7 Azul tecno
    C_AMBER = RGBColor(217, 119, 6)         # #d97706 Ambar advertencia
    C_RED = RGBColor(220, 38, 38)           # #dc2626 Rojo code smell

    def apply_bg(slide):
        bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = C_BG
        bg_shape.line.fill.background()

    def add_header(slide, title, category="SISTEMA BANCARIO"):
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(10.0), Inches(0.3))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        r_cat = p_cat.add_run()
        r_cat.text = category.upper()
        r_cat.font.name = "Arial"
        r_cat.font.size = Pt(11)
        r_cat.font.bold = True
        r_cat.font.color.rgb = C_PURPLE

        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(10.5), Inches(0.65))
        tf_t = t_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        r_t = p_t.add_run()
        r_t.text = title
        r_t.font.name = "Arial"
        r_t.font.size = Pt(24)
        r_t.font.bold = True
        r_t.font.color.rgb = C_TITLE

        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Inches(0.015))
        line.fill.solid()
        line.fill.fore_color.rgb = C_CARD_BORDER
        line.line.fill.background()

        if os.path.exists("img/logo_clean.png"):
            slide.shapes.add_picture("img/logo_clean.png", Inches(11.8), Inches(0.35), height=Inches(0.85))

    def add_card(slide, left, top, width, height, title, items, badge_text=None, border_color=C_CARD_BORDER, badge_color=C_PURPLE):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = C_CARD
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)

        top_bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, Inches(0.1))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = badge_color
        top_bar.line.fill.background()

        tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2), width - Inches(0.5), height - Inches(0.35))
        tf = tb.text_frame
        tf.word_wrap = True

        p0 = tf.paragraphs[0]
        if badge_text:
            r_badge = p0.add_run()
            r_badge.text = f"[{badge_text}] "
            r_badge.font.name = "Arial"
            r_badge.font.size = Pt(13)
            r_badge.font.bold = True
            r_badge.font.color.rgb = badge_color

        r_title = p0.add_run()
        r_title.text = title
        r_title.font.name = "Arial"
        r_title.font.size = Pt(15)
        r_title.font.bold = True
        r_title.font.color.rgb = C_TITLE
        p0.space_after = Pt(10)

        for item in items:
            p = tf.add_paragraph()
            p.space_after = Pt(6)
            if isinstance(item, tuple):
                r_bullet = p.add_run()
                r_bullet.text = "• "
                r_bullet.font.name = "Arial"
                r_bullet.font.size = Pt(11.5)
                r_bullet.font.bold = True
                r_bullet.font.color.rgb = badge_color

                r_label = p.add_run()
                r_label.text = f"{item[0]}: "
                r_label.font.name = "Arial"
                r_label.font.size = Pt(11.5)
                r_label.font.bold = True
                r_label.font.color.rgb = C_TITLE

                r_val = p.add_run()
                r_val.text = item[1]
                r_val.font.name = "Arial"
                r_val.font.size = Pt(11.5)
                r_val.font.bold = False
                r_val.font.color.rgb = C_TEXT
            else:
                r_plain = p.add_run()
                r_plain.text = f"• {item}"
                r_plain.font.name = "Arial"
                r_plain.font.size = Pt(11.5)
                r_plain.font.color.rgb = C_TEXT

    def add_code_comparison_card(slide, left, top, width, height, title, badge_text, badge_color, code_lines, bullets):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = C_CARD
        card.line.color.rgb = C_CARD_BORDER
        card.line.width = Pt(1.5)

        top_bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, Inches(0.08))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = badge_color
        top_bar.line.fill.background()

        tb_t = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.12), width - Inches(0.4), Inches(0.42))
        tf_t = tb_t.text_frame
        tf_t.word_wrap = True
        p0 = tf_t.paragraphs[0]
        r_badge = p0.add_run()
        r_badge.text = f"[{badge_text}] "
        r_badge.font.name = "Arial"
        r_badge.font.size = Pt(12)
        r_badge.font.bold = True
        r_badge.font.color.rgb = badge_color

        r_title = p0.add_run()
        r_title.text = title
        r_title.font.name = "Arial"
        r_title.font.size = Pt(13.5)
        r_title.font.bold = True
        r_title.font.color.rgb = C_TITLE

        c_h = Inches(3.2)
        c_top = top + Inches(0.6)
        code_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(0.2), c_top, width - Inches(0.4), c_h)
        code_bg.fill.solid()
        code_bg.fill.fore_color.rgb = RGBColor(241, 245, 249)  # #f1f5f9 light code panel
        code_bg.line.color.rgb = RGBColor(203, 213, 225)       # #cbd5e1 soft border
        code_bg.line.width = Pt(1.0)

        tb_code = slide.shapes.add_textbox(left + Inches(0.26), c_top + Inches(0.06), width - Inches(0.52), c_h - Inches(0.12))
        tf_code = tb_code.text_frame
        tf_code.word_wrap = True
        tf_code.margin_left = Inches(0.05)
        tf_code.margin_top = Inches(0.05)
        tf_code.margin_right = Inches(0.05)
        tf_code.margin_bottom = Inches(0.05)

        for i, line in enumerate(code_lines):
            p_line = tf_code.paragraphs[0] if i == 0 else tf_code.add_paragraph()
            r_line = p_line.add_run()
            r_line.text = line
            r_line.font.name = "Consolas"
            r_line.font.size = Pt(9.5)
            s_line = line.strip()
            if s_line.startswith("#"):
                r_line.font.color.rgb = RGBColor(100, 116, 139)  # #64748b comment
                r_line.font.italic = True
            elif any(s_line.startswith(kw) for kw in ["class ", "def ", "return ", "from ", "import ", "if ", "for ", "in ", "yield ", "with "]):
                r_line.font.color.rgb = RGBColor(2, 132, 199)    # #0284c7 keyword
            elif any(c in line for c in ["True", "False", "None", "@classmethod", "DatabaseConnection", "CuentaFactory", "EmpleadoBuilder"]):
                r_line.font.color.rgb = RGBColor(124, 58, 237)   # #7c3aed special
            else:
                r_line.font.color.rgb = RGBColor(15, 23, 42)     # #0f172a body code

        b_top = c_top + c_h + Inches(0.1)
        b_h = height - (c_top - top + c_h + Inches(0.15))
        tb_b = slide.shapes.add_textbox(left + Inches(0.2), b_top, width - Inches(0.4), b_h)
        tf_b = tb_b.text_frame
        tf_b.word_wrap = True

        for j, bullet in enumerate(bullets):
            pb = tf_b.paragraphs[0] if j == 0 else tf_b.add_paragraph()
            pb.space_after = Pt(3)
            if isinstance(bullet, tuple):
                rb_dot = pb.add_run()
                rb_dot.text = "• "
                rb_dot.font.name = "Arial"
                rb_dot.font.size = Pt(11)
                rb_dot.font.bold = True
                rb_dot.font.color.rgb = badge_color

                rb_lbl = pb.add_run()
                rb_lbl.text = f"{bullet[0]}: "
                rb_lbl.font.name = "Arial"
                rb_lbl.font.size = Pt(11)
                rb_lbl.font.bold = True
                rb_lbl.font.color.rgb = C_TITLE

                rb_txt = pb.add_run()
                rb_txt.text = bullet[1]
                rb_txt.font.name = "Arial"
                rb_txt.font.size = Pt(11)
                rb_txt.font.color.rgb = C_TEXT
            else:
                rb_p = pb.add_run()
                rb_p.text = f"• {bullet}"
                rb_p.font.name = "Arial"
                rb_p.font.size = Pt(11)
                rb_p.font.color.rgb = C_TEXT

    # SLIDE 1: PORTADA
    s1 = prs.slides.add_slide(blank_layout)
    apply_bg(s1)

    cover_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9))
    cover_box.fill.solid()
    cover_box.fill.fore_color.rgb = C_CARD
    cover_box.line.color.rgb = C_CARD_BORDER
    cover_box.line.width = Pt(1.5)

    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(0.2), Inches(5.9))
    bar.fill.solid()
    bar.fill.fore_color.rgb = C_PURPLE
    bar.line.fill.background()

    tb_c = s1.shapes.add_textbox(Inches(1.4), Inches(1.2), Inches(7.5), Inches(5.0))
    tf1 = tb_c.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    r0 = p0.add_run()
    r0.text = "PROYECTO INTEGRADOR • REFACTORING, TESTING & CI/CD"
    r0.font.name = "Arial"
    r0.font.size = Pt(12)
    r0.font.bold = True
    r0.font.color.rgb = C_PURPLE
    p0.space_after = Pt(14)

    p1 = tf1.add_paragraph()
    r1 = p1.add_run()
    r1.text = "Sistema Bancario"
    r1.font.name = "Arial"
    r1.font.size = Pt(36)
    r1.font.bold = True
    r1.font.color.rgb = C_TITLE
    p1.space_after = Pt(8)

    p2 = tf1.add_paragraph()
    r2 = p2.add_run()
    r2.text = "Refactorización con Patrones de Diseño (GoF) y Dockerización Web"
    r2.font.name = "Arial"
    r2.font.size = Pt(20)
    r2.font.bold = True
    r2.font.color.rgb = C_BLUE
    p2.space_after = Pt(18)

    p3 = tf1.add_paragraph()
    r3 = p3.add_run()
    r3.text = "Implementación de patrones creacionales (Singleton, Factory Method, Builder), cumplimiento riguroso de principios SOLID, automatización de pruebas unitarias y despliegue web aislado en contenedores Docker."
    r3.font.name = "Arial"
    r3.font.size = Pt(13)
    r3.font.color.rgb = C_TEXT
    p3.space_after = Pt(24)

    p4 = tf1.add_paragraph()
    badges = [
        ("✅ 59 Tests Automatizados", C_EMERALD),
        ("  |  🐳 Docker Compose Web", C_BLUE),
        ("  |  🏛️ SOLID & Clean Architecture", C_PURPLE)
    ]
    for b_text, b_col in badges:
        rb = p4.add_run()
        rb.text = b_text
        rb.font.name = "Arial"
        rb.font.size = Pt(13)
        rb.font.bold = True
        rb.font.color.rgb = b_col

    if os.path.exists("img/logo_clean.png"):
        s1.shapes.add_picture("img/logo_clean.png", Inches(9.4), Inches(1.3), height=Inches(3.3))
    if os.path.exists("img/its.png"):
        s1.shapes.add_picture("img/its.png", Inches(9.6), Inches(5.0), width=Inches(2.2))

    # SLIDE 2: OBJETIVOS
    s2 = prs.slides.add_slide(blank_layout)
    apply_bg(s2)
    add_header(s2, "Objetivos del Proyecto: Evolución y Calidad Integral")

    card_w = Inches(3.64)
    h_top = Inches(1.6)
    h_len = Inches(5.4)

    add_card(s2, Inches(0.8), h_top, card_w, h_len, "1. Refactorización & SOLID", [
        ("Diagnóstico", "Detectar code smells, acoplamiento excesivo y duplicación en vistas."),
        ("Patrones GoF", "Implementar Singleton (BD), Factory Method (Cuentas) y Builder (Personas)."),
        ("Principios", "Asegurar SRP, OCP, LSP, ISP y DIP en todas las capas del software."),
        ("Meta", "Código extensible, mantenible y legible según estándares limpios.")
    ], badge_text="DISEÑO", border_color=C_PURPLE, badge_color=C_PURPLE)

    add_card(s2, Inches(4.84), h_top, card_w, h_len, "2. Testing Automatizado", [
        ("Base Existente", "44 tests unitarios y de integración de persistencia y dominio."),
        ("Nuevos Tests", "15 casos de prueba unitarios para verificar patrones de diseño."),
        ("Total Verificado", "59 tests pasando al 100% (3 skipped documentados)."),
        ("Garantía", "Cero regresiones: el comportamiento del negocio se mantiene intacto.")
    ], badge_text="CALIDAD", border_color=C_BLUE, badge_color=C_BLUE)

    add_card(s2, Inches(8.88), h_top, card_w, h_len, "3. Dockerización & DevOps", [
        ("Portabilidad", "Empaquetar la aplicación Flet Web y SQLite en un contenedor aislado."),
        ("Reproducibilidad", "Eliminar el problema 'en mi máquina funciona' para siempre."),
        ("Orquestación", "Despliegue con 1 comando vía Docker Compose (App + Tests)."),
        ("Persistencia", "Garantizar persistencia física de la base de datos bancaria.")
    ], badge_text="DEVOPS", border_color=C_EMERALD, badge_color=C_EMERALD)

    if os.path.exists("img/logo_DevOps.jpg"):
        s2.shapes.add_picture("img/logo_DevOps.jpg", Inches(11.2), Inches(5.6), width=Inches(1.0))

    # SLIDE 3: DIAGNOSTICO CODE SMELLS
    s3 = prs.slides.add_slide(blank_layout)
    apply_bg(s3)
    add_header(s3, "Diagnóstico Inicial: Olores de Código Identificados", "REFACTORIZACIÓN")

    w_half = Inches(5.66)
    add_card(s3, Inches(0.8), Inches(1.6), w_half, Inches(5.4), "Code Smells Detectados (Antes)", [
        ("Múltiples Conexiones BD", "Cada vista instanciaba su propio DAO('sistema_bancario.db'), creando hasta 6 engines de SQLAlchemy independientes."),
        ("Lógica Dispersa de Cuentas", "Decisiones tipo 'isinstance(cuenta, CuentaAhorro)' y 'if ahorro in nombre' replicadas en 4 vistas distintas."),
        ("Constructor Telescópico", "Clase Empleado con 10 parámetros obligatorios/posicionales, haciéndolo ilegible y muy frágil ante cambios."),
        ("Duplicación en Presentación", "Funciones _formatear_monto() y SnackBar de feedback repetidas idénticamente en varias vistas."),
        ("Inconsistencia Visual", "Paleta de colores hardcodeada con valores hexadecimales dispersos y dispares.")
    ], badge_text="DEUDA TÉCNICA", border_color=C_AMBER, badge_color=C_AMBER)

    add_card(s3, Inches(6.86), Inches(1.6), w_half, Inches(5.4), "Impacto y Principios Violados", [
        ("Violación DRY", "Duplicación masiva de lógica en vistas, acceso a datos y componentes de UI."),
        ("Violación OCP", "Agregar un nuevo tipo de cuenta obligaba a modificar código fuente en múltiples módulos."),
        ("Violación SRP", "Las vistas eran responsables de formatear datos, conectar con la BD y renderizar la interfaz."),
        ("Riesgo Concurrencia SQLite", "Tener 6 pools de conexiones compitiendo sobre un archivo SQLite local podía generar bloqueos 'database is locked'."),
        ("Estrategia de Solución", "Aplicar patrones creacionales formales y centralizar fuentes de verdad.")
    ], badge_text="IMPACTO", border_color=C_PURPLE, badge_color=C_PURPLE)

    # SLIDE 4: PATRON SINGLETON
    s4 = prs.slides.add_slide(blank_layout)
    apply_bg(s4)
    add_header(s4, "Patrón Singleton: Conexión Única a Base de Datos", "PATRONES DE DISEÑO")

    code_s4_antes = [
        "# ANTES: Cada vista creaba su propia instancia",
        "# src/vistas/login.py",
        "_dao = DAO('sistema_bancario.db')          # engine #1",
        "",
        "# src/vistas/home_personal.py",
        "_dao = DAOPersonal('sistema_bancario.db')  # engine #2",
        "",
        "# src/vistas/home_operaciones.py",
        "_dao = DAOCliente('sistema_bancario.db')   # engine #3",
        "# ... hasta 6 engines compitiendo por SQLite!"
    ]
    bullets_s4_antes = [
        ("Problema", "Múltiples pools compitiendo sobre el mismo archivo SQLite."),
        ("Riesgo", "Bloqueos concurrentes 'database is locked' y gasto de memoria.")
    ]
    add_code_comparison_card(s4, Inches(0.8), Inches(1.55), w_half, Inches(5.5),
                             "Dispersión de Conexiones", "ANTES", C_RED,
                             code_s4_antes, bullets_s4_antes)

    code_s4_despues = [
        "# DESPUES: Singleton en src/database.py",
        "class DatabaseConnection:",
        "    _instances: dict[str, 'DatabaseConnection'] = {}",
        "    @classmethod",
        "    def instance(cls, db_path='sistema_bancario.db'):",
        "        if db_path not in cls._instances:",
        "            cls._instances[db_path] = cls(db_path)",
        "        return cls._instances[db_path]",
        "",
        "# src/app_context.py (compartido por todas las vistas)",
        "dao = DAO(DB_PATH)  # engine único y reutilizado!"
    ]
    bullets_s4_despues = [
        ("Solución", "Un único Engine físico por ruta y PRAGMA foreign_keys=ON."),
        ("Testing", "DatabaseConnection.reset() permite aislar BD en memoria (:memory:).")
    ]
    add_code_comparison_card(s4, Inches(6.86), Inches(1.55), w_half, Inches(5.5),
                             "DatabaseConnection Singleton", "DESPUÉS", C_EMERALD,
                             code_s4_despues, bullets_s4_despues)

    # SLIDE 5: PATRON FACTORY METHOD
    s5 = prs.slides.add_slide(blank_layout)
    apply_bg(s5)
    add_header(s5, "Patrón Factory Method: Creación Polimórfica de Cuentas", "PATRONES DE DISEÑO")

    code_s5_antes = [
        "# ANTES: Lógica de creación dispersa en vistas",
        "# src/vistas/home_cliente.py",
        "def _nombre_tipo(cuenta):",
        "    if isinstance(cuenta, CuentaAhorro): return 'Caja de Ahorro'",
        "    if isinstance(cuenta, Cuenta): return 'Corriente'",
        "",
        "# src/vistas/home_operaciones.py",
        "if etiqueta == 'Ahorro' and 'ahorro' in nombre_tipo.lower(): ...",
        "",
        "# src/autenticacion.py (BUG: perdía aplicar_interes)",
        "return [Cuenta.from_db_row(fila, c) for fila in filas]"
    ]
    bullets_s5_antes = [
        ("Violación OCP", "Agregar un tipo de cuenta obligaba a tocar múltiples vistas."),
        ("Bug Latente", "Las cuentas de ahorro se degradaban a Cuenta base en el login.")
    ]
    add_code_comparison_card(s5, Inches(0.8), Inches(1.55), w_half, Inches(5.5),
                             "Lógica Dispersa y Pérdida de Subclase", "ANTES", C_RED,
                             code_s5_antes, bullets_s5_antes)

    code_s5_despues = [
        "# DESPUES: Fábrica extensible en src/modelos/cuenta_factory.py",
        "class CuentaFactory:",
        "    _creadores = {}",
        "    @classmethod",
        "    def registrar(cls, tipo, creador):",
        "        cls._creadores[cls._normalizar(tipo)] = creador",
        "",
        "    @classmethod",
        "    def crear_desde_fila(cls, fila, cliente, tipo_nombre):",
        "        ...",
        "# Extensión pura sin tocar la fábrica ni vistas (OCP):",
        "CuentaFactory.registrar('PlazoFijo', _crear_plazo_fijo)"
    ]
    bullets_s5_despues = [
        ("Cumplimiento OCP", "Nuevos tipos de cuenta se registran dinámicamente."),
        ("Corrección", "Se reconstruye la instancia fidedigna con aplicar_interes().")
    ]
    add_code_comparison_card(s5, Inches(6.86), Inches(1.55), w_half, Inches(5.5),
                             "CuentaFactory Extensible (OCP)", "DESPUÉS", C_EMERALD,
                             code_s5_despues, bullets_s5_despues)

    # SLIDE 6: PATRON BUILDER
    s6 = prs.slides.add_slide(blank_layout)
    apply_bg(s6)
    add_header(s6, "Patrón Builder: Construcción Fluida de Entidades", "PATRONES DE DISEÑO")

    code_s6_antes = [
        "# ANTES: Constructor Telescópico (10 Parámetros)",
        "# empleado.py y tests",
        "empleado = Empleado(",
        "    'Luis', 'Pérez', '23456789', 'ClaveSegura3',",
        "    legajo='E-1001',",
        "    cargo='Analista',",
        "    departamento='Sistemas',",
        "    fecha_ingreso=datetime(2024, 1, 15),",
        "    salario=85000,",
        "    sucursal='Central'",
        ")",
        "# -> Difícil de leer, propenso a errores de orden"
    ]
    bullets_s6_antes = [
        ("Antipatrón", "Constructor telescópico con alta carga cognitiva."),
        ("Fragilidad", "Cualquier nuevo atributo rompe tests y llamadas existentes.")
    ]
    add_code_comparison_card(s6, Inches(0.8), Inches(1.55), w_half, Inches(5.5),
                             "Constructor Telescópico Rígido", "ANTES", C_RED,
                             code_s6_antes, bullets_s6_antes)

    code_s6_despues = [
        "# DESPUES: Fluent Interface en src/modelos/persona_builder.py",
        "empleado = (",
        "    EmpleadoBuilder()",
        "    .con_nombre('Luis')",
        "    .con_apellido('Pérez')",
        "    .con_dni('23456789')",
        "    .con_password('ClaveSegura3')",
        "    .con_legajo('E-1001')",
        "    .con_cargo('Analista')",
        "    .con_departamento('Sistemas')",
        "    .con_salario(85000)",
        "    .build()  # Ejecuta validaciones de dominio!",
        ")"
    ]
    bullets_s6_despues = [
        ("Claridad Total", "Construcción expresiva, autodocumentada y modular."),
        ("Invariante", "El método .build() delega en el constructor real de dominio.")
    ]
    add_code_comparison_card(s6, Inches(6.86), Inches(1.55), w_half, Inches(5.5),
                             "EmpleadoBuilder Fluent API", "DESPUÉS", C_EMERALD,
                             code_s6_despues, bullets_s6_despues)

    # SLIDE 7: PRINCIPIO DRY Y CAPA UI (CODIGO ANTES VS DESPUES)
    s7 = prs.slides.add_slide(blank_layout)
    apply_bg(s7)
    add_header(s7, "Principio DRY y Centralización de UI", "REFACTORIZACIÓN")

    code_s7_antes = [
        "# ANTES: Copiado idéntico en 3 vistas de presentación",
        "# home_cliente.py, home_operaciones.py, home_historial.py",
        "def _formatear_monto(monto):",
        "    valor = f'{monto:,.2f}'",
        "    return '$ ' + valor.replace('.', 'X').replace(',', '.').replace('X', ',')",
        "",
        "# Notificaciones duplicadas con colores hardcodeados:",
        "# login.py, home_operaciones.py, etc.",
        "page.snack_bar = ft.SnackBar(",
        "    ft.Text(texto),",
        "    bgcolor='red' if es_error else 'green'",
        ")"
    ]
    bullets_s7_antes = [
        ("Violación DRY", "Lógica idéntica duplicada en múltiples módulos de interfaz."),
        ("Inconsistencia", "Cero coherencia cromática con colores hexadecimales mágicos.")
    ]
    add_code_comparison_card(s7, Inches(0.8), Inches(1.55), w_half, Inches(5.5),
                             "Duplicación en Vistas Flet", "ANTES", C_RED,
                             code_s7_antes, bullets_s7_antes)

    code_s7_despues = [
        "# DESPUES: Fuente de verdad única en src/vistas/ui_utils.py",
        "class Colores:",
        "    FONDO = '#0a0a0f'; VIOLETA = '#8b2fc9'",
        "    VERDE = '#16a34a'; ROJO = '#dc2626'",
        "",
        "def formatear_monto(monto: float) -> str: ...",
        "def mostrar_notificacion(page, texto, es_error=False): ...",
        "",
        "# En las vistas (home_cliente.py, etc.):",
        "from src.vistas.ui_utils import Colores, formatear_monto, mostrar_notificacion"
    ]
    bullets_s7_despues = [
        ("Fuente de Verdad", "Cambiar el formato o paleta requiere editar 1 solo archivo."),
        ("Desacoplamiento", "Vistas enfocadas exclusivamente en la presentación visual.")
    ]
    add_code_comparison_card(s7, Inches(6.86), Inches(1.55), w_half, Inches(5.5),
                             "Centralización en ui_utils.py", "DESPUÉS", C_EMERALD,
                             code_s7_despues, bullets_s7_despues)

    # SLIDE 8: ARQUITECTURA DE PATRONES (DIAGRAMA)
    s8 = prs.slides.add_slide(blank_layout)
    apply_bg(s8)
    add_header(s8, "Arquitectura de Patrones de Diseño Implementados", "PATRONES GoF")

    if os.path.exists("img/patrones_architecture.png"):
        s8.shapes.add_picture("img/patrones_architecture.png", Inches(0.8), Inches(1.55), width=Inches(11.733))

    # SLIDE 9: DOCKERIZACION Y RETO WEB FLET
    s9 = prs.slides.add_slide(blank_layout)
    apply_bg(s9)
    add_header(s9, "Dockerización: De Aplicación Desktop a Web Container", "DEVOPS")

    add_card(s9, Inches(0.8), Inches(1.6), Inches(5.5), Inches(5.4), "El Desafío Técnico de Flet en Docker", [
        ("Comportamiento Nativo", "Flet está diseñado para abrir clientes GUI de Flutter Desktop en el sistema operativo anfitrión."),
        ("Problema en Docker", "En contenedores Linux headless (sin pantalla ni X11), la ejecución de escritorio falla de inmediato."),
        ("Solución Implementada", "Convertir la aplicación en un servidor web ASGI completo basado en FastAPI y Uvicorn."),
        ("Dependencia Clave", "Se agregó flet-web==0.28.3 en requirements.txt para incluir los assets compilados de Flutter Web."),
        ("Variables de Red", "FLET_FORCE_WEB_SERVER=true y FLET_SERVER_IP=0.0.0.0 permiten escuchar en todas las interfaces del contenedor.")
    ], badge_text="DESAFÍO Y SOLUCIÓN", border_color=C_AMBER, badge_color=C_AMBER)

    if os.path.exists("img/docker_architecture.png"):
        s9.shapes.add_picture("img/docker_architecture.png", Inches(6.6), Inches(1.6), width=Inches(5.933))

    # SLIDE 10: DOCKER: ADAPTACION DE CODIGO (ANTES VS DESPUES)
    s10 = prs.slides.add_slide(blank_layout)
    apply_bg(s10)
    add_header(s10, "Dockerización: Adaptación de Código y Despliegue", "DOCKER & CI/CD")

    code_s10_antes = [
        "# ANTES: main.py rígido y despliegue manual",
        "def main(page: ft.Page):",
        "    render_login(page)",
        "",
        "if __name__ == '__main__':",
        "    ft.app(target=main, view=ft.WEB_BROWSER)",
        "",
        "# Proceso de arranque previo (5 pasos en host):",
        "# 1. python -m venv venv",
        "# 2. .\\venv\\Scripts\\Activate.ps1",
        "# 3. pip install -r requirements.txt",
        "# 4. Error en Linux headless: falta entorno gráfico X11",
        "# 5. python main.py"
    ]
    bullets_s10_antes = [
        ("Fricción", "Requiere instalar runtime de Python y dependencias en cada máquina."),
        ("Incompatibilidad", "Falla en servidores Linux sin entorno gráfico de escritorio.")
    ]
    add_code_comparison_card(s10, Inches(0.8), Inches(1.55), w_half, Inches(5.5),
                             "Ejecución Manual Dependiente del Host", "ANTES", C_RED,
                             code_s10_antes, bullets_s10_antes)

    code_s10_despues = [
        "# DESPUES: main.py dinámico con variables de entorno",
        "if __name__ == '__main__':",
        "    host = os.getenv('FLET_SERVER_IP')",
        "    port = int(os.getenv('FLET_SERVER_PORT', '0'))",
        "    kwargs = {'target': main, 'view': ft.WEB_BROWSER}",
        "    if host: kwargs['host'] = host",
        "    if port: kwargs['port'] = port",
        "    ft.app(**kwargs)",
        "",
        "# Despliegue Docker (1 solo comando!):",
        "$ docker compose up --build -d",
        "# -> Corre en http://localhost:8550 sin instalar Python!"
    ]
    bullets_s10_despues = [
        ("Portabilidad 100%", "Cero instalación de Python o SQLite en la máquina local."),
        ("Modo Dual", "Funciona tanto en Docker como en desarrollo local de Windows.")
    ]
    add_code_comparison_card(s10, Inches(6.86), Inches(1.55), w_half, Inches(5.5),
                             "Arranque Dinámico en Contenedor Web", "DESPUÉS", C_EMERALD,
                             code_s10_despues, bullets_s10_despues)

    # SLIDE 11: DOCKER COMPOSE Y PERSISTENCIA
    s11 = prs.slides.add_slide(blank_layout)
    apply_bg(s11)
    add_header(s11, "Orquestación con Docker Compose y Persistencia", "DOCKER COMPOSE")

    add_card(s11, Inches(0.8), Inches(1.6), w_half, Inches(5.4), "Servicios Declarados", [
        ("Servicio banco-app", "Levanta la interfaz web bancaria en el puerto 8550:8550. Listo para producción local."),
        ("Servicio test (Profile test)", "Ejecuta pytest -v dentro del contenedor idéntico al de producción sin interferir con la app web."),
        ("Archivo .env.example", "Documenta variables FLET_SERVER_IP, FLET_SERVER_PORT, FLET_FORCE_WEB_SERVER y DB_PATH."),
        ("Comando Unificado", "docker compose up --build -d compila y levanta la infraestructura en segundos.")
    ], badge_text="SERVICIOS", border_color=C_PURPLE, badge_color=C_PURPLE)

    add_card(s11, Inches(6.86), Inches(1.6), w_half, Inches(5.4), "Persistencia de Datos (Bind Mount)", [
        ("Configuración", "volumes: - ./sistema_bancario.db:/app/sistema_bancario.db"),
        ("Mecanismo", "Mapea directamente el archivo SQLite de la máquina anfitriona dentro del contenedor."),
        ("Ventaja Clave", "Las altas de clientes, depósitos y transferencias persisten aunque el contenedor sea destruido y recreado."),
        ("Facilidad de Backup", "Basta con respaldar el archivo local para tener una copia de seguridad íntegra de la base.")
    ], badge_text="DATOS PERSISTENTES", border_color=C_EMERALD, badge_color=C_EMERALD)

    # SLIDE 12: SUITE DE PRUEBAS AUTOMATIZADAS
    s12 = prs.slides.add_slide(blank_layout)
    apply_bg(s12)
    add_header(s12, "Calidad Garantizada: Suite de Pruebas Automatizadas", "TESTING")

    add_card(s12, Inches(0.8), Inches(1.6), w_half, Inches(5.4), "Métricas de Testing (Pytest)", [
        ("Total de Tests", "59 pruebas automatizadas ejecutadas y aprobadas al 100%."),
        ("Tests de Dominio y Persistencia", "44 tests originales intactos (autenticación, cuentas, clientes, transacciones, etc.)."),
        ("Nuevos Tests de Patrones (15)", "test_patrones.py cubre específicamente la refactorización realizada."),
        ("Tests Omitidos (3 skipped)", "Casos especiales de propuesta a la espera de merges externos."),
        ("Tiempo de Ejecución", "~5.2 segundos en suite completa.")
    ], badge_text="RESULTADOS", border_color=C_EMERALD, badge_color=C_EMERALD)

    add_card(s12, Inches(6.86), Inches(1.6), w_half, Inches(5.4), "Desglose de Tests de Patrones", [
        ("TestSingleton (3 tests)", "Verifica instancia única por ruta, engine compartido entre DAOs y reset() para aislamiento."),
        ("TestCuentaFactory (7 tests)", "Verifica creación correcta por subclase, case-insensitivity, error en tipo inválido, reconstrucción desde BD y extensibilidad OCP."),
        ("TestBuilders (5 tests)", "Verifica construcción de Persona, Cliente y Empleado; comprueba que no se salteen validaciones de dominio.")
    ], badge_text="PATRONES CUBIERTOS", border_color=C_BLUE, badge_color=C_BLUE)

    # SLIDE 13: GUION DE DEMO EN VIVO CON SCREENSHOT
    s13 = prs.slides.add_slide(blank_layout)
    apply_bg(s13)
    add_header(s13, "Guion para la Demostración en Vivo", "DEMO EN VIVO")

    add_card(s13, Inches(0.8), Inches(1.6), Inches(5.8), Inches(5.4), "Paso a Paso en la Terminal", [
        ("1. Levantar la App", "docker compose up --build -d (Compilación de capas e inicio en segundo plano)."),
        ("2. Verificar Salud", "docker compose ps (Mostrar estado 'healthy' y puerto 8550 expuesto)."),
        ("3. Ver Logs del Servidor", "docker compose logs banco-app (Mostrar arranque limpio de Flet y Uvicorn)."),
        ("4. Navegación Web", "Abrir http://localhost:8550 en el navegador. Login Personal: DNI 22233344 | Clave: admin."),
        ("5. Probar Persistencia", "docker compose down y docker compose up -d. Los saldos y transacciones persisten intactos."),
        ("6. Correr Tests en Contenedor", "docker compose run --rm banco-app pytest -v (59 tests pasando en verde dentro de Docker).")
    ], badge_text="TERMINAL Y DEMO", border_color=C_PURPLE, badge_color=C_PURPLE)

    if os.path.exists("img/historial.jpeg"):
        img_box2 = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.6), Inches(5.633), Inches(5.4))
        img_box2.fill.solid()
        img_box2.fill.fore_color.rgb = C_CARD
        img_box2.line.color.rgb = C_CARD_BORDER
        img_box2.line.width = Pt(1.5)

        tb_img2 = s13.shapes.add_textbox(Inches(7.1), Inches(1.7), Inches(5.2), Inches(0.4))
        p_it2 = tb_img2.text_frame.paragraphs[0]
        r_it2 = p_it2.add_run()
        r_it2.text = "📊 Historial y Operaciones en Tiempo Real"
        r_it2.font.name = "Arial"
        r_it2.font.size = Pt(13)
        r_it2.font.bold = True
        r_it2.font.color.rgb = C_TITLE

        s13.shapes.add_picture("img/historial.jpeg", Inches(7.1), Inches(2.2), width=Inches(5.233))

    # SLIDE MVC 1: MODELO, VISTA Y CONTROLADOR (CAPAS)
    s_mvc1 = prs.slides.add_slide(blank_layout)
    apply_bg(s_mvc1)
    add_header(s_mvc1, "Separación MVC: Modelo, Vista y Controlador", "ARQUITECTURA MVC")

    add_card(s_mvc1, Inches(0.8), h_top, card_w, h_len, "Modelo", [
        ("Qué es", "Dominio y persistencia. No conoce la interfaz Flet."),
        ("Dominio", "cliente.py, cuenta.py, cuenta_ahorro.py, persona.py, empleado.py, transaccion.py."),
        ("Persistencia", "dao*.py, models.py y database.py (Singleton de conexión)."),
        ("Inyección", "Los DAO se comparten vía app_context.py.")
    ], badge_text="MODELO", border_color=C_BLUE, badge_color=C_BLUE)

    add_card(s_mvc1, Inches(4.84), h_top, card_w, h_len, "Vista", [
        ("Qué es", "Renderiza la interfaz Flet y delega cada acción al controlador."),
        ("Archivos", "login.py, home_*.py, vista_gestion_clientes.py, navegacion.py, ui_utils.py."),
        ("Regla", "Sin imports de dao, models ni connect()."),
        ("Feedback", "Muestra mensajes y SnackBar con ui_utils.mostrar_notificacion.")
    ], badge_text="VISTA", border_color=C_EMERALD, badge_color=C_EMERALD)

    add_card(s_mvc1, Inches(8.88), h_top, card_w, h_len, "Controlador", [
        ("Qué es", "Casos de uso: valida la entrada y coordina modelo y persistencia."),
        ("Archivos", "src/controladores/: auth, cliente, operacion e historial."),
        ("Inyección", "Recibe el DAO por constructor, no lo instancia."),
        ("Errores", "Convierte excepciones de dominio en errores que la vista presenta.")
    ], badge_text="CONTROLADOR", border_color=C_PURPLE, badge_color=C_PURPLE)

    # SLIDE MVC 2: ANTES VS DESPUES (CONTROLADOR INEXISTENTE -> src/controladores)
    s_mvc2 = prs.slides.add_slide(blank_layout)
    apply_bg(s_mvc2)
    add_header(s_mvc2, "MVC: Antes sin Controlador y Después con src/controladores", "ARQUITECTURA MVC")

    code_mvc2_antes = [
        "# ANTES: sin controlador, la vista usaba el ORM",
        "# src/vistas/home_operaciones.py",
        "from src.modelos.models import TipoCuentaModel",
        "conn = connect()  # acceso directo a SQLite",
        "# Validación de monto y reglas de cuenta en la vista",
        "# Notificación llamada sin el argumento page"
    ]
    bullets_mvc2_antes = [
        ("Problema", "La vista mezclaba UI, reglas de negocio y persistencia."),
        ("Bug", "_mostrar_notificacion se llamaba sin page: fallo en ejecución.")
    ]
    add_code_comparison_card(s_mvc2, Inches(0.8), Inches(1.55), w_half, Inches(5.5),
                             "Vista con ORM directo", "ANTES", C_RED,
                             code_mvc2_antes, bullets_mvc2_antes)

    code_mvc2_despues = [
        "# DESPUÉS: la vista solo delega",
        "# src/app_context.py",
        "operacion_controller = OperacionController(dao_cliente)",
        "# src/vistas/home_operaciones.py",
        "resultado = _operaciones.ejecutar_operacion(",
        "    cuentas, etiqueta, tipo, texto_monto)",
        "# src/controladores/operacion_controller.py",
        "monto = self.parsear_monto(texto_monto)",
        "saldo = self._dao.depositar(cuenta, monto)"
    ]
    bullets_mvc2_despues = [
        ("Separación", "Vistas sin imports de dao, models ni connect()."),
        ("Testing", "tests/test_controladores.py cubre los casos de uso.")
    ]
    add_code_comparison_card(s_mvc2, Inches(6.86), Inches(1.55), w_half, Inches(5.5),
                             "OperacionController con DAO inyectado", "DESPUÉS", C_EMERALD,
                             code_mvc2_despues, bullets_mvc2_despues)

    # SLIDE MVC 3: FLUJO DE UN DEPOSITO Y ESTADO DE VERIFICACION
    s_mvc3 = prs.slides.add_slide(blank_layout)
    apply_bg(s_mvc3)
    add_header(s_mvc3, "MVC en Acción: Flujo de un Depósito y Verificación", "ARQUITECTURA MVC")

    add_card(s_mvc3, Inches(0.8), Inches(1.6), w_half, Inches(5.4), "Flujo de un Depósito", [
        ("1. Vista", "home_operaciones.py captura el monto y la cuenta seleccionada."),
        ("2. Controlador", "OperacionController.ejecutar_operacion() valida y elige la cuenta."),
        ("3. DAO", "dao.depositar(cuenta, monto) persiste el nuevo saldo."),
        ("4. SQLite", "Un único Engine compartido vía DatabaseConnection (Singleton)."),
        ("5. Respuesta", "ResultadoOperacion vuelve a la vista para notificar al usuario.")
    ], badge_text="FLUJO", border_color=C_PURPLE, badge_color=C_PURPLE)

    add_card(s_mvc3, Inches(6.86), Inches(1.6), w_half, Inches(5.4), "Verificación y Límites", [
        ("Tests", "82 passed, 3 skipped (pytest tests/ -q)."),
        ("Comportamiento", "Sin cambios observables; las suites previas siguen en verde."),
        ("Límite", "La UI no se probó en Flet real; sólo smoke de render de las vistas."),
        ("Pendiente", "La etiqueta de tipo de cuenta en home_personal depende aún del texto del número de cuenta.")
    ], badge_text="ESTADO", border_color=C_AMBER, badge_color=C_AMBER)

    # SLIDE 14: CONCLUSIONES Y VALOR AGREGADO
    s14 = prs.slides.add_slide(blank_layout)
    apply_bg(s14)
    add_header(s14, "Conclusiones y Valor Agregado del Proyecto", "CONCLUSIÓN")

    add_card(s14, Inches(0.8), h_top, card_w, h_len, "Arquitectura Limpia", [
        ("Desacoplamiento", "Vistas de presentación libres de responsabilidades de persistencia."),
        ("Extensibilidad", "Fábrica abierta a nuevos tipos sin tocar código existente."),
        ("Mantenibilidad", "Cero duplicación de código gracias a patrones y DRY.")
    ], badge_text="CÓDIGO LIMPIO", border_color=C_PURPLE, badge_color=C_PURPLE)

    add_card(s14, Inches(4.84), h_top, card_w, h_len, "DevOps & Portabilidad", [
        ("Onboarding 1-Paso", "Cualquier miembro del equipo clona y corre en 2 minutos."),
        ("Sin Dependencias", "No requiere instalar Python, SQLite ni Flet en la máquina local."),
        ("Paridad Total", "Mismo comportamiento en desarrollo, CI/CD y producción.")
    ], badge_text="DEVOPS", border_color=C_EMERALD, badge_color=C_EMERALD)

    add_card(s14, Inches(8.88), h_top, card_w, h_len, "Listo para la Nube", [
        ("Estándar OCI", "Imagen Docker estándar lista para desplegarse en la nube."),
        ("Compatibilidad Cloud", "Compatible con AWS ECS, Azure Container Apps y Google Cloud Run."),
        ("Seguridad", "Usuario no-root y healthchecks integrados desde el diseño.")
    ], badge_text="CLOUD READY", border_color=C_BLUE, badge_color=C_BLUE)

    try:
        prs.save(output_path)
        print(f"Presentacion regenerada exitosamente en {output_path}")
    except PermissionError:
        alt_path = "presentacion_sistema_bancario_actualizada.pptx"
        prs.save(alt_path)
        print(f"El archivo original estaba abierto. Presentacion guardada en {alt_path}")

if __name__ == "__main__":
    build_presentation()
