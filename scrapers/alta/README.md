# ALTA.ge Scraper

Парсер цен на кофеварки DeLonghi с сайта ALTA.ge (Грузия)

## 🚀 Быстрый старт

### Рекомендуемый способ (BeautifulSoup - БЫСТРО!)
```bash
python scrapers/alta/alta_bs4_scraper.py
```
⏱️ Время: ~31 секунда  
📊 Результат: 74 товара

### Альтернативный способ (Selenium - НАДЕЖНО)
```bash
python scrapers/alta/alta_selenium_scraper.py
```
⏱️ Время: ~13 минут  
📊 Результат: 74 товара

## 📊 Сравнение версий

| Версия | Время | Скорость | Рекомендация |
|--------|-------|----------|--------------|
| **BS4** | 31 сек | 2.4 товара/сек | ✅ Для регулярного использования |
| **Selenium** | 13.6 мин | 0.09 товара/сек | ⚠️ Для отладки и сложных случаев |

**Ускорение**: BS4 в **26.4 раза быстрее!** ⚡

## 📁 Файлы

- `alta_bs4_scraper.py` - Быстрый парсер (BeautifulSoup)
- `alta_selenium_scraper.py` - Надежный парсер (Selenium)
- `ALTA_PROMPT.md` - Полная документация и все нюансы
- `README.md` - Этот файл

## 📦 Результаты

Сохраняются в `data/output/`:
- `alta_delonghi_prices_YYYYMMDD_HHMMSS.xlsx`
- `alta_delonghi_prices_YYYYMMDD_HHMMSS.csv`

## 🔧 Конфигурация

Настройки в `config.py` (корень проекта):
```python
ALTA_CONFIG = {
    "url": "https://alta.ge/en/small-domestic-appliances/brand=delonghi;-c7s",
    "expected_products": 74,
}
```

## 📖 Подробная документация

См. [ALTA_PROMPT.md](ALTA_PROMPT.md) для:
- Полного описания структуры сайта
- Технических деталей реализации
- Решения известных проблем
- Примеров использования
- Советов по оптимизации

## ✅ Статус

**Готов к продакшену** - 7 октября 2025

