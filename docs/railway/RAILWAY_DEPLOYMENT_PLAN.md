# План размещения проекта на Railway.com

## 📊 Анализ текущего проекта

### Текущая архитектура
- **Тип**: CLI-приложение для парсинга цен
- **Запуск**: Локальные скрипты Python
- **Результат**: Файлы Excel/Word/PDF в локальной папке `data/output/`
- **Браузеры**: Selenium с Chrome/Firefox (с GUI)

### Основные компоненты
1. **Парсеры** (4 сайта):
   - ALTA.ge (74 товара, 31 сек)
   - KONTAKT.ge (28 товаров, 22 сек)
   - ELITE (ee.ge) (40 товаров, 48 сек)
   - DIM_KAVA (dimkava.ge) (41 товар, 35 сек)

2. **Обработка данных**:
   - Сопоставление моделей (model_extractor.py)
   - Сравнение цен (build_price_comparison.py)
   - Генерация отчетов (generate_executive_report.py)

3. **Вывод результатов**:
   - Excel файлы (openpyxl)
   - Word отчеты (python-docx)
   - PDF конвертация (pywin32 - только Windows!)

### ⚠️ Проблемы для Railway

| Проблема | Текущее состояние | Требуется изменение |
|----------|-------------------|---------------------|
| Нет веб-сервера | CLI скрипты | ✅ Добавить Flask/FastAPI |
| Selenium с GUI | `headless: False` | ✅ Переключить на headless |
| Файловая система | Локальные файлы | ✅ Railway Volumes или S3 |
| pywin32 | Windows-only | ✅ Кроссплатформенное решение |
| Chrome браузер | Не установлен | ✅ Dockerfile с Chrome |

---

## 🎯 Рекомендуемая архитектура для Railway

### Вариант 1: REST API + Cron Job (РЕКОМЕНДУЕТСЯ)

```
┌─────────────────────────────────────────┐
│         Railway Web Service              │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  FastAPI Web Server (port 8000)    │ │
│  │  ┌──────────────────────────────┐  │ │
│  │  │ GET  /                       │  │ │
│  │  │ POST /scrape/alta           │  │ │
│  │  │ POST /scrape/kontakt        │  │ │
│  │  │ POST /scrape/elite          │  │ │
│  │  │ POST /scrape/dimkava        │  │ │
│  │  │ POST /scrape/all            │  │ │
│  │  │ GET  /reports/latest        │  │ │
│  │  │ GET  /status                │  │ │
│  │  └──────────────────────────────┘  │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Background Workers                │ │
│  │  - Selenium (headless Chrome)      │ │
│  │  - BeautifulSoup parsers           │ │
│  │  - Data processors                 │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Railway Volume (/app/data)        │ │
│  │  - output/                         │ │
│  │  - inbox/                          │ │
│  │  - logs/                           │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**Преимущества**:
- ✅ API для запуска парсинга по требованию
- ✅ Веб-интерфейс для просмотра результатов
- ✅ Возможность интеграции с другими системами
- ✅ Логи и мониторинг через Railway
- ✅ Cron для автоматического запуска (например, каждый день в 9:00)

### Вариант 2: Только Cron Job

```
┌─────────────────────────────────────────┐
│         Railway Cron Job                 │
│                                          │
│  Расписание: 0 9 * * * (каждый день)   │
│                                          │
│  run_full_cycle.py                      │
│     ↓                                    │
│  Результаты → Email / Google Drive      │
└─────────────────────────────────────────┘
```

**Преимущества**:
- ✅ Простая настройка
- ✅ Не требует постоянного сервера
- ❌ Нет возможности запустить вручную
- ❌ Сложнее отладка

---

## 🛠️ Детальный план реализации (Вариант 1)

### Шаг 1: Создать FastAPI веб-сервер

**Файл**: `api_server.py`

```python
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import subprocess
from pathlib import Path
from datetime import datetime

app = FastAPI(title="Coffee Price Monitoring API")

@app.get("/")
async def root():
    return {
        "service": "Coffee Price Monitoring",
        "version": "1.0.0",
        "endpoints": [
            "/scrape/all",
            "/scrape/alta",
            "/scrape/kontakt", 
            "/scrape/elite",
            "/scrape/dimkava",
            "/reports/latest",
            "/status"
        ]
    }

@app.post("/scrape/all")
async def scrape_all(background_tasks: BackgroundTasks):
    """Запустить полный цикл парсинга всех сайтов"""
    background_tasks.add_task(run_full_cycle)
    return {"status": "started", "message": "Full cycle started in background"}

@app.get("/reports/latest")
async def get_latest_report():
    """Скачать последний отчет"""
    output_dir = Path("data/output")
    files = list(output_dir.glob("price_comparison_*.xlsx"))
    if files:
        latest = max(files, key=lambda x: x.stat().st_mtime)
        return FileResponse(latest)
    return {"error": "No reports found"}

@app.get("/status")
async def status():
    """Статус последнего парсинга"""
    # Проверить последние файлы
    return {
        "last_run": "2025-10-14 09:00:00",
        "status": "success",
        "products_scraped": 183
    }
```

### Шаг 2: Настроить Selenium для headless режима

**Изменить**: `config.py`

```python
# Selenium Configuration для Railway
SELENIUM_CONFIG = {
    "implicit_wait": 3,
    "page_load_timeout": 30,
    "load_more_wait": 1,
    "max_load_more_attempts": 30,
    "headless": True,  # ✅ ОБЯЗАТЕЛЬНО для Railway
    "disable_gpu": True,
    "no_sandbox": True,  # Для Docker
    "disable_dev_shm": True,  # Для Docker
}
```

### Шаг 3: Создать Dockerfile

**Файл**: `Dockerfile`

```dockerfile
FROM python:3.11-slim

# Установить Chrome и ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Установить ChromeDriver
RUN CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# Рабочая директория
WORKDIR /app

# Скопировать requirements
COPY requirements.txt .

# Установить зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Скопировать код
COPY . .

# Создать директории
RUN mkdir -p data/output data/inbox logs

# Запустить API сервер
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Шаг 4: Обновить requirements.txt

```txt
# Текущие зависимости
beautifulsoup4==4.12.3
lxml==5.3.0
selenium==4.27.1
webdriver-manager==4.0.2
openpyxl==3.1.4
pandas==2.1.4
python-dotenv==1.0.1
python-docx==1.2.0

# УБРАТЬ pywin32 (Windows-only)
# pywin32>=305

# Добавить для Railway
fastapi==0.109.0
uvicorn[standard]==0.27.0
aiofiles==23.2.1

# Кроссплатформенная альтернатива для PDF
# Вариант 1: использовать LibreOffice
# Вариант 2: использовать weasyprint
weasyprint==61.0

# Для Google Drive интеграции (опционально)
google-api-python-client==2.116.0
google-auth-httplib2==0.2.0
google-auth-oauthlib==1.2.0
```

### Шаг 5: Создать railway.json

**Файл**: `railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "numReplicas": 1,
    "sleepApplication": false,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Шаг 6: Настроить переменные окружения в Railway

В Railway Dashboard → Variables:

```env
PORT=8000
PYTHON_ENV=production
HEADLESS=true
LOG_LEVEL=INFO
```

### Шаг 7: Настроить Railway Volumes (постоянное хранилище)

В Railway Dashboard → Settings → Volumes:

- **Mount Path**: `/app/data`
- **Size**: 1 GB (достаточно для отчетов)

---

## 🚀 Альтернативы для хранения файлов

### Вариант A: Railway Volumes (ПРОСТОЙ)
- ✅ Встроенное решение
- ✅ Автоматические бэкапы
- ❌ Ограниченный размер
- ❌ Привязка к Railway

### Вариант B: AWS S3 / Google Cloud Storage (МАСШТАБИРУЕМЫЙ)
```python
import boto3

s3 = boto3.client('s3')
s3.upload_file('data/output/report.xlsx', 'my-bucket', 'reports/report.xlsx')
```

### Вариант C: Google Drive API (УДОБНЫЙ)
```python
from googleapiclient.discovery import build

service = build('drive', 'v3', credentials=creds)
file_metadata = {'name': 'price_report.xlsx'}
media = MediaFileUpload('data/output/report.xlsx')
file = service.files().create(body=file_metadata, media_body=media).execute()
```

---

## 📅 Настройка Cron Jobs

### В Railway Dashboard

1. Создать новый сервис типа "Cron Job"
2. Расписание: `0 9 * * *` (каждый день в 9:00)
3. Команда: `python run_full_cycle.py`

### Или через API (внешний cron)

Использовать внешний сервис (например, cron-job.org):
```
POST https://your-railway-app.railway.app/scrape/all
```

---

## ⚡ Быстрый старт

### Локальное тестирование Docker

```bash
# Собрать образ
docker build -t coffee-scraper .

# Запустить контейнер
docker run -p 8000:8000 -v $(pwd)/data:/app/data coffee-scraper

# Проверить API
curl http://localhost:8000/
curl -X POST http://localhost:8000/scrape/all
```

### Деплой на Railway

```bash
# 1. Установить Railway CLI
npm i -g @railway/cli

# 2. Войти в аккаунт
railway login

# 3. Инициализировать проект
railway init

# 4. Деплой
railway up

# 5. Открыть приложение
railway open
```

---

## 🔍 Мониторинг и отладка

### Логи в Railway

```bash
railway logs
```

### Проверка статуса

```bash
curl https://your-app.railway.app/status
```

### Скачать последний отчет

```bash
curl https://your-app.railway.app/reports/latest -o report.xlsx
```

---

## 💰 Оценка стоимости Railway

| Компонент | Использование | Стоимость |
|-----------|---------------|-----------|
| Web Service | 1 instance, 512MB RAM | ~$5/месяц |
| Volume | 1 GB storage | ~$0.25/месяц |
| Egress | ~100 MB/день (отчеты) | ~$0.5/месяц |
| **ИТОГО** | | **~$5-6/месяц** |

**Free tier**: $5 credit/месяц (достаточно для тестирования!)

---

## 📋 Чеклист для деплоя

### Подготовка кода
- [ ] Создать `api_server.py`
- [ ] Изменить `config.py` (headless: True)
- [ ] Обновить `requirements.txt` (убрать pywin32)
- [ ] Создать `Dockerfile`
- [ ] Создать `railway.json`
- [ ] Создать `.dockerignore`

### Railway настройка
- [ ] Создать проект на railway.com
- [ ] Подключить GitHub репозиторий
- [ ] Настроить переменные окружения
- [ ] Создать Railway Volume
- [ ] Настроить домен (опционально)

### Тестирование
- [ ] Локальный тест Docker
- [ ] Деплой на Railway
- [ ] Проверить API endpoints
- [ ] Проверить парсинг всех сайтов
- [ ] Проверить генерацию отчетов
- [ ] Настроить Cron Job

### Документация
- [ ] Обновить README.md
- [ ] Добавить Railway badge
- [ ] Документировать API endpoints

---

## 🎯 Рекомендации

### Первый этап (Минимально работающий продукт)
1. ✅ Создать простой FastAPI сервер
2. ✅ Настроить Dockerfile с headless Chrome
3. ✅ Деплой на Railway
4. ✅ Проверить работу парсинга

### Второй этап (Автоматизация)
1. ⭐ Настроить Cron Job для ежедневного запуска
2. ⭐ Добавить email уведомления
3. ⭐ Интеграция с Google Drive

### Третий этап (Улучшения)
1. 🚀 Веб-интерфейс для просмотра отчетов
2. 🚀 Dashboard с графиками цен
3. 🚀 Telegram бот для уведомлений

---

## ❓ FAQ

### Q: Будет ли работать Selenium в Railway?
**A**: Да, но нужен headless режим и Dockerfile с Chrome.

### Q: Где хранить результаты парсинга?
**A**: Railway Volumes (простой вариант) или S3/Google Drive (масштабируемый).

### Q: Как заменить pywin32 для PDF?
**A**: Использовать `weasyprint` или `LibreOffice` (кроссплатформенные).

### Q: Сколько времени займет парсинг?
**A**: ~2-3 минуты для всех 4 сайтов (183 товара).

### Q: Можно ли запускать парсинг вручную?
**A**: Да, через API endpoint `POST /scrape/all`.

---

## 📞 Следующие шаги

Хотите, чтобы я:
1. ✅ **Создал все необходимые файлы** (api_server.py, Dockerfile, railway.json)?
2. ✅ **Обновил конфигурацию** для headless режима?
3. ✅ **Настроил деплой** на Railway прямо сейчас?

Просто скажите "давай начнем" и я создам все файлы! 🚀

