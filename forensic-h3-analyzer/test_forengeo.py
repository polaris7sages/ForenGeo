#!/usr/bin/env python3
"""
Test script for ForenGeo Forensic H3 Analyzer
"""

from forensic_h3_fixed import ForensicH3Analyzer

def test_basic():
    print("🧪 Testing ForenGeo Forensic H3 Analyzer...")

    # Initialize
    analyzer = ForensicH3Analyzer("test.db", resolution=9)
    print("✅ Database initialized")

    # Add test location
    analyzer.add_location(40.7128, -74.0060, "2024-05-07T10:00:00Z", "test_device")
    print("✅ Location added")

    # Test H3 functions
    h3_index = analyzer.geo_to_h3(40.7128, -74.0060)
    print(f"✅ H3 index: {h3_index}")

    lat, lon = analyzer.h3_to_geo(h3_index)
    print(f"✅ Reverse geo: {lat:.4f}, {lon:.4f}")

    # Test OSINT
    address = analyzer.reverse_geocode(40.7128, -74.0060)
    print(f"✅ Reverse geocode: {address['address']}")

    # Test query
    results = analyzer.query_hex_neighbors(40.7128, -74.0060, 1.0)
    print(f"✅ Query returned {len(results)} results")

    # Test stats
    stats = analyzer.get_statistics()
    print(f"✅ Stats: {stats}")

    analyzer.close()
    print("🎉 All tests passed!")

if __name__ == "__main__":
    test_basic()