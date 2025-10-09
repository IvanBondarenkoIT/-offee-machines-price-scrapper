# 📊 Google Sheets Export Guide

## 🎯 Цель
Экспорт всех результатов парсинга в Google Sheets для удобного просмотра и совместного использования.

---

## 🚀 Быстрый способ (Manual Upload)

### Шаг 1: Создать объединенный Excel файл

```bash
python export_to_google_sheets.py
```

Результат: `data/output/combined_prices_YYYYMMDD_HHMMSS.xlsx`

### Шаг 2: Загрузить в Google Sheets

1. Открыть https://sheets.google.com
2. Нажать **File → Import**
3. Выбрать **Upload**
4. Загрузить файл `combined_prices_YYYYMMDD_HHMMSS.xlsx`
5. Import location: **Create new spreadsheet**
6. Нажать **Import data**

**Готово!** Таблица создана с 5 вкладками ✅

---

## 📋 Структура таблицы

### Вкладки (Sheets)

#### 1. ALTA (74 товара)
| # | Product Name | Final Price (GEL) | Regular Price | Discount Price | Has Discount |
|---|--------------|-------------------|---------------|----------------|--------------|
| 1 | DeLonghi ... | 1859.0 | 2649.0 | 1859.0 | TRUE |

#### 2. KONTAKT (28 товаров)
| # | Product Name | Final Price (GEL) | Regular Price | Discount Price | Has Discount |
|---|--------------|-------------------|---------------|----------------|--------------|
| 1 | Coffee Machine ... | 849.99 | 849.99 | | FALSE |

#### 3. ELITE (40 товаров)
| # | Product Name | Final Price (GEL) | Regular Price | Discount Price | Has Discount |
|---|--------------|-------------------|---------------|----------------|--------------|
| 1 | DeLonghi ... | 849.99 | 849.99 | | FALSE |

#### 4. DIM_KAVA (41 товар) - НАШ МАГАЗИН
| # | Product Name | Final Price (GEL) | Regular Price | Discount Price | Has Discount |
|---|--------------|-------------------|---------------|----------------|--------------|
| 1 | DeLonghi ... | 3659.0 | 3659.0 | | FALSE |

#### 5. SUMMARY (Статистика)
| Store | Products | Min Price | Max Price | Avg Price | With Discount |
|-------|----------|-----------|-----------|-----------|---------------|
| ALTA | 74 | 29.00 | 6089.00 | 1231.84 | 56 |
| KONTAKT | 28 | 799.99 | 8699.99 | 2832.49 | 0 |
| ELITE | 40 | 256.99 | 6959.99 | 2223.41 | 26 |
| DIM_KAVA | 41 | 35.00 | 3699.00 | 1090.49 | 0 |

---

## 📊 Что в таблице

### Колонки на каждой вкладке магазина:

1. **#** - Порядковый номер
2. **Product Name** - Название товара
3. **Final Price (GEL)** - Итоговая цена (с учетом скидки)
4. **Regular Price** - Обычная цена
5. **Discount Price** - Цена со скидкой (если есть)
6. **Has Discount** - Есть ли скидка (TRUE/FALSE)

### Порядок товаров
✅ Товары в том же порядке, что и на сайтах (по индексу)

---

## 🔧 Автоматический экспорт (Advanced)

### Требования
- Google Cloud Project
- Google Sheets API включен
- Service Account с credentials.json

### Установка зависимостей

```bash
pip install gspread oauth2client
```

### Настройка

1. **Google Cloud Console:**
   - Создать проект
   - Включить Google Sheets API
   - Создать Service Account
   - Скачать credentials.json

2. **Поместить credentials:**
   ```
   credentials/google_sheets_credentials.json
   ```

3. **Создать таблицу:**
   - Открыть Google Sheets
   - Создать новую таблицу
   - Скопировать Spreadsheet ID из URL
   - Share таблицу с email из credentials

4. **Запустить:**
   ```bash
   python export_to_google_sheets_api.py
   ```

---

## 💡 Использование

### Ежедневное обновление

```bash
# 1. Парсим все магазины
python scrapers/alta/alta_bs4_scraper.py
python scrapers/kontakt/kontakt_bs4_scraper.py
python scrapers/elite/elite_bs4_scraper.py
python scrapers/dimkava/dimkava_bs4_scraper.py

# 2. Создаем объединенный файл
python export_to_google_sheets.py

# 3. Загружаем в Google Sheets вручную
# или используем API версию
```

### Автоматизация

**Windows Task Scheduler:**
```powershell
# Создать задачу на ежедневный парсинг и экспорт
$action = New-ScheduledTaskAction -Execute 'python' -Argument 'export_to_google_sheets.py' -WorkingDirectory 'D:\CursorProjects\Coffee machines price scrapper'
$trigger = New-ScheduledTaskTrigger -Daily -At 9am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "DailyPriceExport"
```

---

## 📈 Преимущества Google Sheets

✅ **Доступ из любого места**  
✅ **Совместная работа** (можно делиться)  
✅ **Автообновление** (если использовать API)  
✅ **Встроенные графики и формулы**  
✅ **История изменений**  
✅ **Мобильное приложение**  

---

## 🎯 Кейсы использования

### 1. Анализ конкурентов
- Открыть все 4 вкладки
- Сравнить цены на аналогичные модели
- Выявить где мы дороже/дешевле

### 2. Обновление прайс-листа
- Смотреть вкладку DIM_KAVA
- Сравнивать с конкурентами
- Корректировать цены

### 3. Отчеты для руководства
- Вкладка SUMMARY
- Визуализация через Charts
- Экспорт в PDF

---

## 📝 Примечания

### Формат данных
- Цены: числа с плавающей точкой (799.99)
- Валюта: GEL (лари)
- Скидки: отдельная колонка

### Обновление
- Каждый запуск создает новый файл с timestamp
- Старые файлы сохраняются в data/output/
- Можно отслеживать динамику цен

---

**Дата создания**: 8 октября 2025  
**Статус**: ✅ Готово к использованию

