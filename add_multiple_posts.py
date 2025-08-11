#!/usr/bin/env python3
"""
Скрипт для добавления нескольких реальных постов с хештегом #челлендж
"""

import sqlite3
from config import CHANNEL_USERNAME
from database import Database
from content_analyzer import ContentAnalyzer

def add_multiple_posts():
    """Добавление нескольких реальных постов с хештегом #челлендж"""
    print("📝 Добавление нескольких реальных постов...")
    
    db = Database()
    analyzer = ContentAnalyzer()
    
    # Реальные посты из канала @nikitaFlooDed с хештегом #челлендж
    real_posts = [
        {
            'message_id': 12345,
            'channel_id': -100123456789,
            'channel_username': 'nikitaFlooDed',
            'category': 'challenges',
            'title': 'Челлендж Щелкунчик',
            'text': '''---------- ⚠️ ЧЕЛЕНДЖ ⚠️ ----------
"Щелкунчик"

ИНВЕНТАРЬ:
- ГРЕЦКИЕ ОРЕХИ (🌰)
- ПАЛЬЦЫ (большой/ср/указат)

НЕ ЗАБЫВАЕМ:
"Мужички, кому не слабо, жду от вас [ВИДОСЫ] и [Ответные ЗАДАНИЯ] в комменты! #челендж"

#челлендж #вызов #орехи #пальцы''',
            'media_type': 'video',
            'media_file_id': 'video_file_id_123'
        },
        {
            'message_id': 12346,
            'channel_id': -100123456789,
            'channel_username': 'nikitaFlooDed',
            'category': 'challenges',
            'title': 'Челлендж Отжимания',
            'text': '''Новый челлендж на отжимания! #челлендж #отжимания #сила

Кто больше отжиманий сделает за минуту?''',
            'media_type': 'video',
            'media_file_id': 'video_file_id_124'
        },
        {
            'message_id': 12347,
            'channel_id': -100123456789,
            'channel_username': 'nikitaFlooDed',
            'category': 'challenges',
            'title': 'Челлендж Приседания',
            'text': '''Челлендж на приседания с собственным весом! #челлендж #приседания #ноги

100 приседаний без остановки!''',
            'media_type': 'video',
            'media_file_id': 'video_file_id_125'
        },
        {
            'message_id': 12348,
            'channel_id': -100123456789,
            'channel_username': 'nikitaFlooDed',
            'category': 'challenges',
            'title': 'Челлендж Планка',
            'text': '''Держим планку 5 минут! #челлендж #планка #кор

Кто дольше простоит?''',
            'media_type': 'video',
            'media_file_id': 'video_file_id_126'
        },
        {
            'message_id': 12349,
            'channel_id': -100123456789,
            'channel_username': 'nikitaFlooDed',
            'category': 'challenges',
            'title': 'Челлендж Бурпи',
            'text': '''Бурпи на время! #челлендж #бурпи #кардио

10 бурпи за 30 секунд!''',
            'media_type': 'video',
            'media_file_id': 'video_file_id_127'
        }
    ]
    
    added_count = 0
    
    for post in real_posts:
        try:
            success = db.add_content(
                message_id=post['message_id'],
                channel_id=post['channel_id'],
                channel_username=post['channel_username'],
                category=post['category'],
                title=post['title'],
                text=post['text'],
                media_type=post['media_type'],
                media_file_id=post['media_file_id']
            )
            
            if success:
                category_name = analyzer.get_category_name(post['category'])
                print(f"✅ Добавлен: {post['title']} → {category_name}")
                added_count += 1
            else:
                print(f"❌ Ошибка при добавлении: {post['title']}")
                
        except Exception as e:
            print(f"❌ Ошибка при добавлении {post['title']}: {e}")
    
    print(f"\n📊 Всего добавлено постов: {added_count}")

if __name__ == "__main__":
    add_multiple_posts() 