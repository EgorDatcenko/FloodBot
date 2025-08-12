#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы Fitness Content Sorter Bot
"""

import asyncio
import logging
from config import BOT_TOKEN, CHANNEL_USERNAME
from database import Database
from content_analyzer import ContentAnalyzer

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def test_bot_functionality():
    """Тестирование основных функций бота"""
    
    print("🧪 Тестирование Fitness Content Sorter Bot...")
    
    # Инициализация компонентов
    db = Database()
    analyzer = ContentAnalyzer()
    
    # Тест 1: Проверка категоризации
    print("\n📋 Тест 1: Категоризация контента")
    
    test_cases = [
        ("#челлендж Присоединяйтесь к нашему вызову!", "challenges"),
        ("#результаты Мой новый рекорд!", "power_results"),
        ("#советы Как правильно делать приседания", "sport_tips"),
        ("#упражнения Техника приседаний", "exercises"),
        ("#мемы Забавная ситуация в зале", "memes"),
        ("Обычный пост без хештегов", "other")
    ]
    
    for text, expected_category in test_cases:
        category = analyzer.categorize_content(text)
        category_name = analyzer.get_category_name(category)
        status = "✅" if category == expected_category else "❌"
        print(f"{status} '{text[:30]}...' → {category_name}")
    
    # Тест 2: Проверка базы данных
    print("\n🗄️ Тест 2: База данных")
    
    # Добавляем тестовые данные
    test_data = [
        (1, -100123456789, "challenges", "Челлендж дня", "Присоединяйтесь к вызову #челлендж", None, None),
        (2, -100123456789, "power_results", "Мой рекорд", "Новый рекорд в жиме #результаты", None, None),
        (3, -100123456789, "sport_tips", "Совет по технике", "Правильная техника приседаний #советы", None, None),
        (4, -100123456789, "exercises", "Упражнение дня", "Техника выполнения #упражнения", None, None),
        (5, -100123456789, "memes", "Мем из зала", "Забавная ситуация #мемы", None, None),
    ]
    
    for data in test_data:
        success = db.add_content(*data)
        print(f"{'✅' if success else '❌'} Добавление записи {data[0]}")
    
    # Проверяем статистику
    stats = db.get_stats()
    print(f"📊 Статистика: {len(stats)} категорий")
    for category, count in stats.items():
        category_name = analyzer.get_category_name(category)
        print(f"  {category_name}: {count}")
    
    # Тест 3: Проверка поиска
    print("\n🔍 Тест 3: Поиск контента")
    
    search_results = db.search_content("челлендж", limit=5)
    print(f"Найдено {len(search_results)} результатов по запросу 'челлендж'")
    
    # Тест 4: Проверка хештегов
    print("\n🏷️ Тест 4: Хештеги")
    
    for category_key in ['challenges', 'power_results', 'sport_tips', 'exercises', 'memes']:
        hashtags = analyzer.get_hashtags_for_category(category_key)
        category_name = analyzer.get_category_name(category_key)
        print(f"  {category_name}: {' '.join(hashtags)}")
    
    print("\n✅ Тестирование завершено!")

def test_config():
    """Проверка конфигурации"""
    print("\n⚙️ Проверка конфигурации:")
    
    if BOT_TOKEN:
        print("✅ BOT_TOKEN настроен")
    else:
        print("❌ BOT_TOKEN не найден")
    
    print(f"📢 Канал: {CHANNEL_USERNAME}")
    
    from config import CATEGORIES, CATEGORY_KEYWORDS, CATEGORY_HASHTAGS
    print(f"📂 Категорий: {len(CATEGORIES)}")
    print(f"🔑 Ключевых слов: {len(CATEGORY_KEYWORDS)}")
    print(f"🏷️ Хештегов: {len(CATEGORY_HASHTAGS)}")

if __name__ == "__main__":
    print("🚀 Запуск тестов Fitness Content Sorter Bot")
    
    # Проверка конфигурации
    test_config()
    
    # Запуск асинхронных тестов
    asyncio.run(test_bot_functionality()) 