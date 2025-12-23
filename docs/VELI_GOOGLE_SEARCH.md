# Veli Store Google Search Integration

## 🎯 Проблема

Некоторые товары DeLonghi/Melitta/Nivona есть на сайте Veli Store, но **не отображаются** в категориях:
- Внутренний поиск сайта не работает
- Фильтр по брендам показывает не все товары
- Товары находятся только через Google поиск

**Примеры скрытых товаров:**
- `CTJ2103.BK` (тостер) - не в категории "Coffee Makers"
- `CTOV2103.BG` (тостер) - не в категории "Coffee Makers"
- `DLSC301` (аксессуар) - не в категории "Coffee Makers"
- `ECAM290.42.TB` (кофемашина) - может отсутствовать

---

## ✅ Решение: Гибридный подход

### Этап 1: Парсинг категории (быстро)
```
Находим ~12 товаров из категории /coffee-makers-pots/
```

### Этап 2: Проверка недостающих (умно)
```
1. Извлекаем модели из найденных товаров
2. Сравниваем с моделями из остатков
3. Вычисляем разницу: missing = остатки - найденные
```

### Этап 3: Поиск через Google (только для недостающих!)
```
Для каждой недостающей модели:
  1. Поиск через Google: site:veli.store {model}
  2. Парсинг страницы товара
  3. Добавление в результаты
```

---

## 🔧 Использование

### По умолчанию (БЕЗ Google Search)
```python
from scrapers.veli_store.veli_store_bs4_scraper import VeliStoreScraper

scraper = VeliStoreScraper()  # enable_google_search=False (по умолчанию)
scraper.run()
# Результат: ~12 товаров из категории
```

### С Google Search (для недостающих)
```python
from scrapers.veli_store.veli_store_bs4_scraper import VeliStoreScraper
from utils.stock_api_client import StockApiClient

# Получить модели из остатков
api_client = StockApiClient()
inventory_df = api_client.fetch_stock_data()
models = inventory_df['model'].dropna().unique().tolist()

# Запустить с Google Search
scraper = VeliStoreScraper(
    enable_google_search=True,
    inventory_models=models
)
scraper.run()
# Результат: ~12 из категории + недостающие через Google
```

---

## 📊 Оптимизация

### ✅ Исключение найденных (реализовано!)
```python
# В методе search_missing_products():

# Шаг 1: Модели из категории
found_models = {extract_model(p['name']) for p in self.products}

# Шаг 2: Модели из остатков
inventory_models = set(self.inventory_models)

# Шаг 3: ИСКЛЮЧАЕМ найденные!
missing_models = inventory_models - found_models  # ← Только недостающие!

# Шаг 4: Если все найдены - НЕ ИЩЕМ через Google
if not missing_models:
    return []  # Выходим, экономим время
```

### Лимиты
- **Max 20 товаров** за один запуск (можно изменить в коде)
- **Пауза 2 секунды** между Google запросами (чтобы не блокировали)
- **Пауза 3 секунды** между парсингом товаров

---

## 🧪 Тестирование

### Тест 1: Базовая функциональность (без Google)
```bash
python test_veli_simple.py
```
Проверяет что существующий функционал не сломан.

### Тест 2: С Google Search
```bash
python test_veli_with_google.py
```
Демонстрирует:
1. Что находится в категории
2. Что нужно искать через Google
3. Что Google Search ищет ТОЛЬКО недостающие

---

## 📈 Производительность

| Метод | Товаров | Время |
|-------|---------|-------|
| Категория | ~12 | 10 сек |
| Google Search | 1 товар | ~5 сек |
| Google Search | 5 товаров | ~25 сек |

**Пример:**
- Остатки: 50 моделей
- Найдено в категории: 12 моделей
- Недостающих: 38 моделей
- Лимит Google: 20 моделей
- **Итого поисков через Google: 20** (не 50!)
- **Время Google: ~100 сек** (вместо 250 сек)

---

## ⚙️ Конфигурация

### В .env (опционально)
```bash
# Veli Store Google Search settings
VELI_GOOGLE_SEARCH_ENABLED=false  # По умолчанию выключен
VELI_GOOGLE_MAX_SEARCHES=20       # Макс. запросов к Google
VELI_GOOGLE_PAUSE_SECONDS=2       # Пауза между запросами
```

### В коде
```python
# scrapers/veli_store/veli_store_bs4_scraper.py
# Строка 369:
max_searches = 20  # ← Изменить здесь

# Строка 406:
time.sleep(2)  # ← Пауза между Google запросами
```

---

## 🚫 Не влияет на другие парсеры

- ✅ По умолчанию **ВЫКЛЮЧЕН** (`enable_google_search=False`)
- ✅ Другие парсеры работают как раньше
- ✅ `run_full_cycle.py` не изменён
- ✅ Можно использовать опционально

---

## 📝 Логи

### Без Google Search
```
[INFO] Total products scraped from categories: 12
[INFO] Total products (with Google search): 12
```

### С Google Search (все найдены)
```
[INFO] Already found models from category: 12
[INFO]   Models: ['ECAM22.110.SB', 'E957-203', ...]
[INFO] Inventory models to check: 12
[INFO] ✓ No missing products - all inventory items found in categories!
[INFO]   Skipping Google search - not needed!
```

### С Google Search (есть недостающие)
```
[INFO] Already found models from category: 12
[INFO]   Models: ['ECAM22.110.SB', 'E957-203', ...]
[INFO] Inventory models to check: 15
[INFO] ✗ Missing 3 models (NOT found in category):
[INFO]   ['CTJ2103.BK', 'CTOV2103.BG', 'DLSC301']
[INFO]   → Will search these via Google...
[INFO] [1/3] Searching via Google: CTJ2103.BK
[INFO]   -> Found: DeLonghi CTJ2103.BK Toaster - 239.00 GEL
...
[INFO] Found 3 missing products via Google
[INFO] Added 3 products via Google search
```

---

## 🎯 Итог

✅ **Оптимизировано**: Ищем через Google только недостающие  
✅ **Безопасно**: Не влияет на существующий функционал  
✅ **Гибко**: Можно включить/выключить по необходимости  
✅ **Эффективно**: Экономит время на уже найденных товарах

