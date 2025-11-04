# 🚨 WINDOWS "ACCESS DENIED" FIX - run.py

**Date**: 2025-11-04
**Problem**: Getting "Access Denied" error when running `python run.py` on Windows
**Status**: ✅ **MULTIPLE SOLUTIONS AVAILABLE**

---

## 🎯 QUICK FIX (TRY THIS FIRST)

### Move Project to User Folder

**Windows blocks Python from writing to certain folders.**

**Solution**: Move your project to a user-writable location:

```cmd
REM Move to Documents
move C:\...\MAP-LINK-LONG-LANG C:\Users\YourName\Documents\

REM Navigate there
cd C:\Users\YourName\Documents\MAP-LINK-LONG-LANG

REM Run app
python run.py
```

**Why this works**: Your Documents folder has full write permissions!

---

## 🔍 WHAT'S HAPPENING?

When you run `python run.py`, the app tries to:

1. ✅ Check Python version → **No permissions needed**
2. 🔴 **Create `venv/` folder** → **NEEDS WRITE PERMISSION**
3. 🔴 **Install packages** → **NEEDS WRITE PERMISSION**
4. 🔴 **Create `uploads/` and `processed/` folders** → **NEEDS WRITE PERMISSION**
5. ✅ Run Flask app → Usually OK

**If you get "Access Denied", it's failing at steps 2-4.**

---

## 🚫 WHERE NOT TO PUT THE PROJECT

**These folders are PROTECTED on Windows:**

❌ `C:\Program Files\...`
❌ `C:\Windows\...`
❌ `C:\` (root directory)
❌ Network drives without write access
❌ USB drives with read-only mode

**Error you'll see:**
```
Permission denied when accessing project directory
```

---

## ✅ WHERE TO PUT THE PROJECT

**These folders are SAFE on Windows:**

✅ `C:\Users\YourName\Documents\...`
✅ `C:\Users\YourName\Downloads\...`
✅ `C:\Users\YourName\Desktop\...`
✅ `C:\Users\YourName\Projects\...`
✅ Any folder inside your user directory

**No admin rights needed!**

---

## 🔧 STEP-BY-STEP FIX

### Step 1: Check Current Location

```cmd
cd
```

**Is it in a protected folder?** → Move it (Step 2)
**Is it in your user folder?** → Go to Step 3

---

### Step 2: Move Project to Safe Location

**Option A: Using File Explorer (Easier)**
1. Open File Explorer
2. Navigate to current project location
3. Right-click `MAP-LINK-LONG-LANG` folder
4. Click "Cut"
5. Navigate to `C:\Users\YourName\Documents`
6. Right-click empty space → "Paste"
7. Open Command Prompt in new location
8. Run `python run.py`

**Option B: Using Command Prompt**
```cmd
REM Move project
move "C:\current\location\MAP-LINK-LONG-LANG" "C:\Users\YourName\Documents\"

REM Navigate to new location
cd C:\Users\YourName\Documents\MAP-LINK-LONG-LANG

REM Run app
python run.py
```

---

### Step 3: If Still Getting "Access Denied"

**Possible cause**: Antivirus blocking Python

**Solution**:
1. Open Windows Security
2. Click "Virus & threat protection"
3. Click "Manage settings"
4. Temporarily turn OFF "Real-time protection"
5. Run `python run.py`
6. Turn "Real-time protection" back ON

---

### Step 4: If venv Creation Fails

**You'll see this message:**
```
⚠️  Warning: Could not create virtual environment.
💡 This can happen on Windows with restricted permissions.
📌 Options:
   1. Install packages to system Python (easier)
   2. Exit and run as Administrator

Install to system Python? (y/n):
```

**Type `y` and press Enter**

The app will:
- Skip venv creation
- Install packages to your user directory with `--user` flag
- Work without admin rights! ✅

---

## 🧪 TEST IF YOU HAVE WRITE ACCESS

**Quick test to see if folder is writable:**

```cmd
cd C:\path\to\MAP-LINK-LONG-LANG
echo test > test.txt
```

**Result A - Success:**
```
(No error)
```
✅ Folder is writable! → `python run.py` should work

**Result B - Error:**
```
Access is denied.
```
❌ Folder is NOT writable! → Move to user folder (Step 2)

**Clean up:**
```cmd
del test.txt
```

---

## 📊 COMMON ERROR MESSAGES

### Error 1: "Permission denied when accessing project directory"

**Cause**: Project folder itself is protected

**Fix**: Move project to `C:\Users\YourName\Documents\`

---

### Error 2: "Error creating virtual environment"

**Cause**: Can't create `venv/` folder

**Fix**:
- Option 1: Move project to user folder
- Option 2: When prompted, choose "Install to system Python"

---

### Error 3: "Access is denied" (during package installation)

**Cause**: Package installation to venv fails

**Fix**: App will automatically offer to install to system Python with `--user` flag (no admin needed)

---

### Error 4: "uploads/ - Permission denied"

**Cause**: Can't create upload directories

**Fix**: This is OK! App will create them at runtime when you upload a file.

---

## 🎯 RECOMMENDED SETUP (NO ADMIN NEEDED)

**1. Project Location**
```
C:\Users\YourName\Documents\MAP-LINK-LONG-LANG\
```

**2. Run Command**
```cmd
cd C:\Users\YourName\Documents\MAP-LINK-LONG-LANG
python run.py
```

**3. If venv fails**
```
→ Choose "y" to install to system Python
→ Packages install to: C:\Users\YourName\AppData\Roaming\Python\...
```

**4. Result**
```
✅ No admin rights needed
✅ All packages installed
✅ App runs perfectly
```

---

## 🔐 WHY WINDOWS BLOCKS CERTAIN FOLDERS

**Windows protects system folders to prevent:**
- Malware installation
- Accidental system file deletion
- Unauthorized system changes

**Your user folder is safe because:**
- ✅ It's designed for your files
- ✅ You have full control
- ✅ No admin rights needed

---

## 💡 BEST PRACTICES FOR WINDOWS

### DO:
✅ Store projects in `C:\Users\YourName\...`
✅ Use `--user` flag when installing packages (done automatically)
✅ Let app create directories at runtime
✅ Install Python with "Add to PATH" option

### DON'T:
❌ Store projects in `C:\Program Files`
❌ Run as Administrator (unless necessary)
❌ Use network drives for development
❌ Ignore "Access Denied" errors (fix the cause!)

---

## 🚀 FINAL CHECKLIST

Before running `python run.py`:

- [ ] Project is in `C:\Users\YourName\Documents\` (or similar)
- [ ] Python 3.11+ is installed
- [ ] Command Prompt opened in project folder
- [ ] Antivirus temporarily disabled (if needed)
- [ ] Ready to choose "y" if venv creation fails

**Then run:**
```cmd
python run.py
```

**Expected result:**
```
✅ Python version check passes
✅ Virtual environment created (or system Python fallback)
✅ Packages installed with --user flag
✅ App starts successfully
```

---

## 🎉 SUMMARY

**Problem**: "Access Denied" when running `python run.py` on Windows

**Root Cause**: Project in protected folder or permission issues

**Solution**: Move project to `C:\Users\YourName\Documents\`

**Fallback**: If venv fails, install to system Python with `--user` flag

**Result**: App runs perfectly without admin rights! ✅

---

**Status**: ✅ **FULLY FIXED**

**No administrator rights needed!** 🎯

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
