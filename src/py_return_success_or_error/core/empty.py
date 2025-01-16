class Empty:
    """Classe singleton para representar um valor Vazio."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Empty, cls).__new__(cls)
        return cls._instance

    def __str__(self):
        return "<Empty>"  # pragma: no cover


EMPTY = Empty()
