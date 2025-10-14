# Развертывание на Railway.com - Пошаговая инструкция

## 📋 Предварительные требования

1. ✅ Аккаунт на [Railway.com](https://railway.com)
2. ✅ Git репозиторий (GitHub, GitLab, или Bitbucket)
3. ✅ Railway CLI (опционально, но рекомендуется)

---

## 🚀 Метод 1: Деплой через GitHub (РЕКОМЕНДУЕТСЯ)

### Шаг 1: Подготовка репозитория

```bash
# Убедитесь, что все файлы добавлены в git
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### Шаг 2: Создание проекта на Railway

1. Перейдите на [railway.com](https://railway.com)
2. Нажмите **"New Project"**
3. Выберите **"Deploy from GitHub repo"**
4. Авторизуйте Railway для доступа к GitHub
5. Выберите ваш репозиторий `coffee-machines-price-scrapper`
6. Railway автоматически обнаружит `Dockerfile` и начнет сборку

### Шаг 3: Настройка переменных окружения

В Railway Dashboard → **Variables** добавьте:

```env
PORT=8000
PYTHON_ENV=production
HEADLESS=true
LOG_LEVEL=INFO
```

### Шаг 4: Настройка постоянного хранилища (Volume)

1. В Railway Dashboard → **Settings** → **Volumes**
2. Нажмите **"New Volume"**
3. Настройки:
   - **Mount Path**: `/app/data`
   - **Size**: 1 GB (можно увеличить при необходимости)
4. Сохранить и перезапустить деплой

### Шаг 5: Получение публичного URL

1. В Railway Dashboard → **Settings** → **Networking**
2. Нажмите **"Generate Domain"**
3. Railway создаст домен вида: `your-app.railway.app`

### Шаг 6: Проверка работоспособности

```bash
# Проверить health check
curl https://your-app.railway.app/health

# Проверить API
curl https://your-app.railway.app/

# Запустить парсинг
curl -X POST https://your-app.railway.app/scrape/all

# Проверить статус
curl https://your-app.railway.app/status

# Скачать отчет
curl https://your-app.railway.app/reports/latest -o report.xlsx
```

---

## 🛠️ Метод 2: Деплой через Railway CLI

### Установка Railway CLI

```bash
# macOS/Linux
curl -fsSL https://railway.app/install.sh | sh

# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex

# Альтернатива: через npm
npm i -g @railway/cli
```

### Деплой

```bash
# 1. Войти в аккаунт
railway login

# 2. Инициализировать проект
railway init

# 3. Создать Volume (через Dashboard)
# Перейдите в Dashboard и создайте Volume как описано выше

# 4. Деплой
railway up

# 5. Открыть приложение
railway open

# 6. Просмотр логов
railway logs

# 7. Подключиться к контейнеру
railway run bash
```

---

## 📊 Настройка Cron Job для автоматического запуска

### Вариант A: Railway Cron (встроенный)

1. В Railway Dashboard создать новый сервис
2. Выбрать **"Cron Job"**
3. Настроить:
   - **Schedule**: `0 9 * * *` (каждый день в 9:00 UTC)
   - **Command**: `python run_full_cycle.py`
   - Использовать тот же Volume

### Вариант B: Внешний Cron (cron-job.org)

1. Зарегистрироваться на [cron-job.org](https://cron-job.org)
2. Создать новый Cron Job:
   - **URL**: `https://your-app.railway.app/scrape/all`
   - **Method**: POST
   - **Schedule**: `0 9 * * *` (каждый день в 9:00)
3. Включить и сохранить

### Вариант C: GitHub Actions

Создать `.github/workflows/daily-scrape.yml`:

```yaml
name: Daily Price Scraping

on:
  schedule:
    - cron: '0 9 * * *'  # 9:00 UTC каждый день
  workflow_dispatch:  # Можно запустить вручную

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Railway scraping
        run: |
          curl -X POST https://your-app.railway.app/scrape/all
```

---

## 🔧 Локальное тестирование Docker перед деплоем

### Сборка образа

```bash
docker build -t coffee-scraper .
```

### Запуск контейнера

```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e HEADLESS=true \
  --name coffee-scraper \
  coffee-scraper
```

### Проверка

```bash
# Проверить логи
docker logs coffee-scraper

# Проверить API
curl http://localhost:8000/

# Запустить парсинг
curl -X POST http://localhost:8000/scrape/all

# Зайти в контейнер
docker exec -it coffee-scraper bash
```

### Остановка и очистка

```bash
docker stop coffee-scraper
docker rm coffee-scraper
docker rmi coffee-scraper
```

---

## 📱 Использование API

### Основные эндпоинты

#### 1. Получить информацию об API
```bash
GET https://your-app.railway.app/
```

#### 2. Запустить полный цикл парсинга (все 4 сайта)
```bash
POST https://your-app.railway.app/scrape/all
```

Ответ:
```json
{
  "status": "started",
  "message": "Full cycle scraping started in background. Check /status for progress.",
  "started_at": "2025-10-14T09:00:00"
}
```

#### 3. Проверить статус парсинга
```bash
GET https://your-app.railway.app/status
```

Ответ:
```json
{
  "current_status": "running",
  "last_run": "2025-10-14T09:00:00",
  "products_scraped": 183,
  "current_step": "Scraping ELITE",
  "error": null
}
```

#### 4. Скачать последний отчет
```bash
GET https://your-app.railway.app/reports/latest
# Вернет Excel файл для скачивания
```

#### 5. Список всех отчетов
```bash
GET https://your-app.railway.app/reports/list
```

#### 6. Запустить парсинг отдельного сайта
```bash
POST https://your-app.railway.app/scrape/alta
POST https://your-app.railway.app/scrape/kontakt
POST https://your-app.railway.app/scrape/elite
POST https://your-app.railway.app/scrape/dimkava
```

---

## 📈 Мониторинг и логи

### Просмотр логов в Railway Dashboard

1. Railway Dashboard → **Deployments**
2. Выбрать активный деплоймент
3. Вкладка **"Logs"**

### Просмотр логов через CLI

```bash
railway logs --tail
```

### Метрики

Railway автоматически отслеживает:
- ✅ CPU использование
- ✅ Memory использование
- ✅ Network traffic
- ✅ Deployment status

---

## 🔍 Отладка проблем

### Проблема: Контейнер не запускается

**Решение**: Проверьте логи
```bash
railway logs
```

### Проблема: Chrome не работает в headless режиме

**Решение**: Убедитесь, что в `config.py`:
```python
SELENIUM_CONFIG = {
    "headless": True,
    # ...
}
```

### Проблема: Недостаточно памяти

**Решение**: 
1. Railway Dashboard → **Settings** → **Resources**
2. Увеличить RAM до 1GB или 2GB

### Проблема: Файлы исчезают после перезапуска

**Решение**: Убедитесь, что Volume подключен:
1. Railway Dashboard → **Settings** → **Volumes**
2. Mount Path должен быть `/app/data`

### Проблема: PDF конвертация не работает

**Решение**: В Railway используется WeasyPrint (кроссплатформенный). Если нужен оригинальный Word → PDF:
- Добавить LibreOffice в Dockerfile
- Использовать `unoconv`

---

## 💰 Стоимость и Free Tier

### Railway Free Tier (Starter Plan)
- ✅ $5 бесплатных кредитов в месяц
- ✅ 500 часов выполнения
- ✅ 1 GB памяти
- ✅ 1 GB хранилища

### Примерная стоимость для этого проекта

| Компонент | Использование | Стоимость/месяц |
|-----------|---------------|-----------------|
| Web Service (always-on) | 720 часов | ~$4 |
| RAM (512 MB) | постоянно | включено |
| Volume (1 GB) | постоянно | ~$0.25 |
| Egress (100 MB/день) | ~3 GB/месяц | ~$0.50 |
| **ИТОГО** | | **~$5/месяц** |

**Вывод**: Free tier покрывает все расходы для тестирования!

### Оптимизация расходов

1. **Использовать Cron Job вместо Web Service**
   - Запускать только когда нужно (1 раз в день)
   - Стоимость: ~$0.5/месяц

2. **Sleep Application** (если нужен только API по расписанию)
   - Railway может "усыплять" приложение
   - Просыпается при запросе
   - Экономия: ~50%

---

## 🎯 Рекомендации для продакшена

### 1. Настроить уведомления

Добавить email уведомления при завершении парсинга:

```python
import smtplib
from email.message import EmailMessage

def send_notification(report_path):
    msg = EmailMessage()
    msg['Subject'] = 'Price Monitoring Report Ready'
    msg['From'] = 'scraper@company.com'
    msg['To'] = 'director@company.com'
    msg.set_content('New price report is ready!')
    
    # Attach report
    with open(report_path, 'rb') as f:
        msg.add_attachment(f.read(), 
                          maintype='application',
                          subtype='xlsx',
                          filename='report.xlsx')
    
    # Send
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(msg)
```

### 2. Интеграция с Google Drive

Автоматически загружать отчеты в Google Drive:

```python
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

def upload_to_drive(file_path):
    creds = Credentials.from_service_account_info(
        json.loads(os.getenv('GOOGLE_CREDENTIALS'))
    )
    service = build('drive', 'v3', credentials=creds)
    
    file_metadata = {'name': file_path.name}
    media = MediaFileUpload(file_path)
    
    file = service.files().create(
        body=file_metadata,
        media_body=media
    ).execute()
```

### 3. Telegram бот для уведомлений

```python
import requests

def send_telegram(message, report_path=None):
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    requests.post(url, json={'chat_id': chat_id, 'text': message})
    
    if report_path:
        url = f'https://api.telegram.org/bot{bot_token}/sendDocument'
        files = {'document': open(report_path, 'rb')}
        requests.post(url, data={'chat_id': chat_id}, files=files)
```

### 4. Мониторинг через Healthchecks.io

Бесплатный сервис для мониторинга Cron Jobs:

```python
import requests

def ping_healthcheck():
    url = os.getenv('HEALTHCHECK_URL')
    if url:
        requests.get(url)
```

---

## ✅ Чеклист перед деплоем

- [ ] Все файлы созданы (Dockerfile, railway.json, .env.example)
- [ ] Код в git репозитории
- [ ] `config.py` настроен на `headless: True`
- [ ] Railway проект создан
- [ ] Переменные окружения настроены
- [ ] Volume создан и подключен к `/app/data`
- [ ] Домен сгенерирован
- [ ] API endpoints протестированы
- [ ] Cron Job настроен (опционально)
- [ ] Уведомления настроены (опционально)

---

## 🎉 Готово!

После деплоя ваше приложение будет доступно по адресу:
```
https://your-app.railway.app
```

Документация API:
```
https://your-app.railway.app/docs
```

Для автоматического запуска каждый день в 9:00 настройте Cron Job как описано выше.

---

## 📞 Поддержка

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: создайте issue в вашем репозитории

