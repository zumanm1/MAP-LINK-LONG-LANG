# 📋 Comprehensive Test File Documentation

**File**: `test_input_comprehensive.xlsx`
**Created**: 2025-11-04
**Total Rows**: 35
**Purpose**: Validate all map link formats, edge cases, and error handling

---

## 📊 Test Coverage Summary

| Category | Count | Description |
|----------|-------|-------------|
| **Valid URLs** | 21 rows | Various supported formats |
| **Edge Cases** | 10 rows | Blank regions, special characters, precision tests |
| **Invalid URLs** | 9 rows | Error handling validation |
| **International** | 5 rows | Real-world locations worldwide |

---

## 🗺️ Supported URL Formats (Rows 1-15)

### 1. Standard Place Format with Decimal Coordinates
**Row 1**: Sandton City, Johannesburg
**URL**: `https://www.google.com/maps/place/Sandton+City/@-26.108204,28.0527061,17z`
**Pattern**: `/place/NAME/@LAT,LNG,ZOOM`
**Expected**: ✅ Should extract: -26.108204, 28.0527061

### 2. Shortened Google Maps Link (goo.gl)
**Row 2**: Nelson Mandela Square, Sandton
**URL**: `https://maps.app.goo.gl/baixEU9UxYHX8Yox7`
**Pattern**: Shortened URL (requires Selenium to resolve)
**Expected**: ✅ Should extract coordinates after redirect resolution

### 3. @ Format with Integer Coordinates
**Row 3**: Cape Town Stadium
**URL**: `https://www.google.com/maps/@-34,18,12z`
**Pattern**: `/@LAT,LNG,ZOOM` (no decimals)
**Expected**: ✅ Should extract: -34, 18
**Tests**: BUG FIX #9 - Integer coordinate support

### 4. Query Format (q=)
**Row 4**: Table Mountain
**URL**: `https://www.google.com/maps?q=-33.9628,18.4098`
**Pattern**: `?q=LAT,LNG`
**Expected**: ✅ Should extract: -33.9628, 18.4098

### 5. Place Format with Integer Coordinates
**Row 5**: Durban Beach
**URL**: `https://www.google.com/maps/place/Durban/@-30,31,12z`
**Pattern**: `/place/NAME/@LAT,LNG` (integers)
**Expected**: ✅ Should extract: -30, 31

### 6. Mixed Integer/Decimal Coordinates
**Row 6**: Pretoria Union Buildings
**URL**: `https://www.google.com/maps/@-25,28.2293,15z`
**Pattern**: `/@LAT,LNG` (lat=integer, lng=decimal)
**Expected**: ✅ Should extract: -25, 28.2293
**Tests**: Regex flexibility with `(?:\.\d+)?` optional decimal group

### 7. High Precision Decimal (7 decimal places)
**Row 7**: Kruger National Park Gate
**URL**: `https://www.google.com/maps/@-24.9881071,31.5548862,17z`
**Pattern**: `/@LAT,LNG` (7 decimals)
**Expected**: ✅ Should extract: -24.9881071, 31.5548862

### 8. Direct Coordinate Pair (No URL)
**Row 8**: Blyde River Canyon
**URL**: `-24.5472, 30.8104`
**Pattern**: Plain text `LAT, LNG`
**Expected**: ✅ Should extract: -24.5472, 30.8104

### 9. Alternative Domain (maps.google.com)
**Row 9**: Gold Reef City
**URL**: `https://maps.google.com/@-26.2355,27.9854,15z`
**Pattern**: `maps.google.com/@LAT,LNG`
**Expected**: ✅ Should extract: -26.2355, 27.9854

### 10. Search Format
**Row 10**: Robben Island
**URL**: `https://www.google.com/maps/search/-33.8080,18.3708`
**Pattern**: `/search/LAT,LNG`
**Expected**: ✅ Should extract: -33.8080, 18.3708

### 11. URL with Extra Parameters
**Row 11**: V&A Waterfront
**URL**: `https://www.google.com/maps/@-33.9025,18.4186,17z/data=!3m1!4b1`
**Pattern**: `/@LAT,LNG,ZOOM/data=...`
**Expected**: ✅ Should extract: -33.9025, 18.4186
**Tests**: Regex ignores trailing parameters

### 12. Zero Coordinates (Null Island)
**Row 12**: Null Island Test
**URL**: `https://www.google.com/maps/@0,0,12z`
**Pattern**: `/@0,0`
**Expected**: ✅ Should extract: 0, 0
**Tests**: Edge case - both coordinates are zero

### 13. Negative Both Coordinates (Southern/Western Hemisphere)
**Row 13**: Argentina Example
**URL**: `https://www.google.com/maps/@-34.6037,-58.3816,12z`
**Pattern**: `/@-LAT,-LNG`
**Expected**: ✅ Should extract: -34.6037, -58.3816

### 14. URL-Encoded Coordinates
**Row 14**: Johannesburg Zoo
**URL**: `https://www.google.com/maps/place/Zoo/@-26.1677%2C28.0395,15z`
**Pattern**: `/@LAT%2CLNG` (%2C = comma)
**Expected**: ✅ Should extract: -26.1677, 28.0395
**Tests**: URL decoding with `urllib.parse.unquote()`

### 15. HTTP (Not HTTPS)
**Row 15**: Apartheid Museum
**URL**: `http://www.google.com/maps/@-26.2375,27.9866,17z`
**Pattern**: `http://` instead of `https://`
**Expected**: ✅ Should extract: -26.2375, 27.9866

---

## 🔍 Edge Cases (Rows 16-21)

### 16. Blank/Empty Region
**Row 16**: Location with Blank Region
**Region**: `""` (empty string)
**Expected**: ⚠️ Should process but flag blank region
**Tests**: Handling of missing region data

### 17. Missing Region (None/NaN)
**Row 17**: Location with No Region
**Region**: `None` (NaN in Excel)
**Expected**: ⚠️ Should process but flag missing region
**Tests**: NaN handling in pandas DataFrame

### 18. Very Long Location Name
**Row 18**: "Constitutional Court of South Africa - Very Long Name..."
**Expected**: ✅ Should handle long strings without truncation
**Tests**: String length limits

### 19. Special Characters in Name
**Row 19**: "Café & Restaurant's Place (Test)"
**Expected**: ✅ Should handle special chars: `&`, `'`, `(`, `)`
**Tests**: Unicode and special character encoding

### 20. Low Precision (1 Decimal Place)
**Row 20**: Low Precision Location
**URL**: `https://www.google.com/maps/@-26.1,28.0,12z`
**Expected**: ✅ Should extract: -26.1, 28.0
**Tests**: Minimum precision handling

### 21. Very High Precision (7 Decimal Places)
**Row 21**: High Precision Location
**URL**: `https://www.google.com/maps/@-26.1082041,28.0527061,20z`
**Expected**: ✅ Should extract: -26.1082041, 28.0527061
**Tests**: Maximum precision handling

---

## ❌ Invalid/Faulty URLs (Rows 22-30)

### 22. No Coordinates in URL
**Row 22**: INVALID: No Coordinates
**URL**: `https://www.google.com/maps`
**Expected**: ❌ Should fail gracefully, return None/None
**Tests**: Error handling - missing coordinates

### 23. Not a Maps URL
**Row 23**: INVALID: Not Maps URL
**URL**: `https://www.google.com/`
**Expected**: ❌ Should fail gracefully, return None/None
**Tests**: Error handling - wrong domain

### 24. Place Name Only, No Coordinates
**Row 24**: INVALID: Place Name Only
**URL**: `https://www.google.com/maps/place/Johannesburg`
**Expected**: ❌ Should fail gracefully
**Tests**: Pattern matching failure

### 25. Malformed URL
**Row 25**: INVALID: Malformed URL
**URL**: `not-a-valid-url`
**Expected**: ❌ Should fail gracefully
**Tests**: URL validation

### 26. Empty/Blank Map Link
**Row 26**: INVALID: Empty Link
**URL**: `""` (empty string)
**Expected**: ❌ Should skip or return None/None
**Tests**: Empty string handling

### 27. None/Missing Map Link
**Row 27**: INVALID: Missing Link
**URL**: `None` (NaN in Excel)
**Expected**: ❌ Should skip or return None/None
**Tests**: NaN handling for map links

### 28. Out of Range Latitude (> 90)
**Row 28**: INVALID: Lat > 90
**URL**: `https://www.google.com/maps/@95,28,12z`
**Expected**: ❌ Should reject: latitude must be -90 to 90
**Tests**: Coordinate validation - latitude range

### 29. Out of Range Longitude (> 180)
**Row 29**: INVALID: Lng > 180
**URL**: `https://www.google.com/maps/@-26,185,12z`
**Expected**: ❌ Should reject: longitude must be -180 to 180
**Tests**: Coordinate validation - longitude range

### 30. Reversed Coordinates (Common Mistake)
**Row 30**: Edge Case: Might be Reversed
**URL**: `https://www.google.com/maps/@28.0527,-26.1082,17z`
**Expected**: ⚠️ May extract but values seem reversed
**Tests**: Detection of potentially swapped lat/lng

---

## 🌍 Real-World International Examples (Rows 31-35)

### 31. Sydney, Australia
**Name**: Sydney Opera House
**Region**: Sydney, Australia
**URL**: `https://www.google.com/maps/@-33.8568,151.2153,17z`
**Expected**: ✅ -33.8568, 151.2153

### 32. Tokyo, Japan
**Name**: Tokyo Tower
**Region**: Tokyo, Japan
**URL**: `https://www.google.com/maps/@35.6586,139.7454,17z`
**Expected**: ✅ 35.6586, 139.7454

### 33. London, UK
**Name**: Big Ben
**Region**: London, UK
**URL**: `https://www.google.com/maps/@51.5007,-0.1246,17z`
**Expected**: ✅ 51.5007, -0.1246

### 34. New York, USA
**Name**: Statue of Liberty
**Region**: New York, USA
**URL**: `https://www.google.com/maps/@40.6892,-74.0445,17z`
**Expected**: ✅ 40.6892, -74.0445

### 35. Dubai, UAE
**Name**: Burj Khalifa
**Region**: Dubai, UAE
**URL**: `https://www.google.com/maps/@25.1972,55.2744,17z`
**Expected**: ✅ 25.1972, 55.2744

---

## 🧪 What This Test File Validates

### ✅ Bug Fixes Validated
1. **BUG #9**: Integer coordinate support (`@40,74` format)
2. **BUG #1 & #2**: Timeout handling (shortened URLs may timeout)
3. **BUG #3**: Case-insensitive column handling ("Maps link" vs "Map link")
4. **BUG #7**: Frontend DOM ready (file upload should work)

### ✅ URL Pattern Coverage
- ✅ Standard place format
- ✅ Shortened goo.gl links
- ✅ Integer coordinates
- ✅ Decimal coordinates
- ✅ Mixed integer/decimal
- ✅ Query format (q=)
- ✅ Search format
- ✅ Direct coordinate pairs
- ✅ URL-encoded coordinates
- ✅ HTTP vs HTTPS

### ✅ Edge Case Coverage
- ✅ Blank/missing regions
- ✅ Special characters
- ✅ Very long names
- ✅ Zero coordinates (Null Island)
- ✅ Negative coordinates
- ✅ High/low precision (1-7 decimals)

### ✅ Error Handling
- ✅ Invalid URLs
- ✅ Missing coordinates
- ✅ Out of range values
- ✅ Empty/None values
- ✅ Malformed URLs

---

## 📊 Expected Results

After processing this file, you should see:

**Successful Extractions**: ~24 rows (valid URLs + international examples)
**Failed Extractions**: ~9 rows (invalid URLs)
**Edge Cases**: ~2 rows (blank regions, may succeed with warning)

### Success Criteria
1. ✅ All valid URLs extract coordinates correctly
2. ✅ Integer coordinates work (BUG #9 validated)
3. ✅ Invalid URLs fail gracefully (no crashes)
4. ✅ Edge cases handled without errors
5. ✅ International locations work
6. ✅ High/low precision preserved

---

## 🚀 How to Use This Test File

### Via Flask Web App (Port 5006)
1. Open http://localhost:5006
2. Click "Choose File"
3. Select `test_input_comprehensive.xlsx`
4. Click "Upload File"
5. Review preview table
6. Click "Process File"
7. Wait for processing (may take 1-2 minutes)
8. Click "Download Results"

### Via CLI
```bash
python map_converter.py test_input_comprehensive.xlsx output_results.xlsx
```

### Via Streamlit
```bash
streamlit run app.py
# Upload test_input_comprehensive.xlsx in the UI
```

---

## 📝 Notes

- **Shortened URLs (Row 2)**: May take longer to process due to redirect resolution
- **Invalid URLs (Rows 22-30)**: Will appear in results with empty LONG/LATTs columns
- **Blank Regions (Rows 16-17)**: Will process but may show warning in logs
- **Timeout**: If any URL takes > 20 seconds, it will timeout gracefully (BUG #1 fix)

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
