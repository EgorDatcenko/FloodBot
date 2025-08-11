#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправлений медиа и порядка постов
"""

from database import Database
from content_analyzer import ContentAnalyzer

def test_order_fix():
    """Тестирование исправления порядка постов"""
    print("🧪 Тестирование исправления порядка постов...")
    
    db = Database()
    analyzer = ContentAnalyzer()
    
    # Тестируем порядок постов в разных категориях
    categories = ['memes', 'challenges', 'power_results', 'sport_tips', 'exercises', 'flood', 'other']
    
    for category in categories:
        print(f"\n📁 Категория: {analyzer.get_category_name(category)}")
        posts = db.get_content_by_category(category, limit=5)
        
        if posts:
            print(f"   Найдено постов: {len(posts)}")
            print("   Порядок постов (по дате создания):")
            for i, post in enumerate(posts, 1):
                created_at = post.get('created_at', 'Неизвестно')
                title = post.get('title', 'Без заголовка')[:30]
                print(f"   {i}. {created_at} - {title}...")
        else:
            print("   Постов не найдено")

def test_media_fix():
    """Тестирование исправления медиа"""
    print("\n🧪 Тестирование исправления медиа...")
    
    db = Database()
    
    # Получаем посты с медиа
    posts_with_media = db.get_content_with_media(limit=10)
    
    print(f"📊 Найдено постов с медиа: {len(posts_with_media)}")
    
    # Анализируем типы медиа
    media_types = {}
    for post in posts_with_media:
        media_type = post.get('media_type')
        if media_type:
            media_types[media_type] = media_types.get(media_type, 0) + 1
    
    print("\n📱 Статистика по типам медиа:")
    for media_type, count in media_types.items():
        print(f"   • {media_type}: {count}")
    
    # Проверяем дублирующие записи
    print("\n🔍 Проверка дублирующих записей:")
    message_ids = {}
    duplicates = 0
    
    for post in posts_with_media:
        message_id = post.get('message_id')
        if message_id in message_ids:
            duplicates += 1
            print(f"   ❌ Дублирующий message_id: {message_id}")
        else:
            message_ids[message_id] = 1
    
    if duplicates == 0:
        print("   ✅ Дублирующих записей не найдено")
    else:
        print(f"   ⚠️ Найдено дублирующих записей: {duplicates}")

def test_database_integrity():
    """Тестирование целостности базы данных"""
    print("\n🧪 Тестирование целостности базы данных...")
    
    db = Database()
    
    # Общая статистика
    total_posts = db.get_total_posts_count()
    real_stats = db.get_real_stats()
    
    print(f"📊 Общая статистика:")
    print(f"   Всего постов: {total_posts}")
    print(f"   Категорий: {len(real_stats)}")
    
    # Проверяем, что сумма по категориям равна общему количеству
    sum_by_category = sum(real_stats.values())
    if sum_by_category == total_posts:
        print("   ✅ Целостность данных: OK")
    else:
        print(f"   ❌ Ошибка целостности: {sum_by_category} != {total_posts}")

def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЙ МЕДИА И ПОРЯДКА ПОСТОВ")
    print("=" * 60)
    
    test_order_fix()
    test_media_fix()
    test_database_integrity()
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    main() 