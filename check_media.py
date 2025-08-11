from database import Database

def check_media():
    db = Database()
    
    # Получаем все посты с медиа
    challenges = db.get_content_by_category('challenges', limit=50)
    
    print(f"📊 Проверяю медиа в {len(challenges)} постах категории 'challenges'")
    print("\n" + "="*60)
    
    media_count = 0
    for i, post in enumerate(challenges, 1):
        media_type = post.get('media_type')
        media_file_id = post.get('media_file_id')
        
        print(f"{i}. ID: {post['id']}")
        print(f"   Заголовок: {post['title'][:50]}...")
        print(f"   Медиа тип: {media_type}")
        print(f"   Медиа file_id: {media_file_id}")
        
        if media_type and media_file_id:
            media_count += 1
            print(f"   ✅ Есть медиа")
        else:
            print(f"   ❌ Нет медиа")
        print("-" * 40)
    
    print(f"\n📈 Итого постов с медиа: {media_count}/{len(challenges)}")

if __name__ == "__main__":
    check_media() 