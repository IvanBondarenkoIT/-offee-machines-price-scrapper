# KONTAKT.ge Scraper

Парсер цен на кофеварки DeLonghi с сайта KONTAKT.ge (Грузия)

## 🚀 Быстрый старт

```bash
python scrapers/kontakt/kontakt_bs4_scraper.py
```

⏱️ Время: ~22 секунды  
📊 Результат: 28 товаров DeLonghi

## 📊 Результаты

- ✅ 28/28 товаров (100%)
- ⚡ 22 секунды
- 💰 Цены: 799.99 - 8699.99 GEL
- 📁 Сохранение в Excel и CSV

## 📁 Файлы

- `kontakt_bs4_scraper.py` - Быстрый BS4 парсер
- `kontakt_selenium_scraper.py` - Selenium парсер (не завершен)
- `KONTAKT_PROMPT.md` - Полная документация
- `README.md` - Этот файл

## 📦 Результаты

Сохраняются в `data/output/`:
- `kontakt_bs4_prices_YYYYMMDD_HHMMSS.xlsx`
- `kontakt_bs4_prices_YYYYMMDD_HHMMSS.csv`

## 🔍 Технические детали

### CSS Селекторы
- **Названия**: `.prodItem__title`
- **Цены**: `.prodItem__prices.prodItem__prices--active`
- **Внутри**: `strong > i` или `strong > b`

### Особенности
- Простая структура (CSS классы)
- Быстрый парсинг
- Меньше кликов "Load More" чем ALTA

## 📖 Документация

См. [KONTAKT_PROMPT.md](KONTAKT_PROMPT.md)

## ✅ Статус

**Готов к продакшену** - 7 октября 2025

