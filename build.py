"""Build script for creating standalone executable with PyInstaller"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_build_dirs():
    """Clean up build and dist directories"""
    print("Cleaning build directories...")
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")

    # Remove spec file if it exists
    spec_file = "TT Events Manager.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"  Removed {spec_file}")

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"PyInstaller {PyInstaller.__version__} found")
        return True
    except ImportError:
        print("PyInstaller not found!")
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        return True

def build_executable():
    """Build the executable using PyInstaller"""
    print("\nBuilding executable...")

    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',              # Single file executable
        '--windowed',             # No console window
        '--name', 'TT Events Manager',  # Name of executable
        '--hidden-import', 'PIL._tkinter_finder',  # Required for Pillow
        '--hidden-import', 'babel.numbers',  # Required for tkcalendar
        '--collect-all', 'tkcalendar',  # Include all tkcalendar files
        '--collect-all', 'customtkinter',  # Include all customtkinter files
        'main.py'
    ]

    # Add config file if it exists
    if os.path.exists('config.json'):
        cmd.insert(-1, '--add-data')
        cmd.insert(-1, 'config.json;.' if sys.platform == 'win32' else 'config.json:.')

    # Add icon if it exists
    if os.path.exists('icon.ico'):
        cmd.insert(1, '--icon=icon.ico')

    print(f"Running: {' '.join(cmd)}")

    try:
        subprocess.check_call(cmd)
        print("\n✓ Build successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error code {e.returncode}")
        return False

def create_dist_package():
    """Create a distribution package with necessary files"""
    print("\nCreating distribution package...")

    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("  Error: dist/ directory not found")
        return False

    # Create a release folder
    release_dir = dist_dir / "TT Events Manager"
    release_dir.mkdir(exist_ok=True)

    # Copy executable
    exe_name = "TT Events Manager.exe" if sys.platform == 'win32' else "TT Events Manager"
    exe_path = dist_dir / exe_name
    if exe_path.exists():
        shutil.copy2(exe_path, release_dir / exe_name)
        print(f"  Copied {exe_name}")

    # Copy config file if it exists
    if os.path.exists('config.json'):
        shutil.copy2('config.json', release_dir / 'config.json')
        print("  Copied config.json")

    # Create README for distribution
    readme_content = """# TT Events Manager

## Installation

1. Extract all files to a folder of your choice
2. Run "TT Events Manager.exe"
3. The database (events.db) will be created automatically on first run

## Backups

- Automatic backups are created daily in the "backups" folder
- Manual backups can be created with Ctrl+B
- Keep your backups safe!

## Keyboard Shortcuts

- **Ctrl+N** - Quick create new event
- **Ctrl+S** - Save current form
- **Ctrl+P** - Print current view
- **Ctrl+B** - Manual backup
- **F1** - Open help

## Support

For issues or questions, please contact the developer.

---
Designed by Kerry Restante
"""

    with open(release_dir / "README.txt", 'w') as f:
        f.write(readme_content)
    print("  Created README.txt")

    print(f"\nDistribution package created in: {release_dir.absolute()}")
    return True

def main():
    """Main build process"""
    print("=" * 60)
    print("TT Events Manager - Build Script")
    print("=" * 60)
    print()

    # Check PyInstaller
    if not check_pyinstaller():
        print("Failed to install PyInstaller")
        return 1

    # Clean previous builds
    clean_build_dirs()

    # Build executable
    if not build_executable():
        return 1

    # Create distribution package
    if not create_dist_package():
        return 1

    print("\n" + "=" * 60)
    print("Build complete!")
    print("=" * 60)
    print(f"\nYour executable is in: dist/TT Events Manager/")
    print("\nYou can distribute the entire 'TT Events Manager' folder to users.")

    return 0

if __name__ == "__main__":
    sys.exit(main())
