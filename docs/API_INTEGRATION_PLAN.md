# 📋 ПЛАН ИНТЕГРАЦИИ STOCK API

**Дата**: 11 декабря 2025  
**Цель**: Заменить чтение Excel файла остатков на API запрос к серверу

---

## 🎯 ТЕКУЩАЯ СИТУАЦИЯ

### Что работает сейчас:
```
build_price_comparison.py 
  → load_inventory()
    → InventoryParser.parse_file('остатки.xls')
      → Парсинг Excel файла (сложная структура)
        → Возвращает DataFrame с полями:
          - name, model, brand, quantity, price, category, is_valid
```

### Что есть в API:
- **Endpoint**: `POST /api/query`
- **Формат**: JSON с SQL запросом
- **Ответ**: `{success: true, data: [...]}` 
- **Поля**: GROUP_NAME, GROUP_ID, GOOD_ID, GOOD_NAME, QUANTITY, PRICE, TOTAL_SUM
- **Точность**: 99.89% (проверено)

---

## 🔍 АНАЛИЗ: ЧТО НУЖНО, А ЧТО НЕТ

### ✅ ЧТО НУЖНО ИЗМЕНИТЬ:

1. **`build_price_comparison.py`** - метод `load_inventory()`
   - Сейчас: читает Excel файл через `InventoryParser`
   - Нужно: получать данные через API
   - **Затронуто**: 1 метод в 1 файле

2. **Конфигурация** - добавить API settings
   - URL endpoint
   - Возможно токен авторизации
   - Таймауты и retry настройки

3. **Новый модуль** - `utils/stock_api_client.py`
   - Класс для работы с API
   - Метод получения данных
   - Конвертация JSON → DataFrame в формате `InventoryParser`

### ❌ ЧТО НЕ НУЖНО ТРОГАТЬ:

1. **Все скраперы** (6 штук) - НЕ ТРОГАТЬ
   - alta, kontakt, elite, dimkava, coffeehub, coffeepin
   - Они не работают с инвентарём

2. **`utils/inventory_parser.py`** - ОСТАВИТЬ КАК ЕСТЬ
   - Может понадобиться для fallback
   - Не удалять, только не использовать

3. **`utils/enhanced_matcher.py`** - НЕ ТРОГАТЬ
   - Работает с уже загруженными данными
   - Не зависит от источника данных

4. **`utils/model_extractor.py`** - НЕ ТРОГАТЬ
   - Извлекает модели из названий
   - Универсальный, работает с любыми данными

5. **`run_full_cycle.py`** - ПРОВЕРИТЬ, НО НЕ МЕНЯТЬ
   - Просто запускает все скраперы
   - Может не зависеть от инвентаря

---

## 📝 ДЕТАЛЬНЫЙ ПЛАН РЕАЛИЗАЦИИ

### ЭТАП 1: Подготовка (Сбор информации)

**Задачи:**
- [ ] Узнать у пользователя:
  - URL API endpoint
  - Нужен ли токен авторизации?
  - Есть ли ограничения по запросам?
- [ ] Уточнить формат SQL запроса (из документации)
- [ ] Понять какие поля из API соответствуют полям InventoryParser

**Риски**: Нет
**Время**: 5 минут

---

### ЭТАП 2: Создание модуля API клиента

**Файл**: `utils/stock_api_client.py`

**Что создать:**
```python
class StockApiClient:
    def __init__(self, api_url, api_token=None)
    def get_stock_data(self) -> pd.DataFrame
    def _make_request(self, sql_query) -> dict
    def _convert_to_dataframe(self, api_response) -> pd.DataFrame
```

**Логика конвертации API → DataFrame:**
```
API Response:
  GOOD_NAME → name
  GOOD_ID → good_id (новое поле)
  QUANTITY → quantity
  PRICE → price
  GROUP_NAME → category (опционально)

Нужно добавить:
  model → extract using ModelExtractor
  brand → extract using InventoryParser._extract_brand()
  is_valid → calculate using InventoryParser._is_valid_product()
```

**Важно**: 
- Добавить обработку ошибок (timeout, connection error)
- Добавить retry механизм (3 попытки)
- Логирование всех запросов

**Риски**: 
- API может быть недоступен
- **Решение**: Fallback на Excel файл

**Время**: 30 минут

---

### ЭТАП 3: Конфигурация

**Файл**: `config.py` (добавить секцию)

```python
# STOCK API Configuration
STOCK_API_CONFIG = {
    "enabled": True,  # Переключатель API/Excel
    "api_url": "https://api.example.com/api/query",  # Нужно уточнить
    "api_token": os.getenv("STOCK_API_TOKEN", None),  # Из env
    "timeout": 30,  # секунды
    "retry_attempts": 3,
    "retry_delay": 2,  # секунды между попытками
    "fallback_to_excel": True,  # Использовать Excel если API не работает
}
```

**Файл**: `.env.example` (создать/обновить)

```
# Stock API Configuration
STOCK_API_URL=https://your-api-endpoint.com/api/query
STOCK_API_TOKEN=your_token_here_if_needed
```

**Риски**: Нет
**Время**: 10 минут

---

### ЭТАП 4: Модификация build_price_comparison.py

**Что изменить:**

**Текущий код** (строки 29-104):
```python
def load_inventory(self) -> pd.DataFrame:
    """Load inventory from остатки.xls using InventoryParser"""
    # ... текущая логика с Excel ...
```

**Новый код**:
```python
def load_inventory(self) -> pd.DataFrame:
    """Load inventory from API or Excel file"""
    print("\n[1/6] Loading INVENTORY...")
    
    # Проверяем конфигурацию
    if STOCK_API_CONFIG.get("enabled", False):
        print("  Attempting to load from API...")
        try:
            # Пробуем загрузить через API
            api_client = StockApiClient(
                api_url=STOCK_API_CONFIG["api_url"],
                api_token=STOCK_API_CONFIG.get("api_token")
            )
            df_result = api_client.get_stock_data()
            
            print(f"[OK] Loaded {len(df_result)} products from API")
            print(f"     Brands: {df_result['brand'].value_counts().to_dict()}")
            return df_result
            
        except Exception as e:
            print(f"[ERROR] Failed to load from API: {e}")
            
            # Fallback к Excel если включен
            if STOCK_API_CONFIG.get("fallback_to_excel", True):
                print("[FALLBACK] Loading from Excel file...")
                return self._load_inventory_from_excel()
            else:
                raise
    else:
        print("  API disabled, loading from Excel...")
        return self._load_inventory_from_excel()

def _load_inventory_from_excel(self) -> pd.DataFrame:
    """Load inventory from Excel file (старая логика)"""
    # Весь текущий код из load_inventory() переносим сюда
    # БЕЗ ИЗМЕНЕНИЙ
```

**Важно**:
- Старая логика НЕ удаляется, только переносится в отдельный метод
- Добавляется переключатель через config
- Добавляется fallback механизм

**Риски**: 
- Может сломаться если API вернёт неправильный формат
- **Решение**: Валидация данных перед возвратом

**Время**: 20 минут

---

### ЭТАП 5: Тестирование API клиента (изолированно)

**Файл**: `test_stock_api.py` (временный)

**Что тестировать:**
1. Успешный запрос к API
2. Проверка формата ответа
3. Конвертация в DataFrame
4. Извлечение моделей и брендов
5. Валидация продуктов
6. Обработка ошибок (timeout, 404, 500)
7. Retry механизм

**Команда**:
```bash
python test_stock_api.py
```

**Ожидаемый результат**:
```
[OK] API connection successful
[OK] Loaded 1294 products from API
[OK] Extracted models for 95% products
[OK] Brands: {'DeLonghi': 150, 'Melitta': 45, ...}
[OK] Valid products: 85 (category='product', price>50)
```

**Риски**:
- API может быть медленным
- **Решение**: Увеличить timeout

**Время**: 15 минут

---

### ЭТАП 6: Интеграционное тестирование

**Тест 1**: Запуск build_price_comparison.py (только инвентарь)
```bash
# Включаем API
# В config.py: STOCK_API_CONFIG["enabled"] = True

python build_price_comparison.py
```

**Проверяем**:
- Данные загружаются через API ✓
- Количество продуктов соответствует (~85) ✓
- Нет ошибок ✓

**Тест 2**: Fallback к Excel (симулируем ошибку API)
```bash
# В config.py: STOCK_API_CONFIG["api_url"] = "https://invalid-url.com"

python build_price_comparison.py
```

**Проверяем**:
- API не работает (ошибка) ✓
- Fallback к Excel ✓
- Данные загружаются из Excel ✓

**Тест 3**: Полный цикл с API
```bash
python run_full_cycle.py
```

**Проверяем**:
- Все скраперы работают ✓
- Инвентарь загружается через API ✓
- Сравнение цен строится правильно ✓
- Excel файл создаётся ✓

**Риски**:
- Могут быть несоответствия в данных API vs Excel
- **Решение**: Сравнить результаты и скорректировать

**Время**: 20 минут

---

### ЭТАП 7: Сравнение результатов (API vs Excel)

**Создать**: `compare_api_vs_excel.py` (временный)

**Что сравнить**:
1. Количество продуктов
2. Список брендов
3. Количество валидных продуктов
4. Цены (для одинаковых товаров)
5. Модели (для одинаковых товаров)

**Отчёт**:
```
API vs EXCEL COMPARISON:
  Total products: API=1294, Excel=1244 (diff: +50, +4.0%)
  Valid products: API=85, Excel=85 (diff: 0, 0%)
  Brands: DeLonghi, Melitta, Nivona (same)
  Price match: 98.5% (42 of 85 products have identical prices)
  Model extraction: 95% success rate for both
```

**Критерии успеха**:
- Valid products: разница < 5%
- Price match: > 95%
- Model extraction: > 90%

**Риски**: Нет
**Время**: 15 минут

---

### ЭТАП 8: Документация

**Обновить файлы:**

1. **`README_FINALIZED.md`** - добавить секцию про API
```markdown
## 🔌 Stock Data Source

By default, inventory is loaded from Excel file `data/inbox/остатки.xls`.

To use API instead:
1. Set API URL in config.py or .env
2. Enable API in config: `STOCK_API_CONFIG["enabled"] = True`
3. Run full cycle as usual
```

2. **`docs/STOCK_API_INTEGRATION.md`** - добавить раздел "Implementation Status"
```markdown
## ✅ Implementation Status

- [x] API documented
- [x] API tested (99.89% accuracy)
- [x] StockApiClient implemented
- [x] Integration with build_price_comparison.py
- [x] Fallback to Excel
- [x] Configuration
- [x] Testing
```

3. **`STAGE_COMPLETE_20251211.md`** - обновить
```markdown
## 🆕 Добавлено в этом этапе:

### API интеграция для получения остатков:
- Создан `utils/stock_api_client.py`
- Добавлена конфигурация `STOCK_API_CONFIG`
- Модифицирован `build_price_comparison.py`
- Сохранён fallback на Excel файл
```

**Риски**: Нет
**Время**: 10 минут

---

### ЭТАП 9: Очистка и финализация

**Удалить временные файлы:**
- `test_stock_api.py`
- `compare_api_vs_excel.py`

**Закоммитить**:
```bash
git add .
git commit -m "feat: Add Stock API integration with Excel fallback"
git push origin feature/web-app
```

**Риски**: Нет
**Время**: 5 минут

---

## ⏱️ ОБЩЕЕ ВРЕМЯ

| Этап | Время | Риск |
|------|-------|------|
| 1. Подготовка | 5 мин | Низкий |
| 2. API Client | 30 мин | Средний |
| 3. Конфигурация | 10 мин | Низкий |
| 4. Модификация build | 20 мин | Средний |
| 5. Тест API | 15 мин | Низкий |
| 6. Интеграция тест | 20 мин | Высокий |
| 7. Сравнение | 15 мин | Низкий |
| 8. Документация | 10 мин | Низкий |
| 9. Очистка | 5 мин | Низкий |
| **ИТОГО** | **~2 часа** | |

---

## 🎯 КРИТЕРИИ УСПЕХА

### Обязательные:
- ✅ API загружает данные без ошибок
- ✅ Формат данных совпадает с InventoryParser
- ✅ Fallback на Excel работает при ошибках API
- ✅ Все существующие скраперы работают
- ✅ Полный цикл `run_full_cycle.py` выполняется успешно

### Желательные:
- ✅ Количество valid products: разница < 5%
- ✅ API быстрее чем Excel (< 5 секунд)
- ✅ Retry механизм работает при временных ошибках
- ✅ Логирование всех API запросов

---

## 🚨 РИСКИ И РЕШЕНИЯ

| Риск | Вероятность | Решение |
|------|-------------|---------|
| API недоступен | Средняя | Fallback на Excel |
| Неправильный формат данных | Низкая | Валидация + тесты |
| Медленный API | Средняя | Timeout + кэширование |
| Изменилась структура API | Низкая | Версионирование API |
| Сломались скраперы | Очень низкая | Не трогаем их код |

---

## 📋 ЧЕКЛИСТ ПЕРЕД НАЧАЛОМ

- [ ] Получить API URL от пользователя
- [ ] Уточнить нужен ли токен авторизации
- [ ] Проверить доступность API (ping test)
- [ ] Убедиться что Excel файл есть (для fallback)
- [ ] Сделать backup текущего кода
- [ ] Создать тестовую ветку (опционально)

---

## 📋 ЧЕКЛИСТ ПОСЛЕ РЕАЛИЗАЦИИ

- [ ] API клиент работает
- [ ] Конфигурация настроена
- [ ] build_price_comparison.py использует API
- [ ] Fallback на Excel работает
- [ ] Тесты пройдены
- [ ] Сравнение API vs Excel (< 5% разница)
- [ ] Полный цикл работает
- [ ] Документация обновлена
- [ ] Код закоммичен
- [ ] Временные файлы удалены

---

**ВАЖНО**: На каждом этапе тестировать изолированно, не переходить к следующему пока текущий не работает!


