#!/usr/bin/env python3
"""
Скрипт для проверки конфигурации Fitness Content Sorter Bot
"""

import os
from dotenv import load_dotenv

def check_config():
    """Проверка конфигурации бота"""
    print("🔍 Проверка конфигурации Fitness Content Sorter Bot")
    print("=" * 50)
    
    # Загружаем переменные окружения
    load_dotenv()
    
    # Проверяем BOT_TOKEN
    bot_token = os.getenv('BOT_TOKEN')
    if bot_token:
        print("✅ BOT_TOKEN найден")
        print(f"   Токен: {bot_token[:10]}...{bot_token[-10:]}")
    else:
        print("❌ BOT_TOKEN не найден")
        print("   Создайте файл .env и добавьте BOT_TOKEN=your_token_here")
    
    # Проверяем CHANNEL_USERNAME
    channel_username = os.getenv('CHANNEL_USERNAME', '@nikitaFlooDed')
    print(f"📢 Канал: {channel_username}")
    
    # Проверяем файлы
    print("\n📁 Проверка файлов:")
    
    required_files = [
        'bot.py',
        'config.py',
        'database.py',
        'content_analyzer.py',
        'requirements.txt'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - отсутствует")
    
    # Проверяем базу данных
    print("\n🗄️ Проверка базы данных:")
    if os.path.exists('content_bot.db'):
        size = os.path.getsize('content_bot.db')
        print(f"✅ База данных существует ({size} байт)")
    else:
        print("ℹ️ База данных будет создана при первом запуске")
    
    # Проверяем зависимости
    print("\n📦 Проверка зависимостей:")
    try:
        import telegram
        print("✅ python-telegram-bot установлен")
    except ImportError:
        print("❌ python-telegram-bot не установлен")
        print("   Запустите: py -m pip install -r requirements.txt")
    
    try:
        import requests
        print("✅ requests установлен")
    except ImportError:
        print("❌ requests не установлен")
    
    try:
        import dotenv
        print("✅ python-dotenv установлен")
    except ImportError:
        print("❌ python-dotenv не установлен")
    
    print("\n" + "=" * 50)
    
    if bot_token:
        print("✅ Конфигурация готова к запуску!")
        print("🚀 Запустите: py run_bot.py")
    else:
        print("❌ Необходимо настроить BOT_TOKEN")
        print("📝 Создайте файл .env с содержимым:")
        print("BOT_TOKEN=your_bot_token_here")
        print("CHANNEL_USERNAME=@nikitaFlooDed")

if __name__ == "__main__":
    check_config() 