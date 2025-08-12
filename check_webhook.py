#!/usr/bin/env python3
"""
Проверка webhook статуса
"""

import requests

# Замените на ваш токен
TOKEN = "8207363649:AAGRhGrlXsRi3tkP5oZCs0ncIeOUDNwR1fo"

def check_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print("🔍 Webhook статус:")
        print(f"   URL: {data['result']['url']}")
        print(f"   Ошибка: {data['result']['last_error_message']}")
        print(f"   Ожидающие обновления: {data['result']['pending_update_count']}")
        
        if data['result']['url'] == "https://floodbot-pqmy.onrender.com/webhook":
            print("✅ Webhook установлен правильно!")
        else:
            print("❌ Webhook установлен неправильно!")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    check_webhook() 