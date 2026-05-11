from flask import Flask, request, jsonify
from forensic_h3_fixed import ForensicH3Analyzer
from deepweb_forensics import DeepWebForensics

app = Flask(__name__)
indexer = ForensicH3Analyzer('.fh3.db')
deepweb = DeepWebForensics()

@app.route('/query/<float:lat>/<float:lon>/<float:radius>')
def query(lat, lon, radius):
    results = indexer.query_hex_neighbors(lat, lon, radius)
    return jsonify(results.to_dict('records'))

@app.route('/status')
def status():
    return jsonify(indexer.get_statistics())

@app.route('/hotspots')
def hotspots():
    device_id = request.args.get('device')
    days = int(request.args.get('days', 30))
    return jsonify(indexer.hotspot_analysis(device_id, days))

@app.route('/reverse')
def reverse_geocode():
    lat = float(request.args.get('lat', 0))
    lon = float(request.args.get('lon', 0))
    return jsonify(indexer.reverse_geocode(lat, lon))

@app.route('/deepweb/analyze', methods=['POST'])
def analyze_deepweb():
    content = request.json.get('content', '')
    metadata = request.json.get('metadata', {})
    results = deepweb.comprehensive_deepweb_analysis(content, metadata)
    return jsonify(results)

@app.route('/deepweb/tor/<ip>')
def check_tor_exit(ip):
    is_exit = deepweb._is_tor_exit_node(ip)
    return jsonify({'ip': ip, 'is_tor_exit': is_exit})

@app.route('/deepweb/report/<case_id>')
def generate_deepweb_report(case_id):
    report_path = deepweb.generate_deepweb_report(case_id)
    return jsonify({'report_path': report_path, 'case_id': case_id})

@app.route('/correlate/darkweb/<device_id>')
def correlate_darkweb(device_id):
    correlations = indexer.correlate_darkweb_locations(device_id)
    return jsonify({'device_id': device_id, 'correlations': correlations})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)