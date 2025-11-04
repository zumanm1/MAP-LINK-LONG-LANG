#!/usr/bin/env python3
"""
Test file for Google Places API Text Search
Tests place name URLs that require API lookups
"""

import pandas as pd

# Create test data with place name searches
data = {
    'Name': [
        'Eiffel Tower (place name)',
        'Tokyo Tower (place name)',
        'Sydney Opera House (place name)',
        'Statue of Liberty (place name)',
        'Starbucks (generic search)',
        'Lumen Field (place name)',
        'Big Ben (place name)',
        'Golden Gate Bridge (place name)',
    ],
    'Region': ['Test'] * 8,
    'Maps link': [
        # Place name searches (require Google Places API)
        'https://www.google.com/maps/search/?api=1&query=Eiffel+Tower',
        'https://www.google.com/maps/search/?api=1&query=Tokyo+Tower',
        'https://www.google.com/maps/search/?api=1&query=Sydney+Opera+House',
        'https://www.google.com/maps/search/?api=1&query=Statue+of+Liberty',
        'https://www.google.com/maps/search/?api=1&query=starbucks',
        'https://www.google.com/maps/search/?api=1&query=lumen+field',
        'https://www.google.com/maps/search/?api=1&query=Big+Ben',
        'https://www.google.com/maps/search/?api=1&query=Golden+Gate+Bridge',
    ],
    'LONG': [None] * 8,
    'LATTs': [None] * 8,
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
output_file = 'test_place_names_input.xlsx'
df.to_excel(output_file, index=False)

print(f"✅ Created {output_file}")
print(f"\n🧪 Test URLs:")
print(f"  All URLs contain PLACE NAMES (not coordinates)")
print(f"  Require Google Places API Text Search (Method 4)")

print(f"\n⚙️  Setup Instructions:")
print(f"  1. Get API key: https://console.cloud.google.com/")
print(f"  2. Enable: Places API")
print(f"  3. Set environment variable:")
print(f"     export GOOGLE_MAPS_API_KEY='your-api-key-here'")

print(f"\n📋 Testing Instructions:")
print(f"  python map_converter_enhanced.py {output_file} test_place_names_output.xlsx")

print(f"\n✅ Expected: All 8 place names should resolve to coordinates via API")
print(f"\n❌ Without API Key: All 8 will fail (expected behavior)")

print(f"\nExpected Coordinates (approximate):")
print(f"  1. Eiffel Tower: lng=2.2945, lat=48.8584")
print(f"  2. Tokyo Tower: lng=139.7454, lat=35.6586")
print(f"  3. Sydney Opera House: lng=151.2153, lat=-33.8568")
print(f"  4. Statue of Liberty: lng=-74.0445, lat=40.6892")
print(f"  5. Starbucks: (varies by location)")
print(f"  6. Lumen Field: lng=-122.3316, lat=47.5952")
print(f"  7. Big Ben: lng=-0.1246, lat=51.5007")
print(f"  8. Golden Gate Bridge: lng=-122.4783, lat=37.8199")
