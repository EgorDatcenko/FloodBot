import re
import logging
from typing import Dict, List, Tuple
from config import CATEGORY_KEYWORDS, CATEGORIES, CATEGORY_HASHTAGS

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    def __init__(self):
        self.category_keywords = CATEGORY_KEYWORDS
        self.categories = CATEGORIES
        self.category_hashtags = CATEGORY_HASHTAGS
    
    def categorize_content(self, text: str, title: str = "") -> str:
        """
        Автоматическая категоризация контента на основе хештегов и ключевых слов
        """
        if not text and not title:
            return 'other'
        
        # Объединяем текст и заголовок для анализа
        full_text = f"{title} {text}".lower()
        
        # Сначала проверяем хештеги (приоритет выше)
        hashtag_category = self._categorize_by_hashtags(full_text)
        if hashtag_category:
            return hashtag_category
        
        # Затем проверяем ключевые слова
        keyword_category = self._categorize_by_keywords(full_text)
        if keyword_category:
            return keyword_category
        
        return 'other'
    
    def _categorize_by_hashtags(self, text: str) -> str:
        """
        Категоризация по хештегам (высший приоритет)
        """
        # Ищем все хештеги в тексте
        hashtags = re.findall(r'#\w+', text)
        
        if not hashtags:
            return None
        
        # Подсчитываем совпадения хештегов для каждой категории
        category_scores = {}
        
        for category, category_hashtags in self.category_hashtags.items():
            score = 0
            for hashtag in hashtags:
                if hashtag in category_hashtags:
                    score += 2  # Хештеги имеют больший вес
            if score > 0:
                category_scores[category] = score
        
        # Возвращаем категорию с наивысшим баллом
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return None
    
    def _categorize_by_keywords(self, text: str) -> str:
        """
        Категоризация по ключевым словам
        """
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                # Ищем точные совпадения слов
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, text)
                score += len(matches)
            
            if score > 0:
                category_scores[category] = score
        
        # Возвращаем категорию с наивысшим баллом
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return None
    
    def extract_hashtags(self, text: str) -> List[str]:
        """
        Извлечение всех хештегов из текста
        """
        return re.findall(r'#\w+', text.lower())
    
    def extract_media_info(self, message) -> Tuple[str, str]:
        """
        Извлечение информации о медиа из сообщения с улучшенной обработкой
        Возвращает: (media_type, media_file_id)
        """
        media_type = None
        media_file_id = None
        
        try:
            # Проверяем различные типы медиа в порядке приоритета
            if hasattr(message, 'media_group_id') and message.media_group_id:
                # Это часть медиа-группы - обрабатываем как единое целое
                logger.info(f"📱 Найдена медиа-группа: {message.media_group_id}")
                # Возвращаем тип основного медиа из группы
                if hasattr(message, 'photo') and message.photo:
                    media_type = 'photo'
                    media_file_id = message.photo[-1].file_id
                elif hasattr(message, 'video') and message.video:
                    media_type = 'video'
                    media_file_id = message.video.file_id
                elif hasattr(message, 'animation') and message.animation:
                    media_type = 'animation'
                    media_file_id = message.animation.file_id
                logger.info(f"📸 Медиа из группы: {media_type} - {media_file_id}")
            elif hasattr(message, 'photo') and message.photo:
                # Обычное фото (может быть несколько в одном сообщении)
                media_type = 'photo'
                media_file_id = message.photo[-1].file_id  # Берем самое качественное фото
                logger.info(f"📸 Найдено фото: {media_file_id}")
            elif hasattr(message, 'video') and message.video:
                media_type = 'video'
                media_file_id = message.video.file_id
                logger.info(f"🎥 Найдено видео: {media_file_id}")
            elif hasattr(message, 'animation') and message.animation:
                media_type = 'animation'
                media_file_id = message.animation.file_id
                logger.info(f"🎬 Найдена анимация: {media_file_id}")
            elif hasattr(message, 'audio') and message.audio:
                media_type = 'audio'
                media_file_id = message.audio.file_id
                logger.info(f"🎵 Найдено аудио: {media_file_id}")
            elif hasattr(message, 'document') and message.document:
                media_type = 'document'
                media_file_id = message.document.file_id
                logger.info(f"📄 Найден документ: {media_file_id}")
            elif hasattr(message, 'voice') and message.voice:
                media_type = 'voice'
                media_file_id = message.voice.file_id
                logger.info(f"🎤 Найдено голосовое: {media_file_id}")
            elif hasattr(message, 'video_note') and message.video_note:
                media_type = 'video_note'
                media_file_id = message.video_note.file_id
                logger.info(f"📹 Найдено видео-сообщение: {media_file_id}")
            elif hasattr(message, 'sticker') and message.sticker:
                media_type = 'sticker'
                media_file_id = message.sticker.file_id
                logger.info(f"😀 Найден стикер: {media_file_id}")
            else:
                logger.info("📝 Медиа не найдено")
                
        except Exception as e:
            logger.error(f"❌ Ошибка при извлечении медиа: {e}")
            media_type = None
            media_file_id = None
        
        return media_type, media_file_id
    
    def extract_all_media_info(self, message) -> List[Tuple[str, str]]:
        """
        Извлечение ВСЕХ медиа из сообщения (для медиа-групп)
        Возвращает: [(media_type, media_file_id), ...]
        """
        media_list = []
        
        try:
            # Проверяем фото (может быть несколько размеров)
            if hasattr(message, 'photo') and message.photo:
                # Берем только самое качественное фото
                media_list.append(('photo', message.photo[-1].file_id))
                logger.info(f"📸 Добавлено фото: {message.photo[-1].file_id}")
            
            # Проверяем видео
            if hasattr(message, 'video') and message.video:
                media_list.append(('video', message.video.file_id))
                logger.info(f"🎥 Добавлено видео: {message.video.file_id}")
            
            # Проверяем анимацию
            if hasattr(message, 'animation') and message.animation:
                media_list.append(('animation', message.animation.file_id))
                logger.info(f"🎬 Добавлена анимация: {message.animation.file_id}")
            
            # Проверяем аудио
            if hasattr(message, 'audio') and message.audio:
                media_list.append(('audio', message.audio.file_id))
                logger.info(f"🎵 Добавлено аудио: {message.audio.file_id}")
            
            # Проверяем документ
            if hasattr(message, 'document') and message.document:
                media_list.append(('document', message.document.file_id))
                logger.info(f"📄 Добавлен документ: {message.document.file_id}")
            
            # Проверяем голосовое
            if hasattr(message, 'voice') and message.voice:
                media_list.append(('voice', message.voice.file_id))
                logger.info(f"🎤 Добавлено голосовое: {message.voice.file_id}")
            
            # Проверяем видео-сообщение
            if hasattr(message, 'video_note') and message.video_note:
                media_list.append(('video_note', message.video_note.file_id))
                logger.info(f"📹 Добавлено видео-сообщение: {message.video_note.file_id}")
            
            # Проверяем стикер
            if hasattr(message, 'sticker') and message.sticker:
                media_list.append(('sticker', message.sticker.file_id))
                logger.info(f"😀 Добавлен стикер: {message.sticker.file_id}")
            
            if not media_list:
                logger.info("📝 Медиа не найдено")
                
        except Exception as e:
            logger.error(f"❌ Ошибка при извлечении всех медиа: {e}")
        
        return media_list
    
    def extract_text_content(self, message) -> Tuple[str, str]:
        """
        Извлечение текстового содержимого из сообщения
        """
        title = ""
        text = ""
        
        if message.text:
            text = message.text
        elif message.caption:
            text = message.caption
        
        # Попытка извлечь заголовок (первая строка)
        if text:
            lines = text.split('\n')
            if len(lines) > 1:
                title = lines[0].strip()
                text = '\n'.join(lines[1:]).strip()
            else:
                title = text[:100] + "..." if len(text) > 100 else text
                text = ""
        
        return title, text
    
    def get_category_name(self, category_key: str) -> str:
        """
        Получение человекочитаемого названия категории
        """
        return self.categories.get(category_key, category_key)
    
    def get_all_categories(self) -> Dict[str, str]:
        """
        Получение всех доступных категорий
        """
        return self.categories
    
    def get_hashtags_for_category(self, category: str) -> List[str]:
        """
        Получение рекомендуемых хештегов для категории
        """
        return self.category_hashtags.get(category, []) 