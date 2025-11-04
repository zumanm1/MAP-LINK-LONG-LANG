#!/usr/bin/env python3
"""
Bug Reproduction Test Cases
Demonstrates each critical bug with minimal test case
"""

from map_converter import extract_coordinates_from_url

print("=" * 80)
print("BUG REPRODUCTION TEST CASES")
print("=" * 80)

print("\n" + "=" * 80)
print("BUG #1: Pattern 4 matches /search/ URLs (false positive)")
print("=" * 80)
url = "https://www.google.com/maps/search/26.108204,28.0527061/"
lng, lat = extract_coordinates_from_url(url)
print(f"URL: {url}")
print(f"Expected: None, None")
print(f"Actual: {lng}, {lat}")
print(f"Status: {'FAIL - False positive' if lng is not None else 'PASS'}")

print("\n" + "=" * 80)
print("BUG #2: Pattern 4 matches /dir/ URLs (false positive)")
print("=" * 80)
url = "https://www.google.com/maps/dir/40.7128,-74.0060/41.8781,-87.6298/"
lng, lat = extract_coordinates_from_url(url)
print(f"URL: {url}")
print(f"Expected: None, None (or reject multi-coord URLs)")
print(f"Actual: {lng}, {lat}")
print(f"Status: {'FAIL - False positive' if lng is not None else 'PASS'}")

print("\n" + "=" * 80)
print("BUG #3: Invalid latitude -91.0 accepted (out of range)")
print("=" * 80)
url = "https://www.google.com/maps/@-91.0,28.0,17z"
lng, lat = extract_coordinates_from_url(url)
print(f"URL: {url}")
print(f"Expected: None, None (latitude must be -90 to 90)")
print(f"Actual: lng={lng}, lat={lat}")
if lat is not None and abs(lat) > 90:
    print(f"Status: FAIL - Invalid latitude {lat} accepted")
else:
    print(f"Status: PASS")

print("\n" + "=" * 80)
print("BUG #4: Invalid latitude 91.0 accepted (out of range)")
print("=" * 80)
url = "https://www.google.com/maps/@91.0,28.0,17z"
lng, lat = extract_coordinates_from_url(url)
print(f"URL: {url}")
print(f"Expected: None, None (latitude must be -90 to 90)")
print(f"Actual: lng={lng}, lat={lat}")
if lat is not None and abs(lat) > 90:
    print(f"Status: FAIL - Invalid latitude {lat} accepted")
else:
    print(f"Status: PASS")

print("\n" + "=" * 80)
print("BUG #5: Invalid longitude 181.0 accepted (out of range)")
print("=" * 80)
url = "https://www.google.com/maps/@-26.0,181.0,17z"
lng, lat = extract_coordinates_from_url(url)
print(f"URL: {url}")
print(f"Expected: None, None (longitude must be -180 to 180)")
print(f"Actual: lng={lng}, lat={lat}")
if lng is not None and abs(lng) > 180:
    print(f"Status: FAIL - Invalid longitude {lng} accepted")
else:
    print(f"Status: PASS")

print("\n" + "=" * 80)
print("BUG #6: Invalid longitude -181.0 accepted (out of range)")
print("=" * 80)
url = "https://www.google.com/maps/@-26.0,-181.0,17z"
lng, lat = extract_coordinates_from_url(url)
print(f"URL: {url}")
print(f"Expected: None, None (longitude must be -180 to 180)")
print(f"Actual: lng={lng}, lat={lat}")
if lng is not None and abs(lng) > 180:
    print(f"Status: FAIL - Invalid longitude {lng} accepted")
else:
    print(f"Status: PASS")

print("\n" + "=" * 80)
print("BUG #7: Extreme invalid coordinates 200.0,300.0 accepted")
print("=" * 80)
url = "https://www.google.com/maps/@200.0,300.0,17z"
lng, lat = extract_coordinates_from_url(url)
print(f"URL: {url}")
print(f"Expected: None, None (both way out of Earth bounds)")
print(f"Actual: lng={lng}, lat={lat}")
if (lat is not None and abs(lat) > 90) or (lng is not None and abs(lng) > 180):
    print(f"Status: FAIL - Invalid coordinates accepted")
else:
    print(f"Status: PASS")

print("\n" + "=" * 80)
print("BUG #8: Unicode minus sign causes wrong latitude sign")
print("=" * 80)
url = "https://www.google.com/maps/@−26.108204,28.0527061"  # Unicode minus U+2212
lng, lat = extract_coordinates_from_url(url)
print(f"URL: {url}")
print(f"Expected: lng=28.0527061, lat=-26.108204")
print(f"Actual: lng={lng}, lat={lat}")
if lat is not None and lat > 0:
    print(f"Status: FAIL - Latitude sign wrong (Unicode minus not recognized)")
else:
    print(f"Status: PASS or correctly rejected")

print("\n" + "=" * 80)
print("BUG #9: Multiple decimal points partially parsed")
print("=" * 80)
url = "https://www.google.com/maps/@-26.108.204,28.052.706"
lng, lat = extract_coordinates_from_url(url)
print(f"URL: {url}")
print(f"Expected: None, None (malformed coordinates)")
print(f"Actual: lng={lng}, lat={lat}")
if lng is not None or lat is not None:
    print(f"Status: FAIL - Malformed coordinates partially parsed")
else:
    print(f"Status: PASS")

print("\n" + "=" * 80)
print("BUG #10: Extreme values -999999.999999 accepted")
print("=" * 80)
url = "https://www.google.com/maps/@-999999.999999,999999.999999"
lng, lat = extract_coordinates_from_url(url)
print(f"URL: {url}")
print(f"Expected: None, None (far outside valid Earth coordinates)")
print(f"Actual: lng={lng}, lat={lat}")
if lng is not None or lat is not None:
    print(f"Status: FAIL - Extreme invalid values accepted")
else:
    print(f"Status: PASS")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("\nCritical bugs found:")
print("1. Pattern 4 matches /search/ URLs - False positive")
print("2. Pattern 4 matches /dir/ URLs - False positive")
print("3-7. No coordinate range validation - Accepts invalid lat/lng")
print("8. Unicode minus sign not handled - Wrong sign")
print("9. Multiple decimal points partially parsed - Data corruption")
print("10. Extreme values accepted - No bounds checking")
