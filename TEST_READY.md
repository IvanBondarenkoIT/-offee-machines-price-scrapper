# ✅ Тест готов к запуску

## 📋 Что создано

1. **`test_woocommerce_client.py`** - полный тестовый скрипт
2. **`TEST_INSTRUCTIONS.md`** - подробные инструкции
3. **Обновлен `requirements.txt`** - добавлен `requests==2.31.0`
4. **Обновлен `utils/woocommerce_client.py`** - добавлена поддержка `.env` файла

---

## 🚀 Как запустить тест

### Вариант 1: С .env файлом (рекомендуется)

1. Создайте файл `.env` в корне проекта:
```env
WC_URL=https://dimkava.ge
WC_CONSUMER_KEY=ck_your_actual_key_here
WC_CONSUMER_SECRET=cs_your_actual_secret_here
WC_API_VERSION=wc/v3
```

2. Запустите тест:
```bash
python test_woocommerce_client.py
```

### Вариант 2: Через переменные окружения системы

Установите переменные в PowerShell:
```powershell
$env:WC_URL="https://dimkava.ge"
$env:WC_CONSUMER_KEY="ck_..."
$env:WC_CONSUMER_SECRET="cs_..."
```

Затем запустите:
```bash
python test_woocommerce_client.py
```

---

## 📊 Что проверяет тест

✅ **TEST 1:** Загрузка конфигурации  
✅ **TEST 2:** Подключение к WooCommerce API  
✅ **TEST 3:** Получение данных (товары со stock_status='instock')  
✅ **TEST 4:** Качество извлечения моделей  

---

## ⚠️ Текущий статус

Тест запускается, но требует реальные API ключи для полного тестирования.

**Текущий вывод:**
```
[FAIL] Configuration not found
Required environment variables:
  - WC_URL
  - WC_CONSUMER_KEY
  - WC_CONSUMER_SECRET
```

Это **нормально** - тест работает корректно и ждет настройки.

---

## 🔑 Где получить API ключи

1. Войти в админ-панель WooCommerce: `dimkava.ge/wp-admin`
2. WooCommerce → Settings → Advanced → REST API
3. Создать новый ключ или использовать существующий
4. Скопировать Consumer Key и Consumer Secret

---

## ✅ После успешного теста

Если все тесты пройдут:
- ✅ Клиент готов к использованию
- ✅ Можно переходить к этапу 2 (создание `export_woocommerce_data.py`)
- ✅ Данные получаются корректно

---

## 📝 Примечания

- Тест не влияет на существующий код
- `run_full_cycle.py` и все скраперы не затронуты ✅
- Можно безопасно запускать тест в любой момент
