#!/usr/bin/env python3
"""
Скрипт для очистки базы данных
"""

import os
import sqlite3
import time

def clear_database():
    """Очистка базы данных от блокировок"""
    db_path = "content_bot.db"
    
    print("🧹 Очистка базы данных...")
    
    # Проверяем, существует ли файл базы данных
    if os.path.exists(db_path):
        print(f"📁 Найден файл базы данных: {db_path}")
        
        # Пытаемся подключиться к базе данных
        try:
            with sqlite3.connect(db_path, timeout=60.0) as conn:
                cursor = conn.cursor()
                
                # Проверяем таблицы
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"📊 Найдено таблиц: {len(tables)}")
                
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"  📋 {table_name}: {count} записей")
                
                print("✅ База данных доступна и не заблокирована")
                
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print("⚠️ База данных заблокирована. Пытаюсь разблокировать...")
                
                # Ждем немного и пробуем снова
                time.sleep(5)
                
                try:
                    with sqlite3.connect(db_path, timeout=60.0) as conn:
                        print("✅ База данных разблокирована")
                except Exception as e2:
                    print(f"❌ Не удалось разблокировать базу данных: {e2}")
                    print("💡 Попробуйте перезапустить все скрипты")
            else:
                print(f"❌ Ошибка базы данных: {e}")
        except Exception as e:
            print(f"❌ Ошибка при работе с базой данных: {e}")
    else:
        print("ℹ️ Файл базы данных не найден. Он будет создан при первом запуске.")

if __name__ == "__main__":
    clear_database() 