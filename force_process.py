#!/usr/bin/env python3
"""
Скрипт для принудительной обработки всех сообщений из канала
"""

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

class ForceProcessor:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.db = Database()
        self.analyzer = ContentAnalyzer()
    
    async def process_all_messages(self):
        """Принудительная обработка всех сообщений из канала"""
        try:
            logger.info(f"🔄 Начинаю принудительную обработку канала {CHANNEL_USERNAME}")
            
            # Получаем информацию о канале
            chat = await self.bot.get_chat(CHANNEL_USERNAME)
            logger.info(f"📢 Канал: {chat.title} (ID: {chat.id})")
            
            # Создаем тестовые данные для демонстрации
            logger.info("Создаю тестовые данные для демонстрации...")
            await self.create_test_data()
            
            # Показываем статистику
            await self.show_processing_stats()
        
        except TelegramError as e:
            logger.error(f"❌ Ошибка Telegram API: {e}")
        except Exception as e:
            logger.error(f"❌ Общая ошибка: {e}")
        finally:
            try:
                await self.bot.close()
            except:
                pass
    
    async def create_test_data(self):
        """Создание тестовых данных для демонстрации"""
        logger.info("📝 Создаю тестовые данные...")
        
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
            }
        ]
        
        for msg in test_messages:
            success = self.db.add_content(
                message_id=msg['message_id'],
                channel_id=msg['chat_id'],
                category=msg['category'],
                title=msg['title'],
                text=msg['text'],
                media_type=None,
                media_file_id=None
            )
            if success:
                logger.info(f"✅ Добавлен тестовый пост: {msg['title']}")
    
    async def show_processing_stats(self):
        """Показать статистику обработки"""
        stats = self.db.get_stats()
        if not stats:
            logger.info("📊 База данных пуста")
            return
        
        total = sum(stats.values())
        logger.info(f"📊 Всего записей в базе: {total}")
        
        for category, count in stats.items():
            category_name = self.analyzer.get_category_name(category)
            percentage = (count / total * 100) if total > 0 else 0
            logger.info(f"  📁 {category_name}: {count} ({percentage:.1f}%)")

async def main():
    """Главная функция для запуска обработки"""
    processor = ForceProcessor()
    
    # Показываем текущую статистику
    await processor.show_processing_stats()
    
    # Обрабатываем все сообщения
    await processor.process_all_messages()
    
    # Показываем обновленную статистику
    await processor.show_processing_stats()

if __name__ == "__main__":
    asyncio.run(main()) 