#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправления статистики
"""

from database import Database
from content_analyzer import ContentAnalyzer

def test_stats_fix():
    """Тестирование исправления статистики"""
    print("🧪 Тестирование исправления статистики...")
    
    db = Database()
    analyzer = ContentAnalyzer()
    
    # Показываем старую статистику
    print("\n📊 СТАРАЯ СТАТИСТИКА (из таблицы stats):")
    old_stats = db.get_stats()
    old_total = sum(old_stats.values()) if old_stats else 0
    print(f"   Всего постов: {old_total}")
    for category, count in old_stats.items():
        category_name = analyzer.get_category_name(category)
        print(f"   • {category_name}: {count}")
    
    # Показываем актуальную статистику
    print("\n📊 АКТУАЛЬНАЯ СТАТИСТИКА (из таблицы content):")
    real_stats = db.get_real_stats()
    real_total = db.get_total_posts_count()
    print(f"   Всего постов: {real_total}")
    for category, count in real_stats.items():
        category_name = analyzer.get_category_name(category)
        print(f"   • {category_name}: {count}")
    
    # Обновляем статистику
    print("\n🔄 Обновляю статистику...")
    db.update_all_stats()
    
    # Показываем обновленную статистику
    print("\n📊 ОБНОВЛЕННАЯ СТАТИСТИКА:")
    updated_stats = db.get_stats()
    updated_total = sum(updated_stats.values()) if updated_stats else 0
    print(f"   Всего постов: {updated_total}")
    for category, count in updated_stats.items():
        category_name = analyzer.get_category_name(category)
        print(f"   • {category_name}: {count}")
    
    # Проверяем, совпадают ли данные
    print(f"\n✅ РЕЗУЛЬТАТ:")
    if real_total == updated_total:
        print(f"   ✅ Статистика обновлена корректно!")
        print(f"   📊 Актуальное количество постов: {real_total}")
    else:
        print(f"   ❌ Ошибка! Данные не совпадают:")
        print(f"      Реальное количество: {real_total}")
        print(f"      Обновленное количество: {updated_total}")

if __name__ == "__main__":
    test_stats_fix() 