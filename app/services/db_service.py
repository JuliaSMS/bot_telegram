import os
from typing import Optional, List

try:
    from supabase import create_client
except Exception:
    create_client = None

from app.models.user_model import User
from app.models.log_model import LogEntry


class DBService:
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")
        # Allow forcing fallback (no remote connection) via env var USE_FALLBACK_DB
        use_fallback = os.getenv("USE_FALLBACK_DB", "false").lower() in ("1", "true", "yes")
        if not use_fallback and create_client and self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
            except Exception as e:
                print(f"[DBService] Error creating Supabase client: {e}")
                self.client = None
        else:
            self.client = None

        # In-memory fallback for local testing when Supabase is not configured
        self._mem_users = {}
        self._mem_logs = []
        from app.utils.constants import DEFAULT_PLANS
        self._mem_planos = DEFAULT_PLANS
        self._next_user_id = 1

    # Users
    def get_user_by_telegram(self, telegram_id: int) -> Optional[User]:
        if self.client:
            try:
                res = self.client.table("users").select("*").eq("telegram_id", telegram_id).execute()
                data = None
                if hasattr(res, 'data') and res.data:
                    # supabase-py typically returns a list
                    data = res.data[0] if isinstance(res.data, list) else res.data
                if not data:
                    return None
                return User(**data)
            except Exception as e:
                print(f"[DBService] get_user_by_telegram error: {e}")
                return None

        # fallback to memory
        for u in self._mem_users.values():
            if u.get("telegram_id") == telegram_id:
                return User(**u)
        return None

    def create_user(self, user: dict) -> dict:
        if self.client:
            try:
                res = self.client.table("users").insert(user).execute()
                if hasattr(res, 'data'):
                    return res.data[0] if isinstance(res.data, list) and res.data else res.data
                return {}
            except Exception as e:
                print(f"[DBService] create_user error: {e}")
                return {}

        # memory fallback
        user = dict(user)
        user_id = self._next_user_id
        self._next_user_id += 1
        user["id"] = user_id
        self._mem_users[user_id] = user
        return user

    def update_user(self, telegram_id: int, changes: dict) -> dict:
        if self.client:
            try:
                res = self.client.table("users").update(changes).eq("telegram_id", telegram_id).execute()
                if hasattr(res, 'data'):
                    return res.data
                return {}
            except Exception as e:
                print(f"[DBService] update_user error: {e}")
                return {}

        # memory fallback: find user and update
        for uid, u in self._mem_users.items():
            if u.get("telegram_id") == telegram_id:
                u.update(changes)
                self._mem_users[uid] = u
                return u
        return {}

    # Logs
    def insert_log(self, log: dict) -> dict:
        if self.client:
            try:
                res = self.client.table("logs").insert(log).execute()
                if hasattr(res, 'data'):
                    return res.data
                return {}
            except Exception as e:
                print(f"[DBService] insert_log error: {e}")
                return {}

        self._mem_logs.append(log)
        return log

    # Planos
    def list_planos(self) -> List[dict]:
        if self.client:
            try:
                res = self.client.table("planos").select("*").execute()
                return res.data if hasattr(res, 'data') else []
            except Exception as e:
                print(f"[DBService] list_planos error: {e}")
                from app.utils.constants import DEFAULT_PLANS
                return DEFAULT_PLANS
        return self._mem_planos
