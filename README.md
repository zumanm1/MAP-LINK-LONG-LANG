# Excel Map Coordinates Converter

A Python tool that converts map links in Excel files to longitude and latitude coordinates.

## Features

- Extracts coordinates from various Google Maps link formats
- Processes Excel files with batch conversion
- Comprehensive error handling and logging
- Validates input data and provides detailed feedback
- Preserves original data while adding coordinate columns

## Requirements

- Python 3.11
- pandas
- openpyxl
- requests
- pytest (for testing)

## Installation

1. Clone or navigate to the project directory:
```bash
cd /Users/macbook/Projects/excel-map-coordinates-converter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python map_converter.py <input_excel_file> <output_excel_file>
```

### Example

```bash
python map_converter.py input.xlsx output.xlsx
```

## Input File Format

Your input Excel file must contain the following columns:

- **Name**: Site or location name
- **Region**: Geographic region
- **Map link**: URL to the map location (Google Maps format)
- **Long**: (Optional) Longitude column (will be populated)
- **Latts**: (Optional) Latitude column (will be populated)

### Example Input

| Name         | Region        | Map link                                                      | Long | Latts |
|--------------|---------------|---------------------------------------------------------------|------|-------|
| Sandton City | Johannesburg  | https://www.google.com/maps/place/Sandton+City/@-26.108204,28.0527061,17z |      |       |

## Output File Format

The output Excel file will contain all original columns with the **Long** and **Latts** columns populated:

| Name         | Region        | Map link                                                      | Long      | Latts      |
|--------------|---------------|---------------------------------------------------------------|-----------|------------|
| Sandton City | Johannesburg  | https://www.google.com/maps/place/Sandton+City/@-26.108204,28.0527061,17z | 28.052706 | -26.108204 |

## Supported Map Link Formats

The tool supports various Google Maps URL formats:

1. `https://www.google.com/maps/place/Location/@LAT,LNG,17z`
2. `https://www.google.com/maps?q=LAT,LNG`
3. `https://maps.google.com/?q=LAT,LNG`
4. Direct coordinate pairs: `LAT,LNG`

## Testing

### Run the Test Example

A test file with Sandton City is included:

```bash
python map_converter.py test_input.xlsx test_output.xlsx
```

Expected output:
- Longitude: 28.052706
- Latitude: -26.108204

### Run Unit Tests

```bash
pytest tests/
```

## Logging

The script provides detailed logging output:
- INFO: Successful operations and progress
- WARNING: Non-critical issues (e.g., missing map links)
- ERROR: Critical failures

## Error Handling

The script handles:
- Missing input files
- Invalid Excel formats
- Missing required columns
- Invalid or unparseable map links
- Empty or malformed data

## Project Structure

```
excel-map-coordinates-converter/
├── map_converter.py       # Main conversion script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── tests/                # Test directory
├── test_input.xlsx       # Sample input file
└── test_output.xlsx      # Sample output file
```

## Future Enhancements

- Support for additional map services (Apple Maps, Bing Maps)
- Batch processing of multiple files
- GUI interface
- API integration for geocoding location names

## License

MIT License

## Author

Created for batch conversion of map links to coordinates.
