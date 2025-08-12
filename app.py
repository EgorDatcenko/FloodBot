from flask import Flask, jsonify
import threading
import os
import sys
from datetime import datetime

app = Flask(__name__)

# Глобальная переменная для хранения статуса бота
bot_status = {
    "running": False,
    "started_at": None,
    "last_activity": None
}

def run_bot():
    """Запуск бота в отдельном потоке"""
    try:
        # Импортируем и запускаем бота
        from bot import ContentBot
        import asyncio
        
        bot = ContentBot()
        bot_status["running"] = True
        bot_status["started_at"] = datetime.now().isoformat()
        
        print("🤖 Бот запущен в фоновом режиме")
        
        # Запускаем бота
        asyncio.run(bot.run())
        
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        bot_status["running"] = False
        bot_status["error"] = str(e)

@app.route('/')
def home():
    """Главная страница - показывает статус бота"""
    return jsonify({
        "status": "running",
        "bot": bot_status,
        "message": "FloodBot работает!",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Эндпоинт для проверки здоровья сервиса"""
    return jsonify({
        "status": "healthy",
        "bot_running": bot_status["running"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/status')
def status():
    """Детальный статус бота"""
    return jsonify(bot_status)

if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Получаем порт из переменной окружения (для Render)
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🚀 Запускаем веб-сервер на порту {port}")
    print(f"📱 Бот запускается в фоновом режиме...")
    
    # Запускаем Flask сервер
    app.run(host='0.0.0.0', port=port, debug=False) 