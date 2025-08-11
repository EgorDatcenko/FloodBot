import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

from config import BOT_TOKEN, CHANNEL_USERNAME
from database import Database
from content_analyzer import ContentAnalyzer

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class WorkingContentBot:
    def __init__(self):
        self.db = Database()
        self.analyzer = ContentAnalyzer()
        self.updater = Updater(token=BOT_TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        # Команды
        self.dispatcher.add_handler(CommandHandler("start", self.start_command))
        self.dispatcher.add_handler(CommandHandler("help", self.help_command))
        self.dispatcher.add_handler(CommandHandler("categories", self.categories_command))
        self.dispatcher.add_handler(CommandHandler("stats", self.stats_command))
        self.dispatcher.add_handler(CommandHandler("hashtags", self.hashtags_command))
        
        # Обработка inline кнопок
        self.dispatcher.add_handler(CallbackQueryHandler(self.button_callback))
    
    def start_command(self, update: Update, context: CallbackContext):
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
        update.message.reply_text(welcome_text, reply_markup=keyboard)
    
    def help_command(self, update: Update, context: CallbackContext):
        """Обработчик команды /help"""
        help_text = """
📖 Справка по использованию бота:

🔍 **Поиск контента:**
/search <запрос> - найти контент по ключевым словам

📊 **Статистика:**
/stats - показать статистику по категориям

📂 **Категории:**
/categories - показать все доступные категории

🏷️ **Хештеги:**
/hashtags - показать рекомендуемые хештеги для каждой категории

💡 **Как использовать:**
1. Выберите категорию из меню
2. Просматривайте отсортированный контент
3. Используйте поиск для быстрого доступа к нужной информации

🔄 Бот автоматически анализирует новые сообщения из канала и добавляет их в соответствующие категории.

📝 **Для точной категоризации используйте хештеги:**
#челлендж #кружки #упражнения #мемы #курсы #советы #прогресс #цитаты
        """
        update.message.reply_text(help_text)
    
    def categories_command(self, update: Update, context: CallbackContext):
        """Обработчик команды /categories"""
        keyboard = self.create_categories_keyboard()
        update.message.reply_text("📂 Выберите категорию:", reply_markup=keyboard)
    
    def hashtags_command(self, update: Update, context: CallbackContext):
        """Обработчик команды /hashtags"""
        hashtags_text = "🏷️ Рекомендуемые хештеги для категорий:\n\n"
        
        for category_key, category_name in self.analyzer.get_all_categories().items():
            if category_key != 'other':
                hashtags = self.analyzer.get_hashtags_for_category(category_key)
                hashtags_text += f"📁 {category_name}:\n"
                hashtags_text += f"   {' '.join(hashtags)}\n\n"
        
        hashtags_text += "💡 Используйте эти хештеги в постах для точной категоризации!"
        update.message.reply_text(hashtags_text)
    
    def stats_command(self, update: Update, context: CallbackContext):
        """Обработчик команды /stats"""
        stats = self.db.get_stats()
        
        if not stats:
            update.message.reply_text("📊 Пока нет данных для отображения статистики.")
            return
        
        stats_text = "📊 Статистика по категориям:\n\n"
        total = sum(stats.values())
        
        for category, count in stats.items():
            category_name = self.analyzer.get_category_name(category)
            percentage = (count / total * 100) if total > 0 else 0
            stats_text += f"📁 {category_name}: {count} ({percentage:.1f}%)\n"
        
        stats_text += f"\n📈 Всего записей: {total}"
        update.message.reply_text(stats_text)
    
    def button_callback(self, update: Update, context: CallbackContext):
        """Обработчик нажатий на inline кнопки"""
        query = update.callback_query
        query.answer()
        
        if query.data.startswith("category_"):
            category = query.data.replace("category_", "")
            self.show_category_content(query, category)
        elif query.data == "back_to_categories":
            keyboard = self.create_categories_keyboard()
            query.edit_message_text("📂 Выберите категорию:", reply_markup=keyboard)
    
    def show_category_content(self, query, category: str):
        """Показать контент выбранной категории"""
        content = self.db.get_content_by_category(category, limit=5)
        category_name = self.analyzer.get_category_name(category)
        
        if not content:
            query.edit_message_text(
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
        
        query.edit_message_text(response, reply_markup=keyboard)
    
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
    
    def run(self):
        """Запуск бота"""
        logger.info("Запуск Fitness Content Sorter Bot...")
        self.updater.start_polling()
        self.updater.idle()

if __name__ == "__main__":
    bot = WorkingContentBot()
    bot.run() 