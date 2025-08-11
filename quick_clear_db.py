#!/usr/bin/env python3
"""
Быстрая очистка базы данных
"""

import os
from database import Database

def quick_clear():
    """Быстрая очистка базы данных"""
    db_path = "content_bot.db"
    
    print("🗑️ Быстрая очистка базы данных...")
    
    try:
        # Удаляем файл базы данных
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ Старый файл базы данных удален")
        
        # Создаем новую базу данных
        db = Database()
        db.init_database()
        print("✅ Новая база данных создана")
        
        # Проверяем, что база пуста
        total_posts = db.get_total_posts_count()
        print(f"📊 Постов в новой базе: {total_posts}")
        
        if total_posts == 0:
            print("✅ База данных успешно очищена и готова к использованию!")
        else:
            print("❌ Ошибка: в базе все еще есть посты")
            
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")

if __name__ == "__main__":
    quick_clear() 