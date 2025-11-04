#!/usr/bin/env python3
"""
Create test file with invalid coordinates to verify validation is working
"""

import pandas as pd

# Create test data with invalid coordinates
data = {
    'Name': [
        'Valid Coordinates',
        'Invalid Lat > 90',
        'Invalid Lat < -90',
        'Invalid Lng > 180',
        'Invalid Lng < -180',
        'Just Over Boundary Lat',
        'Just Over Boundary Lng',
        'Both Invalid',
        'Boundary Valid (90, 180)',
        'Boundary Valid (-90, -180)',
    ],
    'Region': [
        'Test Region',
        'Test Region',
        'Test Region',
        'Test Region',
        'Test Region',
        'Test Region',
        'Test Region',
        'Test Region',
        'Test Region',
        'Test Region',
    ],
    'Maps link': [
        'https://maps.google.com/?q=-26.1076,28.0567',  # Valid
        'https://maps.google.com/?q=999.0,28.0',  # Invalid lat > 90
        'https://maps.google.com/?q=-200.0,28.0',  # Invalid lat < -90
        'https://maps.google.com/?q=-26.0,500.0',  # Invalid lng > 180
        'https://maps.google.com/?q=-26.0,-300.0',  # Invalid lng < -180
        'https://maps.google.com/?q=90.001,0.0',  # Just over boundary lat
        'https://maps.google.com/?q=0.0,180.001',  # Just over boundary lng
        'https://maps.google.com/?q=999.0,500.0',  # Both invalid
        'https://maps.google.com/?q=90.0,180.0',  # Boundary valid
        'https://maps.google.com/?q=-90.0,-180.0',  # Boundary valid
    ],
    'LONG': [None] * 10,
    'LATTs': [None] * 10,
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
output_file = 'test_invalid_coords_input.xlsx'
df.to_excel(output_file, index=False)

print(f"✅ Created {output_file}")
print(f"\n🧪 Test Cases:")
print(f"  1. Valid Coordinates (-26.1076, 28.0567) → Should ACCEPT ✅")
print(f"  2. Invalid Lat > 90 (999.0, 28.0) → Should REJECT ❌")
print(f"  3. Invalid Lat < -90 (-200.0, 28.0) → Should REJECT ❌")
print(f"  4. Invalid Lng > 180 (-26.0, 500.0) → Should REJECT ❌")
print(f"  5. Invalid Lng < -180 (-26.0, -300.0) → Should REJECT ❌")
print(f"  6. Just Over Boundary Lat (90.001, 0.0) → Should REJECT ❌")
print(f"  7. Just Over Boundary Lng (0.0, 180.001) → Should REJECT ❌")
print(f"  8. Both Invalid (999.0, 500.0) → Should REJECT ❌")
print(f"  9. Boundary Valid (90.0, 180.0) → Should ACCEPT ✅")
print(f"  10. Boundary Valid (-90.0, -180.0) → Should ACCEPT ✅")

print(f"\n📋 Expected Results:")
print(f"  - Rows 1, 9, 10: Should have coordinates (ACCEPTED)")
print(f"  - Rows 2-8: Should have NaN/blank (REJECTED)")
print(f"  - Comments column should show validation errors for rejected rows")
