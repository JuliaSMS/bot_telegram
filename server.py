from flask import Flask
import threading
import os

app = Flask(__name__)


@app.route("/")
def index():
    return "Bot ativo 🚀"


def run_flask():
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 8080))
    app.run(host=host, port=port)


def start_bot():
    # Import here to avoid circular import at module import time
    try:
        from app.bot import start_polling
        start_polling()
    except Exception as e:
        print("Erro ao iniciar o bot:", e)


if __name__ == "__main__":
    # Start bot in a thread
    t = threading.Thread(target=start_bot, daemon=True)
    t.start()
    # Run Flask (blocking)
    run_flask()
