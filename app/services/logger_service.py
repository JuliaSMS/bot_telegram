from datetime import datetime


class LoggerService:
    def __init__(self, db_service):
        self.db = db_service

    def log(self, telegram_id: int, tipo: str, prompt: str, resultado: str = None):
        entry = {
            "telegram_id": telegram_id,
            "tipo": tipo,
            "prompt": prompt,
            "resultado": resultado,
            "data": datetime.utcnow().isoformat(),
        }
        self.db.insert_log(entry)
