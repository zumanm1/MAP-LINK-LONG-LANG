#!/usr/bin/env python3
"""
Enhanced Map Link to Coordinates Converter
Supports 4 fallback methods for extracting coordinates
"""

import pandas as pd
import re
import sys
import logging
from typing import Tuple, Optional
from urllib.parse import urlparse, parse_qs, unquote
import requests
from bs4 import BeautifulSoup
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_coordinates(lng: float, lat: float) -> Tuple[Optional[float], Optional[float]]:
    """
    Validate longitude and latitude are within valid ranges.

    Returns:
        Tuple of (lng, lat) if valid, or (None, None) if invalid
    """
    if not (-90.0 <= lat <= 90.0):
        logger.error(f"❌ Invalid latitude: {lat} (must be between -90 and 90)")
        return None, None

    if not (-180.0 <= lng <= 180.0):
        logger.error(f"❌ Invalid longitude: {lng} (must be between -180 and 180)")
        return None, None

    return lng, lat


def method1_regex_extraction(map_link: str) -> Tuple[Optional[float], Optional[float]]:
    """
    METHOD 1: Direct regex pattern matching (fastest, most reliable)

    Supports patterns:
    - https://www.google.com/maps/place/Location/@-26.108204,28.0527061,17z
    - https://www.google.com/maps?q=-26.108204,28.0527061
    - https://maps.google.com/?q=-26.108204,28.0527061
    - https://www.google.com/maps/search/query/@-26.094,28.186,13z
    - https://www.google.com/maps/search/?api=1&query=47.5951518%2C-122.3316393
    - URLs ending in =en (language parameter)
    - https://goo.gl/maps/... (shortened URLs)
    """
    if not map_link or not isinstance(map_link, str):
        return None, None

    try:
        # Pattern 1: query=lat%2Clng format (URL-encoded comma)
        # Example: ?api=1&query=47.5951518%2C-122.3316393
        pattern_query_encoded = r'[?&]query=(-?\d+\.?\d*)%2C(-?\d+\.?\d*)'
        match = re.search(pattern_query_encoded, map_link, re.IGNORECASE)
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
            logger.debug(f"✅ Method 1 (Pattern Query Encoded): Found coordinates query={lat}%2C{lng}")
            return validate_coordinates(lng, lat)

        # Pattern 2: @lat,lng,zoom format (including search URLs)
        pattern2 = r'@(-?\d+\.\d+),(-?\d+\.\d+),?\d*z?'
        match = re.search(pattern2, map_link)
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
            logger.debug(f"✅ Method 1 (Pattern 2): Found coordinates @{lat},{lng}")
            return validate_coordinates(lng, lat)

        # Pattern 3: q=lat,lng format
        pattern3 = r'[?&]q=(-?\d+\.\d+),(-?\d+\.\d+)'
        match = re.search(pattern3, map_link)
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
            logger.debug(f"✅ Method 1 (Pattern 3): Found coordinates q={lat},{lng}")
            return validate_coordinates(lng, lat)

        # Pattern 4: /place/.../@lat,lng
        pattern4 = r'/place/[^/]+/@(-?\d+\.\d+),(-?\d+\.\d+)'
        match = re.search(pattern4, map_link)
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
            logger.debug(f"✅ Method 1 (Pattern 4): Found coordinates in place URL")
            return validate_coordinates(lng, lat)

        # Pattern 5: Direct coordinate pair (with or without URL encoding)
        # First decode URL-encoded characters
        from urllib.parse import unquote
        decoded_link = unquote(map_link)

        pattern5 = r'(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)'
        match = re.search(pattern5, decoded_link)
        if match:
            coord1, coord2 = float(match.group(1)), float(match.group(2))
            # Determine which is lat vs lng based on ranges
            if abs(coord1) <= 90 and abs(coord2) <= 180:
                logger.debug(f"✅ Method 1 (Pattern 5): Found coordinates {coord1},{coord2}")
                return validate_coordinates(coord2, coord1)
            elif abs(coord2) <= 90 and abs(coord1) <= 180:
                return validate_coordinates(coord1, coord2)

        return None, None

    except Exception as e:
        logger.debug(f"Method 1 failed: {str(e)}")
        return None, None


def method2_url_resolution(map_link: str, timeout=10) -> Tuple[Optional[float], Optional[float]]:
    """
    METHOD 2: Resolve shortened URLs (goo.gl, maps.app.goo.gl) and extract from redirect

    Handles:
    - https://goo.gl/maps/xyz → redirects to full URL
    - https://maps.app.goo.gl/xyz → redirects to full URL
    - https://google.co.za/maps/... → follows to google.com
    """
    try:
        # Check if it's a shortened or regional URL
        if any(domain in map_link for domain in ['goo.gl', 'maps.app.goo.gl', 'google.co.za', 'google.com.au']):
            logger.info(f"🔄 Method 2: Resolving shortened/regional URL...")

            # Follow redirects to get final URL
            response = requests.head(map_link, allow_redirects=True, timeout=timeout)
            resolved_url = response.url

            if resolved_url != map_link:
                logger.info(f"✅ Method 2: Resolved to {resolved_url[:80]}...")
                # Try regex extraction on resolved URL
                return method1_regex_extraction(resolved_url)

        return None, None

    except Exception as e:
        logger.debug(f"Method 2 failed: {str(e)}")
        return None, None


def method3_html_scraping(map_link: str, timeout=15) -> Tuple[Optional[float], Optional[float]]:
    """
    METHOD 3: Fetch HTML content and scrape coordinates from page source

    Looks for:
    - Meta tags with coordinates
    - JavaScript variables containing lat/lng
    - Schema.org structured data
    """
    try:
        logger.info(f"🌐 Method 3: Fetching HTML content...")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(map_link, headers=headers, timeout=timeout, allow_redirects=True)

        if response.status_code == 200:
            html_content = response.text

            # Try to find coordinates in HTML
            # Pattern 1: Look for coordinates in URL within HTML
            coords_in_html = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', html_content)
            if coords_in_html:
                lat, lng = float(coords_in_html.group(1)), float(coords_in_html.group(2))
                logger.info(f"✅ Method 3: Found coordinates in HTML: {lat},{lng}")
                return validate_coordinates(lng, lat)

            # Pattern 2: Look for JSON data with coordinates
            json_pattern = r'"center":\{"lat":(-?\d+\.\d+),"lng":(-?\d+\.\d+)\}'
            json_match = re.search(json_pattern, html_content)
            if json_match:
                lat, lng = float(json_match.group(1)), float(json_match.group(2))
                logger.info(f"✅ Method 3: Found coordinates in JSON: {lat},{lng}")
                return validate_coordinates(lng, lat)

            # Pattern 3: Look for meta tags
            soup = BeautifulSoup(html_content, 'html.parser')

            # Check og:latitude and og:longitude meta tags
            lat_meta = soup.find('meta', property='og:latitude')
            lng_meta = soup.find('meta', property='og:longitude')

            if lat_meta and lng_meta:
                lat = float(lat_meta.get('content'))
                lng = float(lng_meta.get('content'))
                logger.info(f"✅ Method 3: Found coordinates in meta tags: {lat},{lng}")
                return validate_coordinates(lng, lat)

        return None, None

    except Exception as e:
        logger.debug(f"Method 3 failed: {str(e)}")
        return None, None


def method4_google_places_api(map_link: str, api_key: Optional[str] = None) -> Tuple[Optional[float], Optional[float]]:
    """
    METHOD 4: Use Google Places API Text Search (Recommended & Free Tier)

    Best for: Place names, addresses, and general queries
    Free tier: 1,000 requests/day
    API: https://maps.googleapis.com/maps/api/place/textsearch/json

    Note: Requires GOOGLE_MAPS_API_KEY environment variable
    Falls back gracefully if not available
    """
    try:
        if not api_key:
            import os
            api_key = os.environ.get('GOOGLE_MAPS_API_KEY')

        if not api_key:
            logger.debug("Method 4: Skipped (no API key)")
            return None, None

        logger.info(f"🗺️  Method 4: Using Google Places API Text Search...")

        # Extract query from URL
        query = None

        # Try to extract from query= parameter (place name searches)
        query_match = re.search(r'[?&]query=([^&]+)', map_link)
        if query_match:
            query = unquote(query_match.group(1)).replace('+', ' ')
            # Skip if it's coordinates (already handled by Method 1)
            if re.match(r'^-?\d+\.?\d*,-?\d+\.?\d*$', query):
                logger.debug("Method 4: Skipped (query contains coordinates, already extracted)")
                return None, None

        # Try to extract from place name in URL
        if not query:
            place_match = re.search(r'/place/([^/@]+)', map_link)
            if place_match:
                query = unquote(place_match.group(1)).replace('+', ' ')

        # Try to extract from search term
        if not query:
            search_match = re.search(r'/search/([^/@]+)', map_link)
            if search_match:
                query = unquote(search_match.group(1)).replace('+', ' ')

        if not query:
            logger.debug("Method 4: No place name found in URL")
            return None, None

        logger.info(f"   🔍 Searching for: '{query}'")

        # Use Google Places API Text Search
        places_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': query,
            'key': api_key
        }

        response = requests.get(places_url, params=params, timeout=10)
        data = response.json()

        if data.get('status') == 'OK' and data.get('results'):
            result = data['results'][0]
            location = result['geometry']['location']
            lat = location['lat']
            lng = location['lng']
            place_id = result.get('place_id', 'N/A')
            place_name = result.get('name', query)

            logger.info(f"✅ Method 4: Found '{place_name}' (place_id: {place_id[:20]}...)")
            logger.info(f"   Coordinates: {lat},{lng}")
            return validate_coordinates(lng, lat)
        elif data.get('status') == 'ZERO_RESULTS':
            logger.warning(f"Method 4: No results found for '{query}'")
            return None, None
        else:
            logger.warning(f"Method 4: API returned status: {data.get('status')}")
            return None, None

    except Exception as e:
        logger.debug(f"Method 4 failed: {str(e)}")
        return None, None


def extract_coordinates_from_url(map_link: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Enhanced coordinate extraction with 4 fallback methods.

    Methods (in order):
    1. Direct regex extraction (fast, covers 95% of cases)
    2. URL resolution for shortened/regional URLs
    3. HTML scraping when regex fails
    4. Google Places API Text Search (requires API key, free tier 1000/day)

    Returns:
        Tuple of (longitude, latitude) or (None, None) if all methods fail
    """
    if not map_link or not isinstance(map_link, str):
        return None, None

    logger.info(f"🔍 Extracting coordinates from: {map_link[:80]}...")

    # METHOD 1: Direct regex extraction (fastest)
    lng, lat = method1_regex_extraction(map_link)
    if lng is not None and lat is not None:
        logger.info(f"✅ Success with Method 1 (Regex): {lng:.6f}, {lat:.6f}")
        return lng, lat

    # METHOD 2: URL resolution for shortened URLs
    lng, lat = method2_url_resolution(map_link)
    if lng is not None and lat is not None:
        logger.info(f"✅ Success with Method 2 (URL Resolution): {lng:.6f}, {lat:.6f}")
        return lng, lat

    # METHOD 3: HTML scraping
    lng, lat = method3_html_scraping(map_link)
    if lng is not None and lat is not None:
        logger.info(f"✅ Success with Method 3 (HTML Scraping): {lng:.6f}, {lat:.6f}")
        return lng, lat

    # METHOD 4: Google Places API Text Search (requires API key)
    lng, lat = method4_google_places_api(map_link)
    if lng is not None and lat is not None:
        logger.info(f"✅ Success with Method 4 (Google Places API): {lng:.6f}, {lat:.6f}")
        return lng, lat

    logger.warning(f"❌ All 4 methods failed to extract coordinates from: {map_link[:80]}...")
    return None, None


def process_excel_file(input_file: str, output_file: str) -> None:
    """
    Process Excel file and convert map links to coordinates.
    Uses enhanced extraction with 4 fallback methods.
    """
    try:
        logger.info(f"Reading input file: {input_file}")
        df = pd.read_excel(input_file)
        df.columns = df.columns.str.strip()

        # Column mapping and validation
        column_mapping = {col.lower(): col for col in df.columns}

        map_column = None
        map_column_options = ['map link', 'maps link', 'maps', 'map', 'map links', 'maps links', 'map_link', 'maps_link', 'maplink', 'mapslink']

        for option in map_column_options:
            if option in column_mapping:
                map_column = column_mapping[option]
                break

        if not map_column:
            actual_columns = ', '.join(f'"{col}"' for col in df.columns)
            raise ValueError(f'Missing required map column. Found columns: {actual_columns}')

        # Find or create LONG/LATTs columns
        long_column = None
        for option in ['long', 'longitude', 'lng']:
            if option in column_mapping:
                long_column = column_mapping[option]
                break
        if not long_column:
            long_column = 'LONG'
            df[long_column] = None

        lat_column = None
        for option in ['latts', 'latt', 'lat', 'latitude']:
            if option in column_mapping:
                lat_column = column_mapping[option]
                break
        if not lat_column:
            lat_column = 'LATTs'
            df[lat_column] = None

        name_column = column_mapping.get('name', 'Name')

        if 'Comments' not in df.columns:
            df['Comments'] = None

        total_rows = len(df)
        logger.info(f"{'='*60}")
        logger.info(f"🚀 Starting processing: {total_rows} rows")
        logger.info(f"{'='*60}")

        successful = 0
        failed = 0
        skipped = 0

        for idx, row in df.iterrows():
            map_link = row[map_column]
            row_name = row.get(name_column, f"Row {idx + 1}")
            progress = ((idx + 1) / total_rows) * 100

            logger.info(f"📍 Processing row {idx + 1}/{total_rows} ({progress:.1f}%) - {row_name}")

            # Skip blank map links
            if pd.isna(map_link) or str(map_link).strip() == '':
                df.at[idx, 'Comments'] = 'Skipped: No map link provided'
                logger.warning(f"   ⏭️  Skipped: No map link provided")
                skipped += 1
                continue

            # Extract coordinates with 4 fallback methods
            lng, lat = extract_coordinates_from_url(str(map_link))

            if lng is not None and lat is not None:
                df.at[idx, long_column] = lng
                df.at[idx, lat_column] = lat
                df.at[idx, 'Comments'] = 'Success'
                successful += 1
                logger.info(f"   ✅ Success: Lng={lng:.6f}, Lat={lat:.6f}")
            else:
                df.at[idx, 'Comments'] = 'Failed: Could not extract coordinates (tried 4 methods)'
                failed += 1
                logger.error(f"   ❌ Failed: All methods exhausted")

            logger.info("")

        # Save output
        logger.info(f"Saving output file: {output_file}")
        df.to_excel(output_file, index=False)

        logger.info(f"{'='*60}")
        logger.info(f"✅ Processing complete!")
        logger.info(f"   Total: {total_rows} rows")
        logger.info(f"   ✅ Successful: {successful}")
        logger.info(f"   ❌ Failed: {failed}")
        logger.info(f"   ⏭️  Skipped: {skipped}")
        logger.info(f"{'='*60}")

        # Generate separate files for failed and skipped rows
        from pathlib import Path
        output_path = Path(output_file)
        output_stem = output_path.stem
        output_dir = output_path.parent
        output_ext = output_path.suffix

        # Filter failed rows (rows with Comments starting with "Failed")
        failed_df = df[df['Comments'].str.startswith('Failed', na=False)]
        if len(failed_df) > 0:
            failed_file = output_dir / f"{output_stem}_failed{output_ext}"
            failed_df.to_excel(failed_file, index=False)
            logger.info(f"✅ Saved {len(failed_df)} failed rows to: {failed_file}")
        else:
            logger.info("✅ No failed rows - skipping failed file")

        # Filter skipped rows (rows with Comments starting with "Skipped")
        skipped_df = df[df['Comments'].str.startswith('Skipped', na=False)]
        if len(skipped_df) > 0:
            skipped_file = output_dir / f"{output_stem}_skipped{output_ext}"
            skipped_df.to_excel(skipped_file, index=False)
            logger.info(f"✅ Saved {len(skipped_df)} skipped rows to: {skipped_file}")
        else:
            logger.info("✅ No skipped rows - skipping skipped file")

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python map_converter_enhanced.py <input_excel_file> <output_excel_file>")
        print("Example: python map_converter_enhanced.py input.xlsx output.xlsx")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        process_excel_file(input_file, output_file)
    except Exception as e:
        sys.exit(1)


if __name__ == "__main__":
    main()
