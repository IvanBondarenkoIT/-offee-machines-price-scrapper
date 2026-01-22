# Чеклист для деплоя

## ✅ Выполнено

- [x] Все скраперы работают
- [x] Полный цикл парсинга работает
- [x] Загрузка на фронтенд работает
- [x] Веб-приложение развернуто на Railway
- [x] WooCommerce клиент создан
- [x] Экспорт WooCommerce данных работает

## 📋 Следующие шаги

### 1. Интеграция WooCommerce в основной цикл
- [ ] Добавить загрузку WooCommerce данных в `build_price_comparison.py`
- [ ] Добавить колонки `DIM_KAVA_STOCK` и `DIM_KAVA_WC_PRICE` в Excel
- [ ] Обновить матчинг для WooCommerce продуктов

### 2. Обновление фронтенда для WooCommerce
- [ ] Обновить `web_app/models/product.py` (добавить поле `dimkava_wc_stock`)
- [ ] Обновить `web_app/services/upload_service.py` (парсинг WooCommerce столбцов)
- [ ] Обновить `web_app/services/comparison_service.py` (исключение DIM_KAVA_WC)
- [ ] Обновить `web_app/templates/comparison/index.html` (столбцы WC Stock и WC Price)

### 3. Миграция БД (после обновления моделей)
После обновления моделей нужно выполнить миграцию БД:

**Вариант 1: Использовать Flask-Migrate (если настроен)**
```bash
flask db migrate -m "Add dimkava_wc_stock field"
flask db upgrade
```

**Вариант 2: Ручная миграция SQL**
```sql
ALTER TABLE products ADD COLUMN dimkava_wc_stock INTEGER DEFAULT NULL;
```

**Вариант 3: Если БД пустая - использовать db.create_all()**
```python
from web_app.database import db
from web_app.app import create_app

app = create_app()
with app.app_context():
    db.create_all()
```

### 4. Настройка переменных окружения на Railway
После деплоя нужно добавить в Railway:
- `WC_URL=https://dimkava.ge`
- `WC_CONSUMER_KEY=ck_...`
- `WC_CONSUMER_SECRET=cs_...`
- `WC_API_VERSION=wc/v3` (опционально)
- `WC_TIMEOUT=30` (опционально)

### 5. Тестирование на продакшене
1. Запустить полный цикл с WooCommerce
2. Загрузить Excel файл через `upload_data.py`
3. Проверить отображение в веб-интерфейсе
4. Проверить обратную совместимость (файлы без WooCommerce столбцов)

## 📝 Важные замечания

1. **Обратная совместимость**: Веб-приложение работает с файлами БЕЗ WooCommerce полей (показывает "-")
2. **Graceful degradation**: Если WooCommerce API недоступен, приложение продолжает работать без WooCommerce данных
3. **Новые поля опциональны**: Если `DIM_KAVA_STOCK` или `DIM_KAVA_WC_PRICE` отсутствуют - показывается "-"

## 🔍 Проверка после деплоя

- [ ] Excel файлы с WooCommerce столбцами загружаются без ошибок
- [ ] Столбцы "WC Stock" и "WC Price" отображаются в таблице сравнения
- [ ] Данные сохраняются в БД (проверить через админ-панель или SQL запрос)
- [ ] Файлы без WooCommerce столбцов обрабатываются корректно
- [ ] Экспорт в Excel включает WooCommerce столбцы
