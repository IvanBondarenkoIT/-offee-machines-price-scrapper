"""
Build script for creating portable .exe
Requires: pip install pyinstaller
"""
import subprocess
import sys
from pathlib import Path
import shutil

def build_executable():
    """Build portable executable"""
    print("=" * 80)
    print("BUILDING PORTABLE EXECUTABLE")
    print("=" * 80)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("[OK] PyInstaller found")
    except ImportError:
        print("[ERROR] PyInstaller not installed")
        print("Install it with: pip install pyinstaller")
        return False
    
    # Paths
    script_dir = Path(__file__).parent
    main_script = script_dir / 'portable_main.py'
    dist_dir = script_dir / 'dist'
    build_dir = script_dir / 'build'
    
    # Clean previous builds
    if dist_dir.exists():
        print("\n[1/4] Cleaning previous build...")
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # PyInstaller command
    print("\n[2/4] Building executable...")
    cmd = [
        'pyinstaller',
        '--onefile',                    # Single file
        '--windowed',                   # No console (use --console for debugging)
        '--name=PriceMonitor',          # Output name
        '--icon=NONE',                  # No icon (add .ico file if needed)
        '--add-data', f'{script_dir / "config"};config',  # Include config folder
        '--hidden-import', 'selenium',
        '--hidden-import', 'bs4',
        '--hidden-import', 'pandas',
        '--hidden-import', 'openpyxl',
        '--hidden-import', 'docx',
        '--hidden-import', 'win32com',
        str(main_script)
    ]
    
    result = subprocess.run(cmd, cwd=str(script_dir))
    
    if result.returncode != 0:
        print("[ERROR] Build failed!")
        return False
    
    # Copy config and folders to dist
    print("\n[3/4] Copying folders...")
    exe_file = dist_dir / 'PriceMonitor.exe'
    
    if exe_file.exists():
        # Copy folders
        for folder in ['inventory', 'output', 'logs']:
            src = script_dir / folder
            dst = dist_dir / folder
            if src.exists():
                shutil.copytree(src, dst, dirs_exist_ok=True)
                print(f"  Copied: {folder}/")
        
        # Copy config (already included but copy README)
        config_dst = dist_dir / 'config'
        config_dst.mkdir(exist_ok=True)
        shutil.copy2(script_dir / 'config' / 'README.txt', config_dst / 'README.txt')
        shutil.copy2(script_dir / 'config' / 'settings.ini', config_dst / 'settings.ini')
        
        print("\n[4/4] Creating final package...")
        # Create archive
        archive_name = script_dir / 'PriceMonitor_Portable'
        shutil.make_archive(str(archive_name), 'zip', dist_dir)
        
        print("\n" + "=" * 80)
        print("BUILD SUCCESSFUL!")
        print("=" * 80)
        print(f"\nExecutable: {exe_file}")
        print(f"Archive:    {archive_name}.zip")
        print(f"\nSize: {exe_file.stat().st_size / 1024 / 1024:.1f} MB")
        return True
    else:
        print("[ERROR] Executable not found!")
        return False


if __name__ == '__main__':
    success = build_executable()
    sys.exit(0 if success else 1)

