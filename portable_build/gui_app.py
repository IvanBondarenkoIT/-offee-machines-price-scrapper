"""
Simple GUI for Price Monitor
Shows progress and status during execution
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import os
from pathlib import Path
import subprocess
from datetime import datetime
import shutil

# Add parent directory to path
SCRIPT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from portable_build.config_loader import ConfigLoader


class PriceMonitorGUI:
    """Simple GUI for Price Monitor"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Price Monitor - Мониторинг цен DeLonghi")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        self.config = None
        self.is_running = False
        
        self.setup_ui()
        self.check_config()
    
    def setup_ui(self):
        """Setup user interface"""
        # Header
        header = tk.Frame(self.root, bg="#2c3e50", height=80)
        header.pack(fill=tk.X)
        
        title = tk.Label(
            header, 
            text="Price Monitor",
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title.pack(pady=10)
        
        subtitle = tk.Label(
            header,
            text="Система мониторинга цен конкурентов DeLonghi",
            font=("Arial", 10),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        subtitle.pack()
        
        # Main content
        content = tk.Frame(self.root, padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Status section
        status_frame = tk.LabelFrame(content, text="Статус", font=("Arial", 10, "bold"), padx=10, pady=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = tk.Label(
            status_frame,
            text="Готов к запуску",
            font=("Arial", 11),
            fg="#27ae60"
        )
        self.status_label.pack()
        
        self.inventory_label = tk.Label(
            status_frame,
            text="Проверка файла остатков...",
            font=("Arial", 9),
            fg="#7f8c8d"
        )
        self.inventory_label.pack()
        
        # Progress section
        progress_frame = tk.LabelFrame(content, text="Прогресс", font=("Arial", 10, "bold"), padx=10, pady=10)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_label = tk.Label(
            progress_frame,
            text="Ожидание запуска...",
            font=("Arial", 9)
        )
        self.progress_label.pack(pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=600
        )
        self.progress_bar.pack(fill=tk.X)
        
        # Log section
        log_frame = tk.LabelFrame(content, text="Лог выполнения", font=("Arial", 10, "bold"), padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            font=("Consolas", 9),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = tk.Frame(content)
        button_frame.pack(fill=tk.X)
        
        self.start_button = tk.Button(
            button_frame,
            text="▶ ЗАПУСТИТЬ МОНИТОРИНГ",
            command=self.start_monitoring,
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            height=2,
            cursor="hand2"
        )
        self.start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.open_button = tk.Button(
            button_frame,
            text="📁 Открыть результаты",
            command=self.open_output,
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            state=tk.DISABLED
        )
        self.open_button.pack(side=tk.LEFT, padx=5)
        
        self.exit_button = tk.Button(
            button_frame,
            text="✕ Выход",
            command=self.exit_app,
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white"
        )
        self.exit_button.pack(side=tk.LEFT, padx=(5, 0))
    
    def check_config(self):
        """Check configuration and inventory file"""
        try:
            self.config = ConfigLoader()
            self.log("✓ Настройки загружены")
            
            # Check inventory
            inventory_path = self.config.paths['inventory']
            inventory_files = list(inventory_path.glob('остатки.*'))
            inventory_files = [f for f in inventory_files if f.suffix in ['.xls', '.xlsx']]
            
            if inventory_files:
                self.log(f"✓ Файл остатков найден: {inventory_files[0].name}")
                self.inventory_label.config(
                    text=f"✓ Файл остатков: {inventory_files[0].name}",
                    fg="#27ae60"
                )
            else:
                self.log("✗ Файл остатков НЕ найден!")
                self.inventory_label.config(
                    text="✗ Положите файл 'остатки.xls' в папку inventory/",
                    fg="#e74c3c"
                )
                self.start_button.config(state=tk.DISABLED)
                
        except Exception as e:
            self.log(f"✗ Ошибка загрузки настроек: {e}")
            self.status_label.config(text="Ошибка настроек", fg="#e74c3c")
    
    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def update_status(self, text, color="#3498db"):
        """Update status label"""
        self.status_label.config(text=text, fg=color)
        self.root.update()
    
    def update_progress(self, text):
        """Update progress label"""
        self.progress_label.config(text=text)
        self.root.update()
    
    def start_monitoring(self):
        """Start monitoring in background thread"""
        if self.is_running:
            return
        
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.progress_bar.start(10)
        
        # Run in thread
        thread = threading.Thread(target=self.run_monitoring)
        thread.daemon = True
        thread.start()
    
    def run_monitoring(self):
        """Run the actual monitoring process"""
        try:
            self.update_status("Выполняется...", "#f39c12")
            self.log("\n" + "="*60)
            self.log("ЗАПУСК МОНИТОРИНГА ЦЕН")
            self.log("="*60)
            
            # Step 1: Check inventory
            self.update_progress("Шаг 1/6: Проверка файла остатков...")
            self.log("\n[1/6] Проверка файла остатков...")
            
            inventory_path = self.config.paths['inventory']
            inventory_files = list(inventory_path.glob('остатки.*'))
            inventory_files = [f for f in inventory_files if f.suffix in ['.xls', '.xlsx']]
            
            if not inventory_files:
                raise Exception("Файл остатков не найден!")
            
            self.log(f"  ✓ Найден: {inventory_files[0].name}")
            
            # Step 2: Run scrapers
            self.update_progress("Шаг 2/6: Парсинг сайтов конкурентов (3-5 минут)...")
            self.log("\n[2/6] Парсинг сайтов конкурентов...")
            self.log("  Это займет 3-5 минут, пожалуйста подождите...")
            
            # Run full cycle from main project
            main_script = SCRIPT_DIR / 'run_full_cycle.py'
            
            self.log(f"\n  Запуск: {main_script.name}")
            
            result = subprocess.run(
                [sys.executable, str(main_script)],
                cwd=str(SCRIPT_DIR),
                capture_output=True,
                text=True,
                timeout=900  # 15 minutes max
            )
            
            if result.returncode != 0:
                raise Exception(f"Ошибка выполнения: {result.stderr[:500]}")
            
            # Parse output
            output_lines = result.stdout.split('\n')
            
            # Find key information
            for line in output_lines:
                if 'ALTA' in line and 'SUCCESS' in line:
                    self.log("  ✓ ALTA: успешно")
                elif 'KONTAKT' in line and 'SUCCESS' in line:
                    self.log("  ✓ KONTAKT: успешно")
                elif 'ELITE' in line and 'SUCCESS' in line:
                    self.log("  ✓ ELITE: успешно")
                elif 'DIM_KAVA' in line and 'SUCCESS' in line:
                    self.log("  ✓ DIM_KAVA: успешно")
            
            # Step 3: Find results
            self.update_progress("Шаг 3/6: Поиск результатов...")
            self.log("\n[3/6] Поиск результатов...")
            
            source_output = SCRIPT_DIR / 'data' / 'output'
            
            # Find latest files
            excel_files = list(source_output.glob('price_comparison_*.xlsx'))
            word_files = list(source_output.glob('executive_report_*.docx'))
            pdf_files = list(source_output.glob('executive_report_*.pdf'))
            
            latest_excel = max(excel_files, key=lambda x: x.stat().st_mtime) if excel_files else None
            latest_word = max(word_files, key=lambda x: x.stat().st_mtime) if word_files else None
            latest_pdf = max(pdf_files, key=lambda x: x.stat().st_mtime) if pdf_files else None
            
            # Step 4: Copy results
            self.update_progress("Шаг 4/6: Копирование результатов...")
            self.log("\n[4/6] Копирование результатов...")
            
            results_copied = []
            
            if latest_excel:
                dest = self.config.paths['excel'] / latest_excel.name
                shutil.copy2(latest_excel, dest)
                self.log(f"  ✓ Excel: {latest_excel.name}")
                results_copied.append(('excel', dest))
            
            if latest_word:
                dest = self.config.paths['reports'] / latest_word.name
                shutil.copy2(latest_word, dest)
                self.log(f"  ✓ Word:  {latest_word.name}")
                results_copied.append(('word', dest))
            
            if latest_pdf:
                dest = self.config.paths['reports'] / latest_pdf.name
                shutil.copy2(latest_pdf, dest)
                self.log(f"  ✓ PDF:   {latest_pdf.name}")
                results_copied.append(('pdf', dest))
            
            # Step 5: Show statistics
            self.update_progress("Шаг 5/6: Анализ результатов...")
            self.log("\n[5/6] Анализ результатов...")
            
            # Parse statistics from output
            for line in output_lines:
                if 'Products compared:' in line or 'TOTAL PRODUCTS' in line:
                    self.log(f"  {line.strip()}")
                elif 'Total quantity:' in line or 'Total value:' in line:
                    self.log(f"  {line.strip()}")
            
            # Step 6: Complete
            self.update_progress("Шаг 6/6: Завершение...")
            self.log("\n[6/6] Завершение...")
            
            self.log("\n" + "="*60)
            self.log("✓ МОНИТОРИНГ ЗАВЕРШЕН УСПЕШНО!")
            self.log("="*60)
            self.log(f"\nРезультаты сохранены в: output/")
            self.log(f"  - Excel таблицы: output/excel/")
            self.log(f"  - Отчеты:        output/reports/")
            
            # Update UI
            self.progress_bar.stop()
            self.update_status("✓ Завершено успешно!", "#27ae60")
            self.update_progress("Готово! Результаты в папке output/")
            
            self.start_button.config(state=tk.NORMAL)
            self.open_button.config(state=tk.NORMAL)
            
            # Show success message
            messagebox.showinfo(
                "Успех!",
                f"Мониторинг завершен!\n\n"
                f"Создано файлов: {len(results_copied)}\n"
                f"Результаты в папке: output/\n\n"
                f"Открыть папку с результатами?"
            )
            
            # Auto-open if configured
            if self.config and self.config.general['open_report']:
                self.open_output()
            
        except Exception as e:
            self.log(f"\n✗ ОШИБКА: {e}")
            self.progress_bar.stop()
            self.update_status("✗ Ошибка выполнения", "#e74c3c")
            self.update_progress("Ошибка! См. лог выше")
            self.start_button.config(state=tk.NORMAL)
            
            messagebox.showerror(
                "Ошибка",
                f"Произошла ошибка:\n\n{str(e)[:200]}\n\n"
                f"Проверьте:\n"
                f"1. Файл остатков в папке inventory/\n"
                f"2. Интернет соединение\n"
                f"3. Лог выполнения в окне программы"
            )
        
        finally:
            self.is_running = False
    
    def open_output(self):
        """Open output folder"""
        if self.config:
            output_path = self.config.paths['output']
            os.startfile(output_path)
            self.log(f"\n✓ Открыта папка: {output_path}")
    
    def exit_app(self):
        """Exit application"""
        if self.is_running:
            if not messagebox.askyesno(
                "Выход",
                "Мониторинг еще выполняется!\n\nВы уверены что хотите выйти?"
            ):
                return
        
        self.root.quit()
    
    def run(self):
        """Run the GUI"""
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Run
        self.root.mainloop()


def main():
    """Entry point"""
    app = PriceMonitorGUI()
    app.run()


if __name__ == '__main__':
    main()

