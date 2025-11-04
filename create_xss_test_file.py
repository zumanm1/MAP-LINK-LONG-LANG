#!/usr/bin/env python3
"""
Create test file with XSS payloads for manual validation
"""

import pandas as pd

# Create test data with various XSS payloads
data = {
    'Name': [
        'XSS Test 1: Script Alert',
        'XSS Test 2: Image Error',
        'XSS Test 3: SVG Onload',
        'XSS Test 4: Body Onload',
        'XSS Test 5: Valid URL (Control)',
    ],
    'Region': [
        'Test Region',
        'Test Region',
        'Test Region',
        'Test Region',
        'Gauteng',
    ],
    'Maps link': [
        '<script>alert("XSS")</script>',  # Classic script tag
        '<img src=x onerror=alert(1)>',  # Image error handler
        '<svg/onload=alert(\'XSS\')>',  # SVG onload
        '<body onload=alert("XSS")>',  # Body onload
        'https://maps.google.com/?q=-26.1076,28.0567',  # Valid URL (control)
    ],
    'LONG': [None] * 5,
    'LATTs': [None] * 5,
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
output_file = 'test_xss_validation_input.xlsx'
df.to_excel(output_file, index=False)

print(f"✅ Created {output_file}")
print(f"\n🔒 XSS Test Payloads:")
print(f"  1. Script Alert: <script>alert(\"XSS\")</script>")
print(f"  2. Image Error: <img src=x onerror=alert(1)>")
print(f"  3. SVG Onload: <svg/onload=alert('XSS')>")
print(f"  4. Body Onload: <body onload=alert(\"XSS\")>")
print(f"  5. Valid URL (control): https://maps.google.com/?q=-26.1076,28.0567")

print(f"\n📋 Manual Testing Instructions:")
print(f"  1. Start Flask app: python flask_app.py")
print(f"  2. Open browser: http://localhost:5000")
print(f"  3. Upload this file: {output_file}")
print(f"  4. Click 'Process'")
print(f"  5. View processing log section")
print(f"  6. ✅ EXPECTED: XSS payloads displayed as plain text (not executed)")
print(f"  7. ❌ FAIL IF: Any alert() popup appears")
print(f"  8. ❌ FAIL IF: Browser console shows errors (F12)")

print(f"\n🎯 What to Look For:")
print(f"  - Processing log should show XSS payloads as text")
print(f"  - No JavaScript alerts should appear")
print(f"  - No errors in browser console (F12)")
print(f"  - URL section should display payloads safely inside <code> tags")
print(f"  - Valid URL (row 5) should process successfully")
