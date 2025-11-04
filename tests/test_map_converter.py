"""
Unit tests for map_converter.py
"""

import pytest
import sys
import os

# Add parent directory to path to import map_converter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from map_converter import extract_coordinates_from_url


class TestExtractCoordinates:
    """Test coordinate extraction from various URL formats."""
    
    def test_google_maps_place_format(self):
        """Test Google Maps place URL with @ format."""
        url = "https://www.google.com/maps/place/Sandton+City/@-26.108204,28.0527061,17z"
        lng, lat = extract_coordinates_from_url(url)
        assert lng == pytest.approx(28.0527061, rel=1e-6)
        assert lat == pytest.approx(-26.108204, rel=1e-6)
    
    def test_google_maps_query_format(self):
        """Test Google Maps query URL with q= format."""
        url = "https://www.google.com/maps?q=-26.108204,28.0527061"
        lng, lat = extract_coordinates_from_url(url)
        assert lng == pytest.approx(28.0527061, rel=1e-6)
        assert lat == pytest.approx(-26.108204, rel=1e-6)
    
    def test_maps_google_query_format(self):
        """Test maps.google.com URL format."""
        url = "https://maps.google.com/?q=-26.108204,28.0527061"
        lng, lat = extract_coordinates_from_url(url)
        assert lng == pytest.approx(28.0527061, rel=1e-6)
        assert lat == pytest.approx(-26.108204, rel=1e-6)
    
    def test_direct_coordinates(self):
        """Test direct coordinate pairs."""
        url = "-26.108204,28.0527061"
        lng, lat = extract_coordinates_from_url(url)
        assert lng == pytest.approx(28.0527061, rel=1e-6)
        assert lat == pytest.approx(-26.108204, rel=1e-6)
    
    def test_coordinates_with_spaces(self):
        """Test coordinate pairs with spaces."""
        url = "-26.108204, 28.0527061"
        lng, lat = extract_coordinates_from_url(url)
        assert lng == pytest.approx(28.0527061, rel=1e-6)
        assert lat == pytest.approx(-26.108204, rel=1e-6)
    
    def test_positive_coordinates(self):
        """Test positive coordinate values."""
        url = "https://www.google.com/maps/@40.7128,74.0060,15z"
        lng, lat = extract_coordinates_from_url(url)
        assert lng == pytest.approx(74.0060, rel=1e-6)
        assert lat == pytest.approx(40.7128, rel=1e-6)
    
    def test_invalid_url(self):
        """Test invalid URL returns None."""
        url = "https://www.example.com"
        lng, lat = extract_coordinates_from_url(url)
        assert lng is None
        assert lat is None
    
    def test_empty_string(self):
        """Test empty string returns None."""
        url = ""
        lng, lat = extract_coordinates_from_url(url)
        assert lng is None
        assert lat is None
    
    def test_none_value(self):
        """Test None value returns None."""
        url = None
        lng, lat = extract_coordinates_from_url(url)
        assert lng is None
        assert lat is None
    
    def test_non_string_input(self):
        """Test non-string input returns None."""
        url = 12345
        lng, lat = extract_coordinates_from_url(url)
        assert lng is None
        assert lat is None
    
    def test_malformed_coordinates(self):
        """Test malformed coordinates."""
        url = "https://www.google.com/maps/@abc,def"
        lng, lat = extract_coordinates_from_url(url)
        assert lng is None
        assert lat is None
    
    def test_place_url_with_coordinates(self):
        """Test place URL with embedded coordinates."""
        url = "https://www.google.com/maps/place/Test+Location/@-33.8688,151.2093,14z"
        lng, lat = extract_coordinates_from_url(url)
        assert lng == pytest.approx(151.2093, rel=1e-6)
        assert lat == pytest.approx(-33.8688, rel=1e-6)


class TestRealWorldExamples:
    """Test with real-world location examples."""
    
    def test_sandton_city(self):
        """Test Sandton City coordinates extraction."""
        url = "https://www.google.com/maps/place/Sandton+City/@-26.108204,28.0527061,17z"
        lng, lat = extract_coordinates_from_url(url)
        # Verify it's in Johannesburg, South Africa region
        assert -27 < lat < -25  # Johannesburg latitude range
        assert 27 < lng < 29    # Johannesburg longitude range
    
    def test_multiple_zoom_levels(self):
        """Test URLs with different zoom levels."""
        urls = [
            "https://www.google.com/maps/@-26.108204,28.0527061,10z",
            "https://www.google.com/maps/@-26.108204,28.0527061,15z",
            "https://www.google.com/maps/@-26.108204,28.0527061,20z",
        ]
        for url in urls:
            lng, lat = extract_coordinates_from_url(url)
            assert lng == pytest.approx(28.0527061, rel=1e-6)
            assert lat == pytest.approx(-26.108204, rel=1e-6)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
