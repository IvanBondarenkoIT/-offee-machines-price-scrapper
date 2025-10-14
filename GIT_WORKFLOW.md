# 🌿 Git Workflow - Работа с ветками

## 📋 Структура веток

### `main` - Стабильная ветка
- ✅ Только стабильный, протестированный код
- ✅ Готов к деплою на Railway
- ✅ Защищена от прямых коммитов (рекомендуется)

### `dev` - Ветка разработки (текущая)
- 🚧 Активная разработка
- 🚧 Новые функции
- 🚧 Исправления и эксперименты

---

## 🔄 Текущий статус

```
✅ Ветка dev создана и активна
✅ Отправлена на GitHub
✅ Настроено отслеживание origin/dev
```

**Текущая ветка:** `dev` ⭐

---

## 🛠️ Основные команды

### Переключение между ветками

```bash
# Переключиться на dev (разработка)
git checkout dev

# Переключиться на main (стабильная)
git checkout main

# Посмотреть текущую ветку
git branch
```

### Работа в ветке dev

```bash
# 1. Убедиться, что вы на dev
git checkout dev

# 2. Внести изменения в код
# ... редактирование файлов ...

# 3. Закоммитить изменения
git add .
git commit -m "Add new feature: описание"

# 4. Отправить на GitHub
git push origin dev
```

### Слияние dev → main (когда готово)

```bash
# 1. Переключиться на main
git checkout main

# 2. Обновить main
git pull origin main

# 3. Слить изменения из dev
git merge dev

# 4. Отправить на GitHub
git push origin main

# 5. Вернуться на dev для дальнейшей работы
git checkout dev
```

---

## 🎯 Рекомендуемый workflow

### Вариант 1: Простой (для одного разработчика)

```
dev (разработка)
  ↓
  ↓ (когда готово)
  ↓
main (стабильная)
  ↓
Railway (автодеплой)
```

**Процесс:**
1. Работаете в `dev`
2. Когда функция готова и протестирована → `merge` в `main`
3. Railway автоматически деплоит из `main`

### Вариант 2: С feature branches (для команды)

```
feature/inventory-upload
  ↓
dev (тестирование)
  ↓
main (продакшн)
  ↓
Railway
```

**Процесс:**
1. Создаете ветку для функции: `git checkout -b feature/название`
2. Работаете в feature ветке
3. Готово → merge в `dev` для тестирования
4. Протестировано → merge в `main`
5. Railway деплоит

---

## 📝 Примеры для текущего проекта

### Сценарий 1: Добавление новой функции

```bash
# Находимся в dev
git checkout dev

# Создаем функцию (например, email уведомления)
# ... код ...

# Коммитим
git add .
git commit -m "Add email notifications for scraping completion"
git push origin dev

# Тестируем на Railway (можно подключить dev ветку)

# Когда готово - мержим в main
git checkout main
git merge dev
git push origin main
```

### Сценарий 2: Исправление бага

```bash
# Если баг критичный - можно фиксить прямо в dev
git checkout dev

# Исправляем
# ... код ...

git add .
git commit -m "Fix: Chrome installation in Dockerfile"
git push origin dev

# Если нужно срочно - сразу в main
git checkout main
git merge dev
git push origin main
```

### Сценарий 3: Эксперименты

```bash
# Создаем отдельную ветку для экспериментов
git checkout -b experiment/new-parser
# ... эксперименты ...

# Если успешно - мержим в dev
git checkout dev
git merge experiment/new-parser

# Если неудачно - просто удаляем
git branch -D experiment/new-parser
```

---

## 🚀 Railway Deployment

### Настройка на Railway

**Вариант 1: Main только (рекомендуется для начала)**
- Railway → Settings → Deploy branch: `main`
- Деплой только когда мержите в main

**Вариант 2: Отдельные окружения**
- **Production**: деплой из `main`
- **Staging**: деплой из `dev`

Настройка в Railway:
1. Создать 2 сервиса (или 2 проекта)
2. Production → Deploy from `main`
3. Staging → Deploy from `dev`

---

## 📊 Pull Requests (на GitHub)

Для более строгого контроля:

1. **Защитить main** (GitHub Settings → Branches):
   - Require pull request before merging
   - Require approvals: 1

2. **Workflow с PR:**
   ```bash
   # Работаете в dev
   git checkout dev
   git add .
   git commit -m "Feature: описание"
   git push origin dev
   
   # На GitHub создаете Pull Request: dev → main
   # Проверяете изменения
   # Merge через интерфейс GitHub
   ```

---

## 🔍 Полезные команды

```bash
# Посмотреть все ветки (локальные и удаленные)
git branch -a

# Посмотреть текущую ветку
git branch

# Посмотреть историю коммитов
git log --oneline --graph --all

# Посмотреть различия между ветками
git diff main dev

# Посмотреть статус
git status

# Удалить локальную ветку (если не нужна)
git branch -d название-ветки

# Удалить удаленную ветку
git push origin --delete название-ветки
```

---

## ✅ Текущая настройка проекта

```
Repository: IvanBondarenkoIT/-offee-machines-price-scrapper

Branches:
  * dev     ← Текущая ветка (для разработки)
    main    ← Стабильная ветка (для Railway)

Remote branches:
  origin/dev
  origin/main
```

---

## 🎯 Рекомендации

### Для разработки:
- ✅ **Всегда работайте в `dev`**
- ✅ Коммитьте часто с понятными сообщениями
- ✅ Пушьте в `origin/dev` регулярно

### Для деплоя:
- ✅ Тестируйте в `dev` перед мержем
- ✅ Мержите в `main` только стабильный код
- ✅ После мержа в `main` - Railway автоматически деплоит

### Для команды:
- ✅ Создавайте feature branches для больших фич
- ✅ Используйте Pull Requests
- ✅ Ревьюте код перед мержем

---

## 🚨 Частые проблемы

### Проблема: "Нужно срочно исправить баг в main"

**Решение:**
```bash
# Создать hotfix ветку от main
git checkout main
git checkout -b hotfix/critical-bug

# Исправить
# ... код ...

# Коммит
git commit -am "Hotfix: описание"

# Мерж в main
git checkout main
git merge hotfix/critical-bug
git push origin main

# Мерж в dev (чтобы не потерять исправление)
git checkout dev
git merge hotfix/critical-bug
git push origin dev

# Удалить hotfix ветку
git branch -d hotfix/critical-bug
```

### Проблема: "Конфликты при мерже"

**Решение:**
```bash
# При мерже возникли конфликты
git merge dev
# CONFLICT ...

# Открыть файлы с конфликтами
# Разрешить вручную (удалить <<<<<<, ======, >>>>>>)

# Добавить разрешенные файлы
git add .

# Завершить мерж
git commit -m "Merge dev into main"
```

---

## 📖 Дополнительные ресурсы

- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Git Branching Model](https://nvie.com/posts/a-successful-git-branching-model/)
- [Railway Deployment Docs](https://docs.railway.app/deploy/deployments)

---

**Создано**: 2025-10-14  
**Текущая ветка**: `dev` ✅  
**Готово к разработке**: Да 🚀

