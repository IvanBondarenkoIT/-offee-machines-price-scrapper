# 🧪 Tests - Scraper Health Checks

Быстрые тесты для проверки работоспособности скраперов.

## 🚀 Запуск тестов

### Простой способ
```bash
python run_tests.py
```

### Прямой запуск
```bash
python tests/test_alta_scraper.py
```

## 📊 Что тестируется

### ✅ Unit Tests (быстро, <5 сек)

1. **Model Extraction** - Извлечение моделей из названий
   - Проверяет regex паттерны
   - Тестирует разные форматы названий
   - Примеры: `(ECAM22.114.B)`, `EC685.R`, `DLSC310`

2. **Model Matching** - Сопоставление моделей
   - Точное совпадение
   - Case-insensitive сравнение
   - Fuzzy match (варианты цветов)

3. **Price Cleaning** - Очистка цен
   - Удаление символов валюты
   - Обработка разделителей
   - Преобразование в float

### ✅ Integration Test (медленнее, ~30-60 сек)

**ALTA BS4 Quick Test**
- Загружает первую страницу ALTA
- Проверяет парсинг минимум 10 товаров
- Валидирует структуру данных
- Проверяет типы данных (цены numeric)

## 🎯 Цель тестов

### Не для полного тестирования
Эти тесты НЕ заменяют полное тестирование. Они для:
- ✅ Быстрой проверки "ничего не сломалось"
- ✅ Smoke test перед деплоем
- ✅ Периодическая проверка работоспособности
- ✅ Проверка после изменения кода

### Что НЕ тестируется
- ❌ Полный парсинг всех 74 товаров (слишком долго)
- ❌ Обход защиты от ботов (слишком хрупкое)
- ❌ Точность всех XPath (структура сайта может меняться)

## 📝 Примеры вывода

### Успешный запуск
```
╔══════════════════════════════════════════════════════════════════╗
║                  SCRAPER HEALTH CHECK                            ║
╚══════════════════════════════════════════════════════════════════╝

### UNIT TESTS ###

============================================================
TEST: Model Extraction
============================================================
[OK] DeLonghi Magnifica S (ECAM22.114.B)  -> ECAM22.114.B
[OK] DeLonghi Dinamica (ECAM350.55.B)     -> ECAM350.55.B
[RESULT] 5/5 tests passed (100%)

============================================================
TEST SUMMARY
============================================================
[PASS] Model Extraction
[PASS] Model Matching
[PASS] Price Cleaning
[PASS] ALTA BS4 Quick Test

Total: 4/4 tests passed (100%)

╔══════════════════════════════════════════════════════════════════╗
║                    ✓ ALL TESTS PASSED                           ║
╚══════════════════════════════════════════════════════════════════╝
```

### Провальный тест
```
[FAIL] Assertion failed: Expected at least 10 products, got 0

[WARNING] 1 test(s) failed
```

## ⚙️ Когда запускать

### Регулярно
- 📅 **Ежедневно** - автоматический cron/Task Scheduler
- 🔄 **Перед коммитом** - проверка изменений
- 📦 **Перед деплоем** - финальная проверка

### После изменений
- 🔧 После обновления скраперов
- 📝 После изменения utils
- 🌐 После обновления зависимостей
- ⚙️ После изменения config.py

## 🔧 Настройка автоматического запуска

### Windows Task Scheduler
```powershell
# Создать задачу на запуск каждый день в 8:00
$action = New-ScheduledTaskAction -Execute 'python' -Argument 'D:\CursorProjects\Coffee machines price scrapper\run_tests.py'
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "ScraperHealthCheck"
```

### Linux Cron
```bash
# Добавить в crontab (каждый день в 8:00)
0 8 * * * cd /path/to/project && python run_tests.py >> logs/tests.log 2>&1
```

## 📈 Расширение тестов

### Добавить тест для нового магазина

```python
# tests/test_elite_scraper.py
def test_elite_scraper_quick():
    """Quick test for ELITE scraper"""
    # Аналогично test_alta_scraper_quick
    pass
```

### Добавить в runner

```python
# run_tests.py
from tests.test_elite_scraper import test_elite_scraper_quick

# В run_all_tests()
results.append(("ELITE Quick Test", test_elite_scraper_quick()))
```

## 🐛 Troubleshooting

### "Driver setup failed"
**Проблема**: ChromeDriver не найден или несовместим

**Решение**:
```bash
pip install --upgrade webdriver-manager selenium
```

### "Connection timeout"
**Проблема**: Сайт недоступен или медленный интернет

**Решение**:
- Проверить интернет-соединение
- Увеличить timeout в config.py
- Попробовать позже

### "Expected 10 products, got 0"
**Проблема**: Структура сайта изменилась или защита заблокировала

**Решение**:
- Проверить сайт вручную
- Обновить XPath/селекторы
- Проверить User-Agent

## 📊 Метрики

### Время выполнения
- Unit tests: **< 5 секунд**
- Integration test: **30-60 секунд**
- **Всего**: **~1 минута**

### Coverage
- ✅ Model extraction: 100%
- ✅ Price cleaning: 100%
- ✅ Basic scraping: 100%
- ⚠️ Full scraping: Не тестируется (слишком долго)

---

**Совет**: Запускайте эти тесты часто! Они быстрые и помогут поймать проблемы рано.

