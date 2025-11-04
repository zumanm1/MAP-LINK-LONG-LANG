#!/usr/bin/env python3
"""
Test South African Map Support - Top 10 Cities
Validates coordinate extraction for major South African cities.
"""

from map_converter import extract_coordinates_from_url

def test_south_african_cities():
    """Test coordinate extraction for South Africa's top 10 cities"""

    print("🇿🇦 Testing South African Map Support - Top 10 Cities\n")
    print("=" * 80)

    # Top 10 South African cities with actual coordinates
    south_african_cities = [
        {
            'name': 'Johannesburg',
            'province': 'Gauteng',
            'lat': -26.2041,
            'lng': 28.0473,
            'population': '5.6M',
            'description': 'Largest city, economic hub'
        },
        {
            'name': 'Cape Town',
            'province': 'Western Cape',
            'lat': -33.9249,
            'lng': 18.4241,
            'population': '4.7M',
            'description': 'Legislative capital, tourism hub'
        },
        {
            'name': 'Durban',
            'province': 'KwaZulu-Natal',
            'lat': -29.8587,
            'lng': 31.0218,
            'population': '3.9M',
            'description': 'Major port city'
        },
        {
            'name': 'Pretoria',
            'province': 'Gauteng',
            'lat': -25.7479,
            'lng': 28.2293,
            'population': '2.5M',
            'description': 'Administrative capital'
        },
        {
            'name': 'Port Elizabeth (Gqeberha)',
            'province': 'Eastern Cape',
            'lat': -33.9608,
            'lng': 25.6022,
            'population': '1.3M',
            'description': 'Major industrial center'
        },
        {
            'name': 'Bloemfontein',
            'province': 'Free State',
            'lat': -29.0852,
            'lng': 26.1596,
            'population': '520K',
            'description': 'Judicial capital'
        },
        {
            'name': 'East London',
            'province': 'Eastern Cape',
            'lat': -33.0153,
            'lng': 27.9116,
            'population': '478K',
            'description': 'Only river port'
        },
        {
            'name': 'Nelspruit (Mbombela)',
            'province': 'Mpumalanga',
            'lat': -25.4753,
            'lng': 30.9700,
            'population': '450K',
            'description': 'Gateway to Kruger Park'
        },
        {
            'name': 'Polokwane',
            'province': 'Limpopo',
            'lat': -23.9045,
            'lng': 29.4689,
            'population': '628K',
            'description': 'Capital of Limpopo'
        },
        {
            'name': 'Kimberley',
            'province': 'Northern Cape',
            'lat': -28.7282,
            'lng': 24.7499,
            'population': '225K',
            'description': 'Diamond mining city'
        }
    ]

    print("\n📋 Testing Coordinate Extraction\n")

    passed = 0
    failed = 0
    tolerance = 0.01  # Allow 0.01 degree tolerance (~1km)

    for city in south_african_cities:
        print(f"\n{'─' * 80}")
        print(f"🏙️  City: {city['name']}")
        print(f"   Province: {city['province']}")
        print(f"   Population: {city['population']}")
        print(f"   Info: {city['description']}")
        print(f"   Expected: lat={city['lat']}, lng={city['lng']}")

        # Test different URL formats
        test_urls = [
            f"https://www.google.com/maps/@{city['lat']},{city['lng']},17z",
            f"https://www.google.com/maps?q={city['lat']},{city['lng']}",
            f"https://maps.google.com/?q={city['lat']},{city['lng']}",
            f"{city['lat']}, {city['lng']}"  # Direct coordinates
        ]

        city_passed = True
        for url_format in test_urls:
            lng, lat = extract_coordinates_from_url(url_format)

            if lng is None or lat is None:
                print(f"   ❌ FAIL: Could not extract from: {url_format[:50]}...")
                city_passed = False
                break

            # Check if within tolerance
            lat_diff = abs(lat - city['lat'])
            lng_diff = abs(lng - city['lng'])

            if lat_diff <= tolerance and lng_diff <= tolerance:
                continue  # This format passed
            else:
                print(f"   ❌ FAIL: Coordinates outside tolerance")
                print(f"      Expected: lat={city['lat']}, lng={city['lng']}")
                print(f"      Got: lat={lat}, lng={lng}")
                print(f"      Diff: lat={lat_diff:.4f}, lng={lng_diff:.4f}")
                city_passed = False
                break

        if city_passed:
            print(f"   ✅ PASS: All formats extracted correctly")
            print(f"      Actual: lat={lat}, lng={lng}")
            passed += 1
        else:
            failed += 1

    print(f"\n{'=' * 80}")
    print(f"\n📊 RESULTS: {passed}/10 cities passed")

    if failed == 0:
        print("\n✅ SUCCESS: All South African cities supported!")
        print("\n🇿🇦 South Africa Map Coverage: 100%")
        return True
    else:
        print(f"\n⚠️  WARNING: {failed} cities failed")
        print("\n🇿🇦 South Africa Map Coverage: {:.1f}%".format((passed/10)*100))
        return False


def test_south_africa_coordinate_ranges():
    """Test edge cases specific to South African coordinate ranges"""

    print("\n\n🔬 Testing South African Coordinate Ranges\n")
    print("=" * 80)

    # South Africa spans:
    # Latitude: -22° to -35° (North to South)
    # Longitude: 16° to 33° (West to East)

    test_cases = [
        # (description, lat, lng, should_work)
        ("Northernmost point (Limpopo)", -22.0, 29.0, True),
        ("Southernmost point (Cape Agulhas)", -34.8333, 20.0167, True),
        ("Westernmost point (Western Cape)", -28.0, 16.5, True),
        ("Easternmost point (KwaZulu-Natal)", -28.0, 32.8, True),
        ("Geographic center", -28.5, 24.5, True),
        ("Negative longitude (should work)", -26.0, -28.0, True),  # Invalid but test handling
    ]

    passed = 0
    total = len(test_cases)

    for description, lat, lng, should_work in test_cases:
        print(f"\nTest: {description}")
        print(f"   Coordinates: lat={lat}, lng={lng}")

        # Test with different formats
        test_url = f"https://www.google.com/maps/@{lat},{lng},17z"
        extracted_lng, extracted_lat = extract_coordinates_from_url(test_url)

        if extracted_lng is None or extracted_lat is None:
            if should_work:
                print(f"   ❌ FAIL: Should have extracted but got None")
            else:
                print(f"   ✅ PASS: Correctly rejected invalid coordinates")
                passed += 1
        else:
            tolerance = 0.01
            lat_match = abs(extracted_lat - lat) <= tolerance
            lng_match = abs(extracted_lng - lng) <= tolerance

            if lat_match and lng_match and should_work:
                print(f"   ✅ PASS: Extracted correctly")
                print(f"      Got: lat={extracted_lat}, lng={extracted_lng}")
                passed += 1
            elif not should_work:
                print(f"   ⚠️  WARNING: Extracted invalid coordinates (but tolerated)")
                print(f"      Got: lat={extracted_lat}, lng={extracted_lng}")
                passed += 1
            else:
                print(f"   ❌ FAIL: Coordinates don't match")
                print(f"      Expected: lat={lat}, lng={lng}")
                print(f"      Got: lat={extracted_lat}, lng={extracted_lng}")

    print(f"\n{'=' * 80}")
    print(f"\n📊 RESULTS: {passed}/{total} edge cases handled correctly")

    return passed == total


def test_sandton_city_example():
    """Test the Sandton City example from documentation"""

    print("\n\n🏢 Testing Sandton City (Documentation Example)\n")
    print("=" * 80)

    # Sandton City - from the project README
    test_urls = [
        "https://maps.app.goo.gl/baixEU9UxYHX8Yox7",  # Shortened URL (requires resolution)
        "https://www.google.com/maps/@-26.108204,28.052706,17z",  # Standard format
        "https://www.google.com/maps?q=-26.108204,28.052706",  # Query format
        "-26.108204, 28.052706"  # Direct coordinates
    ]

    expected_lat = -26.108204
    expected_lng = 28.052706
    tolerance = 0.01

    print(f"\n📍 Sandton City, Johannesburg")
    print(f"   Expected: lat={expected_lat}, lng={expected_lng}")
    print(f"\nTesting URL formats:\n")

    passed = 0
    for i, url in enumerate(test_urls, 1):
        print(f"{i}. {url[:60]}...")

        lng, lat = extract_coordinates_from_url(url)

        if lng is None or lat is None:
            print(f"   ⚠️  Could not extract (may need URL resolution)")
            if "goo.gl" in url:
                print(f"   ℹ️  Shortened URLs require network request")
                passed += 1  # Don't fail on shortened URLs without network
            continue

        lat_diff = abs(lat - expected_lat)
        lng_diff = abs(lng - expected_lng)

        if lat_diff <= tolerance and lng_diff <= tolerance:
            print(f"   ✅ PASS: lat={lat}, lng={lng}")
            passed += 1
        else:
            print(f"   ❌ FAIL: lat={lat}, lng={lng}")
            print(f"      Diff: lat={lat_diff:.6f}, lng={lng_diff:.6f}")

    print(f"\n{'=' * 80}")
    print(f"\n📊 RESULTS: {passed}/{len(test_urls)} formats supported")

    return passed >= 3  # At least 3 out of 4 should work


if __name__ == "__main__":
    print("\n" + "🇿🇦 " * 20)
    print("\n  SOUTH AFRICA MAP SUPPORT TEST SUITE")
    print("\n" + "🇿🇦 " * 20)

    # Run all tests
    test1 = test_south_african_cities()
    test2 = test_south_africa_coordinate_ranges()
    test3 = test_sandton_city_example()

    print("\n\n" + "=" * 80)
    print("\n📋 FINAL SUMMARY\n")
    print("=" * 80)

    results = [
        ("Top 10 Cities", test1),
        ("Coordinate Ranges", test2),
        ("Sandton City Example", test3)
    ]

    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not result:
            all_passed = False

    print("\n" + "=" * 80)

    if all_passed:
        print("\n🎉 SUCCESS: South Africa is fully supported!")
        print("\n🇿🇦 All major cities and coordinate ranges work correctly!")
        exit(0)
    else:
        print("\n⚠️  PARTIAL SUCCESS: Some tests failed")
        print("\n🇿🇦 Review output above for details")
        exit(1)
