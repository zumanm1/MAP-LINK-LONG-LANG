#!/usr/bin/env python3
"""
Critical Bug Detection Tests
Tests for coordinate extraction bugs, regex pattern issues, and data handling
"""

from map_converter import extract_coordinates_from_url
import pandas as pd
import numpy as np
import tempfile
import os

def test_regex_pattern_bugs():
    """Test for regex pattern bugs that miss valid URLs or match invalid ones"""

    print("\n🔍 Testing Regex Pattern Bugs\n")
    print("=" * 80)

    test_cases = [
        # Valid URLs that might be missed
        ("https://www.google.com/maps/@-26.108204,28.0527061,17z/data=!3m1!4b1", 28.0527061, -26.108204, "Should match: URL with /data parameter"),
        ("https://www.google.com/maps/place/Location/@-26.1,28.05,17z", 28.05, -26.1, "Should match: Short decimal places"),
        ("https://www.google.com/maps/place/@-26.108204,28.0527061", 28.0527061, -26.108204, "Should match: No zoom parameter"),
        ("https://www.google.com/maps?q=-26.108204,28.0527061&z=17", 28.0527061, -26.108204, "Should match: Query with zoom"),
        ("https://maps.google.com/?q=-26.108204,28.0527061&ll=-26,28", 28.0527061, -26.108204, "Should match: Query with extra params"),

        # Integer coordinates (no decimal point)
        ("https://www.google.com/maps/@-26,28,17z", None, None, "Should NOT match: Integer coords (no decimal)"),
        ("https://www.google.com/maps?q=-26,28", None, None, "Should NOT match: Integer coords (no decimal)"),
        ("-26,28", None, None, "Should NOT match: Integer coords (no decimal)"),

        # Edge case: Large decimal precision
        ("https://www.google.com/maps/@-26.1082041234567,28.0527061234567,17z", 28.0527061234567, -26.1082041234567, "Should match: High precision"),

        # Edge case: Zero coordinates
        ("https://www.google.com/maps/@0.0,0.0,17z", 0.0, 0.0, "Should match: Zero coordinates"),

        # Edge case: Coordinates without @ symbol
        ("https://www.google.com/maps/search/26.108204,28.0527061/", None, None, "Should NOT match: No @ or q= pattern"),

        # Shortened URL format (should be handled after resolution)
        ("https://goo.gl/maps/abc123", None, None, "May fail: Shortened URL without resolution"),
        ("https://maps.app.goo.gl/abc123", None, None, "May fail: Shortened URL without resolution"),
    ]

    bugs_found = []
    passed = 0
    failed = 0

    for url, expected_lng, expected_lat, description in test_cases:
        print(f"\nTest: {description}")
        print(f"  URL: {url}")
        print(f"  Expected: lng={expected_lng}, lat={expected_lat}")

        lng, lat = extract_coordinates_from_url(url)

        print(f"  Actual:   lng={lng}, lat={lat}")

        if expected_lng is None:
            if lng is None and lat is None:
                print(f"  ✅ PASS")
                passed += 1
            else:
                print(f"  ❌ FAIL - Should have returned None but got values")
                bugs_found.append(f"BUG: Regex matched invalid format: {url}")
                failed += 1
        else:
            if lng is None or lat is None:
                print(f"  ❌ FAIL - Valid URL not matched")
                bugs_found.append(f"BUG: Regex missed valid URL: {url}")
                failed += 1
            elif abs(lng - expected_lng) < 0.0001 and abs(lat - expected_lat) < 0.0001:
                print(f"  ✅ PASS")
                passed += 1
            else:
                print(f"  ❌ FAIL - Wrong coordinates extracted")
                bugs_found.append(f"BUG: Wrong coords for URL: {url}")
                failed += 1

    print(f"\n{'=' * 80}")
    print(f"\n📊 Results: {passed} passed, {failed} failed")

    return bugs_found


def test_coordinate_swap_bugs():
    """Test for coordinate swap bugs (lat/lng reversed)"""

    print("\n\n🔄 Testing Coordinate Swap Bugs\n")
    print("=" * 80)

    # Known location coordinates to verify lat/lng order
    test_cases = [
        # (url, expected_lng, expected_lat, location_name)
        ("https://www.google.com/maps/@-26.108204,28.0527061,17z", 28.0527061, -26.108204, "Sandton, SA (negative lat, positive lng)"),
        ("https://www.google.com/maps/@40.7128,-74.0060,17z", -74.0060, 40.7128, "NYC (positive lat, negative lng)"),
        ("https://www.google.com/maps/@-33.8688,151.2093,17z", 151.2093, -33.8688, "Sydney (negative lat, large positive lng)"),
        ("https://www.google.com/maps/@51.5074,-0.1278,17z", -0.1278, 51.5074, "London (positive lat, small negative lng)"),
        ("https://www.google.com/maps/@35.6762,139.6503,17z", 139.6503, 35.6762, "Tokyo (both positive, lng > 90)"),

        # Direct coordinate tests
        ("-26.108204,28.0527061", 28.0527061, -26.108204, "Direct coords: negative lat, positive lng"),
        ("40.7128,-74.0060", -74.0060, 40.7128, "Direct coords: positive lat, negative lng"),

        # Query format
        ("https://www.google.com/maps?q=-26.108204,28.0527061", 28.0527061, -26.108204, "Query format: Sandton"),
        ("https://www.google.com/maps?q=40.7128,-74.0060", -74.0060, 40.7128, "Query format: NYC"),
    ]

    bugs_found = []
    passed = 0
    failed = 0

    for url, expected_lng, expected_lat, location_name in test_cases:
        print(f"\nTest: {location_name}")
        print(f"  Expected: lng={expected_lng}, lat={expected_lat}")

        lng, lat = extract_coordinates_from_url(url)

        print(f"  Actual:   lng={lng}, lat={lat}")

        if lng is None or lat is None:
            print(f"  ❌ FAIL - Could not extract coordinates")
            bugs_found.append(f"BUG: Failed to extract from {location_name}")
            failed += 1
        elif abs(lng - expected_lng) < 0.0001 and abs(lat - expected_lat) < 0.0001:
            print(f"  ✅ PASS")
            passed += 1
        else:
            print(f"  ❌ FAIL - Coordinates swapped or wrong")
            if abs(lng - expected_lat) < 0.0001 and abs(lat - expected_lng) < 0.0001:
                print(f"  🚨 CRITICAL: Lat/Lng are SWAPPED!")
                bugs_found.append(f"CRITICAL BUG: Lat/Lng swapped for {location_name}")
            else:
                bugs_found.append(f"BUG: Wrong coordinates for {location_name}")
            failed += 1

    print(f"\n{'=' * 80}")
    print(f"\n📊 Results: {passed} passed, {failed} failed")

    return bugs_found


def test_nan_propagation():
    """Test for NaN value propagation bugs"""

    print("\n\n⚠️  Testing NaN Propagation Bugs\n")
    print("=" * 80)

    # Create test DataFrame with mixed data
    test_data = {
        'Name': ['Location1', 'Location2', 'Location3', 'Location4'],
        'Region': ['RegionA', 'RegionB', 'RegionC', 'RegionD'],
        'Map link': [
            'https://www.google.com/maps/@-26.108204,28.0527061,17z',
            '',  # Empty string
            np.nan,  # NaN value
            'https://www.google.com/maps/@40.7128,-74.0060,17z'
        ]
    }

    df = pd.DataFrame(test_data)

    print(f"Test DataFrame created with {len(df)} rows")
    print(f"  Row 0: Valid URL")
    print(f"  Row 1: Empty string")
    print(f"  Row 2: NaN value")
    print(f"  Row 3: Valid URL")

    bugs_found = []

    # Simulate processing logic from process_excel_file
    df['LONG'] = None
    df['LATTs'] = None

    for idx, row in df.iterrows():
        map_link = row['Map link']

        # Skip empty/NaN (same logic as in code)
        if pd.isna(map_link) or str(map_link).strip() == '':
            continue

        lng, lat = extract_coordinates_from_url(str(map_link))

        if lng is not None and lat is not None:
            df.at[idx, 'LONG'] = lng
            df.at[idx, 'LATTs'] = lat

    # Check results
    print(f"\nResults after processing:")
    for idx, row in df.iterrows():
        lng = row['LONG']
        lat = row['LATTs']
        map_link = row['Map link']

        print(f"\n  Row {idx}: {row['Name']}")
        print(f"    Map link: {map_link}")
        print(f"    LONG: {lng}, LATTs: {lat}")
        print(f"    Type LONG: {type(lng)}, Type LATTs: {type(lat)}")

        # Check for issues
        if idx in [1, 2]:  # Empty or NaN rows
            if lng is not None or lat is not None:
                print(f"    ❌ FAIL - Should have None for empty/NaN input")
                bugs_found.append(f"BUG: NaN/empty not handled correctly at row {idx}")
            else:
                print(f"    ✅ PASS - Correctly left as None")
        else:  # Valid rows
            if lng is None or lat is None:
                print(f"    ❌ FAIL - Should have extracted coordinates")
                bugs_found.append(f"BUG: Failed to extract valid coordinates at row {idx}")
            else:
                print(f"    ✅ PASS - Coordinates extracted")

    # Check for data type issues
    print(f"\n\nChecking data types in DataFrame columns:")
    print(f"  LONG dtype: {df['LONG'].dtype}")
    print(f"  LATTs dtype: {df['LATTs'].dtype}")

    # Check if any strings crept in
    for idx, val in df['LONG'].items():
        if val is not None and isinstance(val, str):
            print(f"  ❌ FAIL - LONG at row {idx} is string: {val}")
            bugs_found.append(f"BUG: String coordinate at row {idx} LONG column")

    for idx, val in df['LATTs'].items():
        if val is not None and isinstance(val, str):
            print(f"  ❌ FAIL - LATTs at row {idx} is string: {val}")
            bugs_found.append(f"BUG: String coordinate at row {idx} LATTs column")

    print(f"\n{'=' * 80}")

    return bugs_found


def test_data_type_bugs():
    """Test for data type bugs (string coords, float errors)"""

    print("\n\n🔢 Testing Data Type Bugs\n")
    print("=" * 80)

    test_cases = [
        # Test various string formats
        ("  -26.108204  ,  28.0527061  ", "String with spaces"),
        ("-26.108204,28.0527061", "String without spaces"),
        ("https://www.google.com/maps/@-26.108204,28.0527061,17z", "URL string"),

        # Test potential float precision issues
        ("https://www.google.com/maps/@-26.10820412345678901234,28.05270612345678901234,17z", "Very high precision"),

        # Test edge cases
        ("https://www.google.com/maps/@-0.0,0.0,17z", "Zero values"),
        ("https://www.google.com/maps/@-90.0,180.0,17z", "Max valid values"),
    ]

    bugs_found = []
    passed = 0
    failed = 0

    for url, description in test_cases:
        print(f"\nTest: {description}")
        print(f"  Input: {url}")

        lng, lat = extract_coordinates_from_url(url)

        print(f"  Result: lng={lng}, lat={lat}")
        print(f"  Types: lng={type(lng)}, lat={type(lat)}")

        # Check if result types are correct
        if lng is not None:
            if not isinstance(lng, (float, int)):
                print(f"  ❌ FAIL - lng is not numeric: {type(lng)}")
                bugs_found.append(f"BUG: lng returned as {type(lng)} instead of float")
                failed += 1
            elif isinstance(lng, str):
                print(f"  ❌ FAIL - lng is string: '{lng}'")
                bugs_found.append(f"BUG: lng returned as string")
                failed += 1
            else:
                print(f"  ✅ PASS - lng type correct")
                passed += 1
        else:
            print(f"  ⚠️  lng is None")

        if lat is not None:
            if not isinstance(lat, (float, int)):
                print(f"  ❌ FAIL - lat is not numeric: {type(lat)}")
                bugs_found.append(f"BUG: lat returned as {type(lat)} instead of float")
                failed += 1
            elif isinstance(lat, str):
                print(f"  ❌ FAIL - lat is string: '{lat}'")
                bugs_found.append(f"BUG: lat returned as string")
                failed += 1
            else:
                print(f"  ✅ PASS - lat type correct")
                passed += 1
        else:
            print(f"  ⚠️  lat is None")

    print(f"\n{'=' * 80}")
    print(f"\n📊 Results: {passed} type checks passed, {failed} failed")

    return bugs_found


def test_url_resolution_timeout():
    """Test URL resolution and timeout handling"""

    print("\n\n⏱️  Testing URL Resolution and Timeout Bugs\n")
    print("=" * 80)

    test_cases = [
        # Valid shortened URLs
        ("https://goo.gl/maps/abc123", "Shortened goo.gl URL"),
        ("https://maps.app.goo.gl/abc123", "Shortened maps.app.goo.gl URL"),

        # Invalid shortened URLs
        ("https://goo.gl/invalid", "Invalid shortened URL"),

        # Regular URLs (should work without resolution)
        ("https://www.google.com/maps/@-26.108204,28.0527061,17z", "Regular URL (no resolution needed)"),
    ]

    bugs_found = []

    print(f"\nNote: This test may be slow due to network requests...")

    for url, description in test_cases:
        print(f"\nTest: {description}")
        print(f"  URL: {url}")

        try:
            import time
            start_time = time.time()

            lng, lat = extract_coordinates_from_url(url)

            elapsed = time.time() - start_time

            print(f"  Result: lng={lng}, lat={lat}")
            print(f"  Time: {elapsed:.2f}s")

            # Check for timeout issues
            if elapsed > 15:  # Should complete within 15 seconds with 10s timeout
                print(f"  ⚠️  WARNING - Request took longer than expected")
                bugs_found.append(f"WARNING: Slow URL resolution for {description}")

            if "Regular URL" in description and elapsed > 1:
                print(f"  ⚠️  WARNING - Regular URL should not need resolution")
                bugs_found.append(f"BUG: Regular URL triggered resolution logic")

        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            bugs_found.append(f"BUG: Exception during URL processing: {description} - {str(e)}")

    print(f"\n{'=' * 80}")

    return bugs_found


if __name__ == "__main__":
    print("\n" + "🐛 " * 30)
    print("\n  CRITICAL BUG DETECTION TEST SUITE")
    print("\n" + "🐛 " * 30)

    all_bugs = []

    # Run all tests
    all_bugs.extend(test_regex_pattern_bugs())
    all_bugs.extend(test_coordinate_swap_bugs())
    all_bugs.extend(test_nan_propagation())
    all_bugs.extend(test_data_type_bugs())
    all_bugs.extend(test_url_resolution_timeout())

    # Print summary
    print("\n\n" + "=" * 80)
    print("\n📋 CRITICAL BUGS FOUND\n")
    print("=" * 80)

    if all_bugs:
        print(f"\n🚨 Found {len(all_bugs)} potential bugs:\n")
        for i, bug in enumerate(all_bugs, 1):
            print(f"{i}. {bug}")
        exit(1)
    else:
        print("\n✅ No critical bugs detected!")
        exit(0)
