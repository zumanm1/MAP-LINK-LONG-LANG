# Cross-Platform Setup Guide

## 🌍 Platform Compatibility

This application works on:
- ✅ **macOS** (Intel & Apple Silicon)
- ✅ **Windows** (10, 11)
- ✅ **Linux** (Ubuntu, Debian, Fedora, etc.)

All file paths use `pathlib.Path` for cross-platform compatibility.

---

## 🚀 Quick Start by Platform

### **macOS / Linux**

#### **Method 1: Using Shell Scripts (Recommended)**

```bash
# For Flask app
./run_flask.sh

# For Streamlit app
./run_streamlit.sh
```

#### **Method 2: Manual Setup**

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run Flask app
python flask_app.py

# OR run Streamlit app
streamlit run app.py
```

---

### **Windows**

#### **Method 1: Using Batch Scripts (Recommended)**

```cmd
REM For Flask app
run_flask.bat

REM For Streamlit app
run_streamlit.bat
```

#### **Method 2: Manual Setup**

```cmd
REM 1. Create virtual environment
python -m venv venv

REM 2. Activate virtual environment
venv\Scripts\activate.bat

REM 3. Install dependencies
pip install -r requirements.txt

REM 4. Run Flask app
python flask_app.py

REM OR run Streamlit app
streamlit run app.py
```

---

## 📁 File Path Compatibility

### **Implementation**

The Flask app uses `pathlib.Path` for all file operations:

```python
from pathlib import Path

# Get base directory (works on all platforms)
BASE_DIR = Path(__file__).resolve().parent

# Create directories (cross-platform)
UPLOAD_FOLDER = BASE_DIR / 'uploads'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# File operations (cross-platform)
upload_path = UPLOAD_FOLDER / f"{session_id}_{filename}"
df.to_excel(str(upload_path), index=False)
```

### **Why pathlib?**

| Operation | Old Way (os.path) | New Way (pathlib) |
|-----------|-------------------|-------------------|
| Join paths | `os.path.join('uploads', file)` | `Path('uploads') / file` |
| Create dir | `os.makedirs('uploads', exist_ok=True)` | `Path('uploads').mkdir(exist_ok=True)` |
| Check exists | `os.path.exists(path)` | `Path(path).exists()` |
| Get parent | `os.path.dirname(path)` | `Path(path).parent` |
| Resolve | `os.path.abspath(path)` | `Path(path).resolve()` |

**Benefits:**
- ✅ Automatic path separator handling (`/` on Unix, `\` on Windows)
- ✅ Object-oriented API (cleaner code)
- ✅ Better path manipulation
- ✅ Cross-platform by default

---

## 🐍 Python Version Requirements

### **Minimum Version: Python 3.11**

Check your Python version:

```bash
# macOS / Linux
python3 --version

# Windows
python --version
```

### **Installing Python**

#### **macOS**

```bash
# Using Homebrew
brew install python@3.11

# OR download from python.org
# https://www.python.org/downloads/macos/
```

#### **Windows**

```cmd
REM Download installer from python.org
REM https://www.python.org/downloads/windows/

REM Make sure to check "Add Python to PATH" during installation
```

#### **Linux (Ubuntu/Debian)**

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

---

## 📦 Virtual Environment Setup

### **Why Use Virtual Environments?**

- ✅ Isolate project dependencies
- ✅ Avoid conflicts with system Python
- ✅ Easy to replicate on different machines
- ✅ Clean uninstall (just delete `venv/` folder)

### **Creating Virtual Environment**

#### **macOS / Linux**

```bash
# Create
python3 -m venv venv

# Activate
source venv/bin/activate

# Deactivate (when done)
deactivate
```

#### **Windows**

```cmd
REM Create
python -m venv venv

REM Activate
venv\Scripts\activate.bat

REM Deactivate (when done)
deactivate
```

### **Verifying Activation**

When activated, your terminal prompt should show `(venv)`:

```bash
(venv) user@computer:~/MAP-LINK-LONG-LANG$
```

---

## 🔧 Troubleshooting by Platform

### **macOS**

#### **"command not found: python3"**

```bash
# Install Python via Homebrew
brew install python@3.11

# OR use python.org installer
```

#### **"Permission denied: ./run_flask.sh"**

```bash
# Make script executable
chmod +x run_flask.sh run_streamlit.sh
```

#### **SSL Certificate Error (for URL resolution)**

```bash
# Install certificates
/Applications/Python\ 3.11/Install\ Certificates.command
```

---

### **Windows**

#### **"python is not recognized as internal or external command"**

**Solution 1: Add Python to PATH manually**
1. Search for "Environment Variables" in Start Menu
2. Edit "Path" variable
3. Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python311`
4. Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts`
5. Restart terminal

**Solution 2: Reinstall Python**
- Download installer from python.org
- Check "Add Python to PATH" during installation

#### **"cannot be loaded because running scripts is disabled"**

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### **ModuleNotFoundError after installation**

```cmd
REM Make sure virtual environment is activated
venv\Scripts\activate.bat

REM Reinstall dependencies
pip install -r requirements.txt
```

---

### **Linux**

#### **"No module named 'venv'"**

```bash
# Ubuntu/Debian
sudo apt install python3.11-venv

# Fedora
sudo dnf install python3-venv
```

#### **"No module named 'tkinter'" (for Streamlit)**

```bash
# Ubuntu/Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

#### **Permission issues with directories**

```bash
# Fix ownership
sudo chown -R $USER:$USER .

# OR use home directory
cd ~/MAP-LINK-LONG-LANG
```

---

## 🌐 Port Conflicts

### **Flask (Port 5000)**

If port 5000 is already in use:

#### **macOS / Linux**

```bash
# Find process using port 5000
lsof -ti:5000

# Kill process
kill -9 $(lsof -ti:5000)

# OR change port in flask_app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

#### **Windows**

```cmd
REM Find process using port 5000
netstat -ano | findstr :5000

REM Kill process (replace PID with actual PID)
taskkill /PID <PID> /F

REM OR change port in flask_app.py
```

### **Streamlit (Port 8501)**

Streamlit automatically finds available ports, but you can specify:

```bash
streamlit run app.py --server.port 8502
```

---

## 📊 File Paths in Output

### **Path Representation**

The application handles paths internally using `pathlib.Path`, which automatically uses the correct separator for your OS:

- **macOS/Linux**: `/Users/john/uploads/file.xlsx`
- **Windows**: `C:\Users\John\uploads\file.xlsx`

All paths are converted to strings when needed:

```python
# Internal: Path object
upload_path = BASE_DIR / 'uploads' / 'file.xlsx'

# External: String (for pandas, etc.)
df.to_excel(str(upload_path))
```

---

## 🔐 Security Considerations by Platform

### **All Platforms**

```python
# ✅ Secure filename sanitization (cross-platform)
from werkzeug.utils import secure_filename
filename = secure_filename(user_upload.filename)

# ✅ Prevent directory traversal
# Werkzeug ensures filenames don't contain ../
```

### **Windows-Specific**

```python
# ✅ Handle reserved names
# Werkzeug handles: CON, PRN, AUX, NUL, COM1-9, LPT1-9
```

### **Unix-Specific**

```python
# ✅ Handle hidden files
# Werkzeug removes leading dots from filenames
```

---

## 📦 Dependencies by Platform

### **All Platforms**

```txt
pandas==2.0.3          # Data manipulation
openpyxl==3.1.2        # Excel I/O
requests==2.31.0       # HTTP requests
pytest==7.4.0          # Testing
streamlit==1.28.0      # Streamlit framework
Flask==3.0.0           # Flask framework
Werkzeug==3.0.1        # WSGI utilities
```

### **Additional Windows Requirements**

Some packages may require Microsoft C++ Build Tools:
- Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/

### **Additional macOS Requirements**

If you encounter SSL issues:
```bash
pip install certifi
```

---

## 🧪 Testing Cross-Platform

### **Run Tests**

```bash
# All platforms
pytest tests/

# Verbose output
pytest tests/ -v

# Specific test
pytest tests/test_map_converter.py::TestExtractCoordinates
```

### **Test File Paths**

```bash
# Create test directory structure
mkdir -p uploads processed

# Test with sample file
python map_converter.py test_input.xlsx test_output.xlsx
```

---

## 🚢 Deployment Considerations

### **macOS/Linux Production**

```bash
# Use Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 flask_app:app
```

### **Windows Production**

```cmd
REM Use Waitress
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 flask_app:app
```

### **Cross-Platform (Docker)**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "flask_app.py"]
```

---

## 📝 Environment Variables

### **Setting Environment Variables**

#### **macOS / Linux**

```bash
# Temporary (current session)
export SECRET_KEY="your-secret-key-here"

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export SECRET_KEY="your-secret-key-here"' >> ~/.bashrc
source ~/.bashrc
```

#### **Windows**

```cmd
REM Temporary (current session)
set SECRET_KEY=your-secret-key-here

REM Permanent (System Properties)
1. Search "Environment Variables"
2. Add new variable: SECRET_KEY
3. Value: your-secret-key-here
4. Restart terminal
```

---

## 🎯 Platform-Specific Features

### **macOS**

- ✅ Supports Apple Silicon (M1/M2/M3) natively
- ✅ Uses zsh by default (macOS Catalina+)
- ✅ Homebrew for package management

### **Windows**

- ✅ Works with Command Prompt, PowerShell, and WSL
- ✅ Batch scripts for easy startup
- ✅ Windows Defender may scan uploaded files (expected)

### **Linux**

- ✅ Works on all major distributions
- ✅ Systemd service files available (optional)
- ✅ Can run as non-root user

---

## 🆘 Getting Help

### **Check Python Installation**

```bash
# All platforms
python --version  # or python3 --version
pip --version     # or pip3 --version
```

### **Check Dependencies**

```bash
pip list
pip show flask
pip show pandas
```

### **Verify File Paths**

```python
# Run in Python REPL
from pathlib import Path
print(Path(__file__).resolve().parent)
```

---

## ✅ Pre-Flight Checklist

Before running the app on a new machine:

- [ ] Python 3.11+ installed
- [ ] pip installed and updated (`pip install --upgrade pip`)
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Directories created (`uploads/`, `processed/`)
- [ ] Test file available (`test_input.xlsx`)
- [ ] Port 5000 (Flask) or 8501 (Streamlit) available
- [ ] Internet connection (for URL resolution)

---

## 🎓 Summary

**Key Points:**
1. Use `pathlib.Path` for all file operations (cross-platform)
2. Virtual environments isolate dependencies
3. Startup scripts automate setup on all platforms
4. All file paths are relative to project root
5. Works identically on macOS, Windows, and Linux

**No hardcoded paths = Works everywhere! 🌍**
