# Руководство по загрузке файла остатков

## 📋 Обзор

Система поддерживает загрузку файла с остатками (`остатки.xls` или `остатки.xlsx`) для сравнения цен конкурентов с вашим инвентарем.

После загрузки файла система отображает дату актуальности остатков в формате **"Остатки актуальны на DD.MM.YYYY"**.

---

## 🌐 Веб-интерфейс (РЕКОМЕНДУЕТСЯ)

### Шаг 1: Откройте веб-интерфейс

Перейдите на главную страницу вашего приложения:
```
https://your-app.railway.app/
```

### Шаг 2: Загрузите файл

1. В секции **"📤 Загрузка файла с остатками"** нажмите кнопку **"Выбрать файл"**
2. Выберите ваш файл остатков (`остатки.xls` или `остатки.xlsx`)
3. Нажмите **"⬆️ Загрузить файл"**

### Шаг 3: Проверьте результат

После успешной загрузки вы увидите:
```
✅ Файл успешно загружен. Найдено товаров: 76
📅 Дата: 14.10.2025
```

Страница автоматически обновится и покажет:
```
✅ Файл с остатками загружен
📅 Остатки актуальны на: 14.10.2025
📦 Товаров: 76
📄 Файл: остатки.xlsx
```

---

## 🔌 API (для программного использования)

### 1. Загрузить файл остатков

**Endpoint**: `POST /inventory/upload`

**curl пример**:
```bash
curl -X POST \
  https://your-app.railway.app/inventory/upload \
  -F "file=@остатки.xlsx"
```

**Python пример**:
```python
import requests

url = "https://your-app.railway.app/inventory/upload"
files = {"file": open("остатки.xlsx", "rb")}

response = requests.post(url, files=files)
print(response.json())
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

### 2. Получить информацию об остатках

**Endpoint**: `GET /inventory/info`

**curl пример**:
```bash
curl https://your-app.railway.app/inventory/info
```

**Ответ** (файл загружен):
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

**Ответ** (файл не загружен):
```json
{
  "has_file": false,
  "filename": null,
  "uploaded_at": null,
  "uploaded_at_formatted": null,
  "size_bytes": null,
  "products_count": null,
  "message": "Файл с остатками не загружен"
}
```

### 3. Скачать текущий файл остатков

**Endpoint**: `GET /inventory/download`

**curl пример**:
```bash
curl https://your-app.railway.app/inventory/download -o остатки.xlsx
```

---

## 📁 Формат файла

### Требования к файлу:

1. **Расширение**: `.xls` или `.xlsx`
2. **Кодировка**: UTF-8 (для кириллицы)
3. **Структура**: Стандартный Excel файл с товарами

### Пример структуры:

| Артикул | Наименование | Количество | Цена |
|---------|--------------|------------|------|
| EC685.M | DeLonghi Dedica EC685.M | 15 | 599.00 |
| ECAM220.31.SB | DeLonghi Magnifica S | 8 | 1299.00 |

> **Примечание**: Система автоматически определяет структуру файла.

---

## 🔄 Обновление файла остатков

### Вариант 1: Через веб-интерфейс

1. Откройте https://your-app.railway.app/
2. Загрузите новый файл (старый будет автоматически заменен)
3. Дата актуальности обновится автоматически

### Вариант 2: Через API

```bash
# Загрузить обновленный файл
curl -X POST \
  https://your-app.railway.app/inventory/upload \
  -F "file=@остатки_обновленные.xlsx"
```

### Вариант 3: Автоматическое обновление через скрипт

Создайте скрипт для ежедневного обновления:

**update_inventory.py**:
```python
import requests
from pathlib import Path
from datetime import datetime

def upload_inventory(file_path, api_url):
    """Upload inventory file to Railway API"""
    
    if not Path(file_path).exists():
        print(f"❌ Файл не найден: {file_path}")
        return False
    
    url = f"{api_url}/inventory/upload"
    files = {"file": open(file_path, "rb")}
    
    try:
        response = requests.post(url, files=files)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ {data['message']}")
        print(f"📅 Дата: {data['uploaded_at_formatted']}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    # Настройки
    API_URL = "https://your-app.railway.app"
    INVENTORY_FILE = "остатки.xlsx"
    
    # Загрузить
    upload_inventory(INVENTORY_FILE, API_URL)
```

**Запуск**:
```bash
python update_inventory.py
```

### Вариант 4: Через Cron Job

Настроить автоматическое обновление каждый день в 8:00:

**Linux/Mac** (`crontab -e`):
```bash
0 8 * * * cd /path/to/project && python update_inventory.py
```

**Windows** (Task Scheduler):
1. Открыть Task Scheduler
2. Создать новую задачу
3. Trigger: Daily at 8:00 AM
4. Action: `python D:\path\to\update_inventory.py`

---

## 🔍 Проверка актуальности остатков

### В веб-интерфейсе

Главная страница всегда показывает:
```
✅ Файл с остатками загружен
📅 Остатки актуальны на: 14.10.2025
```

### Через API

```bash
curl https://your-app.railway.app/inventory/info | jq '.uploaded_at_formatted'
# Вывод: "14.10.2025"
```

### В health check

```bash
curl https://your-app.railway.app/health | jq '.inventory'
```

Ответ:
```json
{
  "loaded": true,
  "date": "14.10.2025"
}
```

---

## 💾 Хранение файла в Railway

### Railway Volumes

Файл остатков хранится в Railway Volume:
```
/app/data/inbox/остатки.xlsx
```

**Преимущества**:
- ✅ Файл сохраняется между перезапусками
- ✅ Автоматические бэкапы
- ✅ Доступ из любого деплоя

**Настройка Volume**:
1. Railway Dashboard → **Settings** → **Volumes**
2. Mount Path: `/app/data`
3. Size: 1 GB

### Метаданные

Дата загрузки сохраняется в:
```
/app/data/inbox/inventory_metadata.json
```

Содержимое:
```json
{
  "filename": "остатки.xlsx",
  "uploaded_at": "2025-10-14T09:30:00",
  "uploaded_at_formatted": "14.10.2025"
}
```

---

## 🚨 Устранение неполадок

### Проблема: "Файл с остатками не загружен"

**Решение 1**: Загрузите файл через веб-интерфейс

**Решение 2**: Проверьте, что Volume подключен:
```bash
railway run ls -la /app/data/inbox/
```

### Проблема: "Файл должен быть в формате .xls или .xlsx"

**Решение**: Убедитесь, что файл имеет правильное расширение:
```bash
# Конвертировать CSV в XLSX (если нужно)
import pandas as pd
df = pd.read_csv('остатки.csv')
df.to_excel('остатки.xlsx', index=False)
```

### Проблема: Дата не обновляется

**Решение**: Принудительно обновить метаданные:
```bash
# Удалить старые метаданные
curl -X DELETE https://your-app.railway.app/inventory/metadata

# Загрузить файл заново
curl -X POST https://your-app.railway.app/inventory/upload -F "file=@остатки.xlsx"
```

### Проблема: Неправильное количество товаров

**Решение**: Проверьте формат файла:
```python
import pandas as pd

# Прочитать файл
df = pd.read_excel('остатки.xlsx')

# Проверить структуру
print(f"Строк: {len(df)}")
print(f"Столбцов: {len(df.columns)}")
print(df.head())
```

---

## 📊 Интеграция с системой парсинга

После загрузки файла остатков, при запуске полного цикла парсинга:

1. **Система парсит** цены конкурентов (ALTA, KONTAKT, ELITE, DIM_KAVA)
2. **Загружает остатки** из `/app/data/inbox/остатки.xlsx`
3. **Сопоставляет товары** по моделям
4. **Генерирует отчет** с сравнением цен

**Отчет будет включать**:
- ✅ Ваши остатки (количество)
- ✅ Ваши цены
- ✅ Цены конкурентов
- ✅ Разницу в ценах
- ✅ **Дату актуальности остатков**

---

## 📅 Рекомендации

### Ежедневное обновление

Обновляйте файл остатков каждый день перед запуском парсинга:

**Сценарий**:
```bash
# 1. Загрузить остатки (8:00)
python update_inventory.py

# 2. Запустить парсинг (8:05)
curl -X POST https://your-app.railway.app/scrape/all
```

### Уведомления об устаревших остатках

Создайте проверку:

```python
import requests
from datetime import datetime, timedelta

def check_inventory_freshness(api_url, max_days=1):
    """Check if inventory is fresh"""
    response = requests.get(f"{api_url}/inventory/info")
    data = response.json()
    
    if not data['has_file']:
        print("⚠️ Файл остатков не загружен!")
        return False
    
    # Parse date
    uploaded_date = datetime.fromisoformat(data['uploaded_at'])
    days_old = (datetime.now() - uploaded_date).days
    
    if days_old > max_days:
        print(f"⚠️ Остатки устарели на {days_old} дней!")
        print(f"📅 Последнее обновление: {data['uploaded_at_formatted']}")
        return False
    
    print(f"✅ Остатки актуальны ({data['uploaded_at_formatted']})")
    return True

# Использование
check_inventory_freshness("https://your-app.railway.app", max_days=1)
```

---

## ✅ Итоговый чеклист

- [ ] Файл остатков подготовлен (`.xls` или `.xlsx`)
- [ ] Railway Volume настроен (`/app/data`)
- [ ] Файл загружен через веб-интерфейс или API
- [ ] Проверена дата актуальности в веб-интерфейсе
- [ ] Настроено автоматическое обновление (опционально)
- [ ] Протестирован полный цикл парсинга с остатками

---

## 🎉 Готово!

Теперь ваша система:
- ✅ Отображает дату актуальности остатков
- ✅ Позволяет загружать файлы через веб-интерфейс
- ✅ Хранит файлы в постоянном хранилище Railway
- ✅ Предоставляет API для автоматизации

**Главная страница**: https://your-app.railway.app/

**Информация об остатках**: https://your-app.railway.app/inventory/info

