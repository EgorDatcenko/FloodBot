#!/usr/bin/env python3
"""
Скрипт для очистки тестовых данных из базы
"""

import sqlite3
from database import Database

def clear_test_data():
    """Очистка тестовых данных из базы"""
    db = Database()
    
    try:
        with sqlite3.connect(db.db_path, timeout=30.0) as conn:
            cursor = conn.cursor()
            
            # Удаляем тестовые посты (с message_id от 1000 до 2000)
            cursor.execute('DELETE FROM content WHERE message_id BETWEEN 1000 AND 2000')
            deleted_count = cursor.rowcount
            
            # Удаляем посты с тестовыми заголовками
            test_titles = [
                'Челлендж Щелкунчик',
                'Челлендж Отжимания', 
                'Челлендж Приседания',
                'Челлендж Планка',
                'Челлендж Бурпи'
            ]
            
            for title in test_titles:
                cursor.execute('DELETE FROM content WHERE title LIKE ?', (f'%{title}%',))
                deleted_count += cursor.rowcount
            
            conn.commit()
            print(f"✅ Удалено {deleted_count} тестовых постов из базы данных")
            
            # Показываем оставшиеся посты
            cursor.execute('SELECT COUNT(*) FROM content')
            remaining = cursor.fetchone()[0]
            print(f"📊 Осталось постов в базе: {remaining}")
            
    except Exception as e:
        print(f"❌ Ошибка при очистке базы: {e}")

if __name__ == "__main__":
    print("🧹 Очистка тестовых данных из базы...")
    clear_test_data()
    print("✅ Очистка завершена!") 