#!/usr/bin/env python3
"""
Test Bug #1 Fix: Coordinate Logic
Tests the fixed coordinate extraction logic for edge cases
"""

from map_converter import extract_coordinates_from_url

def test_coordinate_logic():
    """Test all coordinate extraction edge cases"""

    print("🧪 Testing Bug #1 Fix: Coordinate Logic\n")
    print("=" * 60)

    test_cases = [
        # (input, expected_lng, expected_lat, description)
        ("45.0, 85.0", 85.0, 45.0, "Both <= 90 (ambiguous)"),
        ("14.5, 120.0", 120.0, 14.5, "Only coord1 <= 90"),
        ("120.0, 14.5", 120.0, 14.5, "Only coord2 <= 90"),
        ("120.0, 150.0", 150.0, 120.0, "Both > 90 (CRITICAL FIX)"),
        ("95.0, 100.0", 100.0, 95.0, "Both > 90 (edge case)"),
        ("91.0, 179.0", 179.0, 91.0, "Both > 90 (max ranges)"),
        ("-26.108204, 28.052706", 28.052706, -26.108204, "Negative latitude"),
        ("40.7580, -73.9855", -73.9855, 40.7580, "Negative longitude"),
        ("-34.603722, 151.283333", 151.283333, -34.603722, "Sydney (both valid)"),
        ("141.347, -33.8678", 141.347, -33.8678, "Eastern longitude, negative lat"),
    ]

    passed = 0
    failed = 0

    for input_coords, expected_lng, expected_lat, description in test_cases:
        print(f"\nTest: {input_coords}")
        print(f"  Description: {description}")
        print(f"  Expected: lng={expected_lng}, lat={expected_lat}")

        lng, lat = extract_coordinates_from_url(input_coords)

        print(f"  Actual:   lng={lng}, lat={lat}")

        if lng == expected_lng and lat == expected_lat:
            print(f"  ✅ PASS")
            passed += 1
        else:
            print(f"  ❌ FAIL")
            failed += 1

    print("\n" + "=" * 60)
    print(f"\n📊 Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("✅ All tests passed! Bug #1 is FIXED!")
        return True
    else:
        print(f"❌ {failed} tests failed. Bug #1 NOT fully fixed.")
        return False

def test_google_maps_urls():
    """Test with real Google Maps URLs"""

    print("\n\n🌐 Testing Real Google Maps URLs\n")
    print("=" * 60)

    test_urls = [
        ("https://www.google.com/maps/@120.0,150.0,17z", 150.0, 120.0, "Eastern Pacific"),
        ("https://www.google.com/maps/@14.5,120.0,17z", 120.0, 14.5, "Philippines"),
        ("https://www.google.com/maps/@-26.108204,28.052706,17z", 28.052706, -26.108204, "South Africa"),
        ("https://www.google.com/maps?q=120.0,150.0", 150.0, 120.0, "Query format"),
    ]

    passed = 0
    failed = 0

    for url, expected_lng, expected_lat, description in test_urls:
        print(f"\nTest: {description}")
        print(f"  URL: {url}")
        print(f"  Expected: lng={expected_lng}, lat={expected_lat}")

        lng, lat = extract_coordinates_from_url(url)

        print(f"  Actual:   lng={lng}, lat={lat}")

        if lng == expected_lng and lat == expected_lat:
            print(f"  ✅ PASS")
            passed += 1
        else:
            print(f"  ❌ FAIL")
            failed += 1

    print("\n" + "=" * 60)
    print(f"\n📊 Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("✅ All URL tests passed!")
        return True
    else:
        print(f"❌ {failed} URL tests failed.")
        return False

if __name__ == "__main__":
    result1 = test_coordinate_logic()
    result2 = test_google_maps_urls()

    if result1 and result2:
        print("\n\n🎉 SUCCESS: Bug #1 completely fixed!")
        exit(0)
    else:
        print("\n\n⚠️  FAILURE: Bug #1 not fully fixed. Review output above.")
        exit(1)
