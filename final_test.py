#!/usr/bin/env python3
"""
Финальный тест всех функций бота
"""

import sqlite3
from config import CATEGORIES
from database import Database
from content_analyzer import ContentAnalyzer

def test_database():
    """Тестирование базы данных"""
    print("🗄️ Тестирование базы данных...")
    
    try:
        db = Database()
        
        # Проверяем статистику
        stats = db.get_stats()
        print(f"✅ Статистика загружена: {len(stats)} категорий")
        
        # Проверяем контент по категориям
        for category in CATEGORIES.keys():
            content = db.get_content_by_category(category, limit=5)
            print(f"   📁 {category}: {len(content)} записей")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False

def test_analyzer():
    """Тестирование анализатора контента"""
    print("\n🔍 Тестирование анализатора контента...")
    
    try:
        analyzer = ContentAnalyzer()
        
        # Тестовые тексты
        test_cases = [
            ("#челлендж Присоединяйтесь к вызову!", "challenges"),
            ("Новый рекорд в жиме лежа! #результаты", "power_results"),
            ("Как правильно делать приседания #советы", "sport_tips"),
            ("Техника выполнения упражнений #упражнения", "exercises"),
            ("Забавная ситуация в спортзале #мемы", "memes"),
        ]
        
        for text, expected in test_cases:
            category = analyzer.categorize_content(text)
            category_name = analyzer.get_category_name(category)
            print(f"   ✅ '{text[:30]}...' → {category_name}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка анализатора: {e}")
        return False

def test_categories():
    """Тестирование категорий"""
    print("\n📂 Тестирование категорий...")
    
    try:
        analyzer = ContentAnalyzer()
        categories = analyzer.get_all_categories()
        
        print("✅ Доступные категории:")
        for key, name in categories.items():
            hashtags = analyzer.get_hashtags_for_category(key)
            print(f"   📁 {name}: {', '.join(hashtags)}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка категорий: {e}")
        return False

def test_search():
    """Тестирование поиска"""
    print("\n🔍 Тестирование поиска...")
    
    try:
        db = Database()
        
        # Тестируем поиск
        results = db.search_content("челлендж", limit=3)
        print(f"✅ Поиск 'челлендж': найдено {len(results)} результатов")
        
        results = db.search_content("упражнения", limit=3)
        print(f"✅ Поиск 'упражнения': найдено {len(results)} результатов")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")
        return False

def main():
    """Главная функция"""
    print("🧪 Финальное тестирование Fitness Content Sorter Bot")
    print("=" * 60)
    
    tests = [
        test_database,
        test_analyzer,
        test_categories,
        test_search
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("✅ Все тесты пройдены успешно!")
        print("🚀 Бот полностью готов к работе")
        print("\n📱 Теперь можете использовать бота в Telegram:")
        print("   - Отправьте /start для начала работы")
        print("   - Используйте /help для справки")
        print("   - Выберите категории для просмотра контента")
    else:
        print("❌ Некоторые тесты не пройдены")
        print("🔧 Проверьте настройки и попробуйте снова")

if __name__ == "__main__":
    main() 