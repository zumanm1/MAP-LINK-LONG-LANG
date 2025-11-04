#!/usr/bin/env python3
"""
Parallel Map Link to Coordinates Converter
Runs ALL 5 extraction methods in parallel and compares results
"""

import pandas as pd
import re
import sys
import logging
from typing import Tuple, Optional, Dict
from urllib.parse import urlparse, parse_qs, unquote
import requests
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_coordinates(lng: float, lat: float) -> Tuple[Optional[float], Optional[float]]:
    """Validate longitude and latitude are within valid ranges."""
    if not (-90.0 <= lat <= 90.0):
        return None, None
    if not (-180.0 <= lng <= 180.0):
        return None, None
    return lng, lat


def method1_regex_extraction(map_link: str) -> Tuple[Optional[float], Optional[float]]:
    """METHOD 1: Direct regex pattern matching (fastest, most reliable)"""
    if not map_link or not isinstance(map_link, str):
        return None, None

    try:
        # Pattern 1: query=lat%2Clng format (URL-encoded comma)
        pattern_query_encoded = r'[?&]query=(-?\d+\.?\d*)%2C(-?\d+\.?\d*)'
        match = re.search(pattern_query_encoded, map_link, re.IGNORECASE)
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
            return validate_coordinates(lng, lat)

        # BUG FIX #9: Make decimal points optional to support integer coordinates
        # Pattern 2: @lat,lng,zoom format (supports @40,74,12z and @40.123,74.456,12z)
        pattern2 = r'@(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?),?\d*z?'
        match = re.search(pattern2, map_link)
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
            return validate_coordinates(lng, lat)

        # Pattern 3: q=lat,lng format (supports q=40,74 and q=40.123,74.456)
        pattern3 = r'[?&]q=(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)'
        match = re.search(pattern3, map_link)
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
            return validate_coordinates(lng, lat)

        # Pattern 4: /place/.../@lat,lng (supports integer and decimal)
        pattern4 = r'/place/[^/]+/@(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)'
        match = re.search(pattern4, map_link)
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
            return validate_coordinates(lng, lat)

        # Pattern 5: Direct coordinate pair (supports integer and decimal)
        decoded_link = unquote(map_link)
        pattern5 = r'(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)'
        match = re.search(pattern5, decoded_link)
        if match:
            coord1, coord2 = float(match.group(1)), float(match.group(2))
            if abs(coord1) <= 90 and abs(coord2) <= 180:
                return validate_coordinates(coord2, coord1)
            elif abs(coord2) <= 90 and abs(coord1) <= 180:
                return validate_coordinates(coord1, coord2)

        return None, None

    except Exception as e:
        logger.debug(f"Method 1 failed: {str(e)}")
        return None, None


def method2_url_resolution(map_link: str, timeout=10) -> Tuple[Optional[float], Optional[float]]:
    """METHOD 2: Resolve shortened URLs and extract from redirect"""
    try:
        if any(domain in map_link for domain in ['goo.gl', 'maps.app.goo.gl', 'google.co.za', 'google.com.au']):
            response = requests.head(map_link, allow_redirects=True, timeout=timeout)
            resolved_url = response.url

            if resolved_url != map_link:
                return method1_regex_extraction(resolved_url)

        return None, None

    except Exception as e:
        logger.debug(f"Method 2 failed: {str(e)}")
        return None, None


def method3_html_scraping(map_link: str, timeout=15) -> Tuple[Optional[float], Optional[float]]:
    """METHOD 3: Fetch HTML content and scrape coordinates"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(map_link, headers=headers, timeout=timeout, allow_redirects=True)

        if response.status_code == 200:
            html_content = response.text

            # Try coordinates in HTML
            coords_in_html = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', html_content)
            if coords_in_html:
                lat, lng = float(coords_in_html.group(1)), float(coords_in_html.group(2))
                return validate_coordinates(lng, lat)

            # Try JSON data
            json_pattern = r'"center":\{"lat":(-?\d+\.\d+),"lng":(-?\d+\.\d+)\}'
            json_match = re.search(json_pattern, html_content)
            if json_match:
                lat, lng = float(json_match.group(1)), float(json_match.group(2))
                return validate_coordinates(lng, lat)

            # Try meta tags
            soup = BeautifulSoup(html_content, 'html.parser')
            lat_meta = soup.find('meta', property='og:latitude')
            lng_meta = soup.find('meta', property='og:longitude')

            if lat_meta and lng_meta:
                lat = float(lat_meta.get('content'))
                lng = float(lng_meta.get('content'))
                return validate_coordinates(lng, lat)

        return None, None

    except Exception as e:
        logger.debug(f"Method 3 failed: {str(e)}")
        return None, None


def method4_google_places_api(map_link: str, api_key: Optional[str] = None) -> Tuple[Optional[float], Optional[float]]:
    """METHOD 4: Use Google Places API Text Search"""
    try:
        if not api_key:
            import os
            api_key = os.environ.get('GOOGLE_MAPS_API_KEY')

        if not api_key:
            return None, None

        # Extract query from URL
        query = None

        query_match = re.search(r'[?&]query=([^&]+)', map_link)
        if query_match:
            query = unquote(query_match.group(1)).replace('+', ' ')
            if re.match(r'^-?\d+\.?\d*,-?\d+\.?\d*$', query):
                return None, None

        if not query:
            place_match = re.search(r'/place/([^/@]+)', map_link)
            if place_match:
                query = unquote(place_match.group(1)).replace('+', ' ')

        if not query:
            search_match = re.search(r'/search/([^/@]+)', map_link)
            if search_match:
                query = unquote(search_match.group(1)).replace('+', ' ')

        if not query:
            return None, None

        # Use Google Places API Text Search
        places_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {'query': query, 'key': api_key}

        response = requests.get(places_url, params=params, timeout=10)
        data = response.json()

        if data.get('status') == 'OK' and data.get('results'):
            result = data['results'][0]
            location = result['geometry']['location']
            lat = location['lat']
            lng = location['lng']
            return validate_coordinates(lng, lat)

        return None, None

    except Exception as e:
        logger.debug(f"Method 4 failed: {str(e)}")
        return None, None


def method5_selenium_scraping(map_link: str, timeout=20) -> Tuple[Optional[float], Optional[float]]:
    """METHOD 5: Use Selenium to scrape Google Maps (like Puppeteer)"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.common.exceptions import TimeoutException as SeleniumTimeoutException
        from webdriver_manager.chrome import ChromeDriverManager

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        # Auto-install ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # BUG FIX #2: Add page load timeout to prevent infinite hangs
        driver.set_page_load_timeout(15)  # 15 second max page load
        driver.set_script_timeout(10)     # 10 second max script execution

        try:
            driver.get(map_link)
            time.sleep(5)  # Wait for redirect and page load

            # Extract from URL after redirect
            current_url = driver.current_url
            match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', current_url)

            if match:
                lat, lng = float(match.group(1)), float(match.group(2))
                result = validate_coordinates(lng, lat)
                return result

            # Try to extract from page source
            page_source = driver.page_source
            match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', page_source)

            if match:
                lat, lng = float(match.group(1)), float(match.group(2))
                result = validate_coordinates(lng, lat)
                return result

            return None, None

        except SeleniumTimeoutException:
            # BUG FIX #2: Handle page load timeout gracefully
            logger.debug(f"Selenium page load timeout for {map_link}")
            return None, None
        finally:
            # BUG FIX #6: Ensure driver.quit() always runs (no early returns above)
            driver.quit()

    except Exception as e:
        logger.debug(f"Method 5 failed: {str(e)}")
        return None, None


def extract_coordinates_parallel(map_link: str) -> Dict[str, Tuple[Optional[float], Optional[float]]]:
    """
    Run ALL 5 extraction methods in parallel and return results from each.

    Returns:
        Dict with keys: 'method1', 'method2', 'method3', 'method4', 'method5'
        Each value is a tuple of (longitude, latitude) or (None, None)
    """
    results = {
        'method1': (None, None),
        'method2': (None, None),
        'method3': (None, None),
        'method4': (None, None),
        'method5': (None, None),
    }

    if not map_link or not isinstance(map_link, str):
        return results

    # Define methods to run
    methods = {
        'method1': lambda: method1_regex_extraction(map_link),
        'method2': lambda: method2_url_resolution(map_link),
        'method3': lambda: method3_html_scraping(map_link),
        'method4': lambda: method4_google_places_api(map_link),
        'method5': lambda: method5_selenium_scraping(map_link),
    }

    # Run all methods in parallel with timeout protection
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_method = {executor.submit(func): name for name, func in methods.items()}

        try:
            # BUG FIX #1: Add timeout to as_completed (20s max wait for all methods)
            for future in as_completed(future_to_method, timeout=20):
                method_name = future_to_method[future]
                try:
                    # BUG FIX #1: Add timeout to future.result (5s per method)
                    results[method_name] = future.result(timeout=5)
                except TimeoutError:
                    logger.debug(f"{method_name} timed out after 5 seconds")
                    results[method_name] = (None, None)
                except Exception as e:
                    logger.debug(f"{method_name} raised exception: {str(e)}")
                    results[method_name] = (None, None)
        except TimeoutError:
            # as_completed() timed out - some methods still running
            logger.warning("Parallel extraction timed out after 20 seconds")
            for future, name in future_to_method.items():
                if not future.done():
                    logger.debug(f"{name} did not complete in time")
                    if name not in results or results[name] == (None, None):
                        results[name] = (None, None)

    return results


def process_excel_file(input_file: str, output_file: str) -> None:
    """Process Excel file with parallel extraction from all 5 methods."""
    try:
        logger.info(f"Reading input file: {input_file}")
        df = pd.read_excel(input_file)
        df.columns = df.columns.str.strip()

        column_mapping = {col.lower(): col for col in df.columns}

        # Find map column
        map_column = None
        map_column_options = ['map link', 'maps link', 'maps', 'map', 'map links', 'maps links']
        for option in map_column_options:
            if option in column_mapping:
                map_column = column_mapping[option]
                break

        if not map_column:
            raise ValueError(f'Missing required map column. Found columns: {", ".join(df.columns)}')

        # Add columns for each method
        for i in range(1, 6):
            df[f'Method{i}_LONG'] = None
            df[f'Method{i}_LAT'] = None

        df['Best_LONG'] = None
        df['Best_LAT'] = None
        df['Comments'] = None

        total_rows = len(df)
        logger.info(f"{'='*60}")
        logger.info(f"🚀 Starting parallel processing: {total_rows} rows")
        logger.info(f"{'='*60}")

        for idx, row in df.iterrows():
            map_link = row[map_column]
            row_name = row.get('Name', f"Row {idx + 1}")
            progress = ((idx + 1) / total_rows) * 100

            logger.info(f"📍 Processing row {idx + 1}/{total_rows} ({progress:.1f}%) - {row_name}")

            if pd.isna(map_link) or str(map_link).strip() == '':
                df.at[idx, 'Comments'] = 'Skipped: No map link provided'
                logger.warning(f"   ⏭️  Skipped: No map link provided")
                continue

            # Extract with all 5 methods in parallel
            logger.info(f"   🔄 Running all 5 methods in parallel...")
            results = extract_coordinates_parallel(str(map_link))

            # Store results for each method
            success_count = 0
            for i in range(1, 6):
                method_key = f'method{i}'
                lng, lat = results[method_key]

                if lng is not None and lat is not None:
                    df.at[idx, f'Method{i}_LONG'] = lng
                    df.at[idx, f'Method{i}_LAT'] = lat
                    success_count += 1
                    logger.info(f"   ✅ Method {i}: Lng={lng:.6f}, Lat={lat:.6f}")
                else:
                    logger.info(f"   ❌ Method {i}: Failed")

            # Use Method 1 as "best" (most reliable for coordinates)
            best_lng, best_lat = results['method1']

            # If Method 1 failed, try others in order
            if best_lng is None:
                for i in range(2, 6):
                    best_lng, best_lat = results[f'method{i}']
                    if best_lng is not None:
                        break

            if best_lng is not None and best_lat is not None:
                df.at[idx, 'Best_LONG'] = best_lng
                df.at[idx, 'Best_LAT'] = best_lat
                df.at[idx, 'Comments'] = f'Success: {success_count}/5 methods succeeded'
            else:
                df.at[idx, 'Comments'] = 'Failed: All 5 methods failed'

            logger.info("")

        # Save output
        logger.info(f"Saving output file: {output_file}")
        df.to_excel(output_file, index=False)

        logger.info(f"{'='*60}")
        logger.info(f"✅ Processing complete!")
        logger.info(f"{'='*60}")

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python map_converter_parallel.py <input_excel_file> <output_excel_file>")
        print("Example: python map_converter_parallel.py input.xlsx output.xlsx")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        process_excel_file(input_file, output_file)
    except Exception as e:
        sys.exit(1)


if __name__ == "__main__":
    main()
