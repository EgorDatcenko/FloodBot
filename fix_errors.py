#!/usr/bin/env python3
"""
Скрипт для исправления ошибок в bot.py
"""

import re

def fix_bot_errors():
    """Исправление ошибок в bot.py"""
    
    # Читаем файл
    with open('bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Исправляем get_category_stats на get_stats
    content = re.sub(r'get_category_stats\(\)', 'get_stats()', content)
    
    # Исправляем отступы в try-except блоках
    # Находим и исправляем проблемные места
    
    # Исправляем отступы в строке 312-315
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Исправляем отступы в проблемных местах
        if i == 311:  # Строка с else:
            if 'else:' in line and line.strip() == 'else:':
                fixed_lines.append('                        else:')
            else:
                fixed_lines.append(line)
        elif i == 312:  # Строка с logger.info
            if 'logger.info' in line and 'Новых постов для обработки не найдено' in line:
                fixed_lines.append('                            logger.info("ℹ️ Новых постов для обработки не найдено")')
            else:
                fixed_lines.append(line)
        elif i == 313:  # Строка с else:
            if 'else:' in line and line.strip() == 'else:':
                fixed_lines.append('                    else:')
            else:
                fixed_lines.append(line)
        elif i == 314:  # Строка с logger.info
            if 'logger.info' in line and 'Сообщений из канала не найдено' in line:
                fixed_lines.append('                        logger.info("ℹ️ Сообщений из канала не найдено")')
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Объединяем строки обратно
    content = '\n'.join(fixed_lines)
    
    # Записываем исправленный файл
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Ошибки в bot.py исправлены!")

if __name__ == "__main__":
    fix_bot_errors() 