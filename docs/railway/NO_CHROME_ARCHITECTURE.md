# 🏗️ Архитектура Railway: Без Chrome/Selenium

## 🎯 Решение

**Railway версия**: БЕЗ Chrome/Selenium  
**Локальная версия**: С Chrome/Selenium (опционально)

---

## ✅ Преимущества версии без Chrome

### Память:
```
С Chrome:    ~400-500MB RAM → OOM Kill на Free Tier
БЕЗ Chrome:  ~150-200MB RAM → Отлично работает! ✅
```

### Размер образа:
```
С Chrome:    ~2GB
БЕЗ Chrome:  ~200MB (в 10 раз меньше!)
```

### Время сборки:
```
С Chrome:    ~2 минуты
БЕЗ Chrome:  ~30 секунд
```

### Стоимость Railway:
```
С Chrome:    Нужен Hobby Plan ($5-10/месяц)
БЕЗ Chrome:  Free Tier достаточно! 🎉
```

---

## 🔧 Технические детали

### Парсинг на Railway

Все 4 сайта поддерживают BeautifulSoup парсинг:

| Сайт | Скрипт | Товаров | Время |
|------|--------|---------|-------|
| ALTA | `scrapers/alta/alta_bs4_scraper.py` | 74 | ~31 сек |
| KONTAKT | `scrapers/kontakt/kontakt_bs4_scraper.py` | 28 | ~22 сек |
| ELITE | `scrapers/elite/elite_bs4_scraper.py` | 40 | ~48 сек |
| DIM_KAVA | `scrapers/dimkava/dimkava_bs4_scraper.py` | 41 | ~35 сек |

**Итого**: 183 товара за ~2-3 минуты БЕЗ Selenium! ✅

### Что работает на Railway:

✅ **Веб-интерфейс**:
- Загрузка файла остатков
- Отображение даты: "Остатки актуальны на DD.MM.YYYY"
- Запуск парсинга через кнопку
- Скачивание отчетов

✅ **REST API**:
- POST /scrape/all - Полный цикл парсинга (BeautifulSoup)
- POST /scrape/alta, /kontakt, /elite, /dimkava
- POST /inventory/upload
- GET /reports/latest
- GET /status

✅ **Обработка данных**:
- Сопоставление моделей
- Сравнение цен
- Генерация Excel отчетов
- Генерация Word/PDF отчетов

### Что НЕ работает (и не нужно):

❌ Selenium парсинг (требует Chrome)
- `alta_selenium_scraper.py` - не используется
- `kontakt_selenium_scraper.py` - не используется

**НО**: BeautifulSoup версии есть для всех сайтов! ✅

---

## 📁 Структура файлов

### Dockerfiles:

```
Dockerfile                 ← Текущий (БЕЗ Chrome) для Railway
Dockerfile.full            ← Полный (С Chrome) для локальной разработки
Dockerfile.minimal-test    ← Минимальный тест (только Hello World)
Dockerfile.no-chrome       ← То же что Dockerfile (резервная копия)
```

### Scrapers:

**Для Railway (используются)**:
```
scrapers/alta/alta_bs4_scraper.py         ✅
scrapers/kontakt/kontakt_bs4_scraper.py   ✅
scrapers/elite/elite_bs4_scraper.py       ✅
scrapers/dimkava/dimkava_bs4_scraper.py   ✅
```

**Для локального использования (опционально)**:
```
scrapers/alta/alta_selenium_scraper.py    (не используется на Railway)
scrapers/kontakt/kontakt_selenium_scraper.py
```

---

## 🚀 Как использовать

### На Railway (облако):

```bash
# 1. Открыть веб-интерфейс
https://your-app.railway.app/

# 2. Загрузить файл остатков
[Выбрать файл] → [Загрузить]

# 3. Увидеть дату
"Остатки актуальны на 14.10.2025"

# 4. Запустить парсинг (BeautifulSoup)
[Запустить полный цикл]

# 5. Скачать отчет
[Скачать последний отчет]
```

**Парсинг работает!** BeautifulSoup справляется со всеми сайтами.

### Локально (с Chrome опционально):

```bash
# С полным Dockerfile
docker build -f Dockerfile.full -t coffee-scraper-full .
docker run -p 8000:8000 coffee-scraper-full

# Или просто Python
python run_full_cycle.py
```

Selenium скраперы доступны только локально.

---

## 💰 Стоимость

### Railway Free Tier (БЕЗ Chrome):
```
✅ Memory: 150-200MB (из 512MB доступно)
✅ Storage: 200MB образ
✅ Стоимость: $0 (Free Tier покрывает!)
```

### С Chrome потребовалось бы:
```
❌ Memory: 400-500MB → нужен Hobby Plan
❌ Storage: 2GB образ
❌ Стоимость: ~$5-10/месяц
```

**Экономия**: Бесплатно вместо $5-10/месяц! 🎉

---

## 📊 Производительность

### BeautifulSoup vs Selenium:

| Метод | Скорость | Память | Надежность |
|-------|----------|--------|------------|
| BeautifulSoup | ⚡⚡⚡ Быстро | 💾 Мало | ✅ Высокая |
| Selenium | ⚡ Медленно | 💾💾💾 Много | ✅✅ Очень высокая |

Для парсинга цен **BeautifulSoup достаточно**! ✅

---

## 🎯 Рекомендации

### Для Railway (продакшн):
- ✅ Используйте `Dockerfile` (БЕЗ Chrome)
- ✅ BeautifulSoup парсинг
- ✅ Free Tier достаточно
- ✅ Автоматический запуск по расписанию

### Для локальной разработки:
- ✅ Используйте `Dockerfile.full` (С Chrome) если нужно
- ✅ Или просто `python run_full_cycle.py`
- ✅ Selenium доступен для экспериментов

### Если нужен Selenium на Railway:
- Увеличить Memory до 1GB (Settings → Resources)
- Использовать `Dockerfile.full`
- Стоимость: ~$1/месяц дополнительно

**НО**: В этом нет необходимости! BeautifulSoup работает отлично! ✅

---

## 📝 Итоги

**Архитектура принята**:
- Railway = БЕЗ Chrome (BeautifulSoup only)
- Локально = С Chrome (если нужно)

**Преимущества**:
- 🆓 Бесплатно на Railway
- ⚡ Быстро
- 💾 Мало памяти
- ✅ Работает стабильно

**Компромисс**:
- ❌ Нет Selenium на Railway
- ✅ НО BeautifulSoup справляется со всеми сайтами!

---

**Дата**: 2025-10-14  
**Решение**: Финальное! БЕЗ Chrome на Railway  
**Статус**: Оптимально! 🎉

