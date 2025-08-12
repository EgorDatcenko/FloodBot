#!/usr/bin/env python3
"""
Тестовый скрипт для проверки переменных окружения
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Проверка переменных окружения:")
print(f"BOT_TOKEN: {'✅ установлен' if os.getenv('BOT_TOKEN') else '❌ отсутствует'}")
print(f"WEBHOOK_URL: {os.getenv('WEBHOOK_URL', '❌ не установлен')}")
print(f"PORT: {os.environ.get('PORT', '❌ не установлен')}")

if os.getenv('BOT_TOKEN'):
    token = os.getenv('BOT_TOKEN')
    print(f"Токен (первые 10 символов): {token[:10]}...")
else:
    print("❌ BOT_TOKEN не найден! Добавьте его в переменные окружения Render.") 