# Flask Map Coordinates Converter - Complete Guide

## 🎯 Overview

This is a Flask-based web application that converts Google Maps URLs in Excel files to GPS coordinates (longitude and latitude). It's a complete conversion from the original Streamlit app, maintaining all UI/UX features with enhanced control and customization.

---

## 🏗️ Architecture Deep Dive

### **Backend Architecture (Flask)**

```
flask_app.py (Main Application)
├── Routes
│   ├── / (GET) - Main page
│   ├── /upload (POST) - File upload & validation
│   ├── /process/<session_id> (POST) - Coordinate extraction
│   ├── /download/<session_id> (GET) - File download
│   └── /health (GET) - Health check
├── Session Management
│   └── In-memory dictionary (processing_results)
└── File Storage
    ├── uploads/ - Temporary uploaded files
    └── processed/ - Generated output files
```

### **Frontend Architecture**

```
templates/index.html (UI Structure)
├── Upload Section
├── Preview Section
├── Progress Section
├── Results Section
└── Instructions Section

static/
├── css/style.css (Styling)
└── js/app.js (Client-side logic)
```

### **Data Flow**

```
User uploads .xlsx file
    ↓
Frontend sends file via FormData
    ↓
Flask /upload endpoint validates & stores file
    ↓
Returns session_id + preview data (JSON)
    ↓
JavaScript displays preview table
    ↓
User clicks "Extract Coordinates"
    ↓
Frontend calls /process/<session_id>
    ↓
Flask reads file, extracts coordinates row-by-row
    ↓
Returns processed data + statistics (JSON)
    ↓
JavaScript displays results + download button
    ↓
User clicks "Download"
    ↓
Flask serves processed .xlsx file
```

---

## 🚀 Installation & Setup

### **1. Install Dependencies**

```bash
pip install -r requirements.txt
```

Dependencies installed:
- **Flask** (3.0.0): Web framework
- **Werkzeug** (3.0.1): WSGI utilities and file handling
- **pandas** (2.0.3): Excel I/O and data manipulation
- **openpyxl** (3.1.2): Excel file format support
- **requests** (2.31.0): HTTP requests for URL resolution

### **2. Run the Flask App**

```bash
python flask_app.py
```

The app will start on `http://0.0.0.0:5000`

### **3. Access in Browser**

Open: `http://localhost:5000`

---

## 📋 API Endpoints Documentation

### **1. GET /**
- **Purpose**: Render main application page
- **Returns**: HTML page (index.html)
- **Response**: 200 OK

---

### **2. POST /upload**
- **Purpose**: Upload and validate Excel file
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file`: Excel file (.xlsx)

**Request Example**:
```javascript
const formData = new FormData();
formData.append('file', fileObject);

fetch('/upload', {
    method: 'POST',
    body: formData
});
```

**Success Response (200)**:
```json
{
    "success": true,
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "preview_data": [
        {
            "Name": "Sandton City",
            "Region": "Johannesburg",
            "Maps": "https://maps.app.goo.gl/baixEU9UxYHX8Yox7",
            "LONG": null,
            "LATTs": null
        }
    ],
    "preview_columns": ["Name", "Region", "Maps", "LONG", "LATTs"],
    "total_rows": 150,
    "map_column": "Maps"
}
```

**Error Response (400)**:
```json
{
    "error": "Missing required map column: \"Map link\" or \"Maps\""
}
```

**Validations Performed**:
1. File exists in request
2. File has .xlsx extension
3. File contains required columns: `Name`, `Region`
4. File contains map column: `Map link` OR `Maps`

---

### **3. POST /process/<session_id>**
- **Purpose**: Process uploaded file and extract coordinates
- **Parameters**:
  - `session_id`: UUID from upload response

**Request Example**:
```javascript
fetch('/process/550e8400-e29b-41d4-a716-446655440000', {
    method: 'POST'
});
```

**Success Response (200)**:
```json
{
    "success": true,
    "total_rows": 150,
    "successful": 142,
    "failed": 8,
    "processed_data": [
        {
            "Name": "Sandton City",
            "Region": "Johannesburg",
            "Maps": "https://maps.app.goo.gl/baixEU9UxYHX8Yox7",
            "LONG": 28.052706,
            "LATTs": -26.108204
        }
    ],
    "processed_columns": ["Name", "Region", "Maps", "LONG", "LATTs"]
}
```

**Processing Logic**:
1. Load Excel file from `uploads/` directory
2. Create or find `LONG`/`Long` and `LATTs`/`Latts` columns
3. For each row:
   - Extract map link from map column
   - Call `extract_coordinates_from_url()` from `map_converter.py`
   - Parse URL using 4 regex patterns
   - Resolve shortened URLs via HTTP redirects
   - Update longitude and latitude columns
4. Save processed file to `processed/` directory
5. Return statistics and full dataset

---

### **4. GET /download/<session_id>**
- **Purpose**: Download processed Excel file
- **Parameters**:
  - `session_id`: UUID from upload response

**Response**:
- **Content-Type**: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **Headers**: `Content-Disposition: attachment; filename=processed_*.xlsx`
- **Body**: Binary Excel file

**Browser Behavior**: Triggers file download dialog

---

### **5. GET /health**
- **Purpose**: Health check for monitoring
- **Returns**: JSON status

**Response**:
```json
{
    "status": "healthy"
}
```

---

## 🎨 UI/UX Features Comparison

| Feature | Streamlit | Flask Implementation |
|---------|-----------|---------------------|
| **File Upload** | `st.file_uploader()` | Custom drag-drop styled button |
| **Data Preview** | `st.dataframe()` | Dynamic HTML table generation |
| **Progress Bar** | `st.progress()` | CSS-animated progress bar |
| **Status Text** | `st.empty().text()` | Real-time DOM updates |
| **Success Messages** | `st.success()` | Custom alert boxes with CSS |
| **Warning Messages** | `st.warning()` | Custom alert boxes with CSS |
| **Error Messages** | `st.error()` | Custom alert boxes with CSS |
| **Download Button** | `st.download_button()` | Flask `send_file()` endpoint |
| **Statistics Cards** | `st.metric()` | CSS Grid layout with cards |
| **Responsive Layout** | Built-in | Custom CSS media queries |
| **Dark Theme** | Built-in | Custom CSS variables |

---

## 💻 Frontend Technology Stack

### **HTML (Semantic Structure)**
- **Progressive disclosure**: Sections shown/hidden based on state
- **Accessibility**: Proper ARIA labels and semantic tags
- **SEO-friendly**: Meta tags and structured data

### **CSS (Modern Styling)**
- **CSS Grid**: Statistics dashboard layout
- **Flexbox**: Centered content and alignment
- **CSS Variables**: Color scheme management
- **Animations**: Fade-in transitions, progress bar
- **Responsive**: Mobile-first approach with breakpoints

### **JavaScript (ES6+)**
- **Async/Await**: Modern promise handling
- **Fetch API**: RESTful API communication
- **DOM Manipulation**: Dynamic table generation
- **Event Delegation**: Efficient event handling
- **State Management**: Client-side session tracking

---

## 🔧 Technical Implementation Details

### **Session Management**

```python
# In-memory storage (Development)
processing_results = {
    'session_id': {
        'filename': 'data.xlsx',
        'upload_path': 'uploads/uuid_data.xlsx',
        'map_column': 'Maps',
        'total_rows': 150,
        'status': 'completed',
        'output_path': 'processed/uuid_processed_data.xlsx',
        'successful': 142,
        'failed': 8
    }
}
```

**Production Recommendation**: Use Redis or database for persistence
```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.setex(session_id, 3600, json.dumps(session_data))  # 1 hour expiry
```

---

### **File Upload Handling**

```python
# Security measures implemented:
1. File extension validation (.xlsx only)
2. Secure filename sanitization (Werkzeug)
3. File size limit (16MB max)
4. Unique file naming (UUID prefix)
5. Isolated storage directories
```

---

### **Coordinate Extraction (Reused from map_converter.py)**

```python
def extract_coordinates_from_url(map_link: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Regex patterns used (in order of precedence):

    1. @lat,lng format
       Pattern: r'@(-?\d+\.\d+),(-?\d+\.\d+)'
       Example: @-26.108204,28.0527061

    2. q=lat,lng format
       Pattern: r'[?&]q=(-?\d+\.\d+),(-?\d+\.\d+)'
       Example: ?q=-26.108204,28.0527061

    3. /place/.../@lat,lng
       Pattern: r'/place/[^/]+/@(-?\d+\.\d+),(-?\d+\.\d+)'
       Example: /place/Sandton/@-26.108204,28.0527061

    4. Direct coordinates
       Pattern: r'(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)'
       Example: -26.108204, 28.0527061

    Shortened URL resolution:
    - Detects goo.gl or maps.app.goo.gl
    - Uses requests.head() with allow_redirects=True
    - Extracts final URL from response.url
    - Applies regex patterns to resolved URL
    """
```

---

### **Progress Bar Implementation**

**Backend** (Flask):
- Processes synchronously, returns when complete
- Could be enhanced with WebSockets for real-time updates

**Frontend** (JavaScript):
```javascript
// Simulated progress (smooth UX):
function simulateProgress() {
    let progress = 0;
    const interval = setInterval(() => {
        if (progress < 90) {
            progress += Math.random() * 10;
            progressFill.style.width = Math.min(progress, 90) + '%';
        }
    }, 200);
}

// On completion:
progressFill.style.width = '100%';
```

**Enhancement Opportunity**: Use Server-Sent Events (SSE)
```python
@app.route('/process-stream/<session_id>')
def process_stream(session_id):
    def generate():
        for idx, row in df.iterrows():
            # Process row
            progress = (idx + 1) / len(df) * 100
            yield f"data: {json.dumps({'progress': progress})}\n\n"

    return Response(generate(), mimetype='text/event-stream')
```

---

## 🔒 Security Considerations

### **Implemented**:
✅ File extension validation
✅ Filename sanitization (Werkzeug's `secure_filename`)
✅ File size limits (16MB)
✅ Secret key for session management
✅ CSRF protection (Flask-WTF recommended for production)

### **Recommended for Production**:
- Add authentication/authorization
- Implement rate limiting (Flask-Limiter)
- Add HTTPS/TLS encryption
- Sanitize Excel file contents (check for macros)
- Add virus scanning for uploads
- Implement CORS policies
- Use environment variables for secrets

---

## 🚀 Production Deployment

### **Option 1: Gunicorn (Recommended)**

```bash
# Install
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 flask_app:app
```

### **Option 2: Docker**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "flask_app:app"]
```

```bash
docker build -t map-converter .
docker run -p 5000:5000 map-converter
```

### **Option 3: AWS Elastic Beanstalk**

```bash
# Initialize EB
eb init -p python-3.11 map-converter

# Create environment
eb create map-converter-env

# Deploy
eb deploy
```

---

## 📊 Performance Optimization

### **Current Bottlenecks**:
1. **Shortened URL resolution**: Synchronous HTTP requests
2. **Large file processing**: Loads entire file into memory
3. **Session storage**: In-memory dictionary (not scalable)

### **Optimization Strategies**:

**1. Async URL Resolution**:
```python
import asyncio
import aiohttp

async def extract_coordinates_async(url):
    async with aiohttp.ClientSession() as session:
        async with session.head(url, allow_redirects=True) as response:
            resolved_url = str(response.url)
            # Extract coordinates
```

**2. Chunked Processing**:
```python
chunk_size = 100
for chunk in pd.read_excel(file, chunksize=chunk_size):
    # Process chunk
    yield progress_update
```

**3. Redis Session Storage**:
```python
import redis
cache = redis.Redis(host='localhost', port=6379)
cache.setex(session_id, 3600, json.dumps(data))
```

**4. Background Tasks with Celery**:
```python
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379')

@celery.task
def process_file_async(session_id):
    # Long-running processing
    pass
```

---

## 🧪 Testing the Flask App

### **Manual Testing**:
```bash
# Start server
python flask_app.py

# Open browser
open http://localhost:5000

# Upload test file
# Use: test_input.xlsx
```

### **API Testing with cURL**:
```bash
# Upload file
curl -X POST http://localhost:5000/upload \
  -F "file=@test_input.xlsx"

# Process file (use session_id from response)
curl -X POST http://localhost:5000/process/<session_id>

# Download file
curl -O http://localhost:5000/download/<session_id>
```

### **Automated Testing** (Recommended):
```python
import pytest
from flask_app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_upload(client):
    with open('test_input.xlsx', 'rb') as f:
        response = client.post('/upload', data={'file': f})
    assert response.status_code == 200
    assert 'session_id' in response.json
```

---

## 🎯 Key Differences: Streamlit vs Flask

### **Streamlit Approach**:
- **State Management**: Session state (automatic)
- **Rendering**: Reruns entire script on interaction
- **Deployment**: Streamlit Cloud (proprietary)
- **Customization**: Limited to Streamlit components
- **Learning Curve**: Low (Python-only)

### **Flask Approach**:
- **State Management**: Manual (session IDs, databases)
- **Rendering**: Client-side JavaScript updates
- **Deployment**: Any platform (Heroku, AWS, Azure, Docker)
- **Customization**: Full control (HTML/CSS/JS)
- **Learning Curve**: Medium (requires frontend knowledge)

### **When to Choose Flask**:
✅ Need full UI/UX control
✅ Require RESTful API endpoints
✅ Want to integrate with existing systems
✅ Need scalable production deployment
✅ Require custom authentication/authorization

### **When to Choose Streamlit**:
✅ Rapid prototyping
✅ Internal data tools
✅ Python-only team
✅ Simple deployment needs
✅ Data science focused apps

---

## 📚 Additional Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **Pandas Excel I/O**: https://pandas.pydata.org/docs/reference/io.html#excel
- **Fetch API**: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
- **CSS Grid**: https://css-tricks.com/snippets/css/complete-guide-grid/

---

## 🐛 Troubleshooting

### **Issue**: "No module named 'flask'"
**Solution**: `pip install Flask==3.0.0`

### **Issue**: "Address already in use"
**Solution**: Kill process on port 5000
```bash
lsof -ti:5000 | xargs kill -9
```

### **Issue**: "Session ID not found"
**Solution**: Server restarted - sessions are in-memory. Re-upload file.

### **Issue**: "File upload fails"
**Solution**: Check file size (max 16MB) and format (.xlsx only)

---

## 👨‍💻 Development Workflow

```bash
# 1. Make changes to code
# 2. Flask auto-reloads (debug=True)
# 3. Refresh browser to see changes
# 4. Test in browser
# 5. Check console for errors (F12)
```

---

**Built with ❤️ using Flask, Pandas, and Modern JavaScript**
