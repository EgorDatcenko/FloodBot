#!/usr/bin/env python3
"""
Тестовый скрипт для проверки обработки медиа после очистки базы данных
"""

from database import Database
from content_analyzer import ContentAnalyzer

def test_empty_database():
    """Тестирование пустой базы данных"""
    print("🧪 Тестирование пустой базы данных...")
    
    db = Database()
    
    # Проверяем, что база пуста
    total_posts = db.get_total_posts_count()
    real_stats = db.get_real_stats()
    
    print(f"📊 Статистика базы данных:")
    print(f"   Всего постов: {total_posts}")
    print(f"   Категорий: {len(real_stats)}")
    
    if total_posts == 0:
        print("   ✅ База данных пуста и готова к тестированию")
        return True
    else:
        print("   ❌ База данных не пуста!")
        return False

def test_media_analyzer():
    """Тестирование анализатора медиа"""
    print("\n🧪 Тестирование анализатора медиа...")
    
    analyzer = ContentAnalyzer()
    
    # Создаем тестовое сообщение (заглушка)
    class MockMessage:
        def __init__(self):
            self.text = "Тестовый пост с #мем"
            self.photo = [MockPhoto()]
            self.media_group_id = "test_group_123"
        
        def hasattr(self, attr):
            return hasattr(self, attr)
    
    class MockPhoto:
        def __init__(self):
            self.file_id = "test_photo_id_123"
    
    # Тестируем извлечение медиа
    mock_message = MockMessage()
    
    print("📱 Тестирование extract_media_info:")
    media_type, media_file_id = analyzer.extract_media_info(mock_message)
    print(f"   Тип медиа: {media_type}")
    print(f"   File ID: {media_file_id}")
    
    print("\n📱 Тестирование extract_all_media_info:")
    all_media = analyzer.extract_all_media_info(mock_message)
    print(f"   Всего медиа: {len(all_media)}")
    for i, (m_type, m_id) in enumerate(all_media, 1):
        print(f"   {i}. {m_type}: {m_id}")
    
    print("\n📱 Тестирование extract_text_content:")
    title, text = analyzer.extract_text_content(mock_message)
    print(f"   Заголовок: {title}")
    print(f"   Текст: {text}")
    
    print("\n📱 Тестирование categorize_content:")
    category = analyzer.categorize_content(text, title)
    category_name = analyzer.get_category_name(category)
    print(f"   Категория: {category} ({category_name})")

def test_database_methods():
    """Тестирование методов базы данных"""
    print("\n🧪 Тестирование методов базы данных...")
    
    db = Database()
    
    # Тестируем добавление контента
    print("📝 Тестирование добавления контента:")
    success = db.add_content(
        message_id=12345,
        channel_id=-1001234567890,
        channel_username="test_channel",
        category="memes",
        title="Тестовый мем",
        text="Это тестовый мем для проверки #мем",
        media_type="photo",
        media_file_id="test_photo_id_123"
    )
    print(f"   Результат добавления: {'✅ Успешно' if success else '❌ Ошибка'}")
    
    # Проверяем, что пост добавился
    total_posts = db.get_total_posts_count()
    print(f"   Постов в базе: {total_posts}")
    
    # Тестируем получение поста
    post = db.get_content_by_message_id(12345)
    if post:
        print(f"   ✅ Пост найден: {post.get('title', 'Без заголовка')}")
    else:
        print("   ❌ Пост не найден")
    
    # Тестируем получение по категории
    posts = db.get_content_by_category("memes", limit=5)
    print(f"   Постов в категории 'memes': {len(posts)}")
    
    # Тестируем статистику
    stats = db.get_real_stats()
    print(f"   Статистика: {stats}")

def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ ОБРАБОТКИ МЕДИА ПОСЛЕ ОЧИСТКИ БАЗЫ ДАННЫХ")
    print("=" * 70)
    
    # Проверяем, что база пуста
    if not test_empty_database():
        print("\n❌ База данных не пуста! Очистите её перед тестированием.")
        return
    
    # Тестируем анализатор медиа
    test_media_analyzer()
    
    # Тестируем методы базы данных
    test_database_methods()
    
    print("\n✅ Тестирование завершено!")
    print("\n💡 Теперь можете запустить бота и протестировать ручную загрузку постов:")

if __name__ == "__main__":
    main() 