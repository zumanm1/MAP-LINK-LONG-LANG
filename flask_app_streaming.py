#!/usr/bin/env python3
"""
Flask Web App with Real-Time Progress Streaming
Adds Server-Sent Events (SSE) for live progress updates to the UI
"""

from flask import Flask, render_template, request, jsonify, send_file, session, Response, stream_with_context
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import pandas as pd
import numpy as np
import io
import os
import uuid
import time
import logging
import json
from pathlib import Path
from threading import Lock, Thread
from werkzeug.utils import secure_filename
from map_converter import extract_coordinates_from_url
import signal as signal_module
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
SESSION_TTL = 7200  # 2 hours in seconds (increased for better UX)

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
            age = current_time - data.get('created_at', 0)

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

            # Delete session lock
            with session_locks_lock:
                if session_id in session_locks:
                    del session_locks[session_id]

            logger.info(f"🧹 Cleaned up expired session {session_id[:8]}... (age: {age/60:.1f} minutes)")

        if expired_sessions:
            logger.info(f"✅ Total cleanup: {len(expired_sessions)} expired sessions removed")


@app.after_request
def after_request_cleanup(response):
    """Clean up old sessions after each request."""
    cleanup_old_sessions()
    return response


def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'xlsx'


@contextmanager
def timeout_context(seconds):
    """Context manager for timeout using signal (Unix-like systems only)."""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timeout after {seconds} seconds")

    # Only use signal on Unix-like systems
    if hasattr(signal_module, 'SIGALRM'):
        old_handler = signal_module.signal(signal_module.SIGALRM, timeout_handler)
        signal_module.alarm(seconds)
        try:
            yield
        finally:
            signal_module.alarm(0)
            signal_module.signal(signal_module.SIGALRM, old_handler)
    else:
        # On Windows, just yield without timeout (or use threading.Timer)
        yield


def process_single_url(map_link, max_attempts=3, retry_delay=2, url_timeout=180):
    """
    Process a single URL with timeout and retry logic.

    Args:
        map_link: The map URL to process
        max_attempts: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        url_timeout: Timeout per attempt in seconds (3 minutes)

    Returns:
        tuple: (lng, lat, attempt_number, error_message)
    """
    lng, lat = None, None
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            with timeout_context(url_timeout):
                lng, lat = extract_coordinates_from_url(str(map_link))

            if lng is not None and lat is not None:
                return lng, lat, attempt, None
            else:
                last_error = "Could not extract coordinates from URL"
                if attempt < max_attempts:
                    time.sleep(retry_delay)

        except TimeoutError as e:
            last_error = f"Timeout: URL took longer than {url_timeout} seconds to process"
            if attempt < max_attempts:
                time.sleep(retry_delay)

        except Exception as e:
            last_error = str(e)
            if attempt < max_attempts:
                time.sleep(retry_delay)

    return None, None, max_attempts, last_error


def process_file_streaming(session_id):
    """
    Process file and yield progress updates for streaming.
    Each yield sends a Server-Sent Event to the client.
    """
    try:
        session_info = processing_results[session_id]

        # Read the uploaded file
        df = pd.read_excel(session_info['upload_path'])
        df.columns = df.columns.str.strip()

        map_column = session_info['map_column']

        # Determine longitude and latitude column names
        column_mapping_lower = {col.lower(): col for col in df.columns}

        long_column = None
        for option in ['long', 'longitude', 'lng']:
            if option in column_mapping_lower:
                long_column = column_mapping_lower[option]
                break
        if not long_column:
            long_column = 'LONG'
            df[long_column] = None

        lat_column = None
        for option in ['latts', 'latt', 'lat', 'latitude']:
            if option in column_mapping_lower:
                lat_column = column_mapping_lower[option]
                break
        if not lat_column:
            lat_column = 'LATTs'
            df[lat_column] = None

        if 'Comments' not in df.columns:
            df['Comments'] = None

        successful = 0
        failed = 0
        skipped = 0
        processing_log = []
        total_rows = len(df)

        # Send initial status
        yield f"data: {json.dumps({'type': 'start', 'total_rows': total_rows})}\n\n"

        # Process each row with 3-minute timeout
        for idx, row in df.iterrows():
            map_link = row[map_column]
            row_name = None if pd.isna(row['Name']) else row['Name']
            row_display = row_name if row_name else f"Row {idx + 1}"
            progress = ((idx + 1) / total_rows) * 100

            # Send progress update
            yield f"data: {json.dumps({'type': 'progress', 'row': idx + 1, 'total': total_rows, 'progress': progress, 'name': row_display})}\n\n"

            # Skip rows with missing map links
            if pd.isna(map_link) or str(map_link).strip() == '':
                skipped += 1
                df.at[idx, 'Comments'] = 'Skipped: No map link provided'

                yield f"data: {json.dumps({'type': 'log', 'level': 'warning', 'message': f'Row {idx + 1}: Skipped - No map link'})}\n\n"

                processing_log.append({
                    'row': idx + 1,
                    'name': row_name,
                    'status': 'skipped',
                    'reason': 'No map link provided',
                    'progress': progress
                })
                continue

            # Process with 3-minute timeout (180 seconds) and 3 attempts
            yield f"data: {json.dumps({'type': 'log', 'level': 'info', 'message': f'Row {idx + 1}: Processing {row_display}...'})}\n\n"

            lng, lat, attempts, error = process_single_url(
                map_link,
                max_attempts=3,
                retry_delay=2,
                url_timeout=180  # 3 minutes per attempt
            )

            if lng is not None and lat is not None:
                df.at[idx, long_column] = lng
                df.at[idx, lat_column] = lat
                df.at[idx, 'Comments'] = 'Success'
                successful += 1

                yield f"data: {json.dumps({'type': 'log', 'level': 'success', 'message': f'Row {idx + 1}: Success - Lng={lng:.4f}, Lat={lat:.4f} (Attempt {attempts})'})}\n\n"

                processing_log.append({
                    'row': idx + 1,
                    'name': row_name,
                    'status': 'success',
                    'lng': lng,
                    'lat': lat,
                    'attempts': attempts,
                    'map_link': str(map_link)[:50] + '...' if len(str(map_link)) > 50 else str(map_link),
                    'progress': progress
                })
            else:
                failed += 1
                comment = f"Failed after {attempts} attempts: {error}"
                df.at[idx, 'Comments'] = comment

                yield f"data: {json.dumps({'type': 'log', 'level': 'error', 'message': f'Row {idx + 1}: Failed - {error}'})}\n\n"

                processing_log.append({
                    'row': idx + 1,
                    'name': row_name,
                    'status': 'failed',
                    'reason': error,
                    'attempts': attempts,
                    'map_link': str(map_link)[:50] + '...' if len(str(map_link)) > 50 else str(map_link),
                    'progress': progress
                })

        # Save processed file
        output_filename = f"processed_{session_info['filename']}"
        output_path = app.config['PROCESSED_FOLDER'] / f"{session_id}_{output_filename}"
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
        session_info['processed_data'] = df.replace({np.nan: None}).to_dict('records')
        session_info['processed_columns'] = df.columns.tolist()

        # Send completion
        yield f"data: {json.dumps({'type': 'complete', 'successful': successful, 'failed': failed, 'skipped': skipped, 'total_rows': total_rows, 'processing_log': processing_log, 'processed_data': session_info['processed_data'], 'processed_columns': session_info['processed_columns']})}\n\n"

    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        session_info['status'] = 'error'
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


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
        df.columns = df.columns.str.strip()
        column_mapping = {col.lower(): col for col in df.columns}

        # Validate required map column
        map_column = None
        map_column_options = ['map link', 'maps link', 'maps', 'map', 'map links', 'maps links', 'map_link', 'maps_link', 'maplink', 'mapslink']

        for option in map_column_options:
            if option in column_mapping:
                map_column = column_mapping[option]
                break

        if not map_column:
            actual_columns = ', '.join(f'"{col}"' for col in df.columns)
            return jsonify({
                'error': f'Missing required map column. Looking for: "Map link" or "Maps" (case-insensitive). Found columns: {actual_columns}'
            }), 400

        # Validate other required columns
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
        preview_data = df.head(10).replace({np.nan: None}).to_dict('records')
        preview_columns = df.columns.tolist()

        # Save the full dataframe for processing
        filename = secure_filename(file.filename)
        upload_path = app.config['UPLOAD_FOLDER'] / f"{session_id}_{filename}"
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(str(upload_path), index=False)

        # Store session info with timestamp for cleanup
        processing_results[session_id] = {
            'filename': filename,
            'upload_path': str(upload_path),
            'map_column': map_column,
            'total_rows': len(df),
            'status': 'uploaded',
            'created_at': time.time()
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


@app.route('/process-stream/<session_id>')
def process_stream(session_id):
    """Stream processing progress using Server-Sent Events (SSE)."""
    if session_id not in processing_results:
        return jsonify({
            'error': 'Invalid session ID. Your session may have expired. Please upload the file again.'
        }), 400

    # Mark as processing
    processing_results[session_id]['status'] = 'processing'
    processing_results[session_id]['created_at'] = time.time()

    return Response(
        stream_with_context(process_file_streaming(session_id)),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


@app.route('/download/<session_id>')
def download_file(session_id):
    """Download the processed file."""
    if session_id not in processing_results:
        return jsonify({
            'error': 'Invalid session ID. Your session may have expired. Please upload and process the file again.'
        }), 404

    session_info = processing_results[session_id]
    session_info['created_at'] = time.time()

    if session_info['status'] != 'completed':
        return jsonify({'error': 'File has not been processed yet'}), 400

    try:
        # Resolve and validate path to prevent path traversal attacks
        output_path = Path(session_info['output_path']).resolve()
        processed_folder = app.config['PROCESSED_FOLDER'].resolve()

        # Check if path is within allowed directory
        try:
            output_path.relative_to(processed_folder)
        except ValueError:
            logger.error(f"🚨 Path traversal attempt blocked: {output_path}")
            return jsonify({'error': 'Invalid file path'}), 403

        # Verify file exists
        if not output_path.exists():
            return jsonify({'error': 'File not found'}), 404

        # Verify it's a file (not a directory)
        if not output_path.is_file():
            return jsonify({'error': 'Invalid file'}), 400

        return send_file(
            str(output_path),
            as_attachment=True,
            download_name=session_info['output_filename'],
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': f'Error downloading file: {str(e)}'}), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
