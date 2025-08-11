import logging
import requests
import json
import time
from config import BOT_TOKEN, CHANNEL_USERNAME
from database import Database
from content_analyzer import ContentAnalyzer

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MinimalContentBot:
    def __init__(self):
        self.db = Database()
        self.analyzer = ContentAnalyzer()
        self.base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
        self.offset = 0
    
    def send_message(self, chat_id, text, reply_markup=None):
        """Отправка сообщения через API"""
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        
        response = requests.post(url, json=data)
        return response.json()
    
    def edit_message(self, chat_id, message_id, text, reply_markup=None):
        """Редактирование сообщения через API"""
        url = f"{self.base_url}/editMessageText"
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML"
        }
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        
        response = requests.post(url, json=data)
        return response.json()
    
    def answer_callback_query(self, callback_query_id, text=""):
        """Ответ на callback query"""
        url = f"{self.base_url}/answerCallbackQuery"
        data = {
            "callback_query_id": callback_query_id,
            "text": text
        }
        response = requests.post(url, json=data)
        return response.json()
    
    def get_updates(self):
        """Получение обновлений"""
        url = f"{self.base_url}/getUpdates"
        params = {
            "offset": self.offset,
            "timeout": 30
        }
        response = requests.get(url, params=params)
        return response.json()
    
    def get_channel_messages(self, limit=50):
        """Получение сообщений из канала"""
        try:
            # Получаем информацию о канале
            chat_url = f"{self.base_url}/getChat"
            chat_response = requests.post(chat_url, json={"chat_id": CHANNEL_USERNAME})
            chat_data = chat_response.json()
            
            if not chat_data.get("ok"):
                logger.error(f"Не удалось получить информацию о канале: {chat_data}")
                return []
            
            chat_id = chat_data["result"]["id"]
            
            # Получаем сообщения из канала
            messages_url = f"{self.base_url}/getUpdates"
            messages_response = requests.get(messages_url, params={
                "limit": limit,
                "timeout": 1
            })
            messages_data = messages_response.json()
            
            if not messages_data.get("ok"):
                logger.error(f"Не удалось получить сообщения: {messages_data}")
                return []
            
            # Фильтруем сообщения из канала
            channel_messages = []
            for update in messages_data.get("result", []):
                if "channel_post" in update:
                    message = update["channel_post"]
                    if message.get("chat", {}).get("id") == chat_id:
                        channel_messages.append(message)
            
            logger.info(f"Найдено {len(channel_messages)} сообщений из канала")
            return channel_messages
            
        except Exception as e:
            logger.error(f"Ошибка при получении сообщений из канала: {e}")
            return []
    
    def process_historical_content(self):
        """Обработка исторического контента"""
        logger.info("Начинаю обработку исторического контента...")
        
        messages = self.get_channel_messages(limit=100)
        
        for message in messages:
            try:
                # Извлекаем текст
                text = message.get("text", "") or message.get("caption", "")
                
                if not text:
                    continue
                
                # Извлекаем хештеги
                hashtags = self.analyzer.extract_hashtags(text)
                
                # Категоризируем контент
                category = self.analyzer.categorize_content(text, "")
                
                # Сохраняем в базу данных
                success = self.db.add_content(
                    message_id=message["message_id"],
                    channel_id=message["chat"]["id"],
                    category=category,
                    title="",
                    text=text,
                    media_type=None,
                    media_file_id=None
                )
                
                if success:
                    category_name = self.analyzer.get_category_name(category)
                    hashtags_str = " ".join(hashtags) if hashtags else "без хештегов"
                    logger.info(f"Добавлен в категорию '{category_name}' (хештеги: {hashtags_str})")
                
            except Exception as e:
                logger.error(f"Ошибка при обработке сообщения {message.get('message_id')}: {e}")
        
        logger.info("Обработка исторического контента завершена")
    
    def create_categories_keyboard(self):
        """Создание клавиатуры с категориями"""
        categories = self.analyzer.get_all_categories()
        keyboard = []
        
        for category_key, category_name in categories.items():
            keyboard.append([{
                "text": f"📁 {category_name}",
                "callback_data": f"category_{category_key}"
            }])
        
        return {"inline_keyboard": keyboard}
    
    def create_back_keyboard(self):
        """Создание клавиатуры с кнопкой назад"""
        return {
            "inline_keyboard": [[{
                "text": "🔙 Назад",
                "callback_data": "back_to_categories"
            }]]
        }
    
    def handle_start_command(self, chat_id):
        """Обработка команды /start"""
        welcome_text = """
🏋️‍♂️ Добро пожаловать в Fitness Content Sorter Bot!

Этот бот автоматически сортирует контент из канала @nikitaFlooDed по категориям.

📋 Доступные команды:
/categories - Просмотр всех категорий
/stats - Статистика по категориям
/hashtags - Рекомендуемые хештеги
/process - Обработать исторический контент

Выберите категорию ниже для просмотра контента:
        """
        
        keyboard = self.create_categories_keyboard()
        return self.send_message(chat_id, welcome_text, keyboard)
    
    def handle_categories_command(self, chat_id):
        """Обработка команды /categories"""
        keyboard = self.create_categories_keyboard()
        return self.send_message(chat_id, "📂 Выберите категорию:", reply_markup=keyboard)
    
    def handle_stats_command(self, chat_id):
        """Обработка команды /stats"""
        stats = self.db.get_stats()
        
        if not stats:
            return self.send_message(chat_id, "📊 Пока нет данных для отображения статистики.")
        
        stats_text = "📊 Статистика по категориям:\n\n"
        total = sum(stats.values())
        
        for category, count in stats.items():
            category_name = self.analyzer.get_category_name(category)
            percentage = (count / total * 100) if total > 0 else 0
            stats_text += f"📁 {category_name}: {count} ({percentage:.1f}%)\n"
        
        stats_text += f"\n📈 Всего записей: {total}"
        return self.send_message(chat_id, stats_text)
    
    def handle_hashtags_command(self, chat_id):
        """Обработка команды /hashtags"""
        hashtags_text = "🏷️ Рекомендуемые хештеги для категорий:\n\n"
        
        for category_key, category_name in self.analyzer.get_all_categories().items():
            if category_key != 'other':
                hashtags = self.analyzer.get_hashtags_for_category(category_key)
                hashtags_text += f"📁 {category_name}:\n"
                hashtags_text += f"   {' '.join(hashtags)}\n\n"
        
        hashtags_text += "💡 Используйте эти хештеги в постах для точной категоризации!"
        return self.send_message(chat_id, hashtags_text)
    
    def handle_process_command(self, chat_id):
        """Обработка команды /process"""
        self.send_message(chat_id, "🔄 Начинаю обработку исторического контента...")
        
        # Запускаем обработку в отдельном потоке
        import threading
        thread = threading.Thread(target=self.process_historical_content)
        thread.start()
        
        return self.send_message(chat_id, "✅ Обработка запущена! Проверьте статистику через /stats")
    
    def handle_category_callback(self, chat_id, message_id, category):
        """Обработка выбора категории"""
        content = self.db.get_content_by_category(category, limit=50)  # Увеличиваем лимит
        category_name = self.analyzer.get_category_name(category)
        
        if not content:
            text = f"📁 Категория '{category_name}' пока пуста."
            keyboard = self.create_back_keyboard()
            return self.edit_message(chat_id, message_id, text, keyboard)
        
        response = f"📁 Категория: {category_name}\n"
        response += f"📊 Найдено постов: {len(content)}\n\n"
        
        for i, item in enumerate(content, 1):
            title = item['title'] or "Без заголовка"
            # Показываем полный текст поста
            full_text = item['text']
            
            response += f"{i}. 📝 {title}\n"
            response += f"   {full_text}\n"
            response += "   " + "─" * 50 + "\n\n"
            
            # Ограничиваем длину сообщения (Telegram лимит ~4096 символов)
            if len(response) > 3500:
                response += f"... и еще {len(content) - i} постов"
                break
        
        keyboard = self.create_back_keyboard()
        return self.edit_message(chat_id, message_id, response, keyboard)
    
    def handle_back_callback(self, chat_id, message_id):
        """Обработка кнопки назад"""
        keyboard = self.create_categories_keyboard()
        return self.edit_message(chat_id, message_id, "📂 Выберите категорию:", keyboard)
    
    def process_update(self, update):
        """Обработка обновления"""
        try:
            # Обработка сообщений
            if "message" in update:
                message = update["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "")
                
                if text == "/start":
                    self.handle_start_command(chat_id)
                elif text == "/categories":
                    self.handle_categories_command(chat_id)
                elif text == "/stats":
                    self.handle_stats_command(chat_id)
                elif text == "/hashtags":
                    self.handle_hashtags_command(chat_id)
                elif text == "/process":
                    self.handle_process_command(chat_id)
            
            # Обработка callback queries
            elif "callback_query" in update:
                callback_query = update["callback_query"]
                chat_id = callback_query["message"]["chat"]["id"]
                message_id = callback_query["message"]["message_id"]
                callback_query_id = callback_query["id"]
                data = callback_query["data"]
                
                # Отвечаем на callback query
                self.answer_callback_query(callback_query_id)
                
                if data.startswith("category_"):
                    category = data.replace("category_", "")
                    self.handle_category_callback(chat_id, message_id, category)
                elif data == "back_to_categories":
                    self.handle_back_callback(chat_id, message_id)
        
        except Exception as e:
            logger.error(f"Ошибка при обработке обновления: {e}")
    
    def run(self):
        """Запуск бота"""
        logger.info("Запуск Fitness Content Sorter Bot...")
        
        while True:
            try:
                # Получаем обновления
                response = self.get_updates()
                
                if response.get("ok"):
                    updates = response.get("result", [])
                    
                    for update in updates:
                        self.process_update(update)
                        self.offset = update["update_id"] + 1
                
                # Небольшая задержка
                time.sleep(1)
            
            except Exception as e:
                logger.error(f"Ошибка в главном цикле: {e}")
                time.sleep(5)

if __name__ == "__main__":
    bot = MinimalContentBot()
    bot.run() 