#!/usr/bin/env python3
"""
Create comprehensive validation test file with various issues
"""

import pandas as pd
import numpy as np

# Create test data with various issues
data = {
    'Name': [
        # Valid names
        'Sandton_2334_FSUDG_23',
        'CAPE TOWN CBD',
        '23232_Durban_Main',
        'Pretoria 12313',

        # Edge case names
        'Site_A_B_C_123',
        '',  # Empty string name
        None,  # NaN name
        '!!!Special###Chars',
        'a',  # Single character
        '12345',  # Numbers only

        # More valid names
        'Location|Zone|A12',
        'Building[Section-B]',
        '  Spaces_Around  ',
        'MiXeD_CaSe_123',
        'Name.With.Dots',

        # Additional test cases
        'Normal Location',
        'Test_Site_001',
        'Area-North-456',
        'Complex_Name_With_Many_Parts_789',
        'Short',
    ],
    'Region': [
        # Valid regions
        'Gauteng',
        'Western Cape',
        'KwaZulu-Natal',
        'Gauteng',

        # Edge case regions
        'Free State',
        'Eastern Cape',
        'Mpumalanga',
        'Limpopo',
        'North West',
        'Northern Cape',

        # More regions
        'Gauteng',
        'Western Cape',
        'KwaZulu-Natal',
        'Gauteng',
        'Western Cape',

        # Additional regions
        'Free State',
        'Eastern Cape',
        'Gauteng',
        'Western Cape',
        'KwaZulu-Natal',
    ],
    'Maps link': [
        # Valid URLs
        'https://maps.google.com/?q=-26.1076,28.0567',
        'https://www.google.com/maps/@-33.9249,18.4241,15z',
        'https://maps.google.com/?q=-29.8587,31.0218',
        'https://maps.google.com/?q=-25.7479,28.2293',

        # Issues: Empty/blank/invalid
        None,  # NaN/None
        '',  # Empty string
        '   ',  # Whitespace only
        'not a valid url',  # Invalid URL
        'http://example.com',  # Not a map URL
        'maps.google.com',  # Missing protocol

        # More valid URLs
        'https://www.google.com/maps/place/@-23.9045,29.4689,17z',
        'https://maps.google.com/?q=-32.9783,27.8708',
        'https://maps.google.com/?q=-33.9608,25.6022',
        'https://www.google.com/maps/@-33.8918,18.5810,15z',
        'https://maps.google.com/?q=-26.2041,28.0473',

        # Additional test cases
        'https://goo.gl/maps/invalidshorturl',  # Invalid shortened URL
        'https://maps.google.com/?q=-28.7451,24.7519',  # Valid
        'https://maps.google.com/?q=-25.7863,28.2775',  # Valid
        None,  # Another NaN
        'https://maps.google.com/?q=-26.5225,27.8546',  # Valid
    ],
    'LONG': [None] * 20,  # All empty initially
    'LATTs': [None] * 20,  # All empty initially
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
output_file = 'test_validation_input.xlsx'
df.to_excel(output_file, index=False)

print(f"✅ Created {output_file} with {len(df)} rows")
print(f"\nBreakdown:")
print(f"  - Valid map links: {df['Maps link'].notna().sum() - (df['Maps link'] == '').sum() - (df['Maps link'] == '   ').sum()}")
print(f"  - None/NaN links: {df['Maps link'].isna().sum()}")
print(f"  - Empty string links: {(df['Maps link'] == '').sum()}")
print(f"  - Whitespace only links: {(df['Maps link'] == '   ').sum()}")
print(f"  - Invalid URLs: ~3-4")
print(f"\nName edge cases:")
print(f"  - Empty string name: 1")
print(f"  - NaN name: 1")
print(f"  - Complex names: {len(df) - 2}")
print(f"\n📋 File structure:")
print(f"  Columns: {df.columns.tolist()}")
print(f"\n🔍 First 10 rows preview:")
print(df.head(10).to_string(index=True))
