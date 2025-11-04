#!/usr/bin/env python3
"""
Excel Map Link to Coordinates Converter
Converts map links in Excel files to longitude and latitude coordinates.
"""

import pandas as pd
import re
import sys
import logging
from typing import Tuple, Optional
from urllib.parse import urlparse, parse_qs
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_coordinates_from_url(map_link: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Extract longitude and latitude from various map link formats.
    
    Args:
        map_link: URL string containing map location
        
    Returns:
        Tuple of (longitude, latitude) or (None, None) if extraction fails
    """
    if not map_link or not isinstance(map_link, str):
        return None, None
    
    try:
        # If it's a shortened URL (goo.gl or maps.app.goo.gl), resolve it first
        if 'goo.gl' in map_link or 'maps.app.goo.gl' in map_link:
            try:
                response = requests.head(map_link, allow_redirects=True, timeout=10)
                map_link = response.url
                logger.debug(f"Resolved shortened URL to: {map_link}")
            except Exception as e:
                logger.warning(f"Failed to resolve shortened URL: {str(e)}")
        
        # Google Maps formats:
        # 1. https://www.google.com/maps/place/Location/@-26.108204,28.0527061,17z
        # 2. https://www.google.com/maps?q=-26.108204,28.0527061
        # 3. https://maps.google.com/?q=-26.108204,28.0527061
        # 4. https://goo.gl/maps/... (shortened, resolved above)
        
        # Pattern 1: @lat,lng format
        pattern1 = r'@(-?\d+\.\d+),(-?\d+\.\d+)'
        match = re.search(pattern1, map_link)
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
            return lng, lat
        
        # Pattern 2: q=lat,lng format
        pattern2 = r'[?&]q=(-?\d+\.\d+),(-?\d+\.\d+)'
        match = re.search(pattern2, map_link)
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
            return lng, lat
        
        # Pattern 3: /maps/place/.../@lat,lng
        pattern3 = r'/place/[^/]+/@(-?\d+\.\d+),(-?\d+\.\d+)'
        match = re.search(pattern3, map_link)
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
            return lng, lat
        
        # Pattern 4: Direct coordinate pair in URL
        pattern4 = r'(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)'
        match = re.search(pattern4, map_link)
        if match:
            coord1, coord2 = float(match.group(1)), float(match.group(2))
            # Determine which is lat and which is lng based on typical ranges
            # Latitude: -90 to 90, Longitude: -180 to 180
            if abs(coord1) <= 90 and abs(coord2) <= 180:
                # coord1 is likely latitude
                return coord2, coord1
            elif abs(coord2) <= 90 and abs(coord1) <= 180:
                # coord2 is likely latitude
                return coord1, coord2
            elif abs(coord1) <= 90:
                # Only coord1 fits latitude range, coord2 must be longitude
                return coord2, coord1
            elif abs(coord2) <= 90:
                # Only coord2 fits latitude range, coord1 must be longitude
                return coord1, coord2
            else:
                # Both > 90, can't determine order - assume first is lat, second is lng
                # This handles edge cases like (120.0, 150.0) in Eastern Asia/Pacific
                return coord2, coord1
        
        logger.warning(f"Could not extract coordinates from: {map_link}")
        return None, None
        
    except Exception as e:
        logger.error(f"Error extracting coordinates from {map_link}: {str(e)}")
        return None, None


def process_excel_file(input_file: str, output_file: str) -> None:
    """
    Process Excel file and convert map links to coordinates.
    
    Args:
        input_file: Path to input Excel file
        output_file: Path to output Excel file
    """
    try:
        # Read the Excel file
        logger.info(f"Reading input file: {input_file}")
        df = pd.read_excel(input_file)

        # Clean column names: strip whitespace
        df.columns = df.columns.str.strip()

        # Create a case-insensitive column mapping
        column_mapping = {col.lower(): col for col in df.columns}

        # Validate required map column (case-insensitive, flexible names)
        map_column = None
        map_column_options = ['map link', 'maps link', 'maps', 'map', 'map links', 'maps links', 'map_link', 'maps_link', 'maplink', 'mapslink']

        for option in map_column_options:
            if option in column_mapping:
                map_column = column_mapping[option]
                break

        if not map_column:
            actual_columns = ', '.join(f'"{col}"' for col in df.columns)
            raise ValueError(f'Missing required map column. Looking for: "Map link" or "Maps" (case-insensitive). Found columns: {actual_columns}')

        # Validate other required columns (case-insensitive)
        required_columns = ['name', 'region']
        missing_columns = []

        for req_col in required_columns:
            if req_col not in column_mapping:
                missing_columns.append(req_col.capitalize())
        if missing_columns:
            actual_columns = ', '.join(f'"{col}"' for col in df.columns)
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}. Found columns: {actual_columns}")

        # Determine longitude and latitude column names (case-insensitive, flexible)
        # The column_mapping already maps lowercase keys to actual column names
        # So 'long' maps to 'LONG' if that's what the user has

        # Try to find existing Long column
        long_column = None
        for option in ['long', 'longitude', 'lng']:
            if option in column_mapping:
                long_column = column_mapping[option]  # Returns actual column name (e.g., 'LONG')
                break

        # If not found, create new column with default name 'LONG'
        if not long_column:
            long_column = 'LONG'
            df[long_column] = None

        # Try to find existing Lat column
        lat_column = None
        for option in ['latts', 'latt', 'lat', 'latitude']:
            if option in column_mapping:
                lat_column = column_mapping[option]  # Returns actual column name (e.g., 'LATTs')
                break

        # If not found, create new column with default name 'LATTs'
        if not lat_column:
            lat_column = 'LATTs'
            df[lat_column] = None
        
        # Get the actual Name column (case-insensitive)
        name_column = column_mapping.get('name', 'Name')

        # Process each row
        logger.info(f"Processing {len(df)} rows...")
        for idx, row in df.iterrows():
            map_link = row[map_column]
            row_name = row.get(name_column, f"Row {idx + 1}")

            # Skip rows with missing or empty map links (blank output)
            if pd.isna(map_link) or str(map_link).strip() == '':
                logger.warning(f"Row {idx + 1} ({row_name}): No map link provided")
                # LONG and LATTs remain blank (NaN) - no modification
                continue

            # Process rows with map links
            lng, lat = extract_coordinates_from_url(str(map_link))
            if lng is not None and lat is not None:
                df.at[idx, long_column] = lng
                df.at[idx, lat_column] = lat
                logger.info(f"Row {idx + 1} ({row_name}): Extracted coordinates - Lng: {lng}, Lat: {lat}")
            else:
                logger.warning(f"Row {idx + 1} ({row_name}): Failed to extract coordinates")
                # LONG and LATTs remain blank (NaN) - no modification
        
        # Save to output file
        logger.info(f"Saving output file: {output_file}")
        df.to_excel(output_file, index=False)
        logger.info("Processing complete!")
        
        # Display summary
        successful = df[[long_column, lat_column]].notna().all(axis=1).sum()
        total = len(df)
        logger.info(f"Summary: Successfully processed {successful}/{total} rows")
        
    except FileNotFoundError as e:
        logger.error(f"Input file not found: {input_file}")
        raise
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 3:
        print("Usage: python map_converter.py <input_excel_file> <output_excel_file>")
        print("Example: python map_converter.py input.xlsx output.xlsx")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        process_excel_file(input_file, output_file)
    except Exception as e:
        sys.exit(1)


if __name__ == "__main__":
    main()
