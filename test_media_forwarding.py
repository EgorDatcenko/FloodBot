#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы с пересылкой медиа
"""

import asyncio
import logging
from telegram import Bot
from telegram.error import TelegramError
from config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def test_media_access():
    """Тестирование доступа к медиа файлам"""
    bot = Bot(token=BOT_TOKEN)
    
    # Тестовые file_id (нужно заменить на реальные)
    test_file_ids = [
        # Добавьте сюда реальные file_id из вашей базы данных
        # "BQACAgIAAxkBAAIB..." # пример
    ]
    
    print("🔍 Тестирование доступа к медиа файлам...")
    
    for i, file_id in enumerate(test_file_ids, 1):
        try:
            print(f"\n📁 Тест {i}: {file_id[:20]}...")
            file_info = await bot.get_file(file_id)
            if file_info:
                print(f"   ✅ Доступен: {file_info.file_id}")
                print(f"   📏 Размер: {file_info.file_size} байт")
                print(f"   🔗 URL: {file_info.file_path}")
            else:
                print(f"   ❌ Недоступен: file_info пустой")
        except TelegramError as e:
            print(f"   ❌ Ошибка: {e}")
        except Exception as e:
            print(f"   ❌ Неожиданная ошибка: {e}")
    
    await bot.close()

async def test_bot_info():
    """Тестирование информации о боте"""
    bot = Bot(token=BOT_TOKEN)
    
    try:
        me = await bot.get_me()
        print(f"\n🤖 Информация о боте:")
        print(f"   Имя: {me.first_name}")
        print(f"   Username: @{me.username}")
        print(f"   ID: {me.id}")
        print(f"   Может читать сообщения: {me.can_read_all_group_messages}")
        print(f"   Поддерживает inline режим: {me.supports_inline_queries}")
    except Exception as e:
        print(f"❌ Ошибка при получении информации о боте: {e}")
    
    await bot.close()

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов медиа...")
    
    await test_bot_info()
    await test_media_access()
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    asyncio.run(main()) 