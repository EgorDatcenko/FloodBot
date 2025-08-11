#!/usr/bin/env python3
"""
Скрипт для полной очистки базы данных постов
"""

import sqlite3
import os
from database import Database

def clear_posts_database():
    """Полная очистка базы данных постов"""
    db_path = "content_bot.db"
    
    if not os.path.exists(db_path):
        print("❌ База данных не найдена!")
        return
    
    print("🗑️ Начинаю очистку базы данных постов...")
    
    try:
        # Подключаемся к базе данных
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Получаем статистику перед очисткой
            cursor.execute("SELECT COUNT(*) FROM content")
            posts_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM stats")
            stats_count = cursor.fetchone()[0]
            
            print(f"📊 Найдено постов: {posts_count}")
            print(f"📊 Найдено записей статистики: {stats_count}")
            
            if posts_count == 0:
                print("✅ База данных уже пуста!")
                return
            
            # Подтверждение очистки
            confirm = input(f"\n⚠️ Вы уверены, что хотите удалить {posts_count} постов? (y/N): ")
            if confirm.lower() != 'y':
                print("❌ Очистка отменена!")
                return
            
            # Очищаем таблицу content
            cursor.execute("DELETE FROM content")
            deleted_posts = cursor.rowcount
            
            # Очищаем таблицу stats
            cursor.execute("DELETE FROM stats")
            deleted_stats = cursor.rowcount
            
            # Подтверждаем изменения
            conn.commit()
            
            print(f"✅ Удалено постов: {deleted_posts}")
            print(f"✅ Удалено записей статистики: {deleted_stats}")
            print("✅ База данных очищена!")
            
    except Exception as e:
        print(f"❌ Ошибка при очистке базы данных: {e}")

def reset_database():
    """Полный сброс базы данных (удаление и пересоздание)"""
    db_path = "content_bot.db"
    
    print("🔄 Начинаю полный сброс базы данных...")
    
    try:
        # Удаляем файл базы данных
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ Старый файл базы данных удален")
        
        # Создаем новую базу данных
        db = Database()
        db.init_database()
        print("✅ Новая база данных создана")
        
    except Exception as e:
        print(f"❌ Ошибка при сбросе базы данных: {e}")

def show_database_info():
    """Показать информацию о базе данных"""
    db_path = "content_bot.db"
    
    if not os.path.exists(db_path):
        print("❌ База данных не найдена!")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Информация о постах
            cursor.execute("SELECT COUNT(*) FROM content")
            posts_count = cursor.fetchone()[0]
            
            # Информация о категориях
            cursor.execute("SELECT category, COUNT(*) FROM content GROUP BY category")
            categories = cursor.fetchall()
            
            # Информация о медиа
            cursor.execute("SELECT COUNT(*) FROM content WHERE media_type IS NOT NULL")
            media_count = cursor.fetchone()[0]
            
            # Размер файла
            file_size = os.path.getsize(db_path)
            
            print("📊 ИНФОРМАЦИЯ О БАЗЕ ДАННЫХ:")
            print(f"   📁 Файл: {db_path}")
            print(f"   📏 Размер: {file_size} байт")
            print(f"   📝 Всего постов: {posts_count}")
            print(f"   🎬 Постов с медиа: {media_count}")
            print(f"   📁 Категорий: {len(categories)}")
            
            if categories:
                print("\n📁 По категориям:")
                for category, count in categories:
                    print(f"   • {category}: {count}")
            
    except Exception as e:
        print(f"❌ Ошибка при получении информации: {e}")

def main():
    """Основная функция"""
    print("🗑️ СКРИПТ ОЧИСТКИ БАЗЫ ДАННЫХ ПОСТОВ")
    print("=" * 50)
    
    while True:
        print("\nВыберите действие:")
        print("1. Показать информацию о базе данных")
        print("2. Очистить посты (оставить структуру)")
        print("3. Полный сброс базы данных")
        print("4. Выход")
        
        choice = input("\nВаш выбор (1-4): ").strip()
        
        if choice == '1':
            show_database_info()
        elif choice == '2':
            clear_posts_database()
        elif choice == '3':
            confirm = input("⚠️ Это удалит ВСЕ данные! Продолжить? (y/N): ")
            if confirm.lower() == 'y':
                reset_database()
            else:
                print("❌ Сброс отменен!")
        elif choice == '4':
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор!")

if __name__ == "__main__":
    main() 