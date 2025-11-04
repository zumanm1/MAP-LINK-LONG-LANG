# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a Python utility that converts Google Maps URLs to longitude/latitude coordinates in Excel files. The tool processes batch Excel files, extracting coordinates from various map link formats and populating coordinate columns.

## Development Commands

### Setup

```bash
# Install dependencies (Python 3.11 required)
pip install -r requirements.txt
```

### Running the Tool

**Command Line**:
```bash
# Basic usage
python map_converter.py <input_excel_file> <output_excel_file>

# Example with test files
python map_converter.py test_input.xlsx test_output.xlsx
```

**Streamlit Web App**:
```bash
# Start the web interface
streamlit run app.py

# Opens at http://localhost:8501
# - Upload Excel file via browser
# - Extract coordinates with progress tracking
# - Download processed file
```

### Testing

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_map_converter.py

# Run specific test class
pytest tests/test_map_converter.py::TestExtractCoordinates

# Run specific test case
pytest tests/test_map_converter.py::TestExtractCoordinates::test_google_maps_place_format

# Run tests matching a pattern
pytest tests/ -k "google_maps"
```

## Architecture

### Core Design Pattern

The codebase follows a two-function architecture:

1. **`extract_coordinates_from_url(map_link: str)`**: Pure extraction logic that parses various Google Maps URL formats using regex patterns. Returns `(longitude, latitude)` tuple or `(None, None)` on failure.

2. **`process_excel_file(input_file: str, output_file: str)`**: Orchestrates the full pipeline - reads Excel, validates schema, applies extraction to each row, and writes output.

This separation enables:
- Unit testing of extraction logic independently (see `TestExtractCoordinates` class)
- Different front-ends (CLI, API, GUI) to reuse the core extraction function
- Clear error boundaries between parsing and I/O operations

### Coordinate Extraction Strategy

The `extract_coordinates_from_url()` function uses 4 sequential regex patterns to handle different Google Maps URL formats:

1. **`@lat,lng` format**: `@(-?\d+\.\d+),(-?\d+\.\d+)` - Matches place URLs like `/maps/place/Location/@-26.108,28.052,17z`
2. **`q=lat,lng` format**: `[?&]q=(-?\d+\.\d+),(-?\d+\.\d+)` - Matches query URLs like `/maps?q=-26.108,28.052`
3. **Place-specific format**: `/place/[^/]+/@(-?\d+\.\d+),(-?\d+\.\d+)` - Explicit place extraction
4. **Direct coordinates**: `(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)` - Handles bare coordinate pairs with automatic lat/lng determination based on value ranges (-90 to 90 for latitude, -180 to 180 for longitude)

The patterns are tried in sequence; first match wins. This cascading strategy handles shortened URLs, query parameters, and various Google Maps format variations.

### Excel Schema Requirements

**Input columns (required)**:
- `Name`: Location identifier
- `Region`: Geographic region
- `Map link`: URL string to parse

**Output columns (populated)**:
- `Long`: Longitude coordinate (float)
- `Latts`: Latitude coordinate (float)

The processor preserves all original columns and creates `Long`/`Latts` columns if they don't exist. Each row is logged individually with success/failure status.

## Key Implementation Details

- **Type safety**: Uses type hints throughout (`Tuple[Optional[float], Optional[float]]`)
- **Logging levels**: INFO for success, WARNING for missing/invalid data, ERROR for critical failures
- **Coordinate validation**: Implements range checking (latitude: -90 to 90, longitude: -180 to 180) for ambiguous coordinate pairs
- **Error handling**: Graceful degradation - individual row failures don't halt batch processing
- **Testing approach**: Comprehensive unit tests covering format variations, edge cases (empty, None, malformed), and real-world examples with geographic validation
