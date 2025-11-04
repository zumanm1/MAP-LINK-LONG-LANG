#!/usr/bin/env python3
"""
Flask Web App for Excel Map Coordinates Converter
Converts map links in Excel files to longitude and latitude coordinates.
"""

from flask import Flask, render_template, request, jsonify, send_file, session
import pandas as pd
import io
import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
from map_converter import extract_coordinates_from_url

# Get the base directory (cross-platform)
BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = BASE_DIR / 'uploads'
app.config['PROCESSED_FOLDER'] = BASE_DIR / 'processed'

# Ensure upload directories exist (cross-platform)
app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)
app.config['PROCESSED_FOLDER'].mkdir(parents=True, exist_ok=True)

# Store processing results in memory (in production, use Redis or database)
processing_results = {}


def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'xlsx'


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and initial validation."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Only .xlsx files are allowed'}), 400

    try:
        # Generate unique session ID for this upload
        session_id = str(uuid.uuid4())

        # Read the uploaded file
        df = pd.read_excel(file)

        # Validate required columns
        map_column = None
        if 'Map link' in df.columns:
            map_column = 'Map link'
        elif 'Maps' in df.columns:
            map_column = 'Maps'
        else:
            return jsonify({
                'error': 'Missing required map column: "Map link" or "Maps"'
            }), 400

        required_columns = ['Name', 'Region']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({
                'error': f'Missing required columns: {", ".join(missing_columns)}'
            }), 400

        # Store original data for preview
        preview_data = df.head(10).to_dict('records')
        preview_columns = df.columns.tolist()

        # Save the full dataframe for processing (cross-platform path)
        filename = secure_filename(file.filename)
        upload_path = app.config['UPLOAD_FOLDER'] / f"{session_id}_{filename}"
        df.to_excel(str(upload_path), index=False)

        # Store session info
        processing_results[session_id] = {
            'filename': filename,
            'upload_path': str(upload_path),
            'map_column': map_column,
            'total_rows': len(df),
            'status': 'uploaded'
        }

        return jsonify({
            'success': True,
            'session_id': session_id,
            'preview_data': preview_data,
            'preview_columns': preview_columns,
            'total_rows': len(df),
            'map_column': map_column
        })

    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 400


@app.route('/process/<session_id>', methods=['POST'])
def process_file(session_id):
    """Process the uploaded file and extract coordinates."""
    if session_id not in processing_results:
        return jsonify({'error': 'Invalid session ID'}), 400

    session_info = processing_results[session_id]

    if session_info['status'] == 'processing':
        return jsonify({'error': 'File is already being processed'}), 400

    try:
        # Mark as processing
        session_info['status'] = 'processing'

        # Read the uploaded file
        df = pd.read_excel(session_info['upload_path'])
        map_column = session_info['map_column']

        # Determine longitude and latitude column names
        long_column = 'Long' if 'Long' in df.columns else 'LONG'
        if long_column not in df.columns:
            df[long_column] = None

        lat_column = 'Latts' if 'Latts' in df.columns else 'LATTs'
        if lat_column not in df.columns:
            df[lat_column] = None

        successful = 0
        failed = 0
        skipped = 0
        processing_log = []

        # Process each row
        for idx, row in df.iterrows():
            map_link = row[map_column]

            # Skip rows with missing map links (don't process)
            if pd.isna(map_link) or str(map_link).strip() == '':
                skipped += 1
                processing_log.append({
                    'row': idx + 1,
                    'name': row['Name'],
                    'status': 'skipped',
                    'reason': 'No map link provided'
                })
                continue

            # Process rows with map links
            lng, lat = extract_coordinates_from_url(str(map_link))
            if lng is not None and lat is not None:
                df.at[idx, long_column] = lng
                df.at[idx, lat_column] = lat
                successful += 1
                processing_log.append({
                    'row': idx + 1,
                    'name': row['Name'],
                    'status': 'success',
                    'lng': lng,
                    'lat': lat,
                    'map_link': str(map_link)[:50] + '...' if len(str(map_link)) > 50 else str(map_link)
                })
            else:
                failed += 1
                processing_log.append({
                    'row': idx + 1,
                    'name': row['Name'],
                    'status': 'failed',
                    'reason': 'Could not extract coordinates from URL',
                    'map_link': str(map_link)[:50] + '...' if len(str(map_link)) > 50 else str(map_link)
                })

        # Save processed file (cross-platform path)
        output_filename = f"processed_{session_info['filename']}"
        output_path = app.config['PROCESSED_FOLDER'] / f"{session_id}_{output_filename}"
        df.to_excel(str(output_path), index=False)

        # Update session info
        session_info['status'] = 'completed'
        session_info['output_path'] = str(output_path)
        session_info['output_filename'] = output_filename
        session_info['successful'] = successful
        session_info['failed'] = failed
        session_info['skipped'] = skipped
        session_info['processing_log'] = processing_log
        session_info['processed_data'] = df.to_dict('records')
        session_info['processed_columns'] = df.columns.tolist()

        return jsonify({
            'success': True,
            'total_rows': len(df),
            'successful': successful,
            'failed': failed,
            'skipped': skipped,
            'processing_log': processing_log,
            'processed_data': session_info['processed_data'],
            'processed_columns': session_info['processed_columns']
        })

    except Exception as e:
        session_info['status'] = 'error'
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500


@app.route('/download/<session_id>')
def download_file(session_id):
    """Download the processed file."""
    if session_id not in processing_results:
        return jsonify({'error': 'Invalid session ID'}), 404

    session_info = processing_results[session_id]

    if session_info['status'] != 'completed':
        return jsonify({'error': 'File has not been processed yet'}), 400

    try:
        return send_file(
            session_info['output_path'],
            as_attachment=True,
            download_name=session_info['output_filename'],
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({'error': f'Error downloading file: {str(e)}'}), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
