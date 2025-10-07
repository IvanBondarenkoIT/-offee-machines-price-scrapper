"""Check comparison file structure"""
import pandas as pd
from pathlib import Path

INBOX_DIR = Path("data/inbox")

# Find comparison file
comparison_files = list(INBOX_DIR.glob("*.xlsx"))
comparison_files = [f for f in comparison_files if "сравн" in f.name.lower() or "сравнение" in f.name.lower()]
comparison_files = [f for f in comparison_files if not f.name.startswith('~$')]

if not comparison_files:
    print("No comparison file found!")
    exit(1)

comp_file = comparison_files[0]
print(f"File: {comp_file.name}")
print("="*80)

df = pd.read_excel(comp_file)
print(f"\nShape: {df.shape}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nFirst 10 rows:\n")
print(df.head(10).to_string())

