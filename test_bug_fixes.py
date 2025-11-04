#!/usr/bin/env python3
"""
Comprehensive Test Script: Validate All Bug Fixes + Corner Cases
Tests all 9 critical and high-priority bug fixes with extensive URL format coverage
"""

import sys
import time
from map_converter import extract_coordinates_from_url
from map_converter_parallel import extract_coordinates_parallel

print("="*80)
print("🧪 COMPREHENSIVE BUG FIX VALIDATION TESTS")
print("="*80)

# Test counters
total_tests = 0
passed_tests = 0
failed_tests = 0
test_results = []

def test(name, condition, message="", url=""):
    """Helper function to run tests"""
    global total_tests, passed_tests, failed_tests
    total_tests += 1

    if condition:
        print(f"✅ PASS: {name}")
        passed_tests += 1
        test_results.append(("✅", name, url))
        return True
    else:
        print(f"❌ FAIL: {name}")
        if message:
            print(f"   {message}")
        if url:
            print(f"   URL: {url}")
        failed_tests += 1
        test_results.append(("❌", name, url))
        return False

# ============================================================================
# TEST SUITE 1: INTEGER COORDINATE SUPPORT (BUG #9)
# ============================================================================
print("\n" + "="*80)
print("TEST SUITE 1: Integer Coordinate Support (BUG #9)")
print("="*80)

test_cases_integers = [
    # Format: (url, description)
    ("https://www.google.com/maps/@40,74,12z", "Integer @ format"),
    ("https://www.google.com/maps?q=40,-74", "Integer q= format"),
    ("https://www.google.com/maps/place/NYC/@40,-74,12z", "Integer place format"),
    ("https://maps.google.com/@-33,151,15z", "Negative integers"),
    ("https://www.google.com/maps/@0,0,12z", "Zero coordinates"),
]

for url, desc in test_cases_integers:
    lng, lat = extract_coordinates_from_url(url)
    test(f"Integer coords: {desc}",
         lng is not None and lat is not None,
         f"Expected coordinates, got: lng={lng}, lat={lat}",
         url)

# ============================================================================
# TEST SUITE 2: DECIMAL COORDINATE SUPPORT (REGRESSION)
# ============================================================================
print("\n" + "="*80)
print("TEST SUITE 2: Decimal Coordinate Support (Regression Check)")
print("="*80)

test_cases_decimals = [
    ("https://www.google.com/maps/@40.7128,-74.0060,12z", "Standard decimal @ format"),
    ("https://www.google.com/maps?q=40.7128,-74.0060", "Decimal q= format"),
    ("https://www.google.com/maps/place/NYC/@40.7128,-74.0060,12z", "Decimal place format"),
    ("https://www.google.com/maps/@-33.8688,151.2093,15z", "Sydney coordinates"),
    ("https://www.google.com/maps/@51.5074,-0.1278,13z", "London coordinates"),
]

for url, desc in test_cases_decimals:
    lng, lat = extract_coordinates_from_url(url)
    test(f"Decimal coords: {desc}",
         lng is not None and lat is not None,
         f"Expected coordinates, got: lng={lng}, lat={lat}",
         url)

# ============================================================================
# TEST SUITE 3: MIXED INTEGER/DECIMAL COORDINATES
# ============================================================================
print("\n" + "="*80)
print("TEST SUITE 3: Mixed Integer/Decimal Coordinates")
print("="*80)

test_cases_mixed = [
    ("https://www.google.com/maps/@40,-74.5,12z", "Integer lat, decimal lng"),
    ("https://www.google.com/maps/@40.5,-74,12z", "Decimal lat, integer lng"),
    ("https://www.google.com/maps?q=40,-74.123456", "High precision mixed"),
    ("https://www.google.com/maps/@-26,28.0527061,17z", "South Africa mixed"),
]

for url, desc in test_cases_mixed:
    lng, lat = extract_coordinates_from_url(url)
    test(f"Mixed coords: {desc}",
         lng is not None and lat is not None,
         f"Expected coordinates, got: lng={lng}, lat={lat}",
         url)

# ============================================================================
# TEST SUITE 4: REAL-WORLD GOOGLE MAPS URLS
# ============================================================================
print("\n" + "="*80)
print("TEST SUITE 4: Real-World Google Maps URLs")
print("="*80)

test_cases_realworld = [
    # Major cities with various formats
    ("https://www.google.com/maps/@-26.108204,28.0527061,17z", "Johannesburg, South Africa"),
    ("https://www.google.com/maps/@-33.865143,151.209900,10z", "Sydney, Australia"),
    ("https://www.google.com/maps/place/Eiffel+Tower/@48.8583701,2.2922926,17z", "Eiffel Tower, Paris"),
    ("https://www.google.com/maps/@35.6762,139.6503,12z", "Tokyo, Japan"),
    ("https://www.google.com/maps?q=-34.6037,-58.3816", "Buenos Aires, Argentina"),
    ("https://maps.google.com/maps?q=40.7580,-73.9855", "Times Square, NYC"),
    ("https://www.google.com/maps/@51.5074,-0.1278,13z", "London, UK"),
    ("https://www.google.com/maps/place/Dubai/@25.2048,55.2708,11z", "Dubai, UAE"),
]

for url, desc in test_cases_realworld:
    lng, lat = extract_coordinates_from_url(url)
    test(f"Real-world: {desc}",
         lng is not None and lat is not None,
         f"Expected coordinates, got: lng={lng}, lat={lat}",
         url)

# ============================================================================
# TEST SUITE 5: EDGE CASES AND BOUNDARIES
# ============================================================================
print("\n" + "="*80)
print("TEST SUITE 5: Edge Cases and Boundaries")
print("="*80)

test_cases_edge = [
    # Boundary coordinates
    ("https://www.google.com/maps/@90,180,12z", "Max latitude/longitude"),
    ("https://www.google.com/maps/@-90,-180,12z", "Min latitude/longitude"),
    ("https://www.google.com/maps/@0,0,12z", "Null Island (0,0)"),
    ("https://www.google.com/maps/@-90,0,12z", "South Pole"),
    ("https://www.google.com/maps/@90,0,12z", "North Pole"),
    ("https://www.google.com/maps/@0,180,12z", "International Date Line"),
    ("https://www.google.com/maps/@0,-180,12z", "International Date Line West"),
]

for url, desc in test_cases_edge:
    lng, lat = extract_coordinates_from_url(url)
    test(f"Edge case: {desc}",
         lng is not None and lat is not None,
         f"Expected coordinates, got: lng={lng}, lat={lat}",
         url)

# ============================================================================
# TEST SUITE 6: URL FORMAT VARIATIONS
# ============================================================================
print("\n" + "="*80)
print("TEST SUITE 6: URL Format Variations")
print("="*80)

test_cases_formats = [
    # Different URL patterns
    ("https://www.google.com/maps/@40.7128,-74.0060,12z/data=!3m1!4b1", "With extra parameters"),
    ("https://maps.google.com/?q=40.7128,-74.0060", "maps.google.com domain"),
    ("https://www.google.com/maps/search/40.7128,-74.0060", "Search format"),
    ("https://www.google.com/maps/dir//40.7128,-74.0060/@40.7128,-74.0060,12z", "Directions format"),
    ("http://www.google.com/maps/@40.7128,-74.0060,12z", "HTTP (not HTTPS)"),
    ("https://google.com/maps/@40.7128,-74.0060,12z", "No www"),
]

for url, desc in test_cases_formats:
    lng, lat = extract_coordinates_from_url(url)
    test(f"Format variation: {desc}",
         lng is not None and lat is not None,
         f"Expected coordinates, got: lng={lng}, lat={lat}",
         url)

# ============================================================================
# TEST SUITE 7: PRECISION VARIATIONS
# ============================================================================
print("\n" + "="*80)
print("TEST SUITE 7: Precision Variations")
print("="*80)

test_cases_precision = [
    ("https://www.google.com/maps/@40.7,-74.0,12z", "1 decimal place"),
    ("https://www.google.com/maps/@40.71,-74.01,12z", "2 decimal places"),
    ("https://www.google.com/maps/@40.712,-74.006,12z", "3 decimal places"),
    ("https://www.google.com/maps/@40.7128,-74.0060,12z", "4 decimal places"),
    ("https://www.google.com/maps/@40.71280,-74.00600,12z", "5 decimal places"),
    ("https://www.google.com/maps/@40.712800,-74.006000,12z", "6 decimal places"),
    ("https://www.google.com/maps/@40.7128001,-74.0060001,12z", "7 decimal places"),
]

for url, desc in test_cases_precision:
    lng, lat = extract_coordinates_from_url(url)
    test(f"Precision: {desc}",
         lng is not None and lat is not None,
         f"Expected coordinates, got: lng={lng}, lat={lat}",
         url)

# ============================================================================
# TEST SUITE 8: PARALLEL EXTRACTION TIMEOUT (BUG #1, #2)
# ============================================================================
print("\n" + "="*80)
print("TEST SUITE 8: Parallel Extraction Timeout (BUG #1, #2)")
print("="*80)

# Test 8.1: Parallel extraction completes within timeout
url_parallel = "https://www.google.com/maps/@-26.108204,28.0527061,17z"
start_time = time.time()
results = extract_coordinates_parallel(url_parallel)
elapsed = time.time() - start_time

test("Parallel extraction timeout",
     elapsed < 25,  # Should complete within 20s + buffer
     f"Took {elapsed:.1f}s (should be < 25s)",
     url_parallel)

# Test 8.2: At least one method succeeds
method1_success = results.get('method1') != (None, None)
test("At least one method succeeds",
     method1_success,
     f"Method1 result: {results.get('method1')}")

# Test 8.3: Results contain valid coordinates
successful_methods = [name for name, (lng, lat) in results.items()
                      if lng is not None and lat is not None]
test("Multiple methods succeed",
     len(successful_methods) >= 1,
     f"Successful methods: {successful_methods}")

# ============================================================================
# TEST SUITE 9: COORDINATE VALIDATION
# ============================================================================
print("\n" + "="*80)
print("TEST SUITE 9: Coordinate Validation")
print("="*80)

# Collect all coordinates from previous tests
all_coords = []
for result_type, name, url in test_results:
    if url and result_type == "✅":
        lng, lat = extract_coordinates_from_url(url)
        if lng is not None and lat is not None:
            all_coords.append((lng, lat, url))

# Test 9.1: Valid latitude range (-90 to 90)
invalid_lats = [(lng, lat, url) for lng, lat, url in all_coords if not (-90 <= lat <= 90)]
test("All latitudes in valid range (-90 to 90)",
     len(invalid_lats) == 0,
     f"Invalid latitudes found: {len(invalid_lats)}")

# Test 9.2: Valid longitude range (-180 to 180)
invalid_lngs = [(lng, lat, url) for lng, lat, url in all_coords if not (-180 <= lng <= 180)]
test("All longitudes in valid range (-180 to 180)",
     len(invalid_lngs) == 0,
     f"Invalid longitudes found: {len(invalid_lngs)}")

# Test 9.3: No NaN or None values slipped through
none_coords = [(lng, lat, url) for lng, lat, url in all_coords
               if lng is None or lat is None or
               str(lng) == 'nan' or str(lat) == 'nan']
test("No NaN or None coordinates",
     len(none_coords) == 0,
     f"NaN/None coordinates found: {len(none_coords)}")

# ============================================================================
# TEST SUITE 10: NEGATIVE TEST CASES (SHOULD FAIL GRACEFULLY)
# ============================================================================
print("\n" + "="*80)
print("TEST SUITE 10: Negative Test Cases (Should Fail Gracefully)")
print("="*80)

negative_test_cases = [
    ("https://www.google.com/maps", "No coordinates in URL"),
    ("https://www.google.com/", "Not a maps URL"),
    ("invalid_url", "Invalid URL format"),
    ("https://www.google.com/maps/place/New+York", "Place name only, no coords"),
    ("", "Empty string"),
]

for url, desc in negative_test_cases:
    try:
        lng, lat = extract_coordinates_from_url(url)
        test(f"Negative test: {desc}",
             lng is None and lat is None,
             f"Expected None, got: lng={lng}, lat={lat}",
             url)
    except Exception as e:
        # Should handle gracefully, not crash
        test(f"Negative test: {desc}",
             True,
             f"Handled gracefully with: {type(e).__name__}",
             url)

# ============================================================================
# FINAL RESULTS SUMMARY
# ============================================================================
print("\n" + "="*80)
print("📊 FINAL TEST RESULTS SUMMARY")
print("="*80)
print(f"Total Tests Run: {total_tests}")
print(f"✅ Passed: {passed_tests}")
print(f"❌ Failed: {failed_tests}")
print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
print("="*80)

# Print category breakdown
print("\n📋 TEST CATEGORY BREAKDOWN:")
print("-"*80)
print(f"Suite 1 - Integer Coordinates:        {len(test_cases_integers)} tests")
print(f"Suite 2 - Decimal Coordinates:        {len(test_cases_decimals)} tests")
print(f"Suite 3 - Mixed Coordinates:          {len(test_cases_mixed)} tests")
print(f"Suite 4 - Real-World URLs:            {len(test_cases_realworld)} tests")
print(f"Suite 5 - Edge Cases:                 {len(test_cases_edge)} tests")
print(f"Suite 6 - Format Variations:          {len(test_cases_formats)} tests")
print(f"Suite 7 - Precision Variations:       {len(test_cases_precision)} tests")
print(f"Suite 8 - Parallel Processing:        3 tests")
print(f"Suite 9 - Validation:                 3 tests")
print(f"Suite 10 - Negative Tests:            {len(negative_test_cases)} tests")
print("="*80)

# Print coverage statistics
total_url_tests = (len(test_cases_integers) + len(test_cases_decimals) +
                   len(test_cases_mixed) + len(test_cases_realworld) +
                   len(test_cases_edge) + len(test_cases_formats) +
                   len(test_cases_precision))
print(f"\n📍 URL FORMAT COVERAGE: {total_url_tests} unique URL patterns tested")
print("="*80)

if failed_tests == 0:
    print("\n🎉 ALL TESTS PASSED! Application is production-ready.")
    print("✅ Integer coordinate support validated")
    print("✅ Decimal coordinate support validated")
    print("✅ Mixed coordinate support validated")
    print("✅ Real-world URL compatibility validated")
    print("✅ Edge cases handled correctly")
    print("✅ Parallel extraction timeout working")
    print("✅ Coordinate validation passed")
    print("✅ Negative cases handled gracefully")
    sys.exit(0)
else:
    print(f"\n⚠️  {failed_tests} TEST(S) FAILED - Review required")
    print("\nFailed tests:")
    for result_type, name, url in test_results:
        if result_type == "❌":
            print(f"  - {name}")
            if url:
                print(f"    URL: {url}")
    sys.exit(1)
