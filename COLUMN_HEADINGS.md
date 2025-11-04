# 📋 COLUMN HEADINGS - LONG and LATTs

**Date**: 2025-11-04
**Status**: ✅ **VERIFIED - Default headings are 'LONG' and 'LATTs'**

---

## 🎯 Default Column Headings

When the script creates new coordinate columns, they are named:
- **LONG** (all uppercase)
- **LATTs** (mixed case with double 't')

---

## 📊 Column Detection Behavior

The script uses **case-insensitive detection** to find existing columns:

### 1. New Files (No Long/Lat Columns)

**Input File:**
```
Name | Region | Maps link
-----|--------|----------
```

**Output File:**
```
Name | Region | Maps link | LONG | LATTs
-----|--------|-----------|------|-------
```

✅ Creates **'LONG'** and **'LATTs'** columns

---

### 2. Files with Existing 'LONG' and 'LATTs'

**Input File:**
```
Name | Region | Maps link | LONG | LATTs
-----|--------|-----------|------|-------
     |        |           |      |
```

**Output File:**
```
Name | Region | Maps link | LONG | LATTs
-----|--------|-----------|------|-------
     |        |           | 28.05| -26.10
```

✅ Uses existing **'LONG'** and **'LATTs'** columns (no duplicates created)

---

### 3. Files with Lowercase Columns

**Input File:**
```
Name | Region | Maps link | long | lat
-----|--------|-----------|------|-----
     |        |           |      |
```

**Output File:**
```
Name | Region | Maps link | long | lat
-----|--------|-----------|------|-----
     |        |           | 28.05| -26.10
```

✅ Uses existing **'long'** and **'lat'** columns (preserves lowercase)

---

### 4. Files with Other Variations

The script detects and uses existing columns with these names (case-insensitive):

**For Longitude:**
- `long`
- `longitude`
- `lng`
- `LONG`
- `Long`
- Any mixed case variation

**For Latitude:**
- `latts`
- `latt`
- `lat`
- `latitude`
- `LATTs`
- `Latts`
- `LAT`
- Any mixed case variation

---

## 🧪 Test Results

All tests passed successfully:

### Test 1: New Files Use 'LONG' and 'LATTs'
```
Input columns:  ['Name', 'Region', 'Maps link']
Output columns: ['Name', 'Region', 'Maps link', 'LONG', 'LATTs']
```
✅ **PASSED** - Default headings are 'LONG' and 'LATTs'

### Test 2: Existing 'LONG' and 'LATTs' Preserved
```
Input columns:  ['Name', 'Region', 'Maps link', 'LONG', 'LATTs']
Output columns: ['Name', 'Region', 'Maps link', 'LONG', 'LATTs']
Column count: 5 (no duplicates)
```
✅ **PASSED** - Existing columns are reused

### Test 3: Lowercase Columns Detected
```
Input columns:  ['Name', 'Region', 'Maps link', 'long', 'lat']
Output columns: ['Name', 'Region', 'Maps link', 'long', 'lat']
```
✅ **PASSED** - Lowercase columns detected and used

---

## 🔍 How It Works

### Code Implementation (map_converter.py)

```python
# Clean column names: strip whitespace
df.columns = df.columns.str.strip()

# Create a case-insensitive column mapping
column_mapping = {col.lower(): col for col in df.columns}

# Try to find existing Long column
long_column = None
for option in ['long', 'longitude', 'lng']:
    if option in column_mapping:
        long_column = column_mapping[option]  # Returns actual column name
        break

# If not found, create new column with default name 'LONG'
if not long_column:
    long_column = 'LONG'
    df[long_column] = None

# Try to find existing Lat column
lat_column = None
for option in ['latts', 'latt', 'lat', 'latitude']:
    if option in column_mapping:
        lat_column = column_mapping[option]  # Returns actual column name
        break

# If not found, create new column with default name 'LATTs'
if not lat_column:
    lat_column = 'LATTs'
    df[lat_column] = None
```

### How Case-Insensitive Mapping Works

```python
# Example: File has columns ['Name', 'Region', 'Maps link', 'LONG', 'LATTs']

# Step 1: Create lowercase mapping
column_mapping = {
    'name': 'Name',
    'region': 'Region',
    'maps link': 'Maps link',
    'long': 'LONG',      # 'long' key maps to 'LONG' column
    'latts': 'LATTs'     # 'latts' key maps to 'LATTs' column
}

# Step 2: Search for 'long' in mapping
if 'long' in column_mapping:
    long_column = column_mapping['long']  # Returns 'LONG'

# Result: Uses existing 'LONG' column instead of creating 'Long'
```

---

## 📝 Summary Table

| Scenario | Input Columns | Output Columns | Result |
|----------|---------------|----------------|--------|
| **New file** | Name, Region, Maps link | Name, Region, Maps link, **LONG**, **LATTs** | Creates new columns |
| **Has LONG/LATTs** | Name, Region, Maps link, LONG, LATTs | Name, Region, Maps link, **LONG**, **LATTs** | Uses existing |
| **Has Long/Latts** | Name, Region, Maps link, Long, Latts | Name, Region, Maps link, **Long**, **Latts** | Uses existing |
| **Has long/lat** | Name, Region, Maps link, long, lat | Name, Region, Maps link, **long**, **lat** | Uses existing |
| **Has longitude/latitude** | Name, Region, Maps link, longitude, latitude | Name, Region, Maps link, **longitude**, **latitude** | Uses existing |

---

## ✅ Key Takeaways

1. ✅ **Default headings** are **'LONG'** and **'LATTs'** (not 'Long' and 'Latts')
2. ✅ **Case-insensitive detection** finds existing columns regardless of case
3. ✅ **No duplicate columns** created when existing columns are found
4. ✅ **Preserves original naming** when existing columns are detected
5. ✅ **Works with all variations**: LONG, Long, long, Longitude, longitude, lng, etc.

---

## 🎯 Best Practices

### For New Files:
- Don't include LONG/LATTs columns in input
- Script will create them automatically
- Default names: **'LONG'** and **'LATTs'**

### For Existing Files:
- Keep your existing column names
- Script will detect and use them
- Works with any case variation

### For Consistency:
- Use **'LONG'** and **'LATTs'** in your templates
- Matches the script's default naming
- Easier to maintain across multiple files

---

**Status**: ✅ **VERIFIED - Column headings work correctly**

**Test file**: `test_column_headings.py`

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
