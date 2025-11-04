#!/usr/bin/env python3
"""
Cross-Platform Launcher for Excel Map Coordinates Converter
Handles virtual environment creation, package installation, path validation, and app startup.
Works on macOS, Windows, and Linux.
"""

import sys
import subprocess
import os
from pathlib import Path
import shutil

# ANSI color codes for terminal output (works on most terminals)
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=''):
    """Print colored message (works cross-platform)"""
    print(f"{color}{message}{Colors.END}")

def print_header():
    """Print application header"""
    print_colored("\n" + "="*60, Colors.BLUE)
    print_colored("  🗺️  Excel Map Coordinates Converter", Colors.BOLD + Colors.BLUE)
    print_colored("="*60 + "\n", Colors.BLUE)

def check_python_version():
    """Check if Python version is 3.11 or higher"""
    print_colored("🔍 Checking Python version...", Colors.BLUE)
    version = sys.version_info

    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print_colored(
            f"❌ Error: Python 3.11+ required. You have {version.major}.{version.minor}.{version.micro}",
            Colors.RED
        )
        print_colored("   Please install Python 3.11 or higher from https://www.python.org/downloads/", Colors.YELLOW)
        return False

    print_colored(f"   ✅ Python {version.major}.{version.minor}.{version.micro}", Colors.GREEN)
    return True

def setup_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    print_colored("\n🔧 Setting up virtual environment...", Colors.BLUE)

    base_dir = Path(__file__).parent
    venv_dir = base_dir / 'venv'

    # Check if venv exists
    if venv_dir.exists():
        print_colored("   ✅ Virtual environment already exists", Colors.GREEN)
        return venv_dir

    # Create virtual environment
    try:
        print_colored("   📦 Creating virtual environment...", Colors.YELLOW)
        subprocess.check_call(
            [sys.executable, '-m', 'venv', str(venv_dir)],
            stdout=subprocess.DEVNULL
        )
        print_colored("   ✅ Virtual environment created successfully", Colors.GREEN)
        return venv_dir
    except subprocess.CalledProcessError as e:
        print_colored(f"   ❌ Error creating virtual environment: {e}", Colors.RED)
        return None

def get_venv_python(venv_dir):
    """Get path to Python executable in virtual environment"""
    if sys.platform == 'win32':
        return venv_dir / 'Scripts' / 'python.exe'
    else:
        return venv_dir / 'bin' / 'python'

def get_venv_pip(venv_dir):
    """Get path to pip executable in virtual environment"""
    if sys.platform == 'win32':
        return venv_dir / 'Scripts' / 'pip.exe'
    else:
        return venv_dir / 'bin' / 'pip'

def install_packages(venv_dir):
    """Install required packages in virtual environment"""
    print_colored("\n📦 Installing required packages...", Colors.BLUE)

    base_dir = Path(__file__).parent
    requirements_file = base_dir / 'requirements.txt'

    if not requirements_file.exists():
        print_colored("   ❌ Error: requirements.txt not found!", Colors.RED)
        return False

    pip_path = get_venv_pip(venv_dir)

    try:
        # Upgrade pip first
        print_colored("   ⬆️  Upgrading pip...", Colors.YELLOW)
        subprocess.check_call(
            [str(pip_path), 'install', '--upgrade', 'pip'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Install packages
        print_colored("   📥 Installing dependencies...", Colors.YELLOW)
        subprocess.check_call(
            [str(pip_path), 'install', '-q', '-r', str(requirements_file)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        print_colored("   ✅ All packages installed successfully", Colors.GREEN)
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"   ❌ Error installing packages: {e}", Colors.RED)
        print_colored("   💡 Try manually: pip install -r requirements.txt", Colors.YELLOW)
        return False

def validate_paths():
    """Validate and create necessary directories"""
    print_colored("\n📁 Validating directory structure...", Colors.BLUE)

    base_dir = Path(__file__).parent
    required_dirs = ['uploads', 'processed', 'static', 'templates', 'tests']

    all_valid = True

    for dir_name in required_dirs:
        dir_path = base_dir / dir_name

        if dir_name in ['uploads', 'processed']:
            # Create if doesn't exist
            dir_path.mkdir(parents=True, exist_ok=True)
            print_colored(f"   ✅ {dir_name}/ - Created/Verified", Colors.GREEN)
        elif dir_path.exists():
            print_colored(f"   ✅ {dir_name}/ - Found", Colors.GREEN)
        else:
            print_colored(f"   ⚠️  {dir_name}/ - Not found (optional)", Colors.YELLOW)

    # Validate required files
    print_colored("\n📄 Checking required files...", Colors.BLUE)
    required_files = {
        'map_converter.py': 'Core conversion logic',
        'flask_app.py': 'Flask web application',
        'app.py': 'Streamlit web application'
    }

    for file_name, description in required_files.items():
        file_path = base_dir / file_name
        if file_path.exists():
            print_colored(f"   ✅ {file_name} - {description}", Colors.GREEN)
        else:
            print_colored(f"   ❌ {file_name} - Missing!", Colors.RED)
            all_valid = False

    return all_valid

def select_app():
    """Ask user which app to run"""
    print_colored("\n🚀 Select application to run:", Colors.BLUE)
    print("   1. Flask Web App (http://localhost:5000)")
    print("   2. Streamlit Web App (http://localhost:8501)")
    print("   3. CLI Tool (Command line)")
    print("   4. Uninstall (Remove virtual environment)")
    print("   5. Exit")

    while True:
        try:
            choice = input("\n   Enter choice (1-5): ").strip()

            if choice in ['1', '2', '3', '4', '5']:
                return int(choice)
            else:
                print_colored("   ⚠️  Invalid choice. Please enter 1-5.", Colors.YELLOW)
        except KeyboardInterrupt:
            print_colored("\n\n   👋 Goodbye!", Colors.BLUE)
            sys.exit(0)

def run_flask_app(venv_dir):
    """Run Flask application using venv Python"""
    print_colored("\n🌐 Starting Flask Web Server...", Colors.GREEN)
    print_colored("   Access the app at: http://localhost:5000", Colors.BOLD + Colors.GREEN)
    print_colored("   Press Ctrl+C to stop\n", Colors.YELLOW)

    base_dir = Path(__file__).parent
    flask_app = base_dir / 'flask_app.py'
    python_path = get_venv_python(venv_dir)

    try:
        subprocess.run([str(python_path), str(flask_app)])
    except KeyboardInterrupt:
        print_colored("\n\n   ⏹️  Flask server stopped.", Colors.YELLOW)

def run_streamlit_app(venv_dir):
    """Run Streamlit application using venv Python"""
    print_colored("\n🌐 Starting Streamlit Web Server...", Colors.GREEN)
    print_colored("   The app will open in your browser automatically", Colors.BOLD + Colors.GREEN)
    print_colored("   Press Ctrl+C to stop\n", Colors.YELLOW)

    base_dir = Path(__file__).parent
    streamlit_app = base_dir / 'app.py'
    python_path = get_venv_python(venv_dir)

    try:
        subprocess.run([str(python_path), '-m', 'streamlit', 'run', str(streamlit_app)])
    except KeyboardInterrupt:
        print_colored("\n\n   ⏹️  Streamlit server stopped.", Colors.YELLOW)

def run_cli_tool(venv_dir):
    """Run CLI tool using venv Python"""
    print_colored("\n💻 Command Line Tool", Colors.GREEN)
    print_colored("   Usage: python map_converter.py <input.xlsx> <output.xlsx>\n", Colors.YELLOW)

    base_dir = Path(__file__).parent
    python_path = get_venv_python(venv_dir)

    # Check for test file
    test_input = base_dir / 'test_input.xlsx'
    if test_input.exists():
        print_colored("   📝 Test file found: test_input.xlsx", Colors.GREEN)
        run_test = input("   Run test conversion? (y/n): ").strip().lower()

        if run_test == 'y':
            output_file = base_dir / 'test_output_new.xlsx'
            cli_tool = base_dir / 'map_converter.py'

            try:
                subprocess.run([
                    str(python_path),
                    str(cli_tool),
                    str(test_input),
                    str(output_file)
                ])
                print_colored(f"\n   ✅ Output saved to: {output_file}", Colors.GREEN)
            except Exception as e:
                print_colored(f"\n   ❌ Error: {e}", Colors.RED)
    else:
        print_colored("   ℹ️  Provide input and output file paths to process.", Colors.BLUE)
        input("   Press Enter to continue...")

def uninstall():
    """Remove virtual environment and clean up"""
    print_colored("\n🗑️  Uninstalling...", Colors.YELLOW)

    base_dir = Path(__file__).parent
    venv_dir = base_dir / 'venv'

    if not venv_dir.exists():
        print_colored("   ℹ️  No virtual environment found. Nothing to uninstall.", Colors.BLUE)
        return

    print_colored("   ⚠️  This will remove the virtual environment and all installed packages.", Colors.YELLOW)
    confirm = input("   Are you sure? (yes/no): ").strip().lower()

    if confirm in ['yes', 'y']:
        try:
            shutil.rmtree(venv_dir)
            print_colored("   ✅ Virtual environment removed successfully", Colors.GREEN)
            print_colored("   ℹ️  Run this script again to reinstall", Colors.BLUE)
        except Exception as e:
            print_colored(f"   ❌ Error removing virtual environment: {e}", Colors.RED)
    else:
        print_colored("   ❌ Uninstall cancelled", Colors.YELLOW)

def main():
    """Main launcher function"""
    try:
        # Print header
        print_header()

        # Step 1: Check Python version
        if not check_python_version():
            sys.exit(1)

        # Step 2: Setup virtual environment
        venv_dir = setup_virtual_environment()
        if not venv_dir:
            print_colored("\n⚠️  Warning: Could not create virtual environment.", Colors.YELLOW)
            proceed = input("   Continue anyway? (y/n): ").strip().lower()
            if proceed != 'y':
                sys.exit(1)

        # Step 3: Install packages in venv
        if not install_packages(venv_dir):
            print_colored("\n⚠️  Warning: Some packages failed to install.", Colors.YELLOW)
            proceed = input("   Continue anyway? (y/n): ").strip().lower()
            if proceed != 'y':
                sys.exit(1)

        # Step 4: Validate paths
        if not validate_paths():
            print_colored("\n⚠️  Warning: Some required files are missing.", Colors.YELLOW)
            proceed = input("   Continue anyway? (y/n): ").strip().lower()
            if proceed != 'y':
                sys.exit(1)

        # Step 5: Select and run app
        while True:
            choice = select_app()

            if choice == 1:
                run_flask_app(venv_dir)
            elif choice == 2:
                run_streamlit_app(venv_dir)
            elif choice == 3:
                run_cli_tool(venv_dir)
            elif choice == 4:
                uninstall()
                print_colored("\n   👋 Goodbye!", Colors.BLUE)
                break
            elif choice == 5:
                print_colored("\n   👋 Goodbye!", Colors.BLUE)
                break

            # Ask if user wants to run another app
            print_colored("\n" + "="*60, Colors.BLUE)
            again = input("\n   Run another app? (y/n): ").strip().lower()
            if again != 'y':
                print_colored("\n   👋 Goodbye!", Colors.BLUE)
                break

    except KeyboardInterrupt:
        print_colored("\n\n   👋 Goodbye!", Colors.BLUE)
        sys.exit(0)
    except Exception as e:
        print_colored(f"\n   ❌ Unexpected error: {e}", Colors.RED)
        sys.exit(1)

if __name__ == "__main__":
    main()
