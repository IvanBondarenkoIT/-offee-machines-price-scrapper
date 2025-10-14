"""Test inventory file reading"""

import pandas as pd
from pathlib import Path
import sys
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = Path("data/inbox/остатки.xls")

print(f"Файл: {file_path}")
print(f"Существует: {file_path.exists()}")
print(f"Размер: {file_path.stat().st_size if file_path.exists() else 0} bytes")
print()

if file_path.exists():
    try:
        df = pd.read_excel(file_path)
        print(f"[OK] Файл прочитан успешно!")
        print(f"Строк: {len(df)}")
        print(f"Столбцов: {len(df.columns)}")
        print(f"\nКолонки: {list(df.columns)}")
        print(f"\nПервые 3 строки:")
        print(df.head(3).to_string())
    except Exception as e:
        print(f"[ERROR] Ошибка чтения файла: {e}")
        import traceback
        traceback.print_exc()
else:
    print("[ERROR] Файл не найден!")

