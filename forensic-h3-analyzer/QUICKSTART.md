# 🚀 ForenGeo Quick Start Guide

Get up and running with ForenGeo in 5 minutes!

## ⚡ 30-Second Setup

```bash
# 1. Initialize database
python3 fh3_cli.py init

# 2. Add your data
python3 fh3_cli.py add your_locations.csv --case YOUR_CASE_ID

# 3. View your data
python3 fh3_cli.py stats

# 4. Generate map
python3 fh3_cli.py map --type multi

# Done! Open map.html in your browser
```

---

## 🌐 Choose Your Interface

### Option 1: Command Line (Fast & Powerful)
```bash
python3 fh3_cli.py --help
```

**Best for:**
- Scripting and automation
- Batch processing
- Integration with other tools

### Option 2: Web UI (User-Friendly)
```bash
python3 fh3_web.py
# Visit http://localhost:5000
```

**Best for:**
- Interactive exploration
- Real-time analysis
- Non-technical users

### Option 3: GUI (Desktop Application)
```bash
python3 fh3_gui.py
```

**Best for:**
- Traditional users
- Point-and-click interface
- Windows/Mac users

---

## 📊 5 Essential Commands

### 1. View Database Info
```bash
python3 fh3_cli.py stats
# Shows: total locations, devices, hexes, POIs
```

### 2. Find Hotspots
```bash
python3 fh3_cli.py hotspots device_001 --days 30
# Shows: top visited locations for the device
```

### 3. Query Location
```bash
python3 fh3_cli.py query 40.7128 -74.0060 --radius 5.0
# Shows: all locations within 5km
```

### 4. Generate Maps
```bash
# Multi-layer (best for overview)
python3 fh3_cli.py map --type multi

# Density heatmap (see concentration)
python3 fh3_cli.py map --type heatmap

# Movement trajectory (see path)
python3 fh3_cli.py map --type trajectory

# Device comparison (compare multiple devices)
python3 fh3_cli.py map --type comparison
```

### 5. Analyze Deep Web Content
```bash
python3 fh3_cli.py deepweb suspicious_content.txt
# Detects: Tor, onion domains, crypto addresses
```

---

## 📁 Input Data Format

### CSV Format (Recommended)
```csv
timestamp,lat,lon,device_id,app_name
2024-01-01T10:00:00,40.7128,-74.0060,phone_001,Chrome
2024-01-01T11:00:00,40.7589,-73.9851,phone_001,Maps
```

### iOS Plist Format
ForenGeo automatically extracts:
```
Latitude, Longitude, Timestamp, AppName, Altitude, etc.
```

### Just Coordinates?
```csv
lat,lon
40.7128,-74.0060
40.7589,-73.9851
```

---

## 🗺️ Map Types Explained

| Map Type | Use Case | Best For |
|----------|----------|----------|
| **Multi-layer** | Complete overview | General analysis |
| **Heatmap** | See activity density | Hotspot detection |
| **Hexagon** | H3 grid visualization | Understanding hexagons |
| **Cluster** | Large datasets | 1000+ points |
| **Trajectory** | Movement path | Tracking person |
| **Comparison** | Multiple devices | Multi-person analysis |

---

## 💡 Common Tasks

### Task: "I have 3 suspects' location data"
```bash
python3 fh3_cli.py init
python3 fh3_cli.py add suspect1.csv --case INVESTIGATION_001
python3 fh3_cli.py add suspect2.csv --case INVESTIGATION_001
python3 fh3_cli.py add suspect3.csv --case INVESTIGATION_001
python3 fh3_cli.py map --type comparison
# Open the HTML file to see all three overlaid
```

### Task: "Find where suspect was on specific date"
```bash
# First, query the web UI or use pandas:
python3 fh3_cli.py stats  # See what data you have
# Then filter in analysis - CLI shows timestamps
```

### Task: "Detect unusual behavior"
```bash
python3 fh3_cli.py anomalies device_001
# Shows: impossible speeds, unusual patterns, outliers
```

### Task: "Find if suspect visited location"
```bash
python3 fh3_cli.py query 40.7128 -74.0060 --radius 0.5
# 0.5km = ~500m radius
# Shows all visits within that area
```

### Task: "Analyze dark web activity"
```bash
python3 fh3_cli.py deepweb darkweb_logs.txt
# Extracts: Tor IPs, onion domains, crypto addresses
python3 fh3_cli.py deepweb-report --case DARKNET ./reports/
# Generates detailed JSON report
```

---

## 🎯 Real-World Example

**Scenario:** Robbery investigation with suspect phone data

```bash
# Step 1: Initialize
python3 fh3_cli.py init

# Step 2: Add suspect's location history
python3 fh3_cli.py add suspect_iphone_locations.csv --case ROBBERY_2024

# Step 3: Check database
python3 fh3_cli.py stats
# Output: 1,250 locations, 1 device

# Step 4: Find hotspots (home, work, frequent places)
python3 fh3_cli.py hotspots device_0001 --days 30
# Output: Home at [40.1234, -74.5678], Work at [40.9876, -73.4321], etc.

# Step 5: Check if near crime scene
python3 fh3_cli.py query 40.7128 -74.0060 --radius 1.0
# Output: Yes, 15 times in last month within 1km of crime scene!

# Step 6: Visualize
python3 fh3_cli.py map --type multi --output suspect_movements.html
python3 fh3_cli.py map --type trajectory --output suspect_path.html

# Step 7: Check for anomalies
python3 fh3_cli.py anomalies device_0001
# Output: Large speed jumps on date X (possible teleportation/spoofing)

# Step 8: Export for court
python3 fh3_cli.py export --case ROBBERY_2024 ./court_evidence/

# Step 9: Generate comprehensive report
# Open map.html files in browser for visual evidence
```

---

## ⚙️ System Requirements

**Minimum:**
- 2GB RAM
- Python 3.9+
- 500MB disk space

**Recommended:**
- 8GB+ RAM
- Python 3.10+
- 2GB disk space for large datasets
- Chrome/Firefox browser

---

## 🐛 Troubleshooting

**Map won't open?**
```bash
# Try specifying output file
python3 fh3_cli.py map --output my_map.html
# Open my_map.html directly in browser
```

**"No database" error?**
```bash
python3 fh3_cli.py init
```

**Data not showing?**
```bash
# Check if data is there
python3 fh3_cli.py stats

# Try simpler map type
python3 fh3_cli.py map --type cluster
```

**Slow performance?**
```bash
# Reduce radius
python3 fh3_cli.py query 40.7128 -74.0060 --radius 1.0

# Filter by device
python3 fh3_cli.py hotspots device_001
```

---

## 📚 Next Steps

1. **Read FEATURES.md** - Complete feature guide
2. **Run demo** - `python3 demo_all_features.py`
3. **Try web UI** - `python3 fh3_web.py`
4. **Check examples** - See test files: `test_forengeo.py`
5. **Get help** - `python3 fh3_cli.py --help`

---

## 🎓 Learning Path

**Beginner (30 min):**
- Initialize database
- Add sample data
- Generate one map
- View stats

**Intermediate (2 hours):**
- Learn all map types
- Try queries and hotspot analysis
- Export data
- Use web UI

**Advanced (1 day):**
- Deep web forensics
- Anomaly detection
- Privacy assessment
- Multi-device analysis
- Report generation

---

## 📞 Getting Help

```bash
# Show all commands
python3 fh3_cli.py --help

# Show help for specific command
python3 fh3_cli.py map --help

# Run tests to verify installation
python3 test_forengeo.py
python3 test_integration.py

# See the demo
python3 demo_all_features.py
```

---

**Ready to start?** Run this now:
```bash
python3 fh3_cli.py init && python3 demo_all_features.py
```

Enjoy ForenGeo! 🎉
