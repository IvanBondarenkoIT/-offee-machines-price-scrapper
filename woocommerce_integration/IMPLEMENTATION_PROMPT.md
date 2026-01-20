# WooCommerce Stock Integration - Implementation Prompt

## Цель задачи

Добавить новый столбец в таблицу сравнения цен (`build_price_comparison.py`) с информацией об остатках товаров со склада DimKava, полученных через WooCommerce API.

**Важно:** Анализировать только товары, которые есть на складе (stock_quantity > 0).

---

## Текущая архитектура проекта

### 1. Структура `build_price_comparison.py`

**Основные методы:**
- `load_inventory()` - загружает инвентарь из API или Excel
- `load_scraped_data()` - загружает данные со скраперов (ALTA, ELITE, KONTAKT, DIM_KAVA и др.)
- `extract_models_from_all_sources()` - извлекает модели и сопоставляет товары
- `build_comparison_table()` - создает финальную таблицу сравнения цен

**Текущие столбцы в таблице сравнения:**
- `Model` - модель товара
- `Quantity` - количество из инвентаря
- `Our Price` - наша цена (из инвентаря)
- `DIM_KAVA` - цена со скрапера DimKava
- `ALTA`, `KONTAKT`, `ELITE` - цены конкурентов
- И другие столбцы с ценами

### 2. Существующие API клиенты

**`utils/stock_api_client.py`:**
- Подключается к Proxy API для Firebird DB
- Получает остатки через SQL запрос
- Конвертирует в DataFrame
- Используется в `build_price_comparison.py` через `_load_inventory_from_api()`

**Аналогия:** Нужно создать похожий клиент для WooCommerce API.

---

## Требования к реализации

### 1. WooCommerce API Клиент

**Файл:** `utils/woocommerce_client.py`

**Функциональность:**
- Подключение к WooCommerce REST API
- Получение всех товаров с пагинацией
- Фильтрация: только товары с `stock_quantity > 0` и `stock_status == 'instock'`
- Извлечение полей:
  - `id` - ID товара
  - `name` - название товара
  - `sku` - артикул
  - `stock_quantity` - остаток на складе (главное поле!)
  - `stock_status` - статус (instock/outofstock/onbackorder)
  - `price` - текущая цена (может быть regular_price или sale_price)
  - `regular_price` - обычная цена (без скидки)
  - `sale_price` - цена со скидкой (если есть скидка)
  - `model` - извлеченная модель из названия (используя ModelExtractor)

**Конфигурация (добавить в `config.py`):**
```python
WOOCOMMERCE_CONFIG = {
    "enabled": os.getenv("USE_WOOCOMMERCE_STOCK", "false").lower() == "true",
    "url": os.getenv("WC_URL", ""),
    "consumer_key": os.getenv("WC_CONSUMER_KEY", ""),
    "consumer_secret": os.getenv("WC_CONSUMER_SECRET", ""),
    "api_version": os.getenv("WC_API_VERSION", "wc/v3"),
    "timeout": int(os.getenv("WC_TIMEOUT", "30")),
    "retry_attempts": 3,
    "retry_delay": 2,
}
```

**Переменные окружения (.env):**
```
USE_WOOCOMMERCE_STOCK=true
WC_URL=https://dimkava.ge
WC_CONSUMER_KEY=ck_your_consumer_key_here
WC_CONSUMER_SECRET=cs_your_consumer_secret_here
WC_API_VERSION=wc/v3
WC_TIMEOUT=30
```

**Важно:** Реальные credentials должны быть только в файле `.env` (который не в git), а не в документации!

### 2. Интеграция в `build_price_comparison.py`

**Новый метод:** `load_woocommerce_stock() -> pd.DataFrame`

**Логика:**
1. Проверить `WOOCOMMERCE_CONFIG["enabled"]`
2. Если включено - загрузить данные через WooCommerce клиент
3. Фильтровать: только `stock_quantity > 0`
4. Извлечь модели из названий товаров (ModelExtractor)
5. Вернуть DataFrame с колонками:
   - `name` - название товара
   - `model` - извлеченная модель
   - `stock_quantity` - остаток на складе
   - `sku` - артикул
   - `price` - текущая цена (sale_price если есть, иначе regular_price)
   - `regular_price` - обычная цена (без скидки)
   - `sale_price` - цена со скидкой (если есть)
   - `has_discount` - есть ли скидка (sale_price != None и sale_price != regular_price)

**Вызов:** Добавить в метод `__init__()` или в начале `build_comparison_table()`

### 3. Добавление столбца в таблицу сравнения

**Место:** Метод `build_comparison_table()`

**Новые столбцы:**
- `DIM_KAVA_STOCK` или `DimKava Stock` - остаток на складе
- Обязательно: добавить столбец с ценами из WooCommerce для сравнения

**Логика сопоставления:**
1. Для каждой строки в таблице сравнения (по модели):
   - Найти соответствующий товар в WooCommerce данных
   - Использовать сопоставление по модели (как для других источников)
   - Если найдено:
     - Добавить `stock_quantity` в столбец `DIM_KAVA_STOCK`
     - Если есть `sale_price` - использовать его как финальную цену
     - Если нет `sale_price` - использовать `regular_price`
     - Сохранить информацию о скидке (если `sale_price` != `regular_price`)
   - Если не найдено - оставить пустым или "-"

**Приоритет сопоставления:**
1. Точное совпадение нормализованной модели
2. Нечеткое совпадение моделей (fuzzy matching, confidence >= 0.9)
3. Если не найдено - оставить пустым

### 4. Фильтрация товаров

**Важно:** В таблицу сравнения попадают только товары, которые:
- Есть в инвентаре (INVENTORY)
- Имеют остаток на складе > 0 (из WooCommerce)

**Логика:**
- После загрузки WooCommerce данных и сопоставления
- Фильтровать строки таблицы: `DIM_KAVA_STOCK > 0` или `DIM_KAVA_STOCK != '-'`

---

## Структура файлов

```
woocommerce_integration/
├── IMPLEMENTATION_PROMPT.md  (этот файл)
└── (будущие файлы для разработки)

utils/
└── woocommerce_client.py  (новый файл)

config.py  (обновить - добавить WOOCOMMERCE_CONFIG)

build_price_comparison.py  (обновить - добавить загрузку и столбец)
```

---

## Зависимости

**Новый пакет:**
```bash
pip install woocommerce
```

**Уже установлено:**
- `python-dotenv` - для .env файлов
- `pandas` - для работы с данными
- `requests` - для HTTP запросов (если woocommerce не использует)

---

## Пример использования WooCommerce API

```python
from woocommerce import API
import os
from dotenv import load_dotenv

load_dotenv()

wcapi = API(
    url=os.getenv('WC_URL'),
    consumer_key=os.getenv('WC_CONSUMER_KEY'),
    consumer_secret=os.getenv('WC_CONSUMER_SECRET'),
    version=os.getenv('WC_API_VERSION', 'wc/v3'),
    timeout=int(os.getenv('WC_TIMEOUT', 30)),
    query_string_auth=True
)

# Получить товары с остатками
response = wcapi.get('products', params={
    'per_page': 100,
    'page': 1,
    'stock_status': 'instock'  # Только товары в наличии
})

products = response.json()
# Фильтровать: stock_quantity > 0
in_stock = [p for p in products if p.get('stock_quantity', 0) > 0]

# Извлечь цены
for product in in_stock:
    regular_price = product.get('regular_price', '0')
    sale_price = product.get('sale_price', '')
    # Текущая цена: sale_price если есть, иначе regular_price
    current_price = sale_price if sale_price else regular_price
    has_discount = bool(sale_price and sale_price != regular_price)
```

---

## Вопросы для уточнения

1. **Название столбца:** `DIM_KAVA_STOCK` или `DimKava Stock` или другое?
2. **Формат значения:** Только число (остаток) или "Остаток: X шт"?
3. **Цены из WooCommerce:** Добавлять столбец с ценами из WooCommerce (с учетом sale_price) или только остатки?
4. **Формат цен:** Показывать только финальную цену или "regular_price \\ sale_price" (как для других источников)?
5. **Сопоставление:** Использовать существующий механизм сопоставления (ModelExtractor) или нужна отдельная логика?
6. **Фильтрация:** Фильтровать таблицу сравнения (показывать только товары с остатками) или показывать все, но с пустым столбцом для товаров без остатков?
7. **Кэширование:** Нужно ли кэшировать данные WooCommerce API для ускорения?

---

## План реализации

**Статус:** ✅ ВСЕ ЭТАПЫ ЗАВЕРШЕНЫ - ИНТЕГРАЦИЯ РАБОТАЕТ

### Этап 1: Создание WooCommerce клиента ✅ ЗАВЕРШЕН
- [x] Создать `utils/woocommerce_client.py` ✅
- [x] Реализовать подключение к API ✅
- [x] Реализовать получение товаров с пагинацией ✅
- [x] Реализовать фильтрацию (stock_quantity > 0) ✅
- [x] Извлечь цены: `regular_price`, `sale_price`, определить финальную цену ✅
- [x] Добавить извлечение моделей ✅
- [x] Добавить обработку ошибок и retry логику ✅

**Прогресс:** Создан полнофункциональный WooCommerce клиент по аналогии с `stock_api_client.py`. Клиент поддерживает пагинацию, фильтрацию по остаткам, извлечение цен (regular_price, sale_price) и моделей через ModelExtractor.

### Этап 2: Обновление конфигурации ✅ ЗАВЕРШЕН
- [x] Добавить `WOOCOMMERCE_CONFIG` в `config.py` ✅
- [x] Обновить `env.example.txt` с новыми переменными (WC_USER_AGENT добавлен) ✅
- [x] Добавить валидацию конфигурации ✅

### Этап 3: Интеграция в build_price_comparison.py ✅ ЗАВЕРШЕН
- [x] Добавить метод `load_woocommerce_stock()` ✅
- [x] Интегрировать загрузку данных (включая regular_price и sale_price) ✅
- [x] Добавить сопоставление товаров по моделям ✅
- [x] Добавить столбец `DIM_KAVA_STOCK` в таблицу сравнения ✅
- [x] Добавить столбец `DIM_KAVA_WC_PRICE` с ценами из WooCommerce ✅
- [x] Добавить фильтрацию: показывать только товары с остатками > 0 ✅

**Прогресс:** 
- Добавлен метод `load_woocommerce_stock()` с graceful degradation (не ломает существующий функционал)
- WooCommerce данные интегрированы в процесс сопоставления моделей
- Добавлены столбцы `DIM_KAVA_STOCK` (остаток) и `DIM_KAVA_WC_PRICE` (цена с учетом скидок)
- Реализована фильтрация: в таблицу попадают только товары с `stock_quantity > 0` (если WooCommerce включен)
- Метод `run()` обновлен для загрузки WooCommerce данных

### Этап 4: Тестирование ✅ ЗАВЕРШЕН
- [x] Протестировать подключение к WooCommerce API ✅
- [x] Проверить загрузку данных ✅
- [x] Проверить интеграцию в build_price_comparison.py ✅
- [x] Проверить сопоставление товаров ✅

**Результаты тестирования:**
- ✅ Подключение к API работает (после отключения VPN)
- ✅ Загружено 159 товаров, из них 7 с остатками > 0
- ✅ Найден 1 товар DeLonghi: `EC9555.M` (остаток: 14, цена: 2399 со скидкой от 2999)
- ✅ Метод `load_woocommerce_stock()` работает корректно
- ✅ Данные корректно обрабатываются и извлекаются модели
- ✅ Graceful degradation работает (не ломает существующий функционал)
- ✅ **Добавлена поддержка User-Agent для обхода Imunify360** (из промпта WOOCOMMERCE_PRODUCT_STOCK_PROMPT)

**Статус:**
- ✅ Все этапы реализации завершены
- ✅ Интеграция протестирована и работает
- ✅ Готово к использованию в production
- ✅ Интегрировано в `run_full_cycle.py` (отображение WooCommerce данных)
- ✅ Обновлена документация (`docs/general/FULL_CYCLE_GUIDE.md`)
- ✅ Обновлен `env.example.txt` с `WC_USER_AGENT`

---

## Примечания

- Использовать существующие утилиты: `ModelExtractor`, `logger`
- Следовать стилю кода существующих API клиентов
- Добавить логирование всех операций
- Обработать все возможные ошибки (нет подключения, неверные credentials, и т.д.)
- Если WooCommerce API недоступен - не ломать существующий функционал (graceful degradation)
