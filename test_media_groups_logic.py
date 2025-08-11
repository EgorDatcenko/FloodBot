#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import Database
from content_analyzer import ContentAnalyzer

def test_media_groups_logic():
    """Тест исправленной логики обработки медиа-групп"""
    print("🧪 ТЕСТ ИСПРАВЛЕННОЙ ЛОГИКИ МЕДИА-ГРУПП")
    print("=" * 60)
    
    db = Database()
    analyzer = ContentAnalyzer()
    
    # Очищаем тестовые данные
    print("\n🗑️ Очищаю тестовые данные...")
    try:
        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM post_media WHERE content_id IN (SELECT id FROM content WHERE media_group_id = 'test_group_logic')")
            cursor.execute("DELETE FROM content WHERE media_group_id = 'test_group_logic'")
            conn.commit()
        print("✅ Тестовые данные очищены")
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")
    
    # Тест 1: Создание первого поста из медиа-группы
    print("\n1️⃣ Тест создания первого поста из медиа-группы...")
    try:
        success = db.add_content(
            message_id=1001,
            channel_id=-1001234567890,
            channel_username="test_channel",
            category="test",
            title="Тестовый пост с медиа-группой (первое медиа)",
            text="Это первый пост из медиа-группы",
            media_type="photo",
            media_file_id="test_photo_1",
            media_group_id="test_group_logic"
        )
        
        if success:
            print("✅ Первый пост из медиа-группы создан")
            
            # Проверяем, что пост создан
            content = db.get_content_by_media_group_id("test_group_logic")
            if content:
                print(f"   📱 Пост найден: ID {content['id']}, заголовок: {content['title']}")
                
                # Добавляем первое медиа
                db.add_media_to_post(content['id'], 1001, "photo", "test_photo_1", media_order=1)
                print("   📸 Первое медиа добавлено")
            else:
                print("❌ Пост не найден")
        else:
            print("❌ Не удалось создать первый пост")
            
    except Exception as e:
        print(f"❌ Ошибка при создании первого поста: {e}")
    
    # Тест 2: Добавление второго медиа к существующему посту
    print("\n2️⃣ Тест добавления второго медиа к существующему посту...")
    try:
        # Проверяем, что пост уже существует
        existing_post = db.get_content_by_media_group_id("test_group_logic")
        if existing_post:
            print(f"✅ Пост уже существует: ID {existing_post['id']}")
            
            # Добавляем второе медиа к существующему посту
            success = db.add_media_to_post(existing_post['id'], 1002, "photo", "test_photo_2", media_order=2)
            if success:
                print("   📸 Второе медиа добавлено к существующему посту")
            else:
                print("❌ Не удалось добавить второе медиа")
        else:
            print("❌ Пост не найден")
            
    except Exception as e:
        print(f"❌ Ошибка при добавлении второго медиа: {e}")
    
    # Тест 3: Добавление третьего медиа к существующему посту
    print("\n3️⃣ Тест добавления третьего медиа к существующему посту...")
    try:
        # Проверяем, что пост уже существует
        existing_post = db.get_content_by_media_group_id("test_group_logic")
        if existing_post:
            print(f"✅ Пост уже существует: ID {existing_post['id']}")
            
            # Добавляем третье медиа к существующему посту
            success = db.add_media_to_post(existing_post['id'], 1003, "video", "test_video_1", media_order=3)
            if success:
                print("   🎥 Третье медиа (видео) добавлено к существующему посту")
            else:
                print("❌ Не удалось добавить третье медиа")
        else:
            print("❌ Пост не найден")
            
    except Exception as e:
        print(f"❌ Ошибка при добавлении третьего медиа: {e}")
    
    # Тест 4: Проверка результата
    print("\n4️⃣ Проверка результата...")
    try:
        # Получаем пост с медиафайлами
        content = db.get_content_with_media_files("test", limit=10)
        if content:
            for post in content:
                if post.get('media_group_id') == 'test_group_logic':
                    media_files = post.get('media_files', [])
                    print(f"✅ Пост найден: {post['title']}")
                    print(f"   📱 Медиа-группа ID: {post['media_group_id']}")
                    print(f"   📊 Медиафайлов: {len(media_files)}")
                    
                    if media_files:
                        for i, media in enumerate(media_files, 1):
                            print(f"      {i}. {media['media_type']}: {media['media_file_id']} (порядок: {media['media_order']})")
                    else:
                        print("      ❌ Медиафайлы не найдены")
                    break
            else:
                print("❌ Пост с медиа-группой не найден")
        else:
            print("❌ Посты не найдены")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке результата: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")

if __name__ == "__main__":
    test_media_groups_logic() 