from dataclasses import dataclass
from typing import Optional


@dataclass
class LogEntry:
    id: Optional[int]
    telegram_id: int
    tipo: str
    prompt: str
    resultado: Optional[str]
    data: str
