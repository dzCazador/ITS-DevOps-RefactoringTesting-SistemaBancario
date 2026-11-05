"""Domain errors shared by the DAO and the controllers."""


class CuentaNoEncontradaError(LookupError):
    """The requested account does not exist or is not the client's."""

    def __init__(self, etiqueta: str):
        super().__init__(etiqueta)
        self.etiqueta = etiqueta


class TransferenciaInvalidaError(LookupError):
    """A transfer breaks a business rule (same account, same holder)."""
