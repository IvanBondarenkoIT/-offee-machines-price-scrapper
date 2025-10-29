# План очистки проекта

## ✅ Что можно безопасно удалить

### 1. Устаревшие Selenium скрип向外ы
- `scrapers/alta/alta_selenium_scraper.py` ❌ - не используется, есть bs4 версия
- `scrapers/kontakt/kontakt_selenium_scraper.py` ❌ - не используется, есть bs4 версия
- Обновить `scrapers/alta/__init__.py` - убрать импорт Selenium версии

### 2. Тестовые файлы (временно или переместить)
- `test_web_app.py` ❓ - тестовый файл, может быть полезен для разработки
- `test_web_imports.py` ❓ - тестовый файл, может быть полезен

**Решение:** Оставить, но добавить в `docs/testing/`

### 3. Альтернативные/дубликаты
- `scrapers/dimkava/dimkava_pure_bs4.py` ❓ - альтернативная версия, проверить используется ли
**Решение:** Проверить, если не используется - удалить

### 4. Устаревшие конфигурационные файлы
- `babel.cfg` ❌ - Flask-Babel удалён, файл не нужен

### 5. Временные лог файлы
- `vega_ge_scraper.log` ❌ - временный лог файл
**Решение:** Удалить, логи должны быть в `logs/`

### 6. Portable Build
- `portable_build/` ❓ - отдельная версия для портативного использования
**Решение:** Оставить, но проверить актуальность документации

### 7. Файлы в корне для перемещения в docs/

**Web App документация:**
- `FLASK_IMPLEMENTATION_GUIDE.md` → `docs/web_app/`
- `FLASK_WEB_APP_COMPLETE.md` → `docs/web_app/`
- `WEB_APP_PROGRESS.md` → `docs/web_app/`
- `WEB_DEPLOYMENT_PLAN.md` → `docs/web_app/`
- `USER_MANAGEMENT_AND_I18N_PLAN.md` → `docs/web_app/`
- `AUTH_SIMPLIFIED.md` → `docs/web_app/`
- `RAILWAY_DEPLOYMENT.md` → `docs/railway/`

**Общая документация:**
- `DEVELOPMENT_COST_ANALYSIS.md` → `docs/general/`
- `PROJECT_FOR_DIRECTOR.md` → `docs/general/` (уже есть копия)

**Новые файлы:**
- `PRODUCT_DESCRIPTION.md` → `docs/general/`
- `PROJECT_CLEANUP_PLAN.md` → `docs/` (этот файл)

## ✅ Что нужно обновить

### 1. scrapers/alta/__init__.py
Убрать импорт `alta_selenium_scraper` если файл удаляется

### 2. .gitignore
Проверить все паттерны, возможно добавить:
- `*.log` (кроме logs/)
- `scrapers/*/__pycache__/`

### 3. README.md
Обновить структуру проекта, убрать упоминания удалённых файлов

## ⚠️ Что НЕ трогать

- `upload_data.example.py` ✅ - пример файла
- `init_db.py` ✅ - может быть полезен
- `generate_railway_keys.py` ✅ - утилита для генерации ключей
- `web_uploader/` ✅あり - необходим для загрузки данных
- `web_app/` ✅ - основной код веб-приложения
- `scrapers/*/` (кроме selenium версий) ✅ - все активные скраперы
- `utils/` ✅ - утилиты
- `config.py` ✅ - конфигурация

