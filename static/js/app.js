/**
 * Flask Map Coordinates Converter - Frontend JavaScript
 * Handles file upload, processing, and UI interactions
 */

// Global state
let currentSessionId = null;
let uploadedFile = null;

// DOM Elements
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const fileName = document.getElementById('fileName');
const errorMessage = document.getElementById('errorMessage');
const previewSection = document.getElementById('previewSection');
const processBtn = document.getElementById('processBtn');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const successMessage = document.getElementById('successMessage');
const warningMessage = document.getElementById('warningMessage');
const resultsSection = document.getElementById('resultsSection');
const downloadBtn = document.getElementById('downloadBtn');
const instructionsSection = document.getElementById('instructionsSection');

// Event Listeners
uploadBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
processBtn.addEventListener('click', handleProcess);
downloadBtn.addEventListener('click', handleDownload);

/**
 * Handle file selection
 */
function handleFileSelect(event) {
    const file = event.target.files[0];

    if (!file) return;

    // Validate file type
    if (!file.name.endsWith('.xlsx')) {
        showError('Only .xlsx files are allowed');
        return;
    }

    uploadedFile = file;
    fileName.textContent = file.name;

    // Upload file to server
    uploadFile(file);
}

/**
 * Upload file to server
 */
async function uploadFile(file) {
    hideAllMessages();
    showLoading(uploadBtn, 'Uploading...');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Upload failed');
        }

        // Store session ID
        currentSessionId = data.session_id;

        // Show preview
        displayPreview(data);

        // Hide instructions
        instructionsSection.style.display = 'none';

    } catch (error) {
        showError(error.message);
        resetUploadButton();
    } finally {
        hideLoading(uploadBtn, '📁 Upload Excel file (.xlsx)');
    }
}

/**
 * Display file preview
 */
function displayPreview(data) {
    // Populate preview table
    const thead = document.getElementById('previewTableHead');
    const tbody = document.getElementById('previewTableBody');

    // Clear existing content
    thead.innerHTML = '';
    tbody.innerHTML = '';

    // Create header row
    const headerRow = document.createElement('tr');
    data.preview_columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);

    // Create data rows (first 10)
    data.preview_data.forEach(row => {
        const tr = document.createElement('tr');
        data.preview_columns.forEach(col => {
            const td = document.createElement('td');
            td.textContent = row[col] || '';
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });

    // Show preview section
    previewSection.style.display = 'block';
}

/**
 * Handle file processing
 */
async function handleProcess() {
    if (!currentSessionId) {
        showError('No file uploaded');
        return;
    }

    hideAllMessages();
    showLoading(processBtn, 'Processing...');

    // Show progress section
    progressSection.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = 'Starting processing...';

    try {
        // Simulate progress animation
        simulateProgress();

        const response = await fetch(`/process/${currentSessionId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Processing failed');
        }

        // Complete progress
        progressFill.style.width = '100%';
        progressText.textContent = 'Processing complete!';

        // Show success message
        showSuccess(`✅ Processing complete! Successfully processed ${data.successful}/${data.total_rows} rows`);

        // Show warning if there were failures or skipped rows
        if (data.failed > 0) {
            showWarning(`⚠️ Failed to extract coordinates for ${data.failed} rows`);
        }
        if (data.skipped > 0) {
            showWarning(`ℹ️ Skipped ${data.skipped} rows with missing map links`);
        }

        // Display results
        displayResults(data);

        // Update statistics
        updateStatistics(data);

        // Display processing log
        displayProcessingLog(data.processing_log);

        // Hide progress after delay
        setTimeout(() => {
            progressSection.style.display = 'none';
        }, 2000);

    } catch (error) {
        showError(error.message);
        progressSection.style.display = 'none';
    } finally {
        hideLoading(processBtn, '🔄 Extract Coordinates');
    }
}

/**
 * Simulate progress bar animation
 */
function simulateProgress() {
    let progress = 0;
    const interval = setInterval(() => {
        if (progress < 90) {
            progress += Math.random() * 10;
            progressFill.style.width = Math.min(progress, 90) + '%';
            progressText.textContent = `Processing... ${Math.round(progress)}%`;
        }
    }, 200);

    // Store interval ID for cleanup
    window.progressInterval = interval;
}

/**
 * Display processing results
 */
function displayResults(data) {
    const thead = document.getElementById('resultsTableHead');
    const tbody = document.getElementById('resultsTableBody');

    // Clear existing content
    thead.innerHTML = '';
    tbody.innerHTML = '';

    // Create header row
    const headerRow = document.createElement('tr');
    data.processed_columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);

    // Create data rows
    data.processed_data.forEach(row => {
        const tr = document.createElement('tr');
        data.processed_columns.forEach(col => {
            const td = document.createElement('td');
            const value = row[col];

            // Format numbers to fixed decimal places
            if (typeof value === 'number') {
                td.textContent = value.toFixed(6);
            } else {
                td.textContent = value || '';
            }

            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });

    // Show results section
    resultsSection.style.display = 'block';
}

/**
 * Update statistics cards
 */
function updateStatistics(data) {
    document.getElementById('statTotal').textContent = data.total_rows;
    document.getElementById('statSuccess').textContent = data.successful;
    document.getElementById('statFailed').textContent = data.failed;
    document.getElementById('statSkipped').textContent = data.skipped || 0;
}

/**
 * Display processing log
 */
function displayProcessingLog(processingLog) {
    if (!processingLog || processingLog.length === 0) {
        return;
    }

    const logContainer = document.getElementById('processingLog');
    const logSection = document.getElementById('processingLogSection');

    // Clear existing log
    logContainer.innerHTML = '';

    // Group logs by status
    const skippedLogs = processingLog.filter(log => log.status === 'skipped');
    const failedLogs = processingLog.filter(log => log.status === 'failed');
    const successLogs = processingLog.filter(log => log.status === 'success');

    // Display skipped entries
    if (skippedLogs.length > 0) {
        const skippedHeader = document.createElement('div');
        skippedHeader.className = 'log-section-header';
        skippedHeader.innerHTML = `<h4>⚠️ Skipped Rows (${skippedLogs.length})</h4>`;
        logContainer.appendChild(skippedHeader);

        skippedLogs.forEach(log => {
            const entry = createLogEntry(log, 'skipped');
            logContainer.appendChild(entry);
        });
    }

    // Display failed entries
    if (failedLogs.length > 0) {
        const failedHeader = document.createElement('div');
        failedHeader.className = 'log-section-header';
        failedHeader.innerHTML = `<h4>❌ Failed Rows (${failedLogs.length})</h4>`;
        logContainer.appendChild(failedHeader);

        failedLogs.forEach(log => {
            const entry = createLogEntry(log, 'failed');
            logContainer.appendChild(entry);
        });
    }

    // Only show first 10 successful entries to avoid clutter
    if (successLogs.length > 0) {
        const successHeader = document.createElement('div');
        successHeader.className = 'log-section-header';
        successHeader.innerHTML = `<h4>✅ Sample Successful Rows (showing ${Math.min(10, successLogs.length)} of ${successLogs.length})</h4>`;
        logContainer.appendChild(successHeader);

        successLogs.slice(0, 10).forEach(log => {
            const entry = createLogEntry(log, 'success');
            logContainer.appendChild(entry);
        });
    }

    // Show the log section
    logSection.style.display = 'block';
}

/**
 * Create a log entry element
 */
function createLogEntry(log, status) {
    const entry = document.createElement('div');
    entry.className = `log-entry ${status}`;

    const header = document.createElement('div');
    header.className = 'log-entry-header';
    header.textContent = `Row ${log.row}: ${log.name}`;
    entry.appendChild(header);

    if (log.reason) {
        const detail = document.createElement('div');
        detail.className = 'log-entry-detail';
        detail.textContent = `Reason: ${log.reason}`;
        entry.appendChild(detail);
    }

    if (log.map_link) {
        const detail = document.createElement('div');
        detail.className = 'log-entry-detail';
        detail.innerHTML = `URL: <code>${log.map_link}</code>`;
        entry.appendChild(detail);
    }

    if (log.lng && log.lat) {
        const detail = document.createElement('div');
        detail.className = 'log-entry-detail';
        detail.textContent = `Coordinates: ${log.lng.toFixed(6)}, ${log.lat.toFixed(6)}`;
        entry.appendChild(detail);
    }

    return entry;
}

/**
 * Handle file download
 */
async function handleDownload() {
    if (!currentSessionId) {
        showError('No processed file available');
        return;
    }

    try {
        // Open download in new window
        window.location.href = `/download/${currentSessionId}`;
    } catch (error) {
        showError('Error downloading file: ' + error.message);
    }
}

/**
 * Show error message
 */
function showError(message) {
    errorMessage.textContent = '❌ ' + message;
    errorMessage.style.display = 'block';

    // Auto-hide after 5 seconds
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

/**
 * Show success message
 */
function showSuccess(message) {
    successMessage.textContent = message;
    successMessage.style.display = 'block';
}

/**
 * Show warning message
 */
function showWarning(message) {
    warningMessage.textContent = message;
    warningMessage.style.display = 'block';
}

/**
 * Hide all messages
 */
function hideAllMessages() {
    errorMessage.style.display = 'none';
    successMessage.style.display = 'none';
    warningMessage.style.display = 'none';
}

/**
 * Show loading state on button
 */
function showLoading(button, text) {
    button.disabled = true;
    button.classList.add('loading');
    button.dataset.originalText = button.textContent;
    button.textContent = text;
}

/**
 * Hide loading state on button
 */
function hideLoading(button, text) {
    button.disabled = false;
    button.classList.remove('loading');
    button.textContent = text || button.dataset.originalText;
}

/**
 * Reset upload button
 */
function resetUploadButton() {
    fileName.textContent = '';
    fileInput.value = '';
    uploadedFile = null;
}

/**
 * Clear progress interval on page unload
 */
window.addEventListener('beforeunload', () => {
    if (window.progressInterval) {
        clearInterval(window.progressInterval);
    }
});
