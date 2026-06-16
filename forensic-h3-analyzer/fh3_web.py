#!/usr/bin/env python3
"""
Enhanced Flask Web UI for ForenGeo
Provides a modern web interface for forensic H3 analysis
"""

from flask import Flask, request, jsonify, render_template_string, send_file, send_from_directory, g
from forensic_h3_fixed import ForensicH3Analyzer
from deepweb_forensics import DeepWebForensics
from pathlib import Path
import os
import json
from datetime import datetime
import traceback
import threading

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['JSON_SORT_KEYS'] = False

DB_PATH = Path(os.getenv('FORNEGO_DB_PATH', '.fh3.db'))
FORNEGO_HOST = os.getenv('FORNEGO_HOST', '0.0.0.0')
FORNEGO_PORT = int(os.getenv('FORNEGO_PORT', '5000'))
FORNEGO_DEBUG = os.getenv('FORNEGO_DEBUG', 'False').lower() in ('1', 'true', 'yes')
API_TOKEN = os.getenv('FORNEGO_API_TOKEN')

# Thread-local storage for database connections
_thread_local = threading.local()

def get_indexer():
    """Get or create thread-local database connection"""
    if not hasattr(_thread_local, 'indexer'):
        try:
            _thread_local.indexer = ForensicH3Analyzer(str(DB_PATH))
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize indexer: {e}")
            _thread_local.indexer = None
    return _thread_local.indexer

def get_deepweb():
    """Get or create thread-local deep web analyzer"""
    if not hasattr(_thread_local, 'deepweb'):
        try:
            _thread_local.deepweb = DeepWebForensics()
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize deepweb: {e}")
            _thread_local.deepweb = None
    return _thread_local.deepweb

# HTML Templates
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>ForenGeo - Forensic H3 OSINT Analyzer</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .content {
            padding: 30px;
        }
        .section {
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
        }
        .section h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #333;
        }
        input[type="text"], input[type="number"], input[type="file"], select, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .button-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .success { color: #4CAF50; background: #f1f8f4; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .error { color: #f44336; background: #fef1f0; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .info { color: #2196F3; background: #f0f7ff; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .results {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
            max-height: 400px;
            overflow-y: auto;
        }
        .stat-box {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            margin: 10px 10px 10px 0;
            border-radius: 5px;
            min-width: 200px;
        }
        .stat-box .value { font-size: 2em; font-weight: bold; }
        .stat-box .label { font-size: 0.9em; opacity: 0.9; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .card {
            background: #f9f9f9;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            padding: 15px;
            transition: transform 0.2s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .card h3 { color: #667eea; margin-bottom: 10px; }
        a { color: #667eea; text-decoration: none; }
        a:hover { text-decoration: underline; }
        code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕵️ ForenGeo</h1>
            <p>Advanced H3 Forensic & OSINT Analyzer</p>
        </div>
        <div class="content">
            {% block content %}{% endblock %}
        </div>
    </div>
</body>
</html>
'''

INDEX_TEMPLATE = BASE_TEMPLATE.replace(
    '{% block content %}{% endblock %}',
    '''
    <div style="text-align:right;margin-bottom:10px;">
        <button onclick="setApiToken()">Set API Token</button>
    </div>

    <script>
        // Attach Authorization header automatically when FORNEGO token is set in localStorage
        (function(){
            const _fetch = window.fetch.bind(window);
            window.fetch = function(url, opts){
                opts = opts || {};
                opts.headers = opts.headers || {};
                try{
                    const t = localStorage.getItem('FORNEGO_API_TOKEN');
                    if(t){
                        opts.headers['Authorization'] = 'Bearer ' + t;
                    }
                }catch(e){}
                return _fetch(url, opts);
            };

            window.setApiToken = function(){
                const t = prompt('Enter API token (will be stored in browser localStorage):');
                if(t){ localStorage.setItem('FORNEGO_API_TOKEN', t); alert('Token saved to localStorage'); }
            };
        })();
    </script>

    <div class="section">
        <h2>📊 Database Statistics</h2>
        <div id="stats"></div>
    </div>

    <div class="section">
        <h2>🗺️ Map Generation</h2>
        <div class="form-group">
            <label>Map Type:</label>
            <select id="mapType">
                <option value="multi">Multi-Layer (Default)</option>
                <option value="heatmap">Density Heatmap</option>
                <option value="hexagon">H3 Hexagons</option>
                <option value="cluster">Clustered Markers</option>
                <option value="trajectory">Movement Trajectory</option>
                <option value="comparison">Device Comparison</option>
            </select>
        </div>
        <div class="form-group">
            <label>Device ID (optional):</label>
            <input type="text" id="deviceId" placeholder="Leave empty for all devices">
        </div>
        <button onclick="generateMap()">Generate Map</button>
        <div id="mapResult"></div>
    </div>

    <div class="section">
        <h2>🔍 Spatial Query</h2>
        <div class="grid">
            <div class="form-group">
                <label>Latitude:</label>
                <input type="number" id="queryLat" value="40.7128" step="0.0001">
            </div>
            <div class="form-group">
                <label>Longitude:</label>
                <input type="number" id="queryLon" value="-74.0060" step="0.0001">
            </div>
            <div class="form-group">
                <label>Radius (km):</label>
                <input type="number" id="queryRadius" value="1.0" step="0.1" min="0">
            </div>
        </div>
        <button onclick="spatialQuery()">Query</button>
        <div id="queryResult"></div>
    </div>

    <div class="section">
        <h2>🔥 Hotspot Analysis</h2>
        <div class="form-group">
            <label>Device ID (optional):</label>
            <input type="text" id="hotspotDevice" placeholder="Leave empty for all devices">
        </div>
        <div class="form-group">
            <label>Days:</label>
            <input type="number" id="hotspotDays" value="30" min="1">
        </div>
        <button onclick="getHotspots()">Analyze Hotspots</button>
        <div id="hotspotResult"></div>
    </div>

    <div class="section">
        <h2>� Phone OSINT</h2>
        <div class="form-group">
            <label>Phone Number:</label>
            <input type="text" id="phoneNumber" placeholder="+91 98765 43210 or +1 202-555-0143">
        </div>
        <div class="form-group">
            <label>Content to Scan:</label>
            <textarea id="phoneContent" rows="4" placeholder="Paste content containing phone numbers..."></textarea>
        </div>
        <div class="button-group">
            <button onclick="phoneOsint()">Enrich Number</button>
            <button onclick="extractPhone()">Extract Numbers</button>
        </div>
        <div id="phoneResult"></div>
    </div>

    <div class="section">
        <h2>🤖 Android Artifact Analysis</h2>
        <div class="form-group">
            <label>Artifact Content:</label>
            <textarea id="androidContent" rows="5" placeholder="Paste Android artifact text or JSON here..."></textarea>
        </div>
        <button onclick="analyzeAndroid()">Analyze Android Artifacts</button>
        <div id="androidResult"></div>
    </div>

    <div class="section">
        <h2>🐧 Linux Forensic Log Analysis</h2>
        <div class="form-group">
            <label>Log Content:</label>
            <textarea id="linuxContent" rows="5" placeholder="Paste Linux log or artifact text here..."></textarea>
        </div>
        <button onclick="analyzeLinux()">Analyze Linux Logs</button>
        <div id="linuxResult"></div>
    </div>

    <div class="section">
        <h2>�🕵️ Deep Web Analysis</h2>
        <div class="form-group">
            <label>Content to Analyze:</label>
            <textarea id="deepwebContent" rows="5" placeholder="Paste content containing potential dark web indicators..."></textarea>
        </div>
        <button onclick="analyzeDeepweb()">Analyze</button>
        <div id="deepwebResult"></div>
    </div>

    <script>
        function showResult(elementId, data, isError = false) {
            const element = document.getElementById(elementId);
            if (isError) {
                element.innerHTML = `<div class="error">${data}</div>`;
            } else {
                element.innerHTML = `<div class="success"><pre>${JSON.stringify(data, null, 2)}</pre></div>`;
            }
        }

        function getStatus() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    let html = '';
                    for (const [key, value] of Object.entries(data)) {
                        html += `<div class="stat-box"><div class="value">${value}</div><div class="label">${key}</div></div>`;
                    }
                    document.getElementById('stats').innerHTML = html;
                })
                .catch(e => showResult('stats', 'Failed to load statistics', true));
        }

        function generateMap() {
            const mapType = document.getElementById('mapType').value;
            const deviceId = document.getElementById('deviceId').value;
            const params = new URLSearchParams();
            if (mapType) params.append('type', mapType);
            if (deviceId) params.append('device', deviceId);

            fetch(`/api/map?${params}`)
                .then(r => r.json())
                .then(data => {
                    if (data.file) {
                        document.getElementById('mapResult').innerHTML = 
                            `<div class="info">✅ Map generated! <a href="${data.file}" target="_blank">View Map</a></div>`;
                    } else {
                        showResult('mapResult', data.error || 'Failed to generate map', true);
                    }
                })
                .catch(e => showResult('mapResult', e.message, true));
        }

        function spatialQuery() {
            const lat = parseFloat(document.getElementById('queryLat').value);
            const lon = parseFloat(document.getElementById('queryLon').value);
            const radius = parseFloat(document.getElementById('queryRadius').value);

            fetch(`/api/query/${lat}/${lon}/${radius}`)
                .then(r => r.json())
                .then(data => showResult('queryResult', data))
                .catch(e => showResult('queryResult', e.message, true));
        }

        function getHotspots() {
            const device = document.getElementById('hotspotDevice').value;
            const days = document.getElementById('hotspotDays').value;
            const params = new URLSearchParams();
            if (device) params.append('device', device);
            if (days) params.append('days', days);

            fetch(`/api/hotspots?${params}`)
                .then(r => r.json())
                .then(data => showResult('hotspotResult', data))
                .catch(e => showResult('hotspotResult', e.message, true));
        }

        function extractPhone() {
            const content = document.getElementById('phoneContent').value;
            if (!content.trim()) {
                showResult('phoneResult', 'Please enter content to scan', true);
                return;
            }

            fetch('/api/phone/extract', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            })
                .then(r => r.json())
                .then(data => showResult('phoneResult', data))
                .catch(e => showResult('phoneResult', e.message, true));
        }

        function phoneOsint() {
            const phone = document.getElementById('phoneNumber').value;
            const content = document.getElementById('phoneContent').value;
            if (!phone.trim() && !content.trim()) {
                showResult('phoneResult', 'Provide a phone number or content to enrich', true);
                return;
            }

            fetch('/api/phone/osint', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone_number: phone, content })
            })
                .then(r => r.json())
                .then(data => showResult('phoneResult', data))
                .catch(e => showResult('phoneResult', e.message, true));
        }

        function analyzeAndroid() {
            const content = document.getElementById('androidContent').value;
            if (!content.trim()) {
                showResult('androidResult', 'Please enter Android artifact content', true);
                return;
            }

            fetch('/api/android/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            })
                .then(r => r.json())
                .then(data => showResult('androidResult', data))
                .catch(e => showResult('androidResult', e.message, true));
        }

        function analyzeLinux() {
            const content = document.getElementById('linuxContent').value;
            if (!content.trim()) {
                showResult('linuxResult', 'Please enter Linux log content', true);
                return;
            }

            fetch('/api/linux/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            })
                .then(r => r.json())
                .then(data => showResult('linuxResult', data))
                .catch(e => showResult('linuxResult', e.message, true));
        }

        function analyzeDeepweb() {
            const content = document.getElementById('deepwebContent').value;
            if (!content.trim()) {
                showResult('deepwebResult', 'Please enter content to analyze', true);
                return;
            }

            fetch('/api/deepweb/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content, metadata: {} })
            })
                .then(r => r.json())
                .then(data => showResult('deepwebResult', data))
                .catch(e => showResult('deepwebResult', e.message, true));
        }

        // Load stats on page load
        window.addEventListener('load', getStatus);
    </script>
    '''
)

# API Routes
@app.route('/')
def index():
    return render_template_string(INDEX_TEMPLATE)

@app.route('/api/status')
def status():
    try:
        indexer = get_indexer()
        if not indexer:
            return jsonify({'error': 'Database not initialized'}), 500
        stats = indexer.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.before_request
def require_api_token():
    """Require API token for /api/* endpoints if FORNEGO_API_TOKEN is set."""
    # allow static and UI routes
    if not request.path.startswith('/api/'):
        return None
    # always allow status
    if request.path == '/api/status':
        return None
    if not API_TOKEN:
        # no token configured -> allow access (backwards compatible)
        return None
    # check header or x-api-key
    auth = request.headers.get('Authorization', '')
    api_key = request.headers.get('X-API-KEY', '')
    if auth.startswith('Bearer '):
        token = auth.split(' ', 1)[1].strip()
    else:
        token = api_key
    if not token or token != API_TOKEN:
        return jsonify({'error': 'Unauthorized'}), 401

@app.route('/api/query/<float:lat>/<float:lon>/<float:radius>')
def query(lat, lon, radius):
    try:
        indexer = get_indexer()
        if not indexer:
            return jsonify({'error': 'Database not initialized'}), 500
        results = indexer.query_hex_neighbors(lat, lon, radius)
        return jsonify(results.to_dict('records') if not results.empty else [])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hotspots')
def hotspots():
    try:
        indexer = get_indexer()
        if not indexer:
            return jsonify({'error': 'Database not initialized'}), 500
        device_id = request.args.get('device')
        days = int(request.args.get('days', 30))
        hotspots_data = indexer.hotspot_analysis(device_id, days)
        return jsonify(hotspots_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reverse/<lat>/<lon>')
def reverse_geocode(lat, lon):
    try:
        indexer = get_indexer()
        if not indexer:
            return jsonify({'error': 'Database not initialized'}), 500
        lat_float = float(lat)
        lon_float = float(lon)
        return jsonify(indexer.reverse_geocode(lat_float, lon_float))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/map')
def generate_map():
    try:
        indexer = get_indexer()
        if not indexer:
            return jsonify({'error': 'Database not initialized'}), 500
        
        device_id = request.args.get('device')
        
        output_file = f"maps/forengeo_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        os.makedirs('maps', exist_ok=True)
        
        indexer.create_interactive_map(device_id, output_file)
        return jsonify({'file': f'/{output_file}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deepweb/analyze', methods=['POST'])
def analyze_deepweb():
    try:
        deepweb = get_deepweb()
        if not deepweb:
            return jsonify({'error': 'Deep web analyzer not initialized'}), 500
        
        data = request.get_json()
        content = data.get('content', '')
        metadata = data.get('metadata', {})
        
        results = deepweb.comprehensive_deepweb_analysis(content, metadata)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/phone/extract', methods=['POST'])
def extract_phone():
    """Extract phone numbers from content using regex pattern"""
    try:
        import re
        from phonenumbers import parse, is_valid_number
        
        data = request.get_json()
        content = data.get('content', '')
        
        # Phone regex patterns
        patterns = [
            r'\+?1?\s*\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})',  # US
            r'\+91[\s]?(\d{5})[\s.-]?(\d{5})',  # India
            r'\+\d{1,3}\s?\d{1,14}',  # General international
        ]
        
        phones = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    phone_str = ''.join(match)
                else:
                    phone_str = match
                phones.append(phone_str)
        
        return jsonify({'extracted_phones': list(set(phones)), 'count': len(set(phones))})
    except Exception as e:
        return jsonify({'error': str(e), 'extracted_phones': [], 'count': 0}), 400

@app.route('/api/phone/osint', methods=['POST'])
def phone_osint():
    """Perform OSINT enrichment on phone numbers"""
    try:
        import phonenumbers
        
        data = request.get_json()
        phone_number = data.get('phone_number', '').strip()
        content = data.get('content', '').strip()
        
        result = {'numbers': []}
        
        if phone_number:
            try:
                parsed = phonenumbers.parse(phone_number, None)
                result['numbers'].append({
                    'number': phone_number,
                    'country': phonenumbers.region_code_for_number(parsed),
                    'carrier': 'Unknown',
                    'type': phonenumbers.number_type(parsed),
                    'valid': phonenumbers.is_valid_number(parsed)
                })
            except Exception as e:
                result['error'] = str(e)
        elif content:
            import re
            patterns = [r'\+?1?\s*\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})', r'\+91[\s]?(\d{5})[\s.-]?(\d{5})']
            for pattern in patterns:
                for match in re.finditer(pattern, content):
                    number_str = match.group(0)
                    try:
                        parsed = phonenumbers.parse(number_str, None)
                        result['numbers'].append({
                            'number': number_str,
                            'country': phonenumbers.region_code_for_number(parsed),
                            'valid': phonenumbers.is_valid_number(parsed)
                        })
                    except:
                        pass
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'numbers': []}), 400

@app.route('/api/temporal', methods=['GET'])
def temporal_analysis():
    """Analyze temporal patterns in location data"""
    try:
        indexer = get_indexer()
        if not indexer:
            return jsonify({'error': 'Database not initialized'}), 500
        
        device_id = request.args.get('device')
        result = indexer.temporal_analysis(device_id)
        # Handle DataFrame result
        if result is not None:
            if hasattr(result, 'empty'):
                return jsonify(result.to_dict('list') if not result.empty else {'message': 'No temporal data available'})
            elif isinstance(result, dict):
                return jsonify(result)
            else:
                return jsonify({'data': str(result)})
        return jsonify({'message': 'No temporal data available'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/movement', methods=['GET'])
def movement_patterns():
    """Analyze movement patterns"""
    try:
        indexer = get_indexer()
        if not indexer:
            return jsonify({'error': 'Database not initialized'}), 500
        
        device_id = request.args.get('device')
        result = indexer.analyze_movement_patterns(device_id)
        return jsonify(result if result else {'message': 'No movement data available'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/anomalies', methods=['GET'])
def anomalies():
    """Detect spatial and temporal anomalies"""
    try:
        indexer = get_indexer()
        if not indexer:
            return jsonify({'error': 'Database not initialized'}), 500
        
        device_id = request.args.get('device')
        result = indexer.detect_anomalies(device_id)
        # Handle DataFrame result
        if result is not None:
            if hasattr(result, 'empty'):
                return jsonify(result.to_dict('list') if not result.empty else {'message': 'No anomalies detected'})
            elif isinstance(result, dict):
                return jsonify(result)
            else:
                return jsonify({'data': str(result)})
        return jsonify({'message': 'No anomalies detected'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/privacy-risk', methods=['GET'])
def privacy_risk():
    """Assess privacy risk and tracking vulnerability"""
    try:
        indexer = get_indexer()
        if not indexer:
            return jsonify({'error': 'Database not initialized'}), 500
        
        device_id = request.args.get('device')
        result = indexer.privacy_risk_assessment(device_id)
        return jsonify(result if result else {'message': 'No privacy risk data available'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deepweb/analysis', methods=['POST'])
def deepweb_analysis():
    """Comprehensive deep web and dark web analysis"""
    try:
        deepweb = get_deepweb()
        if not deepweb:
            return jsonify({'error': 'Deep web analyzer not initialized'}), 500
        
        data = request.get_json()
        content = data.get('content', '')
        metadata = data.get('metadata', {})
        
        results = deepweb.comprehensive_deepweb_analysis(content, metadata)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/kml', methods=['GET'])
def export_kml():
    """Export location data as KML for Google Earth"""
    try:
        indexer = get_indexer()
        if not indexer:
            return jsonify({'error': 'Database not initialized'}), 500
        
        device_id = request.args.get('device', None)
        output_file = f"maps/forengeo_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.kml"
        os.makedirs('maps', exist_ok=True)
        
        try:
            if device_id:
                indexer.export_kml(output_file, device_id)
            else:
                indexer.export_kml(output_file)
        except TypeError:
            # Fallback if device_id parameter not supported
            indexer.export_kml(output_file)
        
        return jsonify({'file': f'/{output_file}', 'format': 'KML'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export location data as Autopsy CSV"""
    try:
        indexer = get_indexer()
        if not indexer:
            return jsonify({'error': 'Database not initialized'}), 500
        
        case_id = request.args.get('case_id', 'web_export')
        output_dir = f"maps/autopsy_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs('autopsy_export', exist_ok=True)
        
        try:
            indexer.export_autopsy_csv(case_id, 'autopsy_export')
            output_file = f"autopsy_export/case_{case_id}_locations.csv"
        except Exception as e:
            # Fallback: create CSV manually
            import pandas as pd
            df = pd.read_sql("SELECT * FROM locations", indexer.conn)
            output_file = f"{output_dir}/locations.csv"
            df.to_csv(output_file, index=False)
        
        return jsonify({'file': f'/{output_file}', 'format': 'CSV'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/maps/<path:filename>')
def serve_map(filename):
    return send_from_directory('maps', filename)

if __name__ == '__main__':
    print("🚀 Starting ForenGeo Web UI...")
    print(f"📡 Access the web interface at http://{FORNEGO_HOST}:{FORNEGO_PORT}")
    print("Press Ctrl+C to stop the server")
    try:
        app.run(host=FORNEGO_HOST, port=FORNEGO_PORT, debug=FORNEGO_DEBUG)
    except KeyboardInterrupt:
        print("\n⛔ Server stopped")
