# 📚 Документация проекта

Добро пожаловать в документацию **Coffee Price Monitoring System**!

## 🗂️ Структура документации

### 📁 [railway/](railway/) - Деплой на Railway.com

Все о размещении проекта в облаке Railway:

- **[QUICK_START_RAILWAY.md](railway/QUICK_START_RAILWAY.md)** ⚡ - Быстрый старт (5 минут)
- **[README_RAILWAY.md](railway/README_RAILWAY.md)** - Полная документация Railway
- **[RAILWAY_DEPLOY.md](railway/RAILWAY_DEPLOY.md)** - Пошаговая инструкция деплоя
- **[RAILWAY_DEPLOYMENT_PLAN.md](railway/RAILWAY_DEPLOYMENT_PLAN.md)** - Детальный план
- **[INVENTORY_UPLOAD_GUIDE.md](railway/INVENTORY_UPLOAD_GUIDE.md)** - Загрузка остатков
- **[RAILWAY_FEATURES.md](railway/RAILWAY_FEATURES.md)** - Новые функции
- **[RAILWAY_FIXES.md](railway/RAILWAY_FIXES.md)** - Исправления ошибок
- **[RAILWAY_SUMMARY.md](railway/RAILWAY_SUMMARY.md)** - Итоговый отчет
- **[DOCKERFILE_FIX.md](railway/DOCKERFILE_FIX.md)** - Исправление Dockerfile

### 📁 [general/](general/) - Общая документация

Руководства по использованию проекта:

- **[PROJECT_OVERVIEW.md](general/PROJECT_OVERVIEW.md)** - Обзор проекта для директора
- **[FULL_CYCLE_GUIDE.md](general/FULL_CYCLE_GUIDE.md)** - Полный цикл работы
- **[EXECUTIVE_REPORT_GUIDE.md](general/EXECUTIVE_REPORT_GUIDE.md)** - Создание отчетов
- **[GIT_WORKFLOW.md](general/GIT_WORKFLOW.md)** - Работа с Git ветками

### 📁 Техническая документация (в корне docs/)

Дополнительные материалы:

- [ALTA_CHECKLIST.md](ALTA_CHECKLIST.md) - Чеклист для ALTA
- [GOOGLE_SHEETS_GUIDE.md](GOOGLE_SHEETS_GUIDE.md) - Экспорт в Google Sheets
- [INVENTORY_INTEGRATION.md](INVENTORY_INTEGRATION.md) - Интеграция с инвентарем
- [MATCHING_IMPROVEMENT_PLAN.md](MATCHING_IMPROVEMENT_PLAN.md) - План улучшения сопоставления
- [PRICE_COMPARISON_PLAN.md](PRICE_COMPARISON_PLAN.md) - План сравнения цен
- [PROMPT.md](PROMPT.md) - Промпты для AI
- [README.md](README.md) - Техническое README

---

## 🎯 Быстрая навигация

### Я хочу:

**🚀 Разместить проект в облаке**
→ [railway/QUICK_START_RAILWAY.md](railway/QUICK_START_RAILWAY.md)

**💻 Запустить локально**
→ [general/FULL_CYCLE_GUIDE.md](general/FULL_CYCLE_GUIDE.md)

**📊 Создать отчет для директора**
→ [general/EXECUTIVE_REPORT_GUIDE.md](general/EXECUTIVE_REPORT_GUIDE.md)

**📤 Загрузить файл остатков**
→ [railway/INVENTORY_UPLOAD_GUIDE.md](railway/INVENTORY_UPLOAD_GUIDE.md)

**🔧 Исправить ошибки Railway**
→ [railway/RAILWAY_FIXES.md](railway/RAILWAY_FIXES.md)

**🌿 Работать с Git ветками**
→ [general/GIT_WORKFLOW.md](general/GIT_WORKFLOW.md)

**📖 Понять проект целиком**
→ [general/PROJECT_OVERVIEW.md](general/PROJECT_OVERVIEW.md)

---

## 📂 Полная структура проекта

```
Coffee Price Monitoring/
├── 📄 README.md                       # Главный README
├── 📄 api_server.py                   # FastAPI веб-сервер
├── 📄 Dockerfile                      # Docker образ для Railway
├── 📄 requirements.txt                # Python зависимости (Windows)
├── 📄 requirements.railway.txt        # Python зависимости (Railway)
│
├── 📁 docs/                           # ВСЯ ДОКУМЕНТАЦИЯ
│   ├── 📄 README.md                   # Этот файл - навигация
│   │
│   ├── 📁 railway/                    # Railway деплой
│   │   ├── QUICK_START_RAILWAY.md     # ⚡ Начать здесь!
│   │   ├── README_RAILWAY.md          # Полная документация
│   │   ├── RAILWAY_DEPLOY.md          # Пошаговая инструкция
│   │   ├── RAILWAY_DEPLOYMENT_PLAN.md # Детальный план
│   │   ├── INVENTORY_UPLOAD_GUIDE.md  # Загрузка остатков
│   │   ├── RAILWAY_FEATURES.md        # Новые функции
│   │   ├── RAILWAY_FIXES.md           # Исправления
│   │   ├── RAILWAY_SUMMARY.md         # Итоговый отчет
│   │   └── DOCKERFILE_FIX.md          # Исправление Dockerfile
│   │
│   ├── 📁 general/                    # Общая документация
│   │   ├── PROJECT_OVERVIEW.md        # Обзор проекта
│   │   ├── FULL_CYCLE_GUIDE.md        # Полный цикл
│   │   ├── EXECUTIVE_REPORT_GUIDE.md  # Отчеты
│   │   └── GIT_WORKFLOW.md            # Git ветки
│   │
│   └── 📁 (остальные технические файлы)
│
├── 📁 scrapers/                       # Парсеры сайтов
│   ├── alta/                          # ALTA.ge
│   ├── kontakt/                       # KONTAKT.ge
│   ├── elite/                         # ELITE (ee.ge)
│   └── dimkava/                       # DIM_KAVA
│
└── 📁 utils/                          # Утилиты
    ├── model_extractor.py             # Извлечение моделей
    ├── excel_writer.py                # Запись в Excel
    └── product_matcher.py             # Сопоставление товаров
```

---

## 🎓 Рекомендуемый порядок чтения

### Для директора:
1. [general/PROJECT_OVERVIEW.md](general/PROJECT_OVERVIEW.md) - Что делает система
2. [railway/QUICK_START_RAILWAY.md](railway/QUICK_START_RAILWAY.md) - Как запустить в облаке
3. [railway/INVENTORY_UPLOAD_GUIDE.md](railway/INVENTORY_UPLOAD_GUIDE.md) - Как загружать остатки

### Для разработчика:
1. [general/PROJECT_OVERVIEW.md](general/PROJECT_OVERVIEW.md) - Обзор проекта
2. [general/FULL_CYCLE_GUIDE.md](general/FULL_CYCLE_GUIDE.md) - Локальный запуск
3. [general/GIT_WORKFLOW.md](general/GIT_WORKFLOW.md) - Работа с Git
4. [railway/RAILWAY_DEPLOYMENT_PLAN.md](railway/RAILWAY_DEPLOYMENT_PLAN.md) - Архитектура Railway
5. [railway/RAILWAY_DEPLOY.md](railway/RAILWAY_DEPLOY.md) - Деплой

### Для DevOps:
1. [railway/RAILWAY_DEPLOYMENT_PLAN.md](railway/RAILWAY_DEPLOYMENT_PLAN.md) - Архитектура
2. [railway/DOCKERFILE_FIX.md](railway/DOCKERFILE_FIX.md) - Исправления Docker
3. [railway/RAILWAY_FIXES.md](railway/RAILWAY_FIXES.md) - Решение проблем
4. [railway/RAILWAY_DEPLOY.md](railway/RAILWAY_DEPLOY.md) - Деплой

---

## 📊 Статистика документации

| Категория | Файлов | Примерно строк |
|-----------|---------|----------------|
| Railway | 9 | ~3500 |
| General | 4 | ~2000 |
| Technical | 7+ | ~1000 |
| **ИТОГО** | **20+** | **~6500** |

---

## 🔄 Обновление документации

Документация регулярно обновляется. Актуальная версия всегда доступна на GitHub:

```
https://github.com/IvanBondarenkoIT/-offee-machines-price-scrapper
```

---

**Создано**: 2025-10-14  
**Последнее обновление**: 2025-10-14  
**Версия**: 2.0 (реорганизация)
