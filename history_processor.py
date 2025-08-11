import asyncio
import logging
from telegram import Bot
from telegram.error import TelegramError
from config import BOT_TOKEN, CHANNEL_USERNAME
from database import Database
from content_analyzer import ContentAnalyzer

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class HistoryProcessor:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.db = Database()
        self.analyzer = ContentAnalyzer()
    
    async def process_channel_history(self, limit: int = 100):
        """
        Обработка исторического контента из канала
        """
        try:
            logger.info(f"Начинаю обработку исторического контента из канала {CHANNEL_USERNAME}")
            
            # Получаем информацию о канале
            chat = await self.bot.get_chat(CHANNEL_USERNAME)
            logger.info(f"Канал: {chat.title} (ID: {chat.id})")
            
            # Получаем сообщения из канала
            messages = []
            try:
                # Попробуем получить сообщения через updates
                updates = await self.bot.get_updates(limit=limit)
                for update in updates:
                    if update.channel_post:
                        messages.append(update.channel_post)
                    elif update.message and update.message.chat.type == 'channel':
                        messages.append(update.message)
                
                # Если сообщений нет, создаем тестовые данные
                if not messages:
                    logger.info("Создаю тестовые данные для демонстрации...")
                    # Здесь можно добавить тестовые сообщения
                    pass
                
            except Exception as e:
                logger.error(f"Ошибка при получении сообщений: {e}")
                messages = []
            
            logger.info(f"Найдено {len(messages)} сообщений для обработки")
            
            # Обрабатываем каждое сообщение
            processed = 0
            for message in messages:
                try:
                    # Извлекаем информацию о контенте
                    title, text = self.analyzer.extract_text_content(message)
                    media_type, media_file_id = self.analyzer.extract_media_info(message)
                    
                    # Извлекаем хештеги
                    hashtags = self.analyzer.extract_hashtags(f"{title} {text}")
                    
                    # Категоризируем контент
                    category = self.analyzer.categorize_content(text, title)
                    
                    # Сохраняем в базу данных
                    success = self.db.add_content(
                        message_id=message.message_id,
                        channel_id=message.chat.id,
                        category=category,
                        title=title,
                        text=text,
                        media_type=media_type,
                        media_file_id=media_file_id
                    )
                    
                    if success:
                        category_name = self.analyzer.get_category_name(category)
                        hashtags_str = " ".join(hashtags) if hashtags else "без хештегов"
                        logger.info(f"[{processed + 1}/{len(messages)}] Добавлен в категорию '{category_name}' (хештеги: {hashtags_str})")
                        processed += 1
                    else:
                        logger.warning(f"Не удалось сохранить сообщение {message.message_id}")
                
                except Exception as e:
                    logger.error(f"Ошибка при обработке сообщения {message.message_id}: {e}")
            
            logger.info(f"Обработка завершена. Успешно обработано: {processed}/{len(messages)}")
            
            # Показываем статистику
            stats = self.db.get_stats()
            if stats:
                logger.info("Статистика по категориям:")
                for category, count in stats.items():
                    category_name = self.analyzer.get_category_name(category)
                    logger.info(f"  {category_name}: {count}")
        
        except TelegramError as e:
            logger.error(f"Ошибка Telegram API: {e}")
        except Exception as e:
            logger.error(f"Общая ошибка: {e}")
        finally:
            try:
                await self.bot.close()
            except:
                pass
    
    async def show_processing_stats(self):
        """
        Показать статистику обработки
        """
        stats = self.db.get_stats()
        if not stats:
            logger.info("База данных пуста")
            return
        
        total = sum(stats.values())
        logger.info(f"Всего записей в базе: {total}")
        
        for category, count in stats.items():
            category_name = self.analyzer.get_category_name(category)
            percentage = (count / total * 100) if total > 0 else 0
            logger.info(f"  {category_name}: {count} ({percentage:.1f}%)")

async def main():
    """
    Главная функция для запуска обработки
    """
    processor = HistoryProcessor()
    
    # Показываем текущую статистику
    await processor.show_processing_stats()
    
    # Обрабатываем исторический контент
    await processor.process_channel_history(limit=50)  # Уменьшаем лимит
    
    # Показываем обновленную статистику
    await processor.show_processing_stats()

if __name__ == "__main__":
    asyncio.run(main()) 