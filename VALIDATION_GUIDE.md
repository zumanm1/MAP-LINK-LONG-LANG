# Validation & Error Handling Guide

## 🎯 Overview

Both the Streamlit and Flask versions now include comprehensive validation for missing map links. Rows with missing or empty map links are **skipped** (not processed) and tracked separately.

---

## 📊 Processing Categories

Each row in your Excel file falls into one of three categories:

### 1. ✅ **Successful**
- Has a valid map link
- Coordinates extracted successfully
- Longitude and Latitude columns populated

### 2. ❌ **Failed**
- Has a map link provided
- But coordinates could not be extracted
- Reasons:
  - Invalid URL format
  - Unsupported map provider
  - Malformed coordinates

### 3. ⚠️ **Skipped**
- No map link provided (empty or null)
- Row is **not processed**
- Original data preserved
- Longitude and Latitude remain empty

---

## 🔍 Validation Logic

### **Backend Validation (Python)**

```python
# Both Streamlit and Flask use this logic:

for idx, row in df.iterrows():
    map_link = row[map_column]

    # Skip rows with missing map links (don't process)
    if pd.isna(map_link) or str(map_link).strip() == '':
        skipped += 1
        continue  # Don't attempt to extract coordinates

    # Process rows with map links
    lng, lat = extract_coordinates_from_url(str(map_link))
    if lng is not None and lat is not None:
        successful += 1  # Coordinates extracted
    else:
        failed += 1  # Extraction failed
```

**Key Points:**
- `pd.isna()` checks for `NaN`, `None`, `NaT` values
- `.strip() == ''` checks for whitespace-only strings
- Skipped rows are logged but not counted as failures

---

## 📝 Processing Log (Flask Only)

The Flask version provides a detailed processing log showing exactly what happened to each row.

### **Log Structure**

```json
{
  "row": 5,
  "name": "Central Park",
  "status": "skipped",
  "reason": "No map link provided"
}
```

### **Log Categories**

#### **Skipped Entries**
```json
{
  "row": 5,
  "name": "Central Park",
  "status": "skipped",
  "reason": "No map link provided"
}
```

#### **Failed Entries**
```json
{
  "row": 12,
  "name": "Times Square",
  "status": "failed",
  "reason": "Could not extract coordinates from URL",
  "map_link": "https://example.com/invalid-map-link"
}
```

#### **Successful Entries**
```json
{
  "row": 1,
  "name": "Sandton City",
  "status": "success",
  "lng": 28.052706,
  "lat": -26.108204,
  "map_link": "https://maps.app.goo.gl/baixEU9UxYHX8Yox7"
}
```

---

## 🎨 UI Display

### **Streamlit Version**

```
✅ Processing complete! Successfully processed 142/150 rows

⚠️ Failed to extract coordinates for 3 rows

ℹ️ Skipped 5 rows with missing map links

┌─────────────┬────────────┬────────┬──────────┐
│ Total Rows  │ Successful │ Failed │ Skipped  │
├─────────────┼────────────┼────────┼──────────┤
│     150     │    142     │   3    │    5     │
└─────────────┴────────────┴────────┴──────────┘
```

### **Flask Version**

```
✅ Processing complete! Successfully processed 142/150 rows

⚠️ Failed to extract coordinates for 3 rows

ℹ️ Skipped 5 rows with missing map links

┌─────────────┬────────────┬────────┬──────────┐
│ Total Rows  │ Successful │ Failed │ Skipped  │
├─────────────┼────────────┼────────┼──────────┤
│     150     │    142     │   3    │    5     │
└─────────────┴────────────┴────────┴──────────┘

📋 Processing Details

⚠️ Skipped Rows (5)
┌─────────────────────────────────────────────┐
│ Row 5: Central Park                         │
│ Reason: No map link provided                │
└─────────────────────────────────────────────┘
│ Row 12: Brooklyn Bridge                     │
│ Reason: No map link provided                │
└─────────────────────────────────────────────┘
... (all skipped rows shown)

❌ Failed Rows (3)
┌─────────────────────────────────────────────┐
│ Row 23: Empire State Building               │
│ Reason: Could not extract coordinates       │
│ URL: https://example.com/invalid-link       │
└─────────────────────────────────────────────┘
... (all failed rows shown)

✅ Sample Successful Rows (showing 10 of 142)
┌─────────────────────────────────────────────┐
│ Row 1: Sandton City                         │
│ URL: https://maps.app.goo.gl/baixEU...      │
│ Coordinates: 28.052706, -26.108204          │
└─────────────────────────────────────────────┘
... (first 10 successful rows shown)
```

---

## 🧪 Testing Validation

### **Test Data Setup**

Create an Excel file with these scenarios:

```excel
| Row | Name              | Region     | Maps                                    |
|-----|-------------------|------------|-----------------------------------------|
| 1   | Valid Link        | NYC        | https://maps.app.goo.gl/valid           |
| 2   | Missing Link      | LA         | [empty]                                 |
| 3   | Whitespace Only   | Chicago    | "   "                                   |
| 4   | Invalid URL       | Houston    | https://example.com/notamap             |
| 5   | Direct Coords     | Phoenix    | 33.4484,-112.0740                       |
| 6   | Null Value        | Philly     | [null/NaN]                              |
```

### **Expected Results**

```
Total Rows:  6
Successful:  2  (rows 1 and 5)
Failed:      1  (row 4)
Skipped:     3  (rows 2, 3, and 6)
```

---

## 🔧 Implementation Details

### **Flask Backend (`flask_app.py`)**

```python
# Lines 138-180

successful = 0
failed = 0
skipped = 0
processing_log = []

for idx, row in df.iterrows():
    map_link = row[map_column]

    # Skip rows with missing map links
    if pd.isna(map_link) or str(map_link).strip() == '':
        skipped += 1
        processing_log.append({
            'row': idx + 1,
            'name': row['Name'],
            'status': 'skipped',
            'reason': 'No map link provided'
        })
        continue

    # Process rows with map links
    lng, lat = extract_coordinates_from_url(str(map_link))
    if lng is not None and lat is not None:
        df.at[idx, long_column] = lng
        df.at[idx, lat_column] = lat
        successful += 1
        processing_log.append({
            'row': idx + 1,
            'name': row['Name'],
            'status': 'success',
            'lng': lng,
            'lat': lat,
            'map_link': str(map_link)[:50] + '...'
        })
    else:
        failed += 1
        processing_log.append({
            'row': idx + 1,
            'name': row['Name'],
            'status': 'failed',
            'reason': 'Could not extract coordinates from URL',
            'map_link': str(map_link)[:50] + '...'
        })
```

### **Flask Frontend (`static/js/app.js`)**

```javascript
// Lines 266-362

function displayProcessingLog(processingLog) {
    // Group logs by status
    const skippedLogs = processingLog.filter(log => log.status === 'skipped');
    const failedLogs = processingLog.filter(log => log.status === 'failed');
    const successLogs = processingLog.filter(log => log.status === 'success');

    // Display skipped entries (all)
    if (skippedLogs.length > 0) {
        // Show all skipped rows
    }

    // Display failed entries (all)
    if (failedLogs.length > 0) {
        // Show all failed rows
    }

    // Display successful entries (first 10 only)
    if (successLogs.length > 0) {
        // Show only first 10 to avoid clutter
    }
}

function createLogEntry(log, status) {
    const entry = document.createElement('div');
    entry.className = `log-entry ${status}`;

    // Add header (row number and name)
    // Add reason (if failed or skipped)
    // Add map link (if provided)
    // Add coordinates (if successful)

    return entry;
}
```

### **Streamlit Version (`app.py`)**

```python
# Lines 65-105

successful = 0
failed = 0
skipped = 0

for idx, row in df.iterrows():
    map_link = row[map_column]

    # Skip rows with missing map links
    if pd.isna(map_link) or str(map_link).strip() == '':
        skipped += 1
        continue

    # Process rows with map links
    lng, lat = extract_coordinates_from_url(str(map_link))
    if lng is not None and lat is not None:
        df.at[idx, long_column] = lng
        df.at[idx, lat_column] = lat
        successful += 1
    else:
        failed += 1

# Display messages
st.success(f"✅ Processing complete! Successfully processed {successful}/{len(df)} rows")

if failed > 0:
    st.warning(f"⚠️ Failed to extract coordinates for {failed} rows")

if skipped > 0:
    st.info(f"ℹ️ Skipped {skipped} rows with missing map links")

# Display statistics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Rows", len(df))
with col2:
    st.metric("Successful", successful)
with col3:
    st.metric("Failed", failed)
with col4:
    st.metric("Skipped", skipped)
```

---

## 📈 API Response Structure (Flask)

### **POST /process/<session_id> Response**

```json
{
  "success": true,
  "total_rows": 150,
  "successful": 142,
  "failed": 3,
  "skipped": 5,
  "processing_log": [
    {
      "row": 1,
      "name": "Sandton City",
      "status": "success",
      "lng": 28.052706,
      "lat": -26.108204,
      "map_link": "https://maps.app.goo.gl/baixEU9UxYHX8Yox7"
    },
    {
      "row": 5,
      "name": "Central Park",
      "status": "skipped",
      "reason": "No map link provided"
    },
    {
      "row": 23,
      "name": "Empire State",
      "status": "failed",
      "reason": "Could not extract coordinates from URL",
      "map_link": "https://example.com/invalid"
    }
  ],
  "processed_data": [ /* full dataset */ ],
  "processed_columns": ["Name", "Region", "Maps", "LONG", "LATTs"]
}
```

---

## 🎯 Best Practices

### **For Users**

1. **Review skipped rows**: Check the processing log to identify rows with missing links
2. **Add missing links**: Update your Excel file with map links for skipped rows
3. **Re-upload and process**: Process again to get coordinates for previously skipped rows
4. **Verify failed rows**: Manually check URLs that failed extraction

### **For Developers**

1. **Always validate input**: Check for null/empty values before processing
2. **Log everything**: Maintain detailed logs for debugging
3. **Categorize results**: Separate skipped, failed, and successful operations
4. **Provide feedback**: Show users exactly what happened to each row
5. **Don't count skips as failures**: They're different issues

---

## 🔍 Common Scenarios

### **Scenario 1: Partial Data Entry**

```
User uploads file with 100 rows
- 80 rows have map links
- 20 rows are still being researched (no links yet)

Result:
✅ Successful: 78
❌ Failed: 2
⚠️ Skipped: 20

Action: User can download processed file, add missing links later, and re-process
```

### **Scenario 2: Data Migration**

```
User migrating from old system
- Old system had different URL format
- Some URLs are invalid/broken

Result:
✅ Successful: 120
❌ Failed: 15 (old URL format not supported)
⚠️ Skipped: 5 (never had links)

Action: User reviews failed rows in processing log, manually fixes URLs
```

### **Scenario 3: Incremental Processing**

```
User adds new locations weekly
- Processes file with existing + new locations
- New locations don't have coordinates yet
- Old locations already processed

Result:
✅ Successful: 150 (all locations with links)
❌ Failed: 0
⚠️ Skipped: 10 (new locations without research)

Action: Next week, after research, re-upload to fill in skipped rows
```

---

## 🚨 Error Messages Explained

| Message | Meaning | Action |
|---------|---------|--------|
| "No map link provided" | Cell is empty/null | Add map URL to Excel file |
| "Could not extract coordinates from URL" | URL format not recognized | Check URL format or use supported provider |
| "Missing required map column" | Excel missing 'Maps' or 'Map link' column | Rename column or add it |
| "Failed to resolve shortened URL" | Network issue or invalid shortened URL | Check internet connection, verify URL |

---

## 📊 Statistics Interpretation

```
Total Rows:   150    (Total records in Excel file)
Successful:   142    (Coordinates extracted and saved)
Failed:       3      (Processing attempted but failed)
Skipped:      5      (Not processed due to missing links)

Processing Rate: 142/145 = 97.9%  (excluding skipped)
Coverage Rate:   142/150 = 94.7%  (including skipped)
```

**Key Metric**: Focus on **Processing Rate** (excludes skipped rows) to measure extraction accuracy.

---

## 🎓 Summary

### **What Changed**

✅ Added "Skipped" category for missing map links
✅ Separated skipped from failed (different issues)
✅ Added detailed processing log (Flask)
✅ Enhanced statistics display (4 metrics instead of 3)
✅ Better user feedback with specific messages

### **Why It Matters**

1. **Clearer Reporting**: Users know exactly what happened to each row
2. **Better Data Quality**: Skipped rows can be easily identified and fixed
3. **No False Failures**: Missing data isn't counted as processing failure
4. **Audit Trail**: Processing log shows detailed history (Flask)
5. **Incremental Workflow**: Users can process partial data and come back

---

**Both versions now handle validation consistently and provide clear feedback! 🎉**
