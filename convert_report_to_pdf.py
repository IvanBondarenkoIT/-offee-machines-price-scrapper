"""
Convert Word report to PDF automatically
"""

from pathlib import Path
import subprocess
import sys

def convert_to_pdf_with_word():
    """Convert using Word COM automation (Windows only)"""
    try:
        import win32com.client
        
        # Find latest report
        output_dir = Path(__file__).parent / 'data' / 'output'
        report_files = list(output_dir.glob('executive_report_*.docx'))
        
        if not report_files:
            print("[ERROR] No executive report found")
            return None
        
        latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
        print(f"Converting: {latest_report.name}")
        
        # Output PDF path
        pdf_path = latest_report.with_suffix('.pdf')
        
        # Create Word application
        word = win32com.client.Dispatch('Word.Application')
        word.Visible = False
        
        # Open document
        doc = word.Documents.Open(str(latest_report.absolute()))
        
        # Save as PDF (format 17 = PDF)
        doc.SaveAs(str(pdf_path.absolute()), FileFormat=17)
        
        # Close
        doc.Close()
        word.Quit()
        
        print(f"[SUCCESS] PDF created: {pdf_path.name}")
        return pdf_path
        
    except ImportError:
        print("[ERROR] pywin32 not installed")
        print("Install: pip install pywin32")
        return None
    except Exception as e:
        print(f"[ERROR] Conversion failed: {e}")
        return None

def manual_instructions():
    """Show manual conversion instructions"""
    print("\n" + "="*80)
    print("MANUAL CONVERSION TO PDF")
    print("="*80)
    print("\nWord document is now open. To save as PDF:")
    print("\n1. In Word: File > Save As")
    print("2. Choose location: data\\output\\")
    print("3. File type: PDF (*.pdf)")
    print("4. Click 'Save'")
    print("\nOr use keyboard shortcut:")
    print("  - Press F12")
    print("  - Select 'PDF' from dropdown")
    print("  - Click 'Save'")
    print("\n" + "="*80)

if __name__ == "__main__":
    print("="*80)
    print("CONVERT EXECUTIVE REPORT TO PDF")
    print("="*80)
    
    # Try automatic conversion
    print("\nAttempting automatic conversion...")
    pdf_path = convert_to_pdf_with_word()
    
    if pdf_path:
        print(f"\n[SUCCESS] PDF ready: {pdf_path}")
        print("PDF file created successfully. You can open it manually if needed.")
    else:
        # Show manual instructions
        manual_instructions()
        
        # Don't automatically open files to avoid CMD windows
        output_dir = Path(__file__).parent / 'data' / 'output'
        report_files = list(output_dir.glob('executive_report_*.docx'))
        if report_files:
            latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
            print(f"Word document available: {latest_report}")
            print("You can open it manually if needed.")

