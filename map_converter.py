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
        # Google Maps formats:
        # 1. https://www.google.com/maps/place/Location/@-26.108204,28.0527061,17z
        # 2. https://www.google.com/maps?q=-26.108204,28.0527061
        # 3. https://maps.google.com/?q=-26.108204,28.0527061
        # 4. https://goo.gl/maps/... (shortened)
        
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
                return coord2, coord1  # coord1 is lat, coord2 is lng
            elif abs(coord2) <= 90 and abs(coord1) <= 180:
                return coord1, coord2  # coord2 is lat, coord1 is lng
        
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
        
        # Validate required columns
        required_columns = ['Name', 'Region', 'Map link']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Initialize Long and Latts columns if they don't exist
        if 'Long' not in df.columns:
            df['Long'] = None
        if 'Latts' not in df.columns:
            df['Latts'] = None
        
        # Process each row
        logger.info(f"Processing {len(df)} rows...")
        for idx, row in df.iterrows():
            map_link = row['Map link']
            if pd.notna(map_link):
                lng, lat = extract_coordinates_from_url(str(map_link))
                if lng is not None and lat is not None:
                    df.at[idx, 'Long'] = lng
                    df.at[idx, 'Latts'] = lat
                    logger.info(f"Row {idx + 1} ({row['Name']}): Extracted coordinates - Lng: {lng}, Lat: {lat}")
                else:
                    logger.warning(f"Row {idx + 1} ({row['Name']}): Failed to extract coordinates")
            else:
                logger.warning(f"Row {idx + 1} ({row['Name']}): No map link provided")
        
        # Save to output file
        logger.info(f"Saving output file: {output_file}")
        df.to_excel(output_file, index=False)
        logger.info("Processing complete!")
        
        # Display summary
        successful = df[['Long', 'Latts']].notna().all(axis=1).sum()
        total = len(df)
        logger.info(f"Summary: Successfully processed {successful}/{total} rows")
        
    except FileNotFoundError:
        logger.error(f"Input file not found: {input_file}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        sys.exit(1)


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 3:
        print("Usage: python map_converter.py <input_excel_file> <output_excel_file>")
        print("Example: python map_converter.py input.xlsx output.xlsx")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    process_excel_file(input_file, output_file)


if __name__ == "__main__":
    main()
