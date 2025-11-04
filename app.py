#!/usr/bin/env python3
"""
Streamlit Web App for Excel Map Coordinates Converter
Converts map links in Excel files to longitude and latitude coordinates.
"""

import streamlit as st
import pandas as pd
import io
import time
import logging
from pathlib import Path
from map_converter import extract_coordinates_from_url, validate_coordinates

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Excel Map Coordinates Converter",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #1e4620;
        border: 1px solid #4CAF50;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #4a1e1e;
        border: 1px solid #f44336;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #1e3a4a;
        border: 1px solid: #2196F3;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processed_df' not in st.session_state:
    st.session_state.processed_df = None
if 'processing_log' not in st.session_state:
    st.session_state.processing_log = []
if 'statistics' not in st.session_state:
    st.session_state.statistics = None


def process_excel_file(uploaded_file):
    """Process uploaded Excel file and extract coordinates."""
    try:
        # Read Excel file
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        # Column mapping
        column_mapping = {col.lower(): col for col in df.columns}

        # Find map column
        map_column = None
        map_column_options = ['map link', 'maps link', 'maps', 'map']
        for option in map_column_options:
            if option in column_mapping:
                map_column = column_mapping[option]
                break

        if not map_column:
            st.error(f"❌ Missing required column. Looking for: 'Map link', 'Maps', or 'Map'. Found: {', '.join(df.columns)}")
            return None, []

        # Find or create LONG/LAT columns
        long_column = None
        for option in ['long', 'longitude', 'lng']:
            if option in column_mapping:
                long_column = column_mapping[option]
                break
        if not long_column:
            long_column = 'LONG'
            df[long_column] = None

        lat_column = None
        for option in ['latts', 'latt', 'lat', 'latitude']:
            if option in column_mapping:
                lat_column = column_mapping[option]
                break
        if not lat_column:
            lat_column = 'LATTs'
            df[lat_column] = None

        name_column = column_mapping.get('name', 'Name')

        if 'Comments' not in df.columns:
            df['Comments'] = None

        # Processing
        total_rows = len(df)
        processing_log = []
        successful = 0
        failed = 0
        skipped = 0

        # Progress bar and status
        progress_bar = st.progress(0)
        status_text = st.empty()
        log_container = st.expander("📋 Processing Log", expanded=True)

        for idx, row in df.iterrows():
            map_link = row[map_column]
            row_name = row.get(name_column, f"Row {idx + 1}")
            progress = (idx + 1) / total_rows

            status_text.text(f"Processing {idx + 1}/{total_rows}: {row_name}")
            progress_bar.progress(progress)

            # Skip blank rows
            if pd.isna(map_link) or str(map_link).strip() == '':
                df.at[idx, 'Comments'] = 'Skipped: No map link provided'
                processing_log.append({
                    'row': idx + 1,
                    'name': row_name,
                    'status': '⏭️ Skipped',
                    'message': 'No map link provided',
                    'map_link': ''
                })
                skipped += 1
                continue

            # Extract coordinates
            lng, lat = extract_coordinates_from_url(str(map_link))

            if lng is not None and lat is not None:
                df.at[idx, long_column] = lng
                df.at[idx, lat_column] = lat
                df.at[idx, 'Comments'] = 'Success'
                successful += 1

                processing_log.append({
                    'row': idx + 1,
                    'name': row_name,
                    'status': '✅ Success',
                    'message': f'Lng: {lng:.6f}, Lat: {lat:.6f}',
                    'map_link': str(map_link)[:50] + '...' if len(str(map_link)) > 50 else str(map_link)
                })
            else:
                df.at[idx, 'Comments'] = 'Failed: Could not extract coordinates'
                failed += 1

                processing_log.append({
                    'row': idx + 1,
                    'name': row_name,
                    'status': '❌ Failed',
                    'message': 'Could not extract coordinates',
                    'map_link': str(map_link)[:50] + '...' if len(str(map_link)) > 50 else str(map_link)
                })

            # Update log display
            with log_container:
                log_df = pd.DataFrame(processing_log)
                st.dataframe(log_df, use_container_width=True, height=300)

        progress_bar.progress(1.0)
        status_text.text("✅ Processing complete!")

        # Statistics
        statistics = {
            'total': total_rows,
            'successful': successful,
            'failed': failed,
            'skipped': skipped
        }

        return df, processing_log, statistics

    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        logger.error(f"Processing error: {str(e)}")
        return None, [], None


def main():
    """Main Streamlit app."""

    # Header
    st.title("🗺️ Excel Map Coordinates Converter")
    st.markdown("Convert Google Maps URLs in Excel files to longitude and latitude coordinates")

    # Sidebar
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This tool extracts GPS coordinates from Google Maps URLs in Excel files.

        **Supported URL formats:**
        - Standard place URLs
        - Query parameter URLs
        - Shortened URLs (goo.gl)
        - Search URLs
        - Regional domains (.co.za, etc.)
        - URL-encoded coordinates

        **Requirements:**
        - Excel file (.xlsx)
        - Column named "Map link" or "Maps"
        - Valid Google Maps URLs
        """)

        st.header("📊 Statistics")
        if st.session_state.statistics:
            stats = st.session_state.statistics
            st.metric("Total Rows", stats['total'])
            st.metric("✅ Successful", stats['successful'])
            st.metric("❌ Failed", stats['failed'])
            st.metric("⏭️ Skipped", stats['skipped'])

            if stats['total'] > 0:
                success_rate = (stats['successful'] / stats['total']) * 100
                st.progress(success_rate / 100)
                st.caption(f"Success Rate: {success_rate:.1f}%")

    # Main content
    tab1, tab2, tab3 = st.tabs(["📁 Upload & Process", "📊 Results", "📋 Processing Log"])

    with tab1:
        st.header("Upload Excel File")

        uploaded_file = st.file_uploader(
            "Choose an Excel file (.xlsx)",
            type=['xlsx'],
            help="Upload an Excel file with a column named 'Map link' or 'Maps'"
        )

        if uploaded_file is not None:
            # Show file info
            st.success(f"✅ File uploaded: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

            # Preview
            with st.expander("👁️ Preview Input Data"):
                try:
                    preview_df = pd.read_excel(uploaded_file)
                    st.dataframe(preview_df.head(10), use_container_width=True)
                    st.caption(f"Showing first 10 of {len(preview_df)} rows")

                    # Reset file pointer
                    uploaded_file.seek(0)
                except Exception as e:
                    st.error(f"Error previewing file: {str(e)}")

            # Process button
            if st.button("🚀 Process File", type="primary"):
                with st.spinner("Processing..."):
                    result_df, log, stats = process_excel_file(uploaded_file)

                    if result_df is not None:
                        st.session_state.processed_df = result_df
                        st.session_state.processing_log = log
                        st.session_state.statistics = stats

                        st.success("✅ Processing complete! View results in the 'Results' tab.")
                        st.balloons()

    with tab2:
        st.header("Processing Results")

        if st.session_state.processed_df is not None:
            df = st.session_state.processed_df

            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                filter_option = st.selectbox(
                    "Filter results:",
                    ["All rows", "Successful only", "Failed only", "Skipped only"]
                )

            # Apply filter
            if filter_option == "Successful only":
                filtered_df = df[df['Comments'] == 'Success']
            elif filter_option == "Failed only":
                filtered_df = df[df['Comments'].str.startswith('Failed', na=False)]
            elif filter_option == "Skipped only":
                filtered_df = df[df['Comments'].str.startswith('Skipped', na=False)]
            else:
                filtered_df = df

            # Display results
            st.dataframe(filtered_df, use_container_width=True, height=500)
            st.caption(f"Showing {len(filtered_df)} of {len(df)} rows")

            # Download buttons
            st.subheader("📥 Download Results")

            col1, col2, col3 = st.columns(3)

            with col1:
                # Download all results
                buffer = io.BytesIO()
                df.to_excel(buffer, index=False, engine='openpyxl')
                buffer.seek(0)

                st.download_button(
                    label="📥 Download All Results",
                    data=buffer,
                    file_name="processed_output.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            with col2:
                # Download failed rows
                failed_df = df[df['Comments'].str.startswith('Failed', na=False)]
                if len(failed_df) > 0:
                    buffer_failed = io.BytesIO()
                    failed_df.to_excel(buffer_failed, index=False, engine='openpyxl')
                    buffer_failed.seek(0)

                    st.download_button(
                        label=f"📥 Download Failed ({len(failed_df)})",
                        data=buffer_failed,
                        file_name="processed_output_failed.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.info("No failed rows")

            with col3:
                # Download skipped rows
                skipped_df = df[df['Comments'].str.startswith('Skipped', na=False)]
                if len(skipped_df) > 0:
                    buffer_skipped = io.BytesIO()
                    skipped_df.to_excel(buffer_skipped, index=False, engine='openpyxl')
                    buffer_skipped.seek(0)

                    st.download_button(
                        label=f"📥 Download Skipped ({len(skipped_df)})",
                        data=buffer_skipped,
                        file_name="processed_output_skipped.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.info("No skipped rows")

        else:
            st.info("👆 Upload and process a file to see results here")

    with tab3:
        st.header("Processing Log")

        if st.session_state.processing_log:
            log_df = pd.DataFrame(st.session_state.processing_log)

            # Filter log
            status_filter = st.multiselect(
                "Filter by status:",
                options=['✅ Success', '❌ Failed', '⏭️ Skipped'],
                default=['✅ Success', '❌ Failed', '⏭️ Skipped']
            )

            filtered_log = log_df[log_df['status'].isin(status_filter)]

            st.dataframe(filtered_log, use_container_width=True, height=500)
            st.caption(f"Showing {len(filtered_log)} of {len(log_df)} log entries")
        else:
            st.info("👆 Process a file to see the detailed log here")

    # Footer
    st.markdown("---")
    st.markdown(
        "🤖 Generated with [Claude Code](https://claude.com/claude-code) | "
        "Co-Authored-By: Claude <noreply@anthropic.com>"
    )


if __name__ == "__main__":
    main()
