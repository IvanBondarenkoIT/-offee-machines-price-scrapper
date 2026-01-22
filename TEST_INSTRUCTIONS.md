# 🧪 Инструкции по тестированию WooCommerce клиента

## 📋 Подготовка

### 1. Установить зависимости
```bash
pip install requests
```
Или если используете requirements.txt:
```bash
pip install -r requirements.txt
```

### 2. Настроить переменные окружения

Создайте файл `.env` в корне проекта (или установите переменные в системе):

```env
WC_URL=https://dimkava.ge
WC_CONSUMER_KEY=ck_your_actual_key_here
WC_CONSUMER_SECRET=cs_your_actual_secret_here
WC_API_VERSION=wc/v3
```

**Где получить ключи:**
1. Войти в админ-панель WooCommerce (dimkava.ge/wp-admin)
2. WooCommerce → Settings → Advanced → REST API
3. Создать новый ключ или использовать существующий
4. Скопировать Consumer Key и Consumer Secret

### 3. Загрузить переменные окружения

Если используете `.env` файл, убедитесь, что он загружается:
```python
from dotenv import load_dotenv
load_dotenv()
```

Или установите переменные в системе перед запуском.

---

## 🚀 Запуск теста

```bash
python test_woocommerce_client.py
```

---

## ✅ Что проверяет тест

1. **Конфигурация** - наличие и корректность переменных окружения
2. **Подключение** - успешное подключение к WooCommerce API
3. **Получение данных** - загрузка товаров с фильтрацией по stock_status
4. **Извлечение моделей** - корректность работы ModelExtractor
5. **Формат данных** - правильность структуры DataFrame

---

## 📊 Ожидаемый результат

```
================================================================================
WOOCOMMERCE CLIENT TEST SUITE
================================================================================

================================================================================
TEST 1: Configuration Loading
================================================================================
[OK] Configuration loaded:
  URL: https://dimkava.ge
  Consumer Key: ck_xxxxx...
  Consumer Secret: cs_xxxxx...
  API Version: wc/v3

================================================================================
TEST 2: API Connection
================================================================================
[OK] Client created successfully
[OK] API connection successful
  Sample product: DeLonghi ECAM22.110.SB...

================================================================================
TEST 3: Data Retrieval
================================================================================
[OK] Retrieved 45 products with models

First 5 products:
  1. Model: ECAM22.110.SB
     Name: DeLonghi ECAM22.110.SB...
     Price: 1999.0
     Stock: 5
  ...

================================================================================
TEST SUMMARY
================================================================================
[OK] All tests passed!
[OK] Retrieved 45 products successfully
```

---

## ⚠️ Возможные проблемы

### Ошибка: "Configuration not found"
- Проверьте, что переменные окружения установлены
- Убедитесь, что `.env` файл в корне проекта
- Проверьте названия переменных (WC_URL, WC_CONSUMER_KEY, WC_CONSUMER_SECRET)

### Ошибка: "API request failed" / 401 Unauthorized
- Проверьте правильность Consumer Key и Consumer Secret
- Убедитесь, что ключи не истекли
- Проверьте права доступа ключа (Read permission)

### Ошибка: "No data retrieved"
- Проверьте, что в магазине есть товары со статусом "instock"
- Проверьте, что товары имеют названия с моделями (DeLonghi, Melitta, Nivona)

### Ошибка: "Many duplicate models"
- Это может быть нормально, если есть варианты одного товара
- Проверьте качество извлечения моделей в логах

---

## 🔍 Дополнительная отладка

Если тест не проходит, можно запустить клиент напрямую:

```python
from utils.woocommerce_client import WooCommerceClient

client = WooCommerceClient(
    url="https://dimkava.ge",
    consumer_key="ck_...",
    consumer_secret="cs_..."
)

# Простой тест подключения
response = client._make_request('products', {'per_page': 1})
print(response)
```

---

## ✅ После успешного теста

Если все тесты прошли успешно:
1. ✅ Клиент готов к использованию
2. ✅ Можно переходить к этапу 2 (создание export_woocommerce_data.py)
3. ✅ Данные получаются корректно
