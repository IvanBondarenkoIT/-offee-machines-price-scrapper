# Система мониторинга цен конкурентов

Автоматическая система для сбора и анализа цен на кофеварки DeLonghi с сайтов конкурентов.

**⚡ Локальный запуск**: `python run_full_cycle.py` (2 минуты на всё!)

**☁️ Деплой на Railway.com**: Готово к размещению в облаке с веб-интерфейсом! 
📖 См. [QUICK_START_RAILWAY.md](QUICK_START_RAILWAY.md)

## 📚 Документация

**📖 [Полная документация](docs/)** - Вся документация проекта

### 🚀 Быстрый старт
- **[docs/railway/QUICK_START_RAILWAY.md](docs/railway/QUICK_START_RAILWAY.md)** - Быстрый старт на Railway ⚡
- **[docs/general/PROJECT_OVERVIEW.md](docs/general/PROJECT_OVERVIEW.md)** - Обзор проекта для директора
- **[docs/general/FULL_CYCLE_GUIDE.md](docs/general/FULL_CYCLE_GUIDE.md)** - Руководство по полному циклу

### ☁️ Railway.com (Облачное размещение)
- **[docs/railway/](docs/railway/)** - Вся документация по Railway
  - Деплой на облако
  - Загрузка остатков
  - Исправление ошибок
  - API endpoints

### 💻 Локальное использование
- **[docs/general/](docs/general/)** - Общая документация
  - Локальный запуск
  - Git workflow
  - Создание отчетов

## 🎯 Что делает система

1. **Собирает цены** с 4 сайтов автоматически:
   - **ALTA** (alta.ge) - 68 товаров
   - **KONTAKT** (kontakt.ge) - 28 товаров
   - **ELITE** (ee.ge) - 40 товаров
   - **DIM KAVA** (dimkava.ge) - 41 товар (НАШ САЙТ)

2. **Сопоставляет товары** по моделям (37/47 товаров, 79%)

3. **Создает отчеты**:
   - Excel таблица сравнения цен
   - Word отчет для руководства
   - PDF для email/печати

**Время выполнения**: 2-3 минуты на всё!

## 📁 Структура проекта
```
Coffee machines price scrapper/
├── 📄 Основная документация (в корне)
│   ├── README.md                      # Этот файл
│   ├── PROJECT_OVERVIEW.md            # Обзор для директора ⭐
│   ├── FULL_CYCLE_GUIDE.md            # Руководство по использованию
│   └── EXECUTIVE_REPORT_GUIDE.md      # Создание отчетов
│
├── 🤖 Основные скрипты
│   ├── run_full_cycle.py              # Полный цикл (запускать это!)
│   ├── build_price_comparison.py      # Сравнение цен
│   ├── generate_executive_report.py   # Word отчет
│   ├── generate_all_reports.py        # Все отчеты сразу
│   └── convert_report_to_pdf.py       # Конвертация в PDF
│
├── 📊 Данные
│   ├── data/inbox/                    # Входные данные (остатки.xls)
│   └── data/output/                   # Результаты (Excel, Word, PDF)
│
├── 🔧 Скраперы
│   ├── scrapers/alta/                 # ALTA (68 товаров)
│   ├── scrapers/kontakt/              # KONTAKT (28 товаров)
│   ├── scrapers/elite/                # ELITE (40 товаров)
│   └── scrapers/dimkava/              # DIM_KAVA (41 товар, наш сайт)
│
├── 🛠️ Утилиты
│   ├── utils/model_extractor.py       # Извлечение моделей
│   ├── utils/excel_writer.py          # Сохранение в Excel
│   └── utils/logger.py                # Логирование
│
└── 📖 Техническая документация
    └── docs/                          # Планы, детали, история
```

## Установка

1. Создать виртуальное окружение:
```bash
python -m venv venv
```

2. Активировать виртуальное окружение:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Установить зависимости:
```bash
pip install -r requirements.txt
```

## Тестирование

Запустить быстрые тесты для проверки работоспособности:
```bash
python run_tests.py
```

Время выполнения: ~30-60 секунд

Тесты проверяют:
- ✅ Извлечение моделей из названий
- ✅ Сопоставление моделей
- ✅ Очистку цен
- ✅ Базовый парсинг ALTA (16 товаров)

## Использование

### Быстрый старт - Все магазины сразу

```bash
# Парсим все 4 магазина
python scrapers/alta/alta_bs4_scraper.py      # 74 товара, 31 сек
python scrapers/kontakt/kontakt_bs4_scraper.py # 28 товаров, 22 сек
python scrapers/elite/elite_bs4_scraper.py     # 40 товаров, 48 сек
python scrapers/dimkava/dimkava_bs4_scraper.py # 41 товар, 35 сек

# Создаем объединенный Excel для Google Sheets
python export_to_google_sheets.py
```

**Результат**: 183 товара за ~136 секунд (~2.3 минуты)

### Экспорт в Google Sheets

```bash
python export_to_google_sheets.py
```

Создает файл `combined_prices_YYYYMMDD_HHMMSS.xlsx` с 6 вкладками:
- **ALTA** - 74 товара
- **KONTAKT** - 28 товаров
- **ELITE** - 40 товаров
- **DIM_KAVA** - 41 товар (наш магазин)
- **INVENTORY** - 76 товаров DeLonghi из наших остатков (1264 единицы)
- **SUMMARY** - статистика

📖 Подробнее: [GOOGLE_SHEETS_GUIDE.md](GOOGLE_SHEETS_GUIDE.md)

### Отдельные парсеры

```bash
# ALTA (31 сек)
python scrapers/alta/alta_bs4_scraper.py

# KONTAKT (22 сек)
python scrapers/kontakt/kontakt_bs4_scraper.py

# ELITE (48 сек)
python scrapers/elite/elite_bs4_scraper.py

# DIM KAVA - наш магазин (35 сек)
python scrapers/dimkava/dimkava_bs4_scraper.py
```

Результаты сохраняются в `data/output/`:
- `*_prices_YYYYMMDD_HHMMSS.xlsx` - Excel файл
- `*_prices_YYYYMMDD_HHMMSS.csv` - CSV файл

### Структура результатов
Результаты содержат следующие колонки:
- `index` - номер товара (1-74)
- `name` - название товара
- `regular_price` - обычная цена (число)
- `regular_price_str` - обычная цена (текст)
- `discount_price` - цена со скидкой (число, если есть)
- `discount_price_str` - цена со скидкой (текст, если есть)
- `final_price` - итоговая цена (с учетом скидки)
- `has_discount` - есть ли скидка (true/false)
- `scraped_at` - дата и время парсинга
- `url` - URL страницы

## Технические детали

### ALTA (https://alta.ge)
- **URL с фильтром**: https://alta.ge/en/small-domestic-appliances/brand=delonghi;-c7s
- **Количество товаров**: 74
- **Кнопка "Загрузить еще"**: `/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[4]/button`
- **XPath для названий**: Указаны в `data/inbox/Parsing alta.xlsx`
- **XPath для цен**: Указаны в `data/inbox/Parsing alta.xlsx`
- **XPath для цен со скидкой**: Указаны в `data/inbox/Parsing alta.xlsx`

### Структура данных из Excel
Файл `Parsing alta.xlsx` содержит:
- Колонка 1: XPath для названия товара
- Колонка 2: Примеры названий товаров
- Колонка 3: XPath для обычной цены
- Колонка 4: Примеры цен
- Колонка 5: XPath для цены со скидкой
- Колонка 6: Примеры цен со скидкой

## Статус выполнения

### ✅ Все магазины готовы (4/4)

| Магазин | Товаров | Время | Статус |
|---------|---------|-------|--------|
| ALTA | 74 | 31 сек | ✅ Готово |
| KONTAKT | 28 | 22 сек | ✅ Готово |
| ELITE | 40 | 48 сек | ✅ Готово |
| DIM KAVA | 41 | 35 сек | ✅ Готово |
| **ИТОГО** | **183** | **136 сек** | **✅ 100%** |

### Дополнительные функции
- ✅ Анализ цен (analyze_prices.py)
- ✅ Сравнение с нашим инвентарем (compare_prices.py)
- ✅ Экспорт в Google Sheets (export_to_google_sheets.py)
- ✅ Тесты (pytest)
- ✅ Документация

## Требования
- Python 3.8+
- Selenium 4.27+
- Chrome/Firefox браузер
- Стабильное интернет-соединение

