#!/usr/bin/env python3
"""
🚨 FH3 Advanced Forensic H3 CLI - Complete OSINT & Analysis Tool
"""

import argparse
import os
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
from forensic_h3_fixed import ForensicH3Analyzer
from deepweb_forensics import DeepWebForensics

class FH3CLI:
    def __init__(self, db_path: str = ".fh3.db"):
        self.db_path = Path(db_path)
        self.indexer = None

    def _get_indexer(self):
        if self.indexer is None:
            if not self.db_path.exists():
                print("❌ No database. Run 'fh3 init'")
                sys.exit(1)
            self.indexer = ForensicH3Analyzer(str(self.db_path))
        return self.indexer

    def init(self):
        self.indexer = ForensicH3Analyzer(str(self.db_path))
        print("✅ FH3 database initialized (.fh3.db)")
        self.indexer.close()

    def add(self, files, case_id):
        indexer = self._get_indexer()
        for f in files:
            indexer.add_with_hash(f, case_id)
        indexer.close()

    def query(self, lat, lon, radius=1.0):
        indexer = self._get_indexer()
        results = indexer.query_hex_neighbors(lat, lon, radius)
        print(f"\n📍 {len(results)} hits within {radius}km:")
        print(results[['timestamp', 'lat', 'lon', 'device_id', 'app_name']].head(10).to_string(index=False))
        indexer.close()

    def verify(self):
        indexer = self._get_indexer()
        indexer.verify_integrity()
        indexer.close()

    def hotspots(self, device_id=None, days=30):
        indexer = self._get_indexer()
        hotspots = indexer.hotspot_analysis(device_id, days)
        print(f"\n🔥 Top hotspots for {device_id or 'all devices'} (last {days} days):")
        for i, (h3_hex, count) in enumerate(list(hotspots.items())[:10]):
            lat, lon = indexer.h3_to_geo(h3_hex)
            print(f"{i+1}. {h3_hex}: {count} visits (lat: {lat:.4f}, lon: {lon:.4f})")
        indexer.close()

    def anomalies(self, device_id):
        indexer = self._get_indexer()
        anomalies = indexer.detect_anomalies(device_id)
        print(f"\n🕵️ Anomalies detected for {device_id}:")
        print(anomalies.to_string(index=False))
        indexer.close()

    def patterns(self, device_id):
        indexer = self._get_indexer()
        patterns = indexer.analyze_movement_patterns(device_id)
        print(f"\n📊 Movement patterns for {device_id}:")
        for key, value in patterns.items():
            print(f"{key}: {value}")
        indexer.close()

    def privacy(self, device_id):
        indexer = self._get_indexer()
        risks = indexer.privacy_risk_assessment(device_id)
        print(f"\n🔒 Privacy risk assessment for {device_id}:")
        for key, value in risks.items():
            print(f"{key}: {value}")
        indexer.close()

    def geocode(self, address):
        indexer = self._get_indexer()
        lat, lon = indexer.geocode_address(address)
        if lat and lon:
            print(f"📍 {address} -> lat: {lat}, lon: {lon}")
            h3_hex = indexer.geo_to_h3(lat, lon)
            print(f"H3 index: {h3_hex}")
        else:
            print("❌ Geocoding failed")
        indexer.close()

    def reverse_geocode(self, lat, lon):
        indexer = self._get_indexer()
        result = indexer.reverse_geocode(lat, lon)
        print(f"📍 {lat}, {lon} -> {result['address']}")
        indexer.close()

    def poi_search(self, lat, lon, radius=1000, poi_type='amenity'):
        indexer = self._get_indexer()
        pois = indexer.search_poi_nearby(lat, lon, radius, poi_type)
        print(f"\n🏢 Found {len(pois)} POIs within {radius}m:")
        for poi in pois[:10]:
            print(f"- {poi['name']} ({poi['lat']:.4f}, {poi['lon']:.4f})")
        indexer.close()

    def map(self, device_id=None, output='map.html'):
        indexer = self._get_indexer()
        indexer.create_interactive_map(device_id, output)
        indexer.close()

    def kml(self, device_id=None, output='locations.kml'):
        indexer = self._get_indexer()
        indexer.export_kml(device_id, output)
        indexer.close()

    def stats(self):
        indexer = self._get_indexer()
        stats = indexer.get_statistics()
        print("\n📊 Database Statistics:")
        for key, value in stats.items():
            print(f"{key}: {value}")
        indexer.close()

    def status(self):
        indexer = self._get_indexer()
        stats = indexer.get_statistics()
        print("\n📊 FH3 Status:")
        print(f"total_locations: {stats.get('total_locations', 0)}")
        print(f"unique_devices: {stats.get('unique_devices', 0)}")
        print(f"unique_hexes: {stats.get('unique_hexes', 0)}")
        print(f"poi_entries: {stats.get('poi_entries', 0)}")
        indexer.close()

    def export(self, case_id, output_dir):
        indexer = self._get_indexer()
        indexer.export_autopsy_csv(case_id, output_dir)
        indexer.close()

    def analyze_deepweb(self, content_file):
        """Analyze content for deep web indicators"""
        indexer = self._get_indexer()
        deepweb = DeepWebForensics()

        try:
            with open(content_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            results = deepweb.comprehensive_deepweb_analysis(content)
            print(f"\n🔍 Deep Web Analysis Results for {content_file}:")
            print(f"📊 Tor Exit Nodes: {results['analysis']['tor']['analysis']['exit_nodes_found']}")
            print(f"🧅 Onion Domains: {results['analysis']['onion']['analysis']['total_domains']}")
            print(f"💰 Crypto Addresses: {results['analysis']['crypto']['analysis']['total_addresses']}")
            print(f"🛒 Marketplace Products: {results['analysis']['marketplace']['analysis']['products_found']}")

            # Detailed output
            if results['analysis']['onion']['onion_domains']:
                print(f"\n🧅 Onion Domains Found:")
                for domain in results['analysis']['onion']['onion_domains'][:5]:
                    print(f"  - {domain}")

            if results['analysis']['crypto']['addresses']:
                print(f"\n💰 Cryptocurrency Addresses:")
                for currency, addresses in results['analysis']['crypto']['addresses'].items():
                    print(f"  {currency.upper()}: {len(addresses)} addresses")

        except Exception as e:
            print(f"❌ Deep web analysis failed: {e}")
        finally:
            deepweb.close()
            indexer.close()

    def deepweb_report(self, case_id, output_dir):
        """Generate deep web forensics report"""
        deepweb = DeepWebForensics()
        try:
            report_path = deepweb.generate_deepweb_report(case_id, output_dir)
            print(f"📋 Deep web report generated: {report_path}")
        except Exception as e:
            print(f"❌ Report generation failed: {e}")
        finally:
            deepweb.close()

    def correlate_darkweb(self, device_id):
        """Correlate device locations with dark web activity"""
        indexer = self._get_indexer()
        deepweb = DeepWebForensics()

        try:
            correlations = indexer.correlate_darkweb_locations(device_id)
            print(f"\n🔗 Dark Web Correlations for {device_id}:")
            print(f"Found {len(correlations)} location matches with dark web activity")

            for corr in correlations[:10]:
                print(f"  📍 {corr['device_location']} - Dark Web IP: {corr['darkweb_ip']}")
                print(f"     Time: {corr['timestamp']}")

        except Exception as e:
            print(f"❌ Correlation analysis failed: {e}")
        finally:
            deepweb.close()
            indexer.close()


def main():
    parser = argparse.ArgumentParser(description="FH3 Forensic H3 Analyzer - Advanced OSINT Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Init
    subparsers.add_parser('init', help='Initialize FH3 database')

    # Add files
    add_parser = subparsers.add_parser('add', help='Add evidence files')
    add_parser.add_argument('files', nargs='+', help='Files to add')
    add_parser.add_argument('--case', required=True, help='Case ID')

    # Query
    query_parser = subparsers.add_parser('query', help='Query locations')
    query_parser.add_argument('lat', type=float, help='Latitude')
    query_parser.add_argument('lon', type=float, help='Longitude')
    query_parser.add_argument('--radius', type=float, default=1.0, help='Radius in km')

    # Verify
    subparsers.add_parser('verify', help='Verify chain of custody')

    # Hotspots
    hotspots_parser = subparsers.add_parser('hotspots', help='Analyze hotspots')
    hotspots_parser.add_argument('device_id', nargs='?', help='Device ID (optional)')
    hotspots_parser.add_argument('--days', type=int, default=30, help='Days to analyze')

    # Anomalies
    anomalies_parser = subparsers.add_parser('anomalies', help='Detect anomalies')
    anomalies_parser.add_argument('device_id', help='Device ID')

    # Patterns
    patterns_parser = subparsers.add_parser('patterns', help='Analyze movement patterns')
    patterns_parser.add_argument('device_id', help='Device ID')

    # Privacy
    privacy_parser = subparsers.add_parser('privacy', help='Privacy risk assessment')
    privacy_parser.add_argument('device_id', help='Device ID')

    # Geocode
    geocode_parser = subparsers.add_parser('geocode', help='Geocode address')
    geocode_parser.add_argument('address', help='Address to geocode')

    # Reverse geocode
    revgeo_parser = subparsers.add_parser('revgeo', help='Reverse geocode coordinates')
    revgeo_parser.add_argument('lat', type=float, help='Latitude')
    revgeo_parser.add_argument('lon', type=float, help='Longitude')

    # POI search
    poi_parser = subparsers.add_parser('poi', help='Search points of interest')
    poi_parser.add_argument('lat', type=float, help='Latitude')
    poi_parser.add_argument('lon', type=float, help='Longitude')
    poi_parser.add_argument('--radius', type=int, default=1000, help='Radius in meters')
    poi_parser.add_argument('--type', default='amenity', help='POI type')

    # Map
    map_parser = subparsers.add_parser('map', help='Create interactive map')
    map_parser.add_argument('--device', help='Device ID')
    map_parser.add_argument('--output', default='map.html', help='Output file')

    # KML
    kml_parser = subparsers.add_parser('kml', help='Export to KML')
    kml_parser.add_argument('--device', help='Device ID')
    kml_parser.add_argument('--output', default='locations.kml', help='Output file')

    # Stats
    subparsers.add_parser('stats', help='Show database statistics')
    subparsers.add_parser('status', help='Show database status')
    export_parser = subparsers.add_parser('export', help='Export Autopsy CSV')
    export_parser.add_argument('--case', required=True, help='Case ID')
    export_parser.add_argument('output', help='Output directory')

    # Deep Web Forensics
    deepweb_parser = subparsers.add_parser('deepweb', help='Analyze content for deep web indicators')
    deepweb_parser.add_argument('content_file', help='File containing content to analyze')

    deepweb_report_parser = subparsers.add_parser('deepweb-report', help='Generate deep web forensics report')
    deepweb_report_parser.add_argument('--case', required=True, help='Case ID')
    deepweb_report_parser.add_argument('output_dir', help='Output directory')

    correlate_parser = subparsers.add_parser('correlate-darkweb', help='Correlate locations with dark web activity')
    correlate_parser.add_argument('device_id', help='Device ID to correlate')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = FH3CLI()

    if args.command == 'init':
        cli.init()
    elif args.command == 'add':
        cli.add(args.files, args.case)
    elif args.command == 'query':
        cli.query(args.lat, args.lon, args.radius)
    elif args.command == 'verify':
        cli.verify()
    elif args.command == 'hotspots':
        cli.hotspots(args.device_id, args.days)
    elif args.command == 'anomalies':
        cli.anomalies(args.device_id)
    elif args.command == 'patterns':
        cli.patterns(args.device_id)
    elif args.command == 'privacy':
        cli.privacy(args.device_id)
    elif args.command == 'geocode':
        cli.geocode(args.address)
    elif args.command == 'revgeo':
        cli.reverse_geocode(args.lat, args.lon)
    elif args.command == 'poi':
        cli.poi_search(args.lat, args.lon, args.radius, args.type)
    elif args.command == 'map':
        cli.map(args.device, args.output)
    elif args.command == 'kml':
        cli.kml(args.device, args.output)
    elif args.command == 'stats':
        cli.stats()
    elif args.command == 'status':
        cli.status()
    elif args.command == 'export':
        cli.export(args.case, args.output)
    elif args.command == 'deepweb':
        cli.analyze_deepweb(args.content_file)
    elif args.command == 'deepweb-report':
        cli.deepweb_report(args.case, args.output_dir)
    elif args.command == 'correlate-darkweb':
        cli.correlate_darkweb(args.device_id)

if __name__ == '__main__':
    main()