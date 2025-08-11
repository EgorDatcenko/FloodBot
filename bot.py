import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError
from telegram.constants import MessageOriginType
import asyncio
from datetime import datetime

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
        # Команды - оставляем только /start
        self.application.add_handler(CommandHandler("start", self.start_command))
        
        # Обработка inline кнопок
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Обработка текстовых сообщений (для меню)
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.text_message_handler))
        
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

Этот бот автоматически сортирует контент из каналов @nikitaFlooDed и Флудские ТРЕНИ по категориям.

📋 Выберите категорию из меню ниже:
        """
        
        keyboard = self.create_main_keyboard()
        await update.message.reply_text(welcome_text, reply_markup=keyboard)
        
        # Загружаем посты при первом запуске
        await update.message.reply_text("🔄 Загружаю посты из каналов...")
        await self.auto_load_new_posts()
        
        # Обновляем статистику и получаем актуальные данные
        self.db.update_all_stats()
        total_posts = self.db.get_total_posts_count()
        
        await update.message.reply_text(
            f"✅ Загрузка завершена!\n\n"
            f"📊 Всего постов в базе: {total_posts}\n\n"
            f"💡 Используйте кнопки меню для просмотра категорий!"
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
            # Показываем актуальную статистику
            self.db.update_all_stats()  # Обновляем статистику
            stats = self.db.get_real_stats()  # Получаем актуальные данные
            total_posts = self.db.get_total_posts_count()
            
            if not stats:
                await query.edit_message_text("📊 Статистика пока недоступна.")
                return
            
            stats_text = "📊 Статистика по категориям:\n\n"
            
            for category, count in stats.items():
                category_name = self.analyzer.get_category_name(category)
                stats_text += f"📁 {category_name}: {count} постов\n"
            
            stats_text += f"\n📈 Всего постов: {total_posts}"
            await query.edit_message_text(stats_text)
        elif data == "back_to_main":
            # Возвращаемся к главному меню
            welcome_text = """
🏋️‍♂️ Добро пожаловать в Fitness Content Sorter Bot!

Этот бот автоматически сортирует контент из каналов @nikitaFlooDed и Флудские ТРЕНИ по категориям.

📋 Выберите категорию из меню ниже:
            """
            keyboard = self.create_main_keyboard()
            await query.edit_message_text(welcome_text, reply_markup=keyboard)
        else:
            await query.edit_message_text("❓ Используйте кнопки меню для навигации.")
    
    async def auto_load_new_posts(self):
        """Автоматическая загрузка новых постов из канала"""
        try:
            logger.info("🔄 Автоматическая загрузка новых постов...")
            
            # Получаем последние сообщения из канала
            try:
                chat = await self.application.bot.get_chat(CHANNEL_USERNAME)
                logger.info(f"✅ Канал найден: {chat.title}")
                
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
                
                # Получаем последние сообщения из канала
                try:
                    logger.info("📥 Получаю последние сообщения из канала...")
                    
                    # Получаем последние сообщения через get_updates
                    messages = []
                    
                    try:
                        updates = await self.application.bot.get_updates(limit=100, timeout=1)
                        for update_item in updates:
                            if update_item.channel_post and update_item.channel_post.chat.username == CHANNEL_USERNAME.replace('@', ''):
                                messages.append(update_item.channel_post)
                        logger.info(f"📥 Получено {len(messages)} сообщений через get_updates")
                    except Exception as e:
                        logger.warning(f"❌ get_updates не работает: {e}")
                    
                    # Если сообщений нет, попробуем получить через webhook или другие способы
                    if not messages:
                        logger.info("📥 Новых сообщений нет, попробуем получить через другие способы...")
                        
                        # Попробуем получить последние сообщения через get_chat
                        try:
                            # Получаем информацию о канале
                            channel_info = await self.application.bot.get_chat(CHANNEL_USERNAME)
                            logger.info(f"📊 Информация о канале: {channel_info.title}, ID: {channel_info.id}")
                            
                            # К сожалению, без webhook получить историю канала сложно
                            # Но можем попробовать получить последние сообщения через другие методы
                            logger.info("⚠️ Для получения истории канала нужен webhook или специальные права")
                            
                        except Exception as e:
                            logger.warning(f"❌ Не удалось получить информацию о канале: {e}")
                    
                    logger.info(f"📥 Всего получено {len(messages)} сообщений из канала")
                    
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
                                    logger.info(f"✅ Новый пост {message.message_id} добавлен в категорию '{category_name}'")
                                    processed_count += 1
                                    
                            except Exception as e:
                                logger.error(f"❌ Ошибка при обработке сообщения {message.message_id}: {e}")
                        
                        if processed_count > 0:
                            logger.info(f"✅ Автоматически обработано {processed_count} новых постов")
                        else:
                            logger.info("ℹ️ Новых постов для обработки не найдено")
                    else:
                        logger.info("ℹ️ Сообщений из канала не найдено")
                        
                except Exception as e:
                    logger.warning(f"❌ Не удалось получить сообщения из канала: {e}")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка при доступе к каналу: {e}")
                
        except Exception as e:
            logger.error(f"❌ Общая ошибка при автоматической загрузке: {e}")
    
    async def show_category_content(self, query, category: str):
        """Показать контент выбранной категории с улучшенной обработкой медиа"""
        # Сначала загружаем новые посты
        await self.auto_load_new_posts()
        
        # Сначала пробуем получить контент с медиафайлами из таблицы post_media
        content = self.db.get_content_with_media_files(category, limit=50)
        
        # Если не получилось, используем старый метод для получения постов
        if not content:
            logger.info(f"📁 Не удалось получить контент через get_content_with_media_files, используем старый метод")
            content = self.db.get_content_by_category(category, limit=50)
            
            # Преобразуем старые посты в новый формат
            for item in content:
                media_type = item.get('media_type')
                media_file_id = item.get('media_file_id')
                
                if media_type and media_file_id:
                    # Создаем медиафайл в новом формате
                    item['media_files'] = [{
                        'media_type': media_type,
                        'media_file_id': media_file_id,
                        'media_order': 0
                    }]
                else:
                    item['media_files'] = []
        
        category_name = self.analyzer.get_category_name(category)
        
        logger.info(f"📁 Получено {len(content)} постов для категории '{category}'")
        for i, item in enumerate(content, 1):
            media_files = item.get('media_files', [])
            logger.info(f"   {i}. Пост {item['id']}: '{item['title'][:30]}...' - медиафайлов: {len(media_files)}")
            if media_files:
                for j, media in enumerate(media_files, 1):
                    logger.info(f"      {j}. {media['media_type']}: {media['media_file_id'][:20]}... (порядок: {media['media_order']})")
        
        if not content:
            await query.edit_message_text(
                f"📁 Категория '{category_name}' пока пуста.\n\n💡 Пересылайте сообщения из каналов @nikitaFlooDed или Флудские ТРЕНИ для добавления контента.",
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
                message_id = item['message_id']
                channel_id = item.get('channel_id')
                media_files = item.get('media_files', [])
                
                caption = f"📝 <b>{title}</b>\n\n{text}"
                
                # Пытаемся переслать оригинальное сообщение только если есть channel_id
                if channel_id:
                    try:
                        await self.application.bot.forward_message(
                            chat_id=query.from_user.id,
                            from_chat_id=channel_id,
                            message_id=message_id
                        )
                        logger.info(f"✅ Переслан оригинальный пост {message_id} из канала {channel_id}")
                        continue
                    except Exception as forward_error:
                        logger.warning(f"⚠️ Не удалось переслать пост {message_id}: {forward_error}")
                        # Продолжаем с отправкой через file_id
                
                # Отправляем контент с медиафайлами
                if media_files:
                    logger.info(f"📤 Отправляю пост {item['id']} с {len(media_files)} медиафайлами")
                    if len(media_files) > 1:
                        # Отправляем как медиа-группу
                        logger.info(f"   📱 Отправляю как медиа-группу: {len(media_files)} файлов")
                        await self._send_media_group(query.from_user.id, media_files, caption)
                    else:
                        # Отправляем как одиночное медиа
                        logger.info(f"   📱 Отправляю как одиночное медиа: {media_files[0]['media_type']}")
                        await self._send_single_media(query.from_user.id, media_files[0], caption)
                else:
                    logger.info(f"📤 Отправляю пост {item['id']} без медиафайлов")
                    # Отправляем только текст
                    await self.application.bot.send_message(
                        chat_id=query.from_user.id,
                        text=caption,
                        parse_mode='HTML'
                    )
                
                # Небольшая задержка между постами
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Ошибка при отправке поста {item.get('id', 'unknown')}: {e}")
                # Отправляем упрощенную версию поста
                try:
                    await self.application.bot.send_message(
                        chat_id=query.from_user.id,
                        text=f"📝 <b>{item.get('title', 'Без заголовка')}</b>\n\n{item.get('text', 'Нет текста')}",
                        parse_mode='HTML'
                    )
                except Exception as simple_error:
                    logger.error(f"Не удалось отправить упрощенную версию поста: {simple_error}")
        
        # Показываем кнопку "Назад" после отправки всех постов
        await query.edit_message_text(
            f"✅ Отправлено {len(content)} постов из категории '{category_name}'\n\n🔙 Используйте кнопку ниже для возврата в главное меню",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
            ]])
        )
    
    async def _send_single_media(self, chat_id: int, media: dict, caption: str):
        """Отправка одного медиафайла"""
        media_type = media['media_type']
        media_file_id = media['media_file_id']
        
        try:
            # Проверяем доступность медиа
            file_info = await self.application.bot.get_file(media_file_id)
            if not file_info or not file_info.file_id:
                raise Exception("Медиа недоступно")
            
            if media_type == 'video':
                await self.application.bot.send_video(
                    chat_id=chat_id,
                    video=media_file_id,
                    caption=caption,
                    parse_mode='HTML'
                )
            elif media_type == 'photo':
                await self.application.bot.send_photo(
                    chat_id=chat_id,
                    photo=media_file_id,
                    caption=caption,
                    parse_mode='HTML'
                )
            elif media_type == 'animation':
                await self.application.bot.send_animation(
                    chat_id=chat_id,
                    animation=media_file_id,
                    caption=caption,
                    parse_mode='HTML'
                )
            elif media_type == 'audio':
                await self.application.bot.send_audio(
                    chat_id=chat_id,
                    audio=media_file_id,
                    caption=caption,
                    parse_mode='HTML'
                )
            elif media_type == 'document':
                await self.application.bot.send_document(
                    chat_id=chat_id,
                    document=media_file_id,
                    caption=caption,
                    parse_mode='HTML'
                )
            elif media_type == 'voice':
                await self.application.bot.send_voice(
                    chat_id=chat_id,
                    voice=media_file_id,
                    caption=caption,
                    parse_mode='HTML'
                )
            elif media_type == 'video_note':
                await self.application.bot.send_video_note(
                    chat_id=chat_id,
                    video_note=media_file_id
                )
                # Отправляем текст отдельно для video_note
                await self.application.bot.send_message(
                    chat_id=chat_id,
                    text=caption,
                    parse_mode='HTML'
                )
            elif media_type == 'sticker':
                await self.application.bot.send_sticker(
                    chat_id=chat_id,
                    sticker=media_file_id
                )
                # Отправляем текст отдельно для стикеров
                await self.application.bot.send_message(
                    chat_id=chat_id,
                    text=caption,
                    parse_mode='HTML'
                )
            else:
                # Для других типов медиа отправляем только текст
                await self.application.bot.send_message(
                    chat_id=chat_id,
                    text=caption,
                    parse_mode='HTML'
                )
                
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке медиа {media_type}: {e}")
            # Отправляем только текст
            try:
                await self.application.bot.send_message(
                    chat_id=chat_id,
                    text=f"{caption}\n\n⚠️ Медиа недоступно",
                    parse_mode='HTML'
                )
            except:
                pass
    
    async def _send_media_group(self, chat_id: int, media_files: list, caption: str):
        """Отправка группы медиафайлов"""
        try:
            from telegram import InputMediaPhoto, InputMediaVideo, InputMediaAnimation, InputMediaAudio, InputMediaDocument
            
            media_group = []
            caption_added = False
            
            for media in media_files:
                media_type = media['media_type']
                media_file_id = media['media_file_id']
                
                # Проверяем доступность медиа
                try:
                    file_info = await self.application.bot.get_file(media_file_id)
                    if not file_info or not file_info.file_id:
                        continue
                except:
                    continue
                
                # Добавляем caption только к первому медиа
                current_caption = caption if not caption_added else ""
                caption_added = True
                
                if media_type == 'photo':
                    media_group.append(InputMediaPhoto(
                        media=media_file_id,
                        caption=current_caption,
                        parse_mode='HTML'
                    ))
                elif media_type == 'video':
                    media_group.append(InputMediaVideo(
                        media=media_file_id,
                        caption=current_caption,
                        parse_mode='HTML'
                    ))
                elif media_type == 'animation':
                    media_group.append(InputMediaAnimation(
                        media=media_file_id,
                        caption=current_caption,
                        parse_mode='HTML'
                    ))
                elif media_type == 'audio':
                    media_group.append(InputMediaAudio(
                        media=media_file_id,
                        caption=current_caption,
                        parse_mode='HTML'
                    ))
                elif media_type == 'document':
                    media_group.append(InputMediaDocument(
                        media=media_file_id,
                        caption=current_caption,
                        parse_mode='HTML'
                    ))
            
            if media_group:
                await self.application.bot.send_media_group(
                    chat_id=chat_id,
                    media=media_group
                )
            else:
                # Если ни одно медиа не доступно, отправляем только текст
                await self.application.bot.send_message(
                    chat_id=chat_id,
                    text=caption,
                    parse_mode='HTML'
                )
                
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке медиа-группы: {e}")
            # Отправляем только текст
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=caption,
                parse_mode='HTML'
            )
    
    def create_categories_keyboard(self) -> InlineKeyboardMarkup:
        """Создание клавиатуры с категориями"""
        categories = self.analyzer.get_all_categories()
        keyboard = []
        
        for category_key, category_name in categories.items():
            keyboard.append([InlineKeyboardButton(
                f"{category_name}", 
                callback_data=f"category_{category_key}"
            )])
        
        # Добавляем кнопку "Назад"
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])
        
        return InlineKeyboardMarkup(keyboard)
    
    def create_main_keyboard(self) -> ReplyKeyboardMarkup:
        """Создание основной клавиатуры с черным текстом для мобильных устройств"""
        keyboard = [
            [KeyboardButton("🎯 ЧЕЛЛЕНДЖИ"), KeyboardButton("💪 СИЛОВЫЕ")],
            [KeyboardButton("💡 СПОРТ СОВЕТЫ"), KeyboardButton("😄 МЕМЫ")],
            [KeyboardButton("🏋️‍♂️ УПРАЖНЕНИЯ"), KeyboardButton("🌊 ФЛУДЩИНА")],
            [KeyboardButton("📊 СТАТИСТИКА"), KeyboardButton("📁 ДРУГОЕ")]
        ]
        return ReplyKeyboardMarkup(
            keyboard, 
            resize_keyboard=True, 
            one_time_keyboard=False,
            input_field_placeholder="Выберите категорию...",
            selective=False
        )
    
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

    async def text_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений для меню"""
        text = update.message.text
        
        if text == "🎯 ЧЕЛЛЕНДЖИ":
            await self.show_category_content_text(update, "challenges")
        elif text == "💪 СИЛОВЫЕ":
            await self.show_category_content_text(update, "power_results")
        elif text == "💡 СПОРТ СОВЕТЫ":
            await self.show_category_content_text(update, "sport_tips")
        elif text == "😄 МЕМЫ":
            await self.show_category_content_text(update, "memes")
        elif text == "🏋️‍♂️ УПРАЖНЕНИЯ":
            await self.show_category_content_text(update, "exercises")
        elif text == "🌊 ФЛУДЩИНА":
            await self.show_category_content_text(update, "flood")
        elif text == "📁 ДРУГОЕ":
            await self.show_category_content_text(update, "other")
        elif text == "📊 СТАТИСТИКА":
            # Показываем актуальную статистику
            self.db.update_all_stats()  # Обновляем статистику
            stats = self.db.get_real_stats()  # Получаем актуальные данные
            total_posts = self.db.get_total_posts_count()
            
            if not stats:
                await update.message.reply_text("📊 Статистика пока недоступна.")
                return
            
            stats_text = "📊 Статистика по категориям:\n\n"
            
            for category, count in stats.items():
                category_name = self.analyzer.get_category_name(category)
                stats_text += f"📁 {category_name}: {count} постов\n"
            
            stats_text += f"\n📈 Всего постов: {total_posts}"
            await update.message.reply_text(stats_text)
        else:
            await update.message.reply_text("❓ Используйте кнопки меню для навигации.")
    
    async def get_posts_by_hashtag(self, hashtag: str, limit: int = 10) -> list:
        """Получение постов с конкретным хештегом из канала"""
        try:
            logger.info(f"🔍 Ищу посты с хештегом {hashtag} в канале...")
            
            # Добавляем задержку перед запросом
            await asyncio.sleep(1)
            
            posts_with_hashtag = []
            
            # Получаем через get_updates
            try:
                updates = await self.application.bot.get_updates(limit=100, timeout=5)
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
            except Exception as e:
                logger.warning(f"❌ get_updates не работает: {e}")
            
            logger.info(f"📊 Найдено {len(posts_with_hashtag)} постов с хештегом {hashtag}")
            return posts_with_hashtag
        except Exception as e:
            logger.error(f"❌ Ошибка при получении постов с хештегом {hashtag}: {e}")
            return []
    
    async def show_category_content_text(self, update: Update, category: str):
        """Показать контент категории через сообщения от бота (с медиа, если есть)"""
        # Сначала загружаем новые посты
        await self.auto_load_new_posts()
        
        # Сначала пробуем получить контент с медиафайлами из таблицы post_media
        content = self.db.get_content_with_media_files(category, limit=50)
        
        # Если не получилось, используем старый метод для получения постов
        if not content:
            logger.info(f"📁 Не удалось получить контент через get_content_with_media_files, используем старый метод")
            content = self.db.get_content_by_category(category, limit=50)
            
            # Преобразуем старые посты в новый формат
            for item in content:
                media_type = item.get('media_type')
                media_file_id = item.get('media_file_id')
                
                if media_type and media_file_id:
                    # Создаем медиафайл в новом формате
                    item['media_files'] = [{
                        'media_type': media_type,
                        'media_file_id': media_file_id,
                        'media_order': 0
                    }]
                else:
                    item['media_files'] = []
        
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
                        media_group_id = getattr(message, 'media_group_id', None)
                        
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
                            media_file_id=media_file_id,
                            media_group_id=media_group_id
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
                    
                    # Преобразуем новые посты в новый формат
                    for item in content:
                        media_type = item.get('media_type')
                        media_file_id = item.get('media_file_id')
                        
                        if media_type and media_file_id:
                            # Создаем медиафайл в новом формате
                            item['media_files'] = [{
                                'media_type': media_type,
                                'media_file_id': media_file_id,
                                'media_order': 0
                            }]
                        else:
                            item['media_files'] = []
                else:
                    await update.message.reply_text(
                        f"❌ Не удалось добавить новые посты в категорию '{category_name}'"
                    )
                    return
        
        await update.message.reply_text(
            f"📁 Категория: {category_name}\nНайдено постов: {len(content)}\n\nПоказываю посты..."
        )
        
        for item in content:
            title = item['title'] or "Без заголовка"
            text = item['text'] or "Нет текста"
            channel_id = item.get('channel_id')
            media_files = item.get('media_files', [])
            caption = f"📝 <b>{title}</b>\n\n{text}"
            
            # Логируем информацию о посте для отладки
            logger.info(f"📤 Отправляю пост {item['message_id']}:")
            logger.info(f"   Медиафайлов: {len(media_files)}")
            for i, media in enumerate(media_files, 1):
                logger.info(f"   {i}. {media['media_type']}: {media['media_file_id'][:20]}...")
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
                # Пытаемся переслать оригинальное сообщение только если есть channel_id
                if channel_id:
                    try:
                        await self.application.bot.forward_message(
                            chat_id=chat_id,
                            from_chat_id=channel_id,
                            message_id=item['message_id']
                        )
                        logger.info(f"✅ Переслан оригинальный пост {item['message_id']} из канала {channel_id}")
                        continue
                    except Exception as forward_error:
                        logger.warning(f"⚠️ Не удалось переслать пост {item['message_id']}: {forward_error}")
                        # Продолжаем с отправкой через file_id
                
                # Отправляем контент с медиафайлами
                if media_files:
                    # Если есть несколько медиафайлов, отправляем их группой
                    if len(media_files) > 1:
                        await self._send_media_group(chat_id, media_files, caption)
                    else:
                        # Один медиафайл
                        media = media_files[0]
                        await self._send_single_media(chat_id, media, caption)
                else:
                    # Только текст
                    await self.application.bot.send_message(
                        chat_id=chat_id,
                        text=caption,
                        parse_mode='HTML'
                    )
                    
            except Exception as e:
                logger.error(f"❌ Ошибка при отправке поста {item.get('message_id', 'unknown')}: {e}")
                # Отправляем хотя бы текст
                try:
                    await self.application.bot.send_message(
                        chat_id=chat_id,
                        text=f"{caption}\n\n⚠️ Ошибка при отправке медиа",
                        parse_mode='HTML'
                    )
                except:
                    pass
        
        # Показываем клавиатуру снова после отправки всех постов
        keyboard = self.create_main_keyboard()
        await update.message.reply_text(
            f"✅ Отправлено {len(content)} постов из категории '{category_name}'\n\n"
            f"💡 Используйте кнопки меню для просмотра других категорий!",
            reply_markup=keyboard
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
            
            # Проверяем медиа-группу
            media_group_id = getattr(message, 'media_group_id', None)
            
            # Проверяем, не добавлен ли уже этот пост
            existing_post = None
            if media_group_id:
                # Для медиа-группы проверяем по media_group_id
                existing_post = self.db.get_content_by_media_group_id(media_group_id)
                if existing_post:
                    logger.info(f"📱 Медиа-группа {media_group_id} уже существует в базе данных")
                    # НЕ возвращаемся - добавляем медиафайлы к существующему посту
                    logger.info(f"   📱 Добавляю медиафайлы к существующему посту {existing_post['id']}")
                else:
                    logger.info(f"📱 Новая медиа-группа {media_group_id}")
            else:
                # Для обычного сообщения проверяем по message_id
                existing_post = self.db.get_content_by_message_id(message.message_id)
                if existing_post:
                    logger.info(f"📱 Пост {message.message_id} уже существует в базе данных")
                    return
            
            # Извлекаем информацию о контенте
            title, text = self.analyzer.extract_text_content(message)
            media_type, media_file_id = self.analyzer.extract_media_info(message)
            
            # Извлекаем хештеги для логирования
            hashtags = self.analyzer.extract_hashtags(f"{title} {text}")
            
            # Категоризируем контент
            category = self.analyzer.categorize_content(text, title)
            
            # ВАЖНО: Если это медиа-группа и у нас есть существующий пост,
            # используем категорию существующего поста для сохранения целостности
            if media_group_id and existing_post:
                category = existing_post['category']
                logger.info(f"📱 Использую категорию существующего поста: {category}")
            
            # Получаем username канала
            channel_username = message.chat.username or "unknown_channel"
            
            logger.info(f"   📝 Заголовок: {title[:50]}...")
            logger.info(f"   📄 Текст: {text[:100]}...")
            logger.info(f"   🏷️ Хештеги: {hashtags}")
            logger.info(f"   📁 Категория: {category}")
            logger.info(f"   🎬 Медиа: {media_type}")
            logger.info(f"   📱 Медиа-группа ID: {media_group_id}")
            
            # Сохраняем в базу данных
            success = True
            content_id = None
            
            if existing_post and media_group_id:
                # Пост уже существует для медиа-группы, используем его ID
                content_id = existing_post['id']
                logger.info(f"📱 Использую существующий пост {content_id} для медиа-группы")
            else:
                # Создаем новый пост
                success = self.db.add_content(
                    message_id=message.message_id,
                    channel_id=message.chat.id,
                    channel_username=channel_username,
                    category=category,
                    title=title,
                    text=text,
                    media_type=media_type,
                    media_file_id=media_file_id,
                    media_group_id=media_group_id
                )
                
                if success:
                    # Получаем ID созданного поста
                    if media_group_id:
                        content = self.db.get_content_by_media_group_id(media_group_id)
                    else:
                        content = self.db.get_content_by_message_id(message.message_id)
                    
                    if content:
                        content_id = content['id']
                        logger.info(f"📱 Создан новый пост {content_id}")
                    else:
                        logger.error(f"❌ Не удалось получить ID созданного поста")
                        success = False
                else:
                    logger.error(f"❌ Не удалось создать новый пост")
            
            # Если это медиа-группа, добавляем все медиафайлы
            if media_group_id and success and content_id:
                # Извлекаем все медиа из группы
                all_media = self.analyzer.extract_all_media_info(message)
                logger.info(f"   📊 Добавляю {len(all_media)} медиафайлов в группу")
                
                for i, (m_type, m_id) in enumerate(all_media, 1):
                    try:
                        # Проверяем доступность каждого медиафайла
                        file_info = await self.application.bot.get_file(m_id)
                        if file_info and file_info.file_id:
                            # Добавляем медиафайл в базу данных
                            self.db.add_media_to_post(content_id, message.message_id, m_type, m_id, i)
                            logger.info(f"   ✅ Добавлен медиафайл {i}: {m_type} - {m_id[:20]}...")
                        else:
                            logger.warning(f"   ⚠️ Медиафайл {i} недоступен: {m_type}")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Ошибка при добавлении медиафайла {i}: {e}")
            
            if success:
                category_name = self.analyzer.get_category_name(category)
                hashtags_str = " ".join(hashtags) if hashtags else "без хештегов"
                
                if media_group_id and existing_post:
                    action_text = "добавлены медиафайлы к посту"
                elif media_group_id:
                    action_text = "создан новый пост с медиа-группой"
                else:
                    action_text = "добавлен пост"
                
                logger.info(f"✅ {action_text} {message.message_id} из канала {channel_username} в категорию '{category_name}' (хештеги: {hashtags_str})")
            else:
                logger.error(f"❌ Ошибка при сохранении сообщения {message.message_id}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка при обработке сообщения из канала: {e}")
            if message:
                logger.error(f"   ID сообщения: {message.message_id}")
                logger.error(f"   Текст: {getattr(message, 'text', 'Нет текста')}")
                logger.error(f"   Канал: {getattr(message.chat, 'username', 'Нет username')}")
    
    async def forwarded_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик пересланных сообщений из канала с улучшенной обработкой медиа"""
        message = update.message
        
        try:
            # Проверяем, что это переслано из канала
            if not message or not hasattr(message, 'forward_origin') or not message.forward_origin:
                logger.info("📱 Сообщение не является пересланным из канала")
                return

            # Проверяем тип origin
            if message.forward_origin.type != MessageOriginType.CHANNEL:
                await message.reply_text("⚠️ Это сообщение не из канала.")
                return

            channel = message.forward_origin.chat
            channel_username = getattr(channel, 'username', None)
            channel_title = getattr(channel, 'title', None)
            orig_message_id = message.forward_origin.message_id

            # Проверяем, что сообщение из разрешенных каналов
            allowed_channels = ['nikitaFlooDed', 'Флудские ТРЕНИ']
            is_allowed = False
            
            if channel_username:
                # Проверяем по username
                if channel_username in allowed_channels:
                    is_allowed = True
            elif channel_title:
                # Проверяем по названию канала
                if channel_title in allowed_channels:
                    is_allowed = True
            
            if not is_allowed:
                await message.reply_text(
                    "❌ Сообщения из этого канала не принимаются.\n\n"
                    "✅ Разрешены только сообщения из каналов:\n"
                    "• @nikitaFlooDed (ХАТАуФЛУДА)\n"
                    "• Флудские ТРЕНИ"
                )
                return

            # Проверяем медиа-группу
            media_group_id = getattr(message, 'media_group_id', None)

            # Проверяем, не добавлен ли уже этот пост
            existing_post = None
            if media_group_id:
                # Для медиа-группы проверяем по media_group_id
                existing_post = self.db.get_content_by_media_group_id(media_group_id)
                if existing_post:
                    logger.info(f"📱 Медиа-группа {media_group_id} уже существует в базе данных")
                    # НЕ возвращаемся - добавляем медиафайлы к существующему посту
                    logger.info(f"   📱 Добавляю медиафайлы к существующему посту {existing_post['id']}")
                else:
                    logger.info(f"📱 Новая медиа-группа {media_group_id}")
            else:
                # Для обычного сообщения проверяем по message_id
                existing_post = self.db.get_content_by_message_id(orig_message_id)
                if existing_post:
                    logger.info(f"📱 Пост {orig_message_id} уже существует в базе данных")
                    await message.reply_text("✅ Этот пост уже добавлен в базу данных.")
                    return

            # Извлекаем данные
            title, text = self.analyzer.extract_text_content(message)
            media_type, media_file_id = self.analyzer.extract_media_info(message)
            
            # Подробное логирование для отладки
            logger.info(f"📱 Пересланное сообщение {orig_message_id} из канала {channel_username or channel_title}:")
            logger.info(f"   Медиа тип: {media_type}")
            logger.info(f"   Медиа file_id: {media_file_id}")
            logger.info(f"   Медиа-группа ID: {media_group_id}")
            logger.info(f"   Заголовок: {title[:50]}...")
            logger.info(f"   Текст: {text[:100]}...")
            
            # Дополнительная информация о медиа-группе
            if media_group_id:
                logger.info(f"   📱 Медиа-группа ID: {media_group_id}")
                # Извлекаем все медиа из группы для анализа
                all_media = self.analyzer.extract_all_media_info(message)
                logger.info(f"   📊 Всего медиа в группе: {len(all_media)}")
                for i, (m_type, m_id) in enumerate(all_media, 1):
                    logger.info(f"   {i}. {m_type}: {m_id[:20]}...")

            # Проверяем доступность медиа с улучшенной обработкой
            media_available = False
            if media_type and media_file_id:
                try:
                    # Пробуем получить информацию о файле для проверки доступности
                    if media_type in ['video', 'photo', 'animation', 'audio', 'document', 'voice', 'video_note', 'sticker']:
                        file_info = await self.application.bot.get_file(media_file_id)
                        if file_info and file_info.file_id:
                            media_available = True
                            logger.info(f"   ✅ Медиа доступно: {file_info.file_id}")
                        else:
                            logger.warning(f"   ⚠️ Медиа недоступно: file_info пустой")
                            media_file_id = None
                    else:
                        logger.info(f"   ⚠️ Неизвестный тип медиа: {media_type}")
                        media_file_id = None
                except Exception as e:
                    logger.warning(f"   ⚠️ Медиа недоступно: {e}")
                    media_file_id = None  # Сбрасываем file_id если он недоступен
            elif media_type and not media_file_id:
                logger.info(f"   ⚠️ Медиа {media_type} есть, но file_id отсутствует")
            else:
                logger.info(f"   ℹ️ Медиа нет")
                            
            # Категоризируем контент
            category = self.analyzer.categorize_content(text, title)
            
            # ВАЖНО: Если это медиа-группа и у нас есть существующий пост,
            # используем категорию существующего поста для сохранения целостности
            if media_group_id and existing_post:
                category = existing_post['category']
                logger.info(f"📱 Использую категорию существующего поста: {category}")
                            
            # Получаем username канала
            channel_username = channel_username or channel_title or "unknown_channel"
                                
            # Сохраняем в базу данных только если это новый пост
            success = True
            content_id = None
            
            if existing_post and media_group_id:
                # Пост уже существует для медиа-группы, используем его ID
                content_id = existing_post['id']
                logger.info(f"📱 Использую существующий пост {content_id} для медиа-группы")
            else:
                # Создаем новый пост
                success = self.db.add_content(
                    message_id=orig_message_id,
                    channel_id=channel.id,
                    channel_username=channel_username,
                    category=category,
                    title=title,
                    text=text,
                    media_type=media_type,
                    media_file_id=media_file_id,
                    media_group_id=media_group_id
                )
                
                if success:
                    # Получаем ID созданного поста
                    if media_group_id:
                        content = self.db.get_content_by_media_group_id(media_group_id)
                    else:
                        content = self.db.get_content_by_message_id(orig_message_id)
                    
                    if content:
                        content_id = content['id']
                        logger.info(f"📱 Создан новый пост {content_id}")
                    else:
                        logger.error(f"❌ Не удалось получить ID созданного поста")
                        success = False
                else:
                    logger.error(f"❌ Не удалось создать новый пост")
            
            # Если это медиа-группа, добавляем все медиафайлы
            if media_group_id and success and content_id:
                # Извлекаем все медиа из группы
                all_media = self.analyzer.extract_all_media_info(message)
                logger.info(f"   📊 Добавляю {len(all_media)} медиафайлов в группу")
                
                for i, (m_type, m_id) in enumerate(all_media, 1):
                    try:
                        # Проверяем доступность каждого медиафайла
                        file_info = await self.application.bot.get_file(m_id)
                        if file_info and file_info.file_id:
                            # Добавляем медиафайл в базу данных
                            self.db.add_media_to_post(content_id, orig_message_id, m_type, m_id, i)
                            logger.info(f"   ✅ Добавлен медиафайл {i}: {m_type} - {m_id[:20]}...")
                        else:
                            logger.warning(f"   ⚠️ Медиафайл {i} недоступен: {m_type}")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Ошибка при добавлении медиафайла {i}: {e}")
                                
            if success:
                category_name = self.analyzer.get_category_name(category)
                if media_type and media_file_id and media_available:
                    media_status = f"{media_type} (доступно)"
                elif media_type and media_file_id:
                    media_status = f"{media_type} (проверка не удалась)"
                elif media_type:
                    media_status = f"{media_type} (file_id отсутствует)"
                else:
                    media_status = "нет"
                    
                if media_group_id and existing_post:
                    # Медиафайлы добавлены к существующему посту
                    group_info = f"\n📱 Медиафайлы добавлены к существующему посту с медиа-группой: {media_group_id}"
                    action_text = "добавлены медиафайлы к посту"
                elif media_group_id:
                    # Создан новый пост с медиа-группой
                    group_info = f"\n📱 Создан новый пост с медиа-группой: {media_group_id}"
                    action_text = "создан новый пост"
                else:
                    # Обычный пост
                    group_info = ""
                    action_text = "добавлен пост"
                    
                await message.reply_text(
                    f"✅ {action_text} в категорию '{category_name}'{group_info}\n\n"
                    f"📝 Заголовок: {title[:100]}...\n"
                    f"📊 Категория: {category_name}\n"
                    f"🎬 Медиа: {media_status}\n"
                    f"⏰ Время: {datetime.now().strftime('%H:%M')}"
                )
                logger.info(f"✅ {action_text} {orig_message_id} в категорию '{category_name}'")
            else:
                await message.reply_text("❌ Ошибка при добавлении сообщения в базу данных.")
                logger.error(f"❌ Ошибка при добавлении поста {orig_message_id}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка в обработчике пересланных сообщений: {e}")
            await message.reply_text("❌ Произошла ошибка при обработке сообщения.")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error(f"❌ Ошибка при обработке обновления: {context.error}")
        
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
        """Запуск бота с простой структурой"""
        logger.info("🚀 Запуск Fitness Content Sorter Bot...")
        
        # Запускаем бота напрямую через run_polling
        self.application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )

if __name__ == "__main__":
    bot = ContentBot()
    bot.run() 