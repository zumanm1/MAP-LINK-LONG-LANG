#!/usr/bin/env python3
"""
Create test file with various complex Google Maps URL formats
"""

import pandas as pd

# Create test data with various URL formats
data = {
    'Name': [
        'Standard Place URL',
        'Query Parameter URL',
        'Search URL with Query',
        'Search URL (Complex)',
        'Google.co.za Regional',
        'Place with Special Chars',
        'Direct Coordinates',
        'Zoom Level URL',
    ],
    'Region': [
        'Test',
        'Test',
        'Test',
        'Test',
        'Test',
        'Test',
        'Test',
        'Test',
    ],
    'Maps link': [
        'https://www.google.com/maps/place/Sandton/@-26.108204,28.0527061,17z',
        'https://maps.google.com/?q=-33.9249,18.4241',
        'https://www.google.com/maps/search/mall/@-26.1076,28.0567,15z',
        'https://www.google.com/maps/search/school+in+barnard+stadium/@-26.0943391,28.1866209,13z/data=!3m1!4b1?entry=ttu&g_ep=EgoyMDI1MTEwMi4wIKXMDSoASAFQAw%3D%3D',
        'https://www.google.co.za/maps/place/Cape+Town/@-33.9249,18.4241,12z',
        'https://www.google.com/maps/place/V%26A+Waterfront/@-33.9022,18.4178,16z',
        'https://www.google.com/maps/@-29.8587,31.0218,14z',
        'https://www.google.com/maps/place/Location/@-25.7479,28.2293,18z/data=abc123',
    ],
    'LONG': [None] * 8,
    'LATTs': [None] * 8,
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
output_file = 'test_complex_urls_input.xlsx'
df.to_excel(output_file, index=False)

print(f"✅ Created {output_file}")
print(f"\n🧪 Test URL Formats:")
print(f"  1. Standard place URL with zoom")
print(f"  2. Query parameter format")
print(f"  3. Search URL with @coordinates")
print(f"  4. Complex search URL with data params (YOUR EXAMPLE)")
print(f"  5. Regional domain (google.co.za)")
print(f"  6. URL-encoded special characters (%26 = &)")
print(f"  7. Direct coordinates with @ symbol")
print(f"  8. Place URL with zoom and data parameter")

print(f"\n📋 Testing Instructions:")
print(f"  python map_converter_enhanced.py {output_file} test_complex_urls_output.xlsx")

print(f"\n✅ Expected: All 8 URLs should extract coordinates successfully")
