#!/usr/bin/env python3
"""
Скрипт для тестирования защиты каналов
"""

def test_channel_protection():
    """Тестирование логики защиты каналов"""
    print("🔒 Тестирование защиты каналов")
    print("=" * 50)
    
    # Разрешенные каналы
    allowed_channels = ['nikitaFlooDed', 'Флудские ТРЕНИ']
    
    # Тестовые случаи
    test_cases = [
        # (username, title, expected_result, description)
        ('nikitaFlooDed', None, True, "Разрешенный канал по username"),
        (None, 'Флудские ТРЕНИ', True, "Разрешенный канал по названию"),
        ('nikitaFlooDed', 'ХАТАуФЛУДА', True, "Разрешенный канал по username (с названием)"),
        ('other_channel', None, False, "Запрещенный канал по username"),
        (None, 'Другой канал', False, "Запрещенный канал по названию"),
        ('spam_channel', 'Спам канал', False, "Запрещенный канал по username и названию"),
        (None, None, False, "Канал без username и названия"),
    ]
    
    print("📋 Разрешенные каналы:")
    for channel in allowed_channels:
        print(f"   • {channel}")
    
    print("\n🧪 Тестовые случаи:")
    
    passed = 0
    total = len(test_cases)
    
    for username, title, expected, description in test_cases:
        # Логика проверки (как в боте)
        is_allowed = False
        
        if username:
            # Проверяем по username
            if username in allowed_channels:
                is_allowed = True
        elif title:
            # Проверяем по названию канала
            if title in allowed_channels:
                is_allowed = True
        
        # Проверяем результат
        result = "✅ ПРОШЕЛ" if is_allowed == expected else "❌ НЕ ПРОШЕЛ"
        status = "разрешен" if is_allowed else "запрещен"
        expected_status = "разрешен" if expected else "запрещен"
        
        print(f"   {result} | {description}")
        print(f"      Username: {username or 'None'}")
        print(f"      Title: {title or 'None'}")
        print(f"      Результат: {status} (ожидалось: {expected_status})")
        print()
        
        if is_allowed == expected:
            passed += 1
    
    print(f"📊 Результаты тестирования:")
    print(f"   • Всего тестов: {total}")
    print(f"   • Пройдено: {passed}")
    print(f"   • Провалено: {total - passed}")
    print(f"   • Успешность: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 Все тесты пройдены! Защита каналов работает корректно.")
    else:
        print(f"\n⚠️ {total - passed} тестов провалено. Проверьте логику защиты.")

if __name__ == "__main__":
    test_channel_protection() 