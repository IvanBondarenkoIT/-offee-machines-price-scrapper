# Исправление Dockerfile для Railway

## ❌ Проблема

При деплое на Railway возникла ошибка:
```
/bin/sh: 1: apt-key: not found
ERROR: failed to build: exit code: 127
```

## 🔍 Причина

Команда `apt-key` устарела и удалена из новых версий Debian (используется в Python 3.11-slim).

**Старый метод (не работает):**
```dockerfile
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
```

## ✅ Решение

Используем современный метод с GPG ключами:

**Новый метод:**
```dockerfile
# Install Google Chrome (modern method without apt-key)
RUN wget -q -O /tmp/google-chrome-key.pub https://dl-ssl.google.com/linux/linux_signing_key.pub \
    && gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg /tmp/google-chrome-key.pub \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* /tmp/google-chrome-key.pub
```

## 📝 Изменения

1. **Добавлен пакет `gpg`** в зависимости:
   ```dockerfile
   RUN apt-get install -y --no-install-recommends \
       gnupg \
       gpg \      # ← Добавлено
       ...
   ```

2. **Заменен метод установки Chrome:**
   - Скачиваем ключ во временный файл
   - Используем `gpg --dearmor` для конвертации
   - Сохраняем в `/usr/share/keyrings/`
   - Используем `signed-by` в sources.list
   - Удаляем временный файл

## 🚀 Результат

После исправления:
- ✅ Dockerfile собирается успешно
- ✅ Chrome устанавливается корректно
- ✅ Совместимость с современными версиями Debian/Ubuntu
- ✅ Railway деплой работает

## 🔄 Как обновить

Изменения уже запушены на GitHub:
```bash
git pull origin main
```

Railway автоматически пересоберет образ при следующем деплое.

## 📚 Подробнее

- [Debian Wiki: APT Key deprecation](https://wiki.debian.org/DebianRepository/UseThirdParty)
- [Google Chrome installation guide](https://www.google.com/linuxrepositories/)

---

**Статус**: ✅ Исправлено и запушено  
**Коммит**: `0c0ade7`  
**Дата**: 2025-10-14

