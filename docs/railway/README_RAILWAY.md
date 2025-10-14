# Coffee Price Monitoring - Railway Deployment

## 🚀 Быстрый старт на Railway

Этот проект готов к развертыванию на [Railway.com](https://railway.com) с полным функционалом:

- ✅ **REST API** для управления парсингом
- ✅ **Веб-интерфейс** для загрузки остатков
- ✅ **Headless Chrome** для парсинга
- ✅ **Постоянное хранилище** для файлов (Railway Volumes)
- ✅ **Автоматическое отслеживание** даты актуальности остатков

---

## 📋 Что было изменено для Railway

### 1. Добавлен FastAPI веб-сервер (`api_server.py`)

**Основные возможности**:
- Веб-интерфейс на главной странице (`/`)
- REST API для запуска парсинга
- Загрузка файла остатков через браузер
- Скачивание отчетов
- Отображение статуса парсинга в реальном времени
- **Отображение даты актуальности остатков**: "Остатки актуальны на DD.MM.YYYY"

### 2. Настроен Selenium для headless режима

**Изменения в `config.py`**:
```python
SELENIUM_CONFIG = {
    "headless": True,  # Включен headless режим для Railway
    # ...
}
```

### 3. Создан Dockerfile с Chrome

**Установлены компоненты**:
- Python 3.11
- Google Chrome (stable)
- ChromeDriver
- Все зависимости проекта

### 4. Убрана зависимость от Windows (`pywin32`)

**Замена**:
- `pywin32` → `weasyprint` (кроссплатформенная конвертация в PDF)

### 5. Добавлена система управления остатками

**Новые endpoints**:
- `POST /inventory/upload` - Загрузка файла остатков
- `GET /inventory/info` - Информация об остатках + дата актуальности
- `GET /inventory/download` - Скачать файл остатков

**Метаданные**:
- Дата загрузки сохраняется в `inventory_metadata.json`
- Формат отображения: `DD.MM.YYYY`
- Автоматический подсчет товаров

---

## 🎯 Архитектура на Railway

```
┌─────────────────────────────────────────────────────┐
│         Railway Web Service (Port 8000)              │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │  FastAPI Server                                │ │
│  │  - Веб-интерфейс (/)                          │ │
│  │  - API endpoints (/scrape/*, /inventory/*)    │ │
│  │  - Отчеты (/reports/*)                        │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │  Background Workers                            │ │
│  │  - Selenium (headless Chrome)                  │ │
│  │  - BeautifulSoup parsers                       │ │
│  │  - Data processors                             │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │  Railway Volume: /app/data                     │ │
│  │  ├── inbox/                                    │ │
│  │  │   ├── остатки.xlsx                         │ │
│  │  │   └── inventory_metadata.json              │ │
│  │  ├── output/                                   │ │
│  │  │   ├── price_comparison_*.xlsx              │ │
│  │  │   └── executive_report_*.pdf               │ │
│  │  └── logs/                                     │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## 📦 Деплой на Railway

### Метод 1: Через GitHub (рекомендуется)

1. **Загрузите код в GitHub**:
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

2. **Создайте проект на Railway**:
   - Перейдите на [railway.com](https://railway.com)
   - New Project → Deploy from GitHub repo
   - Выберите ваш репозиторий
   - Railway автоматически обнаружит `Dockerfile`

3. **Настройте переменные окружения**:
   - Railway Dashboard → Variables
   - Добавьте:
     ```
     PORT=8000
     PYTHON_ENV=production
     HEADLESS=true
     LOG_LEVEL=INFO
     ```

4. **Создайте Volume для хранения файлов**:
   - Railway Dashboard → Settings → Volumes
   - New Volume
   - Mount Path: `/app/data`
   - Size: 1 GB

5. **Сгенерируйте домен**:
   - Settings → Networking → Generate Domain
   - Получите URL вида: `your-app.railway.app`

### Метод 2: Через Railway CLI

```bash
# Установить CLI
npm i -g @railway/cli

# Войти в аккаунт
railway login

# Инициализировать проект
railway init

# Деплой
railway up

# Открыть приложение
railway open
```

---

## 🌐 Использование веб-интерфейса

После деплоя откройте ваш Railway URL в браузере:

```
https://your-app.railway.app/
```

### Главная страница показывает:

1. **Статус остатков**:
   - ✅ Если загружен: "Остатки актуальны на 14.10.2025"
   - ⚠️ Если не загружен: "Файл с остатками не загружен"

2. **Форма загрузки файла**:
   - Выберите файл `.xls` или `.xlsx`
   - Нажмите "Загрузить"
   - Дата обновится автоматически

3. **Кнопка запуска парсинга**:
   - "Запустить полный цикл"
   - Показывает прогресс в реальном времени
   - 183 товара за ~2-3 минуты

4. **Скачивание отчетов**:
   - Последний отчет Excel
   - Отчет для руководства (Word/PDF)

---

## 🔌 API Endpoints

### Управление остатками

#### Загрузить файл остатков
```bash
POST /inventory/upload
```

**curl пример**:
```bash
curl -X POST https://your-app.railway.app/inventory/upload \
  -F "file=@остатки.xlsx"
```

**Ответ**:
```json
{
  "status": "success",
  "message": "Файл успешно загружен. Найдено товаров: 76",
  "filename": "остатки.xlsx",
  "uploaded_at": "2025-10-14T09:30:00",
  "uploaded_at_formatted": "14.10.2025"
}
```

#### Получить информацию об остатках
```bash
GET /inventory/info
```

**curl пример**:
```bash
curl https://your-app.railway.app/inventory/info
```

**Ответ**:
```json
{
  "has_file": true,
  "filename": "остатки.xlsx",
  "uploaded_at": "2025-10-14T09:30:00",
  "uploaded_at_formatted": "14.10.2025",
  "size_bytes": 45678,
  "products_count": 76,
  "message": "Остатки актуальны на 14.10.2025"
}
```

### Запуск парсинга

#### Полный цикл (все 4 сайта)
```bash
POST /scrape/all
```

**curl пример**:
```bash
curl -X POST https://your-app.railway.app/scrape/all
```

#### Отдельные сайты
```bash
POST /scrape/alta      # ALTA.ge (74 товара)
POST /scrape/kontakt   # KONTAKT.ge (28 товаров)
POST /scrape/elite     # ELITE (40 товаров)
POST /scrape/dimkava   # DIM_KAVA (41 товар)
```

### Отчеты

#### Скачать последний отчет
```bash
GET /reports/latest
```

**curl пример**:
```bash
curl https://your-app.railway.app/reports/latest -o report.xlsx
```

#### Список всех отчетов
```bash
GET /reports/list
```

### Статус

#### Проверить статус парсинга
```bash
GET /status
```

#### Health check
```bash
GET /health
```

**Ответ** (включает информацию об остатках):
```json
{
  "status": "healthy",
  "timestamp": "2025-10-14T09:30:00",
  "service": "coffee-price-monitor",
  "inventory": {
    "loaded": true,
    "date": "14.10.2025"
  }
}
```

---

## 🤖 Автоматизация

### Настройка Cron Job для ежедневного запуска

#### Вариант 1: Railway Cron (встроенный)

1. Создать новый сервис в Railway
2. Выбрать "Cron Job"
3. Расписание: `0 9 * * *` (каждый день в 9:00)
4. Команда: `python run_full_cycle.py`

#### Вариант 2: Внешний Cron (cron-job.org)

1. Зарегистрироваться на [cron-job.org](https://cron-job.org)
2. Создать Cron Job:
   - URL: `https://your-app.railway.app/scrape/all`
   - Method: POST
   - Schedule: Daily at 9:00 AM

#### Вариант 3: GitHub Actions

Создать `.github/workflows/daily-scrape.yml`:

```yaml
name: Daily Price Scraping

on:
  schedule:
    - cron: '0 9 * * *'  # 9:00 UTC
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - name: Update inventory
        run: |
          curl -X POST ${{ secrets.RAILWAY_URL }}/inventory/upload \
            -F "file=@остатки.xlsx"
      
      - name: Run scraping
        run: |
          curl -X POST ${{ secrets.RAILWAY_URL }}/scrape/all
```

---

## 💾 Управление файлами остатков

### Автоматическое обновление остатков

Создайте скрипт `update_inventory.py`:

```python
import requests
from pathlib import Path

def upload_inventory(file_path, api_url):
    url = f"{api_url}/inventory/upload"
    files = {"file": open(file_path, "rb")}
    
    response = requests.post(url, files=files)
    data = response.json()
    
    print(f"✅ {data['message']}")
    print(f"📅 Остатки актуальны на: {data['uploaded_at_formatted']}")

if __name__ == "__main__":
    API_URL = "https://your-app.railway.app"
    upload_inventory("остатки.xlsx", API_URL)
```

**Запуск**:
```bash
python update_inventory.py
```

---

## 📊 Типичный рабочий процесс

### Ежедневный автоматический запуск

**Сценарий**:
1. **8:00** - Обновление файла остатков (через скрипт или вручную)
2. **9:00** - Автоматический запуск парсинга (Cron Job)
3. **9:05** - Получение отчетов на email
4. **9:10** - Просмотр отчета директором

### Ручной запуск

**Через веб-интерфейс**:
1. Открыть `https://your-app.railway.app/`
2. Загрузить актуальный файл остатков
3. Проверить дату: "Остатки актуальны на 14.10.2025"
4. Нажать "Запустить полный цикл"
5. Дождаться завершения (~2-3 минуты)
6. Скачать отчет

**Через API**:
```bash
# 1. Загрузить остатки
curl -X POST https://your-app.railway.app/inventory/upload \
  -F "file=@остатки.xlsx"

# 2. Запустить парсинг
curl -X POST https://your-app.railway.app/scrape/all

# 3. Проверить статус
curl https://your-app.railway.app/status

# 4. Скачать отчет
curl https://your-app.railway.app/reports/latest -o report.xlsx
```

---

## 🔧 Локальное тестирование

### Запуск с Docker

```bash
# Собрать образ
docker build -t coffee-scraper .

# Запустить
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e HEADLESS=true \
  coffee-scraper

# Открыть в браузере
open http://localhost:8000
```

### Запуск без Docker

```bash
# Установить зависимости
pip install -r requirements.railway.txt

# Запустить сервер
uvicorn api_server:app --reload

# Открыть в браузере
open http://localhost:8000
```

---

## 📈 Мониторинг

### Проверка здоровья приложения

```bash
curl https://your-app.railway.app/health
```

### Просмотр логов

**Railway Dashboard**:
- Deployments → Logs

**Railway CLI**:
```bash
railway logs --tail
```

### Метрики

Railway автоматически отслеживает:
- CPU и память
- Network traffic
- Deployment status
- Uptime

---

## 💰 Стоимость

| Компонент | Free Tier | Платный план |
|-----------|-----------|--------------|
| Web Service (24/7) | $5 credit | ~$5/месяц |
| Volume (1 GB) | Included | ~$0.25/месяц |
| Egress | Included | ~$0.50/месяц |
| **ИТОГО** | **$5 (бесплатно!)** | **~$6/месяц** |

**Вывод**: Free tier Railway полностью покрывает потребности проекта!

---

## ✅ Чеклист деплоя

- [ ] Код загружен в GitHub
- [ ] Проект создан на Railway
- [ ] Dockerfile обнаружен автоматически
- [ ] Переменные окружения настроены
- [ ] Volume создан (`/app/data`)
- [ ] Домен сгенерирован
- [ ] Приложение успешно запущено
- [ ] Веб-интерфейс открывается
- [ ] Файл остатков загружен
- [ ] Дата актуальности отображается
- [ ] Парсинг работает
- [ ] Отчеты генерируются
- [ ] Cron Job настроен (опционально)

---

## 📚 Дополнительная документация

- **[RAILWAY_DEPLOYMENT_PLAN.md](RAILWAY_DEPLOYMENT_PLAN.md)** - Детальный план деплоя
- **[RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md)** - Пошаговая инструкция
- **[INVENTORY_UPLOAD_GUIDE.md](INVENTORY_UPLOAD_GUIDE.md)** - Руководство по загрузке остатков
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Обзор проекта
- **[FULL_CYCLE_GUIDE.md](FULL_CYCLE_GUIDE.md)** - Полный цикл работы

---

## 🎉 Готово к использованию!

После деплоя ваше приложение доступно 24/7 на Railway:

**Главная страница**: https://your-app.railway.app/

**Swagger API Docs**: https://your-app.railway.app/docs

**Загрузка остатков и просмотр даты актуальности**: https://your-app.railway.app/

Наслаждайтесь автоматическим мониторингом цен! ☕🚀

