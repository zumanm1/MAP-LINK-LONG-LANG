#!/usr/bin/env python3
"""
Flask Web App for Excel Map Coordinates Converter
Converts map links in Excel files to longitude and latitude coordinates.
"""

from flask import Flask, render_template, request, jsonify, send_file, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import pandas as pd
import io
import os
import uuid
import time
from pathlib import Path
from threading import Lock
from werkzeug.utils import secure_filename
from map_converter import extract_coordinates_from_url

# Get the base directory (cross-platform)
BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = BASE_DIR / 'uploads'
app.config['PROCESSED_FOLDER'] = BASE_DIR / 'processed'

# Ensure upload directories exist (cross-platform with error handling)
try:
    app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)
    app.config['PROCESSED_FOLDER'].mkdir(parents=True, exist_ok=True)
except PermissionError:
    print("⚠️  Warning: Could not create upload directories. They will be created when needed.")
except Exception as e:
    print(f"⚠️  Warning: Directory creation issue: {e}")

# Initialize rate limiter for DoS protection
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Store processing results in memory (in production, use Redis or database)
processing_results = {}
processing_results_lock = Lock()

# Session configuration
SESSION_TTL = 3600  # 1 hour in seconds

# Per-session locks to prevent concurrent processing
session_locks = {}
session_locks_lock = Lock()


def get_session_lock(session_id):
    """Get or create a lock for the given session."""
    with session_locks_lock:
        if session_id not in session_locks:
            session_locks[session_id] = Lock()
        return session_locks[session_id]


def cleanup_old_sessions():
    """Remove sessions older than TTL and their associated files."""
    with processing_results_lock:
        current_time = time.time()
        expired_sessions = [
            session_id for session_id, data in processing_results.items()
            if current_time - data.get('created_at', 0) > SESSION_TTL
        ]

        for session_id in expired_sessions:
            data = processing_results[session_id]

            # Delete uploaded file
            if 'upload_path' in data:
                upload_path = Path(data['upload_path'])
                if upload_path.exists():
                    upload_path.unlink(missing_ok=True)

            # Delete processed file
            if 'processed_path' in data:
                processed_path = Path(data['processed_path'])
                if processed_path.exists():
                    processed_path.unlink(missing_ok=True)

            # Remove from dict
            del processing_results[session_id]

        if expired_sessions:
            print(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")


@app.after_request
def after_request_cleanup(response):
    """Clean up old sessions after each request."""
    cleanup_old_sessions()
    return response


def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'xlsx'


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
@limiter.limit("10 per minute")
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

        # Clean column names: strip whitespace
        df.columns = df.columns.str.strip()

        # Create a case-insensitive column mapping
        column_mapping = {col.lower(): col for col in df.columns}

        # Validate required map column (case-insensitive, flexible names)
        map_column = None
        map_column_options = ['map link', 'maps link', 'maps', 'map', 'map links', 'maps links', 'map_link', 'maps_link', 'maplink', 'mapslink']

        for option in map_column_options:
            if option in column_mapping:
                map_column = column_mapping[option]
                break

        if not map_column:
            # Provide helpful error with actual column names
            actual_columns = ', '.join(f'"{col}"' for col in df.columns)
            return jsonify({
                'error': f'Missing required map column. Looking for: "Map link" or "Maps" (case-insensitive). Found columns: {actual_columns}'
            }), 400

        # Validate other required columns (case-insensitive)
        required_columns = ['name', 'region']
        missing_columns = []

        for req_col in required_columns:
            if req_col not in column_mapping:
                missing_columns.append(req_col.capitalize())

        if missing_columns:
            actual_columns = ', '.join(f'"{col}"' for col in df.columns)
            return jsonify({
                'error': f'Missing required columns: {", ".join(missing_columns)}. Found columns: {actual_columns}'
            }), 400

        # Store original data for preview
        preview_data = df.head(10).to_dict('records')
        preview_columns = df.columns.tolist()

        # Save the full dataframe for processing (cross-platform path)
        filename = secure_filename(file.filename)
        upload_path = app.config['UPLOAD_FOLDER'] / f"{session_id}_{filename}"

        # Ensure upload folder exists (in case it wasn't created at startup)
        upload_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_excel(str(upload_path), index=False)

        # Store session info with timestamp for cleanup
        processing_results[session_id] = {
            'filename': filename,
            'upload_path': str(upload_path),
            'map_column': map_column,
            'total_rows': len(df),
            'status': 'uploaded',
            'created_at': time.time()  # Add timestamp for TTL cleanup
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
@limiter.limit("5 per minute")
def process_file(session_id):
    """Process the uploaded file and extract coordinates."""
    if session_id not in processing_results:
        return jsonify({'error': 'Invalid session ID'}), 400

    # Get session lock to prevent concurrent processing
    session_lock = get_session_lock(session_id)

    # Try to acquire lock (non-blocking) - if already locked, return error
    if not session_lock.acquire(blocking=False):
        return jsonify({'error': 'File is already being processed'}), 400

    try:
        session_info = processing_results[session_id]

        # Mark as processing
        session_info['status'] = 'processing'

        # Read the uploaded file
        df = pd.read_excel(session_info['upload_path'])

        # Clean column names: strip whitespace
        df.columns = df.columns.str.strip()

        map_column = session_info['map_column']

        # Determine longitude and latitude column names (case-insensitive, flexible)
        column_mapping_lower = {col.lower(): col for col in df.columns}

        # Try to find existing Long column
        long_column = None
        for option in ['long', 'longitude', 'lng']:
            if option in column_mapping_lower:
                long_column = column_mapping_lower[option]
                break

        # If not found, create new column
        if not long_column:
            long_column = 'Long'
            df[long_column] = None

        # Try to find existing Lat column
        lat_column = None
        for option in ['latts', 'latt', 'lat', 'latitude']:
            if option in column_mapping_lower:
                lat_column = column_mapping_lower[option]
                break

        # If not found, create new column
        if not lat_column:
            lat_column = 'Latts'
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

        # Ensure processed folder exists (in case it wasn't created at startup)
        output_path.parent.mkdir(parents=True, exist_ok=True)

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
    finally:
        # Always release the lock
        session_lock.release()


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
