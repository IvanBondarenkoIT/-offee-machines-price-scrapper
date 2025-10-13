"""
Portable Price Monitor - Main Script
Standalone executable for price monitoring
"""
import sys
import os
from pathlib import Path
import subprocess
from datetime import datetime

# Add parent directory to path to import from main project
SCRIPT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from config_loader import ConfigLoader


def print_header():
    """Print application header"""
    print("=" * 80)
    print("PRICE MONITOR - Мониторинг цен DeLonghi")
    print("=" * 80)
    print(f"Запущено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()


def check_inventory_file(config):
    """Check if inventory file exists"""
    inventory_path = config.paths['inventory']
    
    # Look for остатки.xls or остатки.xlsx
    inventory_files = list(inventory_path.glob('остатки.*'))
    inventory_files = [f for f in inventory_files if f.suffix in ['.xls', '.xlsx']]
    
    if not inventory_files:
        print("[ОШИБКА] Файл остатков не найден!")
        print(f"Положите файл 'остатки.xls' в папку: {inventory_path}")
        input("\nНажмите Enter для выхода...")
        return None
    
    return inventory_files[0]


def run_full_cycle():
    """Run the full monitoring cycle"""
    try:
        # Load configuration
        print("[1/5] Загрузка настроек...")
        config = ConfigLoader()
        print(f"  Базовая папка: {config.base_path}")
        
        # Check inventory
        print("\n[2/5] Проверка файла остатков...")
        inventory_file = check_inventory_file(config)
        if not inventory_file:
            return False
        print(f"  Найден: {inventory_file.name}")
        
        # Ensure output directories exist
        config.paths['reports'].mkdir(parents=True, exist_ok=True)
        config.paths['excel'].mkdir(parents=True, exist_ok=True)
        config.paths['logs'].mkdir(parents=True, exist_ok=True)
        
        # Run main script from parent project
        print("\n[3/5] Запуск парсинга и анализа...")
        print("  Это может занять 5-10 минут...")
        
        main_script = SCRIPT_DIR / 'run_full_cycle.py'
        result = subprocess.run(
            [sys.executable, str(main_script)],
            cwd=str(SCRIPT_DIR),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("\n[ОШИБКА] Ошибка при выполнении:")
            print(result.stderr)
            return False
        
        # Parse output to find result files
        print("\n[4/5] Поиск результатов...")
        output_lines = result.stdout.split('\n')
        
        excel_file = None
        word_file = None
        pdf_file = None
        
        for line in output_lines:
            if 'price_comparison_' in line and '.xlsx' in line:
                # Extract filename
                parts = line.split('price_comparison_')
                if len(parts) > 1:
                    filename = 'price_comparison_' + parts[1].split()[0]
                    excel_file = SCRIPT_DIR / 'data' / 'output' / filename
            elif 'executive_report_' in line and '.docx' in line:
                parts = line.split('executive_report_')
                if len(parts) > 1:
                    filename = 'executive_report_' + parts[1].split()[0]
                    word_file = SCRIPT_DIR / 'data' / 'output' / filename
            elif 'executive_report_' in line and '.pdf' in line:
                parts = line.split('executive_report_')
                if len(parts) > 1:
                    filename = 'executive_report_' + parts[1].split()[0]
                    pdf_file = SCRIPT_DIR / 'data' / 'output' / filename
        
        # Copy results to portable output folder
        print("\n[5/5] Копирование результатов...")
        
        import shutil
        results_copied = False
        
        if excel_file and excel_file.exists():
            dest = config.paths['excel'] / excel_file.name
            shutil.copy2(excel_file, dest)
            print(f"  Excel: {dest.name}")
            results_copied = True
        
        if word_file and word_file.exists():
            dest = config.paths['reports'] / word_file.name
            shutil.copy2(word_file, dest)
            print(f"  Word:  {dest.name}")
            results_copied = True
        
        if pdf_file and pdf_file.exists():
            dest = config.paths['reports'] / pdf_file.name
            shutil.copy2(pdf_file, dest)
            print(f"  PDF:   {dest.name}")
            results_copied = True
            
            # Open PDF if configured
            if config.general['open_report']:
                os.startfile(dest)
        
        if results_copied:
            print("\n" + "=" * 80)
            print("УСПЕШНО ЗАВЕРШЕНО!")
            print("=" * 80)
            print(f"\nРезультаты сохранены в: {config.paths['output']}")
            print(f"  - Excel таблицы: {config.paths['excel']}")
            print(f"  - Отчеты:        {config.paths['reports']}")
            return True
        else:
            print("\n[ПРЕДУПРЕЖДЕНИЕ] Результаты не найдены")
            return False
            
    except Exception as e:
        print(f"\n[ОШИБКА] {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    print_header()
    
    success = run_full_cycle()
    
    print("\n" + "=" * 80)
    if success:
        print("Нажмите Enter для выхода...")
    else:
        print("Возникли ошибки. Нажмите Enter для выхода...")
    input()


if __name__ == '__main__':
    main()

