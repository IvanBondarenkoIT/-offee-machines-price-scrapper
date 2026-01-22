# 🚀 Быстрая настройка WooCommerce ключей

## ⚠️ ВАЖНО: Безопасность

Файл `.env` уже в `.gitignore` и **НЕ попадет в Git**.  
Ключи останутся только локально на вашем компьютере.

---

## 📋 Способ 1: Создать .env файл вручную (РЕКОМЕНДУЕТСЯ)

Создайте файл `.env` в корне проекта со следующим содержимым:

```env
# WooCommerce API (для экспорта данных)
WC_URL=https://dimkava.ge
WC_CONSUMER_KEY=ck_ваш_ключ_здесь
WC_CONSUMER_SECRET=cs_ваш_секрет_здесь
WC_API_VERSION=wc/v3
```

**Где взять ключи:**
1. Войти в админ-панель: `dimkava.ge/wp-admin`
2. WooCommerce → Settings → Advanced → REST API
3. Создать новый ключ или использовать существующий
4. Скопировать Consumer Key и Consumer Secret

---

## 📋 Способ 2: PowerShell скрипт

```powershell
.\create_env_file.ps1 -Key "ck_ваш_ключ" -Secret "cs_ваш_секрет"
```

Или с полными параметрами:
```powershell
.\create_env_file.ps1 -Url "https://dimkava.ge" -Key "ck_..." -Secret "cs_..." -ApiVersion "wc/v3"
```

---

## ✅ Проверка

После создания `.env` файла запустите тест:

```bash
python test_woocommerce_client.py
```

---

## 🔒 Безопасность

- ✅ `.env` файл в `.gitignore`
- ✅ Ключи не попадут в Git
- ✅ Файл остается только локально
- ✅ Можно безопасно коммитить другие изменения

---

## 🧪 После настройки

Если тест пройдет успешно:
1. ✅ Клиент работает корректно
2. ✅ Можно переходить к этапу 2
3. ✅ Данные получаются из WooCommerce API
