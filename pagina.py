from constantes import *

# Classe Pagina
class Pagina:

    def __init__(self) -> None:

        self.numChaves: int = 0
        self.chaves: list = [NULO] * (ORDEM - 1)
        self.offsets: list = [NULO] * (ORDEM - 1)
        self.filhos: list = [NULO] * ORDEM