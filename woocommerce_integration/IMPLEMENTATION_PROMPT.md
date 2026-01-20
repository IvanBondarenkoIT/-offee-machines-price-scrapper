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
  - `price` - цена
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
WC_CONSUMER_KEY=ck_9f1e14b6d61fe7ee49ec1f79fb21b83207d96b5a
WC_CONSUMER_SECRET=cs_0c7a727e5cfeea67f45c7d9db5828134261da4de
WC_API_VERSION=wc/v3
WC_TIMEOUT=30
```

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
   - `price` - цена (опционально, для проверки)

**Вызов:** Добавить в метод `__init__()` или в начале `build_comparison_table()`

### 3. Добавление столбца в таблицу сравнения

**Место:** Метод `build_comparison_table()`

**Новый столбец:** `DIM_KAVA_STOCK` или `DimKava Stock`

**Логика сопоставления:**
1. Для каждой строки в таблице сравнения (по модели):
   - Найти соответствующий товар в WooCommerce данных
   - Использовать сопоставление по модели (как для других источников)
   - Если найдено - добавить `stock_quantity` в столбец
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
```

---

## Вопросы для уточнения

1. **Название столбца:** `DIM_KAVA_STOCK` или `DimKava Stock` или другое?
2. **Формат значения:** Только число (остаток) или "Остаток: X шт"?
3. **Сопоставление:** Использовать существующий механизм сопоставления (ModelExtractor) или нужна отдельная логика?
4. **Фильтрация:** Фильтровать таблицу сравнения (показывать только товары с остатками) или показывать все, но с пустым столбцом для товаров без остатков?
5. **Кэширование:** Нужно ли кэшировать данные WooCommerce API для ускорения?

---

## План реализации

### Этап 1: Создание WooCommerce клиента
- [ ] Создать `utils/woocommerce_client.py`
- [ ] Реализовать подключение к API
- [ ] Реализовать получение товаров с пагинацией
- [ ] Реализовать фильтрацию (stock_quantity > 0)
- [ ] Добавить извлечение моделей
- [ ] Добавить обработку ошибок и retry логику

### Этап 2: Обновление конфигурации
- [ ] Добавить `WOOCOMMERCE_CONFIG` в `config.py`
- [ ] Обновить `.env.example` с новыми переменными
- [ ] Добавить валидацию конфигурации

### Этап 3: Интеграция в build_price_comparison.py
- [ ] Добавить метод `load_woocommerce_stock()`
- [ ] Интегрировать загрузку данных
- [ ] Добавить сопоставление товаров по моделям
- [ ] Добавить столбец `DIM_KAVA_STOCK` в таблицу сравнения

### Этап 4: Тестирование
- [ ] Протестировать подключение к WooCommerce API
- [ ] Проверить загрузку данных
- [ ] Проверить сопоставление товаров
- [ ] Проверить отображение столбца в таблице

---

## Примечания

- Использовать существующие утилиты: `ModelExtractor`, `logger`
- Следовать стилю кода существующих API клиентов
- Добавить логирование всех операций
- Обработать все возможные ошибки (нет подключения, неверные credentials, и т.д.)
- Если WooCommerce API недоступен - не ломать существующий функционал (graceful degradation)
