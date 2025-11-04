#!/usr/bin/env python3
"""
Test Bug #3: Coordinate Validation
Tests that invalid coordinates are rejected with clear error messages.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path to import map_converter
sys.path.insert(0, str(Path(__file__).parent))

from map_converter import extract_coordinates_from_url


class TestCoordinateValidation:
    """Test coordinate validation for various edge cases."""

    def test_valid_coordinates_within_range(self):
        """Test that valid coordinates within range are accepted."""
        # South Africa coordinates
        url = "https://maps.google.com/?q=-26.1076,28.0567"
        lng, lat = extract_coordinates_from_url(url)

        assert lng is not None, "Longitude should not be None"
        assert lat is not None, "Latitude should not be None"
        assert -90 <= lat <= 90, f"Latitude {lat} should be within -90 to 90"
        assert -180 <= lng <= 180, f"Longitude {lng} should be within -180 to 180"
        assert lat == pytest.approx(-26.1076, abs=0.0001)
        assert lng == pytest.approx(28.0567, abs=0.0001)

    def test_boundary_values_positive(self):
        """Test that boundary values (90, 180) are accepted."""
        url = "https://maps.google.com/?q=90.0,180.0"
        lng, lat = extract_coordinates_from_url(url)

        assert lng is not None, "Longitude should not be None for boundary value"
        assert lat is not None, "Latitude should not be None for boundary value"
        assert lat == pytest.approx(90.0, abs=0.0001)
        assert lng == pytest.approx(180.0, abs=0.0001)

    def test_boundary_values_negative(self):
        """Test that boundary values (-90, -180) are accepted."""
        url = "https://maps.google.com/?q=-90.0,-180.0"
        lng, lat = extract_coordinates_from_url(url)

        assert lng is not None, "Longitude should not be None for negative boundary"
        assert lat is not None, "Latitude should not be None for negative boundary"
        assert lat == pytest.approx(-90.0, abs=0.0001)
        assert lng == pytest.approx(-180.0, abs=0.0001)

    def test_invalid_latitude_too_high(self):
        """Test that latitude > 90 is rejected."""
        url = "https://maps.google.com/?q=999.0,28.0"
        lng, lat = extract_coordinates_from_url(url)

        assert lng is None, "Longitude should be None for invalid latitude"
        assert lat is None, "Latitude > 90 should be rejected"

    def test_invalid_latitude_just_above_boundary(self):
        """Test that latitude just above 90 (90.001) is rejected."""
        url = "https://maps.google.com/?q=90.001,0.0"
        lng, lat = extract_coordinates_from_url(url)

        assert lng is None, "Longitude should be None for invalid latitude"
        assert lat is None, "Latitude > 90 (even by 0.001) should be rejected"

    def test_invalid_latitude_too_low(self):
        """Test that latitude < -90 is rejected."""
        url = "https://maps.google.com/?q=-200.0,28.0"
        lng, lat = extract_coordinates_from_url(url)

        assert lng is None, "Longitude should be None for invalid latitude"
        assert lat is None, "Latitude < -90 should be rejected"

    def test_invalid_longitude_too_high(self):
        """Test that longitude > 180 is rejected."""
        url = "https://maps.google.com/?q=-26.0,500.0"
        lng, lat = extract_coordinates_from_url(url)

        assert lng is None, "Longitude > 180 should be rejected"
        assert lat is None, "Latitude should be None for invalid longitude"

    def test_invalid_longitude_just_above_boundary(self):
        """Test that longitude just above 180 (180.001) is rejected."""
        url = "https://maps.google.com/?q=0.0,180.001"
        lng, lat = extract_coordinates_from_url(url)

        assert lng is None, "Longitude > 180 (even by 0.001) should be rejected"
        assert lat is None, "Latitude should be None for invalid longitude"

    def test_invalid_longitude_too_low(self):
        """Test that longitude < -180 is rejected."""
        url = "https://maps.google.com/?q=-26.0,-200.0"
        lng, lat = extract_coordinates_from_url(url)

        assert lng is None, "Longitude < -180 should be rejected"
        assert lat is None, "Latitude should be None for invalid longitude"

    def test_both_coordinates_invalid(self):
        """Test that both invalid coordinates are rejected."""
        url = "https://maps.google.com/?q=999.0,500.0"
        lng, lat = extract_coordinates_from_url(url)

        assert lng is None, "Both coordinates invalid should return None"
        assert lat is None, "Both coordinates invalid should return None"

    def test_zero_coordinates_valid(self):
        """Test that zero coordinates (0, 0) are accepted."""
        url = "https://maps.google.com/?q=0.0,0.0"
        lng, lat = extract_coordinates_from_url(url)

        assert lng is not None, "Longitude 0 should be valid"
        assert lat is not None, "Latitude 0 should be valid"
        assert lat == pytest.approx(0.0, abs=0.0001)
        assert lng == pytest.approx(0.0, abs=0.0001)

    def test_validation_with_different_url_formats(self):
        """Test validation works across all URL format patterns."""
        # Pattern 1: @lat,lng format
        url1 = "https://www.google.com/maps/@999.0,28.0,15z"
        lng1, lat1 = extract_coordinates_from_url(url1)
        assert lng1 is None and lat1 is None, "Invalid lat in pattern 1 should be rejected"

        # Pattern 2: q=lat,lng format
        url2 = "https://maps.google.com/?q=26.0,500.0"
        lng2, lat2 = extract_coordinates_from_url(url2)
        assert lng2 is None and lat2 is None, "Invalid lng in pattern 2 should be rejected"

        # Pattern 3: /place/.../@lat,lng format
        url3 = "https://www.google.com/maps/place/Test/@200.0,28.0,17z"
        lng3, lat3 = extract_coordinates_from_url(url3)
        assert lng3 is None and lat3 is None, "Invalid lat in pattern 3 should be rejected"


class TestCoordinateValidationEdgeCases:
    """Test edge cases for coordinate validation."""

    def test_equator_prime_meridian(self):
        """Test coordinates at equator and prime meridian (0, 0)."""
        url = "https://maps.google.com/?q=0.0,0.0"
        lng, lat = extract_coordinates_from_url(url)

        assert lng == 0.0
        assert lat == 0.0

    def test_north_pole(self):
        """Test coordinates at North Pole (90, 0)."""
        url = "https://maps.google.com/?q=90.0,0.0"
        lng, lat = extract_coordinates_from_url(url)

        assert lng == 0.0
        assert lat == 90.0

    def test_south_pole(self):
        """Test coordinates at South Pole (-90, 0)."""
        url = "https://maps.google.com/?q=-90.0,0.0"
        lng, lat = extract_coordinates_from_url(url)

        assert lng == 0.0
        assert lat == -90.0

    def test_international_date_line_west(self):
        """Test coordinates at International Date Line west (0, -180)."""
        url = "https://maps.google.com/?q=0.0,-180.0"
        lng, lat = extract_coordinates_from_url(url)

        assert lng == -180.0
        assert lat == 0.0

    def test_international_date_line_east(self):
        """Test coordinates at International Date Line east (0, 180)."""
        url = "https://maps.google.com/?q=0.0,180.0"
        lng, lat = extract_coordinates_from_url(url)

        assert lng == 180.0
        assert lat == 0.0

    def test_very_small_decimal_values(self):
        """Test coordinates with very small decimal values."""
        url = "https://maps.google.com/?q=0.000001,0.000001"
        lng, lat = extract_coordinates_from_url(url)

        assert lng is not None
        assert lat is not None
        assert abs(lat - 0.000001) < 0.0001
        assert abs(lng - 0.000001) < 0.0001


if __name__ == "__main__":
    print("=" * 70)
    print("TEST BUG #3: COORDINATE VALIDATION")
    print("=" * 70)
    print("\n🧪 Running coordinate validation tests...\n")

    # Run tests with verbose output
    exit_code = pytest.main([__file__, "-v", "--tb=short"])

    print("\n" + "=" * 70)
    if exit_code == 0:
        print("✅ ALL TESTS PASSED - Coordinate validation is working correctly")
    else:
        print("❌ TESTS FAILED - Coordinate validation needs fixes")
    print("=" * 70)

    sys.exit(exit_code)
