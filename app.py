#!/usr/bin/env python3
"""
Streamlit Web App for Excel Map Coordinates Converter
Converts map links in Excel files to longitude and latitude coordinates.
"""

import streamlit as st
import pandas as pd
import io
from map_converter import extract_coordinates_from_url

st.set_page_config(
    page_title="Map Coordinates Converter",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Excel Map Coordinates Converter")
st.markdown("""
Upload an Excel file with map links and download it with extracted longitude and latitude coordinates.
No API keys required - processes Google Maps URLs directly.
""")

# File uploader
uploaded_file = st.file_uploader(
    "Upload Excel file (.xlsx)",
    type=['xlsx'],
    help="File must contain 'Name', 'Region', and either 'Map link' or 'Maps' columns"
)

if uploaded_file is not None:
    try:
        # Read the uploaded file
        df = pd.read_excel(uploaded_file)
        
        st.subheader("📄 Input File Preview")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Validate required columns
        map_column = None
        if 'Map link' in df.columns:
            map_column = 'Map link'
        elif 'Maps' in df.columns:
            map_column = 'Maps'
        else:
            st.error("❌ Missing required map column: 'Map link' or 'Maps'")
            st.stop()
        
        required_columns = ['Name', 'Region']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"❌ Missing required columns: {missing_columns}")
            st.stop()
        
        # Determine longitude and latitude column names
        long_column = 'Long' if 'Long' in df.columns else 'LONG'
        if long_column not in df.columns:
            df[long_column] = None
        
        lat_column = 'Latts' if 'Latts' in df.columns else 'LATTs'
        if lat_column not in df.columns:
            df[lat_column] = None
        
        # Process button
        if st.button("🔄 Extract Coordinates", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            successful = 0
            failed = 0
            skipped = 0

            # Process each row
            for idx, row in df.iterrows():
                progress = (idx + 1) / len(df)
                progress_bar.progress(progress)
                status_text.text(f"Processing row {idx + 1}/{len(df)}: {row['Name']}")

                map_link = row[map_column]

                # Skip rows with missing map links (don't process)
                if pd.isna(map_link) or str(map_link).strip() == '':
                    skipped += 1
                    continue

                # Process rows with map links
                lng, lat = extract_coordinates_from_url(str(map_link))
                if lng is not None and lat is not None:
                    df.at[idx, long_column] = lng
                    df.at[idx, lat_column] = lat
                    successful += 1
                else:
                    failed += 1

            progress_bar.empty()
            status_text.empty()

            # Display results
            st.success(f"✅ Processing complete! Successfully processed {successful}/{len(df)} rows")

            if failed > 0:
                st.warning(f"⚠️ Failed to extract coordinates for {failed} rows")

            if skipped > 0:
                st.info(f"ℹ️ Skipped {skipped} rows with missing map links")
            
            # Show processed data
            st.subheader("📊 Processed Data")
            st.dataframe(df, use_container_width=True)
            
            # Download button
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            st.download_button(
                label="⬇️ Download Processed File",
                data=output.getvalue(),
                file_name="coordinates_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Show statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Rows", len(df))
            with col2:
                st.metric("Successful", successful)
            with col3:
                st.metric("Failed", failed)
            with col4:
                st.metric("Skipped", skipped)
    
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")

else:
    # Show instructions when no file is uploaded
    st.info("👆 Please upload an Excel file to get started")
    
    st.subheader("📋 Requirements")
    st.markdown("""
    Your Excel file must contain:
    - **Name**: Site or location name
    - **Region**: Geographic region
    - **Map link** or **Maps**: URL to the map location
    - **Long** or **LONG**: (Optional) Longitude column - will be populated
    - **Latts** or **LATTs**: (Optional) Latitude column - will be populated
    """)
    
    st.subheader("🔗 Supported URL Formats")
    st.markdown("""
    - `https://www.google.com/maps/place/Location/@LAT,LNG,17z`
    - `https://www.google.com/maps?q=LAT,LNG`
    - `https://maps.app.goo.gl/...` (shortened URLs)
    - Direct coordinate pairs: `LAT,LNG`
    """)
    
    st.subheader("📝 Example")
    example_df = pd.DataFrame({
        'Name': ['Sandton City'],
        'Region': ['Johannesburg'],
        'Maps': ['https://maps.app.goo.gl/baixEU9UxYHX8Yox7'],
        'LONG': [''],
        'LATTs': ['']
    })
    st.dataframe(example_df, use_container_width=True)
