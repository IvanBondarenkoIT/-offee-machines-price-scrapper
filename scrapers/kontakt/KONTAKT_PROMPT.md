# KONTAKT.ge Scraper - Документация

## 🎯 Цель
Парсинг цен на кофеварки DeLonghi с сайта KONTAKT.ge (Грузия)

## 📊 Ключевые данные

### Сайт
- **URL**: https://kontakt.ge/en/samzareulos-teknika/samzareulos-tsvrili-teknika/qavis-aparatebi?kh_mtsarmoebeli=DeLonghi
- **Язык**: Английский
- **Товаров**: 28 единиц DeLonghi
- **Защита**: Есть базовая защита от ботов

### Структура страницы

#### HTML структура
- **Товары**: Используют класс `prodItem__title` для названий
- **Цены**: Класс `prodItem__prices prodItem__prices--active`
- **Внутри цен**: `<strong><i>` или `<strong><b>`

#### Динамическая подгрузка
- Изначально: ~20 товаров
- Кнопка "Load More": `/html/body/div[1]/main/div[4]/div/div[5]/div/div[2]/button`
- После клика: 28 товаров (все)

### Ключевые CSS классы

```css
.prodItem__title {
    /* Название товара */
}

.prodItem__prices.prodItem__prices--active {
    /* Контейнер с ценами */
}

.prodItem__prices strong i {
    /* Основная цена */
}

.prodItem__prices strong b {
    /* Альтернативный формат цены */
}
```

## 🛠️ Реализованный скрапер

### BeautifulSoup Scraper (kontakt_bs4_scraper.py) ⚡

**Характеристики:**
- ⏱️ Время: ~22 секунды
- 🎯 Точность: 28/28 товаров (100%)
- 📊 Скорость: ~1.3 товара/сек

**Алгоритм:**
1. Selenium загружает страницу
2. Кликает "Load More" (если есть)
3. Получает HTML через `page_source`
4. BS4 находит все элементы с классом `prodItem__title`
5. Для каждого title ищет родительский контейнер с `prodItem__prices`
6. Извлекает цену из `strong > i` или `strong > b`

**Ключевой код:**
```python
# Находим все названия
product_titles = soup.find_all(class_='prodItem__title')

# Для каждого находим цену
for title_elem in product_titles:
    name = title_elem.get_text(strip=True)
    
    # Ищем цену в родительском контейнере
    parent = title_elem.parent
    for _ in range(10):
        price_elem = parent.find(class_='prodItem__prices')
        if price_elem:
            break
        parent = parent.parent
    
    # Извлекаем из strong > i или strong > b
    strong = price_elem.find('strong')
    price = strong.find('i') or strong.find('b')
```

**Преимущества:**
- ✅ Очень быстрый (22 сек)
- ✅ Простая структура (классы, не XPath)
- ✅ Надежный (не зависит от позиции элемента)
- ✅ Все 28 товаров

**Запуск:**
```bash
python scrapers/kontakt/kontakt_bs4_scraper.py
```

## 📈 Производительность

| Метрика | Значение |
|---------|----------|
| Время выполнения | 22 секунды |
| Товаров найдено | 28/28 (100%) |
| Скорость | ~1.3 товара/сек |
| Размер HTML | ~1.1 MB |

## 📦 Выходные данные

### Структура
```python
{
    "index": 1,
    "name": "Coffee Machine DeLonghi EC890.GR",
    "regular_price": 849.99,
    "regular_price_str": "849.99",
    "discount_price": None,
    "discount_price_str": None,
    "final_price": 849.99,
    "has_discount": False,
    "scraped_at": "2025-10-07 14:53:25",
    "url": "https://kontakt.ge/...",
    "store": "KONTAKT",
}
```

### Файлы
```
data/output/kontakt_bs4_prices_20251007_145325.xlsx
data/output/kontakt_bs4_prices_20251007_145325.csv
```

## 🔧 Конфигурация

### config.py
```python
KONTAKT_CONFIG = {
    "url": "https://kontakt.ge/en/samzareulos-teknika/samzareulos-tsvrili-teknika/qavis-aparatebi?kh_mtsarmoebeli=DeLonghi",
    "expected_products": 28,
    "load_more_button_xpath": "/html/body/div[1]/main/div[4]/div/div[5]/div/div[2]/button",
}
```

## 🎯 Извлечение моделей

### Примеры моделей KONTAKT
```
Coffee Machine DeLonghi EC890.GR     -> EC890.GR
Coffee Machine DeLonghi EC9455.M     -> EC9455.M
Coffee machine Delonghi EXAM440.55.W -> EXAM440.55.W
Coffee Machine DeLonghi ECAM21.117.W -> ECAM21.117.W
```

Используется тот же `product_matcher.py` что и для ALTA.

## 📊 Статистика

### Последний парсинг
- **Дата**: 7 октября 2025
- **Товаров**: 28/28 (100%)
- **Время**: 22 секунды
- **Средняя цена**: ~2500 GEL
- **Диапазон**: 799.99 - 8699.99 GEL

### Особенности KONTAKT
- Все товары загружаются за 1-2 клика "Load More"
- Названия чище чем у ALTA (без лишней информации)
- Цены в формате XXX.99 (с копейками)
- Скидок меньше чем у ALTA

## 🔄 Сравнение с ALTA

| Параметр | ALTA | KONTAKT |
|----------|------|---------|
| Товаров | 74 | 28 |
| Время BS4 | 31 сек | 22 сек |
| Скорость | 2.4/сек | 1.3/сек |
| Структура | XPath (сложная) | CSS классы (простая) |
| Скидки | ~95% | Меньше |

## 🐛 Известные проблемы

### 1. Не все товары сразу видны
**Решение**: Кнопка "Load More"

### 2. Названия могут начинаться с "Coffee Machine" или "Coffee machine"
**Решение**: Нормализация при сопоставлении моделей

### 3. Цены в формате XXX.99
**Решение**: clean_price() обрабатывает автоматически

## 📝 Рекомендации

### Для регулярного использования
✅ **Используйте BS4 скрапер** (контакт_bs4_scraper.py)
- Быстро (22 сек)
- Надежно (28/28)
- Простой код

### Частота парсинга
- Ежедневно: достаточно
- Несколько раз в день: если нужен мониторинг цен

---

**Дата создания**: 7 октября 2025  
**Статус**: ✅ Готов к продакшену  
**Время разработки**: ~30 минут

