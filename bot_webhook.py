#!/usr/bin/env python3
import os
import logging
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from database import Database
from content_analyzer import ContentAnalyzer
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class ContentBot:
    def __init__(self):
        self.token = os.getenv('BOT_TOKEN')
        if not self.token:
            raise ValueError("BOT_TOKEN не найден")
        
        self.db = Database()
        self.analyzer = ContentAnalyzer()
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        self.application.add_handler(MessageHandler(filters.ALL, self.forwarded_message_handler))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = "🤖 FloodBot - Помощь\n\nКоманды:\n/start - Запустить бота\n/help - Показать справку\n\nПересылайте посты боту для добавления!"
        await update.message.reply_text(help_text)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("category_"):
            category = query.data.replace("category_", "")
            await self.show_category_content(query, category)
    
    async def show_category_content(self, query, category: str):
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
    
    async def forwarded_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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

bot = ContentBot()

@app.route('/')
def home():
    return jsonify({"status": "running", "bot": "FloodBot"})

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(), bot.application.bot)
        bot.application.process_update(update)
        return jsonify({"status": "ok"})
    except Exception as e:
        logger.error(f"Ошибка в webhook: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

def main():
    port = int(os.environ.get('PORT', 5000))
    webhook_url = os.getenv('WEBHOOK_URL')
    
    if webhook_url:
        bot.application.bot.set_webhook(url=f"{webhook_url}/webhook")
        logger.info(f"Webhook установлен: {webhook_url}/webhook")
    
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()
