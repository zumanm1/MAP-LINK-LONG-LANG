#!/usr/bin/env python3
"""
Cross-Platform Launcher for Excel Map Coordinates Converter
Handles virtual environment creation, package installation, path validation, and app startup.
Works on macOS, Windows, and Linux.
"""

import sys
import subprocess
import os
import time
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
        print_colored("   📦 Creating virtual environment (this may take 10-30 seconds)...", Colors.YELLOW)
        print_colored("   ⏳ Please wait, running: python -m venv venv\n", Colors.BLUE)

        # Use Popen to show we're still alive during creation
        process = subprocess.Popen(
            [sys.executable, '-m', 'venv', str(venv_dir)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Wait and show dots to indicate progress
        while process.poll() is None:
            print(".", end="", flush=True)
            time.sleep(0.5)

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args)

        print()  # New line after dots
        print_colored("   ✅ Virtual environment created successfully", Colors.GREEN)
        return venv_dir
    except subprocess.CalledProcessError as e:
        print_colored(f"\n   ❌ Error creating virtual environment: {e}", Colors.RED)
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

def check_uv_available():
    """Check if uv is available in system"""
    try:
        subprocess.run(['uv', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_packages(venv_dir):
    """Install required packages in virtual environment using uv or pip"""
    print_colored("\n📦 Installing required packages...", Colors.BLUE)

    base_dir = Path(__file__).parent
    requirements_file = base_dir / 'requirements.txt'

    if not requirements_file.exists():
        print_colored("   ❌ Error: requirements.txt not found!", Colors.RED)
        return False

    # Check if uv is available (much faster than pip)
    use_uv = check_uv_available()

    if use_uv:
        print_colored("   ⚡ Using uv (fast package installer)", Colors.GREEN)
        print_colored("   📥 Installing dependencies with verbose output...\n", Colors.YELLOW)

        try:
            # Use uv pip install with verbose output
            subprocess.check_call(
                ['uv', 'pip', 'install', '-r', str(requirements_file), '--python', str(get_venv_python(venv_dir))],
                # NO stdout/stderr suppression - show everything!
            )
            print_colored("\n   ✅ All packages installed successfully with uv", Colors.GREEN)
            return True
        except subprocess.CalledProcessError as e:
            print_colored(f"\n   ❌ Error with uv: {e}", Colors.RED)
            print_colored("   💡 Falling back to pip...", Colors.YELLOW)
            use_uv = False

    if not use_uv:
        print_colored("   🐍 Using pip (standard installer)", Colors.BLUE)
        print_colored("   💡 Install uv for faster installs: pip install uv", Colors.YELLOW)
        print_colored("   📥 Installing dependencies with verbose output...\n", Colors.YELLOW)

        pip_path = get_venv_pip(venv_dir)

        try:
            # Use pip with VERBOSE output (no -q, no DEVNULL)
            subprocess.check_call(
                [str(pip_path), 'install', '-r', str(requirements_file)],
                # NO stdout/stderr suppression - show everything!
            )
            print_colored("\n   ✅ All packages installed successfully with pip", Colors.GREEN)
            return True
        except subprocess.CalledProcessError as e:
            print_colored(f"\n   ❌ Error installing packages: {e}", Colors.RED)
            print_colored("   💡 Try manually: pip install -r requirements.txt", Colors.YELLOW)
            return False

def install_packages_system():
    """Install packages to system Python (fallback when venv fails)"""
    print_colored("\n📦 Installing packages to system Python...", Colors.BLUE)

    base_dir = Path(__file__).parent
    requirements_file = base_dir / 'requirements.txt'

    if not requirements_file.exists():
        print_colored("   ❌ Error: requirements.txt not found!", Colors.RED)
        return False

    # Check if uv is available
    use_uv = check_uv_available()

    if use_uv:
        print_colored("   ⚡ Using uv (fast package installer)", Colors.GREEN)
        print_colored("   📥 Installing dependencies to user directory (no admin needed)...\n", Colors.YELLOW)

        try:
            subprocess.check_call(
                ['uv', 'pip', 'install', '-r', str(requirements_file), '--user'],
            )
            print_colored("\n   ✅ All packages installed successfully with uv", Colors.GREEN)
            return True
        except subprocess.CalledProcessError as e:
            print_colored(f"\n   ❌ Error with uv: {e}", Colors.RED)
            print_colored("   💡 Falling back to pip...", Colors.YELLOW)
            use_uv = False

    if not use_uv:
        print_colored("   🐍 Using pip (standard installer)", Colors.BLUE)
        print_colored("   📥 Installing dependencies to user directory (no admin needed)...\n", Colors.YELLOW)

        try:
            # Use --user flag to install to user directory (no admin needed!)
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '--user', '-r', str(requirements_file)],
            )
            print_colored("\n   ✅ All packages installed successfully with pip", Colors.GREEN)
            return True
        except subprocess.CalledProcessError as e:
            print_colored(f"\n   ❌ Error installing packages: {e}", Colors.RED)
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
            # Create if doesn't exist (with error handling for Windows)
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print_colored(f"   ✅ {dir_name}/ - Created/Verified", Colors.GREEN)
            except PermissionError:
                print_colored(f"   ⚠️  {dir_name}/ - Permission denied (will create at runtime)", Colors.YELLOW)
            except Exception as e:
                print_colored(f"   ⚠️  {dir_name}/ - Could not create: {e}", Colors.YELLOW)
        elif dir_path.exists():
            print_colored(f"   ✅ {dir_name}/ - Found", Colors.GREEN)
        else:
            print_colored(f"   ⚠️  {dir_name}/ - Not found (optional)", Colors.YELLOW)

    # Validate required files
    print_colored("\n📄 Checking required files...", Colors.BLUE)
    required_files = {
        'map_converter.py': 'Core conversion logic',
        'flask_app.py': 'Flask web application'
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
    print("   2. CLI Tool (Command line)")
    print("   3. Uninstall (Remove virtual environment)")
    print("   4. Exit")

    while True:
        try:
            choice = input("\n   Enter choice (1-4): ").strip()

            if choice in ['1', '2', '3', '4']:
                return int(choice)
            else:
                print_colored("   ⚠️  Invalid choice. Please enter 1-4.", Colors.YELLOW)
        except KeyboardInterrupt:
            print_colored("\n\n   👋 Goodbye!", Colors.BLUE)
            sys.exit(0)

def run_flask_app(venv_dir):
    """Run Flask application using venv or system Python"""
    print_colored("\n🌐 Starting Flask Web Server...", Colors.GREEN)
    print_colored("   Access the app at: http://localhost:5000", Colors.BOLD + Colors.GREEN)
    print_colored("   Press Ctrl+C to stop\n", Colors.YELLOW)

    base_dir = Path(__file__).parent
    flask_app = base_dir / 'flask_app.py'

    # Use venv Python if available, otherwise system Python
    if venv_dir:
        python_path = get_venv_python(venv_dir)
    else:
        python_path = sys.executable
        print_colored("   ℹ️  Using system Python", Colors.BLUE)

    try:
        subprocess.run([str(python_path), str(flask_app)])
    except KeyboardInterrupt:
        print_colored("\n\n   ⏹️  Flask server stopped.", Colors.YELLOW)

def run_cli_tool(venv_dir):
    """Run CLI tool using venv or system Python"""
    print_colored("\n💻 Command Line Tool", Colors.GREEN)
    print_colored("   Usage: python map_converter.py <input.xlsx> <output.xlsx>\n", Colors.YELLOW)

    base_dir = Path(__file__).parent

    # Use venv Python if available, otherwise system Python
    if venv_dir:
        python_path = get_venv_python(venv_dir)
    else:
        python_path = sys.executable
        print_colored("   ℹ️  Using system Python", Colors.BLUE)

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
        use_system_python = False

        if not venv_dir:
            print_colored("\n⚠️  Warning: Could not create virtual environment.", Colors.YELLOW)
            print_colored("   💡 This can happen on Windows with restricted permissions.", Colors.BLUE)
            print_colored("   📌 Options:", Colors.BLUE)
            print_colored("      1. Install packages to system Python (easier)", Colors.YELLOW)
            print_colored("      2. Exit and run as Administrator", Colors.YELLOW)

            choice = input("\n   Install to system Python? (y/n): ").strip().lower()
            if choice == 'y':
                print_colored("\n   ✅ Will install packages to system Python", Colors.GREEN)
                use_system_python = True
                venv_dir = None  # Signal to use system Python
            else:
                print_colored("\n   ❌ Exiting. Please run as Administrator and try again.", Colors.RED)
                sys.exit(1)

        # Step 3: Install packages (in venv or system Python)
        if use_system_python:
            print_colored("\n📦 Installing packages to system Python...", Colors.BLUE)
            if not install_packages_system():
                print_colored("\n⚠️  Warning: Some packages failed to install.", Colors.YELLOW)
                proceed = input("   Continue anyway? (y/n): ").strip().lower()
                if proceed != 'y':
                    sys.exit(1)
        elif venv_dir:
            if not install_packages(venv_dir):
                print_colored("\n⚠️  Warning: Some packages failed to install.", Colors.YELLOW)
                print_colored("   💡 Try installing to system Python instead.", Colors.YELLOW)
                choice = input("   Try system Python? (y/n): ").strip().lower()
                if choice == 'y':
                    use_system_python = True
                    venv_dir = None
                    if not install_packages_system():
                        print_colored("\n❌ Installation failed. Exiting.", Colors.RED)
                        sys.exit(1)
                else:
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
                run_cli_tool(venv_dir)
            elif choice == 3:
                uninstall()
                print_colored("\n   👋 Goodbye!", Colors.BLUE)
                break
            elif choice == 4:
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
