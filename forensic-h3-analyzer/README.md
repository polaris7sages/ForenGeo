# ForenGeo - Advanced H3 Forensic & OSINT Analyzer

## Project Report
**Rashtriya Raksha University, Lucknow Campus**  
**Project:** GEOSPATIAL INDEXING  
**Submitted By:** Dhruv Kumar Singh  
**Enrollment No.:** 25020111025081004  
**Submitted To:** Mr. Akash Mishra, Assistant Professor, Digital Forensics  
**Date:** May 2026  

## Abstract
ForenGeo is a Python-based digital forensics and open-source intelligence (OSINT) system built on Uber H3 geospatial indexing. It integrates evidence ingestion, spatial analysis, phone and entity OSINT, and deep web correlation into a single investigative platform.

## Introduction
ForenGeo demonstrates how advanced geospatial indexing can improve the accuracy and utility of location-based digital evidence. The system processes location logs, extracts intelligence from phone numbers, analyzes Android and Linux artifacts, and visualizes results with interactive H3 maps.

## Objectives
- Leverage Uber H3 hierarchical geospatial indexing for forensic location analysis.
- Build an integrated forensic and OSINT workflow for mobile and web investigations.
- Support phone number extraction, Android/Linux artifact analysis, and entity graph generation.
- Provide multi-interface access through CLI, web UI, and Python API.

## Scope
ForenGeo focuses on local evidence analysis and correlation rather than cloud-based data collection. It supports CSV/plist evidence ingestion, SQLite-backed storage, H3 spatial querying, OSINT enrichment, and HTML map export.

## Unique Contribution
- **Native H3 geospatial indexing:** Enables scalable, hierarchical spatial queries and hotspot detection.
- **Forensic + OSINT integration:** Combines evidence analysis, phone intelligence, and dark web correlation in one tool.
- **Entity mapping:** Generates Maltego-style entity relationships with geospatial context.
- **Privacy-first design:** Performs core analysis locally with optional external OSINT API use.

## Methodology
1. Ingest location and evidence data into a SQLite-backed forensic database.
2. Convert lat/lon points to H3 indices for hierarchical spatial analysis.
3. Perform forensic analytics including hotspots, anomalies, and movement patterns.
4. Enrich data with OSINT features: reverse geocoding, POI search, phone number analysis, and entity extraction.
5. Correlate findings with deep web indicators such as Tor, onion domains, and cryptocurrency addresses.
6. Visualize output as interactive Folium maps, KML, CSV, and JSON reports.

## Accuracy and Validation
- **H3 spatial accuracy:** High precision at resolutions 12-15 with consistent hexagon neighbor calculations.
- **Forensic accuracy:** Hotspot and anomaly detection use proven statistical methods.
- **OSINT accuracy:** Reverse geocoding and POI search rely on OpenStreetMap for strong location coverage.
- **Deep web accuracy:** Tor detection and cryptocurrency extraction use validated data patterns.

## Advantages
- Superior spatial analysis with H3 hierarchical indexing
- Fast, efficient spatial queries and multi-resolution analysis
- Integrated forensic, OSINT, and dark web analysis
- Chain of custody support with cryptographic evidence hashes
- Export-ready HTML maps, KML, CSV, and JSON results

## Disadvantages
- External APIs are required for some OSINT enrichment features
- Depends on Python libraries such as H3, Pandas, and Folium
- Not a commercial-forensic suite; intended for academic and investigative research
- Very large datasets may be limited by SQLite performance in some environments

## Execution Overview
ForenGeo supports command-line, web UI, and Python API workflows. See the `Usage` section below for detailed commands and examples.

## Results and Conclusion
ForenGeo proves that H3 geospatial indexing enhances digital forensic investigations, providing accurate location analysis, intelligent entity mapping, and strong investigative reporting capabilities. The tool delivers a practical, privacy-focused research system for forensic professionals.

## 🌟 Key Features

### 🔍 **Full H3Geo Potential**
- **Hierarchical Indexing**: Multi-resolution H3 grids (resolutions 0-15)
- **Spatial Queries**: Efficient k-ring and hex-range neighbor searches
- **Polygon Filling**: Convert areas to H3 hexagon sets
- **Grid Distances**: Calculate H3-based distances and paths
- **Edge Analysis**: H3 edge lengths and boundary calculations

### 🕵️ **Digital Forensics**
- **Chain of Custody**: Cryptographic verification with SHA-256 hashing
- **Evidence Import**: Support for iOS plist and CSV location data
- **Anomaly Detection**: Statistical analysis of location patterns
- **Temporal Analysis**: Time-based movement pattern recognition
- **Autopsy Integration**: Export to CSV for forensic tools
- **Deep Web Correlation**: Link clearnet activity with dark web patterns

### 🌐 **OSINT Capabilities**
- **Reverse Geocoding**: Convert coordinates to addresses (Nominatim)
- **POI Search**: Find points of interest via Overpass API
- **Address Geocoding**: Convert addresses to coordinates
- **Phone OSINT**: Extract and classify Indian + international phone numbers from text and artifacts
- **Phone Enrichment**: Carrier, country, type, and risk profiling for phone contacts
- **Entity Graph Extraction**: Build Maltego-style entity relationships from text, phones, IPs, domains, and locations
- **Weather Integration**: Location-based weather data (API key required)
- **Privacy Assessment**: Risk analysis of location tracking

### 🕵️ **Deep Web Forensics**
- **Tor Network Analysis**: Exit node detection and correlation
- **Onion Domain Analysis**: Hidden service discovery and classification
- **Cryptocurrency Tracking**: BTC, XMR, ETH address extraction and analysis
- **Dark Web Marketplace Monitoring**: Product and vendor analysis
- **Identity Correlation**: Clearnet/darknet identity linking
- **Dark Web Content Analysis**: Comprehensive forensic examination
- **Phone Number OSINT**: Indian + international phone extraction, carrier/country classification, and enriched metadata
- **Android Artifact Inspection**: SMS, call history, IMEI, Android ID, and forensic artifact analysis
- **Linux Log Forensics**: Suspicious login, SSH/cron/systemd, and phone-related evidence extraction

### 📊 **Daily Life Applications**
- **Movement Pattern Analysis**: Detect home/work locations
- **Travel Analysis**: Route reconstruction and speed analysis
- **Privacy Risk Assessment**: Evaluate tracking predictability
- **Hotspot Detection**: Identify frequently visited locations
- **Temporal Clustering**: Analyze activity by time of day/week

### 🗺️ **Advanced Map Visualizations** (NEW!)
- **Multi-Layer Maps**: Heatmaps + hexagons + markers + timeline in one view
- **Density Heatmaps**: Color-coded location concentration visualization
- **H3 Hexagon Maps**: Interactive hexagon grid with visit counts
- **Clustered Markers**: Auto-zoom clustering for large datasets
- **Trajectory Maps**: Movement path visualization with start/end markers
- **Device Comparison**: Overlay multiple devices for correlation analysis
- **OSINT Entity Maps**: Plot extracted entities and relationships on geospatial maps

### 🌐 **Web Interface** (NEW!)
- **Modern Web UI**: Professional dashboard at http://localhost:5000
- **Interactive Maps**: Generate maps directly from browser
- **Real-time API**: RESTful endpoints for all analysis functions
- **OSINT Endpoints**: Phone extraction, phone enrichment, entity analysis, and graph export
- **Live Statistics**: Database stats and device information
- **Map Export**: Download high-quality HTML map files

## ⚙️ Configuration

### API Keys Setup
For enhanced OSINT features, set up the following environment variables:

```bash
# OpenWeatherMap API (for weather data)
export OPENWEATHER_API_KEY="your_api_key_here"

# Etherscan API (for Ethereum blockchain analysis)
export ETHERSCAN_API_KEY="your_api_key_here"
```

Get API keys from:
- [OpenWeatherMap](https://openweathermap.org/api) (free tier available)
- [Etherscan](https://etherscan.io/apis) (free tier available)

## 🔐 DevSecOps & Secure Delivery

ForenGeo now includes a secure development lifecycle that keeps quality, security, and deployment checks repeatable and automated.

Key DevSecOps assets included in this repository:
- `.github/workflows/ci.yml` for automated build, lint, test, and security scanning on push/PR
- `requirements-dev.txt` for reproducible developer tooling
- `test_devsecops.py` for deterministic local unit coverage
- `DemoDevSecOps` workflow with `demo_devsecops.py` to verify functionality and map generation
- `Dockerfile` hardened with a non-root runtime user and minimal image build
- `docker-entrypoint.sh` for first-run database initialization and Gunicorn startup
- `Procfile` included for Heroku and PaaS deployment compatibility
- `.gitignore` and `.dockerignore` to keep temporary artifacts out of source control and containers

How to run the DevSecOps workflow locally:

```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest -q test_devsecops.py
python3 demo_devsecops.py
```

Build a container for staging or deployment:

```bash
docker build -t forengeo .
docker run --rm -p 5000:5000 forengeo
```

Persistent storage and volume example

```bash
# Persist the database and maps to the host
docker run --rm -p 5000:5000 \
	-v "$(pwd)/.fh3.db:/app/.fh3.db" \
	-v "$(pwd)/maps:/app/maps" \
	forengeo
```

This keeps the `.fh3.db` and generated maps on your host filesystem so they survive container restarts.

API authentication

You can secure the API by setting an API token in the container environment variable `FORNEGO_API_TOKEN`. When set, all `/api/*` endpoints (except `/api/status`) require the token via the `Authorization: Bearer <token>` header or `X-API-KEY` header.

Example Docker run with token:

```bash
docker run --rm -p 5000:5000 \
	-e FORNEGO_API_TOKEN="mysecret" \
	-v "$(pwd)/.fh3.db:/app/.fh3.db" \
	-v "$(pwd)/maps:/app/maps" \
	forengeo
```

For SaaS-style deployment, the container launches a production-ready Gunicorn server from `fh3_web:app` and initializes the `.fh3.db` database automatically on first startup.

Optional local compose deployment:

```bash
docker compose up --build
```

## �🛠️ Troubleshooting

### Common Issues

**H3 Installation Issues**
```bash
# If H3 fails to install on some systems
pip install h3 --no-binary h3
```

**Database Errors**
- Ensure write permissions in the working directory
- Delete `.fh3.db` and `deepweb.db` if corrupted and re-run `fh3 init`

**API Rate Limits**
- OSINT features use free APIs with rate limits
- Wait a few minutes between requests or get premium API keys

**Geocoding Failures**
- Nominatim has rate limits; consider using Google Maps API for production
- Check internet connection

**Deep Web Analysis**
- Regex-based detection; may have false positives
- Blockchain APIs require internet and may have limits

**GUI Issues**
- Ensure Tkinter is installed (`apt install python3-tk` on Ubuntu)
- For map previews, ensure a web browser is available

### Performance Tips
- Use H3 resolution 9-10 for balance of accuracy and performance
- Index large datasets before analysis
- Close database connections after use

### Getting Help
- Check test outputs in `test_reports/`
- Run individual tests: `python test_forengeo.py`
- For deep web: `python test_deepweb.py`
- View comprehensive feature guide: `FEATURES.md`
- Quick start guide: `QUICKSTART.md`
- Run feature demo: `python3 demo_all_features.py`

## 📖 Usage

### 🌐 Web Interface (Recommended for Most Users)
```bash
# Start the web UI
python3 fh3_web.py

# Access in your browser at http://localhost:5000
# Features:
# - Interactive map generation (6 types)
# - Spatial queries
# - Hotspot analysis
# - Deep web forensics
# - Real-time statistics
```

### 💻 CLI Commands (git-like interface)

```bash
# Initialize database
./fh3_cli.py init

# Import evidence files
./fh3_cli.py add suspect_phone.plist --case MURDER2024

# Spatial queries
./fh3_cli.py query 40.7128 -74.0060 --radius 2.0

# Analysis commands
./fh3_cli.py hotspots iPhone123 --days 30
./fh3_cli.py anomalies iPhone123
./fh3_cli.py patterns iPhone123
./fh3_cli.py privacy iPhone123

# OSINT features
./fh3_cli.py revgeo 40.7128 -74.0060
./fh3_cli.py geocode "1600 Pennsylvania Avenue, Washington DC"
./fh3_cli.py poi 40.7128 -74.0060 --radius 500 --type amenity
./fh3_cli.py extract-phone --text "+91 98765 43210 or +1-202-555-0143"
./fh3_cli.py phone-osint --phone "+91 98765 43210"
./fh3_cli.py phone-osint --text "Contact +1-202-555-0143 from India"
./fh3_cli.py osint --file suspicious_text.txt --case OSINT2026
./fh3_cli.py export-graph --output entity_graph.json
./fh3_cli.py entity-map --output entity_map.html

# Android/Linux forensics
./fh3_cli.py android android_artifact.db --case ANDROID123
./fh3_cli.py linux /var/log/auth.log --keywords ssh login cron

# Export options
./fh3_cli.py map --device iPhone123 --output case_map.html --type multi
./fh3_cli.py map --device iPhone123 --type heatmap --output heatmap.html
./fh3_cli.py map --device iPhone123 --type trajectory --output path.html
./fh3_cli.py map --device iPhone123 --type comparison --output all_devices.html
./fh3_cli.py map --device iPhone123 --type osint --output entity_map.html
./fh3_cli.py kml --device iPhone123 --output locations.kml
./fh3_cli.py status
./fh3_cli.py export --case MURDER2024 exported_data
./fh3_cli.py stats

# Deep Web Forensics
./fh3_cli.py deepweb suspicious_content.txt
./fh3_cli.py deepweb-report --case DARKWEB2024 reports/
./fh3_cli.py correlate-darkweb iPhone123
```

### Web Interfaces

#### Modern Web Dashboard (NEW!)
```bash
python3 fh3_web.py
# Access at http://localhost:5000
# Features:
# - Professional UI for all operations
# - Interactive map generation
# - Real-time queries and analysis
# - OSINT phone and entity analysis
# - Entity graph export and map generation
# - Database statistics
# - Map file downloads
```

#### Server API (Legacy)
```bash
python3 fh3_server.py
```
- `GET /query/<lat>/<lon>/<radius>` returns matching locations
- `GET /status` returns database statistics
- `GET /hotspots?device=<id>&days=30` returns hotspot counts
- `GET /reverse?lat=<lat>&lon=<lon>` returns reverse geocode data
- `POST /deepweb/analyze` analyzes content for dark web indicators
- `GET /deepweb/tor/<ip>` checks if IP is Tor exit node
- `GET /deepweb/report/<case_id>` generates deep web report

## 📊 Data Sources & Processing

ForenGeo operates with a **privacy-first approach** - all analysis is performed locally with no data transmission to external servers except where explicitly requested for OSINT features.

### 🔍 **H3 Geospatial Engine**
- **Data Source**: Local computation using Uber H3 library (no external data)
- **Process**: Converts latitude/longitude coordinates to H3 hexagonal indices for spatial analysis
- **Output**: H3 indices, spatial relationships, distance calculations, hierarchical grids

### 📍 **Location Data Processing**
- **Data Source**: User-provided evidence files (CSV, plist) or API inputs
- **Process**: Parse location data with validation, store in SQLite with metadata and chain of custody
- **Output**: Forensic database with cryptographic hashing for evidence integrity

### 🌐 **OSINT Features**
- **Reverse Geocoding**: OpenStreetMap Nominatim API (free, rate-limited)
- **POI Search**: OpenStreetMap Overpass API for points of interest
- **Weather Data**: OpenWeatherMap API (requires API key)
- **Process**: External API calls only when requested, results cached locally
- **Privacy**: No location data sent without explicit user consent

### 🕵️ **Deep Web Forensics**
- **Tor Analysis**: Local regex pattern matching + Tor Project bulk exit list API
- **Onion Domains**: Local regex extraction from user content (no .onion access)
- **Cryptocurrency**: Local pattern matching for BTC/XMR/ETH addresses
- **Marketplace Analysis**: Content pattern recognition for dark web marketplace indicators
- **Process**: All analysis performed locally on user-provided content
- **Privacy**: No external data transmission, maintains forensic chain of custody

### 🔗 **Integration & Correlation**
- **Geospatial-Deep Web Correlation**: Links location data with dark web activity patterns
- **Identity Correlation**: Matches clearnet and darknet identities based on patterns
- **Temporal Analysis**: Correlates timing of location changes with online activities
- **Output**: Comprehensive correlation reports with confidence scores

## 🛠️ Architecture

```
ForenGeo/
├── forensic_h3_fixed.py      # Core H3 geospatial analyzer
├── deepweb_forensics.py      # Deep web analysis module
├── fh3_cli.py               # Command-line interface
├── fh3_server.py           # Flask REST API server
├── test_*.py               # Test suites
└── requirements.txt         # Python dependencies
```

### Database Schema
- **locations**: Device locations with H3 indices and metadata
- **poi_data**: Points of interest and OSINT data
- **movement_patterns**: Analyzed movement behaviors
- **tor_analysis**: Tor exit node data and correlations
- **onion_domains**: Discovered .onion services
- **crypto_transactions**: Cryptocurrency address tracking
- **marketplace_data**: Dark web marketplace analysis
- **identity_correlations**: Clearnet/darknet identity linking

## 🔒 Privacy & Security

- **Local Processing**: All core analysis performed locally
- **Chain of Custody**: Cryptographic verification of evidence integrity
- **No Data Exfiltration**: Location data never transmitted without explicit consent
- **Forensic Standards**: Designed for law enforcement and digital forensics use
- **Open Source**: Transparent analysis methods and algorithms

## 🧪 Testing

```bash
# Run all tests
python3 test_forengeo.py
python3 test_deepweb.py
python3 test_integration.py

# Compile check
python3 -m py_compile *.py
```

## 📈 Performance

- **H3 Indexing**: Sub-millisecond lat/lon to H3 conversion
- **Spatial Queries**: Efficient hexagonal neighbor searches
- **Database**: SQLite with optimized indexes for forensic workloads
- **Memory**: Minimal memory footprint for large datasets
- **Scalability**: Handles millions of location points

## 🤝 Contributing

ForenGeo is designed for the digital forensics community. Contributions welcome for:
- Additional H3 analysis algorithms
- New OSINT data sources
- Enhanced deep web pattern recognition
- Performance optimizations
- Forensic tool integrations

## 📄 License

Open source - see LICENSE file for details.

## ⚠️ Legal Notice

ForenGeo is a digital forensics tool designed for authorized law enforcement and security research use. Users are responsible for complying with applicable laws and regulations regarding digital evidence collection and analysis.
- `GET /correlate/darkweb/<device_id>` correlates locations with dark web activity

### GUI Interface

```bash
python fh3_gui.py
```

Features:
- Interactive map visualization with Folium
- Device selection and filtering
- Real-time spatial queries
- Analysis result display
- Export to multiple formats

### Python API

```python
from forensic_h3_fixed import ForensicH3Analyzer

# Initialize analyzer
analyzer = ForensicH3Analyzer("case.db", resolution=9)

# Add location data
analyzer.add_location(40.7128, -74.0060, "2024-01-01T12:00:00Z", "iPhone123")

# Advanced H3 operations
h3_index = analyzer.geo_to_h3(40.7128, -74.0060)
neighbors = analyzer.k_ring(h3_index, 3)
distance = analyzer.h3_distance(h3_index, another_h3)

# OSINT features
address = analyzer.reverse_geocode(40.7128, -74.0060)
pois = analyzer.search_poi_nearby(40.7128, -74.0060, 1000, 'amenity')

# Forensic analysis
hotspots = analyzer.hotspot_analysis("iPhone123")
anomalies = analyzer.detect_anomalies("iPhone123")
patterns = analyzer.analyze_movement_patterns("iPhone123")
privacy = analyzer.privacy_risk_assessment("iPhone123")

# Deep Web Forensics
from deepweb_forensics import DeepWebForensics
deepweb = DeepWebForensics()
results = deepweb.comprehensive_deepweb_analysis(content)
correlations = analyzer.correlate_darkweb_locations("iPhone123")

analyzer.close()
deepweb.close()
```

## 🔧 Technical Details

### H3 Resolutions Used
- **Resolution 7-9**: Optimal for city-level analysis (~5-70km edge length)
- **Resolution 10-12**: Street-level detail (~1-7km edge length)
- **Resolution 13-15**: Building-level precision (~0.5-1km edge length)

### Database Schema
- **locations**: Core location data with H3 indices
- **poi_data**: Cached points of interest
- **movement_patterns**: Analyzed movement data

### Privacy & Ethics
- All analysis is local - no data sent to external servers (except optional OSINT APIs)
- Chain of custody ensures evidence integrity
- Privacy risk assessment helps users understand tracking implications

## 🎯 Unique Advantages Over Other OSINT Tools

1. **H3 Hexagonal Grid**: More accurate spatial clustering than square grids
2. **Hierarchical Analysis**: Multi-scale analysis from global to local
3. **Efficient Queries**: H3's optimized neighbor and distance calculations
4. **Forensic Focus**: Evidence handling with cryptographic verification
5. **Pure Python**: No external dependencies beyond standard libraries
6. **Daily Life Relevance**: Beyond security - personal location intelligence
7. **Deep Web Integration**: Comprehensive dark web forensics and correlation analysis

## 📋 Requirements

- Python 3.8+
- SQLite3
- Internet connection (for OSINT features)
- Optional: OpenWeatherMap API key for weather data

## 🤝 Contributing

Contributions welcome! Focus areas:
- Additional H3 feature implementations
- New OSINT data sources
- Enhanced visualization
- Performance optimizations
- Mobile app integration

## 📄 License

MIT License - see LICENSE file for details.

---

**ForenGeo**: Where H3 meets digital forensics and OSINT intelligence.