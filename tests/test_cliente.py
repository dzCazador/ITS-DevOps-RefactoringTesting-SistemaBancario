import pytest
from src.modelos.cliente import Cliente

# ==============================================================================
# FIXTURES (Evitan duplicación de código según principios de Refactoring)
# ==============================================================================

@pytest.fixture
def cliente_valido():
    """Retorna una instancia con datos válidos para pruebas de éxito."""
    return Cliente(nombre="  juan carlos ", apellido=" gomez ", dni="12345678")


# ==============================================================================
# PRUEBAS UNITARIAS: CASOS DE ÉXITO (Happy Path)
# ==============================================================================

def test_creacion_cliente_formatea_nombre_y_apellido(cliente_valido):
    """Verifica que los métodos getter retornen los datos formateados con Title y Strip."""
    # Act
    nombre_obtenido = cliente_valido.get_nombre()
    apellido_obtenido = cliente_valido.get_apellido()
    dni_obtenido = cliente_valido.get_dni()

    # Assert
    assert nombre_obtenido == "Juan Carlos"
    assert apellido_obtenido == "Gomez"
    assert dni_obtenido == "12345678"


def test_mostrar_datos_retorna_cadena_formateada(cliente_valido):
    """Verifica que la representación en texto del cliente cumpla con el formato esperado."""
    # Arrange
    formato_esperado = "Juan Carlos Gomez (DNI: 12345678)"

    # Act & Assert
    assert cliente_valido.mostrar_datos() == formato_esperado
    assert str(cliente_valido) == formato_esperado


# ==============================================================================
# PRUEBAS UNITARIAS: VALIDACIONES Y EXCEPCIONES (SRP: 1 razón de fallo por test)
# ==============================================================================

def test_lanza_excepcion_cuando_nombre_esta_vacio():
    """SRP: Valida únicamente la falla por nombre obligatorio ausente."""
    with pytest.raises(ValueError, match="Todos los campos del cliente son obligatorios."):
        Cliente(nombre="", apellido="Gomez", dni="12345678")


def test_lanza_excepcion_cuando_apellido_esta_vacio():
    """SRP: Valida únicamente la falla por apellido obligatorio ausente."""
    with pytest.raises(ValueError, match="Todos los campos del cliente son obligatorios."):
        Cliente(nombre="Juan", apellido="", dni="12345678")


def test_lanza_excepcion_cuando_dni_esta_vacio():
    """SRP: Valida únicamente la falla por DNI obligatorio ausente."""
    with pytest.raises(ValueError, match="Todos los campos del cliente son obligatorios."):
        Cliente(nombre="Juan", apellido="Gomez", dni="")


def test_lanza_excepcion_cuando_nombre_contiene_numeros():
    """Valida la regla de negocio: nombre compuesto solo por letras."""
    with pytest.raises(ValueError, match="El nombre y apellido deben contener solo letras."):
        Cliente(nombre="Juan123", apellido="Gomez", dni="12345678")


def test_lanza_excepcion_cuando_apellido_contiene_simbolos():
    """Valida la regla de negocio: apellido compuesto solo por letras."""
    with pytest.raises(ValueError, match="El nombre y apellido deben contener solo letras."):
        Cliente(nombre="Juan", apellido="Gomez!", dni="12345678")


def test_lanza_excepcion_cuando_dni_contiene_caracteres_no_numericos():
    """Valida la regla de negocio: DNI compuesto solo por dígitos."""
    with pytest.raises(ValueError, match="El DNI debe contener solo números."):
        Cliente(nombre="Juan", apellido="Gomez", dni="1234567a")