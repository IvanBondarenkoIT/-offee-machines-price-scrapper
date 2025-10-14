# 🔧 Отладка 502 ошибки на Railway

## ✅ Локальное тестирование

**Результат**: Приложение работает отлично локально!

```
✅ http://localhost:8000/ - Главная страница загружается
✅ http://localhost:8000/health - 200 OK
✅ http://localhost:8000/docs - Swagger работает
```

**Вывод**: Код приложения исправен. Проблема в Railway конфигурации.

---

## 🔍 Возможные причины 502 на Railway

### 1. ⏱️ Timeout при запуске

**Проблема**: Приложение долго запускается, Railway отдает 502 до готовности.

**Проверка в Railway Logs**:
```
Ищем строку: "Application startup complete"
```

**Решение**:
- Увеличить timeout в Railway Settings
- Оптимизировать startup скрипт

---

### 2. 🐛 Приложение падает при старте

**Проблема**: Ошибка при импорте или инициализации на Linux.

**Проверка в Railway Logs**:
```
Ищем: Traceback, ModuleNotFoundError, ImportError
```

**Возможные причины**:
- Отсутствующие зависимости в requirements.railway.txt
- Проблемы с путями (Windows vs Linux)
- Права доступа к файлам

**Решение**:
```dockerfile
# Проверить, что все зависимости установлены
RUN pip list

# Проверить структуру файлов
RUN ls -la /app
```

---

### 3. 📁 Проблемы с start.sh

**Проблема**: Скрипт не выполняется или падает.

**Проверка**:
```bash
# start.sh должен быть executable
RUN chmod +x /app/start.sh

# Должен использовать LF, а не CRLF
```

**Решение**: Пересоздать start.sh с правильными окончаниями строк

---

### 4. 🔌 Неправильная привязка к порту

**Проблема**: Uvicorn слушает не тот интерфейс.

**Проверка в start.sh**:
```bash
exec uvicorn api_server:app \
    --host 0.0.0.0 \        # ✅ Должно быть 0.0.0.0
    --port ${PORT:-8080}    # ✅ Должно использовать $PORT
```

**Неправильно**:
```bash
--host 127.0.0.1  # ❌ Localhost only
--port 8000       # ❌ Жестко заданный порт
```

---

### 5. 📦 Отсутствующие зависимости

**Проблема**: Какой-то пакет не установлен.

**Проверка**:
```dockerfile
# В Dockerfile после pip install
RUN pip list | grep -E "(fastapi|uvicorn|pydantic)"
```

**Решение**: Добавить отсутствующие пакеты в requirements.railway.txt

---

### 6. 🚫 Health check падает

**Проблема**: Health check endpoint возвращает ошибку.

**Проверка**:
```bash
# В контейнере
curl http://localhost:$PORT/health
```

**Решение**: Мы уже отключили HEALTHCHECK в Dockerfile

---

### 7. 🔒 Проблемы с правами пользователя

**Проблема**: appuser не может создать папки или записать файлы.

**Проверка в Dockerfile**:
```dockerfile
USER appuser

# Создать директории ДО переключения на appuser
RUN mkdir -p /app/data && chown appuser:appuser /app/data
```

**Решение**: Убедиться, что все папки созданы с правильными правами

---

## 🎯 Пошаговая отладка для Railway

### Шаг 1: Проверить логи сборки

Railway Logs → Build:
```
Ищем ошибки при:
- apt-get install
- pip install
- COPY команды
```

### Шаг 2: Проверить логи запуска

Railway Logs → Deploy:
```
========================================
Starting Coffee Price Monitor API
========================================
PORT: 8080                              ← Должен быть правильный порт
PYTHON_ENV: production
Working directory: /app
Python version: Python 3.11.x
========================================

INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.  ← Эта строка ОБЯЗАТЕЛЬНА!
INFO:     Uvicorn running on http://0.0.0.0:8080
```

### Шаг 3: Упрощенная версия для теста

Создадим минимальный Dockerfile для быстрого теста:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Только минимум зависимостей
RUN pip install fastapi uvicorn[standard]

# Простой тестовый файл
COPY api_server.py .

# Запуск напрямую (без start.sh)
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Шаг 4: Проверить переменные окружения

В Railway Dashboard → Variables:
```
PORT=8080           ← Убедиться, что установлен
PYTHON_ENV=production
```

---

## 🔧 Быстрые исправления

### Исправление 1: Убрать start.sh (тест)

```dockerfile
# Вместо:
CMD ["/bin/bash", "/app/start.sh"]

# Попробовать напрямую:
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Исправление 2: Добавить логирование

```dockerfile
CMD ["uvicorn", "api_server:app", \
     "--host", "0.0.0.0", \
     "--port", "8080", \
     "--log-level", "debug"]  # Больше логов
```

### Исправление 3: Упростить Dockerfile

Убрать всё лишнее, оставить минимум для теста.

---

## 📊 Чеклист проверки

- [ ] Логи сборки - успешно?
- [ ] Логи запуска - есть "Application startup complete"?
- [ ] Переменная PORT установлена?
- [ ] Health endpoint доступен изнутри контейнера?
- [ ] start.sh имеет права на выполнение?
- [ ] Все зависимости установлены?
- [ ] Папки data/ созданы?
- [ ] Uvicorn слушает 0.0.0.0:$PORT?

---

## 🚀 Следующие шаги

1. **Проверить логи Railway** - самое важное!
2. **Упростить Dockerfile** для теста
3. **Убрать start.sh** - запускать uvicorn напрямую
4. **Добавить debug логирование**
5. **Проверить переменные окружения**

---

## 📝 Шаблон для анализа логов

**Что смотреть в Railway Logs**:

```
✅ ХОРОШО:
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080

❌ ПЛОХО:
Traceback (most recent call last):
  File ...
ModuleNotFoundError: No module named 'fastapi'
  
❌ ПЛОХО:
Error: /bin/bash: /app/start.sh: Permission denied

❌ ПЛОХО:
OSError: [Errno 13] Permission denied: '/app/data'
```

---

**Дата**: 2025-10-14  
**Статус**: Локально работает ✅, Railway 502 ❌  
**Следующий шаг**: Проверить логи Railway

