"""Analyze inventory file structure"""

import pandas as pd
from pathlib import Path
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = Path("data/inbox/остатки.xls")

print(f"Analyzing: {file_path}")
print("=" * 70)

# Read file
df_all = pd.read_excel(file_path)
print(f"Total rows: {len(df_all)}")
print(f"Total columns: {len(df_all.columns)}")
print()

# Show first 20 rows to find where data starts
print("First 20 rows:")
print("=" * 70)
for i in range(min(20, len(df_all))):
    row_data = df_all.iloc[i].values
    # Show only non-NaN values
    non_nan = [str(x) for x in row_data if pd.notna(x)]
    if non_nan:
        print(f"Row {i}: {' | '.join(non_nan[:5])}")
    else:
        print(f"Row {i}: (empty)")

# Try different skip rows
print("\n" + "=" * 70)
print("Testing different header rows:")
print("=" * 70)

for skip in [0, 1, 2, 3, 4, 5, 10]:
    try:
        df = pd.read_excel(file_path, skiprows=skip)
        # Count rows with actual data (not all NaN)
        data_rows = df.dropna(how='all')
        print(f"skiprows={skip}: {len(data_rows)} rows with data, columns={list(df.columns)[:3]}")
    except:
        print(f"skiprows={skip}: Error")

