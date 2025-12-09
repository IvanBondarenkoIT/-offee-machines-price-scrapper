# 🔧 ТОЧНЫЕ ИСПРАВЛЕНИЯ для CoffeeHub и Kontakt

**Дата**: 9 декабря 2025  
**Проблема**: Неправильные цены со скидками  

---

## 1️⃣ COFFEEHUB - Исправление

### Файл: `scrapers/coffeehub/coffeehub_bs4_scraper.py`

### 🔍 Проблема:
- URL: `https://coffeehub.ge/shop/?s=Delonghi&post_type=product` → **404 ERROR**
- Цены: Берет старую цену 3,359 GEL вместо скидочной 2,259 GEL

### ✅ Решение:

#### A) Исправить URL в `config.py`:

```python
# БЫЛО:
COFFEEHUB_CONFIG = {
    "urls": [
        "https://coffeehub.ge/shop/?s=Delonghi&post_type=product",
        "https://coffeehub.ge/shop/?s=Melitta&post_type=product",
    ],
    "pages_per_url": 2,
    "expected_products": 50,
    "pagination_url": "&paged={page_num}",
}

# СТАЛО:
COFFEEHUB_CONFIG = {
    "urls": [
        "https://coffeehub.ge/product-category/coffee-machines/",
    ],
    "pages_per_url": 13,  # 151 товар / 12 на странице
    "expected_products": 50,
    "pagination_url": "page/{page_num}/",  # Новый формат: page/2/
}
```

#### B) Исправить логику цен в методе `scrape_page()`:

**НАЙТИ (примерно строки 143-176):**
```python
# Look for prices
price_element = None
price_text = None

# Try different price selectors
price_selectors = [...]

for selector in price_selectors:
    price_element = product.select_one(selector)
    if price_element:
        price_text = price_element.get_text(strip=True)
        break

if not price_text:
    continue

# Extract price numbers
price_match = re.search(r'([\d,]+\.?\d*)', price_text.replace(',', ''))
if not price_match:
    continue

price = float(price_match.group(1))

# Look for discount price
discount_price = None
discount_element = product.find(['del', 's'], class_=lambda x: x and 'price' in x.lower())
if discount_element:
    discount_text = discount_element.get_text(strip=True)
    discount_match = re.search(r'([\d,]+\.?\d*)', discount_text.replace(',', ''))
    if discount_match:
        discount_price = float(discount_match.group(1))
```

**ЗАМЕНИТЬ НА:**
```python
# Look for sale price and old price FIRST
# ВАЖНО: <ins> = финальная цена (со скидкой), <del> = старая цена
sale_price = None
old_price = None
final_price = None

# Шаг 1: Проверяем <ins> (цена со скидкой)
ins_element = product.find('ins')
if ins_element:
    ins_text = ins_element.get_text(strip=True)
    ins_match = re.search(r'([\d,]+\.?\d*)', ins_text.replace(',', ''))
    if ins_match:
        sale_price = float(ins_match.group(1))
        final_price = sale_price  # Это финальная цена!
        
        # Также получаем старую цену из <del>
        del_element = product.find(['del', 's'])
        if del_element:
            del_text = del_element.get_text(strip=True)
            del_match = re.search(r'([\d,]+\.?\d*)', del_text.replace(',', ''))
            if del_match:
                old_price = float(del_match.group(1))

# Шаг 2: Если нет <ins>, берем обычную цену
if final_price is None:
    price_element = product.select_one('.price')
    if not price_element:
        # Try other selectors
        for selector in ['.woocommerce-Price-amount', '[class*="price"]']:
            price_element = product.select_one(selector)
            if price_element:
                break
    
    if price_element:
        price_text = price_element.get_text(strip=True)
        price_match = re.search(r'([\d,]+\.?\d*)', price_text.replace(',', ''))
        if price_match:
            final_price = float(price_match.group(1))

# Шаг 3: Если цена не найдена - пропускаем
if final_price is None:
    continue
```

#### C) Обновить структуру product_data:

**НАЙТИ:**
```python
product_data = {
    'name': name,
    'price': price,
    'discount_price': discount_price,
    'url': product_url,
    'source': 'COFFEEHUB',
    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}
```

**ЗАМЕНИТЬ НА:**
```python
product_data = {
    'name': name,
    'price': final_price,  # Финальная цена (с учетом скидки)
    'old_price': old_price,  # Старая цена (если была)
    'sale_price': sale_price,  # Цена со скидкой (если есть)
    'url': product_url,
    'source': 'COFFEEHUB',
    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}
```

#### D) Обновить логирование:

**НАЙТИ:**
```python
logger.info(f"Found DeLonghi product: {clean_name} - {price}")
```

**ЗАМЕНИТЬ НА:**
```python
if sale_price:
    logger.info(f"Found product: {clean_name} - {final_price} GEL (was {old_price} GEL)")
else:
    logger.info(f"Found product: {clean_name} - {final_price} GEL")
```

#### E) Добавить дедупликацию в метод `scrape_all_pages()`:

**НАЙТИ (конец метода, после сбора всех товаров):**
```python
logger.info(f"Total products scraped: {len(self.products)}")
```

**ЗАМЕНИТЬ НА:**
```python
logger.info(f"Total products scraped (with duplicates): {len(self.products)}")

# Удаляем дубликаты
unique_products = []
seen = set()
for product in self.products:
    key = (product['name'].lower().strip(), product['price'])
    if key not in seen:
        seen.add(key)
        unique_products.append(product)

self.products = unique_products
logger.info(f"Total unique products: {len(self.products)}")
```

---

## 2️⃣ KONTAKT - Исправление

### Файл: `scrapers/kontakt/kontakt_bs4_scraper.py`

### 🔍 Проблема:
- Тостеры со скидками: берет 329.99 вместо 229.99

### 🎯 Структура Kontakt:
- `<strong><i>` = **обычная/старая** цена (329.99)
- `<strong><b>` = **цена со скидкой** (229.99) - ФИНАЛЬНАЯ!

### ✅ Решение:

**НАЙТИ в методе `parse_with_bs4()` (примерно строки 167-213):**

```python
# Extract prices from strong > i or strong > b
# IMPORTANT: There can be multiple prices (regular + discount)
all_prices = []

strong_tags = price_container.find_all('strong')
for strong in strong_tags:
    # Try i tag first
    i_tag = strong.find('i')
    if i_tag:
        price_text = i_tag.get_text(strip=True)
        if re.search(r'\d{2,}', price_text):
            all_prices.append(price_text)
    
    # Try b tag
    b_tag = strong.find('b')
    if b_tag:
        price_text = b_tag.get_text(strip=True)
        if re.search(r'\d{2,}', price_text):
            all_prices.append(price_text)

# Determine regular and discount prices
regular_price = None
discount_price = None

if len(all_prices) >= 2:
    # Multiple prices = first is regular, last is discount (final)
    regular_price = self.clean_price(all_prices[0])
    discount_price = self.clean_price(all_prices[-1])
elif len(all_prices) == 1:
    # Single price = no discount
    regular_price = self.clean_price(all_prices[0])
    discount_price = None
```

**ЗАМЕНИТЬ НА:**

```python
# Extract prices - KONTAKT specific structure
# <strong><i> = обычная/старая цена
# <strong><b> = цена со скидкой (ФИНАЛЬНАЯ!)
regular_price = None
discount_price = None

strong_tags = price_container.find_all('strong')

# Собираем <i> и <b> отдельно
i_prices = []
b_prices = []

for strong in strong_tags:
    # <i> tag = regular/old price
    i_tag = strong.find('i')
    if i_tag:
        price_text = i_tag.get_text(strip=True)
        if re.search(r'\d{2,}', price_text):
            i_prices.append(price_text)
    
    # <b> tag = discount/sale price (FINAL!)
    b_tag = strong.find('b')
    if b_tag:
        price_text = b_tag.get_text(strip=True)
        if re.search(r'\d{2,}', price_text):
            b_prices.append(price_text)

# Если есть <b>, это финальная цена со скидкой
if b_prices:
    discount_price = self.clean_price(b_prices[0])
    # <i> это старая цена
    if i_prices:
        regular_price = self.clean_price(i_prices[0])
# Если только <i>, это обычная цена (без скидки)
elif i_prices:
    regular_price = self.clean_price(i_prices[0])
    discount_price = None
```

**ТАКЖЕ УДАЛИТЬ СТРОКУ (если есть):**
```python
'all_prices_found': all_prices,  # For debugging
```

И заменить условие добавления продукта:
```python
# БЫЛО:
if regular_price:

# СТАЛО:
if regular_price or discount_price:
```

---

## 🧪 ТЕСТИРОВАНИЕ

### CoffeeHub:
```bash
python scrapers/coffeehub/coffeehub_bs4_scraper.py
```
**Ожидаем**: ~29 уникальных товаров (DeLonghi + Melitta)

### Kontakt:
```bash
python scrapers/kontakt/kontakt_bs4_scraper.py
```
**Ожидаем**: 
- Coffee machines: ~23 товара
- Toasters: 2 товара (оба со скидками 229.99 и 199.99)

---

## ⚠️ ВАЖНО:

**НЕ ТРОГАТЬ ДРУГИЕ СКРАПЕРЫ!**
- ALTA - работает правильно
- ELITE - работает правильно
- COFFEEPIN - работает правильно
- DIMKAVA - работает правильно

Изменения **ТОЛЬКО** в:
1. `config.py` (URL CoffeeHub)
2. `scrapers/coffeehub/coffeehub_bs4_scraper.py` (логика цен)
3. `scrapers/kontakt/kontakt_bs4_scraper.py` (логика цен)

---

## ✅ РЕЗУЛЬТАТ:

После исправлений:
- CoffeeHub: цены со скидками правильные (2,259 вместо 3,359)
- Kontakt: цены со скидками правильные (229.99 вместо 329.99)
- Остальные скраперы: **НЕ ТРОНУТЫ**

---

*Документ создан: 9 декабря 2025*  
*Только локальные изменения в 2 скраперах*

