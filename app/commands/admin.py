from aiogram import types
from aiogram.filters import Command
from app.services.db_service import DBService

db = DBService()


async def cmd_admin(message: types.Message):
    # Simple admin info: number of users in memory fallback
    if not db.client:
        users = getattr(db, '_mem_users', {})
        await message.reply(f"Modo fallback (sem Supabase). Usuários em memória: {len(users)}")
    else:
        res = db.client.table('users').select('count').execute()
        await message.reply(f"Supabase conectado. Status: {res.status_code}")


__all__ = ["cmd_admin"]
# Admin command placeholders (ban, stats, setplan)

def cmd_admin_stub(message):
    return
