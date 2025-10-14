# 🧪 Минимальный тест для Railway

## 🎯 Цель

Убедиться, что Railway вообще может запустить наш проект.

Создано:
- ✅ `api_minimal.py` - простейший FastAPI (только Hello World)
- ✅ `Dockerfile.test` - минимальный Docker (без Chrome, без pandas)

---

## 🚀 Как использовать

### Вариант 1: Локальный тест (чтобы убедиться что работает)

```bash
# Запустить локально
python api_minimal.py

# Открыть в браузере
http://localhost:8000
```

**Должны увидеть**:
```
✅ Railway Works!
Deployment Successful
```

### Вариант 2: Деплой на Railway

#### Шаг 1: Переименовать файлы

```bash
# Сохранить текущие
git mv Dockerfile Dockerfile.full
git mv api_server.py api_server.full.py

# Использовать минимальные
git mv Dockerfile.test Dockerfile
git mv api_minimal.py api_server.py

# Закоммитить
git add .
git commit -m "Test: use minimal Dockerfile and api"
git push origin main
```

#### Шаг 2: Railway пересоберет

Railway увидит изменения в `main`:
- Соберет минимальный Dockerfile (~30 секунд вместо 2 минут)
- Запустит минимальное приложение (только FastAPI, ~50MB RAM)

#### Шаг 3: Проверить

Откройте ваш Railway URL:
```
https://your-app.railway.app/
```

**Должны увидеть**:
```
✅ Railway Works!
Deployment Successful
Coffee Price Monitor API
Всё работает нормально! 🎉
```

---

## 📊 Если это НЕ заработает

Значит проблема в **настройках Railway**, а не в коде!

**Проверить**:

1. **Settings → Deploy → Start Command**: 
   - Должно быть **ПУСТО**!

2. **Settings → Variables**:
   - `PORT` не нужна (используем 8080 по умолчанию)

3. **Service Type**:
   - Должен быть **"Web Service"**

---

## 📊 Если это ЗАРАБОТАЕТ

### ✅ Отлично! Теперь знаем:

1. Railway работает с нашим проектом
2. Проблема была в тяжелых зависимостях (Chrome, pandas)
3. Можно постепенно добавлять функциональность

### 📝 План возврата к полной версии:

**Шаг 1**: Вернуть api_server.py (уже с lazy imports)
```bash
git mv api_server.py api_minimal.py
git mv api_server.full.py api_server.py
```

**Шаг 2**: Вернуть Dockerfile БЕЗ Chrome (сначала без парсинга)
```dockerfile
# Убрать Chrome/ChromeDriver
# Оставить только FastAPI + dependencies для отчетов
```

**Шаг 3**: Если работает - добавить Chrome
```dockerfile
# Добавить установку Chrome
# НО: убедиться что не превышаем память
```

---

## 💰 Важно про память

| Компонент | RAM |
|-----------|-----|
| Python 3.11 | ~20MB |
| FastAPI minimal | ~30MB |
| FastAPI + pandas | ~300MB |
| Chrome headless | ~100-150MB |
| **Railway Free Tier** | **512MB** |

**Вывод**: С Chrome + pandas = близко к лимиту!

**Решение**:
1. Lazy imports (уже сделано)
2. Увеличить RAM до 1GB (Railway Settings)

---

## 🎯 РЕКОМЕНДУЮ ПРЯМО СЕЙЧАС:

### Вариант A: Тест с минимальным приложением (5 минут)

```bash
git mv Dockerfile Dockerfile.full
cp Dockerfile.test Dockerfile
git add Dockerfile Dockerfile.full api_minimal.py
git commit -m "TEST: minimal app without heavy dependencies"
git push origin main
```

Через 2 минуты увидим работает ли вообще Railway с нашим проектом.

### Вариант B: Просто увеличить RAM в Railway

Railway Dashboard → Settings → Resources:
- Memory: **1024 MB** (вместо 512MB)
- Стоимость: ~$1/месяц дополнительно

Может этого хватит для полного приложения!

---

**Что делаем?** 

1. Тестируем минимальное приложение? (вариант A)
2. Увеличиваем память в Railway? (вариант B)
3. Или и то и другое?
