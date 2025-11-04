#!/usr/bin/env python3
"""
Test file for new URL formats:
1. Google Maps API format with URL-encoded coordinates
2. URLs ending in =en (language parameter)
"""

import pandas as pd

# Create test data with new URL formats
data = {
    'Name': [
        'Lumen Field (API format)',
        'Seattle Space Needle (API format)',
        'Tokyo Tower (with =en)',
        'Paris Eiffel Tower (API + =en)',
        'Cape Town (google.co.za with =en)',
        'Sydney Opera House (API format)',
        'London Big Ben (with language)',
        'New York Central Park (API)',
    ],
    'Region': ['Test'] * 8,
    'Maps link': [
        # Google Maps API format with URL-encoded comma
        'https://www.google.com/maps/search/?api=1&query=47.5951518%2C-122.3316393',

        # API format with place ID (coordinates still in URL)
        'https://www.google.com/maps/search/?api=1&query=47.5951518%2C-122.3316393&query_place_id=ChIJKxjxuaNqkFQR3CK6O1HNNqY',

        # URL ending in =en (language parameter)
        'https://www.google.com/maps/place/Tokyo+Tower/@35.6586,139.7454,17z?hl=en',

        # API format with language parameter
        'https://www.google.com/maps/search/?api=1&query=48.8584%2C2.2945&hl=en',

        # Regional domain with language
        'https://www.google.co.za/maps/place/Cape+Town/@-33.9249,18.4241,12z?hl=en',

        # API format Australia
        'https://www.google.com/maps/search/?api=1&query=-33.8568%2C151.2153',

        # Standard URL with language parameter
        'https://www.google.com/maps/place/Big+Ben/@51.5007,-0.1246,17z?hl=en',

        # API format New York
        'https://www.google.com/maps/search/?api=1&query=40.7829%2C-73.9654',
    ],
    'LONG': [None] * 8,
    'LATTs': [None] * 8,
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
output_file = 'test_new_url_formats_input.xlsx'
df.to_excel(output_file, index=False)

print(f"✅ Created {output_file}")
print(f"\n🧪 Test URL Formats:")
print(f"  1. Google Maps API format: ?api=1&query=lat%2Clng")
print(f"  2. API format with place ID: ?query=lat%2Clng&query_place_id=...")
print(f"  3. URLs with language parameter: ?hl=en")
print(f"  4. Regional domains with language: google.co.za?hl=en")
print(f"  5. Combined API + language parameters")

print(f"\n📋 Testing Instructions:")
print(f"  python map_converter_enhanced.py {output_file} test_new_url_formats_output.xlsx")

print(f"\n✅ Expected: All 8 URLs should extract coordinates successfully")
print(f"\nExpected Coordinates:")
print(f"  1. Lumen Field: lng=-122.3316393, lat=47.5951518")
print(f"  2. Space Needle: lng=-122.3493, lat=47.6205")
print(f"  3. Tokyo Tower: lng=139.7454, lat=35.6586")
print(f"  4. Eiffel Tower: lng=2.2945, lat=48.8584")
print(f"  5. Cape Town: lng=18.4241, lat=-33.9249")
print(f"  6. Sydney: lng=151.2153, lat=-33.8568")
print(f"  7. Big Ben: lng=-0.1246, lat=51.5007")
print(f"  8. Central Park: lng=-73.9654, lat=40.7829")
