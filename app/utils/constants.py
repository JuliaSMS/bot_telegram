from enum import Enum


class LogType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"


DEFAULT_PLANS = [
    {"id": 1, "nome": "Free", "limite": 5, "preco": 0},
    {"id": 2, "nome": "Pro", "limite": 50, "preco": 9.99},
]
