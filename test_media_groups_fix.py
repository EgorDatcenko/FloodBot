#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправленной обработки медиа-групп
"""

import asyncio
import logging
from database import Database
from content_analyzer import ContentAnalyzer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_media_groups_fix():
    """Тестирование исправленной обработки медиа-групп"""
    
    print("🧪 ТЕСТИРОВАНИЕ ИСПРАВЛЕННОЙ ОБРАБОТКИ МЕДИА-ГРУПП")
    print("=" * 60)
    
    # Инициализируем компоненты
    db = Database()
    analyzer = ContentAnalyzer()
    
    # Тест 1: Проверка структуры базы данных
    print("\n1️⃣ Проверка структуры базы данных...")
    try:
        import sqlite3
        with sqlite3.connect(db.db_path, timeout=30.0) as conn:
            cursor = conn.cursor()
            
            # Проверяем таблицу post_media
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='post_media'")
            table_exists = cursor.fetchone() is not None
        
        if table_exists:
            print("✅ Таблица post_media существует")
        else:
            print("❌ Таблица post_media не найдена")
            
        # Проверяем колонку media_group_id
        cursor.execute("PRAGMA table_info(content)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'media_group_id' in columns:
            print("✅ Колонка media_group_id существует в таблице content")
        else:
            print("❌ Колонка media_group_id не найдена в таблице content")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке структуры БД: {e}")
    
    # Тест 2: Проверка методов анализатора
    print("\n2️⃣ Проверка методов анализатора...")
    try:
        # Создаем тестовое сообщение с медиа-группой
        class MockMessage:
            def __init__(self):
                self.media_group_id = "test_group_456"
                self.photo = [MockPhoto("photo1"), MockPhoto("photo2")]
                self.caption = "Тестовый пост с несколькими фото"
        
        class MockPhoto:
            def __init__(self, file_id):
                self.file_id = file_id
        
        mock_message = MockMessage()
        
        # Тестируем extract_media_info
        media_type, media_file_id = analyzer.extract_media_info(mock_message)
        print(f"✅ extract_media_info: {media_type} - {media_file_id}")
        
        # Тестируем extract_all_media_info
        all_media = analyzer.extract_all_media_info(mock_message)
        print(f"✅ extract_all_media_info: {len(all_media)} медиафайлов")
        for i, (m_type, m_id) in enumerate(all_media, 1):
            print(f"   {i}. {m_type}: {m_id}")
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании анализатора: {e}")
    
    # Тест 3: Проверка добавления контента с медиа-группой
    print("\n3️⃣ Тестирование добавления контента с медиа-группой...")
    try:
        # Добавляем тестовый контент с медиа-группой
        success = db.add_content(
            message_id=123456,
            channel_id=-1001234567890,
            channel_username="test_channel",
            category="test",
            title="Тестовый пост с медиа-группой",
            text="Это тестовый пост для проверки обработки медиа-групп",
            media_type="photo",
            media_file_id="test_photo_main",
            media_group_id="test_group_456"
        )
        
        if success:
            print("✅ Контент с медиа-группой добавлен")
            
            # Проверяем, что контент добавлен
            content = db.get_content_by_media_group_id("test_group_456")
            if content:
                print(f"✅ Контент найден по media_group_id: {content['title']}")
                
                # Добавляем дополнительные медиафайлы
                print("   📊 Добавляю дополнительные медиафайлы...")
                
                # Симулируем добавление медиафайлов через новый метод
                db.add_media_to_post(content['id'], 123456, "photo", "test_photo_1", media_order=1)
                db.add_media_to_post(content['id'], 123456, "photo", "test_photo_2", media_order=2)
                db.add_media_to_post(content['id'], 123456, "video", "test_video_1", media_order=3)
                
                # Проверяем медиафайлы
                media_files = db.get_post_media(content['id'])
                print(f"✅ Найдено медиафайлов: {len(media_files)}")
                for i, media in enumerate(media_files, 1):
                    print(f"   {i}. {media['media_type']}: {media['media_file_id']} (порядок: {media['media_order']})")
            else:
                print("❌ Контент не найден по media_group_id")
        else:
            print("❌ Не удалось добавить контент с медиа-группой")
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании добавления контента: {e}")
    
    # Тест 4: Проверка получения контента с медиафайлами
    print("\n4️⃣ Тестирование получения контента с медиафайлами...")
    try:
        content_list = db.get_content_with_media_files("test", limit=10)
        if content_list:
            print(f"✅ Найдено {len(content_list)} постов в категории test")
            for i, content in enumerate(content_list, 1):
                print(f"   {i}. {content['title']}")
                media_files = content.get('media_files', [])
                print(f"      Медиафайлов: {len(media_files)}")
                if media_files:
                    for j, media in enumerate(media_files, 1):
                        print(f"         {j}. {media['media_type']}: {media['media_file_id']} (порядок: {media['media_order']})")
                else:
                    print("         ❌ Медиафайлы не найдены")
        else:
            print("❌ Посты в категории test не найдены")
            
    except Exception as e:
        print(f"❌ Ошибка при получении контента: {e}")
    
    # Тест 5: Проверка предотвращения дублирования
    print("\n5️⃣ Тестирование предотвращения дублирования...")
    try:
        # Пытаемся добавить тот же контент снова
        success = db.add_content(
            message_id=123457,  # Другой message_id, но тот же media_group_id
            channel_id=-1001234567890,
            channel_username="test_channel",
            category="test",
            title="Дублированный пост с медиа-группой",
            text="Это дублированный пост",
            media_type="photo",
            media_file_id="test_photo_duplicate",
            media_group_id="test_group_456"  # Тот же media_group_id
        )
        
        if success:
            print("✅ Дублированный контент добавлен (обновлен существующий)")
            
            # Проверяем, что контент обновлен
            content = db.get_content_by_media_group_id("test_group_456")
            if content:
                print(f"✅ Обновленный контент: {content['title']}")
                
                # Проверяем, что медиафайлы добавлены
                media_files = db.get_post_media(content['id'])
                print(f"✅ Всего медиафайлов после обновления: {len(media_files)}")
                for i, media in enumerate(media_files, 1):
                    print(f"   {i}. {media['media_type']}: {media['media_file_id']} (порядок: {media['media_order']})")
        else:
            print("❌ Не удалось обновить контент")
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании дублирования: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")

if __name__ == "__main__":
    asyncio.run(test_media_groups_fix()) 