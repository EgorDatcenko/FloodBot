import logging
import requests
import json
from config import BOT_TOKEN, CHANNEL_USERNAME
from database import Database
from content_analyzer import ContentAnalyzer

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ManualContentProcessor:
    def __init__(self):
        self.db = Database()
        self.analyzer = ContentAnalyzer()
        self.base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
    
    def get_channel_info(self):
        """Получение информации о канале"""
        try:
            url = f"{self.base_url}/getChat"
            response = requests.post(url, json={"chat_id": CHANNEL_USERNAME})
            data = response.json()
            
            if data.get("ok"):
                chat = data["result"]
                logger.info(f"Канал: {chat['title']} (ID: {chat['id']})")
                return chat
            else:
                logger.error(f"Ошибка получения информации о канале: {data}")
                return None
        except Exception as e:
            logger.error(f"Ошибка при получении информации о канале: {e}")
            return None
    
    def add_test_content(self):
        """Добавление тестового контента для демонстрации"""
        logger.info("Добавляю тестовый контент...")
        
        test_messages = [
            # ЧЕЛЛЕНДЖИ
            {
                "message_id": 1001,
                "channel_id": -1002560123534,
                "text": "-------- ⚠️ ЧЕЛЕНДЖ ⚠️ --------\n\n\"Щелкунчик\"\n\n⚠️ ИНВЕНТАРЬ:\n- ГРЕЦКИЕ ОРЕХИ (🌰)\n- ПАЛЬЦЫ (большой/ср/указат)\n\nНЕ ЗАБЫВАЕМ:\n\"Мужички, кому не слабо, жду от вас [ВИДОСЫ] и [Ответные ❞ ЗАДАНИЯ] в комменты! #челендж\"",
                "category": "challenges"
            },
            {
                "message_id": 1002,
                "channel_id": -1002560123534,
                "text": "Новый челлендж на этой неделе! 💪\n\n#челендж #вызов #фитнес",
                "category": "challenges"
            },
            {
                "message_id": 1003,
                "channel_id": -1002560123534,
                "text": "ЧЕЛЛЕНДЖ: Подтягивания на турнике\n\nКто больше подтянется за минуту? #челендж #вызов",
                "category": "challenges"
            },
            # СИЛОВЫЕ РЕЗУЛЬТАТЫ
            {
                "message_id": 1004,
                "channel_id": -1002560123534,
                "text": "Мой результат: жим лежа 120кг! 💪\n\n#результаты #сила #достижения",
                "category": "power_results"
            },
            {
                "message_id": 1005,
                "channel_id": -1002560123534,
                "text": "Прогресс за месяц: приседания с 80кг до 120кг\n\n#прогресс #результаты #сила",
                "category": "power_results"
            },
            # СПОРТ СОВЕТЫ
            {
                "message_id": 1006,
                "channel_id": -1002560123534,
                "text": "Совет дня: всегда разминайтесь перед тренировкой!\n\n#советы #рекомендации #техника",
                "category": "sport_tips"
            },
            {
                "message_id": 1007,
                "channel_id": -1002560123534,
                "text": "Правильная техника приседаний - залог успеха\n\n#техника #советы #подсказки",
                "category": "sport_tips"
            },
            # УПРАЖНЕНИЯ
            {
                "message_id": 1008,
                "channel_id": -1002560123534,
                "text": "Отличная тренировка сегодня! 💪\n\n#упражнения #кружки #прогресс",
                "category": "exercises"
            },
            {
                "message_id": 1009,
                "channel_id": -1002560123534,
                "text": "Комплекс упражнений на пресс\n\n#упражнения #фитнес #тренировка",
                "category": "exercises"
            },
            {
                "message_id": 1010,
                "channel_id": -1002560123534,
                "text": "Кружок: жим гантелей стоя\n\n#кружки #упражнения #фитнес",
                "category": "exercises"
            },
            # МЕМЫ
            {
                "message_id": 1011,
                "channel_id": -1002560123534,
                "text": "Когда наконец-то доделал все подходы 😅\n\n#мемы #юмор #смех",
                "category": "memes"
            },
            {
                "message_id": 1012,
                "channel_id": -1002560123534,
                "text": "Прикол дня: спортзал в 6 утра\n\n#приколы #мемы #юмор",
                "category": "memes"
            }
        ]
        
        for msg in test_messages:
            try:
                # Категоризируем контент
                category = self.analyzer.categorize_content(msg["text"], "")
                
                # Сохраняем в базу данных
                success = self.db.add_content(
                    message_id=msg["message_id"],
                    channel_id=msg["channel_id"],
                    category=category,
                    title="",
                    text=msg["text"],
                    media_type=None,
                    media_file_id=None
                )
                
                if success:
                    category_name = self.analyzer.get_category_name(category)
                    hashtags = self.analyzer.extract_hashtags(msg["text"])
                    hashtags_str = " ".join(hashtags) if hashtags else "без хештегов"
                    logger.info(f"Добавлен в категорию '{category_name}' (хештеги: {hashtags_str})")
                
            except Exception as e:
                logger.error(f"Ошибка при добавлении тестового контента: {e}")
        
        logger.info("Тестовый контент добавлен!")
    
    def show_stats(self):
        """Показать статистику"""
        stats = self.db.get_stats()
        
        if not stats:
            logger.info("База данных пуста")
            return
        
        logger.info("📊 Статистика по категориям:")
        total = sum(stats.values())
        
        for category, count in stats.items():
            category_name = self.analyzer.get_category_name(category)
            percentage = (count / total * 100) if total > 0 else 0
            logger.info(f"  📁 {category_name}: {count} ({percentage:.1f}%)")
        
        logger.info(f"📈 Всего записей: {total}")
    
    def show_content_by_category(self, category):
        """Показать контент по категории"""
        content = self.db.get_content_by_category(category, limit=10)
        category_name = self.analyzer.get_category_name(category)
        
        if not content:
            logger.info(f"📁 Категория '{category_name}' пуста")
            return
        
        logger.info(f"📁 Контент в категории '{category_name}':")
        
        for i, item in enumerate(content, 1):
            title = item['title'] or "Без заголовка"
            text_preview = item['text'][:200] + "..." if len(item['text']) > 200 else item['text']
            
            logger.info(f"  {i}. 📝 {title}")
            logger.info(f"     {text_preview}")
            logger.info("")

def main():
    """Главная функция"""
    processor = ManualContentProcessor()
    
    print("🔧 Ручной обработчик контента")
    print("=" * 50)
    
    # Показываем текущую статистику
    print("\n📊 Текущая статистика:")
    processor.show_stats()
    
    # Добавляем тестовый контент
    print("\n🔄 Добавляю тестовый контент...")
    processor.add_test_content()
    
    # Показываем обновленную статистику
    print("\n📊 Обновленная статистика:")
    processor.show_stats()
    
    # Показываем контент по категориям
    print("\n📁 Контент по категориям:")
    categories = ['challenges', 'power_results', 'sport_tips', 'exercises', 'memes']
    
    for category in categories:
        processor.show_content_by_category(category)
        print("-" * 30)

if __name__ == "__main__":
    main() 