# 🔴 КРИТИЧЕСКИЕ ПРАВИЛА - НЕ НАРУШАТЬ

## ⚠️ ЧТО НЕЛЬЗЯ ТРОГАТЬ

### 1. `run_full_cycle.py` - ЗАПРЕЩЕНО ИЗМЕНЯТЬ
- Запускает все 8 скраперов последовательно
- Вызывает `build_price_comparison.py`
- Показывает результаты
- **ЛЮБЫЕ ИЗМЕНЕНИЯ ЗАПРЕЩЕНЫ**

### 2. Все скраперы в `scrapers/` - ЗАПРЕЩЕНО ИЗМЕНЯТЬ
- `scrapers/alta/alta_bs4_scraper.py`
- `scrapers/kontakt/kontakt_bs4_scraper.py`
- `scrapers/elite/elite_bs4_scraper.py`
- `scrapers/dimkava/dimkava_bs4_scraper.py`
- `scrapers/coffeehub/coffeehub_bs4_scraper.py`
- `scrapers/coffeepin/coffeepin_bs4_scraper.py`
- `scrapers/veli_store/veli_store_bs4_scraper.py`
- `scrapers/vega_ge/vega_ge_bs4_scraper.py`
- **ЛЮБЫЕ ИЗМЕНЕНИЯ ЗАПРЕЩЕНЫ**

### 3. `build_price_comparison.py` - МОЖНО ИЗМЕНЯТЬ ТОЛЬКО ОЧЕНЬ АККУРАТНО
- Используется в `run_full_cycle.py`
- Генерирует Excel с колонками: ALTA, KONTAKT, ELITE, DIM_KAVA, etc.
- **ИЗМЕНЕНИЯ ТОЛЬКО ДЛЯ ДОБАВЛЕНИЯ WooCommerce КОЛОНОК, БЕЗ ЛОМАНИЯ СУЩЕСТВУЮЩЕЙ ЛОГИКИ**

### 4. Веб-приложение `web_app/` - ОСТОРОЖНО
- Используется для деплоя на Railway
- Работает стабильно
- **ИЗМЕНЕНИЯ ТОЛЬКО ПОСЛЕ ТЕСТИРОВАНИЯ**

---

## ✅ ЧТО МОЖНО ДЕЛАТЬ

### 1. Создать новый файл `export_woocommerce_data.py`
- Отдельный скрипт для экспорта WooCommerce данных
- НЕ вызывается из `run_full_cycle.py`
- Можно запускать отдельно

### 2. Создать `utils/woocommerce_client.py`
- Клиент для WooCommerce API
- Используется только в `export_woocommerce_data.py`
- НЕ влияет на существующий код

### 3. Добавить WooCommerce колонки в `build_price_comparison.py` (ОПЦИОНАЛЬНО)
- Только если нужно интегрировать в основной Excel
- ТОЛЬКО после тестирования отдельного экспорта
- БЕЗ изменения существующей логики

---

## 🎯 ПРИНЦИПЫ РАБОТЫ

1. **Тестирование каждого этапа** - перед переходом к следующему
2. **Откат при проблемах** - использовать тег `stable-before-woocommerce`
3. **Минимальные изменения** - только то, что необходимо
4. **Изоляция** - WooCommerce код отдельно от основного

---

## 📍 ТОЧКА ОТКАТА

**Тег:** `stable-before-woocommerce`  
**Коммит:** `36e36cb` (Merge pull request #26)  
**Команда отката:**
```bash
git checkout stable-before-woocommerce
git checkout -b main  # если нужно вернуться на main
```
