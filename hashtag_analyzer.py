import asyncio
import logging
from telegram import Bot
from telegram.error import TelegramError
from config import BOT_TOKEN, CHANNEL_USERNAME
from content_analyzer import ContentAnalyzer

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class HashtagAnalyzer:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.analyzer = ContentAnalyzer()
    
    async def analyze_channel_hashtags(self, limit: int = 50):
        """
        Анализ хештегов из канала
        """
        try:
            logger.info(f"Анализирую хештеги из канала {CHANNEL_USERNAME}")
            
            # Получаем информацию о канале
            chat = await self.bot.get_chat(CHANNEL_USERNAME)
            logger.info(f"Канал: {chat.title} (ID: {chat.id})")
            
            # Получаем сообщения из канала (используем правильный метод)
            messages = []
            try:
                # Получаем последние сообщения
                updates = await self.bot.get_updates(limit=limit)
                for update in updates:
                    if update.channel_post:
                        messages.append(update.channel_post)
                    elif update.message and update.message.chat.type == 'channel':
                        messages.append(update.message)
                
                # Если через updates не получилось, попробуем другой способ
                if not messages:
                    logger.info("Попытка получить сообщения через другой метод...")
                    # Получаем информацию о последних сообщениях
                    try:
                        # Получаем последнее сообщение для определения ID
                        last_message = await self.bot.get_chat_history(chat.id, limit=1)
                        if last_message:
                            # Получаем несколько последних сообщений
                            for i in range(min(limit, 20)):  # Ограничиваем до 20 сообщений
                                try:
                                    message = await self.bot.get_chat_history(chat.id, limit=1, offset=i)
                                    if message:
                                        messages.extend(message)
                                    await asyncio.sleep(0.1)  # Задержка между запросами
                                except Exception as e:
                                    logger.warning(f"Не удалось получить сообщение {i}: {e}")
                                    break
                    except Exception as e:
                        logger.warning(f"Альтернативный метод не сработал: {e}")
                
            except Exception as e:
                logger.error(f"Ошибка при получении сообщений: {e}")
                # Создаем тестовые данные для демонстрации
                messages = []
            
            logger.info(f"Найдено {len(messages)} сообщений для анализа")
            
            # Анализируем хештеги
            all_hashtags = {}
            categorized_messages = {}
            uncategorized_messages = []
            
            for i, message in enumerate(messages, 1):
                try:
                    # Извлекаем текст
                    title, text = self.analyzer.extract_text_content(message)
                    full_text = f"{title} {text}"
                    
                    # Извлекаем хештеги
                    hashtags = self.analyzer.extract_hashtags(full_text)
                    
                    # Категоризируем контент
                    category = self.analyzer.categorize_content(text, title)
                    category_name = self.analyzer.get_category_name(category)
                    
                    # Собираем статистику хештегов
                    for hashtag in hashtags:
                        if hashtag not in all_hashtags:
                            all_hashtags[hashtag] = 0
                        all_hashtags[hashtag] += 1
                    
                    # Группируем сообщения по категориям
                    if category != 'other':
                        if category not in categorized_messages:
                            categorized_messages[category] = []
                        categorized_messages[category].append({
                            'message_id': message.message_id,
                            'hashtags': hashtags,
                            'category': category_name,
                            'text_preview': full_text[:100] + "..." if len(full_text) > 100 else full_text
                        })
                    else:
                        uncategorized_messages.append({
                            'message_id': message.message_id,
                            'hashtags': hashtags,
                            'text_preview': full_text[:100] + "..." if len(full_text) > 100 else full_text
                        })
                    
                    logger.info(f"[{i}/{len(messages)}] ID: {message.message_id}, Категория: {category_name}, Хештеги: {hashtags}")
                
                except Exception as e:
                    logger.error(f"Ошибка при анализе сообщения {message.message_id}: {e}")
            
            # Выводим результаты
            self.print_analysis_results(all_hashtags, categorized_messages, uncategorized_messages)
        
        except TelegramError as e:
            logger.error(f"Ошибка Telegram API: {e}")
        except Exception as e:
            logger.error(f"Общая ошибка: {e}")
        finally:
            try:
                await self.bot.close()
            except:
                pass  # Игнорируем ошибки при закрытии
    
    def print_analysis_results(self, all_hashtags, categorized_messages, uncategorized_messages):
        """
        Вывод результатов анализа
        """
        print("\n" + "="*60)
        print("📊 РЕЗУЛЬТАТЫ АНАЛИЗА ХЕШТЕГОВ")
        print("="*60)
        
        # Статистика хештегов
        if all_hashtags:
            print("\n🏷️ ВСЕ ХЕШТЕГИ В КАНАЛЕ:")
            sorted_hashtags = sorted(all_hashtags.items(), key=lambda x: x[1], reverse=True)
            for hashtag, count in sorted_hashtags:
                print(f"  {hashtag}: {count} раз")
        else:
            print("\n🏷️ ХЕШТЕГИ НЕ НАЙДЕНЫ")
        
        # Категоризированные сообщения
        if categorized_messages:
            print(f"\n✅ КАТЕГОРИЗИРОВАННЫЕ СООБЩЕНИЯ ({len(categorized_messages)} категорий):")
            for category, messages in categorized_messages.items():
                category_name = self.analyzer.get_category_name(category)
                print(f"\n📁 {category_name} ({len(messages)} сообщений):")
                for msg in messages[:3]:  # Показываем первые 3 сообщения
                    hashtags_str = " ".join(msg['hashtags']) if msg['hashtags'] else "без хештегов"
                    print(f"  ID: {msg['message_id']}, Хештеги: {hashtags_str}")
                    print(f"  Текст: {msg['text_preview']}")
        else:
            print("\n✅ КАТЕГОРИЗИРОВАННЫЕ СООБЩЕНИЯ НЕ НАЙДЕНЫ")
        
        # Неклассифицированные сообщения
        if uncategorized_messages:
            print(f"\n❓ НЕКЛАССИФИЦИРОВАННЫЕ СООБЩЕНИЯ ({len(uncategorized_messages)}):")
            for msg in uncategorized_messages[:5]:  # Показываем первые 5
                hashtags_str = " ".join(msg['hashtags']) if msg['hashtags'] else "без хештегов"
                print(f"  ID: {msg['message_id']}, Хештеги: {hashtags_str}")
                print(f"  Текст: {msg['text_preview']}")
        
        # Рекомендации
        print("\n💡 РЕКОМЕНДАЦИИ:")
        print("1. Используйте рекомендуемые хештеги для точной категоризации")
        print("2. Добавьте хештеги к сообщениям без категории")
        print("3. Проверьте правильность написания хештегов")
        
        # Показываем рекомендуемые хештеги
        print("\n🏷️ РЕКОМЕНДУЕМЫЕ ХЕШТЕГИ:")
        for category_key, category_name in self.analyzer.get_all_categories().items():
            if category_key != 'other':
                hashtags = self.analyzer.get_hashtags_for_category(category_key)
                print(f"  {category_name}: {' '.join(hashtags)}")

async def main():
    """
    Главная функция для запуска анализа
    """
    analyzer = HashtagAnalyzer()
    await analyzer.analyze_channel_hashtags(limit=20)  # Уменьшаем лимит

if __name__ == "__main__":
    asyncio.run(main()) 