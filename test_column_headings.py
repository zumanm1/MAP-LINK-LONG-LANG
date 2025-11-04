#!/usr/bin/env python3
"""
Test to verify LONG and LATTs column headings
"""

import pandas as pd
import tempfile
from pathlib import Path
from map_converter import process_excel_file


def test_new_file_uses_long_latts():
    """Test that new files get 'LONG' and 'LATTs' as column headings"""
    # Create test data WITHOUT existing Long/Lat columns
    df = pd.DataFrame({
        'Name': ['Sandton', 'Cape Town', 'Durban'],
        'Region': ['Gauteng', 'Western Cape', 'KwaZulu-Natal'],
        'Maps link': [
            'https://maps.google.com/?q=-26.1076,28.0567',
            'https://maps.google.com/?q=-33.9249,18.4241',
            'https://maps.google.com/?q=-29.8587,31.0218'
        ]
    })

    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_input:
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_output:
            input_path = tmp_input.name
            output_path = tmp_output.name

    try:
        # Save test data
        df.to_excel(input_path, index=False)

        # Process file
        process_excel_file(input_path, output_path)

        # Read result
        result_df = pd.read_excel(output_path)

        # Check that LONG and LATTs columns exist
        assert 'LONG' in result_df.columns, f"Expected 'LONG' column, got: {result_df.columns.tolist()}"
        assert 'LATTs' in result_df.columns, f"Expected 'LATTs' column, got: {result_df.columns.tolist()}"

        # Check that old names don't exist
        assert 'Long' not in result_df.columns, "Old 'Long' column should not exist"
        assert 'Latts' not in result_df.columns, "Old 'Latts' column should not exist"

        # Check that coordinates were filled
        assert pd.notna(result_df['LONG'].iloc[0]), "LONG should have coordinates"
        assert pd.notna(result_df['LATTs'].iloc[0]), "LATTs should have coordinates"

        print("✅ Test passed: New files use 'LONG' and 'LATTs' as headings")
        print(f"   Columns: {result_df.columns.tolist()}")
        print(f"   Sample data:")
        print(f"   - LONG: {result_df['LONG'].iloc[0]}")
        print(f"   - LATTs: {result_df['LATTs'].iloc[0]}")
        return True

    finally:
        # Cleanup
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


def test_existing_long_latts_preserved():
    """Test that existing LONG and LATTs columns are used (not duplicated)"""
    # Create test data WITH existing LONG/LATTs columns
    df = pd.DataFrame({
        'Name': ['Sandton', 'Cape Town', 'Durban'],
        'Region': ['Gauteng', 'Western Cape', 'KwaZulu-Natal'],
        'Maps link': [
            'https://maps.google.com/?q=-26.1076,28.0567',
            'https://maps.google.com/?q=-33.9249,18.4241',
            'https://maps.google.com/?q=-29.8587,31.0218'
        ],
        'LONG': [None, None, None],
        'LATTs': [None, None, None]
    })

    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_input:
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_output:
            input_path = tmp_input.name
            output_path = tmp_output.name

    try:
        # Save test data
        df.to_excel(input_path, index=False)

        # Process file
        process_excel_file(input_path, output_path)

        # Read result
        result_df = pd.read_excel(output_path)

        # Check that LONG and LATTs columns exist
        assert 'LONG' in result_df.columns, f"Expected 'LONG' column, got: {result_df.columns.tolist()}"
        assert 'LATTs' in result_df.columns, f"Expected 'LATTs' column, got: {result_df.columns.tolist()}"

        # Check that coordinates were filled
        assert pd.notna(result_df['LONG'].iloc[0]), "LONG should have coordinates"
        assert pd.notna(result_df['LATTs'].iloc[0]), "LATTs should have coordinates"

        # Count columns to ensure no duplicates
        column_count = len(result_df.columns)
        assert column_count == 5, f"Expected 5 columns, got {column_count}: {result_df.columns.tolist()}"

        print("✅ Test passed: Existing 'LONG' and 'LATTs' columns are preserved")
        print(f"   Columns: {result_df.columns.tolist()}")
        print(f"   Sample data:")
        print(f"   - LONG: {result_df['LONG'].iloc[0]}")
        print(f"   - LATTs: {result_df['LATTs'].iloc[0]}")
        return True

    finally:
        # Cleanup
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


def test_lowercase_long_lat_mapped_correctly():
    """Test that lowercase 'long' and 'lat' columns are detected and used"""
    # Create test data WITH lowercase long/lat columns
    df = pd.DataFrame({
        'Name': ['Sandton', 'Cape Town', 'Durban'],
        'Region': ['Gauteng', 'Western Cape', 'KwaZulu-Natal'],
        'Maps link': [
            'https://maps.google.com/?q=-26.1076,28.0567',
            'https://maps.google.com/?q=-33.9249,18.4241',
            'https://maps.google.com/?q=-29.8587,31.0218'
        ],
        'long': [None, None, None],
        'lat': [None, None, None]
    })

    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_input:
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_output:
            input_path = tmp_input.name
            output_path = tmp_output.name

    try:
        # Save test data
        df.to_excel(input_path, index=False)

        # Process file
        process_excel_file(input_path, output_path)

        # Read result
        result_df = pd.read_excel(output_path)

        # Check that lowercase columns are preserved
        assert 'long' in result_df.columns, f"Expected 'long' column, got: {result_df.columns.tolist()}"
        assert 'lat' in result_df.columns, f"Expected 'lat' column, got: {result_df.columns.tolist()}"

        # Check that LONG and LATTs were NOT created
        assert 'LONG' not in result_df.columns, "'LONG' should not be created when 'long' exists"
        assert 'LATTs' not in result_df.columns, "'LATTs' should not be created when 'lat' exists"

        # Check that coordinates were filled
        assert pd.notna(result_df['long'].iloc[0]), "long should have coordinates"
        assert pd.notna(result_df['lat'].iloc[0]), "lat should have coordinates"

        print("✅ Test passed: Lowercase 'long' and 'lat' columns are detected and used")
        print(f"   Columns: {result_df.columns.tolist()}")
        print(f"   Sample data:")
        print(f"   - long: {result_df['long'].iloc[0]}")
        print(f"   - lat: {result_df['lat'].iloc[0]}")
        return True

    finally:
        # Cleanup
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🧪 Testing LONG and LATTs Column Headings")
    print("="*60 + "\n")

    # Run all tests
    test_new_file_uses_long_latts()
    print()
    test_existing_long_latts_preserved()
    print()
    test_lowercase_long_lat_mapped_correctly()

    print("\n" + "="*60)
    print("✅ All column heading tests passed!")
    print("="*60 + "\n")
