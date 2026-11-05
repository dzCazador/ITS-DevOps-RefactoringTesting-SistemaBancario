"""Use cases for login (authentication)."""

from src.autenticacion import Autenticacion


class CamposIncompletosError(ValueError):
    """DNI or password was empty."""


class CredencialesInvalidasError(ValueError):
    """DNI/password pair does not match a known user."""


class AuthController:
    def __init__(self, dao):
        self._dao = dao
        self._autenticacion = Autenticacion(dao)

    def iniciar_sesion(self, dni: str, clave: str) -> dict:
        """Return the authenticated user identity dict.

        :raises CamposIncompletosError: if DNI or password is blank.
        :raises CredencialesInvalidasError: if the credentials are wrong.
        """
        dni = (dni or "").strip()
        clave = (clave or "").strip()

        if not dni or not clave:
            raise CamposIncompletosError("DNI y clave son obligatorios.")

        usuario = self._autenticacion.autenticar(dni, clave)
        if usuario is None:
            raise CredencialesInvalidasError("DNI o clave incorrectos.")

        return usuario
