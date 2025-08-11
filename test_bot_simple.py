#!/usr/bin/env python3
"""
Простой тест бота без запуска полного приложения
"""

import asyncio
import logging
from bot import ContentBot

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def test_bot():
    """Тестирование основных функций бота"""
    try:
        logger.info("🧪 Начинаю тестирование бота...")
        
        # Создаем экземпляр бота
        bot = ContentBot()
        logger.info("✅ Бот создан успешно")
        
        # Тестируем инициализацию
        await bot.application.initialize()
        logger.info("✅ Приложение инициализировано")
        
        # Тестируем доступ к каналу
        from config import CHANNEL_USERNAME
        chat = await bot.application.bot.get_chat(CHANNEL_USERNAME)
        logger.info(f"✅ Канал найден: {chat.title}")
        
        # Тестируем права бота
        member = await bot.application.bot.get_chat_member(CHANNEL_USERNAME, bot.application.bot.id)
        logger.info(f"✅ Права бота: {member.status}")
        
        # Тестируем базу данных
        stats = bot.db.get_category_stats()
        logger.info(f"✅ Статистика БД: {stats}")
        
        # Тестируем анализатор
        categories = bot.analyzer.get_all_categories()
        logger.info(f"✅ Категории: {list(categories.keys())}")
        
        logger.info("🎉 Все тесты пройдены успешно!")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_bot()) 