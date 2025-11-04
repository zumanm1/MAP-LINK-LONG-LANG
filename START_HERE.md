# 🚀 START HERE - Quick Start Guide

## One-Command Setup (All Platforms)

```bash
python run.py
```

That's it! The script will:
1. ✅ Check Python version (3.11+ required)
2. ✅ Install all required packages automatically
3. ✅ Validate file paths and create directories
4. ✅ Show interactive menu to choose app

---

## 📋 What You Get

```
🗺️  Excel Map Coordinates Converter
========================================

Select application to run:
   1. Flask Web App (http://localhost:5000)
   2. Streamlit Web App (http://localhost:8501)
   3. CLI Tool (Command line)
   4. Exit
```

---

## 🖥️ Platform-Specific Instructions

### **macOS / Linux**

```bash
# Clone the repository
git clone https://github.com/zumanm1/MAP-LINK-LONG-LANG.git
cd MAP-LINK-LONG-LANG

# Run the launcher
python3 run.py
```

### **Windows**

```cmd
REM Clone the repository
git clone https://github.com/zumanm1/MAP-LINK-LONG-LANG.git
cd MAP-LINK-LONG-LANG

REM Run the launcher
python run.py
```

---

## 📝 What Happens When You Run It

### **Step 1: Python Version Check**
```
🔍 Checking Python version...
   ✅ Python 3.11.5
```

### **Step 2: Package Installation**
```
📦 Installing required packages...
   ✅ All packages installed successfully
```

Installs:
- Flask (web framework)
- Streamlit (data app framework)
- pandas (Excel processing)
- openpyxl (Excel I/O)
- requests (URL resolution)
- pytest (testing)

### **Step 3: Path Validation**
```
📁 Validating directory structure...
   ✅ uploads/ - Created/Verified
   ✅ processed/ - Created/Verified
   ✅ static/ - Found
   ✅ templates/ - Found

📄 Checking required files...
   ✅ map_converter.py - Core conversion logic
   ✅ flask_app.py - Flask web application
   ✅ app.py - Streamlit web application
```

### **Step 4: Choose Your App**

#### **Option 1: Flask Web App**
```
🌐 Starting Flask Web Server...
   Access the app at: http://localhost:5000
   Press Ctrl+C to stop
```

Features:
- Modern dark theme UI
- Detailed processing log
- RESTful API endpoints
- Download processed files

#### **Option 2: Streamlit Web App**
```
🌐 Starting Streamlit Web Server...
   The app will open in your browser automatically
   Press Ctrl+C to stop
```

Features:
- Clean, minimal interface
- Real-time updates
- Interactive data tables
- Perfect for data scientists

#### **Option 3: CLI Tool**
```
💻 Command Line Tool
   Usage: python map_converter.py <input.xlsx> <output.xlsx>

   📝 Test file found: test_input.xlsx
   Run test conversion? (y/n): y

   ✅ Output saved to: test_output_new.xlsx
```

---

## 🎯 First-Time User Workflow

### **Step 1: Clone & Run**
```bash
git clone https://github.com/zumanm1/MAP-LINK-LONG-LANG.git
cd MAP-LINK-LONG-LANG
python run.py
```

### **Step 2: Choose Flask App (Option 1)**
The launcher will install packages and start Flask.

### **Step 3: Open Browser**
Navigate to: `http://localhost:5000`

### **Step 4: Upload Your Excel File**
File must have:
- `Name` column (location name)
- `Region` column (geographic region)
- `Maps` or `Map link` column (Google Maps URLs)

### **Step 5: Extract Coordinates**
Click "🔄 Extract Coordinates" button.

### **Step 6: Download Results**
Click "⬇️ Download Processed File" to get your Excel file with coordinates.

---

## 📊 Example Input/Output

### **Input Excel File**
| Name | Region | Maps | LONG | LATTs |
|------|--------|------|------|-------|
| Sandton City | Johannesburg | https://maps.app.goo.gl/baixEU9UxYHX8Yox7 | | |
| Times Square | New York | https://www.google.com/maps/@40.7580,-73.9855,17z | | |

### **Output Excel File**
| Name | Region | Maps | LONG | LATTs |
|------|--------|------|------|-------|
| Sandton City | Johannesburg | https://maps.app.goo.gl/baixEU9UxYHX8Yox7 | 28.052706 | -26.108204 |
| Times Square | New York | https://www.google.com/maps/@40.7580,-73.9855,17z | -73.9855 | 40.7580 |

---

## 🔧 Troubleshooting

### **"Python 3.11+ required"**
Install Python 3.11 or higher:
- macOS: `brew install python@3.11`
- Windows: Download from python.org
- Linux: `sudo apt install python3.11`

### **"Error installing packages"**
Try manually:
```bash
pip install -r requirements.txt
```

### **"Address already in use"**
Port 5000 or 8501 is busy. Either:
- Close other applications using that port
- The launcher will show the error and return to menu

### **"No module named 'flask'"**
The launcher should install packages automatically.
If it fails, run:
```bash
pip install Flask==3.0.0
```

---

## 🌟 Pro Tips

### **Tip 1: Run Multiple Times**
After running Flask or Streamlit, the launcher will ask:
```
Run another app? (y/n):
```
Choose `y` to try a different app without restarting.

### **Tip 2: Test Mode**
Choose Option 3 (CLI Tool) to quickly test with sample data:
```
Run test conversion? (y/n): y
```

### **Tip 3: No Virtual Environment Needed**
The `run.py` script works with your system Python.
Packages are installed globally (or in user directory).

If you prefer isolation, create a virtual environment first:
```bash
# Create venv
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate.bat

# Then run launcher
python run.py
```

---

## 📚 Next Steps

After successfully running the app:

1. **Read Full Documentation**
   - [FLASK_GUIDE.md](FLASK_GUIDE.md) - Flask technical details
   - [QUICK_START.md](QUICK_START.md) - Code explanations
   - [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md) - Error handling

2. **Customize**
   - Modify `static/css/style.css` for custom themes
   - Edit `flask_app.py` for additional features
   - Add new URL patterns in `map_converter.py`

3. **Deploy**
   - See [FLASK_GUIDE.md](FLASK_GUIDE.md#deployment) for production options
   - Docker, Heroku, AWS, Azure all supported

---

## 🎓 Understanding the Project Structure

```
MAP-LINK-LONG-LANG/
├── run.py              ← START HERE! Python launcher
│
├── map_converter.py    ← Core coordinate extraction
├── flask_app.py        ← Flask web app
├── app.py              ← Streamlit web app
│
├── templates/          ← HTML templates (Flask)
├── static/             ← CSS/JS files (Flask)
│
├── uploads/            ← Temp uploaded files (auto-created)
├── processed/          ← Output files (auto-created)
│
└── docs/               ← Documentation
    ├── FLASK_GUIDE.md
    ├── QUICK_START.md
    ├── VALIDATION_GUIDE.md
    └── CROSS_PLATFORM_GUIDE.md
```

---

## ✅ Success Indicators

You'll know it's working when you see:

### **Flask App**
```
🌐 Starting Flask Web Server...
   Access the app at: http://localhost:5000
   Press Ctrl+C to stop

 * Serving Flask app 'flask_app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

### **Streamlit App**
```
🌐 Starting Streamlit Web Server...

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501
```

---

## 🆘 Still Need Help?

1. **Check Python Version**
   ```bash
   python --version
   # Should show 3.11.0 or higher
   ```

2. **Check pip**
   ```bash
   pip --version
   # Should show pip 23.0 or higher
   ```

3. **Manual Package Install**
   ```bash
   pip install -r requirements.txt
   ```

4. **GitHub Issues**
   Report issues at: https://github.com/zumanm1/MAP-LINK-LONG-LANG/issues

---

## 🎉 You're All Set!

The `run.py` launcher handles everything automatically.
Just run it and choose your app!

```bash
python run.py
```

**Happy Mapping! 🗺️**
