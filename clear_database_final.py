import os
from database import Database

def clear_database_final():
    """Полная очистка базы данных"""
    db = Database()
    
    print("🗑️ Очистка базы данных...")
    print("=" * 50)
    
    # Получаем статистику перед очисткой
    stats = db.get_stats()
    total_posts = sum(stats.values()) if stats else 0
    
    print(f"📊 Постов в базе: {total_posts}")
    
    if total_posts == 0:
        print("✅ База данных уже пуста!")
        return
    
    # Показываем количество постов по категориям
    print("\n📋 По категориям:")
    for category, count in stats.items():
        print(f"   {category}: {count}")
    
    print(f"\n⚠️ Удаляю ВСЕ {total_posts} постов...")
    
    try:
        # Удаляем файл базы данных
        if os.path.exists(db.db_path):
            os.remove(db.db_path)
            print("🗑️ Файл базы данных удален")
        
        # Пересоздаем таблицы
        db.init_database()
        
        print("✅ База данных успешно очищена!")
        print("🔄 Теперь можешь переслать посты заново в ЛС боту")
        
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")

if __name__ == "__main__":
    clear_database_final() 