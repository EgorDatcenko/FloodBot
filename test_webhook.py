#!/usr/bin/env python3
"""
Тестовый скрипт для проверки webhook статуса
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_webhook():
    """Проверка webhook статуса"""
    token = os.getenv('BOT_TOKEN')
    if not token:
        print("❌ BOT_TOKEN не найден")
        return
    
    webhook_url = os.getenv('WEBHOOK_URL')
    if not webhook_url:
        print("❌ WEBHOOK_URL не найден")
        return
    
    # Проверяем webhook статус
    url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print("🔍 Статус webhook:")
        print(f"   URL: {data['result']['url']}")
        print(f"   Ошибка: {data['result']['last_error_message']}")
        print(f"   Ожидающие обновления: {data['result']['pending_update_count']}")
        
        if data['result']['url'] == f"{webhook_url}/webhook":
            print("✅ Webhook установлен правильно!")
        else:
            print("❌ Webhook установлен неправильно!")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке webhook: {e}")

def test_endpoints():
    """Проверка HTTP endpoints"""
    webhook_url = os.getenv('WEBHOOK_URL')
    if not webhook_url:
        print("❌ WEBHOOK_URL не найден")
        return
    
    endpoints = [
        ("/", "Главная страница"),
        ("/health", "Здоровье сервиса"),
        ("/setup", "Настройки")
    ]
    
    print("\n🌐 Проверка HTTP endpoints:")
    
    for endpoint, name in endpoints:
        try:
            url = f"{webhook_url}{endpoint}"
            response = requests.get(url)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} {name}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"      Ответ: {data}")
        except Exception as e:
            print(f"   ❌ {name}: ошибка - {e}")

if __name__ == "__main__":
    print("🧪 Тестирование webhook и endpoints")
    print("=" * 40)
    
    test_webhook()
    test_endpoints() 