#!/usr/bin/env python3
"""
Create test file with a bad/slow map link to test retry and timeout logic
"""

import pandas as pd

# Create test data with various URL types including a bad one
data = {
    'Name': [
        'Sandton City',
        'Cape Town CBD',
        'Bad URL Link',
        'Durban Beach',
        'Empty Link Test',
        'Pretoria East',
    ],
    'Region': [
        'Gauteng',
        'Western Cape',
        'Test Region',
        'KwaZulu-Natal',
        'Test Region',
        'Gauteng',
    ],
    'Maps link': [
        'https://maps.google.com/?q=-26.1076,28.0567',  # Valid
        'https://www.google.com/maps/@-33.9249,18.4241,15z',  # Valid
        'https://thisurldoesnotexist.fake.example/badlink',  # Bad URL - will timeout/fail
        'https://maps.google.com/?q=-29.8587,31.0218',  # Valid
        None,  # Empty - should skip
        'https://maps.google.com/?q=-25.7479,28.2293',  # Valid
    ],
    'LONG': [None] * 6,
    'LATTs': [None] * 6,
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
output_file = 'test_with_bad_link.xlsx'
df.to_excel(output_file, index=False)

print(f"✅ Created {output_file}")
print(f"\nTest cases:")
print(f"  1. Valid URL (Sandton)")
print(f"  2. Valid URL (Cape Town)")
print(f"  3. ❌ BAD URL (will fail/timeout after retries)")
print(f"  4. Valid URL (Durban)")
print(f"  5. None/Empty (will skip)")
print(f"  6. Valid URL (Pretoria)")
print(f"\nExpected behavior:")
print(f"  - Rows 1,2,4,6: Should succeed")
print(f"  - Row 3: Should fail after 3 attempts with timeout message in Comments")
print(f"  - Row 5: Should skip with message in Comments")
print(f"  - Progress tracking visible: 'Processing row X/6 (XX.X%)'")
print(f"  - Attempt numbers visible: 'Attempt 1/3', 'Attempt 2/3', etc.")
