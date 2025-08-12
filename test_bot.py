#!/usr/bin/env python3
"""
Тестирование бота через API
"""

import requests

def test_bot():
    """Тестирование бота"""
    token = "8207363649:AAGRhGrlXsRi3tkP5oZCs0ncIeOUDNwR1fo"
    
    # Проверяем информацию о боте
    url = f"https://api.telegram.org/bot{token}/getMe"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data['ok']:
            bot_info = data['result']
            print(f"🤖 Бот: {bot_info['first_name']}")
            print(f"   Username: @{bot_info['username']}")
            print(f"   ID: {bot_info['id']}")
            print("✅ Бот доступен!")
        else:
            print(f"❌ Ошибка: {data['description']}")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке бота: {e}")

def test_webhook():
    """Тестирование webhook"""
    token = "8207363649:AAGRhGrlXsRi3tkP5oZCs0ncIeOUDNwR1fo"
    
    url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data['ok']:
            webhook_info = data['result']
            print(f"\n🔗 Webhook URL: {webhook_info['url']}")
            print(f"   Ошибка: {webhook_info['last_error_message']}")
            print(f"   Ожидающие обновления: {webhook_info['pending_update_count']}")
            
            if webhook_info['url'] == "https://floodbot-pqmy.onrender.com/webhook":
                print("✅ Webhook настроен правильно!")
            else:
                print("❌ Webhook настроен неправильно!")
        else:
            print(f"❌ Ошибка webhook: {data['description']}")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке webhook: {e}")

if __name__ == "__main__":
    print("🧪 Тестирование бота")
    print("=" * 30)
    
    test_bot()
    test_webhook() 