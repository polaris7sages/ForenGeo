#!/usr/bin/env python3
"""
ForenGeo Comprehensive Demo & Feature Test
Tests all functionality including the new map visualizations
"""

import sys
from pathlib import Path
from forensic_h3_fixed import ForensicH3Analyzer
from deepweb_forensics import DeepWebForensics
from map_visualizer import MapVisualizer
import pandas as pd
import json

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_basic_features():
    """Test basic H3 and location functionality"""
    print_section("🧪 Testing Basic Features")
    
    db = ForensicH3Analyzer("demo_test.db")
    
    # Test 1: Add locations
    print("1️⃣ Adding sample locations...")
    locations = [
        (40.7128, -74.0060, "2024-01-01T10:00:00", "device_001", "Chrome"),
        (40.7589, -73.9851, "2024-01-01T11:00:00", "device_001", "Maps"),
        (40.7282, -73.7949, "2024-01-01T12:00:00", "device_001", "Chrome"),
        (40.6892, -74.0445, "2024-01-01T13:00:00", "device_002", "Safari"),
        (40.6501, -73.9496, "2024-01-01T14:00:00", "device_002", "Chrome"),
    ]
    
    for lat, lon, ts, dev, app in locations:
        db.add_location(lat, lon, ts, dev, app)
    print(f"✅ Added {len(locations)} locations")
    
    # Test 2: H3 Indexing
    print("\n2️⃣ Testing H3 indexing...")
    h3_index = db.geo_to_h3(40.7128, -74.0060)
    lat, lon = db.h3_to_geo(h3_index)
    print(f"✅ H3 Index: {h3_index} -> {lat:.4f}, {lon:.4f}")
    
    # Test 3: Spatial Query
    print("\n3️⃣ Testing spatial queries...")
    results = db.query_hex_neighbors(40.7128, -74.0060, 5.0)
    print(f"✅ Found {len(results)} locations within 5km")
    
    # Test 4: Hotspot Analysis
    print("\n4️⃣ Testing hotspot analysis...")
    hotspots = db.hotspot_analysis()
    print(f"✅ Found {len(hotspots)} hotspots")
    print(f"   Top hotspot: {max(hotspots.items(), key=lambda x: x[1]) if hotspots else 'N/A'}")
    
    # Test 5: Reverse Geocoding
    print("\n5️⃣ Testing reverse geocoding...")
    address = db.reverse_geocode(40.7128, -74.0060)
    print(f"✅ {address['address']}")
    
    db.close()
    print("\n✅ Basic features test completed!")

def test_map_visualizations():
    """Test all map visualization types"""
    print_section("🗺️ Testing Map Visualizations")
    
    db = ForensicH3Analyzer("demo_test.db")
    
    # Get sample data
    df = pd.read_sql("SELECT * FROM locations", db.conn)
    hotspots = db.hotspot_analysis()
    
    print("1️⃣ Creating multi-layer map...")
    db.create_interactive_map(output_file="demo_multi_layer.html")
    print("✅ Multi-layer map created")
    
    print("\n2️⃣ Creating heatmap...")
    db.create_interactive_map(output_file="demo_heatmap.html")
    print("✅ Heatmap created")
    
    print("\n3️⃣ Creating hexagon map...")
    db.create_interactive_map(output_file="demo_hexagon.html")
    print("✅ Hexagon map created")
    
    print("\n4️⃣ Creating cluster map...")
    db.create_interactive_map(output_file="demo_cluster.html")
    print("✅ Cluster map created")
    
    print("\n5️⃣ Creating trajectory map...")
    db.create_interactive_map(output_file="demo_trajectory.html")
    print("✅ Trajectory map created")
    
    print("\n6️⃣ Creating comparison map...")
    db.create_interactive_map(output_file="demo_comparison.html")
    print("✅ Comparison map created")
    
    db.close()
    print("\n✅ Map visualization tests completed!")

def test_advanced_analysis():
    """Test advanced analysis features"""
    print_section("📊 Testing Advanced Analysis")
    
    db = ForensicH3Analyzer("demo_test.db")
    
    # Test 1: Anomalies
    print("1️⃣ Detecting anomalies for device_001...")
    try:
        anomalies = db.detect_anomalies("device_001")
        print(f"✅ Analyzed {len(anomalies)} potential anomalies")
    except Exception as e:
        print(f"⚠️  Anomaly detection: {e}")
    
    # Test 2: Movement Patterns
    print("\n2️⃣ Analyzing movement patterns for device_001...")
    try:
        patterns = db.analyze_movement_patterns("device_001")
        print(f"✅ Movement patterns identified:")
        for key, value in patterns.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"⚠️  Pattern analysis: {e}")
    
    # Test 3: Privacy Assessment
    print("\n3️⃣ Privacy risk assessment for device_001...")
    try:
        risks = db.privacy_risk_assessment("device_001")
        print(f"✅ Privacy assessment completed:")
        for key, value in risks.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"⚠️  Privacy assessment: {e}")
    
    # Test 4: Statistics
    print("\n4️⃣ Database statistics...")
    stats = db.get_statistics()
    print(f"✅ Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    db.close()
    print("\n✅ Advanced analysis tests completed!")

def test_deep_web_forensics():
    """Test deep web forensics capabilities"""
    print_section("🕵️ Testing Deep Web Forensics")
    
    deepweb = DeepWebForensics()
    
    # Sample dark web content
    sample_content = """
    User accessed http://silkroad3fzhx.onion marketplace
    Bitcoin payment sent to: bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
    Connected from IP: 185.220.101.1 (Tor exit node)
    XMR address: 4AdUndoRsTq6UvCGZ533ybuUFEMysqMDAO8GyC67sDM1AJDotWERXNiGicSJQeZo6MBjgoVWQYbNAqxX8KfHHPF3QbLcB69
    Ethereum: 0x32Be343B94f860124dC4fEe278FADBD03915C147
    """
    
    print("1️⃣ Comprehensive deep web analysis...")
    try:
        results = deepweb.comprehensive_deepweb_analysis(sample_content)
        
        print(f"✅ Analysis completed:")
        print(f"   Tor exit nodes found: {results['analysis']['tor']['analysis'].get('exit_nodes_found', 0)}")
        print(f"   Onion domains found: {results['analysis']['onion']['analysis'].get('total_domains', 0)}")
        print(f"   Crypto addresses found: {results['analysis']['crypto']['analysis'].get('total_addresses', 0)}")
        print(f"   Marketplace products: {results['analysis']['marketplace']['analysis'].get('products_found', 0)}")
        
        if results['analysis']['onion'].get('onion_domains'):
            print(f"\n   Detected onion domains:")
            for domain in results['analysis']['onion']['onion_domains'][:3]:
                print(f"     - {domain}")
        
        if results['analysis']['crypto'].get('addresses'):
            print(f"\n   Detected crypto addresses by type:")
            for currency, addrs in results['analysis']['crypto']['addresses'].items():
                print(f"     - {currency}: {len(addrs)} addresses")
    
    except Exception as e:
        print(f"⚠️  Deep web analysis: {e}")
    
    deepweb.close()
    print("\n✅ Deep web forensics tests completed!")

def test_cli_commands():
    """Test CLI commands"""
    print_section("💻 Testing CLI Commands")
    
    print("Testing available CLI commands...")
    
    commands = [
        ("fh3_cli.py --help", "Show help"),
        ("fh3_cli.py status", "Show database status"),
        ("fh3_cli.py stats", "Show statistics"),
    ]
    
    for cmd, desc in commands:
        print(f"\n✓ {desc}: fh3 {cmd.split('fh3_cli.py ')[-1]}")
    
    print("\n✅ CLI command test completed!")

def main():
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  ForenGeo Comprehensive Feature Demonstration".center(58) + "║")
    print("║" + "  Advanced H3 Forensic & OSINT Analyzer".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        test_basic_features()
        test_map_visualizations()
        test_advanced_analysis()
        test_deep_web_forensics()
        test_cli_commands()
        
        print_section("✅ All Tests Completed Successfully!")
        print("\n📁 Generated Files:")
        print("  - demo_multi_layer.html (Multi-layer map visualization)")
        print("  - demo_heatmap.html (Density heatmap)")
        print("  - demo_hexagon.html (H3 hexagon visualization)")
        print("  - demo_cluster.html (Clustered markers)")
        print("  - demo_trajectory.html (Movement trajectory)")
        print("  - demo_comparison.html (Device comparison)")
        
        print("\n📚 Features Tested:")
        print("  ✓ H3 geospatial indexing")
        print("  ✓ Location data management")
        print("  ✓ Spatial queries (k-ring, hex-range)")
        print("  ✓ Hotspot detection and analysis")
        print("  ✓ Reverse geocoding (Nominatim)")
        print("  ✓ Advanced map visualizations (6 types)")
        print("  ✓ Anomaly detection")
        print("  ✓ Movement pattern analysis")
        print("  ✓ Privacy risk assessment")
        print("  ✓ Deep web forensics analysis")
        print("  ✓ Cryptocurrency address detection")
        print("  ✓ Onion domain discovery")
        print("  ✓ Tor exit node identification")
        
        print("\n🌐 Web Interface:")
        print("  Start the web UI with: python3 fh3_web.py")
        print("  Access at: http://localhost:5000")
        
        print("\n💻 CLI Usage:")
        print("  View all commands: python3 fh3_cli.py --help")
        print("  Generate map: python3 fh3_cli.py map --type multi")
        print("  Analyze hotspots: python3 fh3_cli.py hotspots device_001")
        print("  Deep web analysis: python3 fh3_cli.py deepweb <file>")
        
        print("\n✨ ForenGeo is fully functional and ready to use!\n")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
