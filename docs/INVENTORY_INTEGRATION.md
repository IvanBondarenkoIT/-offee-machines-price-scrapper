# Интеграция инвентаря (остатки.xls) в экспорт

## Обзор

Добавлена поддержка загрузки и экспорта данных из файла `остатки.xls` (наши складские остатки) в объединенный отчет Google Sheets.

## Что было сделано

### 1. Парсинг файла остатки.xls

Создана функция `load_inventory()` в `export_to_google_sheets.py`, которая:
- Читает файл `data/inbox/остатки.xls` без заголовков
- Находит все строки, содержащие товары DeLonghi
- Извлекает наименование товара и количество на складе
- Фильтрует только товары с количеством > 0

### 2. Структура данных

Файл `остатки.xls` имеет следующую структуру:
- Строки без фиксированных заголовков
- Товары DeLonghi начинаются примерно со строки 116
- Формат строки: `['номер.', 'Наименование товара', 'ед.изм.', количество]`

Примеры товаров:
```
1. DeLonghi Filter for water DLSC002 5513292811 - 252 шт.
2. DeLonghi ECAM22.114.B - 2 шт.
3. Delonghi EC 9865 M - 10 шт.
```

### 3. Результат парсинга

Из файла извлечено:
- **76 товаров DeLonghi**
- **1264 единицы** общего количества

Категории товаров:
- Кофеварки (coffee makers) - ~42 модели
- Аксессуары (accessories) - ~13 позиций
- Средства для чистки (cleaning) - ~7 позиций
- Посуда (dishes) - ~13 позиций
- Чайники и тостеры (kettles, toasters) - ~10 позиций

### 4. Экспорт в Google Sheets

Добавлена новая вкладка **INVENTORY** в файл `combined_prices_YYYYMMDD_HHMMSS.xlsx`:

**Структура вкладки:**
| # | Product Name | Quantity |
|---|--------------|----------|
| 1 | DeLonghi Filter for water DLSC002 5513292811 | 252 |
| 2 | DeLonghi Multiclean DL Set DLSC550 | 27 |
| ... | ... | ... |
| 76 | Delonghi toaster CTOV2103.GR | 1 |

### 5. Обновление SUMMARY

Вкладка SUMMARY теперь включает строку для INVENTORY:

| Store | Products | Total Quantity | Min Price | Max Price | Avg Price | With Discount |
|-------|----------|----------------|-----------|-----------|-----------|---------------|
| ALTA | 74 | - | 29 | 6089 | 1231.84 | 56 |
| KONTAKT | 28 | - | 549.99 | 5999.99 | 1985.34 | 28 |
| ELITE | 40 | - | 256.99 | 6959.99 | 2223.41 | 26 |
| DIM_KAVA | 41 | - | 35.0 | 3699.0 | 1090.49 | 0 |
| **INVENTORY** | **76** | **1264** | - | - | - | - |

## Технические детали

### Обработка путей

Использованы абсолютные пути для надежности:
```python
file_path = Path(__file__).parent / 'data' / 'inbox' / 'остатки.xls'
OUTPUT_DIR = Path(__file__).parent / "data" / "output"
```

### Парсинг строк

Логика извлечения данных:
```python
# Для каждой строки с DeLonghi
if len(row_values) == 4:
    name = str(row_values[1])  # Наименование - второй элемент
    qty = row_values[-1]        # Количество - последний элемент
elif len(row_values) == 3:
    name = str(row_values[0])
    qty = row_values[-1]
```

## Использование

```bash
python export_to_google_sheets.py
```

Результат:
```
[OK] Loading inventory from остатки.xls
[OK] Loaded 76 DeLonghi products from inventory
[OK] Sheet 'INVENTORY': 76 products (our stock)
```

## Файлы

- `export_to_google_sheets.py` - основной скрипт экспорта
- `data/inbox/остатки.xls` - исходный файл инвентаря
- `data/output/combined_prices_YYYYMMDD_HHMMSS.xlsx` - результат

## Коммиты

1. `89f7d74` - Add inventory (остатки.xls) to Google Sheets export
2. `4985167` - Update README: add INVENTORY sheet to export description

## Следующие шаги

Возможные улучшения:
1. Сопоставление товаров из INVENTORY с товарами из магазинов по моделям
2. Расчет разницы в ценах (наши vs конкуренты)
3. Анализ товаров, которые есть у конкурентов, но нет у нас
4. Автоматическое обновление файла остатки.xls из учетной системы

## Статистика

- Всего товаров в системе: **259 позиций** (183 с сайтов + 76 в инвентаре)
- Время выполнения: ~2-3 секунды
- Размер файла: ~50 KB

