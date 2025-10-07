from typing import Tuple
from app.utils.helpers import today_date_str


class LimiterService:
    def __init__(self, db_service):
        self.db = db_service

    def can_generate(self, telegram_id: int) -> Tuple[bool, str]:
        user = self.db.get_user_by_telegram(telegram_id)
        if not user:
            return False, "Usuário não cadastrado. Use /start"

        # reset if last generation is not today
        today = today_date_str()
        if not user.ultima_geracao or user.ultima_geracao != today:
            # reset counter
            self.db.update_user(telegram_id, {"geracoes_hoje": 0, "ultima_geracao": today})
            user.geracoes_hoje = 0
            user.ultima_geracao = today

        if user.geracoes_hoje >= user.limite_diario:
            return False, "Você atingiu o limite diário do seu plano. Aguarde até amanhã ou atualize seu plano."

        return True, "OK"

    def increment(self, telegram_id: int):
        user = self.db.get_user_by_telegram(telegram_id)
        if not user:
            return
        new_count = (user.geracoes_hoje or 0) + 1
        self.db.update_user(telegram_id, {"geracoes_hoje": new_count, "ultima_geracao": today_date_str()})
