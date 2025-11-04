#!/usr/bin/env python3
"""
Test to verify JSON serialization with NaN values
"""

import pandas as pd
import json


def test_nan_to_json():
    """Test that NaN values are properly converted to null in JSON"""
    # Create DataFrame with NaN values
    df = pd.DataFrame({
        'Name': ['Location 1', None, 'Location 3'],
        'LONG': [28.05, None, 31.02],
        'LATTs': [-26.10, None, -29.86]
    })

    print("Original DataFrame:")
    print(df)
    print("\nData types:")
    print(df.dtypes)
    print()

    # Test 1: Without fillna (this would cause JSON error)
    print("="*60)
    print("Test 1: Without fillna (BROKEN)")
    print("="*60)
    try:
        data_broken = df.to_dict('records')
        json_str = json.dumps(data_broken)
        print("❌ This should have failed but didn't!")
        print(f"Result: {json_str[:100]}...")
    except (ValueError, TypeError) as e:
        print(f"✅ Expected error: {type(e).__name__}: {str(e)[:100]}")
    print()

    # Test 2: With .replace() (this should work)
    print("="*60)
    print("Test 2: With .replace({pd.NA: None, float('nan'): None}) (FIXED)")
    print("="*60)
    try:
        # Use replace to convert NaN to None
        import numpy as np
        data_fixed = df.replace({np.nan: None}).to_dict('records')
        json_str = json.dumps(data_fixed)
        print("✅ JSON serialization successful!")
        print(f"Result: {json_str}")

        # Parse back to verify
        parsed = json.loads(json_str)
        print(f"\nParsed back:")
        for i, row in enumerate(parsed):
            print(f"  Row {i+1}: {row}")

        # Verify null values
        assert parsed[1]['Name'] is None, "Name should be null"
        assert parsed[1]['LONG'] is None, "LONG should be null"
        assert parsed[1]['LATTs'] is None, "LATTs should be null"
        print("\n✅ Null values verified correctly")

    except (ValueError, TypeError) as e:
        print(f"❌ Unexpected error: {e}")
        raise
    print()

    return True


def test_processing_log_with_nan():
    """Test that processing log handles NaN names correctly"""
    df = pd.DataFrame({
        'Name': ['Location 1', None, 'Location 3'],
        'Region': ['Region 1', 'Region 2', 'Region 3'],
        'Maps link': ['url1', 'url2', 'url3']
    })

    print("="*60)
    print("Test 3: Processing log with NaN names")
    print("="*60)

    processing_log = []

    for idx, row in df.iterrows():
        # Handle NaN in Name column - convert to None for JSON serialization
        row_name = None if pd.isna(row['Name']) else row['Name']

        processing_log.append({
            'row': idx + 1,
            'name': row_name,
            'status': 'success'
        })

    # Try to serialize to JSON
    try:
        json_str = json.dumps(processing_log)
        print("✅ Processing log JSON serialization successful!")
        print(f"Result: {json_str}")

        # Parse back
        parsed = json.loads(json_str)
        print(f"\nParsed back:")
        for entry in parsed:
            print(f"  {entry}")

        # Verify null name
        assert parsed[1]['name'] is None, "Name should be null for row 2"
        print("\n✅ Null name in processing log verified correctly")

    except (ValueError, TypeError) as e:
        print(f"❌ Unexpected error: {e}")
        raise
    print()

    return True


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🧪 Testing JSON Serialization with NaN Values")
    print("="*60 + "\n")

    test_nan_to_json()
    test_processing_log_with_nan()

    print("="*60)
    print("✅ All JSON serialization tests passed!")
    print("="*60 + "\n")
