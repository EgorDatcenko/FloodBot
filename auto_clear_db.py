#!/usr/bin/env python3
"""
Автоматическая очистка базы данных от старых постов
"""

import sqlite3
import os

def clear_database():
    """Очистка базы данных от всех постов"""
    
    db_path = "content_bot.db"
    
    if not os.path.exists(db_path):
        print("❌ База данных не найдена")
        return
    
    try:
        with sqlite3.connect(db_path, timeout=30.0) as conn:
            cursor = conn.cursor()
            
            # Получаем статистику перед очисткой
            cursor.execute("SELECT COUNT(*) FROM content")
            content_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM post_media")
            media_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM stats")
            stats_count = cursor.fetchone()[0]
            
            print(f"📊 Статистика перед очисткой:")
            print(f"   Постов: {content_count}")
            print(f"   Медиафайлов: {media_count}")
            print(f"   Записей статистики: {stats_count}")
            
            # Очищаем таблицы
            print("\n🧹 Очистка базы данных...")
            
            # Очищаем медиафайлы (сначала из-за внешнего ключа)
            cursor.execute("DELETE FROM post_media")
            media_deleted = cursor.rowcount
            print(f"   ✅ Удалено медиафайлов: {media_deleted}")
            
            # Очищаем посты
            cursor.execute("DELETE FROM content")
            content_deleted = cursor.rowcount
            print(f"   ✅ Удалено постов: {content_deleted}")
            
            # Очищаем статистику
            cursor.execute("DELETE FROM stats")
            stats_deleted = cursor.rowcount
            print(f"   ✅ Удалено записей статистики: {stats_deleted}")
            
            # Сбрасываем автоинкремент
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('content', 'post_media', 'stats')")
            
            conn.commit()
            
            print(f"\n✅ База данных успешно очищена!")
            print(f"   Удалено постов: {content_deleted}")
            print(f"   Удалено медиафайлов: {media_deleted}")
            print(f"   Удалено записей статистики: {stats_deleted}")
            
    except Exception as e:
        print(f"❌ Ошибка при очистке базы данных: {e}")

if __name__ == "__main__":
    print("🗑️ АВТОМАТИЧЕСКАЯ ОЧИСТКА БАЗЫ ДАННЫХ")
    print("=" * 50)
    clear_database() 