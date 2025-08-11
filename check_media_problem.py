from database import Database

def check_media_problem():
    db = Database()
    
    categories = ['power_results', 'sport_tips', 'challenges', 'memes', 'exercises', 'other']
    
    print("🔍 Анализ проблемы с медиа:")
    print("=" * 60)
    
    total_posts = 0
    total_with_media = 0
    
    for category in categories:
        posts = db.get_content_by_category(category, limit=100)
        count = len(posts)
        total_posts += count
        
        media_posts = [p for p in posts if p.get('media_type') and p.get('media_file_id')]
        media_count = len(media_posts)
        total_with_media += media_count
        
        print(f"📁 {category}: {media_count}/{count} с медиа ({media_count/count*100:.1f}%)")
        
        # Показываем посты БЕЗ медиа
        posts_without_media = [p for p in posts if not p.get('media_type') or not p.get('media_file_id')]
        if posts_without_media:
            print(f"   ❌ Посты БЕЗ медиа ({len(posts_without_media)}):")
            for i, post in enumerate(posts_without_media[:5], 1):  # Показываем первые 5
                title = post['title'][:50] + "..." if len(post['title']) > 50 else post['title']
                media_type = post.get('media_type', 'НЕТ')
                media_file_id = post.get('media_file_id', 'НЕТ')
                print(f"   {i}. {title}")
                print(f"      Медиа тип: {media_type}")
                print(f"      Медиа file_id: {media_file_id}")
                print(f"      ID поста: {post['id']}")
                print()
        
        print("-" * 40)
    
    print(f"\n📊 ИТОГО:")
    print(f"   Всего постов: {total_posts}")
    print(f"   С медиа: {total_with_media}")
    print(f"   Без медиа: {total_posts - total_with_media}")
    print(f"   Процент с медиа: {total_with_media/total_posts*100:.1f}%")

if __name__ == "__main__":
    check_media_problem() 