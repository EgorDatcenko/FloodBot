#!/usr/bin/env python3
"""
Скрипт для очистки базы данных бота
"""

import sqlite3
import os
from database import Database

def clear_database():
    """Полная очистка базы данных"""
    db_path = "content_bot.db"
    
    if not os.path.exists(db_path):
        print("❌ База данных не найдена")
        return
    
    try:
        # Подключаемся к базе данных
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Получаем количество записей перед удалением
            cursor.execute("SELECT COUNT(*) FROM content")
            content_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM stats")
            stats_count = cursor.fetchone()[0]
            
            print(f"📊 Найдено записей:")
            print(f"   • Контент: {content_count}")
            print(f"   • Статистика: {stats_count}")
            
            if content_count == 0 and stats_count == 0:
                print("✅ База данных уже пуста")
                return
            
            # Удаляем все записи
            cursor.execute("DELETE FROM content")
            cursor.execute("DELETE FROM stats")
            
            # Сбрасываем автоинкремент
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='content'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='stats'")
            
            conn.commit()
            
            print(f"✅ База данных очищена!")
            print(f"   • Удалено записей контента: {content_count}")
            print(f"   • Удалено записей статистики: {stats_count}")
            
    except Exception as e:
        print(f"❌ Ошибка при очистке базы данных: {e}")

def show_database_info():
    """Показать информацию о базе данных"""
    db_path = "content_bot.db"
    
    if not os.path.exists(db_path):
        print("❌ База данных не найдена")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Получаем статистику
            cursor.execute("SELECT COUNT(*) FROM content")
            content_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT category, COUNT(*) FROM content GROUP BY category")
            categories = cursor.fetchall()
            
            print(f"📊 Информация о базе данных:")
            print(f"   • Всего записей: {content_count}")
            print(f"   • Категории:")
            
            for category, count in categories:
                print(f"     - {category}: {count} записей")
                
    except Exception as e:
        print(f"❌ Ошибка при получении информации: {e}")

if __name__ == "__main__":
    print("🗑️ Очистка базы данных бота")
    print("=" * 40)
    
    # Показываем текущую информацию
    show_database_info()
    print()
    
    # Спрашиваем подтверждение
    response = input("❓ Вы уверены, что хотите очистить базу данных? (y/N): ")
    
    if response.lower() in ['y', 'yes', 'да', 'д']:
        clear_database()
    else:
        print("❌ Операция отменена") 