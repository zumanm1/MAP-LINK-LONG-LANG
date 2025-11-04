# Quick Start Guide - Flask vs Streamlit

## 🚀 Running the Applications

### **Streamlit Version** (Original)
```bash
streamlit run app.py
```
Opens at: `http://localhost:8501`

### **Flask Version** (New)
```bash
python flask_app.py
```
Opens at: `http://localhost:5000`

---

## 📁 Project Structure

```
excel-map-coordinates-converter/
├── map_converter.py          # Core coordinate extraction logic (shared)
│
├── app.py                     # Streamlit web app
├── flask_app.py              # Flask web app (NEW)
│
├── templates/                # Flask HTML templates (NEW)
│   └── index.html
│
├── static/                   # Flask static assets (NEW)
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
├── uploads/                  # Flask temp uploads (auto-created)
├── processed/                # Flask outputs (auto-created)
│
├── tests/
│   └── test_map_converter.py
│
├── requirements.txt          # Python dependencies
├── README.md                 # Original documentation
├── STREAMLIT_GUIDE.md       # Streamlit documentation
├── FLASK_GUIDE.md           # Flask documentation (NEW)
└── QUICK_START.md           # This file (NEW)
```

---

## 🎯 Feature Comparison

| Feature | Streamlit | Flask |
|---------|-----------|-------|
| **File Upload** | Built-in widget | Custom HTML/JS |
| **Data Preview** | `st.dataframe()` | Dynamic HTML table |
| **Processing** | Synchronous | Async-ready |
| **Progress Bar** | Auto-updating | Simulated + real updates |
| **Download** | Memory buffer | File system |
| **Deployment** | Streamlit Cloud | Any platform |
| **Customization** | Limited | Full control |
| **API Access** | No | Yes (RESTful) |

---

## 💡 Code Deep Dive

### **Shared Core Logic** (`map_converter.py`)

Both apps use the same coordinate extraction function:

```python
def extract_coordinates_from_url(map_link: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Extracts coordinates from Google Maps URLs

    Process:
    1. Detect shortened URLs (goo.gl, maps.app.goo.gl)
    2. If shortened: resolve via HTTP redirect
    3. Apply 4 regex patterns in order:
       a. @lat,lng format
       b. ?q=lat,lng format
       c. /place/.../@lat,lng format
       d. Direct coordinate pairs
    4. Validate coordinate ranges
    5. Return (longitude, latitude) or (None, None)
    """
```

**Regex Patterns Explained**:

```python
# Pattern 1: @lat,lng (most common in Google Maps)
r'@(-?\d+\.\d+),(-?\d+\.\d+)'
# Matches: @-26.108204,28.0527061
# Captures: lat=-26.108204, lng=28.0527061

# Pattern 2: q=lat,lng (query parameter format)
r'[?&]q=(-?\d+\.\d+),(-?\d+\.\d+)'
# Matches: ?q=-26.108204,28.0527061
# Captures: lat=-26.108204, lng=28.0527061

# Pattern 3: /place/ URLs
r'/place/[^/]+/@(-?\d+\.\d+),(-?\d+\.\d+)'
# Matches: /place/Sandton/@-26.108204,28.0527061
# Captures: lat=-26.108204, lng=28.0527061

# Pattern 4: Direct coordinates (fallback)
r'(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)'
# Matches: -26.108204, 28.0527061
# Captures: coord1=-26.108204, coord2=28.0527061
# Logic: Determines lat/lng by range validation
```

**URL Shortener Resolution**:
```python
if 'goo.gl' in map_link or 'maps.app.goo.gl' in map_link:
    response = requests.head(map_link, allow_redirects=True, timeout=10)
    map_link = response.url  # Get final URL after redirects
```

---

### **Streamlit Implementation** (`app.py`)

**State Management**:
```python
# Streamlit reruns script on every interaction
# State persists via st.session_state (automatic)

uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type=['xlsx'])
# Returns UploadedFile object or None
```

**Processing Flow**:
```python
if st.button("🔄 Extract Coordinates"):
    progress_bar = st.progress(0)          # Create progress widget
    status_text = st.empty()               # Placeholder for status

    for idx, row in df.iterrows():
        progress = (idx + 1) / len(df)
        progress_bar.progress(progress)    # Update progress (0.0 to 1.0)
        status_text.text(f"Processing row {idx + 1}...")

        # Extract coordinates
        lng, lat = extract_coordinates_from_url(str(map_link))
```

**Download Implementation**:
```python
# Create in-memory Excel file
output = io.BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    df.to_excel(writer, index=False)

# Provide download button
st.download_button(
    label="⬇️ Download Processed File",
    data=output.getvalue(),
    file_name="coordinates_output.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
```

---

### **Flask Implementation** (`flask_app.py`)

**State Management**:
```python
# Manual session management using UUID
processing_results = {}  # In-memory storage

session_id = str(uuid.uuid4())  # Generate unique ID
processing_results[session_id] = {
    'filename': filename,
    'upload_path': upload_path,
    'status': 'uploaded'
}
```

**File Upload Handler**:
```python
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']  # Get file from multipart form

    # Validate extension
    if not file.filename.endswith('.xlsx'):
        return jsonify({'error': 'Only .xlsx files allowed'}), 400

    # Read and validate with pandas
    df = pd.read_excel(file)

    # Save to disk with UUID prefix
    filename = secure_filename(file.filename)  # Sanitize filename
    upload_path = os.path.join('uploads', f"{session_id}_{filename}")
    df.to_excel(upload_path, index=False)

    return jsonify({'session_id': session_id, 'preview_data': ...})
```

**Processing Handler**:
```python
@app.route('/process/<session_id>', methods=['POST'])
def process_file(session_id):
    # Load file from disk
    df = pd.read_excel(session_info['upload_path'])

    # Process each row (same logic as Streamlit)
    for idx, row in df.iterrows():
        lng, lat = extract_coordinates_from_url(str(map_link))
        df.at[idx, long_column] = lng
        df.at[idx, lat_column] = lat

    # Save to disk
    output_path = os.path.join('processed', f"{session_id}_processed.xlsx")
    df.to_excel(output_path, index=False)

    # Return full dataset as JSON
    return jsonify({
        'processed_data': df.to_dict('records'),
        'successful': successful,
        'failed': failed
    })
```

**Download Handler**:
```python
@app.route('/download/<session_id>')
def download_file(session_id):
    # Serve file from disk
    return send_file(
        session_info['output_path'],
        as_attachment=True,
        download_name='processed_output.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
```

---

### **Frontend JavaScript** (`static/js/app.js`)

**File Upload**:
```javascript
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error);
    }

    currentSessionId = data.session_id;  // Store for later use
    displayPreview(data);                // Render preview table
}
```

**Dynamic Table Generation**:
```javascript
function displayPreview(data) {
    const thead = document.getElementById('previewTableHead');
    const tbody = document.getElementById('previewTableBody');

    // Create header row
    const headerRow = document.createElement('tr');
    data.preview_columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);

    // Create data rows
    data.preview_data.forEach(row => {
        const tr = document.createElement('tr');
        data.preview_columns.forEach(col => {
            const td = document.createElement('td');
            td.textContent = row[col] || '';
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}
```

**Progress Bar Animation**:
```javascript
function simulateProgress() {
    let progress = 0;
    const interval = setInterval(() => {
        if (progress < 90) {
            progress += Math.random() * 10;
            progressFill.style.width = Math.min(progress, 90) + '%';
            progressText.textContent = `Processing... ${Math.round(progress)}%`;
        }
    }, 200);
}

// On completion:
progressFill.style.width = '100%';
progressText.textContent = 'Processing complete!';
```

---

### **CSS Styling** (`static/css/style.css`)

**Streamlit-inspired Dark Theme**:
```css
body {
    background-color: #0e1117;  /* Streamlit dark background */
    color: #fafafa;             /* Light text */
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto";
}

/* Primary action button (Streamlit red) */
.btn-primary {
    background-color: #ff4b4b;  /* Streamlit's primary color */
}

/* Success message (Streamlit green) */
.alert-success {
    background-color: #21c35420;
    border-left: 4px solid #21c354;
    color: #21c354;
}
```

**Responsive Grid Layout**:
```css
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
}

@media (max-width: 768px) {
    .stats-grid {
        grid-template-columns: 1fr;  /* Stack on mobile */
    }
}
```

**Smooth Animations**:
```css
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

section {
    animation: fadeIn 0.5s ease-in;
}
```

---

## 🔍 Key Technical Decisions

### **Why UUID for Session IDs?**
```python
session_id = str(uuid.uuid4())
# Generates: "550e8400-e29b-41d4-a716-446655440000"
```
- **Unique**: Collision probability is negligible
- **Unpredictable**: Prevents session hijacking
- **Stateless**: No database lookup needed
- **URL-safe**: Can be used in routes

### **Why Separate Upload and Process Endpoints?**
1. **Preview before processing**: User can verify data first
2. **Better error handling**: Validate early, process later
3. **Separation of concerns**: Each endpoint has single responsibility
4. **Progress tracking**: Can extend to WebSockets/SSE

### **Why In-Memory Session Storage?**
- **Simplicity**: No external dependencies
- **Development**: Fast iteration
- **Limitation**: Not production-ready (data lost on restart)

**Production Alternative**:
```python
# Use Redis
import redis
r = redis.Redis()
r.setex(f"session:{session_id}", 3600, json.dumps(data))
```

### **Why Save Files to Disk?**
- **Memory efficiency**: Don't keep large files in RAM
- **Reliability**: Can recover from crashes
- **Download endpoint**: Need persistent file reference

**Alternative** (In-memory):
```python
# Store in session dict
processing_results[session_id]['file_content'] = df.to_excel()
```

---

## 🧪 Testing Both Versions

### **Test File Requirements**:
```
Excel file with columns:
- Name (required)
- Region (required)
- Maps OR Map link (required)
- LONG or Long (optional)
- LATTs or Latts (optional)
```

### **Example Test Data**:
| Name | Region | Maps | LONG | LATTs |
|------|--------|------|------|-------|
| Sandton City | Johannesburg | https://maps.app.goo.gl/baixEU9UxYHX8Yox7 | | |
| Times Square | New York | https://www.google.com/maps/@40.7580,-73.9855,17z | | |

### **Expected Output**:
| Name | Region | Maps | LONG | LATTs |
|------|--------|------|------|-------|
| Sandton City | Johannesburg | https://maps.app.goo.gl/... | 28.052706 | -26.108204 |
| Times Square | New York | https://www.google.com/maps/... | -73.9855 | 40.7580 |

---

## 🎓 Learning Takeaways

### **Streamlit is Great For**:
- Data scientists who want to build UIs quickly
- Internal tools where deployment flexibility isn't critical
- Prototypes and MVPs
- Python-only teams

### **Flask is Better For**:
- Production web applications
- RESTful APIs
- Custom UI/UX requirements
- Integration with existing frontend frameworks (React, Vue)
- Microservices architecture

### **Core Concepts Demonstrated**:

1. **Backend**:
   - File upload handling (multipart/form-data)
   - Session management (UUID-based)
   - RESTful API design
   - Error handling and validation
   - File I/O operations

2. **Frontend**:
   - Fetch API (async HTTP requests)
   - DOM manipulation
   - Event handling
   - Progressive disclosure UI
   - Responsive design

3. **Data Processing**:
   - Pandas DataFrame operations
   - Regex pattern matching
   - HTTP redirect following
   - Excel file I/O

---

## 📚 Next Steps

1. **Enhance Flask Version**:
   - Add user authentication
   - Implement WebSockets for real-time progress
   - Add file history/dashboard
   - Support batch file processing
   - Add API rate limiting

2. **Deploy**:
   - Streamlit: Streamlit Cloud (free)
   - Flask: Heroku, AWS, Docker, Azure

3. **Extend Functionality**:
   - Support more map providers (Apple Maps, Bing)
   - Reverse geocoding (coordinates → address)
   - Batch API for external integrations
   - CSV/JSON export formats

---

**Happy Coding! 🚀**
