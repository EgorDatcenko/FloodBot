#!/usr/bin/env python3
"""
Скрипт для загрузки реальных данных из канала
"""

import asyncio
import logging
from bot import ContentBot
from config import CHANNEL_USERNAME

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def load_real_channel_data():
    """Загрузка реальных данных из канала"""
    try:
        logger.info("🚀 Запуск загрузки реальных данных из канала...")
        
        # Создаем бота
        bot = ContentBot()
        
        # Загружаем историю канала
        await bot.load_channel_history()
        
        logger.info("✅ Загрузка завершена!")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке: {e}")

if __name__ == "__main__":
    asyncio.run(load_real_channel_data()) 