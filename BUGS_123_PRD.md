# PRD: Fix Bugs #1, #2, #3 - Critical Security and Data Integrity Issues

**Date**: 2025-11-04
**Status**: PRD - Ready for Implementation
**Priority**: CRITICAL (Blocks Production)

---

## 1. PROBLEM STATEMENT

Three critical bugs are preventing the application from being production-ready:

### Bug #1: XSS Vulnerability (app.js:371)
**Current State**: User-supplied map URLs are injected into HTML using `innerHTML`, allowing JavaScript execution.
**Impact**: Attackers can inject malicious scripts to steal session tokens, redirect users, or inject malware.

### Bug #2: Path Traversal (flask_app.py:450-474)
**Current State**: Download endpoint trusts session data without validating file path is within allowed directory.
**Impact**: Attackers can modify session data to download any file on the server (passwords, database, source code).

### Bug #3: No Coordinate Validation (map_converter.py:52-95)
**Current State**: Extracted coordinates are not validated against valid ranges (lat: -90 to 90, lng: -180 to 180).
**Impact**: Invalid coordinates (lat=999, lng=500) are written to output file, corrupting data for downstream applications.

---

## 2. GOALS

### Primary Goals
1. **Bug #1**: Prevent XSS attacks by sanitizing all user-supplied content before rendering
2. **Bug #2**: Prevent path traversal attacks by validating file paths before download
3. **Bug #3**: Prevent data corruption by validating coordinate ranges before storage

### Success Metrics
- All security tests pass (XSS attempts blocked, path traversal rejected)
- All coordinate validation tests pass (invalid coordinates rejected)
- No false positives (valid data still processed correctly)
- Backward compatibility maintained (existing features work as before)

---

## 3. REQUIREMENTS

### Bug #1: XSS Fix Requirements

**Functional Requirements**:
1. Replace `innerHTML` with `textContent` for user-supplied data (map_link)
2. Ensure HTML tags in map URLs are rendered as text, not executed
3. Maintain readable display of URLs in processing log

**Non-Functional Requirements**:
1. No performance impact
2. No visual changes to UI
3. Apply fix to all locations where user data is rendered

**Edge Cases**:
- Map URL contains `<script>alert('XSS')</script>` → Display as text, not execute
- Map URL contains `<img src=x onerror=alert(1)>` → Display as text, not execute
- Map URL contains legitimate HTML entities like `&amp;` → Display correctly

### Bug #2: Path Traversal Fix Requirements

**Functional Requirements**:
1. Validate `output_path` is within `PROCESSED_FOLDER` before serving file
2. Use `Path.resolve()` to resolve symbolic links and relative paths
3. Return 403 Forbidden error if path is outside allowed directory
4. Log all path traversal attempts for security monitoring

**Non-Functional Requirements**:
1. Minimal performance impact (< 1ms per download)
2. No changes to download UI/UX
3. Maintain cross-platform compatibility (Windows/Linux/Mac)

**Edge Cases**:
- Path contains `../../../etc/passwd` → Reject with 403
- Path contains symbolic link to `/etc` → Resolve and reject with 403
- Path contains Windows path like `C:\Windows\System32\config\SAM` → Reject with 403
- Valid path within PROCESSED_FOLDER → Allow download

### Bug #3: Coordinate Validation Fix Requirements

**Functional Requirements**:
1. Validate latitude is within range [-90, 90] after extraction
2. Validate longitude is within range [-180, 180] after extraction
3. Return `(None, None)` if coordinates are invalid
4. Log validation failures with extracted values
5. Update Comments column with specific validation error

**Non-Functional Requirements**:
1. No performance impact (validation is O(1))
2. Maintain backward compatibility with valid coordinates
3. Apply fix to both flask_app.py and map_converter.py (code duplication)

**Edge Cases**:
- Lat = 90.0, Lng = 180.0 → Valid (boundary case)
- Lat = -90.0, Lng = -180.0 → Valid (boundary case)
- Lat = 90.001, Lng = 0 → Invalid, reject
- Lat = 0, Lng = 180.001 → Invalid, reject
- Lat = 999, Lng = 500 → Invalid, reject with clear error message
- Lat = 200, Lng = -200 → Invalid, reject with clear error message

---

## 4. USER STORIES

### Bug #1: XSS Prevention
**As a** security-conscious user
**I want** malicious URLs to be rendered as text
**So that** my browser is not compromised by injected scripts

**Acceptance Criteria**:
- ✅ Upload file with map link containing `<script>alert('XSS')</script>`
- ✅ Processing log displays the script as text, not execute it
- ✅ No JavaScript errors in browser console
- ✅ URL is still readable and copyable

### Bug #2: Path Traversal Prevention
**As a** server administrator
**I want** file downloads to be restricted to processed files only
**So that** sensitive system files cannot be accessed by attackers

**Acceptance Criteria**:
- ✅ Normal download of processed file works as before
- ✅ Attempt to download `/etc/passwd` returns 403 Forbidden
- ✅ Attempt to download `../../../etc/passwd` returns 403 Forbidden
- ✅ Security event is logged with attempted path

### Bug #3: Coordinate Validation
**As a** data analyst
**I want** invalid coordinates to be rejected
**So that** my downstream mapping applications don't crash or display incorrect locations

**Acceptance Criteria**:
- ✅ Valid coordinates (lat=26.1, lng=28.0) are accepted
- ✅ Invalid latitude (lat=999) is rejected with error in Comments column
- ✅ Invalid longitude (lng=500) is rejected with error in Comments column
- ✅ Boundary values (lat=90, lng=180) are accepted
- ✅ Just-outside-boundary values (lat=90.001) are rejected

---

## 5. TECHNICAL DESIGN

### Bug #1: XSS Fix Design

**File**: `static/js/app.js`
**Lines**: 371

**Current Code**:
```javascript
// Line 371 - VULNERABLE
detail.innerHTML = `URL: <code>${log.map_link}</code>`;
```

**New Code**:
```javascript
// Line 371 - SECURE
const urlText = document.createTextNode(log.map_link);
const codeElement = document.createElement('code');
codeElement.appendChild(urlText);
detail.appendChild(document.createTextNode('URL: '));
detail.appendChild(codeElement);
```

**Alternative Simpler Approach** (if <code> not needed):
```javascript
// Line 371 - SECURE (simpler)
detail.textContent = `URL: ${log.map_link}`;
```

### Bug #2: Path Traversal Fix Design

**File**: `flask_app.py`
**Lines**: 450-474

**Current Code**:
```python
# Line 467 - VULNERABLE
return send_file(
    session_info['output_path'],  # No validation
    as_attachment=True,
    download_name=session_info['output_filename'],
    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)
```

**New Code**:
```python
# Lines 467-475 - SECURE
try:
    # Resolve and validate path
    output_path = Path(session_info['output_path']).resolve()
    processed_folder = app.config['PROCESSED_FOLDER'].resolve()

    # Check if path is within allowed directory
    if not output_path.is_relative_to(processed_folder):
        logger.error(f"Path traversal attempt: {output_path}")
        return jsonify({'error': 'Invalid file path'}), 403

    # Check if file exists
    if not output_path.exists():
        return jsonify({'error': 'File not found'}), 404

    return send_file(
        str(output_path),
        as_attachment=True,
        download_name=session_info['output_filename'],
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
except Exception as e:
    return jsonify({'error': f'Error downloading file: {str(e)}'}), 500
```

### Bug #3: Coordinate Validation Fix Design

**File**: `map_converter.py`
**Lines**: 52-95 (after each coordinate extraction)

**New Function**:
```python
def validate_coordinates(lng: float, lat: float) -> Tuple[Optional[float], Optional[float]]:
    """
    Validate longitude and latitude are within valid ranges.

    Args:
        lng: Longitude value
        lat: Latitude value

    Returns:
        Tuple of (lng, lat) if valid, or (None, None) if invalid
    """
    # Validate latitude range: -90 to 90
    if not (-90.0 <= lat <= 90.0):
        logger.error(f"Invalid latitude: {lat} (must be -90 to 90)")
        return None, None

    # Validate longitude range: -180 to 180
    if not (-180.0 <= lng <= 180.0):
        logger.error(f"Invalid longitude: {lng} (must be -180 to 180)")
        return None, None

    return lng, lat
```

**Update extract_coordinates_from_url()** - Add validation before returning:
```python
# After line 56 (Pattern 1)
if match:
    lat, lng = float(match.group(1)), float(match.group(2))
    return validate_coordinates(lng, lat)  # Add validation

# After line 63 (Pattern 2)
if match:
    lat, lng = float(match.group(1)), float(match.group(2))
    return validate_coordinates(lng, lat)  # Add validation

# After line 70 (Pattern 3)
if match:
    lat, lng = float(match.group(1)), float(match.group(2))
    return validate_coordinates(lng, lat)  # Add validation

# After lines 82, 85, 88, 91, 95 (Pattern 4)
# Validate before returning in each branch
```

**Also update flask_app.py** at lines 333, to call the same validation function.

---

## 6. TESTING STRATEGY

### Bug #1: XSS Testing

**Test Case 1: Script Tag Injection**
```
Input: Map link = "<script>alert('XSS')</script>"
Expected: Processing log displays "<script>alert('XSS')</script>" as text
Expected: No JavaScript alert shown
Expected: No errors in browser console
```

**Test Case 2: Image Tag Injection**
```
Input: Map link = "<img src=x onerror=alert(1)>"
Expected: Processing log displays "<img src=x onerror=alert(1)>" as text
Expected: No JavaScript alert shown
```

**Test Case 3: Valid URL**
```
Input: Map link = "https://maps.google.com/?q=-26.1076,28.0567"
Expected: Processing log displays URL as text
Expected: URL is readable and copyable
```

### Bug #2: Path Traversal Testing

**Test Case 1: Normal Download**
```
Setup: Process file normally
Action: Click download button
Expected: File downloads successfully
```

**Test Case 2: Path Traversal with ../../../**
```
Setup: Modify session_info['output_path'] = "/etc/passwd"
Action: Request /download/<session_id>
Expected: 403 Forbidden response
Expected: Error message: "Invalid file path"
Expected: Log entry: "Path traversal attempt: /etc/passwd"
```

**Test Case 3: Symbolic Link Traversal**
```
Setup: Create symlink in PROCESSED_FOLDER pointing to /etc
Setup: Modify session_info['output_path'] to symlink
Action: Request /download/<session_id>
Expected: 403 Forbidden response
```

**Test Case 4: Windows Path Traversal**
```
Setup: Modify session_info['output_path'] = "C:\\Windows\\System32\\config\\SAM"
Action: Request /download/<session_id>
Expected: 403 Forbidden response
```

### Bug #3: Coordinate Validation Testing

**Test Case 1: Valid Coordinates**
```
Input: URL with lat=-26.1076, lng=28.0567
Expected: Coordinates extracted and validated
Expected: LONG=28.0567, LATTs=-26.1076 in output
Expected: Comments="Success"
```

**Test Case 2: Invalid Latitude (> 90)**
```
Input: URL with lat=999.0, lng=28.0
Expected: Coordinates rejected
Expected: LONG=blank, LATTs=blank in output
Expected: Comments="Failed: Invalid latitude: 999.0 (must be -90 to 90)"
```

**Test Case 3: Invalid Longitude (> 180)**
```
Input: URL with lat=-26.0, lng=500.0
Expected: Coordinates rejected
Expected: LONG=blank, LATTs=blank in output
Expected: Comments="Failed: Invalid longitude: 500.0 (must be -180 to 180)"
```

**Test Case 4: Boundary Values (Valid)**
```
Input: URL with lat=90.0, lng=180.0
Expected: Coordinates accepted
Expected: LONG=180.0, LATTs=90.0 in output
Expected: Comments="Success"
```

**Test Case 5: Just Outside Boundary (Invalid)**
```
Input: URL with lat=90.001, lng=0.0
Expected: Coordinates rejected
Expected: LONG=blank, LATTs=blank in output
Expected: Comments="Failed: Invalid latitude: 90.001 (must be -90 to 90)"
```

---

## 7. ROLLOUT PLAN

### Phase 1: Bug #1 (XSS Fix) - 30 minutes
1. Update app.js line 371
2. Run manual XSS test with malicious script
3. Verify no alerts shown, text displayed correctly

### Phase 2: Bug #2 (Path Traversal Fix) - 1 hour
1. Update flask_app.py lines 467-475
2. Create test script to attempt path traversal
3. Verify 403 response for invalid paths
4. Verify normal downloads still work

### Phase 3: Bug #3 (Coordinate Validation Fix) - 2 hours
1. Add validate_coordinates() function to map_converter.py
2. Update all extraction patterns to call validation
3. Update flask_app.py to use same validation
4. Create test file with invalid coordinates
5. Verify invalid coordinates rejected with clear error messages

### Phase 4: Integration Testing - 1 hour
1. Run all existing tests
2. Run new security and validation tests
3. Verify no regressions

### Phase 5: Documentation - 30 minutes
1. Update README with security improvements
2. Create SECURITY_FIXES.md documenting changes
3. Update CHANGELOG

---

## 8. RISKS AND MITIGATIONS

### Risk 1: Breaking Changes
**Risk**: Coordinate validation might reject previously accepted values
**Mitigation**: Only reject clearly invalid values (outside valid ranges), boundary values are still accepted
**Rollback Plan**: Can disable validation by returning lng, lat without validation call

### Risk 2: Performance Impact
**Risk**: Path validation adds overhead to downloads
**Mitigation**: Path.resolve() and is_relative_to() are O(1) operations, < 1ms impact
**Monitoring**: Log download timing before/after fix

### Risk 3: Cross-Platform Compatibility
**Risk**: Path validation might behave differently on Windows vs Linux
**Mitigation**: Use pathlib.Path which handles platform differences
**Testing**: Test on Windows, Linux, and Mac

---

## 9. SUCCESS CRITERIA

### Must Have (Required for Production)
- ✅ All XSS attempts are blocked and displayed as text
- ✅ All path traversal attempts return 403 Forbidden
- ✅ All invalid coordinates are rejected with clear error messages
- ✅ All existing tests pass (no regressions)
- ✅ Normal functionality works as before (valid data processed correctly)

### Nice to Have (Future Improvements)
- 🔜 Add rate limiting to download endpoint (prevent DoS)
- 🔜 Add CSRF token validation
- 🔜 Add Content Security Policy headers
- 🔜 Add automated security testing (OWASP ZAP, Burp Suite)

---

## 10. OPEN QUESTIONS

1. **Q**: Should we log all validation failures for analytics?
   **A**: YES - Log coordinate validation failures to help improve regex patterns

2. **Q**: Should we add a "reason" field to processing log for validation failures?
   **A**: YES - Already exists in Comments column, will use that

3. **Q**: Should we validate coordinates at upload time too (proactive)?
   **A**: NO - Only validate after extraction, upload validation is for file format only

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
