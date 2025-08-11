import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError
from telegram.constants import MessageOriginType
import asyncio

from config import BOT_TOKEN, CHANNEL_USERNAME
from database import Database
from content_analyzer import ContentAnalyzer

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ContentBot:
    def __init__(self):
        self.db = Database()
        self.analyzer = ContentAnalyzer()
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        # Команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("categories", self.categories_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("search", self.search_command))
        self.application.add_handler(CommandHandler("hashtags", self.hashtags_command))
        self.application.add_handler(CommandHandler("load_history", self.load_history_command))
        self.application.add_handler(CommandHandler("debug", self.debug_command))
        self.application.add_handler(CommandHandler("category", self.category_command))
        self.application.add_handler(CommandHandler("load_posts", self.load_posts_command))
        self.application.add_handler(CommandHandler("load_hashtag", self.load_hashtag_command))
        
        # Обработка inline кнопок
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Обработка сообщений из канала
        self.application.add_handler(MessageHandler(filters.ChatType.CHANNEL, self.channel_message_handler))
        
        # Обработка пересланных сообщений из канала в ЛС боту
        self.application.add_handler(MessageHandler(filters.FORWARDED & filters.ChatType.PRIVATE, self.forwarded_message_handler))
        
        # Обработка ошибок
        self.application.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_text = """
🏋️‍♂️ Добро пожаловать в Fitness Content Sorter Bot!

Этот бот автоматически сортирует контент из канала @nikitaFlooDed по категориям.

📋 Выберите категорию из меню ниже:
        """
        
        keyboard = self.create_main_keyboard()
        await update.message.reply_text(welcome_text, reply_markup=keyboard)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
1. Отправьте `/start` для начала работы
2. Выберите категорию из меню для просмотра постов
3. Бот автоматически загрузит и пересласт посты из канала
4. Используйте поиск для быстрого доступа к нужной информации

🔄 Бот автоматически анализирует новые сообщения из канала и добавляет их в соответствующие категории.

📝 **Для точной категоризации используйте хештеги:**
#челлендж #кружки #упражнения #мемы #курсы #советы #прогресс #цитаты

⚠️ **Важно:** 
- Для работы с реальными постами бот должен быть администратором канала @nikitaFlooDed
- При выборе категории бот автоматически загружает и пересылает посты из канала
        """
        await update.message.reply_text(help_text)
    
    async def categories_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /categories"""
        keyboard = self.create_categories_keyboard()
        await update.message.reply_text("📂 Выберите категорию:", reply_markup=keyboard)
    
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
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /search"""
        if not context.args:
            await update.message.reply_text("🔍 Использование: /search <запрос>\n\nПример: /search челлендж")
            return
        
        query = " ".join(context.args)
        results = self.db.search_content(query, limit=10)
        
        if not results:
            await update.message.reply_text(f"🔍 По запросу '{query}' ничего не найдено.")
            return
        
        await update.message.reply_text(
            f"🔍 Результаты поиска по запросу '{query}':\nНайдено постов: {len(results)}\n\nПоказываю посты..."
        )
        
        # Показываем полные посты с медиа
        for item in results:
            title = item['title'] or "Без заголовка"
            text = item['text'] or "Нет текста"
            media_type = item.get('media_type')
            media_file_id = item.get('media_file_id')
            category_name = self.analyzer.get_category_name(item['category'])
            
            caption = f"🔍 <b>Поиск: {query}</b>\n📁 <b>Категория: {category_name}</b>\n\n📝 <b>{title}</b>\n\n{text}"
            
            chat_id = update.message.chat.id
            if not self.is_private_chat(chat_id):
                logger.error(f"❌ Попытка отправить сообщение в канал/группу запрещена! chat_id={chat_id}")
                await update.message.reply_text(
                    "❌ Ошибка: Бот не может отправлять сообщения в канал или группу.",
                    parse_mode='HTML'
                )
                continue
                
            try:
                # Проверяем, есть ли доступное медиа
                has_media = media_type and media_file_id
                
                if has_media and media_type == 'video':
                    try:
                        await self.application.bot.send_video(
                            chat_id=chat_id,
                            video=media_file_id,
                            caption=caption,
                            parse_mode='HTML'
                        )
                    except Exception as media_error:
                        logger.error(f"❌ Ошибка при отправке видео: {media_error}")
                        await update.message.reply_text(
                            f"⚠️ Видео недоступно.\n\n{caption}",
                            parse_mode='HTML'
                        )
                elif has_media and media_type == 'photo':
                    try:
                        await self.application.bot.send_photo(
                            chat_id=chat_id,
                            photo=media_file_id,
                            caption=caption,
                            parse_mode='HTML'
                        )
                    except Exception as media_error:
                        logger.error(f"❌ Ошибка при отправке фото: {media_error}")
                        await update.message.reply_text(
                            f"⚠️ Фото недоступно.\n\n{caption}",
                            parse_mode='HTML'
                        )
                elif has_media and media_type == 'animation':
                    try:
                        await self.application.bot.send_animation(
                            chat_id=chat_id,
                            animation=media_file_id,
                            caption=caption,
                            parse_mode='HTML'
                        )
                    except Exception as media_error:
                        logger.error(f"❌ Ошибка при отправке анимации: {media_error}")
                        await update.message.reply_text(
                            f"⚠️ Анимация недоступна.\n\n{caption}",
                            parse_mode='HTML'
                        )
                else:
                    # Нет медиа или медиа недоступно
                    await update.message.reply_text(
                        caption,
                        parse_mode='HTML'
                    )
            except Exception as e:
                logger.error(f"❌ Общая ошибка при отправке: {e}")
                await update.message.reply_text(
                    f"⚠️ Не удалось отправить контент.\n\n{caption}",
                    parse_mode='HTML'
                )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на inline кнопки"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("category_"):
            category = data.replace("category_", "")
            await self.show_category_content(query, category)
        elif data == "stats":
            await self.stats_command(update, context)
        elif data == "search":
            await query.edit_message_text("🔍 Использование: /search <запрос>\n\nПример: /search челлендж")
        elif data == "load_posts":
            await self.load_posts_command(update, context)
        elif data == "help":
            await self.help_command(update, context)
        elif data == "back_to_main":
            # Возвращаемся к главному меню
            welcome_text = """
🏋️‍♂️ Добро пожаловать в Fitness Content Sorter Bot!

Этот бот автоматически сортирует контент из канала @nikitaFlooDed по категориям.

📋 Выберите категорию из меню ниже:
            """
            keyboard = self.create_main_keyboard()
            await query.edit_message_text(welcome_text, reply_markup=keyboard)
        else:
            await query.edit_message_text("❓ Неизвестная команда. Используйте /help для справки.")
    
    async def auto_load_new_posts(self):
        """Автоматическая загрузка новых постов из канала"""
        try:
            logger.info("🔄 Автоматическая загрузка новых постов...")
            
            # Получаем последние сообщения из канала
            try:
                chat = await self.application.bot.get_chat(CHANNEL_USERNAME)
                logger.info(f"✅ Канал найден: {chat.title}")
                
                # Получаем последние сообщения
                messages = []
                try:
                    # Используем get_updates для получения последних сообщений
                    updates = await self.application.bot.get_updates(limit=50, timeout=1)
                    for update_item in updates:
                        if update_item.channel_post and update_item.channel_post.chat.username == CHANNEL_USERNAME.replace('@', ''):
                            messages.append(update_item.channel_post)
                    logger.info(f"📥 Получено {len(messages)} сообщений из канала")
                except Exception as e:
                    logger.warning(f"❌ Не удалось получить сообщения: {e}")
                    return
                
                if messages:
                    processed_count = 0
                    for message in messages:
                        try:
                            # Проверяем, не добавлен ли уже этот пост
                            existing_post = self.db.get_content_by_message_id(message.message_id)
                            if existing_post:
                                continue
                            
                            # Извлекаем информацию о контенте
                            title, text = self.analyzer.extract_text_content(message)
                            media_type, media_file_id = self.analyzer.extract_media_info(message)
                            
                            # Категоризируем контент
                            category = self.analyzer.categorize_content(text, title)
                            
                            # Получаем username канала
                            channel_username = message.chat.username or CHANNEL_USERNAME.replace('@', '')
                            
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
                                logger.info(f"✅ Новый пост {message.message_id} добавлен в категорию '{category_name}'")
                                processed_count += 1
                                
                        except Exception as e:
                            logger.error(f"❌ Ошибка при обработке сообщения {message.message_id}: {e}")
                    
                    if processed_count > 0:
                        logger.info(f"✅ Автоматически обработано {processed_count} новых постов")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка при доступе к каналу: {e}")
                
        except Exception as e:
            logger.error(f"❌ Общая ошибка при автоматической загрузке: {e}")

    async def show_category_content(self, query, category: str):
        """Показать контент выбранной категории с улучшенной обработкой медиа"""
        # Сначала загружаем новые посты
        await self.auto_load_new_posts()
        
        content = self.db.get_content_by_category(category, limit=50)
        category_name = self.analyzer.get_category_name(category)
        
        if not content:
            await query.edit_message_text(
                f"📁 Категория '{category_name}' пока пуста.\n\n💡 Для загрузки реальных постов из канала используйте команду /load_history",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
                ]])
            )
            return
        
        # Показываем количество найденных постов
        await query.edit_message_text(
            f"📁 Категория: {category_name}\nНайдено постов: {len(content)}\n\nОтправляю посты...",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
            ]])
        )
        
        # Отправляем каждый пост
        for item in content:
            try:
                title = item['title'] or "Без заголовка"
                text = item['text'] or "Нет текста"
                media_type = item.get('media_type')
                media_file_id = item.get('media_file_id')
                message_id = item['message_id']
                
                caption = f"📝 <b>{title}</b>\n\n{text}"
                
                # Сначала пытаемся переслать оригинальное сообщение
                try:
                    await self.application.bot.forward_message(
                        chat_id=query.from_user.id,
                        from_chat_id=CHANNEL_USERNAME,
                        message_id=message_id
                    )
                    logger.info(f"✅ Переслан оригинальный пост {message_id}")
                    continue
                except Exception as forward_error:
                    logger.warning(f"⚠️ Не удалось переслать пост {message_id}: {forward_error}")
                
                # Если пересылка не удалась, отправляем с медиа через file_id
                if media_type and media_file_id:
                    try:
                        if media_type == 'video':
                            await self.application.bot.send_video(
                                chat_id=query.from_user.id,
                                video=media_file_id,
                                caption=caption,
                                parse_mode='HTML'
                            )
                        elif media_type == 'photo':
                            await self.application.bot.send_photo(
                                chat_id=query.from_user.id,
                                photo=media_file_id,
                                caption=caption,
                                parse_mode='HTML'
                            )
                        elif media_type == 'animation':
                            await self.application.bot.send_animation(
                                chat_id=query.from_user.id,
                                animation=media_file_id,
                                caption=caption,
                                parse_mode='HTML'
                            )
                        else:
                            # Для других типов медиа отправляем только текст
                            await self.application.bot.send_message(
                                chat_id=query.from_user.id,
                                text=caption,
                                parse_mode='HTML'
                            )
                        logger.info(f"✅ Отправлен пост {message_id} с медиа {media_type}")
                    except Exception as media_error:
                        logger.error(f"❌ Ошибка при отправке медиа {message_id}: {media_error}")
                        # Отправляем только текст
                        await self.application.bot.send_message(
                            chat_id=query.from_user.id,
                            text=caption,
                            parse_mode='HTML'
                        )
                else:
                    # Нет медиа, отправляем только текст
                    await self.application.bot.send_message(
                        chat_id=query.from_user.id,
                        text=caption,
                        parse_mode='HTML'
                    )
                    logger.info(f"✅ Отправлен текстовый пост {message_id}")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка при отправке поста {item.get('message_id', 'unknown')}: {e}")
                # Отправляем базовую информацию о посте
                try:
                    title = item.get('title', 'Без заголовка')
                    text = item.get('text', 'Нет текста')
                    await self.application.bot.send_message(
                        chat_id=query.from_user.id,
                        text=f"⚠️ Ошибка при отправке поста\n\n📝 <b>{title}</b>\n\n{text}",
                        parse_mode='HTML'
                    )
                except:
                    pass
    
    def create_categories_keyboard(self) -> InlineKeyboardMarkup:
        """Создание клавиатуры с категориями"""
        categories = self.analyzer.get_all_categories()
        keyboard = []
        
        for category_key, category_name in categories.items():
            keyboard.append([InlineKeyboardButton(
                f"{category_name}", 
                callback_data=f"category_{category_key}"
            )])
        
        return InlineKeyboardMarkup(keyboard)
    
    def create_main_keyboard(self) -> InlineKeyboardMarkup:
        """Создание основной клавиатуры с inline кнопками"""
        keyboard = [
            [
                InlineKeyboardButton("🎯 ЧЕЛЛЕНДЖИ", callback_data="category_challenges"),
                InlineKeyboardButton("💪 СИЛОВЫЕ", callback_data="category_power_results")
            ],
            [
                InlineKeyboardButton("💡 СПОРТ СОВЕТЫ", callback_data="category_sport_tips"),
                InlineKeyboardButton("😄 МЕМЫ", callback_data="category_memes")
            ],
            [
                InlineKeyboardButton("🏋️‍♂️ УПРАЖНЕНИЯ", callback_data="category_exercises"),
                InlineKeyboardButton("🌊 ФЛУДЩИНА", callback_data="category_flood")
            ],
            [
                InlineKeyboardButton("📊 СТАТИСТИКА", callback_data="stats"),
                InlineKeyboardButton("🔍 ПОИСК", callback_data="search")
            ],
            [
                InlineKeyboardButton("🔄 ЗАГРУЗИТЬ ПОСТЫ", callback_data="load_posts"),
                InlineKeyboardButton("❓ ПОМОЩЬ", callback_data="help")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def is_private_chat(self, chat_id) -> bool:
        """Проверяет, что chat_id — это личный чат, а не канал/группа."""
        if isinstance(chat_id, int):
            # В Telegram личные чаты — положительные ID, группы/каналы — отрицательные
            return chat_id > 0
        if isinstance(chat_id, str):
            # Каналы обычно начинаются с @ или -100
            if chat_id.startswith('@') or chat_id.startswith('-100'):
                return False
        return True

    async def get_posts_by_hashtag(self, hashtag: str, limit: int = 10) -> list:
        """Получение постов с конкретным хештегом из канала"""
        try:
            logger.info(f"🔍 Ищу посты с хештегом {hashtag} в канале...")
            
            # Добавляем задержку перед запросом
            await asyncio.sleep(1)
            
            # Получаем обновления из канала с увеличенным timeout
            updates = await self.application.bot.get_updates(limit=50, timeout=5)
            posts_with_hashtag = []
            
            logger.info(f"📥 Получено {len(updates)} обновлений из Telegram")
            
            for update_item in updates:
                if update_item.channel_post and update_item.channel_post.chat.username == CHANNEL_USERNAME.replace('@', ''):
                    message = update_item.channel_post
                    
                    # Извлекаем текст сообщения
                    title, text = self.analyzer.extract_text_content(message)
                    full_text = f"{title} {text}".lower()
                    
                    # Проверяем наличие хештега (различные варианты)
                    hashtag_variants = [
                        hashtag.lower(),
                        hashtag.lower().replace('#', ''),
                        hashtag.lower().replace('#', ' '),
                        hashtag.lower().replace('#', '')
                    ]
                    
                    found = False
                    for variant in hashtag_variants:
                        if variant in full_text:
                            found = True
                            break
                    
                    if found:
                        posts_with_hashtag.append(message)
                        logger.info(f"✅ Найден пост {message.message_id} с хештегом {hashtag}")
                        if len(posts_with_hashtag) >= limit:
                            break
            
            logger.info(f"📊 Найдено {len(posts_with_hashtag)} постов с хештегом {hashtag}")
            return posts_with_hashtag
        except Exception as e:
            logger.error(f"❌ Ошибка при получении постов с хештегом {hashtag}: {e}")
            return []
    
    async def show_category_content_text(self, update: Update, category: str):
        """Показать контент категории через сообщения от бота (с медиа, если есть)"""
        content = self.db.get_content_by_category(category, limit=50)
        category_name = self.analyzer.get_category_name(category)
        
        if not content:
            # Если постов нет в базе, попробуем загрузить их из канала
            await update.message.reply_text(
                f"📁 Категория '{category_name}' пуста. Загружаю посты из канала..."
            )
            
            # Определяем хештег для категории
            hashtag_map = {
                'challenges': '#челлендж',
                'memes': '#мемы',
                'power_results': '#результаты',
                'sport_tips': '#советы',
                'exercises': '#упражнения',
                'flood': '#флуд',
                'other': '#другое'
            }
            
            hashtag = hashtag_map.get(category, f'#{category}')
            
            # Получаем посты с хештегом из канала
            posts = await self.get_posts_by_hashtag(hashtag, limit=10)
            
            if posts:
                await update.message.reply_text(
                    f"✅ Найдено {len(posts)} постов с хештегом {hashtag} в канале"
                )
                
                # Обрабатываем найденные посты
                processed_count = 0
                for message in posts:
                    try:
                        # Проверяем, не добавлен ли уже этот пост
                        existing_post = self.db.get_content_by_message_id(message.message_id)
                        if existing_post:
                            continue
                        
                        # Извлекаем информацию о контенте
                        title, text = self.analyzer.extract_text_content(message)
                        media_type, media_file_id = self.analyzer.extract_media_info(message)
                        
                        # Получаем username канала
                        channel_username = message.chat.username or CHANNEL_USERNAME.replace('@', '')
                        
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
                            processed_count += 1
                            
                    except Exception as e:
                        logger.error(f"❌ Ошибка при обработке поста {message.message_id}: {e}")
                
                if processed_count > 0:
                    await update.message.reply_text(
                        f"✅ Добавлено {processed_count} новых постов в категорию '{category_name}'"
                    )
                    # Повторно получаем контент после загрузки
                    content = self.db.get_content_by_category(category, limit=50)
                else:
                    await update.message.reply_text(
                        f"📁 Категория '{category_name}' пока пуста.\n\n💡 Добавьте новый пост с хештегом {hashtag} в канал, чтобы он появился здесь."
                    )
                    return
            else:
                await update.message.reply_text(
                    f"📁 Категория '{category_name}' пока пуста.\n\n💡 Добавьте новый пост с хештегом {hashtag} в канал, чтобы он появился здесь.\n\n💡 Или используйте команду /load_hashtag {hashtag} для загрузки постов."
            )
            return
        
        await update.message.reply_text(
            f"📁 Категория: {category_name}\nНайдено постов: {len(content)}\n\nПоказываю посты..."
        )
        
        for item in content:
            title = item['title'] or "Без заголовка"
            text = item['text'] or "Нет текста"
            media_type = item.get('media_type')
            media_file_id = item.get('media_file_id')
            caption = f"📝 <b>{title}</b>\n\n{text}"
            
            # Логируем информацию о посте для отладки
            logger.info(f"📤 Отправляю пост {item['message_id']}:")
            logger.info(f"   Медиа тип: {media_type}")
            logger.info(f"   Медиа file_id: {media_file_id}")
            logger.info(f"   Заголовок: {title[:50]}...")
            
            chat_id = update.message.chat.id
            if not self.is_private_chat(chat_id):
                logger.error(f"❌ Попытка отправить сообщение в канал/группу запрещена! chat_id={chat_id}")
                await update.message.reply_text(
                    "❌ Ошибка: Бот не может отправлять сообщения в канал или группу.",
                    parse_mode='HTML'
                )
                continue
            try:
                # Проверяем, есть ли доступное медиа
                has_media = media_type and media_file_id
                
                if has_media and media_type == 'video':
                    logger.info(f"   Отправляю видео: {media_file_id}")
                    try:
                        await self.application.bot.send_video(
                            chat_id=chat_id,
                            video=media_file_id,
                            caption=caption,
                            parse_mode='HTML'
                        )
                        logger.info(f"   ✅ Видео отправлено успешно")
                    except Exception as media_error:
                        logger.error(f"   ❌ Ошибка при отправке видео: {media_error}")
                        await update.message.reply_text(
                            f"⚠️ Видео недоступно.\n\n{caption}",
                            parse_mode='HTML'
                        )
                elif has_media and media_type == 'photo':
                    logger.info(f"   Отправляю фото: {media_file_id}")
                    try:
                        await self.application.bot.send_photo(
                            chat_id=chat_id,
                            photo=media_file_id,
                            caption=caption,
                            parse_mode='HTML'
                        )
                        logger.info(f"   ✅ Фото отправлено успешно")
                    except Exception as media_error:
                        logger.error(f"   ❌ Ошибка при отправке фото: {media_error}")
                        await update.message.reply_text(
                            f"⚠️ Фото недоступно.\n\n{caption}",
                            parse_mode='HTML'
                        )
                elif has_media and media_type == 'animation':
                    logger.info(f"   Отправляю анимацию: {media_file_id}")
                    try:
                        await self.application.bot.send_animation(
                            chat_id=chat_id,
                            animation=media_file_id,
                            caption=caption,
                            parse_mode='HTML'
                        )
                        logger.info(f"   ✅ Анимация отправлена успешно")
                    except Exception as media_error:
                        logger.error(f"   ❌ Ошибка при отправке анимации: {media_error}")
                        await update.message.reply_text(
                            f"⚠️ Анимация недоступна.\n\n{caption}",
                            parse_mode='HTML'
                        )
                else:
                    # Нет медиа или медиа недоступно
                    if media_type and not media_file_id:
                        logger.info(f"   Отправляю только текст (медиа {media_type} недоступно)")
                    else:
                        logger.info(f"   Отправляю только текст (нет медиа)")
                    
                    await update.message.reply_text(
                        caption,
                        parse_mode='HTML'
                    )
                    logger.info(f"   ✅ Текст отправлен успешно")
            except Exception as e:
                logger.error(f"   ❌ Общая ошибка при отправке: {e}")
                await update.message.reply_text(
                    f"⚠️ Не удалось отправить контент.\n\n{caption}",
                    parse_mode='HTML'
                )
    
    async def channel_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик сообщений из канала"""
        try:
            message = update.channel_post or update.message
            
            if not message:
                logger.warning("❌ Сообщение из канала не найдено")
                return
            
            logger.info(f"📢 Получено сообщение из канала: {message.message_id}")
            logger.info(f"   Канал: {message.chat.title} (@{message.chat.username})")
            logger.info(f"   Тип сообщения: {type(message).__name__}")
            
            # Проверяем, что это сообщение из нужного канала
            if message.chat.username != CHANNEL_USERNAME.replace('@', ''):
                logger.info(f"   ⚠️ Сообщение не из целевого канала: {message.chat.username} != {CHANNEL_USERNAME.replace('@', '')}")
                return
            
            logger.info(f"   ✅ Сообщение из целевого канала")
            
            # Извлекаем информацию о контенте
            title, text = self.analyzer.extract_text_content(message)
            media_type, media_file_id = self.analyzer.extract_media_info(message)
            
            # Извлекаем хештеги для логирования
            hashtags = self.analyzer.extract_hashtags(f"{title} {text}")
            
            # Категоризируем контент
            category = self.analyzer.categorize_content(text, title)
            
            # Получаем username канала
            channel_username = message.chat.username or "unknown_channel"
            
            logger.info(f"   📝 Заголовок: {title[:50]}...")
            logger.info(f"   📄 Текст: {text[:100]}...")
            logger.info(f"   🏷️ Хештеги: {hashtags}")
            logger.info(f"   📁 Категория: {category}")
            logger.info(f"   🎬 Медиа: {media_type}")
            
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
                hashtags_str = " ".join(hashtags) if hashtags else "без хештегов"
                logger.info(f"✅ Сообщение {message.message_id} из канала {channel_username} добавлено в категорию '{category_name}' (хештеги: {hashtags_str})")
            else:
                logger.error(f"❌ Ошибка при сохранении сообщения {message.message_id}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка при обработке сообщения из канала: {e}")
            if message:
                logger.error(f"   ID сообщения: {message.message_id}")
                logger.error(f"   Текст: {getattr(message, 'text', 'Нет текста')}")
                logger.error(f"   Канал: {getattr(message.chat, 'username', 'Нет username')}")
    
    async def forwarded_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message
        # Проверяем, что это переслано из канала через forward_origin
        if not message or not hasattr(message, 'forward_origin') or not message.forward_origin:
            return

        # Проверяем тип origin
        if message.forward_origin.type != MessageOriginType.CHANNEL:
            await message.reply_text("⚠️ Это сообщение не из канала.")
            return

        channel = message.forward_origin.chat
        channel_username = getattr(channel, 'username', None)
        channel_id = channel.id
        orig_message_id = message.forward_origin.message_id

        # ВРЕМЕННО: Убираем ограничение на конкретный канал
        # if channel_username != CHANNEL_USERNAME.replace('@', ''):
        #     await message.reply_text("⚠️ Это сообщение не из нужного канала.")
        #     return

        # Извлекаем данные
        title, text = self.analyzer.extract_text_content(message)
        media_type, media_file_id = self.analyzer.extract_media_info(message)
        
        # Проверяем, есть ли установленная категория для этого пользователя
        user_id = message.from_user.id
        manual_category = None
        manual_description = None
        
        if hasattr(self, 'pending_categories') and user_id in self.pending_categories:
            pending_info = self.pending_categories[user_id]
            # Проверяем, что команда была отправлена недавно (в течение 5 минут)
            time_diff = (message.date - pending_info['timestamp']).total_seconds()
            if time_diff < 300:  # 5 минут
                manual_category = pending_info['category']
                manual_description = pending_info['description']
                # Удаляем использованную категорию
                del self.pending_categories[user_id]
                logger.info(f"🎯 Используется ручная категория: {manual_category} - {manual_description}")
        
        # Если нет ручной категории, используем автоматическую
        if manual_category:
            category = manual_category
            # Добавляем описание к тексту
            if manual_description:
                text = f"{manual_description}\n\n{text}"
        else:
            category = self.analyzer.categorize_content(text, title)

        # Логируем информацию о медиа для отладки
        logger.info(f"📱 Пересланное сообщение {orig_message_id} из канала {channel_username}:")
        logger.info(f"   Медиа тип: {media_type}")
        logger.info(f"   Медиа file_id: {media_file_id}")
        logger.info(f"   Категория: {category} {'(ручная)' if manual_category else '(автоматическая)'}")
        logger.info(f"   Заголовок: {title[:50]}...")
        logger.info(f"   Текст: {text[:100]}...")

        # Проверяем доступность медиа
        if media_type and media_file_id:
            try:
                # Пробуем получить информацию о файле
                if media_type == 'video':
                    file_info = await self.application.bot.get_file(media_file_id)
                    logger.info(f"   ✅ Медиа доступно: {file_info.file_id}")
                elif media_type == 'photo':
                    file_info = await self.application.bot.get_file(media_file_id)
                    logger.info(f"   ✅ Медиа доступно: {file_info.file_id}")
                elif media_type == 'animation':
                    file_info = await self.application.bot.get_file(media_file_id)
                    logger.info(f"   ✅ Медиа доступно: {file_info.file_id}")
                else:
                    logger.info(f"   ⚠️ Неизвестный тип медиа: {media_type}")
            except Exception as e:
                logger.warning(f"   ⚠️ Медиа недоступно: {e}")
                media_file_id = None  # Сбрасываем file_id если он недоступен
        elif media_type and not media_file_id:
            logger.info(f"   ⚠️ Медиа {media_type} есть, но file_id отсутствует")
        else:
            logger.info(f"   ℹ️ Медиа нет")

        # Сохраняем в базу
        success = self.db.add_content(
            message_id=orig_message_id,
            channel_id=channel_id,
            channel_username=channel_username,
            category=category,
            title=title,
            text=text,
            media_type=media_type,
            media_file_id=media_file_id
        )
        if success:
            category_name = self.analyzer.get_category_name(category)
            if manual_category:
                await message.reply_text(f"✅ Пост добавлен в категорию: {category_name} (ручная категоризация)")
            else:
                await message.reply_text(f"✅ Пост добавлен в категорию: {category_name}")
        else:
            await message.reply_text("❌ Не удалось добавить пост в базу данных.")
    
    async def load_posts_from_channel(self, update: Update, category: str) -> bool:
        """Загрузка постов из канала для конкретной категории"""
        try:
            # Проверяем доступ к каналу
            chat = await self.application.bot.get_chat(CHANNEL_USERNAME)
            logger.info(f"Канал найден: {chat.title}, ID: {chat.id}")
            
            # Получаем последние сообщения из канала
            messages = []
            
            # Способ 1: Попробуем получить через get_updates (единственный доступный способ)
                try:
                    logger.info(f"Пытаюсь получить сообщения через get_updates...")
                    updates = await self.application.bot.get_updates(limit=100, timeout=1)
                    logger.info(f"Получено {len(updates)} обновлений")
                    
                    for update_item in updates:
                        if update_item.channel_post and update_item.channel_post.chat.username == CHANNEL_USERNAME.replace('@', ''):
                            messages.append(update_item.channel_post)
                        await update.message.reply_text(f"✅ Получено {len(messages)} сообщений через get_updates")
                except Exception as e1:
                    await update.message.reply_text(f"⚠️ get_updates не работает: {e1}")
                    
                # Способ 2: Попробуем получить через webhook или другие методы
                try:
                    logger.info(f"Проверяю права бота в канале...")
                    member = await self.application.bot.get_chat_member(CHANNEL_USERNAME, self.application.bot.id)
                    logger.info(f"Права бота: {member.status}")
                    
                    if member.status in ['administrator', 'member']:
                        logger.info("✅ Бот имеет права в канале")
                        # К сожалению, без webhook или специальных прав получить историю канала сложно
                        logger.warning("⚠️ Для получения постов из канала нужен webhook или специальные права")
                    else:
                        logger.warning(f"❌ Бот не имеет прав в канале: {member.status}")
                        
                except Exception as e2:
                    logger.warning(f"❌ Не удалось проверить права бота: {e2}")
            
            if messages:
                logger.info(f"Обрабатываю {len(messages)} сообщений...")
                processed_count = 0
                for message in messages:
                    try:
                        # Извлекаем информацию о контенте
                        title, text = self.analyzer.extract_text_content(message)
                        media_type, media_file_id = self.analyzer.extract_media_info(message)
                        
                        # Категоризируем контент
                        message_category = self.analyzer.categorize_content(text, title)
                        
                        logger.info(f"Сообщение {message.message_id}: категория '{message_category}', нужна '{category}'")
                        
                        # Обрабатываем только посты нужной категории
                        if message_category == category:
                            # Получаем username канала
                            channel_username = message.chat.username or CHANNEL_USERNAME.replace('@', '')
                            
                            # Проверяем, не добавлен ли уже этот пост
                            existing_post = self.db.get_content_by_message_id(message.message_id)
                            if existing_post:
                                logger.info(f"Пост {message.message_id} уже существует в базе")
                                continue
                            
                            # Сохраняем в базу данных
                            success = self.db.add_content(
                                message_id=message.message_id,
                                channel_id=message.chat.id,
                                channel_username=channel_username,
                                category=message_category,
                                title=title,
                                text=text,
                                media_type=media_type,
                                media_file_id=media_file_id
                            )
                            
                            if success:
                                category_name = self.analyzer.get_category_name(message_category)
                                logger.info(f"✅ Сообщение {message.message_id} добавлено в категорию '{category_name}'")
                                processed_count += 1
                            else:
                                logger.warning(f"❌ Не удалось сохранить сообщение {message.message_id}")
                                
                    except Exception as e:
                        logger.error(f"❌ Ошибка при обработке сообщения {message.message_id}: {e}")
                
                logger.info(f"✅ Обработано {processed_count} постов для категории {category}")
                return processed_count > 0
            else:
                logger.warning("❌ Не удалось получить сообщения из канала")
                return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка при загрузке постов из канала: {e}")
            return False
    
    async def load_history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда для загрузки реальных постов из канала"""
        await update.message.reply_text("🔄 Загружаю реальные посты из канала @nikitaFlooDed...")
        
        try:
            # Проверяем доступ к каналу
            chat = await self.application.bot.get_chat(CHANNEL_USERNAME)
            await update.message.reply_text(f"✅ Канал найден: {chat.title}")
            
            # Получаем последние сообщения из канала
            try:
                # Получаем информацию о канале
                channel_id = chat.id
                await update.message.reply_text(f"📥 Получаю сообщения из канала (ID: {channel_id})...")
                
                # Пытаемся получить сообщения через get_updates
                messages = []
                
                    try:
                        updates = await self.application.bot.get_updates(limit=100, timeout=1)
                    for update_item in updates:
                        if update_item.channel_post and update_item.channel_post.chat.username == CHANNEL_USERNAME.replace('@', ''):
                            messages.append(update_item.channel_post)
                        await update.message.reply_text(f"✅ Получено {len(messages)} сообщений через get_updates")
                except Exception as e1:
                    await update.message.reply_text(f"⚠️ get_updates не работает: {e1}")
                        
                    # Проверяем права бота
                        try:
                        member = await self.application.bot.get_chat_member(CHANNEL_USERNAME, self.application.bot.id)
                        await update.message.reply_text(f"👤 Права бота: {member.status}")
                        
                        if member.status in ['administrator', 'member']:
                            await update.message.reply_text("✅ Бот имеет права в канале, но для получения истории нужен webhook")
                        else:
                            await update.message.reply_text(f"❌ Бот не имеет прав в канале: {member.status}")
                    except Exception as e2:
                        await update.message.reply_text(f"⚠️ Не удалось проверить права бота: {e2}")
                    
                else:
                    await update.message.reply_text("⚠️ Не удалось получить сообщения из канала.")
                
            except Exception as e:
                await update.message.reply_text(
                    f"⚠️ Не удалось получить историю канала: {e}\n\n"
                    "💡 Для получения постов из канала настройте webhook или используйте команду /load_hashtag #мемы"
                )
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ Ошибка при доступе к каналу: {e}\n\n"
                "💡 Проверьте, что бот добавлен в канал как администратор"
            )
    
    async def debug_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда для отладки"""
        await update.message.reply_text("🔍 Режим отладки...")
        
        try:
            # Проверяем доступ к каналу
            chat = await self.application.bot.get_chat(CHANNEL_USERNAME)
            await update.message.reply_text(f"✅ Канал найден: {chat.title}, ID: {chat.id}")
            
            # Проверяем права бота
            try:
                member = await self.application.bot.get_chat_member(CHANNEL_USERNAME, self.application.bot.id)
                await update.message.reply_text(f"👤 Права бота: {member.status}")
            except Exception as e:
                await update.message.reply_text(f"❌ Ошибка проверки прав: {e}")
            
            # Проверяем количество постов в базе
            stats = self.db.get_stats()
            await update.message.reply_text(f"📊 Постов в базе: {sum(stats.values()) if stats else 0}")
            
            # Проверяем посты в категории challenges
            challenges = self.db.get_content_by_category('challenges', limit=10)
            await update.message.reply_text(f"🎯 Постов в категории challenges: {len(challenges)}")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка отладки: {e}")
    
    async def category_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда для ручного указания категории при пересылке постов"""
        if not context.args or len(context.args) < 2:
            categories_text = "📁 Доступные категории:\n"
            for category_key, category_name in self.analyzer.get_all_categories().items():
                categories_text += f"• {category_key} - {category_name}\n"
            
            await update.message.reply_text(
                f"🏷️ Использование: /category <категория> <описание>\n\n"
                f"Примеры:\n"
                f"/category challenges Челлендж на отжимания\n"
                f"/category memes Смешной мем про спорт\n\n"
                f"{categories_text}\n"
                f"💡 Перешлите пост и сразу после него отправьте эту команду!"
            )
            return
        
        category = context.args[0].lower()
        description = " ".join(context.args[1:])
        
        # Проверяем, что категория существует
        if category not in self.analyzer.get_all_categories():
            await update.message.reply_text(f"❌ Неизвестная категория: {category}")
            return
        
        # Сохраняем информацию о последнем пересланном посте
        user_id = update.message.from_user.id
        if not hasattr(self, 'pending_categories'):
            self.pending_categories = {}
        
        self.pending_categories[user_id] = {
            'category': category,
            'description': description,
            'timestamp': update.message.date
        }
        
        category_name = self.analyzer.get_category_name(category)
        await update.message.reply_text(
            f"✅ Категория '{category_name}' установлена для следующего пересланного поста.\n\n"
            f"📝 Описание: {description}\n\n"
            f"💡 Теперь перешлите пост, который нужно добавить в эту категорию!"
        )
    
    async def load_posts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда для загрузки постов из канала"""
        await update.message.reply_text("🔄 Загружаю посты из канала...")
        await self.load_all_posts_on_startup()
        await update.message.reply_text("✅ Загрузка постов завершена!")
    
    async def load_hashtag_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Загрузка постов из канала для конкретной категории"""
        try:
            # Проверяем доступ к каналу
            chat = await self.application.bot.get_chat(CHANNEL_USERNAME)
            logger.info(f"Канал найден: {chat.title}, ID: {chat.id}")
            
            # Получаем последние сообщения из канала
            messages = []
            
            # Способ 1: Попробуем получить через get_updates (единственный доступный способ)
            try:
                logger.info(f"Пытаюсь получить сообщения через get_updates...")
                updates = await self.application.bot.get_updates(limit=100, timeout=1)
                logger.info(f"Получено {len(updates)} обновлений")
                
                for update_item in updates:
                    if update_item.channel_post and update_item.channel_post.chat.username == CHANNEL_USERNAME.replace('@', ''):
                        messages.append(update_item.channel_post)
                        logger.info(f"Найдено сообщение из канала: {update_item.channel_post.message_id}")
                
                logger.info(f"✅ Получено {len(messages)} сообщений через get_updates")
            except Exception as e1:
                logger.warning(f"❌ get_updates не работает: {e1}")
                
                # Способ 2: Попробуем получить через webhook или другие методы
                try:
                    logger.info(f"Проверяю права бота в канале...")
                    member = await self.application.bot.get_chat_member(CHANNEL_USERNAME, self.application.bot.id)
                    logger.info(f"Права бота: {member.status}")
                    
                    if member.status in ['administrator', 'member']:
                        logger.info("✅ Бот имеет права в канале")
                        # К сожалению, без webhook или специальных прав получить историю канала сложно
                        logger.warning("⚠️ Для получения постов из канала нужен webhook или специальные права")
                    else:
                        logger.warning(f"❌ Бот не имеет прав в канале: {member.status}")
                        
                except Exception as e2:
                    logger.warning(f"❌ Не удалось проверить права бота: {e2}")
            
            if messages:
                logger.info(f"Обрабатываю {len(messages)} сообщений...")
                processed_count = 0
                for message in messages:
                    try:
                        # Извлекаем информацию о контенте
                        title, text = self.analyzer.extract_text_content(message)
                        media_type, media_file_id = self.analyzer.extract_media_info(message)
                        
                        # Категоризируем контент
                        message_category = self.analyzer.categorize_content(text, title)
                        
                        logger.info(f"Сообщение {message.message_id}: категория '{message_category}', нужна '{category}'")
                        
                        # Обрабатываем только посты нужной категории
                        if message_category == category:
                            # Получаем username канала
                            channel_username = message.chat.username or CHANNEL_USERNAME.replace('@', '')
                            
                            # Проверяем, не добавлен ли уже этот пост
                            existing_post = self.db.get_content_by_message_id(message.message_id)
                            if existing_post:
                                logger.info(f"Пост {message.message_id} уже существует в базе")
                                continue
                            
                            # Сохраняем в базу данных
                            success = self.db.add_content(
                                message_id=message.message_id,
                                channel_id=message.chat.id,
                                channel_username=channel_username,
                                category=message_category,
                                title=title,
                                text=text,
                                media_type=media_type,
                                media_file_id=media_file_id
                            )
                            
                            if success:
                                category_name = self.analyzer.get_category_name(message_category)
                                logger.info(f"✅ Сообщение {message.message_id} добавлено в категорию '{category_name}'")
                                processed_count += 1
                            else:
                                logger.warning(f"❌ Не удалось сохранить сообщение {message.message_id}")
                                
                    except Exception as e:
                        logger.error(f"❌ Ошибка при обработке сообщения {message.message_id}: {e}")
                
                logger.info(f"✅ Обработано {processed_count} постов для категории {category}")
                return processed_count > 0
            else:
                logger.warning("❌ Не удалось получить сообщения из канала")
                return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка при загрузке постов из канала: {e}")
            return False
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error(f"Произошла ошибка: {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Произошла ошибка при обработке запроса. Попробуйте позже."
            )
    
    async def load_all_posts_on_startup(self):
        """Загрузка всех постов из канала при запуске бота"""
        try:
            logger.info("🚀 Запуск загрузки постов из канала при старте бота...")
            
            # Ждем немного, чтобы бот полностью запустился
            await asyncio.sleep(5)
            
            # Проверяем доступ к каналу
            try:
                chat = await self.application.bot.get_chat(CHANNEL_USERNAME)
                logger.info(f"✅ Канал найден: {chat.title}, ID: {chat.id}")
                
                # Проверяем права бота
                try:
                    member = await self.application.bot.get_chat_member(CHANNEL_USERNAME, self.application.bot.id)
                    logger.info(f"👤 Права бота: {member.status}")
                    
                    if member.status not in ['administrator', 'member']:
                        logger.warning(f"❌ Бот не имеет прав в канале: {member.status}")
                        return
                        
                except Exception as e:
                    logger.warning(f"❌ Не удалось проверить права бота: {e}")
                    return
                
                # Пытаемся получить сообщения из канала через get_updates
                messages = []
                try:
                    logger.info("📥 Получаю сообщения из канала...")
                    updates = await self.application.bot.get_updates(limit=100, timeout=1)
                    for update_item in updates:
                        if update_item.channel_post and update_item.channel_post.chat.username == CHANNEL_USERNAME.replace('@', ''):
                            messages.append(update_item.channel_post)
                    logger.info(f"✅ Получено {len(messages)} сообщений из канала")
                except Exception as e:
                    logger.warning(f"❌ Не удалось получить сообщения: {e}")
                    return
                
                if messages:
                    processed_count = 0
                    for message in messages:
                        try:
                            # Проверяем, не добавлен ли уже этот пост
                            existing_post = self.db.get_content_by_message_id(message.message_id)
                            if existing_post:
                                logger.info(f"Пост {message.message_id} уже существует в базе")
                                continue
                            
                            # Извлекаем информацию о контенте
                            title, text = self.analyzer.extract_text_content(message)
                            media_type, media_file_id = self.analyzer.extract_media_info(message)
                            
                            # Категоризируем контент
                            category = self.analyzer.categorize_content(text, title)
                            
                            # Получаем username канала
                            channel_username = message.chat.username or CHANNEL_USERNAME.replace('@', '')
                            
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
                                processed_count += 1
                                
                        except Exception as e:
                            logger.error(f"❌ Ошибка при обработке сообщения {message.message_id}: {e}")
                    
                    logger.info(f"✅ При запуске обработано {processed_count} постов из канала")
                else:
                    logger.warning("❌ Не удалось получить сообщения из канала при запуске")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка при доступе к каналу при запуске: {e}")
                
        except Exception as e:
            logger.error(f"❌ Общая ошибка при загрузке постов при запуске: {e}")
    
    def run(self):
        """Запуск бота с периодической загрузкой новых постов"""
        logger.info("🚀 Запуск Fitness Content Sorter Bot...")
        
        # Запускаем бота в отдельной задаче
        async def run_bot_with_auto_load():
            # Запускаем бота
            await self.application.initialize()
            await self.application.start()
            
            # Загружаем посты при запуске
            await self.load_all_posts_on_startup()
            
            # Запускаем периодическую загрузку новых постов
            async def auto_load_task():
                while True:
                    try:
                        await asyncio.sleep(300)  # Каждые 5 минут
                        await self.auto_load_new_posts()
                    except Exception as e:
                        logger.error(f"❌ Ошибка в задаче автоматической загрузки: {e}")
                        await asyncio.sleep(60)  # Ждем минуту перед повторной попыткой
            
            # Запускаем задачу автоматической загрузки
            asyncio.create_task(auto_load_task())
            
            # Запускаем бота
            await self.application.run_polling(allowed_updates=Update.ALL_TYPES)
        
        # Запускаем асинхронную функцию
        asyncio.run(run_bot_with_auto_load())

if __name__ == "__main__":
    bot = ContentBot()
    bot.run() 