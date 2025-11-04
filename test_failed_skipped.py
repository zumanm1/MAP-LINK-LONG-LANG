#!/usr/bin/env python3
"""
Create test file with mixed results (success, failed, skipped)
"""

import pandas as pd

# Create test data with various scenarios
data = {
    'Name': [
        'Valid URL - Success',
        'Invalid URL - Failed',
        'Empty Map Link - Skipped',
        'Valid URL - Success 2',
        'Bad Format - Failed',
        'Blank - Skipped',
    ],
    'Region': ['Test'] * 6,
    'Maps link': [
        'https://www.google.com/maps/place/Sandton/@-26.108204,28.0527061,17z',
        'https://invalid-map-url-without-coords.com',
        None,  # This will be skipped (blank)
        'https://maps.google.com/?q=-33.9249,18.4241',
        'not-a-url-at-all',
        '',  # This will be skipped (blank)
    ],
    'LONG': [None] * 6,
    'LATTs': [None] * 6,
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
output_file = 'test_failed_skipped_input.xlsx'
df.to_excel(output_file, index=False)

print(f"✅ Created {output_file}")
print(f"\n🧪 Test Scenarios:")
print(f"  2 rows should succeed")
print(f"  2 rows should fail (invalid URLs)")
print(f"  2 rows should be skipped (blank/empty)")
print(f"\n📋 Expected Output Files:")
print(f"  1. test_failed_skipped_output.xlsx (all 6 rows)")
print(f"  2. test_failed_skipped_output_failed.xlsx (2 rows)")
print(f"  3. test_failed_skipped_output_skipped.xlsx (2 rows)")
