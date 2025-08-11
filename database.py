import sqlite3
import json
import time
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path: str = "content_bot.db"):
        self.db_path = db_path
        self.init_database()
        # Дополнительно инициализируем таблицу для медиафайлов
        self.init_media_table()
    
    def init_database(self):
        """Инициализация базы данных"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                
                # Проверяем, существует ли таблица content
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='content'")
                table_exists = cursor.fetchone() is not None
                
                if table_exists:
                    # Проверяем, есть ли колонка media_file_unique_id
                    cursor.execute("PRAGMA table_info(content)")
                    columns = [column[1] for column in cursor.fetchall()]
                    
                    if 'media_file_unique_id' not in columns:
                        # Добавляем новую колонку
                        cursor.execute('ALTER TABLE content ADD COLUMN media_file_unique_id TEXT')
                        print("✅ Добавлена колонка media_file_unique_id в таблицу content")
                    
                    if 'media_group_id' not in columns:
                        # Добавляем новую колонку
                        cursor.execute('ALTER TABLE content ADD COLUMN media_group_id TEXT')
                        print("✅ Добавлена колонка media_group_id в таблицу content")
                else:
                    # Создаем новую таблицу с поддержкой media_file_unique_id
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS content (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            message_id INTEGER UNIQUE,
                            channel_id INTEGER,
                            channel_username TEXT,
                            category TEXT,
                            title TEXT,
                            text TEXT,
                            media_type TEXT,
                            media_file_id TEXT,
                            media_file_unique_id TEXT,
                            media_group_id TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    print("✅ Создана таблица content с поддержкой media_file_unique_id")
                
                # Таблица для хранения статистики
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT,
                        count INTEGER DEFAULT 0,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                
        except Exception as e:
            print(f"Ошибка при инициализации базы данных: {e}")
    
    def add_content(self, message_id: int, channel_id: int, category: str, 
                   title: str = "", text: str = "", media_type: str = None, 
                   media_file_id: str = None, media_file_unique_id: str = None, 
                   channel_username: str = None, media_group_id: str = None) -> bool:
        """Добавление нового контента в базу данных"""
        max_retries = 10
        for attempt in range(max_retries):
            try:
                with sqlite3.connect(self.db_path, timeout=60.0) as conn:
                    cursor = conn.cursor()
                    
                    # Проверяем, существует ли уже пост с таким message_id или media_group_id
                    existing_content = None
                    if media_group_id:
                        cursor.execute('''
                            SELECT id, message_id FROM content 
                            WHERE media_group_id = ? OR message_id = ?
                        ''', (media_group_id, message_id))
                        existing_content = cursor.fetchone()
                    else:
                        cursor.execute('''
                            SELECT id, message_id FROM content 
                            WHERE message_id = ?
                        ''', (message_id,))
                        existing_content = cursor.fetchone()
                    
                    if existing_content:
                        # Обновляем существующий пост
                        content_id = existing_content[0]
                        cursor.execute('''
                            UPDATE content 
                            SET channel_id = ?, channel_username = ?, category = ?, 
                                title = ?, text = ?, media_type = ?, media_file_id = ?, 
                                media_file_unique_id = ?, media_group_id = ?
                            WHERE id = ?
                        ''', (channel_id, channel_username, category, title, text, 
                              media_type, media_file_id, media_file_unique_id, media_group_id, content_id))
                    else:
                        # Создаем новый пост
                        cursor.execute('''
                            INSERT INTO content 
                            (message_id, channel_id, channel_username, category, title, text, 
                             media_type, media_file_id, media_file_unique_id, media_group_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (message_id, channel_id, channel_username, category, title, text, 
                              media_type, media_file_id, media_file_unique_id, media_group_id))
                    
                    conn.commit()
                    
                    # Обновляем статистику в отдельном соединении
                    try:
                        self.update_stats(category)
                    except Exception as e:
                        print(f"Предупреждение: не удалось обновить статистику: {e}")
                    
                    return True
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    print(f"База данных заблокирована, попытка {attempt + 1}/{max_retries}")
                    import time
                    time.sleep(2)  # Увеличиваем время ожидания
                    continue
                else:
                    print(f"Ошибка при добавлении контента: {e}")
                    return False
            except Exception as e:
                print(f"Ошибка при добавлении контента: {e}")
                return False
        return False
    
    def get_content_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """Получение контента по категории"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM content 
                    WHERE category = ? 
                    ORDER BY created_at ASC 
                    LIMIT ?
                ''', (category, limit))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Ошибка при получении контента по категории: {e}")
            return []
    
    def get_content_by_message_id(self, message_id: int) -> Optional[Dict]:
        """Получение контента по message_id"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM content 
                    WHERE message_id = ?
                ''', (message_id,))
                
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            print(f"Ошибка при получении контента по message_id: {e}")
            return None
    
    def get_all_categories(self) -> List[str]:
        """Получение всех категорий с количеством контента"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT category, COUNT(*) as count 
                    FROM content 
                    GROUP BY category 
                    ORDER BY count DESC
                ''')
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении категорий: {e}")
            return []
    
    def search_content(self, query: str, limit: int = 10) -> List[Dict]:
        """Поиск контента по тексту"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM content 
                    WHERE text LIKE ? OR title LIKE ?
                    ORDER BY created_at ASC 
                    LIMIT ?
                ''', (f'%{query}%', f'%{query}%', limit))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Ошибка при поиске контента: {e}")
            return []
    
    def update_stats(self, category: str):
        """Обновление статистики по категории"""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO stats (category, count, last_updated)
                        SELECT ?, COUNT(*), CURRENT_TIMESTAMP
                        FROM content WHERE category = ?
                    ''', (category, category))
                    conn.commit()
                    return
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    print(f"База данных заблокирована при обновлении статистики, попытка {attempt + 1}/{max_retries}")
                    import time
                    time.sleep(1)
                    continue
                else:
                    print(f"Ошибка при обновлении статистики: {e}")
                    break
    
    def get_stats(self) -> Dict[str, int]:
        """Получение статистики по всем категориям"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT category, count FROM stats ORDER BY count DESC')
                return dict(cursor.fetchall())
        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
            return {} 
    
    def get_real_stats(self) -> Dict[str, int]:
        """Получение актуальной статистики напрямую из таблицы content"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT category, COUNT(*) as count 
                    FROM content 
                    GROUP BY category 
                    ORDER BY count DESC
                ''')
                return dict(cursor.fetchall())
        except Exception as e:
            print(f"Ошибка при получении актуальной статистики: {e}")
            return {}
    
    def get_total_posts_count(self) -> int:
        """Получение общего количества постов"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM content')
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"Ошибка при получении количества постов: {e}")
            return 0
    
    def update_all_stats(self):
        """Обновление статистики для всех категорий"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                
                # Получаем актуальную статистику
                cursor.execute('''
                    SELECT category, COUNT(*) as count 
                    FROM content 
                    GROUP BY category
                ''')
                categories = cursor.fetchall()
                
                # Обновляем таблицу stats
                for category, count in categories:
                    cursor.execute('''
                        INSERT OR REPLACE INTO stats (category, count, last_updated)
                        VALUES (?, ?, CURRENT_TIMESTAMP)
                    ''', (category, count))
                
                conn.commit()
                print(f"✅ Статистика обновлена для {len(categories)} категорий")
                
        except Exception as e:
            print(f"Ошибка при обновлении статистики: {e}")

    def delete_content_by_title(self, title: str) -> int:
        """Удаляет посты по заголовку (title). Возвращает количество удалённых записей."""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM content WHERE LOWER(title) LIKE ?', (f'%{title.lower()}%',))
                deleted = cursor.rowcount
                conn.commit()
                return deleted
        except Exception as e:
            print(f"Ошибка при удалении поста: {e}")
            return 0 

    def delete_content_by_id(self, content_id: int) -> bool:
        """Удаляет пост по ID. Возвращает True если удалён."""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM content WHERE id = ?', (content_id,))
                deleted = cursor.rowcount
                conn.commit()
                return deleted > 0
        except Exception as e:
            print(f"Ошибка при удалении поста: {e}")
            return False 
    
    def get_content_with_media(self, limit: int = 100) -> List[Dict]:
        """Получение контента с медиа файлами"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM content 
                    WHERE media_type IS NOT NULL AND media_file_id IS NOT NULL
                    ORDER BY created_at ASC 
                    LIMIT ?
                ''', (limit,))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Ошибка при получении контента с медиа: {e}")
            return []
    
    def get_content_by_media_type(self, media_type: str, limit: int = 10) -> List[Dict]:
        """Получение контента по типу медиа"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM content 
                    WHERE media_type = ? AND media_file_id IS NOT NULL
                    ORDER BY created_at ASC 
                    LIMIT ?
                ''', (media_type, limit))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Ошибка при получении контента по типу медиа: {e}")
            return []
    
    def get_content_by_media_group_id(self, media_group_id: str) -> Optional[Dict]:
        """Получение контента по media_group_id"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM content 
                    WHERE media_group_id = ?
                ''', (media_group_id,))
                
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            print(f"Ошибка при получении контента по media_group_id: {e}")
            return None 
    
    def init_media_table(self):
        """Инициализация таблицы для медиафайлов"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                
                # Создаем таблицу post_media если её нет
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS post_media (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content_id INTEGER,
                        message_id INTEGER,
                        media_type TEXT,
                        media_file_id TEXT,
                        media_file_unique_id TEXT,
                        media_order INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (content_id) REFERENCES content (id) ON DELETE CASCADE
                    )
                ''')
                
                conn.commit()
                print("✅ Таблица post_media готова к работе")
        except Exception as e:
            print(f"Ошибка при инициализации таблицы post_media: {e}")
    
    def add_media_to_post(self, content_id: int, message_id: int, media_type: str, 
                          media_file_id: str, media_file_unique_id: str = None, 
                          media_order: int = 0) -> bool:
        """Добавление медиафайла к посту"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO post_media 
                    (content_id, message_id, media_type, media_file_id, media_file_unique_id, media_order)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (content_id, message_id, media_type, media_file_id, media_file_unique_id, media_order))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка при добавлении медиафайла: {e}")
            return False
    
    def get_post_media(self, content_id: int) -> List[Dict]:
        """Получение всех медиафайлов для поста"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM post_media 
                    WHERE content_id = ?
                    ORDER BY media_order ASC
                ''', (content_id,))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Ошибка при получении медиафайлов поста: {e}")
            return []
    
    def get_content_with_media_files(self, category: str = None, limit: int = 10) -> List[Dict]:
        """Получение контента с медиафайлами"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                
                if category:
                    cursor.execute('''
                        SELECT c.*, pm.media_type, pm.media_file_id, pm.media_order
                        FROM content c
                        LEFT JOIN post_media pm ON c.id = pm.content_id
                        WHERE c.category = ?
                        ORDER BY c.created_at ASC, pm.media_order ASC
                        LIMIT ?
                    ''', (category, limit * 10))  # Увеличиваем лимит, так как JOIN может дать больше строк
                else:
                    cursor.execute('''
                        SELECT c.*, pm.media_type, pm.media_file_id, pm.media_order
                        FROM content c
                        LEFT JOIN post_media pm ON c.id = pm.content_id
                        ORDER BY c.created_at ASC, pm.media_order ASC
                        LIMIT ?
                    ''', (limit * 10,))  # Увеличиваем лимит, так как JOIN может дать больше строк
                
                columns = [description[0] for description in cursor.description]
                raw_results = cursor.fetchall()
                
                # Группируем результаты по content_id
                content_dict = {}
                
                for row in raw_results:
                    row_dict = dict(zip(columns, row))
                    content_id = row_dict['id']
                    
                    if content_id not in content_dict:
                        # Создаем новый пост
                        content_dict[content_id] = {
                            'id': content_id,
                            'message_id': row_dict['message_id'],
                            'channel_id': row_dict['channel_id'],
                            'channel_username': row_dict['channel_username'],
                            'category': row_dict['category'],
                            'title': row_dict['title'],
                            'text': row_dict['text'],
                            'media_type': row_dict['media_type'],
                            'media_file_id': row_dict['media_file_id'],
                            'media_file_unique_id': row_dict['media_file_unique_id'],
                            'media_group_id': row_dict['media_group_id'],
                            'created_at': row_dict['created_at'],
                            'media_files': []
                        }
                    
                    # Добавляем медиафайл, если он есть
                    if row_dict['media_type'] and row_dict['media_file_id']:
                        media_file = {
                            'media_type': row_dict['media_type'],
                            'media_file_id': row_dict['media_file_id'],
                            'media_order': row_dict['media_order'] or 0
                        }
                        content_dict[content_id]['media_files'].append(media_file)
                
                # Если медиафайлов нет в post_media, добавляем из основной таблицы
                for content_id, post in content_dict.items():
                    if not post['media_files']:
                        # Проверяем, есть ли медиа в основной таблице
                        main_media_type = post.get('media_type')
                        main_media_file_id = post.get('media_file_id')
                        
                        if main_media_type and main_media_file_id:
                            # Добавляем медиа из основной таблицы
                            post['media_files'] = [{
                                'media_type': main_media_type,
                                'media_file_id': main_media_file_id,
                                'media_order': 0
                            }]
                            print(f"📱 Добавлен медиафайл из основной таблицы для поста {content_id}: {main_media_type}")
                
                # Сортируем медиафайлы по порядку и ограничиваем количество постов
                results = []
                for content_id, post in content_dict.items():
                    # Сортируем медиафайлы по порядку
                    post['media_files'].sort(key=lambda x: x['media_order'])
                    results.append(post)
                
                # Сортируем посты по времени создания и ограничиваем количество
                results.sort(key=lambda x: x['created_at'], reverse=False)
                results = results[:limit]
                
                return results
        except Exception as e:
            print(f"Ошибка при получении контента с медиафайлами: {e}")
            return [] 