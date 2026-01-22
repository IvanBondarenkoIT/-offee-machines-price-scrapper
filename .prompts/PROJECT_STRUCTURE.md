# 📁 СТРУКТУРА ПРОЕКТА

## 🎯 АРХИТЕКТУРА

### Main (для деплоя на Railway)
- `web_app/` - Flask веб-приложение (44 файла)
- Используется для деплоя на Railway
- Работает стабильно
- **НЕ ТРОГАТЬ без необходимости**

### Локальное использование
- `run_full_cycle.py` - главный скрипт
- `build_price_comparison.py` - построение таблицы сравнения
- `scrapers/` - 8 скраперов
- `utils/` - утилиты

---

## 📂 КЛЮЧЕВЫЕ ФАЙЛЫ

### Основные скрипты
```
run_full_cycle.py              # Главный скрипт (НЕ ТРОГАТЬ)
build_price_comparison.py      # Построение сравнения (можно аккуратно)
```

### Скраперы (НЕ ТРОГАТЬ)
```
scrapers/
├── alta/alta_bs4_scraper.py
├── kontakt/kontakt_bs4_scraper.py
├── elite/elite_bs4_scraper.py
├── dimkava/dimkava_bs4_scraper.py
├── coffeehub/coffeehub_bs4_scraper.py
├── coffeepin/coffeepin_bs4_scraper.py
├── veli_store/veli_store_bs4_scraper.py
└── vega_ge/vega_ge_bs4_scraper.py
```

### Утилиты
```
utils/
├── model_extractor.py         # Извлечение моделей из названий
├── product_matcher.py         # Сопоставление товаров
├── excel_writer.py            # Запись в Excel
└── logger.py                  # Логирование
```

### Веб-приложение (Railway)
```
web_app/
├── app.py                     # Flask приложение
├── models/                    # SQLAlchemy модели
├── routes/                    # Flask routes
├── services/                  # Бизнес-логика
└── templates/                 # HTML шаблоны
```

---

## 🔄 ПОТОК ДАННЫХ

### Локальный цикл (run_full_cycle.py)
```
1. Запуск 8 скраперов
   ↓
2. Сохранение в data/output/*.xlsx
   ↓
3. build_price_comparison.py
   - Загрузка inventory (остатки.xls)
   - Загрузка scraped data
   - Сопоставление по моделям
   - Генерация price_comparison_*.xlsx
   ↓
4. Показ результатов
```

### Веб-приложение (Railway)
```
1. Загрузка Excel через /api/upload
   ↓
2. Парсинг в upload_service.py
   ↓
3. Сохранение в БД (PostgreSQL)
   ↓
4. Отображение в веб-интерфейсе
```

---

## 📊 ФОРМАТ ДАННЫХ

### Excel файлы от скраперов
- Колонки: `name`, `price`, `url`, `model` (опционально)
- Сохраняются в `data/output/`

### Excel файл сравнения (build_price_comparison.py)
- Лист "Price Comparison": товары с ценами конкурентов
- Лист "Statistics": статистика
- Колонки: Model, Name, Quantity, Our Price, ALTA, KONTAKT, ELITE, DIM_KAVA, etc.

---

## 🎯 ЦЕЛЬ: WooCommerce экспорт

**Создать отдельный модуль:**
- `export_woocommerce_data.py` - главный скрипт
- `utils/woocommerce_client.py` - API клиент
- Результат: Excel с WooCommerce данными
- **НЕ интегрировать в run_full_cycle.py** (пока)
