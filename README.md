# Coffee Machines Price Scraper

Проект для парсинга цен на кофеварки DeLonghi с сайтов конкурентов.

## Цель проекта
Собрать актуальные данные о ценах на кофеварки DeLonghi с трех сайтов:
- **ALTA** (https://alta.ge) - 74 товара
- **ELITE** 
- **KONTAKT**

## Структура проекта
```
Coffee machines price scrapper/
├── data/
│   ├── inbox/              # Исходные данные (Excel файлы с XPath)
│   └── output/             # Результаты парсинга
├── scrapers/               # Скрипты для парсинга
│   ├── alta_scraper.py    # Парсер для ALTA
│   ├── elite_scraper.py   # Парсер для ELITE
│   └── kontakt_scraper.py # Парсер для KONTAKT
├── utils/                  # Вспомогательные функции
├── venv/                   # Виртуальное окружение
├── requirements.txt        # Зависимости
├── .gitignore
└── README.md
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

## Использование

### Запуск парсера ALTA
```bash
# Основной способ
python main.py

# Или напрямую
python scrapers/alta_selenium_scraper.py
```

Результат: файлы в папке `data/output/`:
- `alta_delonghi_prices_YYYYMMDD_HHMMSS.xlsx` - Excel файл с данными
- `alta_delonghi_prices_YYYYMMDD_HHMMSS.csv` - CSV файл с данными

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

### ALTA ✅
- [x] Анализ структуры данных
- [ ] Разработка парсера
- [ ] Тестирование
- [ ] Получение 74 товаров

### ELITE ⏳
- [ ] Анализ структуры
- [ ] Разработка парсера
- [ ] Тестирование

### KONTAKT ⏳
- [ ] Анализ структуры
- [ ] Разработка парсера
- [ ] Тестирование

## Требования
- Python 3.8+
- Selenium 4.27+
- Chrome/Firefox браузер
- Стабильное интернет-соединение

