#!/usr/bin/env python3
"""
Test Bug #2: Path Traversal Vulnerability
Tests that download endpoint validates file paths are within allowed directory.
"""

import pytest
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from flask_app import app, processing_results, processing_results_lock


class TestPathTraversal:
    """Test path traversal vulnerability is fixed in download endpoint."""

    @pytest.fixture
    def client(self):
        """Create Flask test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    @pytest.fixture
    def valid_session(self):
        """Create a valid session with a processed file."""
        session_id = "test-session-valid"

        # Create test processed file
        processed_folder = app.config['PROCESSED_FOLDER']
        processed_folder.mkdir(parents=True, exist_ok=True)
        test_file = processed_folder / f"{session_id}_test_output.xlsx"

        # Write dummy Excel file
        import pandas as pd
        df = pd.DataFrame({"Name": ["Test"], "LONG": [28.0], "LATTs": [-26.0]})
        df.to_excel(str(test_file), index=False)

        # Create session info
        with processing_results_lock:
            processing_results[session_id] = {
                'filename': 'test_input.xlsx',
                'output_path': str(test_file),
                'output_filename': 'test_output.xlsx',
                'status': 'completed',
                'created_at': time.time()
            }

        yield session_id, str(test_file)

        # Cleanup
        if test_file.exists():
            test_file.unlink()
        with processing_results_lock:
            if session_id in processing_results:
                del processing_results[session_id]

    def test_valid_download_works(self, client, valid_session):
        """Test that normal file download still works after fix."""
        session_id, file_path = valid_session

        response = client.get(f'/download/{session_id}')

        assert response.status_code == 200, "Valid download should return 200 OK"
        assert response.mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert len(response.data) > 0, "Downloaded file should have content"

    def test_path_traversal_etc_passwd(self, client):
        """Test that /etc/passwd cannot be downloaded via path traversal."""
        session_id = "test-session-malicious-1"

        # Create malicious session with path to /etc/passwd
        with processing_results_lock:
            processing_results[session_id] = {
                'filename': 'malicious_input.xlsx',
                'output_path': '/etc/passwd',  # MALICIOUS PATH
                'output_filename': 'passwd.xlsx',
                'status': 'completed',
                'created_at': time.time()
            }

        try:
            response = client.get(f'/download/{session_id}')

            assert response.status_code == 403, "Path traversal should return 403 Forbidden"
            assert response.json['error'] == 'Invalid file path', "Should return clear error message"
        finally:
            # Cleanup
            with processing_results_lock:
                if session_id in processing_results:
                    del processing_results[session_id]

    def test_path_traversal_relative_path(self, client):
        """Test that ../../../etc/passwd cannot be downloaded."""
        session_id = "test-session-malicious-2"

        # Create malicious session with relative path traversal
        with processing_results_lock:
            processing_results[session_id] = {
                'filename': 'malicious_input.xlsx',
                'output_path': '../../../../../../../etc/passwd',  # RELATIVE TRAVERSAL
                'output_filename': 'passwd.xlsx',
                'status': 'completed',
                'created_at': time.time()
            }

        try:
            response = client.get(f'/download/{session_id}')

            assert response.status_code in [403, 404], "Relative path traversal should return 403 or 404"
            if response.status_code == 403:
                assert response.json['error'] == 'Invalid file path'
        finally:
            # Cleanup
            with processing_results_lock:
                if session_id in processing_results:
                    del processing_results[session_id]

    def test_path_traversal_windows_paths(self, client):
        """Test that Windows system paths cannot be downloaded."""
        session_id = "test-session-malicious-3"

        # Create malicious session with Windows system path
        with processing_results_lock:
            processing_results[session_id] = {
                'filename': 'malicious_input.xlsx',
                'output_path': 'C:\\Windows\\System32\\config\\SAM',  # WINDOWS PATH
                'output_filename': 'sam.xlsx',
                'status': 'completed',
                'created_at': time.time()
            }

        try:
            response = client.get(f'/download/{session_id}')

            assert response.status_code in [403, 404], "Windows path traversal should return 403 or 404"
            if response.status_code == 403:
                assert response.json['error'] == 'Invalid file path'
        finally:
            # Cleanup
            with processing_results_lock:
                if session_id in processing_results:
                    del processing_results[session_id]

    def test_path_traversal_parent_directory(self, client):
        """Test that parent directory cannot be accessed."""
        session_id = "test-session-malicious-4"

        # Get parent directory of PROCESSED_FOLDER
        parent_dir = app.config['PROCESSED_FOLDER'].parent / 'some_sensitive_file.txt'

        with processing_results_lock:
            processing_results[session_id] = {
                'filename': 'malicious_input.xlsx',
                'output_path': str(parent_dir),  # PARENT DIRECTORY
                'output_filename': 'sensitive.xlsx',
                'status': 'completed',
                'created_at': time.time()
            }

        try:
            response = client.get(f'/download/{session_id}')

            assert response.status_code in [403, 404], "Parent directory access should return 403 or 404"
            if response.status_code == 403:
                assert response.json['error'] == 'Invalid file path'
        finally:
            # Cleanup
            with processing_results_lock:
                if session_id in processing_results:
                    del processing_results[session_id]

    def test_invalid_session_id(self, client):
        """Test that invalid session ID returns 404."""
        response = client.get('/download/nonexistent-session-id')

        assert response.status_code == 404, "Invalid session should return 404"
        assert 'Invalid session ID' in response.json['error']

    def test_not_completed_status(self, client):
        """Test that download fails if processing not completed."""
        session_id = "test-session-not-completed"

        with processing_results_lock:
            processing_results[session_id] = {
                'filename': 'test_input.xlsx',
                'output_path': '/some/path/file.xlsx',
                'output_filename': 'test_output.xlsx',
                'status': 'processing',  # NOT COMPLETED
                'created_at': time.time()
            }

        try:
            response = client.get(f'/download/{session_id}')

            assert response.status_code == 400, "Not completed should return 400"
            assert 'has not been processed yet' in response.json['error']
        finally:
            # Cleanup
            with processing_results_lock:
                if session_id in processing_results:
                    del processing_results[session_id]


class TestPathTraversalSymlinks:
    """Test symlink-based path traversal attempts."""

    @pytest.fixture
    def client(self):
        """Create Flask test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_symlink_to_etc(self, client):
        """Test that symlink to /etc directory is blocked."""
        # Only run this test on Unix-like systems
        if sys.platform == 'win32':
            pytest.skip("Symlink test not applicable on Windows")

        session_id = "test-session-symlink"
        processed_folder = app.config['PROCESSED_FOLDER']
        processed_folder.mkdir(parents=True, exist_ok=True)

        # Create symlink to /etc
        symlink_path = processed_folder / "symlink_to_etc"
        try:
            symlink_path.symlink_to('/etc')

            with processing_results_lock:
                processing_results[session_id] = {
                    'filename': 'malicious_input.xlsx',
                    'output_path': str(symlink_path / 'passwd'),  # SYMLINK TRAVERSAL
                    'output_filename': 'passwd.xlsx',
                    'status': 'completed',
                    'created_at': time.time()
                }

            response = client.get(f'/download/{session_id}')

            assert response.status_code == 403, "Symlink traversal should return 403 Forbidden"
            assert response.json['error'] == 'Invalid file path'

        except PermissionError:
            pytest.skip("Insufficient permissions to create symlink")
        finally:
            # Cleanup
            if symlink_path.exists():
                symlink_path.unlink()
            with processing_results_lock:
                if session_id in processing_results:
                    del processing_results[session_id]


if __name__ == "__main__":
    print("=" * 70)
    print("TEST BUG #2: PATH TRAVERSAL VULNERABILITY")
    print("=" * 70)
    print("\n🧪 Running path traversal security tests...\n")

    # Run tests with verbose output
    exit_code = pytest.main([__file__, "-v", "--tb=short"])

    print("\n" + "=" * 70)
    if exit_code == 0:
        print("✅ ALL TESTS PASSED - Path traversal vulnerability is fixed")
    else:
        print("❌ TESTS FAILED - Path traversal vulnerability still exists")
    print("=" * 70)

    sys.exit(exit_code)
