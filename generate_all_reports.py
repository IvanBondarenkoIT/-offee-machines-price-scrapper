"""
Generate all reports: Excel + Word + PDF
Complete package for director
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

def print_header(text):
    print("\n" + "="*80)
    print(text)
    print("="*80)

def run_script(script_name, description):
    """Run a Python script"""
    print(f"\n[Running] {description}...")
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(Path(__file__).parent)
        )
        
        if result.returncode == 0:
            print(f"[OK] {description} completed")
            # Show key lines from output
            for line in result.stdout.split('\n'):
                if 'SUCCESS' in line or 'Saved to:' in line or 'created:' in line:
                    print(f"  {line.strip()}")
            return True
        else:
            print(f"[ERROR] {description} failed")
            print(result.stderr[:200])
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print_header("GENERATING COMPLETE REPORT PACKAGE FOR DIRECTOR")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Step 1: Build price comparison (if needed)
    print_header("STEP 1: Price Comparison Table (Excel)")
    if run_script('build_price_comparison.py', 'Price comparison'):
        results['excel'] = 'SUCCESS'
    else:
        results['excel'] = 'FAILED'
    
    # Step 2: Generate Word report
    print_header("STEP 2: Executive Report (Word)")
    if run_script('generate_executive_report.py', 'Word report'):
        results['word'] = 'SUCCESS'
    else:
        results['word'] = 'FAILED'
    
    # Step 3: Convert to PDF
    print_header("STEP 3: Convert to PDF")
    if run_script('convert_report_to_pdf.py', 'PDF conversion'):
        results['pdf'] = 'SUCCESS'
    else:
        results['pdf'] = 'FAILED'
    
    # Summary
    print_header("REPORT PACKAGE COMPLETE")
    
    output_dir = Path(__file__).parent / 'data' / 'output'
    
    # Find latest files
    excel_files = list(output_dir.glob('price_comparison_*.xlsx'))
    word_files = list(output_dir.glob('executive_report_*.docx'))
    pdf_files = list(output_dir.glob('executive_report_*.pdf'))
    
    print("\nGenerated files:")
    print("-"*80)
    
    if excel_files:
        latest_excel = max(excel_files, key=lambda x: x.stat().st_mtime)
        print(f"[Excel] {latest_excel.name}")
        print(f"        Location: {latest_excel}")
    
    if word_files:
        latest_word = max(word_files, key=lambda x: x.stat().st_mtime)
        print(f"[Word]  {latest_word.name}")
        print(f"        Location: {latest_word}")
    
    if pdf_files:
        latest_pdf = max(pdf_files, key=lambda x: x.stat().st_mtime)
        print(f"[PDF]   {latest_pdf.name}")
        print(f"        Location: {latest_pdf}")
        print(f"        Size: {latest_pdf.stat().st_size / 1024:.1f} KB")
    
    print("\n" + "="*80)
    print("WHAT TO DO NEXT:")
    print("="*80)
    print("\nFor Director:")
    print("  1. Open PDF file (easiest to read)")
    print("  2. Or open Word file (can edit)")
    print("  3. Or open Excel file (for detailed analysis)")
    print("\nFor Email:")
    print("  - Attach PDF file")
    print("  - Subject: 'Price Monitoring Report - [DATE]'")
    print("\nFor Printing:")
    print("  - Open PDF and print")
    print("  - Recommended: Color printing for better readability")
    
    # Results summary
    print("\n" + "="*80)
    print("RESULTS:")
    print("="*80)
    for key, value in results.items():
        status = "[OK]" if value == "SUCCESS" else "[FAIL]"
        print(f"  {status} {key.upper()}: {value}")
    
    success_count = sum(1 for v in results.values() if v == "SUCCESS")
    print(f"\nTotal: {success_count}/{len(results)} successful")
    
    if success_count == len(results):
        print("\n[SUCCESS] All reports generated successfully!")
        return True
    else:
        print("\n[WARNING] Some reports failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

