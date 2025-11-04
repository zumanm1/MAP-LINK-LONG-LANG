# Streamlit App Guide

## Running the Web App

Start the Streamlit app with:

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## Features

- 📤 **Upload Excel files** (.xlsx format)
- 🔄 **Extract coordinates** from Google Maps URLs (no API required)
- 📊 **Preview data** before and after processing
- ⬇️ **Download results** as Excel file
- 📈 **Progress tracking** with real-time status updates
- 📉 **Success metrics** showing processed/failed rows

## Supported URL Formats

The app handles:
- Standard Google Maps URLs: `https://www.google.com/maps/place/Location/@LAT,LNG,17z`
- Query URLs: `https://www.google.com/maps?q=LAT,LNG`
- Shortened URLs: `https://maps.app.goo.gl/...` (automatically resolved)
- Direct coordinates: `LAT,LNG`

## Excel File Requirements

Your input file must have:
- **Name** column: Location name
- **Region** column: Geographic region
- **Map link** or **Maps** column: URL to extract coordinates from
- **Long/LONG** and **Latts/LATTs** columns (optional, will be created/populated)

## Example Workflow

1. Upload your Excel file with map links
2. Preview the data
3. Click "Extract Coordinates"
4. Watch the progress bar
5. Download the processed file with coordinates
