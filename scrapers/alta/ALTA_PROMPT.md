# ALTA.ge Scraper - Полный промпт и документация

## 🎯 Цель
Парсинг цен на кофеварки DeLonghi с сайта ALTA.ge (Грузия)

## 📊 Ключевые данные

### Сайт
- **URL**: https://alta.ge/en/small-domestic-appliances/brand=delonghi;-c7s
- **Язык**: Английский
- **Товаров**: 74 единицы DeLonghi
- **Защита**: CloudFlare/защита от ботов (есть)

### Структура страницы

#### Динамическая подгрузка
- Изначально показывается: **16 товаров**
- Кнопка "Load More": `/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[4]/button`
- Подгружается по: **16 товаров за раз**
- Всего кликов нужно: **4 раза** (16 → 32 → 48 → 64 → 74)

#### HTML структура товара

```html
/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[3]/div[N]/...
```

Где `N` = номер товара от 1 до 74

**Варианты структуры внутри div[N]:**

1. **С 3 блоками** (div/div[3]):
   ```
   div[N]/div/div[3]/a/h2 - название
   div[N]/div/div[3]/div[1]/span[2] - обычная цена
   div[N]/div/div[3]/div[1]/span[1] - цена со скидкой
   ```

2. **С 2 блоками** (div/div[2]):
   ```
   div[N]/div/div[2]/a/h2 - название
   div[N]/div/div[2]/div[1]/span[2] - обычная цена
   div[N]/div/div[2]/div[1]/span[1] - цена со скидкой
   ```

3. **Без скидки**:
   ```
   span - только одна цена (без span[1] и span[2])
   ```

### Данные товара

#### Формат цены
- **Валюта**: GEL (грузинский лари) или ₾
- **Формат в HTML**: `"1499"`, `"549"`, `799₾`
- **С валютой**: может быть с символом ₾ или без
- **Разделители**: могут быть пробелы, запятые

#### Структура скидки
- **Обычная цена**: `span[2]` - зачеркнутая
- **Цена со скидкой**: `span[1]` - крупная, красная
- **Порядок в HTML**: [discount, regular]

#### Примеры товаров
```
1. DeLonghi Dinamica (ECAM350.55.B)
   - Обычная: 2649 GEL
   - Скидка: 1859 GEL
   - Экономия: 790 GEL (30%)

2. DeLonghi Dedica (EC685.R)
   - Обычная: 799 GEL
   - Скидка: 559 GEL
   - Экономия: 240 GEL (30%)

3. DeLonghi Coffee Glasses (DLSC310)
   - Цена: 39 GEL (без скидки)
```

## 🛠️ Реализованные скраперы

### 1. Selenium Scraper (alta_selenium_scraper.py)

**Характеристики:**
- ⏱️ Время: ~13 минут 39 секунд
- 🎯 Точность: 74/74 товара (100%)
- 📊 Скорость: ~0.09 товара/сек

**Технологии:**
- Selenium WebDriver (Chrome)
- XPath для поиска элементов
- Множественные попытки XPath (fallback)
- JavaScript клики для "Load More"

**Преимущества:**
- ✅ Очень надежный
- ✅ Обходит защиту от ботов
- ✅ Множественные fallback XPath
- ✅ Подробное логирование

**Недостатки:**
- ❌ Медленный (implicit_wait на каждый элемент)
- ❌ Много ожиданий (9 сек на товар)
- ❌ Высокая нагрузка на браузер

**Конфигурация:**
```python
SELENIUM_CONFIG = {
    "implicit_wait": 3,  # секунды
    "page_load_timeout": 30,
    "load_more_wait": 1,
    "max_load_more_attempts": 30,
    "headless": False,
}
```

**Запуск:**
```bash
python scrapers/alta/alta_selenium_scraper.py
```

### 2. BeautifulSoup Scraper (alta_bs4_scraper.py) ⚡ РЕКОМЕНДУЕТСЯ

**Характеристики:**
- ⏱️ Время: ~31 секунда
- 🎯 Точность: 74/74 товара (100%)
- 📊 Скорость: ~2.4 товара/сек
- 🚀 **Ускорение: 26.4x быстрее!**

**Технологии:**
- Selenium (только для загрузки страницы)
- BeautifulSoup4 + lxml (для парсинга)
- Поиск по h2 тегам

**Алгоритм:**
1. Selenium загружает страницу
2. Selenium кликает "Load More" 4 раза
3. Получаем HTML (page_source)
4. BS4 парсит HTML локально (БЫСТРО!)
5. Находим все h2 теги (названия товаров)
6. Для каждого h2 ищем родительский контейнер
7. Извлекаем цены из span-ов

**Преимущества:**
- ✅ **Очень быстрый** (26x быстрее Selenium)
- ✅ Простой код
- ✅ Легко поддерживать
- ✅ Меньше нагрузка на систему

**Недостатки:**
- ❌ Требует загрузки всей страницы сразу
- ❌ Менее гибкий при изменении структуры

**Ключевой код:**
```python
# Находим все товары по h2
h2_tags = soup.find_all('h2')

# Для каждого h2 находим родителя с ценами
for h2 in h2_tags:
    parent = h2.parent
    # Поднимаемся на 5 уровней вверх
    for _ in range(5):
        if parent and parent.find_all('span'):
            break
        parent = parent.parent
```

**Запуск:**
```bash
python scrapers/alta/alta_bs4_scraper.py
```

## 📈 Сравнение производительности

| Метрика | Selenium XPath | BeautifulSoup | Улучшение |
|---------|----------------|---------------|-----------|
| Время выполнения | 13 мин 39 сек (819 сек) | 31 секунда | **26.4x** |
| Товаров найдено | 74/74 (100%) | 74/74 (100%) | ✅ |
| Скорость | 0.09 товара/сек | 2.4 товара/сек | **26.6x** |
| Нагрузка на CPU | Высокая | Низкая | ⬇️ |
| Использование RAM | ~500 MB | ~300 MB | ⬇️ |

## 🎯 Извлечение моделей

### Паттерны моделей DeLonghi

```python
# В скобках: DeLonghi Magnifica S (ECAM22.114.B)
pattern1 = r'\(([A-Z0-9]+[.\-][A-Z0-9.]+)\)'

# После "DeLonghi": DeLonghi ECAM22.114.B
pattern2 = r'([A-Z]{2,}[0-9]+[.\-][A-Z0-9.]+[A-Z]?)'

# Простые коды: DLSC310, KG200
pattern3 = r'\b([A-Z]{2,}[0-9]{3,})\b'
```

### Примеры моделей

```
ECAM22.114.B      - Полная модель с вариантом
ECAM350.55.B      - Серия Dinamica
EC685.R           - Dedica (R = red)
EC685.BK          - Dedica (BK = black)
EC685.W           - Dedica (W = white)
ECAM450.65.S      - Eletta Explore
DLSC310           - Аксессуары
KG200             - Кофемолка
```

## 💾 Выходные данные

### Структура Excel/CSV

```python
{
    "index": 1,                          # Номер товара
    "name": "DeLonghi ...",              # Полное название
    "regular_price": 2649.0,             # Обычная цена (float)
    "regular_price_str": "2649",         # Обычная цена (str)
    "discount_price": 1859.0,            # Цена со скидкой (float)
    "discount_price_str": "1859",        # Цена со скидкой (str)
    "final_price": 1859.0,               # Итоговая цена
    "has_discount": True,                # Есть ли скидка
    "scraped_at": "2025-10-07 14:05:35", # Время парсинга
    "url": "https://alta.ge/...",        # URL страницы
}
```

### Файлы результатов

```
data/output/alta_delonghi_prices_20251007_140535.xlsx
data/output/alta_delonghi_prices_20251007_140535.csv
```

## 🔧 Настройка и конфигурация

### config.py

```python
ALTA_CONFIG = {
    "url": "https://alta.ge/en/small-domestic-appliances/brand=delonghi;-c7s",
    "excel_file": INPUT_DIR / "Parsing alta.xlsx",
    "load_more_button_xpath": "/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[4]/button",
    "expected_products": 74,
    "product_container_base": "/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[3]/div[{index}]",
}

SELENIUM_CONFIG = {
    "implicit_wait": 3,
    "page_load_timeout": 30,
    "load_more_wait": 1,
    "max_load_more_attempts": 30,
    "headless": False,
}
```

## 🐛 Известные проблемы и решения

### 1. Защита от ботов
**Проблема**: CloudFlare блокирует автоматические запросы

**Решение**:
```python
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("user-agent=Mozilla/5.0...")
```

### 2. Кнопка "Load More" не находится
**Проблема**: После первого клика кнопка пропадает

**Решение**:
- Прокрутка страницы вниз перед поиском кнопки
- Использование JavaScript для клика
- Проверка `is_displayed()` перед кликом
- Ожидание после клика (2 сек для загрузки)

### 3. Разная структура товаров
**Проблема**: Некоторые товары с div[2], другие с div[3]

**Решение**: Множественные XPath паттерны
```python
name_xpaths = [
    f"...div[{i}]/div/div[3]/a/h2",
    f"...div[{i}]/div/div[2]/a/h2",
]
```

### 4. Unicode ошибки в логах
**Проблема**: `UnicodeEncodeError` на символах ✓ ✗

**Решение**: Заменить на ASCII:
```python
# Вместо: logger.info(f"✓ Product...")
# Использовать: logger.info(f"[OK] Product...")
```

## 📝 Рекомендации использования

### Для регулярного парсинга
✅ **Используйте BS4 скрапер** (`alta_bs4_scraper.py`)
- Быстрый (31 сек)
- Достаточно надежный
- Экономит ресурсы

### Для отладки или изменений структуры
✅ **Используйте Selenium скрапер** (`alta_selenium_scraper.py`)
- Подробные логи
- Множественные fallback
- Легче находить проблемы

### Расписание парсинга
- **Ежедневно**: 1 раз в день (например, 9:00 утра)
- **Еженедельно**: Понедельник утром
- **По требованию**: Перед размещением заказа

### Обработка ошибок
```python
try:
    scraper.run()
except Exception as e:
    # Отправить уведомление
    # Попробовать резервный скрапер
    # Логировать в файл
```

## 🔄 Интеграция с другими модулями

### Анализ цен
```bash
python analyze_prices.py
```
- Статистика цен
- Распределение по диапазонам
- Анализ скидок

### Сравнение с инвентарем
```bash
python compare_prices.py
```
- Сопоставление по моделям
- Сравнение цен
- Отчет о конкурентности

## 📊 Статистика парсинга

### Последний успешный парсинг
- **Дата**: 7 октября 2025
- **Товаров**: 74/74 (100%)
- **Время**: 31 секунда (BS4)
- **Средняя цена**: 1231.84 GEL
- **Диапазон цен**: 29 - 6089 GEL
- **Товаров со скидкой**: ~95%

### Типичные скидки
- **Средняя скидка**: 24.5%
- **Максимальная скидка**: 30%
- **Экономия**: 494 GEL в среднем

## 🚀 Следующие шаги

1. ✅ ALTA скрапер - готов (2 версии)
2. ⏳ ELITE скрапер - аналогично ALTA
3. ⏳ KONTAKT скрапер - аналогично ALTA
4. ⏳ Автоматизация (планировщик)
5. ⏳ Уведомления об изменении цен
6. ⏳ Web интерфейс для просмотра

## 📚 Зависимости

```txt
selenium==4.27.1
webdriver-manager==4.0.2
beautifulsoup4==4.12.3
lxml==5.3.0
openpyxl==3.1.4
pandas==2.1.4
python-dotenv==1.0.1
```

## 🔗 Полезные ссылки

- **GitHub**: https://github.com/IvanBondarenkoIT/-offee-machines-price-scrapper
- **Сайт ALTA**: https://alta.ge
- **Фильтр DeLonghi**: https://alta.ge/en/small-domestic-appliances/brand=delonghi;-c7s

---

**Дата создания**: 7 октября 2025  
**Статус**: ✅ Готов к продакшену  
**Последнее обновление**: 7 октября 2025

