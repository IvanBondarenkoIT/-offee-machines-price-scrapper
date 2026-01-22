# 🔄 Git Workflow: Поэтапные коммиты

## ✅ ТЕКУЩИЙ СТАТУС

**Ветка:** `feature/woocommerce-export-module`  
**Этап 1:** ✅ Закоммичен (2 коммита)  
**Тег:** `stage1-woocommerce-client` создан

---

## 📋 ПЛАН КОММИТОВ ПО ЭТАПАМ

### ✅ ЭТАП 1: WooCommerce клиент (ЗАВЕРШЕН)

**Коммит 1:** `addb8fa` - WooCommerce API client  
**Коммит 2:** `167dcad` - Test suite and documentation  
**Тег:** `stage1-woocommerce-client`

**Статус:** ✅ Готово к пушу на GitHub

---

### ⏳ ЭТАП 2: Экспорт-скрипт (СЛЕДУЮЩИЙ)

**План коммита:**
```bash
git add export_woocommerce_data.py
git commit -m "feat: add WooCommerce data export script

- Create export_woocommerce_data.py for standalone export
- Export to Excel with format: woocommerce_export_YYYYMMDD_HHMMSS.xlsx
- Columns: Model, Name, Price, Stock, URL
- Part of Stage 2: Export script creation"

git tag -a stage2-export-script -m "Stage 2 complete: Export script created"
```

**После коммита:** Запушить на GitHub

---

### ⏳ ЭТАП 3: Интеграция в build_price_comparison.py

**План коммитов (2 коммита):**

**Коммит 1:** Загрузка WooCommerce данных
```bash
git add build_price_comparison.py
git commit -m "feat: integrate WooCommerce stock data loading

- Add load_woocommerce_stock() method
- Add woocommerce_stock attribute
- Optional loading with graceful degradation
- Part of Stage 3: WooCommerce integration"
```

**Коммит 2:** Добавление колонок
```bash
git add build_price_comparison.py
git commit -m "feat: add DIM_KAVA_STOCK and DIM_KAVA_WC_PRICE columns

- Add WooCommerce columns to comparison table
- Support stock quantity and price display
- Handle discount format (regular \\ discount)
- Part of Stage 3: Table columns integration"

git tag -a stage3-integration -m "Stage 3 complete: Integration with build_price_comparison"
```

**После коммитов:** Запушить на GitHub

---

### ⏳ ЭТАП 4: Интеграция в веб-приложение (ОПЦИОНАЛЬНО)

**План коммитов (3 коммита):**

**Коммит 1:** Модели БД
```bash
git add web_app/models/product.py
git commit -m "feat: add dimkava_wc_stock field to Product model"
```

**Коммит 2:** Сервисы
```bash
git add web_app/services/upload_service.py web_app/services/comparison_service.py
git commit -m "feat: add WooCommerce data parsing and display"
```

**Коммит 3:** UI
```bash
git add web_app/templates/comparison/index.html
git commit -m "feat: add WooCommerce columns to comparison UI"

git tag -a stage4-web-app -m "Stage 4 complete: Web app integration"
```

---

## 🚀 КОМАНДЫ ДЛЯ ПУША НА GITHUB

### После каждого этапа:

```bash
# Проверить статус
git status

# Посмотреть коммиты
git log --oneline -5

# Запушить ветку
git push origin feature/woocommerce-export-module

# Запушить теги
git push origin --tags
```

### Создать Pull Request:

После каждого этапа можно создать PR для ревью:
1. Перейти на GitHub
2. Создать PR из `feature/woocommerce-export-module` в `main`
3. Указать номер этапа в описании

---

## ⚠️ ВАЖНЫЕ ПРАВИЛА

1. **НЕ коммитить `.env`** - он в .gitignore
2. **Тестировать перед коммитом** - убедиться что работает
3. **Маленькие коммиты** - один этап = один/несколько логических коммитов
4. **Теги для этапов** - создавать тег после завершения этапа
5. **Пуш после каждого этапа** - чтобы не потерять работу

---

## 🔄 ОТКАТ ПРИ ПРОБЛЕМАХ

### Откатиться к предыдущему этапу:

```bash
# По тегу
git checkout stage1-woocommerce-client

# По коммиту
git checkout addb8fa

# Создать новую ветку от этапа
git checkout -b fix-stage2 stage1-woocommerce-client
```

### Откатить последний коммит (если еще не запушен):

```bash
git reset --soft HEAD~1  # Сохранить изменения
git reset --hard HEAD~1  # Удалить изменения
```

---

## 📊 ТЕКУЩИЙ ПРОГРЕСС

- ✅ **Этап 1:** Закоммичен (2 коммита, 1 тег)
- ⏳ **Этап 2:** Следующий
- ⏳ **Этап 3:** Ожидает
- ⏳ **Этап 4:** Ожидает

---

## ✅ ГОТОВО К ПУШУ ЭТАПА 1

Сейчас можно запушить Этап 1 на GitHub:

```bash
git push origin feature/woocommerce-export-module
git push origin --tags
```
