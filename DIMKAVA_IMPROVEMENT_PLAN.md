# План улучшения скрапинга и сопоставления Dim Kava

## Дата: 2025-12-02
## Автор: AI Assistant
## Статус: DRAFT для обсуждения

---

## 1. АНАЛИЗ ТЕКУЩЕЙ СИТУАЦИИ

### 1.1 Выявленные проблемы

**Проблема #1: Несовпадение количества товаров**
- На сайте Dim Kava: **30 товаров** (по XPath `/html/body/div[2]/div[3]/div/div/div/ul/li[30]`)
- Скрапер собрал: **72 товара** (включая аксессуары, запчасти)
- В итоговом сравнении: только **30 товаров с ценами**

**Проблема #2: Несовпадение форматов моделей**
- На сайте Dim Kava: `DeLonghi ECAM 290.61 SB Magnifica Evo`
- В остатках: `ECAM290.61.SB`
- В скрапере извлекается: `ECAM290.61.SB` ✅ (правильно)
- Но сопоставление не работает из-за:
  - Пробелов в названиях
  - Разных форматов точек
  - Отсутствия нормализации

**Проблема #3: Структура данных остатков**
- Файл `остатки.xls` имеет сложную структуру
- Нет четких заголовков столбцов
- Данные начинаются с разных строк
- Столбцы: `Unnamed: 0, Unnamed: 1, ...`
- Название товара находится в столбце 9 (индекс 9)
- Количество в столбце 17
- Цена в столбце 18

**Проблема #4: Скрапер собирает лишние товары**
- Собираются аксессуары (питчеры, темперы)
- Собираются запчасти (ASSY, PCB, TUBE)
- Собираются товары других брендов (Melitta без моделей)

---

## 2. ДЕТАЛЬНЫЙ ПЛАН УЛУЧШЕНИЯ

### ЭТАП 1: Улучшение парсера остатков (inventory parser)
**Приоритет: КРИТИЧЕСКИЙ**
**Время: 2-3 часа**

#### 1.1 Создать специализированный парсер для остатков

```python
# utils/inventory_parser.py
class InventoryParser:
    """
    Парсер для файла остатков с учетом его специфической структуры
    """
    
    def parse_inventory_file(self, filepath: str) -> pd.DataFrame:
        """
        Парсит файл остатков и возвращает нормализованный DataFrame
        
        Returns:
            DataFrame с колонками:
            - model: нормализованная модель
            - name: полное название
            - quantity: количество
            - price: цена
            - brand: бренд (extracted)
        """
        pass
    
    def extract_model_from_inventory_name(self, name: str) -> str:
        """
        Извлекает модель из названия в остатках
        Примеры:
        - "Delonghi ECAM 290.61.B" -> "ECAM290.61.B"
        - "Delonghi ECAM290.42.TB" -> "ECAM290.42.TB"
        """
        pass
    
    def normalize_inventory_model(self, model: str) -> str:
        """
        Нормализует модель из остатков для сопоставления
        - Убирает пробелы
        - Приводит к верхнему регистру
        - Стандартизирует точки
        """
        pass
```

#### 1.2 Определить правила извлечения данных из остатков

- **Строка заголовка**: Row 4 содержит "я/я", "╩юф", "═ршьхэютрэшх ЄютрЁр"
- **Начало данных**: Row 5+
- **Столбец названия**: Column 9 (index 9)
- **Столбец количества**: Column 17 (index 17)
- **Столбец цены**: Column 18 (index 18)
- **Столбец кода**: Column 5 (index 5) - может содержать артикул

#### 1.3 Фильтрация товаров

Создать правила фильтрации:
```python
def is_valid_product(name: str) -> bool:
    """
    Проверяет, является ли товар валидным продуктом (не аксессуар, не запчасть)
    """
    # Исключить запчасти
    if any(keyword in name.upper() for keyword in [
        'ASSY', 'PCB', 'TUBE', 'FUNNEL', 'SUPPORT', 'DRAINING',
        'CARAF', 'TANK', 'PIPE', 'CONNECTOR', 'VALVE'
    ]):
        return False
    
    # Исключить мелкие аксессуары
    if any(keyword in name.upper() for keyword in [
        'PITCHER', 'TAMPER', 'SPOON', 'MAT', 'FILTER'
    ]):
        return False
    
    # Должен содержать бренд
    if not any(brand in name.upper() for brand in [
        'DELONGHI', 'DE LONGHI', 'MELITTA', 'NIVONA'
    ]):
        return False
    
    return True
```

---

### ЭТАП 2: Улучшение извлечения моделей
**Приоритет: КРИТИЧЕСКИЙ**
**Время: 2-3 часа**

#### 2.1 Расширить ModelExtractor для вариаций

```python
# utils/model_extractor.py

class ModelExtractor:
    # Добавить новые паттерны для DeLonghi
    DELONGHI_PATTERNS = [
        # С пробелами: "ECAM 290.61 SB"
        r'ECAM\s+\d+\.?\d*\.?\d*\.?\s*[A-Z]*',
        # Без пробелов: "ECAM290.61.SB"
        r'ECAM\d+\.?\d*\.?\d*\.?[A-Z]*',
        # С точками: "ECAM 290.61.SB"
        r'ECAM\s*\d+\.\d+\.\d+\.?[A-Z]*',
        # Смешанный: "ECAM290.61 SB"
        r'ECAM\d+\.\d+\s+[A-Z]+',
    ]
    
    @classmethod
    def normalize_for_matching(cls, model: str) -> str:
        """
        АГРЕССИВНАЯ нормализация для сопоставления
        
        Примеры:
        - "ECAM 290.61 SB" -> "ECAM29061SB"
        - "ECAM290.61.SB" -> "ECAM29061SB"
        - "ECAM 290.61.SB" -> "ECAM29061SB"
        
        Все варианты должны давать одинаковый результат!
        """
        if not model:
            return ""
        
        # 1. Верхний регистр
        normalized = model.upper()
        
        # 2. Убрать ВСЕ пробелы
        normalized = normalized.replace(' ', '')
        
        # 3. Убрать ВСЕ точки
        normalized = normalized.replace('.', '')
        
        # 4. Убрать дефисы
        normalized = normalized.replace('-', '')
        
        # 5. Убрать префикс DL (но не DLSC)
        if normalized.startswith('DL') and not normalized.startswith('DLSC'):
            normalized = normalized[2:]
        
        return normalized
    
    @classmethod
    def match_models_fuzzy(cls, model1: str, model2: str) -> tuple[bool, float]:
        """
        Нечеткое сопоставление моделей с оценкой уверенности
        
        Returns:
            (match: bool, confidence: float)
            
        Уровни сопоставления:
        1. Точное совпадение после нормализации -> (True, 1.0)
        2. Совпадение базовой модели (без цвета) -> (True, 0.9)
        3. Совпадение с одной буквой разницы -> (True, 0.7)
        4. Нет совпадения -> (False, 0.0)
        """
        # Уровень 1: Точное совпадение
        m1_norm = cls.normalize_for_matching(model1)
        m2_norm = cls.normalize_for_matching(model2)
        
        if m1_norm == m2_norm:
            return (True, 1.0)
        
        # Уровень 2: Базовая модель (убрать последние 1-2 буквы - цвет)
        m1_base = re.sub(r'[A-Z]{1,2}$', '', m1_norm)
        m2_base = re.sub(r'[A-Z]{1,2}$', '', m2_norm)
        
        if m1_base == m2_base and len(m1_base) >= 5:
            return (True, 0.9)
        
        # Уровень 3: Levenshtein distance = 1
        if cls._levenshtein_distance(m1_norm, m2_norm) == 1:
            return (True, 0.7)
        
        return (False, 0.0)
```

#### 2.2 Создать таблицу синонимов моделей

```python
# config/model_synonyms.py

MODEL_SYNONYMS = {
    # Ключ: нормализованная модель, Значение: список вариантов
    "ECAM29061SB": [
        "ECAM 290.61 SB",
        "ECAM290.61.SB",
        "ECAM 290.61.SB",
        "ECAM290.61 SB",
    ],
    "ECAM29042TB": [
        "ECAM 290.42 TB",
        "ECAM290.42.TB",
        "ECAM 290.42.TB",
    ],
    # ... добавить все известные вариации
}

def get_canonical_model(model: str) -> str:
    """
    Возвращает каноническую форму модели
    """
    normalized = ModelExtractor.normalize_for_matching(model)
    return normalized
```

---

### ЭТАП 3: Улучшение скрапера Dim Kava
**Приоритет: ВЫСОКИЙ**
**Время: 2-3 часа**

#### 3.1 Добавить фильтрацию при скрапинге

```python
# scrapers/dimkava/dimkava_bs4_scraper.py

class DimKavaBS4Scraper:
    
    def is_valid_product(self, name: str, price: float) -> bool:
        """
        Проверяет валидность товара
        """
        # Должна быть цена
        if not price or price < 50:
            return False
        
        # Не должно быть аксессуаров
        accessories_keywords = [
            'PITCHER', 'TAMPER', 'FILTER', 'DESCAL', 'CLEAN',
            'ПИТЧЕР', 'ТЕМПЕР', 'ФИЛЬТР'
        ]
        if any(kw in name.upper() for kw in accessories_keywords):
            return False
        
        # Должен быть бренд
        has_brand = any(brand in name.upper() for brand in [
            'DELONGHI', 'DE LONGHI', 'MELITTA', 'NIVONA'
        ])
        if not has_brand:
            return False
        
        return True
    
    def extract_model_enhanced(self, name: str) -> Optional[str]:
        """
        Улучшенное извлечение модели с множественными попытками
        """
        # Попытка 1: Стандартный экстрактор
        model = extract_model(name)
        if model:
            return model
        
        # Попытка 2: Поиск в скобках
        match = re.search(r'\(([A-Z0-9\s\.]+)\)', name)
        if match:
            potential_model = match.group(1).strip()
            if len(potential_model) >= 5:
                return potential_model
        
        # Попытка 3: Поиск после бренда
        for brand in ['DELONGHI', 'DE LONGHI', 'MELITTA', 'NIVONA']:
            if brand in name.upper():
                parts = name.upper().split(brand)
                if len(parts) > 1:
                    after_brand = parts[1].strip()
                    # Извлечь первое слово/код
                    match = re.search(r'^([A-Z0-9\s\.]+)', after_brand)
                    if match:
                        return match.group(1).strip()
        
        return None
```

#### 3.2 Добавить логирование для отладки

```python
def parse_with_bs4(self, html: str):
    """Parse with detailed logging"""
    
    # ... existing code ...
    
    for idx, (title_elem, li_elem) in enumerate(product_items, 1):
        try:
            name = title_elem.get_text(strip=True)
            
            # Log extraction process
            logger.debug(f"Processing product {idx}: {name[:50]}")
            
            # Extract model
            model = self.extract_model_enhanced(name)
            logger.debug(f"  Extracted model: {model}")
            
            # Validate
            if not self.is_valid_product(name, final_price):
                logger.debug(f"  SKIPPED: Invalid product")
                continue
            
            # ... rest of code ...
            
        except Exception as e:
            logger.error(f"Error parsing product {idx}: {e}")
            logger.error(f"  Name: {name}")
            logger.error(f"  HTML: {str(li_elem)[:200]}")
            continue
```

---

### ЭТАП 4: Улучшение сопоставления (matching)
**Приоритет: КРИТИЧЕСКИЙ**
**Время: 3-4 часа**

#### 4.1 Создать новый модуль сопоставления

```python
# utils/product_matcher_v2.py

class ProductMatcherV2:
    """
    Улучшенный матчер товаров с множественными стратегиями
    """
    
    def __init__(self, inventory_df: pd.DataFrame, scraped_df: pd.DataFrame):
        self.inventory = inventory_df
        self.scraped = scraped_df
        self.matches = []
        self.unmatched_inventory = []
        self.unmatched_scraped = []
    
    def match_products(self) -> pd.DataFrame:
        """
        Сопоставляет товары используя каскад стратегий
        """
        # Стратегия 1: Точное совпадение нормализованных моделей
        self._match_exact_models()
        
        # Стратегия 2: Нечеткое совпадение моделей (без цвета)
        self._match_fuzzy_models()
        
        # Стратегия 3: Совпадение по названию (для товаров без моделей)
        self._match_by_name()
        
        # Стратегия 4: Ручное сопоставление из таблицы синонимов
        self._match_by_synonyms()
        
        return self._build_result_dataframe()
    
    def _match_exact_models(self):
        """Точное совпадение моделей"""
        logger.info("Strategy 1: Exact model matching...")
        
        # Создать индекс нормализованных моделей
        inv_models = {}
        for idx, row in self.inventory.iterrows():
            if pd.notna(row['model']):
                norm_model = ModelExtractor.normalize_for_matching(row['model'])
                inv_models[norm_model] = row
        
        # Сопоставить со скрапленными
        for idx, row in self.scraped.iterrows():
            if pd.notna(row['model']):
                norm_model = ModelExtractor.normalize_for_matching(row['model'])
                if norm_model in inv_models:
                    self.matches.append({
                        'inventory_row': inv_models[norm_model],
                        'scraped_row': row,
                        'match_type': 'exact_model',
                        'confidence': 1.0
                    })
                    logger.info(f"  MATCH: {row['model']} <-> {inv_models[norm_model]['model']}")
    
    def _match_fuzzy_models(self):
        """Нечеткое совпадение"""
        logger.info("Strategy 2: Fuzzy model matching...")
        # ... implementation ...
    
    def _match_by_name(self):
        """Совпадение по названию"""
        logger.info("Strategy 3: Name-based matching...")
        # ... implementation ...
    
    def _match_by_synonyms(self):
        """Совпадение через таблицу синонимов"""
        logger.info("Strategy 4: Synonym-based matching...")
        # ... implementation ...
    
    def generate_match_report(self) -> str:
        """
        Генерирует отчет о сопоставлении
        """
        report = []
        report.append("="*80)
        report.append("PRODUCT MATCHING REPORT")
        report.append("="*80)
        report.append(f"Total inventory products: {len(self.inventory)}")
        report.append(f"Total scraped products: {len(self.scraped)}")
        report.append(f"Matched products: {len(self.matches)}")
        report.append(f"Unmatched inventory: {len(self.unmatched_inventory)}")
        report.append(f"Unmatched scraped: {len(self.unmatched_scraped)}")
        report.append("")
        report.append("Match breakdown by strategy:")
        # ... detailed breakdown ...
        return "\n".join(report)
```

#### 4.2 Интегрировать в main.py

```python
# main.py

def compare_prices():
    """Updated price comparison with new matcher"""
    
    # 1. Load inventory with new parser
    logger.info("Loading inventory...")
    inventory_parser = InventoryParser()
    inventory_df = inventory_parser.parse_inventory_file('data/inbox/остатки.xls')
    logger.info(f"Loaded {len(inventory_df)} products from inventory")
    
    # 2. Load scraped data
    logger.info("Loading scraped data...")
    dimkava_df = pd.read_excel('data/output/dimkava_delonghi_prices_latest.xlsx')
    logger.info(f"Loaded {len(dimkava_df)} products from Dim Kava")
    
    # 3. Match products
    logger.info("Matching products...")
    matcher = ProductMatcherV2(inventory_df, dimkava_df)
    matched_df = matcher.match_products()
    
    # 4. Generate report
    report = matcher.generate_match_report()
    logger.info(report)
    
    # 5. Save results
    matched_df.to_excel('data/output/matched_products.xlsx', index=False)
    with open('data/output/match_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
```

---

### ЭТАП 5: Создание таблицы ручных сопоставлений
**Приоритет: СРЕДНИЙ**
**Время: 1-2 часа**

#### 5.1 Создать CSV с ручными сопоставлениями

```csv
# config/manual_matches.csv
inventory_model,scraped_model,confidence,notes
ECAM290.61.SB,ECAM 290.61 SB,1.0,Space variation
ECAM290.42.TB,ECAM 290.42 TB,1.0,Space variation
EC9255.M,EC 9255 M,1.0,Space variation
...
```

#### 5.2 Загрузчик ручных сопоставлений

```python
# utils/manual_matcher.py

class ManualMatcher:
    """Loads and applies manual matches"""
    
    def __init__(self, csv_path: str = 'config/manual_matches.csv'):
        self.matches = self._load_matches(csv_path)
    
    def _load_matches(self, csv_path: str) -> dict:
        """Load manual matches from CSV"""
        if not os.path.exists(csv_path):
            return {}
        
        df = pd.read_csv(csv_path)
        matches = {}
        for _, row in df.iterrows():
            inv_norm = ModelExtractor.normalize_for_matching(row['inventory_model'])
            scr_norm = ModelExtractor.normalize_for_matching(row['scraped_model'])
            matches[scr_norm] = {
                'inventory_model': inv_norm,
                'confidence': row['confidence'],
                'notes': row.get('notes', '')
            }
        return matches
    
    def find_match(self, scraped_model: str) -> Optional[dict]:
        """Find manual match for scraped model"""
        norm = ModelExtractor.normalize_for_matching(scraped_model)
        return self.matches.get(norm)
```

---

### ЭТАП 6: Валидация и тестирование
**Приоритет: ВЫСОКИЙ**
**Время: 2-3 часа**

#### 6.1 Создать тестовый набор данных

```python
# tests/test_model_matching.py

class TestModelMatching:
    """Test cases for model matching"""
    
    def test_normalization(self):
        """Test model normalization"""
        test_cases = [
            ("ECAM 290.61 SB", "ECAM29061SB"),
            ("ECAM290.61.SB", "ECAM29061SB"),
            ("ECAM 290.61.SB", "ECAM29061SB"),
            ("EC 9255 M", "EC9255M"),
            ("EC9255.M", "EC9255M"),
        ]
        
        for input_model, expected in test_cases:
            result = ModelExtractor.normalize_for_matching(input_model)
            assert result == expected, f"Failed: {input_model} -> {result} (expected {expected})"
    
    def test_fuzzy_matching(self):
        """Test fuzzy matching"""
        test_cases = [
            ("ECAM290.61.SB", "ECAM 290.61 SB", True, 1.0),
            ("EC9255.M", "EC9255.T", True, 0.9),  # Color variant
            ("ECAM290.61", "ECAM290.81", False, 0.0),  # Different model
        ]
        
        for model1, model2, expected_match, expected_conf in test_cases:
            match, conf = ModelExtractor.match_models_fuzzy(model1, model2)
            assert match == expected_match
            assert abs(conf - expected_conf) < 0.1
```

#### 6.2 Создать скрипт валидации

```python
# validate_matching.py

def validate_matching():
    """Validate matching results"""
    
    # Load results
    matched_df = pd.read_excel('data/output/matched_products.xlsx')
    
    # Statistics
    print("="*80)
    print("VALIDATION REPORT")
    print("="*80)
    
    # Check for duplicates
    duplicates = matched_df[matched_df.duplicated(subset=['model'], keep=False)]
    if len(duplicates) > 0:
        print(f"WARNING: Found {len(duplicates)} duplicate matches!")
        print(duplicates[['model', 'name']])
    
    # Check for missing prices
    missing_prices = matched_df[matched_df['price'].isna()]
    if len(missing_prices) > 0:
        print(f"WARNING: Found {len(missing_prices)} products without prices!")
    
    # Check model format consistency
    invalid_models = matched_df[~matched_df['model'].str.match(r'^[A-Z]{2,}[0-9]')]
    if len(invalid_models) > 0:
        print(f"WARNING: Found {len(invalid_models)} products with invalid model format!")
    
    print("="*80)
```

---

### ЭТАП 7: Документация и мониторинг
**Приоритет: СРЕДНИЙ**
**Время: 1-2 часа**

#### 7.1 Создать документацию

```markdown
# docs/MATCHING_GUIDE.md

# Product Matching Guide

## Overview
This document describes how product matching works between inventory and scraped data.

## Model Normalization Rules

1. Convert to uppercase
2. Remove all spaces
3. Remove all dots
4. Remove hyphens
5. Remove DL prefix (except DLSC)

Examples:
- "ECAM 290.61 SB" -> "ECAM29061SB"
- "EC 9255 M" -> "EC9255M"

## Matching Strategies

### Strategy 1: Exact Model Match
- Normalize both models
- Compare for exact equality
- Confidence: 1.0

### Strategy 2: Fuzzy Model Match
- Remove color suffix (last 1-2 letters)
- Compare base models
- Confidence: 0.9

### Strategy 3: Name-based Match
- For products without models
- Use fuzzy string matching
- Confidence: 0.6-0.8

### Strategy 4: Manual Synonyms
- Load from manual_matches.csv
- Override automatic matching
- Confidence: as specified in CSV

## Adding New Matches

To add a new manual match:
1. Edit `config/manual_matches.csv`
2. Add row: inventory_model, scraped_model, confidence, notes
3. Run matching again

## Troubleshooting

### Product not matching?
1. Check model extraction: Is model extracted correctly?
2. Check normalization: Do both models normalize to same string?
3. Add manual match if needed

### Too many false matches?
1. Increase confidence threshold
2. Add exclusion rules
3. Refine fuzzy matching logic
```

#### 7.2 Создать скрипт мониторинга

```python
# monitor_matching.py

def monitor_matching_quality():
    """Monitor matching quality over time"""
    
    # Load historical data
    history = []
    for file in glob.glob('data/output/matched_products_*.xlsx'):
        df = pd.read_excel(file)
        date = extract_date_from_filename(file)
        history.append({
            'date': date,
            'total_matched': len(df),
            'avg_confidence': df['match_confidence'].mean(),
            'exact_matches': len(df[df['match_type'] == 'exact_model']),
            'fuzzy_matches': len(df[df['match_type'] == 'fuzzy_model']),
        })
    
    # Plot trends
    history_df = pd.DataFrame(history)
    history_df.plot(x='date', y=['total_matched', 'exact_matches', 'fuzzy_matches'])
    plt.savefig('data/output/matching_quality_trend.png')
    
    # Alert if quality drops
    if history_df['avg_confidence'].iloc[-1] < 0.8:
        logger.warning("ALERT: Matching confidence dropped below 0.8!")
```

---

## 3. ПЛАН РЕАЛИЗАЦИИ (TIMELINE)

### ✅ ВЫПОЛНЕНО (2025-12-02)

**ЭТАП 1: Парсер остатков** ✅
- ✅ Создан InventoryParser
- ✅ Извлечение моделей из остатков (51.3% успех)
- ✅ Фильтрация валидных товаров (91 из 1383)
- ✅ Определение брендов
- Время: ~2 часа

**ЭТАП 2: Улучшение моделей** ✅
- ✅ Улучшенная нормализация моделей
- ✅ Fuzzy matching с уверенностью (1.0, 0.9, 0.7)
- ✅ Levenshtein distance для опечаток
- ✅ Таблица синонимов (15 записей)
- ✅ EnhancedMatcher с 4 стратегиями
- Результат: 25 → **29 совпадений** (+16%)
- Время: ~2 часа

**ЭТАП 3: Улучшение скрапера Dim Kava** ✅
- ✅ Улучшенная прокрутка для WordPress (3s паузы, 25 прокруток)
- ✅ Агрессивная стратегия lazy loading
- ✅ Фильтрация аксессуаров (16 товаров)
- ✅ Фильтрация запчастей
- ✅ Валидация товаров
- ✅ Улучшенное извлечение моделей (3 стратегии)
- Результат: 59 → **42 валидных товара** (-28.8% мусора)
- Время: ~2 часа

### ⏳ В ПРОЦЕССЕ

**ЭТАП 4: Интеграция в main pipeline** (следующий)
- ⏳ Интегрировать InventoryParser в main.py
- ⏳ Интегрировать EnhancedMatcher в compare_prices.py
- ⏳ Обновить итоговый отчет
- ⏳ Протестировать полный цикл

### 📅 ЗАПЛАНИРОВАНО

**ЭТАП 5: Ручные сопоставления**
- Расширить таблицу синонимов
- Добавить name-based matching
- Создать UI для ручного сопоставления

**ЭТАП 6: Валидация**
- Создать тестовый набор данных
- Автоматические тесты
- Скрипт валидации

**ЭТАП 7: Документация и мониторинг**
- Полная документация
- Скрипт мониторинга качества
- Алерты при проблемах

---

## 4. МЕТРИКИ УСПЕХА

### Текущее состояние
- Сопоставлено: ~30 товаров
- Точность: ~60-70%
- Ручная работа: высокая

### Целевые показатели
- Сопоставлено: 90%+ товаров из остатков
- Точность: 95%+
- Автоматизация: 95%+
- Ручная работа: минимальная (только новые товары)

### KPI
1. **Match Rate**: % товаров из остатков, которые нашли пару в скрапленных данных
   - Текущий: ~40%
   - Цель: 90%+

2. **Precision**: % правильных сопоставлений из всех сопоставлений
   - Текущий: ~70%
   - Цель: 95%+

3. **Recall**: % товаров из остатков, которые должны были найти пару и нашли
   - Текущий: ~60%
   - Цель: 90%+

4. **Confidence Score**: Средняя уверенность в сопоставлениях
   - Текущий: ~0.7
   - Цель: 0.9+

---

## 5. РИСКИ И МИТИГАЦИЯ

### Риск 1: Изменение структуры остатков
**Вероятность**: Средняя
**Влияние**: Высокое
**Митигация**: 
- Версионирование парсера
- Автоматическое обнаружение изменений структуры
- Алерты при ошибках парсинга

### Риск 2: Новые форматы моделей
**Вероятность**: Высокая
**Влияние**: Среднее
**Митигация**:
- Расширяемая система паттернов
- Логирование нераспознанных форматов
- Регулярное обновление паттернов

### Риск 3: Ложные сопоставления
**Вероятность**: Средняя
**Влияние**: Высокое
**Митигация**:
- Множественные стратегии с разной уверенностью
- Ручная валидация низкоуверенных сопоставлений
- Blacklist для известных ложных срабатываний

### Риск 4: Производительность
**Вероятность**: Низкая
**Влияние**: Среднее
**Митигация**:
- Индексирование нормализованных моделей
- Кэширование результатов нормализации
- Параллельная обработка при необходимости

---

## 6. СЛЕДУЮЩИЕ ШАГИ

### Немедленные действия (сегодня)
1. ✅ Проанализировать структуру остатков
2. ⏳ Создать парсер остатков (InventoryParser)
3. ⏳ Протестировать извлечение моделей из остатков

### Краткосрочные (эта неделя)
1. Реализовать улучшенную нормализацию моделей
2. Создать тестовый набор данных
3. Реализовать базовый матчер v2

### Среднесрочные (следующие 2 недели)
1. Полная реализация всех стратегий сопоставления
2. Интеграция в основной pipeline
3. Создание документации

### Долгосрочные (месяц)
1. Мониторинг качества
2. Оптимизация производительности
3. Расширение на другие бренды

---

## 7. ВОПРОСЫ ДЛЯ ОБСУЖДЕНИЯ

1. **Приоритеты**: Согласны ли вы с предложенными приоритетами этапов?

2. **Ручные сопоставления**: Готовы ли вы поддерживать CSV файл с ручными сопоставлениями?

3. **Валидация**: Кто будет валидировать результаты сопоставления?

4. **Обновления**: Как часто обновляется файл остатков?

5. **Новые товары**: Какой процесс для добавления новых товаров?

---

## ЗАКЛЮЧЕНИЕ

Этот план обеспечивает:
- ✅ Систематический подход к решению проблемы
- ✅ Не ломает существующие механизмы (создаем новые модули)
- ✅ Постепенное внедрение (по этапам)
- ✅ Возможность отката (старые модули остаются)
- ✅ Тестирование на каждом этапе
- ✅ Документация для поддержки
- ✅ Мониторинг качества

**Готов начать реализацию с любого этапа по вашему выбору!**

