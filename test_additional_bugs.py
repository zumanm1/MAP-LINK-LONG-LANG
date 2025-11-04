#!/usr/bin/env python3
"""
Additional Critical Bug Tests
Focus on edge cases and data corruption scenarios
"""

from map_converter import extract_coordinates_from_url
import pandas as pd

def test_pattern4_fallback_bugs():
    """Test Pattern 4 (fallback) coordinate detection bugs"""

    print("\n🔍 Testing Pattern 4 Fallback Bugs\n")
    print("=" * 80)

    test_cases = [
        # URLs that should NOT match Pattern 4 but might
        ("https://www.google.com/maps/search/26.108204,28.0527061/", False, "Search URL with trailing slash"),
        ("https://www.google.com/maps/dir/40.7128,-74.0060/41.8781,-87.6298/", False, "Directions URL with multiple coords"),
        ("Price: 26.50, Tax: 18.99", False, "Non-coordinate decimal numbers"),
        ("Version 3.14, Build 2.71", False, "Version numbers"),
        ("https://example.com/api?lat=26.108204&lng=28.0527061", False, "Separate lat/lng params"),

        # URLs that SHOULD match Pattern 4
        ("Just coordinates: -26.108204, 28.0527061", True, "Text with coordinates"),
        ("Coords in text -26.108204,28.0527061 more text", True, "Coordinates embedded in text"),
        ("-26.108204,28.0527061", True, "Pure coordinates"),

        # Ambiguous cases (both coords > 90)
        ("https://www.google.com/maps/search/120.5,150.8/", False, "Search with both > 90"),
        ("Text with 120.5, 150.8 numbers", True, "Text with both > 90 (should still extract)"),
    ]

    bugs_found = []

    for url, should_match, description in test_cases:
        print(f"\nTest: {description}")
        print(f"  URL: {url}")
        print(f"  Should match: {should_match}")

        lng, lat = extract_coordinates_from_url(url)

        print(f"  Result: lng={lng}, lat={lat}")

        if should_match:
            if lng is None or lat is None:
                print(f"  ❌ FAIL - Should have matched")
                bugs_found.append(f"Pattern 4 BUG: Missed valid coords in '{description}'")
            else:
                print(f"  ✅ PASS")
        else:
            if lng is not None and lat is not None:
                print(f"  ❌ FAIL - Should NOT have matched")
                bugs_found.append(f"Pattern 4 BUG: False positive for '{description}': {url}")
            else:
                print(f"  ✅ PASS")

    print(f"\n{'=' * 80}")
    return bugs_found


def test_coordinate_range_validation():
    """Test coordinate range validation bugs"""

    print("\n\n🌍 Testing Coordinate Range Validation\n")
    print("=" * 80)

    test_cases = [
        # Valid ranges
        ("https://www.google.com/maps/@-90.0,180.0,17z", True, "Max valid lat/lng"),
        ("https://www.google.com/maps/@90.0,-180.0,17z", True, "Max valid positive lat, min lng"),
        ("https://www.google.com/maps/@0.0,0.0,17z", True, "Zero coordinates"),

        # Invalid ranges (outside Earth bounds)
        ("https://www.google.com/maps/@-91.0,28.0,17z", True, "Latitude < -90 (INVALID but accepted)"),
        ("https://www.google.com/maps/@91.0,28.0,17z", True, "Latitude > 90 (INVALID but accepted)"),
        ("https://www.google.com/maps/@-26.0,181.0,17z", True, "Longitude > 180 (INVALID but accepted)"),
        ("https://www.google.com/maps/@-26.0,-181.0,17z", True, "Longitude < -180 (INVALID but accepted)"),

        # Edge cases
        ("https://www.google.com/maps/@200.0,300.0,17z", True, "Both way out of range"),
    ]

    bugs_found = []

    for url, should_extract, description in test_cases:
        print(f"\nTest: {description}")
        print(f"  URL: {url}")

        lng, lat = extract_coordinates_from_url(url)

        print(f"  Result: lng={lng}, lat={lat}")

        if lng is not None and lat is not None:
            # Check if values are within valid Earth coordinate ranges
            if abs(lat) > 90:
                print(f"  ⚠️  WARNING - Latitude out of valid range: {lat}")
                bugs_found.append(f"VALIDATION BUG: Accepted invalid latitude {lat} from '{description}'")

            if abs(lng) > 180:
                print(f"  ⚠️  WARNING - Longitude out of valid range: {lng}")
                bugs_found.append(f"VALIDATION BUG: Accepted invalid longitude {lng} from '{description}'")

            if abs(lat) <= 90 and abs(lng) <= 180:
                print(f"  ✅ PASS - Valid coordinates")
        else:
            print(f"  ⚠️  Could not extract")

    print(f"\n{'=' * 80}")
    return bugs_found


def test_multiple_coordinate_pairs():
    """Test URLs with multiple coordinate pairs"""

    print("\n\n🔢 Testing Multiple Coordinate Pairs\n")
    print("=" * 80)

    test_cases = [
        # URLs with multiple coordinate pairs
        ("https://www.google.com/maps/@40.7128,-74.0060,17z/@41.8781,-87.6298,15z",
         -74.0060, 40.7128, "Multiple @ patterns (should use first)"),

        ("https://www.google.com/maps?q=40.7128,-74.0060&ll=41.8781,-87.6298",
         -74.0060, 40.7128, "q= and ll= params (should use first match)"),

        ("https://www.google.com/maps/dir/40.7128,-74.0060/41.8781,-87.6298/",
         None, None, "Directions with multiple coords (should fail or use first)"),

        ("Text: 40.7128,-74.0060 and also 41.8781,-87.6298 here",
         -74.0060, 40.7128, "Text with multiple coords (should use first)"),
    ]

    bugs_found = []

    for url, expected_lng, expected_lat, description in test_cases:
        print(f"\nTest: {description}")
        print(f"  URL: {url}")
        print(f"  Expected: lng={expected_lng}, lat={expected_lat}")

        lng, lat = extract_coordinates_from_url(url)

        print(f"  Actual: lng={lng}, lat={lat}")

        if expected_lng is None:
            if lng is not None:
                print(f"  ⚠️  WARNING - Extracted when should fail: lng={lng}, lat={lat}")
                # Not necessarily a bug, just noting behavior
            else:
                print(f"  ✅ PASS")
        else:
            if lng is None or lat is None:
                print(f"  ❌ FAIL - Should have extracted coordinates")
                bugs_found.append(f"BUG: Failed to extract from '{description}'")
            elif abs(lng - expected_lng) > 0.0001 or abs(lat - expected_lat) > 0.0001:
                print(f"  ⚠️  WARNING - Different coordinates than expected")
                print(f"     This may indicate extracting wrong pair")
                bugs_found.append(f"BUG: Extracted wrong coordinate pair from '{description}'")
            else:
                print(f"  ✅ PASS")

    print(f"\n{'=' * 80}")
    return bugs_found


def test_special_characters():
    """Test URLs with special characters and encoding"""

    print("\n\n🔤 Testing Special Characters and Encoding\n")
    print("=" * 80)

    test_cases = [
        ("https://www.google.com/maps/@-26.108204,28.0527061,17z?entry=ttu",
         28.0527061, -26.108204, "URL with query params"),

        ("https://www.google.com/maps/@-26.108204,28.0527061,17z#test",
         28.0527061, -26.108204, "URL with fragment"),

        ("https://www.google.com/maps/place/Caf%C3%A9/@-26.108204,28.0527061,17z",
         28.0527061, -26.108204, "URL with encoded characters"),

        ("https://www.google.com/maps/place/Location+Name/@-26.108204,28.0527061,17z",
         28.0527061, -26.108204, "URL with + encoding"),

        ("-26.108204,\t28.0527061",
         28.0527061, -26.108204, "Coordinates with tab separator"),

        ("-26.108204,\n28.0527061",
         28.0527061, -26.108204, "Coordinates with newline"),
    ]

    bugs_found = []

    for url, expected_lng, expected_lat, description in test_cases:
        print(f"\nTest: {description}")
        print(f"  URL: {repr(url)}")
        print(f"  Expected: lng={expected_lng}, lat={expected_lat}")

        lng, lat = extract_coordinates_from_url(url)

        print(f"  Actual: lng={lng}, lat={lat}")

        if lng is None or lat is None:
            print(f"  ❌ FAIL - Could not extract")
            bugs_found.append(f"BUG: Failed with special chars in '{description}'")
        elif abs(lng - expected_lng) > 0.0001 or abs(lat - expected_lat) > 0.0001:
            print(f"  ❌ FAIL - Wrong coordinates")
            bugs_found.append(f"BUG: Wrong coords with special chars in '{description}'")
        else:
            print(f"  ✅ PASS")

    print(f"\n{'=' * 80}")
    return bugs_found


def test_excel_output_corruption():
    """Test for data corruption in Excel output"""

    print("\n\n📊 Testing Excel Output Data Integrity\n")
    print("=" * 80)

    import tempfile
    import os

    # Create test DataFrame
    test_data = {
        'Name': ['Loc1', 'Loc2', 'Loc3', 'Loc4', 'Loc5'],
        'Region': ['R1', 'R2', 'R3', 'R4', 'R5'],
        'Map link': [
            'https://www.google.com/maps/@-26.108204,28.0527061,17z',
            'https://www.google.com/maps/@40.7128,-74.0060,17z',
            '',  # Empty
            'https://www.google.com/maps/@-33.8688,151.2093,17z',
            'invalid_url'
        ]
    }

    df = pd.DataFrame(test_data)

    # Process like the main code does
    df['LONG'] = None
    df['LATTs'] = None
    df['Comments'] = None

    for idx, row in df.iterrows():
        map_link = row['Map link']

        if pd.isna(map_link) or str(map_link).strip() == '':
            df.at[idx, 'Comments'] = 'Skipped: No map link'
            continue

        lng, lat = extract_coordinates_from_url(str(map_link))

        if lng is not None and lat is not None:
            df.at[idx, 'LONG'] = lng
            df.at[idx, 'LATTs'] = lat
            df.at[idx, 'Comments'] = 'Success'
        else:
            df.at[idx, 'Comments'] = 'Failed'

    # Save and reload to test Excel handling
    bugs_found = []

    try:
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            tmp_path = tmp.name

        print(f"\nSaving to temporary Excel file...")
        df.to_excel(tmp_path, index=False)

        print(f"Reading back from Excel...")
        df_loaded = pd.read_excel(tmp_path)

        # Compare
        print(f"\nComparing original vs loaded data:\n")

        for idx in range(len(df)):
            orig_lng = df.iloc[idx]['LONG']
            orig_lat = df.iloc[idx]['LATTs']
            load_lng = df_loaded.iloc[idx]['LONG']
            load_lat = df_loaded.iloc[idx]['LATTs']

            print(f"Row {idx}: {df.iloc[idx]['Name']}")
            print(f"  Original: lng={orig_lng}, lat={orig_lat}")
            print(f"  Loaded:   lng={load_lng}, lat={load_lat}")

            # Check for data corruption
            if pd.notna(orig_lng) and pd.notna(load_lng):
                if abs(orig_lng - load_lng) > 0.000001:
                    print(f"  ❌ FAIL - Longitude corrupted")
                    bugs_found.append(f"CORRUPTION: Longitude changed at row {idx}")

                if abs(orig_lat - load_lat) > 0.000001:
                    print(f"  ❌ FAIL - Latitude corrupted")
                    bugs_found.append(f"CORRUPTION: Latitude changed at row {idx}")

                if abs(orig_lng - load_lng) <= 0.000001 and abs(orig_lat - load_lat) <= 0.000001:
                    print(f"  ✅ PASS")
            elif pd.isna(orig_lng) and pd.isna(load_lng):
                print(f"  ✅ PASS - Both None")
            else:
                print(f"  ❌ FAIL - None/value mismatch")
                bugs_found.append(f"CORRUPTION: None/value mismatch at row {idx}")

        # Cleanup
        os.unlink(tmp_path)

    except Exception as e:
        print(f"  ❌ ERROR: {str(e)}")
        bugs_found.append(f"Excel I/O ERROR: {str(e)}")

    print(f"\n{'=' * 80}")
    return bugs_found


if __name__ == "__main__":
    print("\n" + "🔬 " * 30)
    print("\n  ADDITIONAL CRITICAL BUG TESTS")
    print("\n" + "🔬 " * 30)

    all_bugs = []

    # Run all tests
    all_bugs.extend(test_pattern4_fallback_bugs())
    all_bugs.extend(test_coordinate_range_validation())
    all_bugs.extend(test_multiple_coordinate_pairs())
    all_bugs.extend(test_special_characters())
    all_bugs.extend(test_excel_output_corruption())

    # Print summary
    print("\n\n" + "=" * 80)
    print("\n📋 BUGS FOUND IN ADDITIONAL TESTS\n")
    print("=" * 80)

    if all_bugs:
        print(f"\n🚨 Found {len(all_bugs)} bugs:\n")
        for i, bug in enumerate(all_bugs, 1):
            print(f"{i}. {bug}")
        exit(1)
    else:
        print("\n✅ No bugs detected in additional tests!")
        exit(0)
