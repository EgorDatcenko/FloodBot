from database import Database

def check_database():
    db = Database()
    
    # Получаем все посты из категории challenges
    challenges = db.get_content_by_category('challenges', limit=50)
    
    print(f"📊 Найдено постов в категории 'challenges': {len(challenges)}")
    print("\n" + "="*50)
    
    for i, post in enumerate(challenges, 1):
        print(f"{i}. ID: {post['id']}")
        print(f"   Message ID: {post['message_id']}")
        print(f"   Заголовок: {post['title']}")
        print(f"   Текст: {post['text'][:100]}..." if len(post['text']) > 100 else f"   Текст: {post['text']}")
        print(f"   Медиа: {post['media_type']}")
        print(f"   Создан: {post['created_at']}")
        print("-" * 30)

if __name__ == "__main__":
    check_database() 