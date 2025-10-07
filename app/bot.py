import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile

from app.services.db_service import DBService
from app.services.gemini_service import GeminiService
from app.services.limiter_service import LimiterService
from app.services.logger_service import LoggerService
from app.services.storage_service import StorageService


db = DBService()
gemini = GeminiService()
limiter = LimiterService(db)
logger = LoggerService(db)
storage = StorageService(db)

bot_token = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=bot_token) if bot_token else None
dp = Dispatcher()


async def cmd_start(message: types.Message):
    tg_id = message.from_user.id
    nome = message.from_user.full_name
    user = db.get_user_by_telegram(tg_id)
    if not user:
        # create with free plan default
        user_obj = {
            "telegram_id": tg_id,
            "nome": nome,
            "plano": "Free",
            "limite_diario": 5,
            "geracoes_hoje": 0,
            "ultima_geracao": None,
        }
        db.create_user(user_obj)
        await message.reply(f"Bem-vindo, {nome}! Você foi cadastrado com o plano Free.")
    else:
        await message.reply(f"Olá {nome}, bem-vindo de volta! Seu plano: {user.plano}")


async def cmd_meu_plano(message: types.Message):
    tg_id = message.from_user.id
    user = db.get_user_by_telegram(tg_id)
    if not user:
        await message.reply("Usuário não encontrado. Use /start para se registrar.")
        return
    remaining = max(0, user.limite_diario - (user.geracoes_hoje or 0))
    await message.reply(f"Plano: {user.plano}\nLimite diário: {user.limite_diario}\nGerações hoje: {user.geracoes_hoje}\nRestam: {remaining}")


async def cmd_ajuda(message: types.Message):
    text = (
        "/start - registrar-se\n"
        "/meu_plano - ver plano e limites\n"
        "/gerar_texto texto... - gera texto criativo\n"
        "/gerar_imagem texto... - gera imagem (mock)\n"
        "/gerar_video texto... - gera vídeo (stub)\n"
        "/comprar - ver planos\n"
    )
    await message.reply(text)


async def cmd_comprar(message: types.Message):
    planos = db.list_planos()
    lines = []
    for p in planos:
        lines.append(f"{p['id']}: {p['nome']} - limite {p['limite']} - ${p['preco']}")
    await message.reply("\n".join(lines))


async def cmd_gerar_texto(message: types.Message):
    tg_id = message.from_user.id
    prompt = message.get_args()
    ok, msg = limiter.can_generate(tg_id)
    if not ok:
        await message.reply(msg)
        return
    await message.reply("Gerando texto...")
    try:
        result = gemini.generate_text(prompt)
        logger.log(tg_id, "text", prompt, resultado=result)
        limiter.increment(tg_id)
        await message.reply(result)
    except Exception as e:
        logger.log(tg_id, "text", prompt, resultado=str(e))
        await message.reply(f"Erro ao gerar texto: {e}")


async def cmd_gerar_imagem(message: types.Message):
    tg_id = message.from_user.id
    prompt = message.get_args()
    ok, msg = limiter.can_generate(tg_id)
    if not ok:
        await message.reply(msg)
        return
    await message.reply("Gerando imagem... (mock)")
    try:
        img_bytes = gemini.generate_image(prompt)
        # ensure bytes
        if not img_bytes:
            img_bytes = gemini.generate_image(prompt)

        # Upload to storage (supabase) or save locally
        filename = f"images/{tg_id}_{int(__import__('time').time())}.png"
        url_or_path = storage.upload_bytes('generated', filename, img_bytes)

        limiter.increment(tg_id)
        logger.log(tg_id, "image", prompt, resultado=url_or_path)

        # If storage returned local path, send as file; if url, send photo by url
        if url_or_path and url_or_path.startswith('http'):
            await message.reply_photo(photo=url_or_path)
        else:
            # local path
            await message.reply_photo(photo=FSInputFile(url_or_path))
    except Exception as e:
        logger.log(tg_id, "image", prompt, resultado=str(e))
        await message.reply(f"Erro ao gerar imagem: {e}")


async def cmd_gerar_video(message: types.Message):
    tg_id = message.from_user.id
    prompt = message.get_args()
    ok, msg = limiter.can_generate(tg_id)
    if not ok:
        await message.reply(msg)
        return
    await message.reply("Gerando vídeo... (stub)")
    # stub: respond with message and log
    logger.log(tg_id, "video", prompt, resultado="stub")
    limiter.increment(tg_id)
    await message.reply("Geração de vídeo é uma função stub por enquanto.")


def register_handlers():
    dp.message.register(cmd_start, Command(commands=["start"]))
    dp.message.register(cmd_meu_plano, Command(commands=["meu_plano"]))
    dp.message.register(cmd_ajuda, Command(commands=["ajuda"]))
    dp.message.register(cmd_comprar, Command(commands=["comprar"]))
    dp.message.register(cmd_gerar_texto, Command(commands=["gerar_texto"]))
    dp.message.register(cmd_gerar_imagem, Command(commands=["gerar_imagem"]))
    dp.message.register(cmd_gerar_video, Command(commands=["gerar_video"]))


def start_polling():
    if not bot:
        print("TELEGRAM_TOKEN não configurado. Bot não iniciado.")
        return
    register_handlers()
    # Support both polling and webhook modes via BOT_MODE env var
    import asyncio
    import os

    BOT_MODE = os.getenv('BOT_MODE', 'polling')

    async def _run_polling():
        try:
            await dp.start_polling(bot)
        finally:
            await bot.session.close()

    async def _run_webhook():
        # Minimal webhook runner; aiogram webhook requires an ASGI/HTTPS endpoint in production.
        webhook_url = os.getenv('WEBHOOK_URL')
        if not webhook_url:
            print('WEBHOOK_URL não configurado. Saindo do modo webhook.')
            return
        # For deploy, prefer using an ASGI server and aiogram webhook integration.
        await _run_polling()

    if BOT_MODE == 'webhook':
        asyncio.run(_run_webhook())
    else:
        asyncio.run(_run_polling())
