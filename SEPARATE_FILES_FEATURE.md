# SEPARATE FILES FEATURE - Failed & Skipped Rows

**Date**: 2025-11-04
**Status**: ✅ IMPLEMENTED AND TESTED
**Applies to**: `map_converter.py` and `map_converter_enhanced.py`

---

## 🎯 FEATURE REQUEST

User requested:
> "the failed shoud ahve a new excel file and also the skipped should also ahve a excel file."

**Purpose**: Automatically generate separate Excel files for failed and skipped rows, making it easier to review and retry problematic entries.

---

## ✅ SOLUTION

Both `map_converter.py` and `map_converter_enhanced.py` now automatically generate:

1. **Main output file** - Contains ALL rows (successful, failed, and skipped)
2. **Failed rows file** - Contains ONLY rows that failed extraction (suffix: `_failed.xlsx`)
3. **Skipped rows file** - Contains ONLY rows that were skipped (suffix: `_skipped.xlsx`)

### File Naming Convention

If you specify output file: `output.xlsx`

Generated files:
- `output.xlsx` - All rows with status in Comments column
- `output_failed.xlsx` - Only failed rows (if any)
- `output_skipped.xlsx` - Only skipped rows (if any)

**Smart Generation**: Files are only created when there are rows to save. If there are no failed rows, no `_failed.xlsx` file is created.

---

## 📋 ROW STATUS DEFINITIONS

### ✅ Successful
- Coordinates successfully extracted
- `LONG` and `LATTs` columns populated
- `Comments`: "Success"

### ❌ Failed
- URL provided but coordinates could not be extracted
- All extraction methods exhausted (4 methods in enhanced version, 3 attempts in standard version)
- `LONG` and `LATTs` remain blank (NaN)
- `Comments`: "Failed: Could not extract coordinates (tried 4 methods)"

### ⏭️ Skipped
- No map link provided (blank, empty string, or NaN)
- Not attempted
- `LONG` and `LATTs` remain blank (NaN)
- `Comments`: "Skipped: No map link provided"

---

## 🧪 TEST RESULTS

### Test Setup
Created test file with 6 rows:
- 2 rows with valid URLs (should succeed)
- 2 rows with invalid URLs (should fail)
- 2 rows with blank/empty map links (should be skipped)

### Results

**Command**:
```bash
python map_converter_enhanced.py test_failed_skipped_input.xlsx test_failed_skipped_output.xlsx
```

**Output**:
```
============================================================
✅ Processing complete!
   Total: 6 rows
   ✅ Successful: 2
   ❌ Failed: 2
   ⏭️  Skipped: 2
============================================================
✅ Saved 2 failed rows to: test_failed_skipped_output_failed.xlsx
✅ Saved 2 skipped rows to: test_failed_skipped_output_skipped.xlsx
```

**Generated Files**:
1. `test_failed_skipped_output.xlsx` - 6 rows (all)
2. `test_failed_skipped_output_failed.xlsx` - 2 rows (failed only)
3. `test_failed_skipped_output_skipped.xlsx` - 2 rows (skipped only)

---

## 📊 FILE CONTENTS

### Main Output File (`output.xlsx`)
Contains ALL 6 rows with status:

| Name | Region | Maps link | LONG | LATTs | Comments |
|------|--------|-----------|------|-------|----------|
| Valid URL - Success | Test | https://www.google.com/maps/... | 28.052706 | -26.108204 | Success |
| Invalid URL - Failed | Test | https://invalid-map-url... | NaN | NaN | Failed: Could not extract... |
| Empty Map Link - Skipped | Test | NaN | NaN | NaN | Skipped: No map link provided |
| Valid URL - Success 2 | Test | https://maps.google.com/... | 18.424100 | -33.924900 | Success |
| Bad Format - Failed | Test | not-a-url-at-all | NaN | NaN | Failed: Could not extract... |
| Blank - Skipped | Test | (empty) | NaN | NaN | Skipped: No map link provided |

### Failed File (`output_failed.xlsx`)
Contains ONLY 2 failed rows:

| Name | Region | Maps link | LONG | LATTs | Comments |
|------|--------|-----------|------|-------|----------|
| Invalid URL - Failed | Test | https://invalid-map-url... | NaN | NaN | Failed: Could not extract... |
| Bad Format - Failed | Test | not-a-url-at-all | NaN | NaN | Failed: Could not extract... |

### Skipped File (`output_skipped.xlsx`)
Contains ONLY 2 skipped rows:

| Name | Region | Maps link | LONG | LATTs | Comments |
|------|--------|-----------|------|-------|----------|
| Empty Map Link - Skipped | Test | NaN | NaN | NaN | Skipped: No map link provided |
| Blank - Skipped | Test | (empty) | NaN | NaN | Skipped: No map link provided |

---

## 🚀 USAGE

### Standard Version
```bash
python map_converter.py input.xlsx output.xlsx
```

**Generates**:
- `output.xlsx` (all rows)
- `output_failed.xlsx` (if any failed)
- `output_skipped.xlsx` (if any skipped)

### Enhanced Version (4 Fallback Methods)
```bash
python map_converter_enhanced.py input.xlsx output.xlsx
```

**Generates**:
- `output.xlsx` (all rows)
- `output_failed.xlsx` (if any failed)
- `output_skipped.xlsx` (if any skipped)

### With Custom Paths
```bash
python map_converter_enhanced.py /path/to/input.xlsx /path/to/output/results.xlsx
```

**Generates**:
- `/path/to/output/results.xlsx` (all rows)
- `/path/to/output/results_failed.xlsx` (if any failed)
- `/path/to/output/results_skipped.xlsx` (if any skipped)

---

## 💡 USE CASES

### 1. Review Failed Extractions
Open `output_failed.xlsx` to see which URLs couldn't be processed:
- Check for typos in URLs
- Verify URLs are actually Google Maps links
- Identify problematic URL formats
- Manually extract coordinates if needed

### 2. Complete Skipped Rows
Open `output_skipped.xlsx` to see which rows had no map link:
- Add missing map links
- Re-process the file after adding links
- Merge back into main dataset

### 3. Retry Failed Rows
1. Open `output_failed.xlsx`
2. Fix/update URLs
3. Save as new input file
4. Re-run converter on just the failed rows
5. Merge successful results back into main file

### 4. Quality Assurance
- Quickly check how many rows succeeded vs failed
- Identify patterns in failed URLs
- Validate that skipped rows are expected

---

## 🔧 IMPLEMENTATION DETAILS

### Code Location

**map_converter.py**: Lines 310-333
**map_converter_enhanced.py**: Lines 382-405

### How It Works

```python
# After saving main output file
from pathlib import Path
output_path = Path(output_file)
output_stem = output_path.stem  # Filename without extension
output_dir = output_path.parent  # Directory
output_ext = output_path.suffix  # Extension (e.g., .xlsx)

# Filter failed rows
failed_df = df[df['Comments'].str.startswith('Failed', na=False)]
if len(failed_df) > 0:
    failed_file = output_dir / f"{output_stem}_failed{output_ext}"
    failed_df.to_excel(failed_file, index=False)
    logger.info(f"✅ Saved {len(failed_df)} failed rows to: {failed_file}")

# Filter skipped rows
skipped_df = df[df['Comments'].str.startswith('Skipped', na=False)]
if len(skipped_df) > 0:
    skipped_file = output_dir / f"{output_stem}_skipped{output_ext}"
    skipped_df.to_excel(skipped_file, index=False)
    logger.info(f"✅ Saved {len(skipped_df)} skipped rows to: {skipped_file}")
```

### Key Points
- Uses pandas DataFrame filtering: `df[df['Comments'].str.startswith('Failed', na=False)]`
- `na=False` ensures NaN values don't cause errors
- Only creates files if rows exist: `if len(failed_df) > 0:`
- Uses pathlib for cross-platform path handling
- Preserves all columns from original file

---

## ✅ BENEFITS

1. **Easier Review**: Don't need to scroll through entire file to find failed/skipped rows
2. **Targeted Fixes**: Open only the failed file, fix URLs, and re-process
3. **Quality Tracking**: Quickly see success rate and identify problem areas
4. **Workflow Integration**: Use separate files in automated pipelines
5. **Documentation**: Keep failed files as record of problematic entries

---

## 📈 EXAMPLE WORKFLOW

### Step 1: Initial Processing
```bash
python map_converter_enhanced.py data.xlsx results.xlsx
```

**Output**:
```
✅ Processing complete!
   Total: 100 rows
   ✅ Successful: 92
   ❌ Failed: 5
   ⏭️  Skipped: 3
✅ Saved 5 failed rows to: results_failed.xlsx
✅ Saved 3 skipped rows to: results_skipped.xlsx
```

### Step 2: Fix Failed Rows
1. Open `results_failed.xlsx`
2. Review the 5 failed URLs
3. Fix URLs or add missing coordinates manually
4. Save as `data_retry.xlsx`

### Step 3: Re-process Fixed Rows
```bash
python map_converter_enhanced.py data_retry.xlsx results_retry.xlsx
```

### Step 4: Merge Results
- Copy successful rows from `results_retry.xlsx` back into `results.xlsx`
- Final file now has 97/100 rows with coordinates

---

## 🎯 SUCCESS CRITERIA

✅ Separate files automatically generated
✅ Failed rows correctly filtered
✅ Skipped rows correctly filtered
✅ Files only created when rows exist
✅ Works with both standard and enhanced converters
✅ Cross-platform path handling
✅ All columns preserved in separate files
✅ Clear logging of file generation

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
