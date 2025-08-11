#!/usr/bin/env python3
"""
Простой тест бота
"""

import sys
import traceback

def test_imports():
    """Тестирование импортов"""
    print("🔍 Тестирование импортов...")
    
    try:
        from config import BOT_TOKEN, CATEGORIES
        print("✅ config.py импортирован")
        print(f"   BOT_TOKEN: {'Настроен' if BOT_TOKEN else 'Не настроен'}")
        print(f"   Категорий: {len(CATEGORIES)}")
    except Exception as e:
        print(f"❌ Ошибка импорта config.py: {e}")
        return False
    
    try:
        from database import Database
        print("✅ database.py импортирован")
        db = Database()
        print("   База данных инициализирована")
    except Exception as e:
        print(f"❌ Ошибка импорта database.py: {e}")
        return False
    
    try:
        from content_analyzer import ContentAnalyzer
        print("✅ content_analyzer.py импортирован")
        analyzer = ContentAnalyzer()
        print("   Анализатор инициализирован")
    except Exception as e:
        print(f"❌ Ошибка импорта content_analyzer.py: {e}")
        return False
    
    try:
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
        from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
        print("✅ telegram библиотека импортирована")
    except Exception as e:
        print(f"❌ Ошибка импорта telegram: {e}")
        return False
    
    return True

def test_bot_creation():
    """Тестирование создания бота"""
    print("\n🤖 Тестирование создания бота...")
    
    try:
        from bot import ContentBot
        print("✅ bot.py импортирован")
        
        bot = ContentBot()
        print("✅ Бот создан успешно")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка создания бота: {e}")
        print("Детали ошибки:")
        traceback.print_exc()
        return False

def main():
    """Главная функция"""
    print("🧪 Тестирование Fitness Content Sorter Bot")
    print("=" * 50)
    
    # Тестируем импорты
    if not test_imports():
        print("\n❌ Тест импортов не пройден")
        return
    
    # Тестируем создание бота
    if not test_bot_creation():
        print("\n❌ Тест создания бота не пройден")
        return
    
    print("\n✅ Все тесты пройдены!")
    print("🚀 Бот готов к запуску")

if __name__ == "__main__":
    main() 