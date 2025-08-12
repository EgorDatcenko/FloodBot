# 🔄 Инструкция по откату к оригинальной версии бота

## Проблема
Бот перестал корректно работать после изменений в webhook обработке. Возникают ошибки `RuntimeError: Event loop is closed`.

## Решения

### Вариант 1: Использовать упрощенную версию (рекомендуется)
1. Обновите `render.yaml`:
```yaml
startCommand: python bot_webhook_simple.py
```

2. Перезапустите сервис в Render

### Вариант 2: Полный откат к оригинальной версии

#### Шаг 1: Восстановить оригинальный bot.py
```bash
git checkout HEAD~10 bot.py
```

#### Шаг 2: Удалить webhook файлы
```bash
rm bot_webhook.py
rm bot_webhook_simple.py
rm render.yaml
```

#### Шаг 3: Обновить requirements.txt
Удалить Flask:
```
python-telegram-bot==21.7
requests==2.31.0
python-dotenv==1.0.0
```

#### Шаг 4: Настроить Render для Background Worker
1. Создайте новый сервис типа "Background Worker"
2. Установите Start Command: `python bot.py`
3. Добавьте переменные окружения:
   - `BOT_TOKEN`

### Вариант 3: Использовать polling вместо webhook

Создайте `bot_polling.py`:
```python
#!/usr/bin/env python3
import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from database import Database
from content_analyzer import ContentAnalyzer
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentBot:
    def __init__(self):
        self.token = os.getenv('BOT_TOKEN')
        if not self.token:
            raise ValueError("BOT_TOKEN не найден в переменных окружения")
        
        self.db = Database()
        self.analyzer = ContentAnalyzer()
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        self.application.add_handler(MessageHandler(filters.ALL, self.forwarded_message_handler))
    
    async def start_command(self, update, context):
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [InlineKeyboardButton("😄 МЕМЫ", callback_data="category_memes")],
            [InlineKeyboardButton("🎯 ЧЕЛЛЕНДЖИ", callback_data="category_challenges")],
            [InlineKeyboardButton("💪 СИЛОВЫЕ", callback_data="category_power_results")],
            [InlineKeyboardButton("💡 СПОРТ СОВЕТЫ", callback_data="category_sport_tips")],
            [InlineKeyboardButton("🏋️‍♂️ УПРАЖНЕНИЯ", callback_data="category_exercises")],
            [InlineKeyboardButton("🌊 ФЛУДЩИНА", callback_data="category_flood")],
            [InlineKeyboardButton("📁 ДРУГОЕ", callback_data="category_other")]
        ]
        
        await update.message.reply_text(
            "🎯 Добро пожаловать в FloodBot!\nВыберите категорию:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def help_command(self, update, context):
        help_text = "🤖 FloodBot - Помощь\n\nКоманды:\n/start - Запустить бота\n/help - Показать справку\n\nПересылайте посты боту для добавления!"
        await update.message.reply_text(help_text)
    
    async def handle_callback(self, update, context):
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("category_"):
            category = query.data.replace("category_", "")
            await self.show_category_content(query, category)
    
    async def show_category_content(self, query, category):
        content = self.db.get_content_by_category(category, limit=5)
        category_name = self.analyzer.get_category_name(category)
        
        if content:
            text = f"📁 {category_name}\n\n"
            for i, item in enumerate(content, 1):
                title = item.get('title', 'Без заголовка')[:50]
                text += f"{i}. {title}...\n"
        else:
            text = f"📁 {category_name}\n\nПостов пока нет."
        
        await query.edit_message_text(text)
    
    async def forwarded_message_handler(self, update, context):
        message = update.message
        
        if not message.forward_from_chat:
            return
        
        category = self.analyzer.analyze_content(message.text or "")
        title = message.text[:100] if message.text else "Пересланный пост"
        
        success = self.db.add_content(
            message_id=message.forward_from_message_id,
            channel_id=message.forward_from_chat.id,
            channel_username=message.forward_from_chat.username,
            category=category,
            title=title,
            text=message.text or ""
        )
        
        if success:
            await message.reply_text(f"✅ Добавлен в: {self.analyzer.get_category_name(category)}")
        else:
            await message.reply_text("❌ Ошибка добавления")

async def main():
    logger.info("🚀 Запуск FloodBot...")
    
    bot = ContentBot()
    
    # Запускаем бота
    await bot.application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
```

## Рекомендация
Используйте **Вариант 1** (упрощенная версия) - она должна решить проблему с event loop и сохранить webhook функциональность. 