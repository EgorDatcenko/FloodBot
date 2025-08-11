#!/usr/bin/env python3
"""
Скрипт для проверки хештегов в боте
"""

from config import CATEGORY_HASHTAGS, CATEGORIES

def check_hashtags():
    """Проверка хештегов для сортировки"""
    print("🏷️ Проверка хештегов для сортировки в боте")
    print("=" * 60)
    
    # Проверяем требуемые хештеги
    required_hashtags = [
        '#мем', '#спортсоветы', '#челлендж', '#упражнение', 
        '#силовые', '#флудщина'
    ]
    
    print("📋 Требуемые хештеги:")
    for hashtag in required_hashtags:
        print(f"   • {hashtag}")
    
    print("\n📁 Хештеги по категориям в боте:")
    
    found_hashtags = []
    for category, hashtags in CATEGORY_HASHTAGS.items():
        category_name = CATEGORIES.get(category, category)
        print(f"\n   {category_name}:")
        for hashtag in hashtags:
            print(f"     • {hashtag}")
            found_hashtags.append(hashtag)
    
    print("\n🔍 Проверка соответствия:")
    
    # Проверяем каждый требуемый хештег
    missing_hashtags = []
    for required in required_hashtags:
        found = False
        for category, hashtags in CATEGORY_HASHTAGS.items():
            if required in hashtags:
                category_name = CATEGORIES.get(category, category)
                print(f"   ✅ {required} -> {category_name}")
                found = True
                break
        
        if not found:
            print(f"   ❌ {required} -> НЕ НАЙДЕН")
            missing_hashtags.append(required)
    
    print(f"\n📊 Результат:")
    print(f"   • Всего хештегов в боте: {len(found_hashtags)}")
    print(f"   • Требуемых хештегов: {len(required_hashtags)}")
    print(f"   • Найдено: {len(required_hashtags) - len(missing_hashtags)}")
    print(f"   • Отсутствует: {len(missing_hashtags)}")
    
    if missing_hashtags:
        print(f"\n⚠️ Отсутствующие хештеги:")
        for hashtag in missing_hashtags:
            print(f"   • {hashtag}")
    else:
        print(f"\n✅ Все требуемые хештеги найдены!")

if __name__ == "__main__":
    check_hashtags() 