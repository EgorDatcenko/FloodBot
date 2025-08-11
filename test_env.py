import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Получаем значения
bot_token = os.getenv('BOT_TOKEN')
channel_username = os.getenv('CHANNEL_USERNAME')

print("🔍 Проверка переменных окружения:")
print(f"BOT_TOKEN: {bot_token}")
print(f"CHANNEL_USERNAME: {channel_username}")

if bot_token:
    print("✅ Токен бота загружен успешно!")
else:
    print("❌ Токен бота не найден!")

if channel_username:
    print("✅ Имя канала загружено успешно!")
else:
    print("❌ Имя канала не найдено!") 