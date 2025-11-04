#!/usr/bin/env python3
"""
Test suite for flexible column validation
Tests case-insensitive, whitespace-tolerant, and variation-aware column validation
"""

import pytest
import pandas as pd
import tempfile
from pathlib import Path
from map_converter import process_excel_file


def test_lowercase_columns():
    """Test that lowercase column names work"""
    # Create test data with lowercase columns
    df = pd.DataFrame({
        'name': ['Test Location'],
        'region': ['Test Region'],
        'maps': ['https://maps.google.com/?q=-26.1076,28.0567']
    })

    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_input:
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_output:
            input_path = tmp_input.name
            output_path = tmp_output.name

    try:
        # Save test data
        df.to_excel(input_path, index=False)

        # Process file - should work with lowercase columns
        process_excel_file(input_path, output_path)

        # Read result
        result_df = pd.read_excel(output_path)

        # Check that coordinates were extracted
        assert 'Long' in result_df.columns or 'Longitude' in result_df.columns
        assert 'Latts' in result_df.columns or 'Latitude' in result_df.columns

        print("✅ Lowercase columns test passed")
        return True

    finally:
        # Cleanup
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


def test_uppercase_columns():
    """Test that uppercase column names work"""
    # Create test data with uppercase columns
    df = pd.DataFrame({
        'NAME': ['Test Location'],
        'REGION': ['Test Region'],
        'MAP LINK': ['https://maps.google.com/?q=-26.1076,28.0567']
    })

    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_input:
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_output:
            input_path = tmp_input.name
            output_path = tmp_output.name

    try:
        # Save test data
        df.to_excel(input_path, index=False)

        # Process file - should work with uppercase columns
        process_excel_file(input_path, output_path)

        # Read result
        result_df = pd.read_excel(output_path)

        # Check that coordinates were extracted
        assert 'Long' in result_df.columns or 'Longitude' in result_df.columns
        assert 'Latts' in result_df.columns or 'Latitude' in result_df.columns

        print("✅ Uppercase columns test passed")
        return True

    finally:
        # Cleanup
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


def test_column_with_spaces():
    """Test that columns with extra spaces work"""
    # Create test data with spaces in column names
    df = pd.DataFrame({
        ' Name ': ['Test Location'],
        'Region  ': ['Test Region'],
        '  Maps': ['https://maps.google.com/?q=-26.1076,28.0567']
    })

    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_input:
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_output:
            input_path = tmp_input.name
            output_path = tmp_output.name

    try:
        # Save test data
        df.to_excel(input_path, index=False)

        # Process file - should work after stripping spaces
        process_excel_file(input_path, output_path)

        # Read result
        result_df = pd.read_excel(output_path)

        # Check that coordinates were extracted
        assert 'Long' in result_df.columns or 'Longitude' in result_df.columns
        assert 'Latts' in result_df.columns or 'Latitude' in result_df.columns

        print("✅ Column with spaces test passed")
        return True

    finally:
        # Cleanup
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


def test_alternative_map_column_names():
    """Test various alternative map column names"""
    alternative_names = [
        'map',
        'map links',
        'map_link',
        'maplink'
    ]

    for map_col_name in alternative_names:
        # Create test data with alternative column name
        df = pd.DataFrame({
            'Name': ['Test Location'],
            'Region': ['Test Region'],
            map_col_name: ['https://maps.google.com/?q=-26.1076,28.0567']
        })

        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_input:
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_output:
                input_path = tmp_input.name
                output_path = tmp_output.name

        try:
            # Save test data
            df.to_excel(input_path, index=False)

            # Process file - should work with alternative name
            process_excel_file(input_path, output_path)

            # Read result
            result_df = pd.read_excel(output_path)

            # Check that coordinates were extracted
            assert 'Long' in result_df.columns or 'Longitude' in result_df.columns
            assert 'Latts' in result_df.columns or 'Latitude' in result_df.columns

            print(f"✅ Alternative map column name '{map_col_name}' test passed")

        finally:
            # Cleanup
            Path(input_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)

    return True


def test_existing_long_lat_columns():
    """Test that existing Long/Lat columns are used instead of creating new ones"""
    # Create test data with existing Longitude/Latitude columns
    df = pd.DataFrame({
        'Name': ['Test Location'],
        'Region': ['Test Region'],
        'Maps': ['https://maps.google.com/?q=-26.1076,28.0567'],
        'Longitude': [None],
        'Latitude': [None]
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

        # Check that existing columns were used
        assert 'Longitude' in result_df.columns
        assert 'Latitude' in result_df.columns

        # Check that coordinates were filled in
        assert pd.notna(result_df['Longitude'].iloc[0])
        assert pd.notna(result_df['Latitude'].iloc[0])

        # Check that no duplicate columns were created
        assert 'Long' not in result_df.columns
        assert 'Latts' not in result_df.columns

        print("✅ Existing Long/Lat columns test passed")
        return True

    finally:
        # Cleanup
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


def test_missing_required_column():
    """Test that missing required columns are caught with helpful error"""
    # Create test data missing 'Name' column
    df = pd.DataFrame({
        'Region': ['Test Region'],
        'Maps': ['https://maps.google.com/?q=-26.1076,28.0567']
    })

    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_input:
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_output:
            input_path = tmp_input.name
            output_path = tmp_output.name

    try:
        # Save test data
        df.to_excel(input_path, index=False)

        # Process file - should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            process_excel_file(input_path, output_path)

        # Check error message is helpful
        error_msg = str(exc_info.value)
        assert 'Name' in error_msg  # Should mention missing column
        assert 'Found columns' in error_msg  # Should show actual columns

        print("✅ Missing required column test passed")
        return True

    finally:
        # Cleanup
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


def test_missing_map_column():
    """Test that missing map column is caught with helpful error"""
    # Create test data missing map column
    df = pd.DataFrame({
        'Name': ['Test Location'],
        'Region': ['Test Region'],
        'SomeOtherColumn': ['value']
    })

    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_input:
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_output:
            input_path = tmp_input.name
            output_path = tmp_output.name

    try:
        # Save test data
        df.to_excel(input_path, index=False)

        # Process file - should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            process_excel_file(input_path, output_path)

        # Check error message is helpful
        error_msg = str(exc_info.value)
        assert 'map column' in error_msg.lower()  # Should mention map column
        assert 'Found columns' in error_msg  # Should show actual columns

        print("✅ Missing map column test passed")
        return True

    finally:
        # Cleanup
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🧪 Testing Column Validation")
    print("="*60 + "\n")

    # Run all tests
    test_lowercase_columns()
    test_uppercase_columns()
    test_column_with_spaces()
    test_alternative_map_column_names()
    test_existing_long_lat_columns()
    test_missing_required_column()
    test_missing_map_column()

    print("\n" + "="*60)
    print("✅ All column validation tests passed!")
    print("="*60 + "\n")
