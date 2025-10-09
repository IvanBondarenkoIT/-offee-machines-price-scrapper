# Руководство по полному циклу мониторинга цен

## Обзор

Полный цикл автоматически:
1. ✅ Парсит все 4 сайта конкурентов
2. ✅ Загружает наши остатки
3. ✅ Сопоставляет товары по моделям
4. ✅ Создает таблицу сравнения цен
5. ✅ Показывает статистику и результаты

## Быстрый старт

```bash
python run_full_cycle.py
```

**Время выполнения**: ~2 минуты

## Что происходит на каждом этапе

### Этап 1: Парсинг конкурентов (~ 1.5 мин)

Последовательно запускаются скраперы:

1. **ALTA** (alta.ge) - 74 товара (~30 сек)
2. **KONTAKT** (kontakt.ge) - 28 товаров (~20 сек)
3. **ELITE** (ee.ge) - 40 товаров (~45 сек)
4. **DIM_KAVA** (dimkava.ge) - 41 товар (~35 сек)

**Результат**: Excel файлы в `data/output/`:
- `alta_bs4_prices_YYYYMMDD_HHMMSS.xlsx`
- `kontakt_bs4_prices_YYYYMMDD_HHMMSS.xlsx`
- `elite_delonghi_prices_YYYYMMDD_HHMMSS.xlsx`
- `dimkava_delonghi_prices_YYYYMMDD_HHMMSS.xlsx`

### Этап 2: Проверка данных (< 1 сек)

Проверяется наличие и количество товаров:
```
[OK] ALTA      :  74 products
[OK] KONTAKT   :  28 products
[OK] ELITE     :  40 products
[OK] DIM_KAVA  :  41 products
```

### Этап 3: Построение сравнения (< 5 сек)

1. Загрузка инвентаря (остатки.xls) - 47 товаров
2. Загрузка данных со всех сайтов - 183 товара
3. Извлечение моделей - 213 товаров
4. Нормализация и сопоставление
5. Fuzzy matching для вариантов
6. Создание таблицы сравнения

**Результат**: `price_comparison_YYYYMMDD_HHMMSS.xlsx`

### Этап 4: Показ результатов

Выводится:
- Общее количество сопоставленных товаров
- Топ-10 товаров по количеству
- Статистика по ценам
- Конкурентоспособность (сколько товаров у каждого конкурента)

## Результаты последнего запуска

```
TOTAL PRODUCTS COMPARED: 37/47 (79%)
Total quantity: 107 units
Total value: 121,533 GEL

Duration: 108 seconds (1.8 minutes)
```

### Покрытие по конкурентам

| Конкурент | Товаров с ценами |
|-----------|------------------|
| ALTA      | 25 (68%)         |
| KONTAKT   | 10 (27%)         |
| ELITE     | 16 (43%)         |
| DIM_KAVA  | 22 (59%)         |

### Топ-10 товаров по количеству

| Qty | Model | Our Price | Конкуренты |
|-----|-------|-----------|------------|
| 18  | EC9255 | 1,118 GEL | ELITE, DIM_KAVA |
| 14  | EC9865 | 1,814 GEL | DIM_KAVA |
| 8   | EC9255.T | 1,140 GEL | ELITE, DIM_KAVA |
| 5   | ECAM350.50.B | 1,544 GEL | ALTA, KONTAKT |
| 4   | EC9455.M | 1,167 GEL | KONTAKT, DIM_KAVA |

## Файлы результатов

### 1. Таблица сравнения
`data/output/price_comparison_YYYYMMDD_HHMMSS.xlsx`

**Вкладки**:
- **Price Comparison** - основная таблица
- **Statistics** - статистика

**Колонки**:
- Quantity - количество на складе
- Model - модель товара
- Product Name - полное название
- Our Price - наша цена
- ALTA, KONTAKT, ELITE, DIM_KAVA - цены конкурентов

**Формат цен**:
- `799 \ 559` - старая цена \ цена со скидкой
- `927` - обычная цена
- `-` - нет у конкурента

### 2. Индивидуальные файлы парсинга
`data/output/[source]_prices_YYYYMMDD_HHMMSS.xlsx`

Содержат полные данные с каждого сайта:
- index - номер
- name - название товара
- final_price - итоговая цена
- regular_price - обычная цена
- discount_price - цена со скидкой
- has_discount - есть ли скидка

## Периодичность запуска

### Рекомендуемая частота

**Ежедневно** (для активного мониторинга):
```bash
# Добавить в cron (Linux) или Task Scheduler (Windows)
# Запуск каждый день в 9:00
0 9 * * * cd /path/to/project && python run_full_cycle.py
```

**Еженедельно** (для обычного мониторинга):
```bash
# Каждый понедельник в 9:00
0 9 * * 1 cd /path/to/project && python run_full_cycle.py
```

### Windows Task Scheduler

1. Открыть Task Scheduler
2. Create Basic Task
3. Trigger: Daily / Weekly
4. Action: Start a program
5. Program: `python`
6. Arguments: `run_full_cycle.py`
7. Start in: `D:\CursorProjects\Coffee machines price scrapper`

## Устранение проблем

### Scraper failed

**Проблема**: Один из скраперов не работает

**Решение**:
1. Проверить доступность сайта
2. Запустить скрапер отдельно для диагностики:
   ```bash
   python scrapers/alta/alta_bs4_scraper.py
   ```
3. Проверить логи в `logs/scraper.log`

### No data files found

**Проблема**: Не найдены файлы с данными

**Решение**:
1. Проверить папку `data/output/`
2. Запустить скраперы вручную
3. Проверить права доступа к папке

### Model matching issues

**Проблема**: Мало товаров сопоставлено

**Решение**:
1. Проверить файл `остатки.xls` в `data/inbox/`
2. Убедиться, что модели извлекаются корректно
3. Посмотреть в `MATCHING_IMPROVEMENT_PLAN.md` для улучшений

## Анализ результатов

### Где наши цены лучше

```python
import pandas as pd

df = pd.read_excel('data/output/price_comparison_YYYYMMDD_HHMMSS.xlsx')

# Найти товары, где мы дешевле
for col in ['ALTA', 'KONTAKT', 'ELITE', 'DIM_KAVA']:
    # Парсить цены конкурентов
    # Сравнить с Our Price
    # Вывести товары где мы дешевле
```

### Где можно поднять цены

Товары, где наша цена значительно ниже конкурентов:
- Потенциал для увеличения маржи
- Проверить актуальность наших цен

### Где нужно снизить цены

Товары, где мы дороже всех конкурентов:
- Риск потери продаж
- Рассмотреть корректировку цен

## Дополнительные команды

### Только парсинг (без сравнения)

```bash
# ALTA
python scrapers/alta/alta_bs4_scraper.py

# KONTAKT
python scrapers/kontakt/kontakt_bs4_scraper.py

# ELITE
python scrapers/elite/elite_bs4_scraper.py

# DIM_KAVA
python scrapers/dimkava/dimkava_bs4_scraper.py
```

### Только сравнение (с существующими данными)

```bash
python build_price_comparison.py
```

### Экспорт в Google Sheets

```bash
python export_to_google_sheets.py
```

## Логи

Все логи сохраняются в `logs/scraper.log`:
```bash
# Посмотреть последние 50 строк
tail -n 50 logs/scraper.log

# Windows
Get-Content logs/scraper.log -Tail 50
```

## Следующие шаги

1. **Автоматизация**: Настроить периодический запуск
2. **Уведомления**: Добавить email/Telegram уведомления о результатах
3. **Анализ**: Создать дашборд для визуализации трендов цен
4. **Алерты**: Настроить оповещения о критических изменениях цен

## Поддержка

При возникновении проблем:
1. Проверить `logs/scraper.log`
2. Запустить с verbose режимом
3. Проверить документацию в `README.md`
4. Посмотреть план улучшений в `MATCHING_IMPROVEMENT_PLAN.md`

