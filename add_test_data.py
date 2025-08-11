#!/usr/bin/env python3
"""
Скрипт для добавления тестовых данных в базу
"""

from database import Database
from content_analyzer import ContentAnalyzer

def add_test_data():
    """Добавление тестовых данных"""
    print("📝 Добавление тестовых данных...")
    
    db = Database()
    analyzer = ContentAnalyzer()
    
    # Тестовые данные с хештегами #челлендж
    test_messages = [
        {
            'message_id': 1,
            'chat_id': -100123456789,
            'title': 'Челлендж дня',
            'text': 'Присоединяйтесь к вызову #челлендж 💪',
            'category': 'challenges'
        },
        {
            'message_id': 2,
            'chat_id': -100123456789,
            'title': 'Новый челлендж',
            'text': 'Новый челлендж на этой неделе! #челендж #вызов #фитнес',
            'category': 'challenges'
        },
        {
            'message_id': 3,
            'chat_id': -100123456789,
            'title': 'Челлендж "Щелкунчик"',
            'text': '---------- ⚠️ ЧЕЛЕНДЖ ⚠️ ----------\n"Щелкунчик"\nИНВЕНТАРЬ:\n- ГРЕЦКИЕ ОРЕХИ (🌰)\n- ПАЛЬЦЫ (большой/ср/указат)\nНЕ ЗАБЫВАЕМ:\n"Мужички, кому не слабо, жду от вас [ВИДОСЫ] и [Ответные ЗАДАНИЯ] в комменты! #челендж"',
            'category': 'challenges'
        },
        {
            'message_id': 4,
            'chat_id': -100123456789,
            'title': 'Мой рекорд',
            'text': 'Новый рекорд в жиме лежа! #результаты #сила',
            'category': 'power_results'
        },
        {
            'message_id': 5,
            'chat_id': -100123456789,
            'title': 'Совет по технике',
            'text': 'Как правильно делать приседания #советы #техника',
            'category': 'sport_tips'
        },
        {
            'message_id': 6,
            'chat_id': -100123456789,
            'title': 'Упражнение дня',
            'text': 'Техника выполнения приседаний #упражнения #фитнес',
            'category': 'exercises'
        },
        {
            'message_id': 7,
            'chat_id': -100123456789,
            'title': 'Мем из зала',
            'text': 'Забавная ситуация в спортзале #мемы #юмор',
            'category': 'memes'
        }
    ]
    
    for msg in test_messages:
        success = db.add_content(
            message_id=msg['message_id'],
            channel_id=msg['chat_id'],
            category=msg['category'],
            title=msg['title'],
            text=msg['text'],
            media_type=None,
            media_file_id=None
        )
        if success:
            category_name = analyzer.get_category_name(msg['category'])
            print(f"✅ Добавлен: {msg['title']} → {category_name}")
        else:
            print(f"❌ Ошибка при добавлении: {msg['title']}")
    
    # Показываем статистику
    print("\n📊 Статистика:")
    stats = db.get_stats()
    if stats:
        total = sum(stats.values())
        print(f"Всего записей: {total}")
        for category, count in stats.items():
            category_name = analyzer.get_category_name(category)
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  {category_name}: {count} ({percentage:.1f}%)")
    else:
        print("База данных пуста")

if __name__ == "__main__":
    add_test_data() 