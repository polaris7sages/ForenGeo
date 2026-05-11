#!/usr/bin/env python3
"""
Test script for Deep Web Forensics Module
"""

from deepweb_forensics import DeepWebForensics
import json

def test_deepweb_basic():
    print("🕵️ Testing Deep Web Forensics Module...")

    # Initialize
    deepweb = DeepWebForensics()
    print("✅ Deep web analyzer initialized")

    # Test content with various dark web indicators
    test_content = """
    Welcome to the Silk Road marketplace at http://abcdefghijklmnop.onion
    Our vendor accepts Bitcoin: bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
    Also accepting Monero: 4ABCdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abc
    Contact us through Tor at 185.220.101.1
    Special offer: Premium VPN - $29.99
    Dark web forum discussion about versus market
    """

    # Test comprehensive analysis
    results = deepweb.comprehensive_deepweb_analysis(test_content)
    print("✅ Comprehensive analysis completed")

    # Verify results
    assert results['analysis']['onion']['onion_domains'], "Should find onion domain"
    assert results['analysis']['crypto']['addresses'], "Should find crypto addresses"
    assert results['analysis']['marketplace']['products'], "Should find marketplace products"

    print(f"✅ Found {results['analysis']['onion']['analysis']['total_domains']} onion domains")
    print(f"✅ Found {results['analysis']['crypto']['analysis']['total_addresses']} crypto addresses")
    print(f"✅ Found {results['analysis']['marketplace']['analysis']['products_found']} products")

    # Test identity correlation
    clearnet_data = {'username': 'john_doe', 'email': 'john@example.com', 'ip': '192.168.1.1'}
    darknet_data = {'username': 'john_doe', 'email': 'john@example.com', 'ip': '185.220.101.1'}

    correlation = deepweb.correlate_identities(clearnet_data, darknet_data)
    print(f"✅ Identity correlation confidence: {correlation['confidence']:.2f}")

    # Test report generation
    report_path = deepweb.generate_deepweb_report("TEST_CASE", "test_reports")
    print(f"✅ Report generated: {report_path}")

    deepweb.close()
    print("🎉 All deep web tests passed!")

if __name__ == "__main__":
    test_deepweb_basic()