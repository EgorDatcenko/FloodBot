#!/usr/bin/env python3
"""
Скрипт для добавления одного реального поста для тестирования
"""

import sqlite3
from config import CHANNEL_USERNAME
from database import Database
from content_analyzer import ContentAnalyzer

def add_real_post():
    """Добавление одного реального поста для тестирования"""
    print("📝 Добавление реального поста для тестирования...")
    
    db = Database()
    analyzer = ContentAnalyzer()
    
    # Реальные данные из канала @nikitaFlooDed
    real_post = {
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
    }
    
    try:
        success = db.add_content(
            message_id=real_post['message_id'],
            channel_id=real_post['channel_id'],
            channel_username=real_post['channel_username'],
            category=real_post['category'],
            title=real_post['title'],
            text=real_post['text'],
            media_type=real_post['media_type'],
            media_file_id=real_post['media_file_id']
        )
        
        if success:
            category_name = analyzer.get_category_name(real_post['category'])
            print(f"✅ Реальный пост добавлен: {real_post['title']} → {category_name}")
            print(f"📝 Текст: {real_post['text'][:100]}...")
            print(f"📎 Медиа: {real_post['media_type']}")
        else:
            print("❌ Ошибка при добавлении поста")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    add_real_post() 