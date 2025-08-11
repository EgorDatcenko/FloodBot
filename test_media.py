import asyncio
from database import Database
from config import BOT_TOKEN
from telegram import Bot

async def test_media_sending():
    db = Database()
    bot = Bot(token=BOT_TOKEN)
    
    # Получаем первый пост с медиа
    challenges = db.get_content_by_category('challenges', limit=1)
    
    if not challenges:
        print("❌ Нет постов в базе данных")
        return
    
    post = challenges[0]
    media_type = post.get('media_type')
    media_file_id = post.get('media_file_id')
    title = post.get('title', 'Без заголовка')
    
    print(f"🧪 Проверяю доступность медиа:")
    print(f"   Заголовок: {title}")
    print(f"   Медиа тип: {media_type}")
    print(f"   Медиа file_id: {media_file_id}")
    
    try:
        if media_type == 'video' and media_file_id:
            print("   🔍 Проверяю доступность видео...")
            # Только проверяем доступность файла, НЕ отправляем
            file_info = await bot.get_file(media_file_id)
            print(f"   ✅ Видео доступно: {file_info.file_id}")
            print(f"   📁 Размер файла: {file_info.file_size} байт")
        else:
            print("   ❌ Нет видео для проверки")
            
    except Exception as e:
        print(f"   ❌ Ошибка при проверке: {e}")

if __name__ == "__main__":
    asyncio.run(test_media_sending()) 