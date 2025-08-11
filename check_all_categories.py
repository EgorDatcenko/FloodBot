from database import Database

def check_all_categories():
    db = Database()
    
    categories = ['power_results', 'sport_tips', 'challenges', 'memes', 'exercises', 'other']
    
    print("📊 Статистика по всем категориям:")
    print("=" * 50)
    
    total_posts = 0
    for category in categories:
        posts = db.get_content_by_category(category, limit=100)
        count = len(posts)
        total_posts += count
        
        print(f"📁 {category}: {count} постов")
        
        # Показываем первые 3 поста для каждой категории
        if posts:
            print("   Примеры постов:")
            for i, post in enumerate(posts[:3], 1):
                title = post['title'][:50] + "..." if len(post['title']) > 50 else post['title']
                media = post.get('media_type', 'нет')
                print(f"   {i}. {title} (медиа: {media})")
        else:
            print("   (нет постов)")
        print()
    
    print(f"📈 Всего постов: {total_posts}")
    
    # Проверяем посты с медиа
    print("\n🎬 Посты с медиа:")
    print("-" * 30)
    for category in categories:
        posts = db.get_content_by_category(category, limit=100)
        media_posts = [p for p in posts if p.get('media_type')]
        print(f"📁 {category}: {len(media_posts)}/{len(posts)} с медиа")

if __name__ == "__main__":
    check_all_categories() 