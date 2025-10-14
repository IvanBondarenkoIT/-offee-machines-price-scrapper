# 🔧 Проверка настроек Railway

## 🚨 Проблема: Пустые Deploy Logs

Даже с shell form CMD логи не появляются!

---

## ✅ Что проверить в Railway Dashboard

### 1. Service Settings → Deploy

**Start Command**:
- Должно быть **пусто** (используем CMD из Dockerfile)
- Если что-то указано - удалить!

### 2. Service Settings → Variables

**Переменные окружения**:
```
PORT=8080  ← Проверить что установлена
```

Не должно быть конфликтующих переменных.

### 3. Service Settings → Networking

**Domain**:
- Проверить что домен сгенерирован
- Порт должен быть 8080

### 4. Deployments → View Source

**Branch**: Должна быть `main`

### 5. Service Settings → Source

**Root Directory**: Должно быть пусто (корень репозитория)

**Watch Paths**: Должно быть пусто или `**`

---

## 🎯 Текущий тест: Запуск от root

**Изменение**:
```dockerfile
# Было:
USER appuser

# Стало (тест):
# USER appuser  ← Закомментировано
```

**Почему**:
Railway может не поддерживать non-root пользователей или иметь проблемы с правами.

**Если логи появятся** → проблема была в `USER appuser`

**Если логи всё еще пусты** → проблема глубже (настройки Railway или что-то еще)

---

## 🔍 Альтернативные проверки

### Проверка 1: Railway Service Type

Railway Dashboard → Service:
- Должен быть тип **"Web Service"**
- НЕ "Cron Job" или "Worker"

### Проверка 2: Railway Region

Ваш регион: `europe-west4`
- Попробовать сменить на `us-west1` для теста?

### Проверка 3: Railway Restart Policy

Settings → Deploy:
- Restart Policy: Should be enabled
- Health Check: Disabled (мы отключили в Dockerfile)

### Проверка 4: Railway Logs Retention

По умолчанию Railway показывает логи.
Но если есть проблемы - логи могут не записываться.

---

## 🆘 Если логи ВСЁ ЕЩЁ пусты после теста без USER

### Вариант 1: Использовать Dockerfile.minimal

Создать в Railway Settings:
```
Build Settings:
  Docker Build Args: -f Dockerfile.minimal
```

Или:
```bash
# В корне проекта заменить Dockerfile на minimal
mv Dockerfile Dockerfile.full
mv Dockerfile.minimal Dockerfile
git commit -am "Use minimal Dockerfile for debugging"
git push
```

### Вариант 2: Добавить ENTRYPOINT

```dockerfile
ENTRYPOINT ["/bin/sh", "-c"]
CMD ["echo 'TEST START' && python -m uvicorn api_server:app --host 0.0.0.0 --port 8080"]
```

### Вариант 3: Создать start script в репозитории

```bash
# start.sh
#!/bin/sh
set -e
echo "========== STARTUP =========="
pwd
ls -la
python --version
echo "Starting uvicorn..."
exec python -m uvicorn api_server:app --host 0.0.0.0 --port 8080
```

```dockerfile
COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]
```

---

## 📊 Что Railway должен показывать

### Build Logs (есть):
```
✓ [1/11] FROM python:3.11-slim
✓ [2/11] RUN apt-get install...
...
✓ Build time: 20.08 seconds
```

### Deploy Logs (должны быть, но пусто):
```
========== Starting Coffee Price Monitor API ==========
Working directory: /app
...
INFO: Started server process
INFO: Uvicorn running on http://0.0.0.0:8080
```

---

## 🎯 План действий

1. **Сейчас**: Тест без USER appuser
2. **Если не помогло**: Использовать Dockerfile.minimal
3. **Если и это не помогло**: Проверить настройки Railway
4. **Последний вариант**: Создать новый сервис на Railway с нуля

---

## 💡 Возможно Railway требует:

1. **Health check endpoint** - но у нас есть `/health`
2. **Определенный формат логов** - но echo должен работать
3. **Явный ENTRYPOINT** - попробуем если текущий тест не поможет
4. **Запуск от root** - тестируем сейчас

---

**Дата**: 2025-10-14  
**Тест**: Без USER appuser  
**Ожидание**: Логи ДОЛЖНЫ появиться!

