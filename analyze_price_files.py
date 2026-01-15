"""
Анализ Excel файлов из data/inbox для выявления ошибок и неточностей
Файлы: price frome Natia alta.xlsx и price frome Natia elit.xlsx
"""

import pandas as pd
from pathlib import Path
import sys

def analyze_file(file_path: Path, file_name: str):
    """Анализ одного Excel файла на наличие ошибок"""
    print(f"\n{'='*80}")
    print(f"АНАЛИЗ: {file_name}")
    print(f"{'='*80}")
    
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        print(f"\n[ИНФО] ОСНОВНАЯ ИНФОРМАЦИЯ:")
        print(f"  Размер: {df.shape[0]} строк x {df.shape[1]} столбцов")
        print(f"  Столбцы: {list(df.columns)}")
        
        # Show first few rows
        print(f"\n[ИНФО] ПЕРВЫЕ 5 СТРОК:")
        print(df.head().to_string())
        
        # Check for common issues
        print(f"\n[ПРОВЕРКА] ПРОВЕРКА НА ОШИБКИ:")
        
        # 1. Missing values
        missing = df.isnull().sum()
        if missing.sum() > 0:
            print(f"  [ПРЕДУПРЕЖДЕНИЕ] Пропущенные значения:")
            for col, count in missing.items():
                if count > 0:
                    print(f"     - {col}: {count} пропущено ({count/len(df)*100:.1f}%)")
        else:
            print(f"  [OK] Нет пропущенных значений")
        
        # 2. Duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            print(f"  [ПРЕДУПРЕЖДЕНИЕ] Дублирующиеся строки: {duplicates}")
        else:
            print(f"  [OK] Нет дублирующихся строк")
        
        # 3. Price columns analysis
        price_cols = [col for col in df.columns if 'price' in col.lower() or 'цена' in col.lower()]
        if price_cols:
            print(f"\n[ЦЕНЫ] АНАЛИЗ ЦЕН:")
            for col in price_cols:
                if df[col].dtype in ['float64', 'int64']:
                    print(f"  {col}:")
                    print(f"    - Мин: {df[col].min()}")
                    print(f"    - Макс: {df[col].max()}")
                    print(f"    - Среднее: {df[col].mean():.2f}")
                    print(f"    - Нулевые/отрицательные: {(df[col] <= 0).sum()}")
                    print(f"    - Пропущено: {df[col].isnull().sum()}")
                else:
                    # Try to extract numeric values
                    print(f"  {col} (текст):")
                    print(f"    - Примеры значений: {df[col].head(3).tolist()}")
        
        # 4. Product name analysis
        name_cols = [col for col in df.columns if 'name' in col.lower() or 'название' in col.lower() or 'product' in col.lower() or 'товар' in col.lower() or 'column1' in col.lower()]
        if name_cols:
            print(f"\n[ТОВАРЫ] АНАЛИЗ НАЗВАНИЙ ТОВАРОВ:")
            for col in name_cols:
                print(f"  {col}:")
                print(f"    - Всего: {len(df[col])}")
                print(f"    - Уникальных: {df[col].nunique()}")
                print(f"    - Пропущено: {df[col].isnull().sum()}")
                print(f"    - Пустых строк: {(df[col].astype(str).str.strip() == '').sum()}")
                # Check for DeLonghi
                if df[col].dtype == 'object':
                    delonghi_count = df[col].astype(str).str.contains('delonghi', case=False, na=False).sum()
                    print(f"    - Содержит 'DeLonghi': {delonghi_count}")
        
        # 5. Data types
        print(f"\n[ТИПЫ] ТИПЫ ДАННЫХ:")
        for col, dtype in df.dtypes.items():
            print(f"  {col}: {dtype}")
        
        # 6. Show all data if small
        if len(df) <= 20:
            print(f"\n[ДАННЫЕ] ВСЕ ДАННЫЕ:")
            print(df.to_string())
        
        return df
        
    except Exception as e:
        print(f"  [ОШИБКА] Ошибка при чтении файла: {e}")
        import traceback
        traceback.print_exc()
        return None

def compare_files(alta_df, elite_df):
    """Сравнение файлов Alta и Elite для выявления расхождений"""
    print(f"\n{'='*80}")
    print("СРАВНЕНИЕ: ALTA vs ELITE")
    print(f"{'='*80}")
    
    if alta_df is None or elite_df is None:
        print("  [ПРЕДУПРЕЖДЕНИЕ] Невозможно сравнить - один или оба файла не загрузились")
        return
    
    print(f"\n[СРАВНЕНИЕ] РАЗМЕРЫ ФАЙЛОВ:")
    print(f"  ALTA:  {len(alta_df)} строк")
    print(f"  ELITE: {len(elite_df)} строк")
    print(f"  Разница: {abs(len(alta_df) - len(elite_df))} строк")
    
    # Try to find common columns
    common_cols = set(alta_df.columns) & set(elite_df.columns)
    if common_cols:
        print(f"\n[СРАВНЕНИЕ] ОБЩИЕ СТОЛБЦЫ: {list(common_cols)}")
    else:
        print(f"\n[ПРЕДУПРЕЖДЕНИЕ] ОБЩИХ СТОЛБЦОВ НЕ НАЙДЕНО")
        print(f"  Столбцы ALTA:  {list(alta_df.columns)}")
        print(f"  Столбцы ELITE: {list(elite_df.columns)}")

def main():
    """Основная функция анализа"""
    base_dir = Path(__file__).parent
    inbox_dir = base_dir / 'data' / 'inbox'
    
    print("="*80)
    print("АНАЛИЗ ОШИБОК В ФАЙЛАХ С ЦЕНАМИ")
    print("="*80)
    print(f"Рабочая директория: {base_dir}")
    print(f"Входная директория: {inbox_dir}")
    
    # File paths
    alta_file = inbox_dir / 'price frome Natia alta.xlsx'
    elite_file = inbox_dir / 'price frome Natia elit.xlsx'
    
    # Check if files exist
    if not alta_file.exists():
        print(f"\n[ОШИБКА] Файл ALTA не найден: {alta_file}")
        return
    
    if not elite_file.exists():
        print(f"\n[ОШИБКА] Файл ELITE не найден: {elite_file}")
        return
    
    # Analyze both files
    alta_df = analyze_file(alta_file, "ALTA")
    elite_df = analyze_file(elite_file, "ELITE")
    
    # Compare files
    compare_files(alta_df, elite_df)
    
    print(f"\n{'='*80}")
    print("АНАЛИЗ ЗАВЕРШЕН")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
