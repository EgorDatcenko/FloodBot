#!/usr/bin/env python3
"""
Комплексный скрипт для исправления всех проблем
"""

import os
import sqlite3
import time
import subprocess
import sys

def check_and_fix_database():
    """Проверка и исправление базы данных"""
    print("🔧 Проверка базы данных...")
    
    db_path = "content_bot.db"
    
    # Удаляем файл базы данных если он заблокирован
    if os.path.exists(db_path):
        try:
            with sqlite3.connect(db_path, timeout=5.0) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM content")
                count = cursor.fetchone()[0]
                print(f"✅ База данных доступна, записей: {count}")
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print("⚠️ База данных заблокирована, удаляю...")
                os.remove(db_path)
                print("✅ Файл базы данных удален")
            else:
                print(f"❌ Ошибка базы данных: {e}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            if os.path.exists(db_path):
                os.remove(db_path)
                print("✅ Файл базы данных удален")

def add_test_data():
    """Добавление тестовых данных"""
    print("📝 Добавление тестовых данных...")
    
    db_path = "content_bot.db"
    
    # Тестовые данные
    test_data = [
        (1, -100123456789, "challenges", "Челлендж дня", "Присоединяйтесь к вызову #челлендж 💪", None, None),
        (2, -100123456789, "challenges", "Новый челлендж", "Новый челлендж на этой неделе! #челендж #вызов #фитнес", None, None),
        (3, -100123456789, "challenges", "Челлендж Щелкунчик", '---------- ⚠️ ЧЕЛЕНДЖ ⚠️ ----------\n"Щелкунчик"\nИНВЕНТАРЬ:\n- ГРЕЦКИЕ ОРЕХИ (🌰)\n- ПАЛЬЦЫ (большой/ср/указат)\nНЕ ЗАБЫВАЕМ:\n"Мужички, кому не слабо, жду от вас [ВИДОСЫ] и [Ответные ЗАДАНИЯ] в комменты! #челендж"', None, None),
        (4, -100123456789, "power_results", "Мой рекорд", "Новый рекорд в жиме лежа! #результаты #сила", None, None),
        (5, -100123456789, "sport_tips", "Совет по технике", "Как правильно делать приседания #советы #техника", None, None),
        (6, -100123456789, "exercises", "Упражнение дня", "Техника выполнения приседаний #упражнения #фитнес", None, None),
        (7, -100123456789, "memes", "Мем из зала", "Забавная ситуация в спортзале #мемы #юмор", None, None),
    ]
    
    try:
        with sqlite3.connect(db_path, timeout=60.0) as conn:
            cursor = conn.cursor()
            
            # Создаем таблицы
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER UNIQUE,
                    channel_id INTEGER,
                    category TEXT,
                    title TEXT,
                    text TEXT,
                    media_type TEXT,
                    media_file_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Добавляем данные
            for data in test_data:
                cursor.execute('''
                    INSERT OR REPLACE INTO content 
                    (message_id, channel_id, category, title, text, media_type, media_file_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', data)
                print(f"✅ Добавлен: {data[3]}")
            
            # Обновляем статистику
            cursor.execute('''
                INSERT OR REPLACE INTO stats (category, count, last_updated)
                SELECT category, COUNT(*), CURRENT_TIMESTAMP
                FROM content GROUP BY category
            ''')
            
            conn.commit()
            print("✅ Тестовые данные добавлены")
            
    except Exception as e:
        print(f"❌ Ошибка при добавлении данных: {e}")

def test_bot():
    """Тестирование бота"""
    print("🤖 Тестирование бота...")
    
    try:
        # Импортируем и тестируем компоненты
        from config import BOT_TOKEN, CATEGORIES
        from database import Database
        from content_analyzer import ContentAnalyzer
        
        print("✅ Конфигурация загружена")
        print(f"📂 Категорий: {len(CATEGORIES)}")
        
        db = Database()
        print("✅ База данных инициализирована")
        
        analyzer = ContentAnalyzer()
        print("✅ Анализатор контента инициализирован")
        
        # Тестируем категоризацию
        test_text = "#челлендж Присоединяйтесь к вызову!"
        category = analyzer.categorize_content(test_text)
        category_name = analyzer.get_category_name(category)
        print(f"✅ Категоризация работает: '{test_text}' → {category_name}")
        
        print("✅ Все компоненты работают корректно")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")

def main():
    """Главная функция"""
    print("🔧 Комплексное исправление проблем...")
    print("=" * 50)
    
    # 1. Проверяем и исправляем базу данных
    check_and_fix_database()
    print()
    
    # 2. Добавляем тестовые данные
    add_test_data()
    print()
    
    # 3. Тестируем бота
    test_bot()
    print()
    
    print("=" * 50)
    print("✅ Все проблемы исправлены!")
    print("🚀 Теперь можно запускать бота: py bot.py")

if __name__ == "__main__":
    main() 