#!/usr/bin/env python3
"""
Скрипт для проверки отсутствия упоминаний команд в боте
"""

import re

def test_no_command_mentions():
    """Проверка отсутствия упоминаний команд в боте"""
    print("🔍 Проверка отсутствия упоминаний команд в боте")
    print("=" * 60)
    
    # Команды, которые должны быть убраны
    removed_commands = [
        '/help', '/categories', '/stats', '/search', '/hashtags',
        '/load_history', '/debug', '/category', '/load_posts', '/load_hashtag'
    ]
    
    # Читаем файл bot.py
    try:
        with open('bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Файл bot.py не найден")
        return
    
    print("📋 Проверяемые команды:")
    for cmd in removed_commands:
        print(f"   • {cmd}")
    
    print("\n🔍 Результаты проверки:")
    
    found_mentions = []
    
    for cmd in removed_commands:
        # Ищем упоминания команд в тексте (исключая комментарии к функциям)
        pattern = rf'[^#]*{re.escape(cmd)}'
        matches = re.findall(pattern, content, re.MULTILINE)
        
        # Фильтруем комментарии к функциям
        filtered_matches = []
        for match in matches:
            # Исключаем строки, которые являются комментариями к функциям
            if not re.search(rf'"""Обработчик команды {re.escape(cmd)}"""', match):
                filtered_matches.append(match.strip())
        
        if filtered_matches:
            found_mentions.append((cmd, filtered_matches))
            print(f"   ❌ {cmd} - найдено {len(filtered_matches)} упоминаний")
        else:
            print(f"   ✅ {cmd} - не найдено")
    
    if not found_mentions:
        print("\n🎉 Все упоминания команд успешно убраны!")
        print("✅ Бот готов к использованию с упрощенным интерфейсом")
    else:
        print(f"\n⚠️ Найдено {len(found_mentions)} команд с упоминаниями:")
        for cmd, mentions in found_mentions:
            print(f"   • {cmd}:")
            for mention in mentions[:3]:  # Показываем первые 3 упоминания
                print(f"     - {mention[:100]}...")
            if len(mentions) > 3:
                print(f"     - ... и еще {len(mentions) - 3} упоминаний")

def test_allowed_commands():
    """Проверка разрешенных команд"""
    print("\n✅ Проверка разрешенных команд:")
    
    try:
        with open('bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Файл bot.py не найден")
        return
    
    # Проверяем наличие команды /start
    if 'CommandHandler("start"' in content:
        print("   ✅ /start - команда сохранена")
    else:
        print("   ❌ /start - команда не найдена")
    
    # Проверяем отсутствие других команд в setup_handlers
    other_commands = ['help', 'categories', 'stats', 'search', 'hashtags', 
                     'load_history', 'debug', 'category', 'load_posts', 'load_hashtag']
    
    for cmd in other_commands:
        if f'CommandHandler("{cmd}"' in content:
            print(f"   ❌ {cmd} - команда все еще зарегистрирована")
        else:
            print(f"   ✅ {cmd} - команда убрана из обработчиков")

if __name__ == "__main__":
    test_no_command_mentions()
    test_allowed_commands() 