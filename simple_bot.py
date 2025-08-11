import logging
import asyncio
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from config import BOT_TOKEN, CHANNEL_USERNAME
from database import Database
from content_analyzer import ContentAnalyzer

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SimpleContentBot:
    def __init__(self):
        self.db = Database()
        self.analyzer = ContentAnalyzer()
        self.bot = Bot(token=BOT_TOKEN)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_text = """
🏋️‍♂️ Добро пожаловать в Fitness Content Sorter Bot!

Этот бот автоматически сортирует контент из канала @nikitaFlooDed по категориям.

📋 Доступные команды:
/categories - Просмотр всех категорий
/stats - Статистика по категориям
/hashtags - Рекомендуемые хештеги

Выберите категорию ниже для просмотра контента:
        """
        
        keyboard = self.create_categories_keyboard()
        await update.message.reply_text(welcome_text, reply_markup=keyboard)
    
    async def categories_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /categories"""
        keyboard = self.create_categories_keyboard()
        await update.message.reply_text("📂 Выберите категорию:", reply_markup=keyboard)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /stats"""
        stats = self.db.get_stats()
        
        if not stats:
            await update.message.reply_text("📊 Пока нет данных для отображения статистики.")
            return
        
        stats_text = "📊 Статистика по категориям:\n\n"
        total = sum(stats.values())
        
        for category, count in stats.items():
            category_name = self.analyzer.get_category_name(category)
            percentage = (count / total * 100) if total > 0 else 0
            stats_text += f"📁 {category_name}: {count} ({percentage:.1f}%)\n"
        
        stats_text += f"\n📈 Всего записей: {total}"
        await update.message.reply_text(stats_text)
    
    async def hashtags_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /hashtags"""
        hashtags_text = "🏷️ Рекомендуемые хештеги для категорий:\n\n"
        
        for category_key, category_name in self.analyzer.get_all_categories().items():
            if category_key != 'other':
                hashtags = self.analyzer.get_hashtags_for_category(category_key)
                hashtags_text += f"📁 {category_name}:\n"
                hashtags_text += f"   {' '.join(hashtags)}\n\n"
        
        hashtags_text += "💡 Используйте эти хештеги в постах для точной категоризации!"
        await update.message.reply_text(hashtags_text)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на inline кнопки"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("category_"):
            category = query.data.replace("category_", "")
            await self.show_category_content(query, category)
        elif query.data == "back_to_categories":
            keyboard = self.create_categories_keyboard()
            await query.edit_message_text("📂 Выберите категорию:", reply_markup=keyboard)
    
    async def show_category_content(self, query, category: str):
        """Показать контент выбранной категории"""
        content = self.db.get_content_by_category(category, limit=5)
        category_name = self.analyzer.get_category_name(category)
        
        if not content:
            await query.edit_message_text(
                f"📁 Категория '{category_name}' пока пуста.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Назад", callback_data="back_to_categories")
                ]])
            )
            return
        
        response = f"📁 Категория: {category_name}\n\n"
        
        for i, item in enumerate(content, 1):
            title = item['title'] or "Без заголовка"
            text_preview = item['text'][:100] + "..." if len(item['text']) > 100 else item['text']
            
            response += f"{i}. 📝 {title}\n"
            if text_preview:
                response += f"   {text_preview}\n"
            response += "\n"
        
        # Кнопка "Назад"
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Назад", callback_data="back_to_categories")
        ]])
        
        await query.edit_message_text(response, reply_markup=keyboard)
    
    def create_categories_keyboard(self) -> InlineKeyboardMarkup:
        """Создание клавиатуры с категориями"""
        categories = self.analyzer.get_all_categories()
        keyboard = []
        
        for category_key, category_name in categories.items():
            keyboard.append([InlineKeyboardButton(
                f"📁 {category_name}", 
                callback_data=f"category_{category_key}"
            )])
        
        return InlineKeyboardMarkup(keyboard)
    
    async def run(self):
        """Запуск бота"""
        logger.info("Запуск Fitness Content Sorter Bot...")
        
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("categories", self.categories_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("hashtags", self.hashtags_command))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Запускаем бота
        await application.initialize()
        await application.start()
        await application.run_polling(allowed_updates=Update.ALL_TYPES)

async def main():
    bot = SimpleContentBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main()) 