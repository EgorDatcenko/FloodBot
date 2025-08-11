# 🔧 НАСТРОЙКА WEBHOOK ДЛЯ ПОЛУЧЕНИЯ ПОСТОВ ИЗ КАНАЛА

## ⚠️ ПРОБЛЕМА

Бот не может получить посты из канала, которые были добавлены после добавления бота, потому что:

1. **Методы `get_chat_history` и `get_chat_messages` не существуют** в текущей версии Telegram Bot API
2. **Метод `get_updates` работает только с новыми сообщениями** после запуска бота
3. **Для получения истории канала нужен webhook** или специальные права

## 🚀 РЕШЕНИЕ: НАСТРОЙКА WEBHOOK

### Шаг 1: Получение публичного URL

Для работы webhook нужен публичный HTTPS URL. Варианты:

#### Вариант A: ngrok (для тестирования)
```bash
# Установка ngrok
# Скачайте с https://ngrok.com/

# Запуск туннеля
ngrok http 8080
```

#### Вариант B: VPS с доменом
- Арендуйте VPS (например, DigitalOcean, AWS)
- Настройте домен с SSL сертификатом
- Настройте nginx для проксирования на порт 8080

### Шаг 2: Изменение кода бота

Создайте новый файл `bot_webhook.py`:

```python
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, CHANNEL_USERNAME
from database import Database
from content_analyzer import ContentAnalyzer

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class WebhookBot:
    def __init__(self):
        self.db = Database()
        self.analyzer = ContentAnalyzer()
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков"""
        # Добавляем обработчики как в основном боте
        self.application.add_handler(CommandHandler("start", self.start_command))
        # ... остальные обработчики
        
        # Обработка сообщений из канала через webhook
        self.application.add_handler(MessageHandler(filters.ChatType.CHANNEL, self.channel_message_handler))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        # Код как в основном боте
        pass
    
    async def channel_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик сообщений из канала через webhook"""
        try:
            message = update.channel_post or update.message
            
            if not message:
                return
            
            # Проверяем, что это сообщение из нужного канала
            if message.chat.username != CHANNEL_USERNAME.replace('@', ''):
                return
            
            logger.info(f"📢 Получено сообщение из канала через webhook: {message.message_id}")
            
            # Извлекаем информацию о контенте
            title, text = self.analyzer.extract_text_content(message)
            media_type, media_file_id = self.analyzer.extract_media_info(message)
            
            # Категоризируем контент
            category = self.analyzer.categorize_content(text, title)
            
            # Получаем username канала
            channel_username = message.chat.username or "unknown_channel"
            
            # Сохраняем в базу данных
            success = self.db.add_content(
                message_id=message.message_id,
                channel_id=message.chat.id,
                channel_username=channel_username,
                category=category,
                title=title,
                text=text,
                media_type=media_type,
                media_file_id=media_file_id
            )
            
            if success:
                category_name = self.analyzer.get_category_name(category)
                logger.info(f"✅ Сообщение {message.message_id} добавлено в категорию '{category_name}'")
            else:
                logger.error(f"❌ Ошибка при сохранении сообщения {message.message_id}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка при обработке сообщения из канала: {e}")
    
    def run_webhook(self, webhook_url: str, port: int = 8080):
        """Запуск бота с webhook"""
        logger.info(f"🚀 Запуск бота с webhook: {webhook_url}")
        
        # Устанавливаем webhook
        self.application.bot.set_webhook(url=webhook_url)
        
        # Запускаем webhook сервер
        self.application.run_webhook(
            listen="0.0.0.0",
            port=port,
            webhook_url=webhook_url,
            allowed_updates=Update.ALL_TYPES
        )

if __name__ == "__main__":
    # Замените на ваш публичный URL
    WEBHOOK_URL = "https://your-domain.com/webhook"
    
    bot = WebhookBot()
    bot.run_webhook(WEBHOOK_URL)
```

### Шаг 3: Настройка webhook

1. **Получите публичный URL** (например, через ngrok: `https://abc123.ngrok.io`)
2. **Замените `WEBHOOK_URL`** в коде на ваш URL
3. **Запустите бота:**
```bash
py bot_webhook.py
```

### Шаг 4: Проверка работы

1. **Отправьте новый пост** в канал @nikitaFlooDed с хештегом #мемы
2. **Проверьте логи** - должно появиться сообщение о получении поста
3. **Выберите категорию "😄 МЕМЫ"** в боте
4. **Пост должен появиться** в списке

## 🔧 АЛЬТЕРНАТИВНОЕ РЕШЕНИЕ: РУЧНАЯ ЗАГРУЗКА

Если webhook настроить сложно, можно использовать ручную загрузку:

### Команда для загрузки постов с хештегом:

```python
async def load_posts_by_hashtag_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Загрузка постов с конкретным хештегом"""
    if not context.args:
        await update.message.reply_text("🔍 Использование: /load_hashtag <хештег>\n\nПример: /load_hashtag #мемы")
        return
    
    hashtag = context.args[0]
    await update.message.reply_text(f"🔄 Загружаю посты с хештегом {hashtag}...")
    
    # Получаем посты с хештегом
    posts = await self.get_posts_by_hashtag(hashtag, limit=20)
    
    if posts:
        processed_count = 0
        for message in posts:
            # Обрабатываем пост как в основной функции
            # ...
        
        await update.message.reply_text(f"✅ Загружено {processed_count} постов с хештегом {hashtag}")
    else:
        await update.message.reply_text(f"📁 Постов с хештегом {hashtag} не найдено")
```

## 📱 РЕЗУЛЬТАТ

### ✅ С webhook:
- Бот автоматически получает все новые посты из канала
- Посты сохраняются в базу данных в реальном времени
- При выборе категории показываются все посты, включая новые

### ✅ Без webhook:
- Нужно вручную загружать посты командой `/load_hashtag #мемы`
- Работает только с постами, которые появились после запуска бота

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **Не добавляйте посты в канал** - бот должен только читать
2. **Не изменяйте канал** - бот работает только с существующими постами
3. **Используйте правильные хештеги** - #мемы, #челлендж, #советы и т.д.
4. **Webhook требует публичный HTTPS URL** - для продакшена нужен домен с SSL 