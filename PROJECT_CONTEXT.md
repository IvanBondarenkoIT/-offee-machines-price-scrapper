# 🎯 PROJECT CONTEXT - Coffee Machines Price Scraper

**Последнее обновление**: 7 октября 2025, 14:56

## 📊 ТЕКУЩЕЕ СОСТОЯНИЕ

### Готово (2/3 магазина) ✅

#### 1. ALTA.ge ✅ ПОЛНОСТЬЮ ГОТОВ
- **URL**: https://alta.ge/en/small-domestic-appliances/brand=delonghi;-c7s
- **Товаров**: 74 DeLonghi
- **Время парсинга**: 31 секунда (BS4) / 13.6 минут (Selenium)
- **Ускорение**: BS4 в 26.4 раза быстрее!

**Файлы:**
```
scrapers/alta/
├── alta_bs4_scraper.py         ⚡ РЕКОМЕНДУЕТСЯ (31 сек)
├── alta_selenium_scraper.py    🛡️ Надежный (13.6 мин)
├── ALTA_PROMPT.md              📖 Полная документация
├── README.md                   🚀 Быстрый старт
└── __init__.py
```

**Технологии:**
- Selenium для загрузки и клика "Load More"
- BeautifulSoup для быстрого парсинга HTML
- Поиск по h2 тегам (названия)
- Извлечение цен из span элементов

**XPath:**
- Кнопка Load More: `/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[4]/button`
- Товары: `/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[3]/div[N]/...`

---

#### 2. KONTAKT.ge ✅ ГОТОВ
- **URL**: https://kontakt.ge/en/samzareulos-teknika/samzareulos-tsvrili-teknika/qavis-aparatebi?kh_mtsarmoebeli=DeLonghi
- **Товаров**: 28 DeLonghi
- **Время парсинга**: 22 секунды (BS4)

**Файлы:**
```
scrapers/kontakt/
├── kontakt_bs4_scraper.py      ⚡ Быстрый (22 сек)
├── kontakt_selenium_scraper.py ⚠️ Частично (не завершен)
├── KONTAKT_PROMPT.md           📖 Документация
├── README.md                   🚀 Быстрый старт
└── __init__.py
```

**Технологии:**
- CSS классы (проще чем XPath!)
- `.prodItem__title` - названия
- `.prodItem__prices` - цены
- `strong > i` или `strong > b` - значение цены

**XPath:**
- Кнопка Load More: `/html/body/div[1]/main/div[4]/div/div[5]/div/div[2]/button`
- fullXPath примера: `/html/body/div[1]/main/div[4]/div/div[5]/div/div[2]/div[1]/div[28]/div[3]`

---

#### 3. ELITE ⏳ TODO
- **Файл данных**: `data/inbox/Parsing elit.xlsx`
- **Статус**: Ожидает реализации

---

## 📁 Структура проекта

```
Coffee machines price scrapper/
├── scrapers/
│   ├── alta/                    ✅ ГОТОВО (74 товара, 31 сек)
│   ├── kontakt/                 ✅ ГОТОВО (28 товаров, 22 сек)
│   ├── elite/                   ⏳ TODO
│   └── __init__.py
├── utils/
│   ├── logger.py                📝 Логирование
│   ├── excel_writer.py          💾 Сохранение в Excel/CSV
│   └── product_matcher.py       🔍 Извлечение и сопоставление моделей
├── tests/
│   ├── test_alta_scraper.py     ✅ 4/4 тестов pass
│   └── README.md
├── data/
│   ├── inbox/                   📥 Исходные данные (gitignored)
│   │   ├── Parsing alta.xlsx
│   │   ├── Parsing kontakt.xlsx
│   │   ├── Parsing elit.xlsx
│   │   └── сравнение цен .xlsx
│   └── output/                  📤 Результаты (gitignored)
├── logs/                        📋 Логи (gitignored)
├── analyze_prices.py            📊 Анализ цен
├── compare_prices.py            🔍 Сравнение с инвентарем
├── run_tests.py                 🧪 Запуск тестов
├── config.py                    ⚙️ Конфигурация
├── main.py                      🚪 Точка входа
├── requirements.txt             📦 Зависимости
├── .gitignore                   🚫 Исключения
└── README.md                    📖 Документация
```

---

## 🚀 ЗАПУСК СКРАПЕРОВ

### ALTA (74 товара, 31 сек)
```bash
python scrapers/alta/alta_bs4_scraper.py
```

### KONTAKT (28 товаров, 22 сек)
```bash
python scrapers/kontakt/kontakt_bs4_scraper.py
```

### Тесты (~60 сек)
```bash
python run_tests.py
```

### Анализ цен
```bash
python analyze_prices.py
```

### Сравнение с инвентарем
```bash
python compare_prices.py
```

---

## 📊 РЕЗУЛЬТАТЫ И МЕТРИКИ

### Парсинг

| Магазин | Товаров | Время | Скорость | Статус |
|---------|---------|-------|----------|--------|
| ALTA | 74 | 31 сек | 2.4/сек | ✅ |
| KONTAKT | 28 | 22 сек | 1.3/сек | ✅ |
| ELITE | ? | - | - | ⏳ |
| **ИТОГО** | **102** | **53 сек** | **1.9/сек** | **2/3** |

### Сравнение с нашими ценами (ALTA)

**Найдено 8 совпадающих товаров:**
- ✅ Мы ДЕШЕВЛЕ на ВСЕХ 8 товарах (100%)
- 💰 Средняя экономия: **384.38 GEL**
- 📈 Диапазон экономии: 163 - 1187 GEL

**Примеры:**
- DeLonghi Rivelia: Мы 1812₾ vs ALTA 2999₾ = **-1187₾**
- Eletta Explore: Мы 1899₾ vs ALTA 2309₾ = **-410₾**
- Dedica EC685: Мы 396₾ vs ALTA 559₾ = **-163₾**

---

## 🔧 ТЕХНИЧЕСКИЕ ДЕТАЛИ

### Зависимости
```txt
beautifulsoup4==4.12.3    # HTML парсинг
lxml==5.3.0               # XML/HTML parser
selenium==4.27.1          # WebDriver
webdriver-manager==4.0.2  # Auto driver install
openpyxl==3.1.4          # Excel
pandas==2.1.4            # Data processing
python-dotenv==1.0.1     # Environment
pytest==7.4.3            # Testing (optional)
```

### Конфигурация (config.py)

```python
ALTA_CONFIG = {
    "url": "https://alta.ge/en/small-domestic-appliances/brand=delonghi;-c7s",
    "expected_products": 74,
    "load_more_button_xpath": "/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[4]/button",
}

KONTAKT_CONFIG = {
    "url": "https://kontakt.ge/en/samzareulos-teknika/samzareulos-tsvrili-teknika/qavis-aparatebi?kh_mtsarmoebeli=DeLonghi",
    "expected_products": 28,
    "load_more_button_xpath": "/html/body/div[1]/main/div[4]/div/div[5]/div/div[2]/button",
}

SELENIUM_CONFIG = {
    "implicit_wait": 3,
    "page_load_timeout": 30,
    "load_more_wait": 1,
    "max_load_more_attempts": 30,
    "headless": False,
}
```

---

## 🎯 ИЗВЛЕЧЕНИЕ МОДЕЛЕЙ

### Regex паттерны (utils/product_matcher.py)

```python
# В скобках: DeLonghi Magnifica S (ECAM22.114.B)
pattern1 = r'\(([A-Z0-9]+[.\-][A-Z0-9.]+)\)'

# После DeLonghi: DeLonghi ECAM22.114.B
pattern2 = r'([A-Z]{2,}[0-9]+[.\-][A-Z0-9.]+[A-Z]?)'

# Простые: DLSC310, KG200
pattern3 = r'\b([A-Z]{2,}[0-9]{3,})\b'
```

### Примеры

**ALTA:**
```
DeLonghi Magnifica S (ECAM22.114.B)  -> ECAM22.114.B
DeLonghi Dedica (EC685.R)            -> EC685.R
```

**KONTAKT:**
```
Coffee Machine DeLonghi EC890.GR     -> EC890.GR
Coffee machine Delonghi EXAM440.55.W -> EXAM440.55.W
```

---

## 📈 PERFORMANCE BENCHMARKS

### Сравнение методов парсинга

| Метод | ALTA (74) | KONTAKT (28) | Ускорение |
|-------|-----------|--------------|-----------|
| **Selenium XPath** | 13.6 мин | N/A | - |
| **BeautifulSoup** | 31 сек | 22 сек | **26.4x** |

### Узкие места Selenium
- implicit_wait на каждый элемент (3 сек)
- Множественные попытки XPath
- ~9 секунд на товар

### Почему BS4 быстрее
- ✅ Один раз получаем HTML
- ✅ Парсинг локально (без сети)
- ✅ Простые CSS селекторы
- ✅ Нет ожиданий на каждый элемент

---

## 🧪 ТЕСТИРОВАНИЕ

### Тесты (tests/test_alta_scraper.py)

**Запуск:**
```bash
python run_tests.py
```

**Результаты:**
- ✅ Model Extraction: 5/5 (100%)
- ✅ Model Matching: 4/4 (100%)
- ✅ Price Cleaning: 6/6 (100%)
- ✅ ALTA Quick Test: PASS

**Время**: ~30-60 секунд

**Что тестируется:**
- Извлечение моделей из названий
- Сопоставление моделей (exact, fuzzy, case-insensitive)
- Очистка цен (символы валюты, GEL, кавычки)
- Быстрый парсинг первых 16 товаров ALTA

---

## 📝 ВАЖНЫЕ ФАЙЛЫ ДОКУМЕНТАЦИИ

### Основные
- **README.md** - Общая документация проекта
- **PROJECT_STATUS.md** - Текущий статус
- **PROJECT_CONTEXT.md** - Этот файл (контекст для продолжения)
- **QUICK_START.md** - Быстрый старт для пользователя
- **PROMPT.md** - Техническое задание
- **ALTA_CHECKLIST.md** - Чеклист ALTA

### По магазинам
- **scrapers/alta/ALTA_PROMPT.md** - Все нюансы ALTA
- **scrapers/kontakt/KONTAKT_PROMPT.md** - Все нюансы KONTAKT
- **tests/README.md** - Документация тестов

---

## 🔄 КАК ПРОДОЛЖИТЬ РАБОТУ

### После перезапуска проекта:

1. **Активировать окружение:**
   ```bash
   venv\Scripts\activate
   ```

2. **Проверить что все работает:**
   ```bash
   python run_tests.py
   ```

3. **Запустить парсеры:**
   ```bash
   # ALTA
   python scrapers/alta/alta_bs4_scraper.py
   
   # KONTAKT
   python scrapers/kontakt/kontakt_bs4_scraper.py
   ```

4. **Проанализировать результаты:**
   ```bash
   python analyze_prices.py
   python compare_prices.py
   ```

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

### Приоритет 1: ELITE скрапер ⏳

**Данные:**
- Файл: `data/inbox/Parsing elit.xlsx`
- Аналогичная структура как у ALTA и KONTAKT

**План:**
1. Создать `scrapers/elite/`
2. Изучить структуру сайта (URL из Excel)
3. Создать BS4 скрапер (шаблон: KONTAKT или ALTA)
4. Протестировать
5. Документировать
6. Закоммитить

### Приоритет 2: Объединенный парсер

**Идея:** Один скрипт для всех магазинов
```bash
python scrape_all.py
```

### Приоритет 3: Автоматизация

- Планировщик задач (Windows Task Scheduler / cron)
- Ежедневный парсинг
- Уведомления о изменении цен
- История цен (база данных)

### Приоритет 4: Анализ и отчеты

- Сравнение всех 3 магазинов
- Графики динамики цен
- Excel отчеты для менеджмента
- Web dashboard

---

## 💾 ВЫХОДНЫЕ ДАННЫЕ

### Структура результатов

```python
{
    "index": 1,                          # Номер товара
    "name": "DeLonghi ...",              # Название
    "regular_price": 2649.0,             # Обычная цена (float)
    "regular_price_str": "2649",         # Обычная цена (string)
    "discount_price": 1859.0,            # Скидка (float, может быть None)
    "discount_price_str": "1859",        # Скидка (string)
    "final_price": 1859.0,               # Итоговая цена
    "has_discount": True,                # Есть ли скидка
    "scraped_at": "2025-10-07 14:05:35", # Дата парсинга
    "url": "https://...",                # URL страницы
    "store": "ALTA",                     # Магазин (для KONTAKT+)
}
```

### Файлы результатов

```
data/output/
├── alta_delonghi_prices_20251007_140535.xlsx      # ALTA Excel
├── alta_delonghi_prices_20251007_140535.csv       # ALTA CSV
├── kontakt_bs4_prices_20251007_145325.xlsx        # KONTAKT Excel
├── kontakt_bs4_prices_20251007_145325.csv         # KONTAKT CSV
└── price_comparison_20251007_134725.xlsx          # Сравнение
```

---

## 🛠️ КЛЮЧЕВЫЕ МОДУЛИ

### utils/product_matcher.py

**Функции:**
- `extract_model(name)` - Извлечь модель из названия
- `normalize_model(model)` - Нормализовать модель
- `models_match(m1, m2)` - Точное совпадение
- `fuzzy_match(m1, m2)` - Нечеткое совпадение (варианты цветов)

**Примеры:**
```python
extract_model("DeLonghi Magnifica S (ECAM22.114.B)")  # -> "ECAM22.114.B"
models_match("ECAM22.114.B", "ecam22.114.b")          # -> True
fuzzy_match("ECAM22.114.B", "ECAM22.114.SB")          # -> True (варианты)
```

### utils/excel_writer.py

**Функции:**
- `save_to_excel(data, filename)` - Сохранить в Excel
- `save_to_csv(data, filename)` - Сохранить в CSV
- Автоматический timestamp в именах файлов

### utils/logger.py

**Особенности:**
- Логирование в консоль (INFO)
- Логирование в файл (DEBUG + INFO + ERROR)
- Файл: `logs/scraper.log`

---

## 🔍 ИЗВЕСТНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ

### 1. Unicode ошибки в логах (₾, ✓, ✗)
**Проблема:** Windows console cp1251 не поддерживает Unicode

**Решение:** Заменены все символы на ASCII:
- ✓ → [OK]
- ✗ → [ERROR]
- ⚠ → [WARNING]
- ₾ → GEL

### 2. Медленный Selenium парсинг
**Проблема:** implicit_wait на каждый элемент

**Решение:** BS4 скраперы - берут HTML один раз, парсят локально

### 3. Защита от ботов
**Проблема:** CloudFlare блокирует

**Решение:**
```python
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
```

### 4. Разная структура товаров
**Проблема:** У ALTA - XPath, у KONTAKT - CSS классы

**Решение:** Отдельные скраперы для каждого магазина

---

## 📊 СТАТИСТИКА ПАРСИНГА

### ALTA (последний запуск)
- Дата: 7 октября 2025, 14:05
- Товаров: 74/74 (100%)
- Время: 31 секунда
- Средняя цена: 1231.84 GEL
- Со скидкой: ~95%
- Средняя скидка: 24.5%

### KONTAKT (последний запуск)
- Дата: 7 октября 2025, 14:53
- Товаров: 28/28 (100%)
- Время: 22 секунды
- Диапазон цен: 799.99 - 8699.99 GEL
- Средняя цена: ~2500 GEL

---

## 🔗 ССЫЛКИ

### GitHub
**Repository**: https://github.com/IvanBondarenkoIT/-offee-machines-price-scrapper

**Коммитов**: 10
- Initial commit (Selenium ALTA)
- Price analysis tools
- BS4 scraper (26x faster)
- ALTA organization
- Test suite
- KONTAKT scraper
- Cleanup debug files

### Сайты
- **ALTA**: https://alta.ge/en/small-domestic-appliances/brand=delonghi;-c7s
- **KONTAKT**: https://kontakt.ge/en/samzareulos-teknika/samzareulos-tsvrili-teknika/qavis-aparatebi?kh_mtsarmoebeli=DeLonghi
- **ELITE**: TBD (из Excel файла)

---

## 📋 ЧЕКЛИСТ ДЛЯ ELITE

Когда будем делать ELITE, следовать этому плану:

- [ ] 1. Создать `scrapers/elite/`
- [ ] 2. Добавить ELITE_CONFIG в config.py
- [ ] 3. Изучить `data/inbox/Parsing elit.xlsx`
- [ ] 4. Определить URL и структуру сайта
- [ ] 5. Создать debug скрипт для анализа HTML
- [ ] 6. Найти CSS классы или XPath для:
  - [ ] Названий товаров
  - [ ] Цен
  - [ ] Кнопки "Load More"
- [ ] 7. Создать BS4 скрапер (шаблон: KONTAKT)
- [ ] 8. Протестировать
- [ ] 9. Создать документацию (ELITE_PROMPT.md)
- [ ] 10. Добавить тесты
- [ ] 11. Закоммитить и запушить

---

## 💡 СОВЕТЫ ДЛЯ РАЗРАБОТКИ

### При создании нового скрапера:

1. **Анализ структуры:**
   - Откр
ыть сайт в браузере
   - F12 -> Elements
   - Найти названия товаров и цены
   - Скопировать fullXPath или CSS селекторы

2. **Debug скрипт:**
   - Создать `debug_[магазин].py`
   - Загрузить страницу с Selenium
   - Сохранить HTML
   - Попробовать разные селекторы
   - Удалить после завершения

3. **BS4 скрапер (рекомендуется):**
   - Selenium для загрузки + клик "Load More"
   - BS4 для парсинга HTML
   - CSS классы предпочтительнее XPath
   - Быстрее в 20-30 раз!

4. **Тестирование:**
   - Проверить на первых 10-20 товарах
   - Проверить извлечение цен
   - Убедиться что все товары найдены

---

## 🔐 БЕЗОПАСНОСТЬ

### .gitignore исключает:

```gitignore
# Данные
data/inbox/          # Исходные Excel файлы
data/output/         # Результаты парсинга

# Окружение
venv/                # Виртуальное окружение
.env                 # Переменные окружения

# Логи
logs/                # Логи работы
*.log

# Отладка
debug_*.py
debug_*.html
check_*.py
test_kontakt*.py
test_alta*.py
```

---

## 📞 КОМАНДЫ ДЛЯ РАБОТЫ

### Git
```bash
git status                    # Проверить статус
git add .                     # Добавить все
git commit -m "message"       # Закоммитить
git push                      # Отправить на GitHub
```

### Python
```bash
python run_tests.py                           # Тесты
python scrapers/alta/alta_bs4_scraper.py     # ALTA
python scrapers/kontakt/kontakt_bs4_scraper.py  # KONTAKT
python analyze_prices.py                      # Анализ
python compare_prices.py                      # Сравнение
```

---

## 🎯 ЦЕЛИ ПРОЕКТА

### Основная цель
Автоматизировать сбор и анализ цен конкурентов для принятия ценовых решений.

### Достигнуто
- ✅ 2/3 магазина готовы
- ✅ 102 товара парсятся за 53 секунды
- ✅ Анализ и сравнение с инвентарем
- ✅ Автоматические тесты
- ✅ Полная документация

### Осталось
- ⏳ ELITE скрапер
- ⏳ Объединенный парсер всех магазинов
- ⏳ Автоматизация (планировщик)
- ⏳ Уведомления
- ⏳ Web интерфейс

---

**СТАТУС**: 🟢 Активная разработка  
**ПРОГРЕСС**: 66% (2/3 магазина)  
**ГОТОВНОСТЬ К ПРОДАКШЕНУ**: ALTA ✅ | KONTAKT ✅ | ELITE ⏳

---

## 💬 ЗАМЕТКИ

- Все скраперы сохраняют в один формат (легко объединить)
- Модули независимы (можно запускать отдельно)
- Тесты гарантируют стабильность
- Документация полная и подробная
- Готов к масштабированию

**ПРОЕКТ ГОТОВ К ПРОДОЛЖЕНИЮ!** 🚀

