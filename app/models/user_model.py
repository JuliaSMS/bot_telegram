from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: Optional[int]
    telegram_id: int
    nome: str
    plano: str
    limite_diario: int
    geracoes_hoje: int
    ultima_geracao: Optional[str]

