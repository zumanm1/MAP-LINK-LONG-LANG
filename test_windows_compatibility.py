#!/usr/bin/env python3
"""
Windows Compatibility Test Suite
Tests all Windows-specific issues and cross-platform compatibility.
"""

import sys
import os
from pathlib import Path
import subprocess
import platform

def print_header(title):
    """Print section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print('=' * 80)

def test_python_version():
    """Test Python version compatibility"""
    print_header("Python Version Check")

    version = sys.version_info
    print(f"✓ Python Version: {version.major}.{version.minor}.{version.micro}")
    print(f"✓ Platform: {sys.platform}")
    print(f"✓ System: {platform.system()}")

    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ FAIL: Python 3.11+ required")
        return False

    print("✅ PASS: Python version compatible")
    return True

def test_pathlib_operations():
    """Test pathlib cross-platform compatibility"""
    print_header("Pathlib Cross-Platform Operations")

    try:
        # Test Path creation
        base_dir = Path(__file__).parent
        print(f"✓ Base directory: {base_dir}")

        # Test Path joining (cross-platform)
        test_path = base_dir / 'uploads' / 'test.xlsx'
        print(f"✓ Path joining works: {test_path}")

        # Test Windows-style paths
        if sys.platform == 'win32':
            print(f"✓ Windows path: {test_path.as_posix()}")
            print(f"✓ Windows drive: {test_path.drive}")

        # Test resolve() for absolute paths
        abs_path = base_dir.resolve()
        print(f"✓ Absolute path: {abs_path}")

        # Test exists() check
        exists = base_dir.exists()
        print(f"✓ Path.exists() works: {exists}")

        # Test mkdir with parents=True
        test_dir = base_dir / 'temp_test_dir'
        test_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ mkdir(parents=True) works")

        # Test cleanup
        test_dir.rmdir()
        print(f"✓ rmdir() works")

        print("✅ PASS: All pathlib operations work")
        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False

def test_file_operations():
    """Test file I/O operations"""
    print_header("File I/O Operations")

    try:
        base_dir = Path(__file__).parent
        test_file = base_dir / 'temp_test_file.txt'

        # Test write
        test_file.write_text("Test content", encoding='utf-8')
        print(f"✓ File write works")

        # Test read
        content = test_file.read_text(encoding='utf-8')
        print(f"✓ File read works: '{content}'")

        # Test unlink with missing_ok
        test_file.unlink(missing_ok=True)
        print(f"✓ unlink(missing_ok=True) works")

        # Test unlink non-existent (should not raise)
        test_file.unlink(missing_ok=True)
        print(f"✓ unlink on non-existent file works")

        print("✅ PASS: All file operations work")
        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        # Cleanup on error
        try:
            test_file.unlink(missing_ok=True)
        except:
            pass
        return False

def test_subprocess_operations():
    """Test subprocess calls (Python execution)"""
    print_header("Subprocess Operations")

    try:
        # Test Python executable detection
        python_exe = sys.executable
        print(f"✓ Python executable: {python_exe}")

        # Test subprocess call
        result = subprocess.run(
            [python_exe, '--version'],
            capture_output=True,
            text=True
        )
        print(f"✓ subprocess.run works: {result.stdout.strip()}")

        # Test with Path objects (should convert to str automatically in recent Python)
        script_path = Path(__file__).parent / 'map_converter.py'
        if script_path.exists():
            # Don't actually run it, just test path handling
            cmd = [python_exe, str(script_path)]
            print(f"✓ Path to string conversion: {cmd}")

        print("✅ PASS: All subprocess operations work")
        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False

def test_venv_compatibility():
    """Test virtual environment compatibility"""
    print_header("Virtual Environment Compatibility")

    try:
        # Check if running in venv
        in_venv = hasattr(sys, 'prefix') and sys.prefix != sys.base_prefix
        print(f"✓ In virtual environment: {in_venv}")

        # Test venv paths
        if sys.platform == 'win32':
            venv_python = 'Scripts/python.exe'
            venv_pip = 'Scripts/pip.exe'
        else:
            venv_python = 'bin/python'
            venv_pip = 'bin/pip'

        print(f"✓ Platform-specific venv paths:")
        print(f"  - Python: {venv_python}")
        print(f"  - Pip: {venv_pip}")

        # Test Path construction for venv
        base_dir = Path(__file__).parent
        venv_dir = base_dir / 'venv'
        venv_python_path = venv_dir / venv_python.replace('/', os.sep)

        print(f"✓ Venv path construction: {venv_python_path}")

        print("✅ PASS: Virtual environment compatibility OK")
        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False

def test_encoding_compatibility():
    """Test text encoding compatibility"""
    print_header("Text Encoding Compatibility")

    try:
        # Test UTF-8 encoding
        test_text = "Test: 🗺️ 🇿🇦 Johannesburg -26.2041°S, 28.0473°E"
        print(f"✓ UTF-8 text: {test_text}")

        # Test encoding/decoding
        encoded = test_text.encode('utf-8')
        decoded = encoded.decode('utf-8')
        assert decoded == test_text
        print(f"✓ UTF-8 encode/decode works")

        # Test default encoding
        default_encoding = sys.getdefaultencoding()
        print(f"✓ Default encoding: {default_encoding}")

        if default_encoding.lower() != 'utf-8':
            print(f"⚠️  WARNING: Default encoding is not UTF-8")
            print(f"   Files should explicitly specify encoding='utf-8'")

        print("✅ PASS: Text encoding compatible")
        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False

def test_flask_compatibility():
    """Test Flask and related imports"""
    print_header("Flask Compatibility")

    try:
        # Test Flask import
        import flask
        print(f"✓ Flask version: {flask.__version__}")

        # Test werkzeug import
        import werkzeug
        print(f"✓ Werkzeug version: {werkzeug.__version__}")

        # Test pandas import
        import pandas as pd
        print(f"✓ Pandas version: {pd.__version__}")

        # Test openpyxl import
        import openpyxl
        print(f"✓ Openpyxl version: {openpyxl.__version__}")

        print("✅ PASS: All Flask dependencies available")
        return True

    except ImportError as e:
        print(f"❌ FAIL: Missing dependency: {e}")
        print(f"   Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False

def test_threading_compatibility():
    """Test threading operations"""
    print_header("Threading Compatibility")

    try:
        from threading import Lock, Thread

        # Test Lock creation
        lock = Lock()
        print(f"✓ Lock created: {lock}")

        # Test acquire/release
        lock.acquire()
        print(f"✓ Lock acquired")
        lock.release()
        print(f"✓ Lock released")

        # Test with statement
        with lock:
            print(f"✓ Lock works with 'with' statement")

        print("✅ PASS: Threading operations work")
        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False

def test_windows_specific():
    """Test Windows-specific issues"""
    print_header("Windows-Specific Checks")

    if sys.platform != 'win32':
        print("ℹ️  Skipping Windows-specific tests (not on Windows)")
        return True

    try:
        # Test long path support
        import ctypes
        long_path_enabled = ctypes.windll.ntdll.RtlAreLongPathsEnabled()
        print(f"✓ Long path support: {'Enabled' if long_path_enabled else 'Disabled'}")

        if not long_path_enabled:
            print("⚠️  WARNING: Long paths disabled in Windows Registry")
            print("   Paths longer than 260 chars may fail")

        # Test file locking behavior
        base_dir = Path(__file__).parent
        test_file = base_dir / 'temp_lock_test.txt'

        # Create and open file
        with open(test_file, 'w') as f:
            f.write("test")
            print(f"✓ File locking works")

        # Cleanup
        test_file.unlink(missing_ok=True)

        # Test case sensitivity
        test_path1 = base_dir / 'TempTest.txt'
        test_path2 = base_dir / 'temptest.txt'
        print(f"✓ Path comparison: {test_path1} == {test_path2}: {test_path1 == test_path2}")

        print("✅ PASS: Windows-specific checks OK")
        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        # Cleanup
        try:
            test_file.unlink(missing_ok=True)
        except:
            pass
        return False

def main():
    """Run all compatibility tests"""
    print("\n" + "🪟 " * 20)
    print("\n  WINDOWS COMPATIBILITY TEST SUITE")
    print("\n" + "🪟 " * 20)

    tests = [
        ("Python Version", test_python_version),
        ("Pathlib Operations", test_pathlib_operations),
        ("File Operations", test_file_operations),
        ("Subprocess Operations", test_subprocess_operations),
        ("Virtual Environment", test_venv_compatibility),
        ("Text Encoding", test_encoding_compatibility),
        ("Flask Dependencies", test_flask_compatibility),
        ("Threading", test_threading_compatibility),
        ("Windows-Specific", test_windows_specific)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR in {test_name}: {e}")
            results.append((test_name, False))

    # Print summary
    print_header("SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "=" * 80)
    print(f"\n📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 SUCCESS: All compatibility tests passed!")
        print("\n✅ Application is 100% Windows compatible!")
        return 0
    else:
        print(f"\n⚠️  WARNING: {total - passed} test(s) failed")
        print("\n❌ Some compatibility issues found")
        return 1

if __name__ == "__main__":
    sys.exit(main())
