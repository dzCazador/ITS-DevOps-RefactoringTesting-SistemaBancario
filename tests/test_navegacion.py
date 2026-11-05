from src.vistas.navegacion import nombre_cuenta_para_header


def test_nombre_cuenta_para_header_usa_mercado_pago():
    assert nombre_cuenta_para_header("Corriente") == "Mercado Pago"
    assert nombre_cuenta_para_header("Caja de ahorro") == "Mercado Pago"
    assert nombre_cuenta_para_header("Mercado Pago") == "Mercado Pago"
    assert nombre_cuenta_para_header("Empresa") == "Empresa"
