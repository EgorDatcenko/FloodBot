#!/usr/bin/env python3
"""
Скрипт для запуска Fitness Content Sorter Bot
"""

import asyncio
import logging
import sys
from bot import ContentBot

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Главная функция для запуска бота"""
    try:
        logger.info("🚀 Запуск Fitness Content Sorter Bot...")
        
        # Создаем и запускаем бота
        bot = ContentBot()
        
        logger.info("✅ Бот успешно запущен!")
        logger.info("📱 Отправьте /start в Telegram для начала работы")
        
        # Запускаем бота
        bot.run()
            
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1) 