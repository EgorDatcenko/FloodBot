# 🔍 РУКОВОДСТВО ПО ДИАГНОСТИКЕ БОТА

## 🚨 **Проблема: Бот не отвечает в Telegram**

### 📋 **Шаг 1: Проверьте переменные окружения в Render**

1. Перейдите в Render Dashboard → ваш сервис → Environment
2. Убедитесь, что установлены:
   ```
   BOT_TOKEN=ваш_токен_бота
   WEBHOOK_URL=https://floodbot-pqmy.onrender.com
   ```

### 📋 **Шаг 2: Проверьте логи Render**

В логах должны быть:
```
✅ Бот успешно инициализирован
🗑️ Старый webhook удален
✅ Webhook установлен: https://floodbot-pqmy.onrender.com/webhook
🌐 Запуск Flask сервера на порту 10000
```

### 📋 **Шаг 3: Проверьте HTTP endpoints**

Откройте в браузере:
- `https://floodbot-pqmy.onrender.com/` - статус бота
- `https://floodbot-pqmy.onrender.com/setup` - настройки
- `https://floodbot-pqmy.onrender.com/health` - здоровье сервиса

### 📋 **Шаг 4: Проверьте webhook в Telegram**

Откройте в браузере:
```
https://api.telegram.org/bot<ВАШ_ТОКЕН>/getWebhookInfo
```

Должно показать:
```json
{
  "ok": true,
  "result": {
    "url": "https://floodbot-pqmy.onrender.com/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "last_error_date": 0,
    "last_error_message": "",
    "max_connections": 40
  }
}
```

## 🔧 **Возможные проблемы и решения:**

### ❌ **Проблема 1: BOT_TOKEN не найден**
**Симптомы:** В логах "BOT_TOKEN не найден в переменных окружения"

**Решение:**
1. В Render Dashboard → Environment → Add Environment Variable
2. Key: `BOT_TOKEN`
3. Value: ваш токен бота (без кавычек)

### ❌ **Проблема 2: WEBHOOK_URL не установлен**
**Симптомы:** В логах "WEBHOOK_URL не установлен"

**Решение:**
1. В Render Dashboard → Environment → Add Environment Variable
2. Key: `WEBHOOK_URL`
3. Value: `https://floodbot-pqmy.onrender.com` (без слеша в конце)

### ❌ **Проблема 3: Webhook не установлен**
**Симптомы:** В getWebhookInfo показывает пустой URL

**Решение:**
1. Перезапустите сервис в Render
2. Проверьте логи на ошибки установки webhook
3. Убедитесь, что WEBHOOK_URL правильный

### ❌ **Проблема 4: Ошибки в webhook**
**Симптомы:** В getWebhookInfo показывает last_error_message

**Решение:**
1. Проверьте логи Render на ошибки
2. Убедитесь, что бот инициализирован правильно
3. Проверьте, что все зависимости установлены

## 🧪 **Тестирование:**

### 1. **Тест переменных окружения:**
```bash
curl https://floodbot-pqmy.onrender.com/setup
```

### 2. **Тест здоровья сервиса:**
```bash
curl https://floodbot-pqmy.onrender.com/health
```

### 3. **Тест webhook:**
```bash
curl https://api.telegram.org/bot<ТОКЕН>/getWebhookInfo
```

### 4. **Тест бота:**
- Отправьте `/start` боту в Telegram
- Проверьте, что бот отвечает

## 📊 **Ожидаемые результаты:**

### ✅ **Успешная работа:**
- Логи показывают "✅ Бот успешно инициализирован"
- Webhook установлен правильно
- HTTP endpoints отвечают 200 OK
- Бот отвечает на команды в Telegram

### ❌ **Проблемы:**
- Ошибки инициализации бота
- Webhook не установлен
- HTTP endpoints возвращают ошибки
- Бот не отвечает в Telegram

## 🚀 **Быстрое исправление:**

1. **Проверьте переменные окружения**
2. **Перезапустите сервис**
3. **Проверьте логи**
4. **Протестируйте endpoints**
5. **Проверьте webhook статус**

**Если проблема остается, проверьте все шаги по порядку!** 🔍 