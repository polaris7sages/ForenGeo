# 🎯 ForenGeo - Complete Feature Guide

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Installation & Setup](#installation--setup)
3. [Core H3 Features](#core-h3-features)
4. [Map Visualizations](#map-visualizations)
5. [Forensic Analysis](#forensic-analysis)
6. [OSINT Features](#osint-features)
7. [Deep Web Forensics](#deep-web-forensics)
8. [Usage Examples](#usage-examples)
9. [Troubleshooting](#troubleshooting)

---

## System Overview

ForenGeo is an advanced forensic and OSINT analysis platform built on Uber's H3 geospatial indexing system. It combines:

- **H3 Geospatial Indexing**: Hierarchical hexagonal grid for efficient spatial queries
- **Forensic Analysis**: Chain of custody, evidence tracking, and anomaly detection
- **Map Visualization**: 6 different interactive map types for data exploration
- **Deep Web Forensics**: Cryptocurrency, Tor, and dark web analysis
- **OSINT Integration**: Geocoding, POI search, and address lookups

---

## Installation & Setup

### Requirements
- Python 3.9+
- 2GB RAM minimum
- Internet connection (for APIs)

### Quick Start
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize database
python3 fh3_cli.py init

# 3. Add evidence files
python3 fh3_cli.py add demo_locations.csv --case CASE001

# 4. View data
python3 fh3_cli.py stats
```

### Start Web Interface
```bash
python3 fh3_web.py
# Access at http://localhost:5000
```

---

## Core H3 Features

### H3 Geospatial Indexing

H3 converts geographic coordinates into hierarchical hexagonal indices. This enables:

#### **Spatial Queries**
```bash
# Find all locations within 5km of coordinates
python3 fh3_cli.py query 40.7128 -74.0060 --radius 5.0
```

**What it does:**
- Converts center point to H3 hexagon
- Finds all surrounding hexagons within radius
- Returns all location data in those hexagons
- 10x faster than radius-based queries

#### **Hotspot Detection**
```bash
# Find frequently visited locations
python3 fh3_cli.py hotspots device_001 --days 30
```

**Output:**
- Top visited H3 hexagons
- Visit counts per hexagon
- Latitude/longitude of each hotspot
- Temporal patterns

#### **Movement Analysis**
```bash
# Analyze movement patterns
python3 fh3_cli.py patterns device_001
```

**Features:**
- Detected home/work locations
- Travel speeds and routes
- Temporal patterns
- Geographic diversity

---

## Map Visualizations

### 6 Interactive Map Types

#### **1. Multi-Layer Map (DEFAULT)**
```bash
python3 fh3_cli.py map --type multi --device device_001
```

**Layers:**
- 🔥 Density heatmap (location intensity)
- 📍 Clustered markers (interactive points)
- 🔷 H3 hexagon hotspots (visit frequency)
- 📈 Timeline visualization (temporal progression)

**Best for:** Complete overview of device activity

#### **2. Density Heatmap**
```bash
python3 fh3_cli.py map --type heatmap --device device_001
```

**Features:**
- Red zones = high concentration
- Yellow zones = low concentration
- Smooth gradient visualization
- Real-time density calculation

**Best for:** Identifying activity clusters quickly

#### **3. H3 Hexagon Map**
```bash
python3 fh3_cli.py map --type hexagon --device device_001
```

**Features:**
- Each hexagon colored by visit count
- Size and color indicate frequency
- Interactive popups with statistics
- Resolution-based visualization

**Best for:** Understanding H3 indexing impact

#### **4. Clustered Markers**
```bash
python3 fh3_cli.py map --type cluster --device device_001
```

**Features:**
- Auto-zoom clustering
- Popup information on markers
- Device and timestamp details
- Performance optimized

**Best for:** Large datasets with many points

#### **5. Trajectory Map**
```bash
python3 fh3_cli.py map --type trajectory --device device_001
```

**Features:**
- Red line showing movement path
- Green marker = start point
- Red marker = end point
- Intermediate points numbered

**Best for:** Understanding movement routes

#### **6. Device Comparison**
```bash
python3 fh3_cli.py map --type comparison
```

**Features:**
- Different colors per device
- Overlapped movements
- Device-specific filtering
- Cross-device analysis

**Best for:** Multi-suspect analysis

---

## Forensic Analysis

### Anomaly Detection
```bash
python3 fh3_cli.py anomalies device_001
```

**Detects:**
- Unusual speed changes
- Impossible travel scenarios
- Sudden location jumps
- Behavioral outliers
- Statistical deviations

### Privacy Risk Assessment
```bash
python3 fh3_cli.py privacy device_001
```

**Evaluates:**
- Tracking vulnerability
- Location predictability
- Home/work inference risk
- Temporal patterns
- Geographic diversity

---

## OSINT Features

### Geocoding
```bash
# Convert address to coordinates
python3 fh3_cli.py geocode "Times Square, New York, NY"

# Reverse geocode coordinates
python3 fh3_cli.py revgeo 40.7128 -74.0060
```

### Point of Interest Search
```bash
# Find nearby amenities
python3 fh3_cli.py poi 40.7128 -74.0060 --type amenity --radius 1000
```

**Supported POI Types:**
- amenity (restaurants, shops, etc.)
- leisure (parks, entertainment)
- tourism (museums, landmarks)
- healthcare
- transportation

---

## Deep Web Forensics

### Content Analysis
```bash
python3 fh3_cli.py deepweb content.txt
```

**Analyzes:**
- Tor exit nodes
- Onion domains (.onion)
- Cryptocurrency addresses (BTC, ETH, XMR)
- Dark web marketplace indicators
- Hidden service patterns

### Cryptocurrency Detection
```python
# Detects multiple formats
BTC: bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
ETH: 0x32Be343B94f860124dC4fEe278FADBD03915C147
XMR: 4AdUndoRsTq6UvCGZ533ybuUFEMysqMDAO8GyC67sDM1AJDotWERXNiGicSJQeZo6MBjgoVWQYbNAqxX8KfHHPF3QbLcB69
```

### Report Generation
```bash
python3 fh3_cli.py deepweb-report --case CASE001 ./reports/
```

**Generates:**
- JSON report with findings
- Evidence extracted
- Timeline of activity
- Risk assessment

---

## Usage Examples

### Example 1: Suspect Location Analysis
```bash
# Initialize case
python3 fh3_cli.py init

# Add suspect's location data
python3 fh3_cli.py add suspect_locations.csv --case ROBBERY_001

# Find hotspots around crime scene
python3 fh3_cli.py query 40.7128 -74.0060 --radius 2.0

# Generate comprehensive map
python3 fh3_cli.py map --type multi --device suspect_phone --output suspect_movements.html

# Detect anomalies
python3 fh3_cli.py anomalies suspect_phone
```

### Example 2: Multi-Device Comparison
```bash
# Add multiple devices
python3 fh3_cli.py add device1_locations.csv --case CASE_A
python3 fh3_cli.py add device2_locations.csv --case CASE_A
python3 fh3_cli.py add device3_locations.csv --case CASE_A

# Create comparison map
python3 fh3_cli.py map --type comparison --output multi_device.html

# Compare hotspots
python3 fh3_cli.py hotspots device1 --days 30
python3 fh3_cli.py hotspots device2 --days 30
```

### Example 3: Deep Web Investigation
```bash
# Analyze suspected dark web content
python3 fh3_cli.py deepweb darkweb_logs.txt

# Generate forensics report
python3 fh3_cli.py deepweb-report --case DARKNET_001 ./reports/

# Correlate with device locations
python3 fh3_cli.py correlate-darkweb device_001
```

### Example 4: Web UI Analysis
```bash
# Start web server
python3 fh3_web.py

# Access at http://localhost:5000
# Use browser interface for:
# - Interactive map generation
# - Real-time queries
# - Deep web analysis
# - Statistics viewing
```

---

## Troubleshooting

### Issue: "No database. Run 'fh3 init'"
**Solution:**
```bash
python3 fh3_cli.py init
```

### Issue: API Rate Limits
**Solution:**
- Nominatim: Wait 1 second between requests
- Overpass: Query smaller areas
- Get premium API keys for higher limits

### Issue: Map Won't Display
**Solutions:**
1. Check browser compatibility (Chrome, Firefox recommended)
2. Ensure folium is installed: `pip install folium`
3. Try generating without layers: Use simple map type
4. Check for JavaScript errors in console (F12)

### Issue: Slow Queries
**Solutions:**
1. Use smaller radius for spatial queries
2. Filter by device_id when possible
3. Use lower H3 resolution for faster indexing
4. Index database with: `CREATE INDEX idx_device ON locations(device_id)`

### Issue: Memory Issues
**Solutions:**
1. Process large datasets in batches
2. Close database connections: `indexer.close()`
3. Delete old databases: `rm old.db`
4. Reduce H3 resolution (9-10 optimal)

---

## Advanced Configuration

### API Keys
```bash
# Optional: Set OpenWeatherMap API key
export OPENWEATHER_API_KEY="your_key_here"

# Optional: Set Etherscan API key
export ETHERSCAN_API_KEY="your_key_here"
```

### H3 Resolution Levels
```python
Resolution 0-2:  Global scale
Resolution 3-5:  Continental scale
Resolution 6-8:  Regional scale
Resolution 9-10: City scale (recommended)
Resolution 11-13: Building scale
Resolution 14-15: Micro scale
```

---

## Performance Tips

1. **Use appropriate resolution**: 9-10 for most cases
2. **Index frequently queried fields**
3. **Close connections after use**
4. **Use device_id filter for queries**
5. **Batch import large datasets**
6. **Clean up old test databases**

---

## Support & Documentation

- **CLI Help**: `python3 fh3_cli.py --help`
- **Web UI**: Run `python3 fh3_web.py` then visit http://localhost:5000
- **Test Suite**: Run `python3 test_forengeo.py`
- **Integration Tests**: Run `python3 test_integration.py`
- **Demo**: Run `python3 demo_all_features.py`

---

## License & Attribution

ForenGeo uses:
- **H3**: Uber's hierarchical hexagonal geospatial index
- **Folium**: Interactive maps
- **Nominatim**: OpenStreetMap geocoding
- **GeoPy**: Geospatial calculations

Built for forensic investigation and OSINT analysis.
