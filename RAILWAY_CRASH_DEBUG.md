# 🔍 Railway Crash Debug

## ❌ Текущая проблема
Build успешен (108.62s), но приложение **крашится после старта**

## ✅ Что работает:
- [x] Docker build завершается успешно
- [x] Все зависимости установлены
- [x] Chrome и ChromeDriver установлены
- [x] Файлы скопированы

## ❓ Что проверить:

### 1. Deploy Logs (КРИТИЧНО!)
**В Railway откройте вкладку "Deployments" → "View Logs" → покажите что там**

Возможные причины краша:
- PORT environment variable не передается
- Uvicorn не может запуститься на порту 8080
- Permission issues с Chrome/ChromeDriver
- Недостаточно памяти при старте (хотя у вас 8GB)

### 2. Исправления, которые мы попробовали:

#### Fix #1: Вернули USER appuser
```dockerfile
USER appuser
```
**Зачем**: Без этого могут быть permission issues с файлами

#### Fix #2: Используем python -m uvicorn
```dockerfile
CMD ["python", "-m", "uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "info"]
```
**Проблема**: Railway передает переменную `PORT`, а мы хардкодим `8080`

### 3. Следующее исправление (если не поможет):

**Вариант A**: Использовать переменную PORT от Railway
```dockerfile
CMD sh -c "python -m uvicorn api_server:app --host 0.0.0.0 --port ${PORT:-8080} --log-level info"
```

**Вариант B**: Добавить startup script
```bash
#!/bin/bash
export PORT=${PORT:-8080}
python -m uvicorn api_server:app --host 0.0.0.0 --port $PORT --log-level info
```

## 📋 ЧТО МНЕ ПОКАЗАТЬ:

1. **Deploy Logs** (в Railway Console)
   - Что пишет при старте?
   - Есть ли ошибки?
   - На каком порту пытается стартовать?

2. **Railway Settings**
   - Какой PORT указан в Variables?
   - Есть ли другие environment variables?

3. **Crash Logs**
   - Exit code приложения
   - Последние строки перед крашем

## 🎯 ЖДЕМ:
После того как вы покажете deploy logs, мы сразу поймем проблему!

