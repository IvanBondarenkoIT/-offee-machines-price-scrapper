# ELITE (ee.ge) Scraper

Парсер цен на кофеварки DeLonghi с сайта ELITE (ee.ge) в Грузии

## 🚀 Быстрый старт

```bash
python scrapers/elite/elite_bs4_scraper.py
```

⏱️ Время: ~48 секунд  
📊 Результат: 40 товаров DeLonghi (16+16+8 с 3 страниц)

## 📊 Результаты

- ✅ 40/40 товаров (100%)
- ⚡ 48 секунд (3 страницы)
- 💰 Цены: 256.99 - 6959.99 GEL
- 🏷️ Со скидкой: 26/40 (65%)
- 📁 Сохранение в Excel и CSV

## 📁 Файлы

- `elite_bs4_scraper.py` - Быстрый BS4 парсер с пагинацией
- `ELITE_PROMPT.md` - Полная документация
- `README.md` - Этот файл
- `__init__.py` - Package

## 🔍 Технические детали

### Пагинация
- Страница 1: `https://ee.ge/en/coffee-machine/brand=delonghi;-c201t`
- Страница 2: `https://ee.ge/en/coffee-machine/brand=delonghi;-c201t?page=2`
- Страница 3: `https://ee.ge/en/coffee-machine/brand=delonghi;-c201t?page=3`

### HTML Селекторы
- **Названия**: `<h3>` теги
- **Цены**: `span[1]` (скидка), `span[2]` (обычная)

### Особенности
- URL пагинация (проще чем кнопки)
- 3 страницы (16+16+8 товаров)
- Высокий процент скидок (65%)
- Формат цен: XXX.99

## 📖 Документация

См. [ELITE_PROMPT.md](ELITE_PROMPT.md)

## ✅ Статус

**Готов к продакшену** - 7 октября 2025

