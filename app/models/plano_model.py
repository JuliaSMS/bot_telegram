from dataclasses import dataclass


@dataclass
class Plano:
    id: int
    nome: str
    limite: int
    preco: float
