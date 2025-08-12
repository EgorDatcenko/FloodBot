import threading
from flask import Flask
import os

# Запускаем Flask-сервер-затычку для Render
app = Flask(__name__)

@app.route('/')
def index():
    return "FloodBot is running!"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web, daemon=True).start()

# Далее запускаем бота как обычно
import bot
if __name__ == "__main__":
    bot_main = bot.ContentBot()
    bot_main.run()