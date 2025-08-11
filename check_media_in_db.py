#!/usr/bin/env python3
"""
Скрипт для проверки медиа файлов в базе данных
"""

import asyncio
import logging
from database import Database
from telegram import Bot
from telegram.error import TelegramError
from config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def check_media_in_database():
    """Проверка медиа файлов в базе данных"""
    db = Database()
    bot = Bot(token=BOT_TOKEN)
    
    print("🔍 Проверка медиа файлов в базе данных...")
    
    # Получаем все записи с медиа
    content_with_media = db.get_content_with_media()
    
    if not content_with_media:
        print("📝 В базе данных нет записей с медиа")
        return
    
    print(f"📊 Найдено {len(content_with_media)} записей с медиа")
    
    # Статистика по типам медиа
    media_stats = {}
    available_count = 0
    unavailable_count = 0
    
    for item in content_with_media:
        media_type = item.get('media_type')
        media_file_id = item.get('media_file_id')
        message_id = item.get('message_id')
        title = item.get('title', 'Без заголовка')[:50]
        
        # Подсчитываем статистику
        if media_type:
            media_stats[media_type] = media_stats.get(media_type, 0) + 1
        
        print(f"\n📱 Пост {message_id}: {title}")
        print(f"   Тип медиа: {media_type}")
        print(f"   File ID: {media_file_id[:30] if media_file_id else 'Нет'}...")
        
        # Проверяем доступность медиа
        if media_file_id:
            try:
                file_info = await bot.get_file(media_file_id)
                if file_info and file_info.file_id:
                    print(f"   ✅ Доступен")
                    print(f"   📏 Размер: {file_info.file_size} байт")
                    available_count += 1
                else:
                    print(f"   ❌ Недоступен (file_info пустой)")
                    unavailable_count += 1
            except TelegramError as e:
                print(f"   ❌ Недоступен: {e}")
                unavailable_count += 1
            except Exception as e:
                print(f"   ❌ Ошибка проверки: {e}")
                unavailable_count += 1
        else:
            print(f"   ⚠️ File ID отсутствует")
            unavailable_count += 1
    
    # Выводим итоговую статистику
    print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"   Всего записей с медиа: {len(content_with_media)}")
    print(f"   Доступных медиа: {available_count}")
    print(f"   Недоступных медиа: {unavailable_count}")
    print(f"   Процент доступности: {(available_count/len(content_with_media)*100):.1f}%")
    
    print(f"\n📁 Статистика по типам медиа:")
    for media_type, count in media_stats.items():
        print(f"   {media_type}: {count}")
    
    await bot.close()

async def test_specific_media():
    """Тестирование конкретных медиа файлов"""
    db = Database()
    bot = Bot(token=BOT_TOKEN)
    
    print("\n🎯 Тестирование конкретных медиа файлов...")
    
    # Получаем несколько примеров каждого типа медиа
    media_types = ['video', 'photo', 'animation', 'audio', 'document']
    
    for media_type in media_types:
        print(f"\n📁 Тестирование {media_type}:")
        content = db.get_content_by_media_type(media_type, limit=3)
        
        if not content:
            print(f"   Нет записей с типом {media_type}")
            continue
        
        for item in content:
            media_file_id = item.get('media_file_id')
            message_id = item.get('message_id')
            
            if media_file_id:
                try:
                    file_info = await bot.get_file(media_file_id)
                    if file_info:
                        print(f"   ✅ {message_id}: {media_file_id[:20]}... - Доступен")
                    else:
                        print(f"   ❌ {message_id}: {media_file_id[:20]}... - Недоступен")
                except Exception as e:
                    print(f"   ❌ {message_id}: {media_file_id[:20]}... - Ошибка: {e}")
            else:
                print(f"   ⚠️ {message_id}: File ID отсутствует")
    
    await bot.close()

async def main():
    """Основная функция"""
    print("🚀 Запуск проверки медиа в базе данных...")
    
    await check_media_in_database()
    await test_specific_media()
    
    print("\n✅ Проверка завершена!")

if __name__ == "__main__":
    asyncio.run(main()) 