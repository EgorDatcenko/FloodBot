import sqlite3
from database import Database

def clear_database_sql():
    """Очистка базы данных через SQL"""
    db = Database()
    
    print("🗑️ Очистка базы данных через SQL...")
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
        # Подключаемся к базе данных
        with sqlite3.connect(db.db_path, timeout=30.0) as conn:
            cursor = conn.cursor()
            
            # Очищаем таблицу content
            cursor.execute('DELETE FROM content')
            deleted_count = cursor.rowcount
            
            # Очищаем таблицу stats
            cursor.execute('DELETE FROM stats')
            
            # Сохраняем изменения
            conn.commit()
            
            print(f"✅ Удалено {deleted_count} постов из базы данных!")
            print("🔄 Теперь можешь переслать посты заново в ЛС боту")
        
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")

if __name__ == "__main__":
    clear_database_sql() 