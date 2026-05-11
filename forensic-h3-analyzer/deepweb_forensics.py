#!/usr/bin/env python3
"""
Deep Web Forensics Module for ForenGeo
Analyzes dark web patterns, Tor networks, cryptocurrency transactions, and hidden services
"""

import re
import hashlib
import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Set
from pathlib import Path
import sqlite3
import pandas as pd
from urllib.parse import urlparse
import socket
import ssl
from geopy.geocoders import Nominatim
import h3
from forensic_h3_fixed import ForensicH3Analyzer

try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False

class DeepWebForensics:
    """
    Advanced deep web forensics analyzer for dark web investigation
    """

    def __init__(self, db_path: str = "deepweb.db"):
        self.db_path = Path(db_path)
        self.conn = None
        self.geolocator = Nominatim(user_agent="DeepWeb-Forensics")
        self._init_db()

        # Known patterns
        self.tor_exit_nodes = set()
        self.onion_patterns = [
            r'(?:https?://)?([a-z2-7]{16}\.onion)',  # v2 onions
            r'(?:https?://)?([a-z2-7]{56}\.onion)',  # v3 onions
        ]
        self.crypto_patterns = {
            'bitcoin': r'bc1[a-zA-Z0-9]{25,34}',
            'monero': r'4[0-9AB][a-zA-Z0-9]{93}',
            'ethereum': r'0x[a-fA-F0-9]{40}',
        }
        self.darknet_markets = [
            'silkroad', 'alphabay', 'dream', 'wallstreet', 'cannazon',
            'darkmarket', 'versus', 'empire', 'whitehouse'
        ]

    def _init_db(self):
        """Initialize deep web forensics database"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()

        # Tor and onion analysis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tor_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT,
                is_exit_node BOOLEAN,
                first_seen TEXT,
                last_seen TEXT,
                country TEXT,
                asn TEXT,
                h3_index TEXT
            )
        """)

        # Onion domains and services
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS onion_domains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                onion_url TEXT UNIQUE,
                title TEXT,
                description TEXT,
                category TEXT,
                first_discovered TEXT,
                last_seen TEXT,
                status TEXT,
                h3_index TEXT
            )
        """)

        # Cryptocurrency transactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crypto_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT,
                currency TEXT,
                amount REAL,
                timestamp TEXT,
                tx_hash TEXT,
                source TEXT,
                h3_index TEXT
            )
        """)

        # Dark web marketplace data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS marketplace_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_name TEXT,
                product_name TEXT,
                price REAL,
                currency TEXT,
                category TEXT,
                vendor TEXT,
                timestamp TEXT,
                h3_index TEXT
            )
        """)

        # Correlation analysis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS identity_correlations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clearnet_identity TEXT,
                darknet_identity TEXT,
                correlation_type TEXT,
                confidence REAL,
                evidence TEXT,
                timestamp TEXT
            )
        """)

        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_tor_ip ON tor_analysis(ip_address)",
            "CREATE INDEX IF NOT EXISTS idx_onion_url ON onion_domains(onion_url)",
            "CREATE INDEX IF NOT EXISTS idx_crypto_addr ON crypto_transactions(address)",
            "CREATE INDEX IF NOT EXISTS idx_market_name ON marketplace_data(market_name)",
            "CREATE INDEX IF NOT EXISTS idx_correlation ON identity_correlations(clearnet_identity, darknet_identity)"
        ]

        for idx in indexes:
            cursor.execute(idx)

        self.conn.commit()

    # TOR NETWORK ANALYSIS
    def analyze_tor_exit_nodes(self, ip_list: List[str]) -> Dict[str, any]:
        """Analyze IP addresses for Tor exit node correlation"""
        results = {'exit_nodes': [], 'suspicious_ips': [], 'analysis': {}}

        for ip in ip_list:
            if self._is_tor_exit_node(ip):
                results['exit_nodes'].append(ip)
                # Get geolocation and H3 index
                try:
                    location = self.geolocator.reverse(f"{ip}")
                    if location:
                        lat, lon = location.latitude, location.longitude
                        h3_index = h3.latlng_to_cell(lat, lon, 9)
                        self._store_tor_analysis(ip, True, lat, lon, h3_index)
                except:
                    pass

        results['analysis'] = {
            'total_ips': len(ip_list),
            'exit_nodes_found': len(results['exit_nodes']),
            'percentage': (len(results['exit_nodes']) / len(ip_list)) * 100 if ip_list else 0
        }

        return results

    def _is_tor_exit_node(self, ip: str) -> bool:
        """Check if IP is a known Tor exit node"""
        try:
            # Check against known Tor exit node lists
            response = requests.get(f"https://check.torproject.org/cgi-bin/TorBulkExitList.py?ip={ip}", timeout=10)
            return ip in response.text
        except:
            return False

    def _store_tor_analysis(self, ip: str, is_exit: bool, lat: float = None, lon: float = None, h3_index: str = None):
        """Store Tor analysis results"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO tor_analysis
            (ip_address, is_exit_node, first_seen, last_seen, h3_index)
            VALUES (?, ?, ?, ?, ?)
        """, (ip, is_exit, datetime.now().isoformat(), datetime.now().isoformat(), h3_index))
        self.conn.commit()

    # ONION DOMAIN ANALYSIS
    def analyze_onion_domains(self, text_content: str) -> Dict[str, any]:
        """Extract and analyze onion domains from text content"""
        results = {'onion_domains': [], 'analysis': {}}

        for pattern in self.onion_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            results['onion_domains'].extend(matches)

        # Remove duplicates
        results['onion_domains'] = list(set(results['onion_domains']))

        # Analyze each domain
        for domain in results['onion_domains']:
            self._analyze_onion_domain(domain)

        results['analysis'] = {
            'total_domains': len(results['onion_domains']),
            'v2_onions': len([d for d in results['onion_domains'] if len(d.split('.')[0]) == 16]),
            'v3_onions': len([d for d in results['onion_domains'] if len(d.split('.')[0]) == 56])
        }

        return results

    def _analyze_onion_domain(self, onion_url: str):
        """Analyze individual onion domain"""
        cursor = self.conn.cursor()

        # Check if already exists
        cursor.execute("SELECT id FROM onion_domains WHERE onion_url = ?", (onion_url,))
        if cursor.fetchone():
            # Update last seen
            cursor.execute("""
                UPDATE onion_domains SET last_seen = ?, status = 'active'
                WHERE onion_url = ?
            """, (datetime.now().isoformat(), onion_url))
        else:
            # Insert new domain
            cursor.execute("""
                INSERT INTO onion_domains (onion_url, first_discovered, last_seen, status)
                VALUES (?, ?, ?, 'discovered')
            """, (onion_url, datetime.now().isoformat(), datetime.now().isoformat()))

        self.conn.commit()

    # CRYPTOCURRENCY ANALYSIS
    def analyze_cryptocurrency(self, text_content: str) -> Dict[str, any]:
        """Extract and analyze cryptocurrency addresses"""
        results = {'addresses': {}, 'analysis': {}}

        for currency, pattern in self.crypto_patterns.items():
            matches = re.findall(pattern, text_content)
            if matches:
                results['addresses'][currency] = list(set(matches))

                # Store in database
                for address in results['addresses'][currency]:
                    self._store_crypto_address(address, currency)

        results['analysis'] = {
            'total_addresses': sum(len(addrs) for addrs in results['addresses'].values()),
            'currencies_found': list(results['addresses'].keys())
        }

        return results

    def _store_crypto_address(self, address: str, currency: str):
        """Store cryptocurrency address"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO crypto_transactions (address, currency, timestamp)
            VALUES (?, ?, ?)
        """, (address, currency, datetime.now().isoformat()))
        self.conn.commit()

    def correlate_crypto_transactions(self, address: str) -> Dict[str, any]:
        """Correlate cryptocurrency transactions with location data"""
        # This would integrate with blockchain explorers
        # For now, return placeholder analysis
        return {
            'address': address,
            'transactions': [],
            'analysis': 'Blockchain correlation requires external API integration'
        }

    # DARK WEB MARKETPLACE ANALYSIS
    def analyze_marketplace_content(self, content: str) -> Dict[str, any]:
        """Analyze dark web marketplace content"""
        results = {'products': [], 'analysis': {}}

        # Look for marketplace patterns
        for market in self.darknet_markets:
            if market.lower() in content.lower():
                results['analysis']['detected_market'] = market

        # Extract product information (simplified)
        product_patterns = [
            r'(\w+)\s*-\s*\$?(\d+(?:\.\d{2})?)',
            r'(\w+)\s*price:\s*\$?(\d+(?:\.\d{2})?)',
        ]

        for pattern in product_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for name, price in matches:
                results['products'].append({
                    'name': name.strip(),
                    'price': float(price),
                    'currency': 'USD'
                })

        # Store marketplace data
        for product in results['products']:
            self._store_marketplace_data(product)

        results['analysis']['products_found'] = len(results['products'])
        return results

    def _store_marketplace_data(self, product: dict):
        """Store marketplace product data"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO marketplace_data
            (product_name, price, currency, timestamp)
            VALUES (?, ?, ?, ?)
        """, (product['name'], product['price'], product['currency'], datetime.now().isoformat()))
        self.conn.commit()

    # IDENTITY CORRELATION
    def correlate_identities(self, clearnet_data: dict, darknet_data: dict) -> Dict[str, any]:
        """Correlate clearnet and darknet identities"""
        correlations = []
        confidence_scores = []

        # Username correlation
        if 'username' in clearnet_data and 'username' in darknet_data:
            if clearnet_data['username'].lower() == darknet_data['username'].lower():
                correlations.append('username_match')
                confidence_scores.append(0.8)

        # Email correlation
        if 'email' in clearnet_data and 'email' in darknet_data:
            if clearnet_data['email'] == darknet_data['email']:
                correlations.append('email_match')
                confidence_scores.append(0.9)

        # IP correlation
        if 'ip' in clearnet_data and 'ip' in darknet_data:
            if clearnet_data['ip'] == darknet_data['ip']:
                correlations.append('ip_match')
                confidence_scores.append(0.7)

        # Store correlation
        if correlations:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            self._store_identity_correlation(
                clearnet_data.get('username', 'unknown'),
                darknet_data.get('username', 'unknown'),
                ','.join(correlations),
                avg_confidence,
                json.dumps({'clearnet': clearnet_data, 'darknet': darknet_data})
            )

        return {
            'correlations': correlations,
            'confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            'evidence': len(correlations)
        }

    def _store_identity_correlation(self, clearnet_id: str, darknet_id: str,
                                   corr_type: str, confidence: float, evidence: str):
        """Store identity correlation"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO identity_correlations
            (clearnet_identity, darknet_identity, correlation_type, confidence, evidence, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (clearnet_id, darknet_id, corr_type, confidence, evidence, datetime.now().isoformat()))
        self.conn.commit()

    # COMPREHENSIVE ANALYSIS
    def comprehensive_deepweb_analysis(self, content: str, metadata: dict = None) -> Dict[str, any]:
        """Run comprehensive deep web analysis on content"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'content_hash': hashlib.sha256(content.encode()).hexdigest(),
            'analysis': {}
        }

        # Analyze different aspects
        results['analysis']['tor'] = self.analyze_tor_exit_nodes(
            re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', content)
        )

        results['analysis']['onion'] = self.analyze_onion_domains(content)
        results['analysis']['crypto'] = self.analyze_cryptocurrency(content)
        results['analysis']['marketplace'] = self.analyze_marketplace_content(content)

        # Metadata analysis
        if metadata:
            results['analysis']['metadata'] = self._analyze_metadata(metadata)

        return results

    def _analyze_metadata(self, metadata: dict) -> dict:
        """Analyze file or network metadata"""
        analysis = {}

        if 'ip' in metadata:
            analysis['ip_analysis'] = self.analyze_tor_exit_nodes([metadata['ip']])

        if 'user_agent' in metadata:
            analysis['user_agent'] = metadata['user_agent']
            # Check for Tor browser indicators
            tor_indicators = ['tor', 'onion', 'darknet']
            analysis['tor_browser_likely'] = any(indicator in metadata['user_agent'].lower()
                                                for indicator in tor_indicators)

        return analysis

    # GEOSPATIAL CORRELATION
    def correlate_geospatial_darkweb(self, h3_analyzer, device_id: str) -> Dict[str, any]:
        """Correlate device locations with dark web activities using H3"""
        correlations = {
            'location_tor_correlations': [],
            'temporal_patterns': [],
            'risk_assessment': {}
        }

        # Get device locations
        df = pd.read_sql(f"SELECT * FROM locations WHERE device_id='{device_id}'", h3_analyzer.conn)
        if df.empty:
            return {'error': 'No location data for device'}

        # Get dark web activities with H3 indices
        tor_df = pd.read_sql("SELECT * FROM tor_analysis WHERE h3_index IS NOT NULL", self.conn)
        onion_df = pd.read_sql("SELECT * FROM onion_domains WHERE h3_index IS NOT NULL", self.conn)

        # Correlate locations with Tor exit nodes
        for _, location in df.iterrows():
            device_hex = location['h3_index']

            # Find nearby Tor exit nodes
            for _, tor_node in tor_df.iterrows():
                if tor_node['h3_index']:
                    distance = h3.grid_distance(device_hex, tor_node['h3_index'])
                    if distance <= 3:  # Within 3 hexes (adjustable)
                        correlations['location_tor_correlations'].append({
                            'device_location': (location['lat'], location['lon']),
                            'tor_ip': tor_node['ip_address'],
                            'distance_hexes': distance,
                            'timestamp': location['timestamp']
                        })

        # Analyze temporal patterns
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour

        # Look for patterns around typical dark web activity times
        night_hours = df[(df['hour'] >= 22) | (df['hour'] <= 6)]
        if not night_hours.empty:
            correlations['temporal_patterns'].append({
                'pattern': 'night_activity',
                'locations': len(night_hours),
                'description': 'Device active during typical dark web hours (10 PM - 6 AM)'
            })

        # Risk assessment
        tor_nearby = len(correlations['location_tor_correlations'])
        correlations['risk_assessment'] = {
            'tor_proximity_risk': 'High' if tor_nearby > 5 else 'Medium' if tor_nearby > 1 else 'Low',
            'temporal_risk': 'High' if len(correlations['temporal_patterns']) > 0 else 'Low',
            'overall_darkweb_risk': 'High' if (tor_nearby > 5 or len(correlations['temporal_patterns']) > 0) else 'Medium' if tor_nearby > 0 else 'Low'
        }

        return correlations

    def analyze_darkweb_communities(self) -> Dict[str, any]:
        """Analyze dark web community patterns and clusters"""
        analysis = {
            'market_clusters': {},
            'identity_networks': [],
            'geographic_distribution': {}
        }

        cursor = self.conn.cursor()

        # Analyze marketplace clusters
        cursor.execute("""
            SELECT market_name, COUNT(*) as products, AVG(price) as avg_price
            FROM marketplace_data
            GROUP BY market_name
            ORDER BY products DESC
        """)

        for row in cursor.fetchall():
            analysis['market_clusters'][row[0]] = {
                'product_count': row[1],
                'avg_price': row[2]
            }

        # Analyze identity correlation networks
        cursor.execute("""
            SELECT clearnet_identity, darknet_identity, correlation_type, confidence
            FROM identity_correlations
            WHERE confidence > 0.7
            ORDER BY confidence DESC
        """)

        for row in cursor.fetchall():
            analysis['identity_networks'].append({
                'clearnet': row[0],
                'darknet': row[1],
                'correlation_type': row[2],
                'confidence': row[3]
            })

        # Geographic distribution of Tor nodes
        cursor.execute("""
            SELECT h3_index, COUNT(*) as nodes
            FROM tor_analysis
            WHERE h3_index IS NOT NULL
            GROUP BY h3_index
            ORDER BY nodes DESC
        """)

        for row in cursor.fetchall():
            analysis['geographic_distribution'][row[0]] = row[1]

        return analysis

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Integration with main ForensicH3Analyzer
def integrate_deepweb_forensics(analyzer: ForensicH3Analyzer, deepweb_analyzer: DeepWebForensics):
    """Integrate deep web forensics with main analyzer"""

    # Add deep web analysis methods to main analyzer
    def analyze_deepweb_content(self, content: str, metadata: dict = None):
        return deepweb_analyzer.comprehensive_deepweb_analysis(content, metadata)

    def correlate_darkweb_locations(self, device_id: str):
        """Correlate device locations with dark web activity"""
        return deepweb_analyzer.correlate_geospatial_darkweb(self, device_id)

    def analyze_darkweb_communities(self):
        """Analyze dark web community patterns"""
        return deepweb_analyzer.analyze_darkweb_communities()

    # Monkey patch methods
    ForensicH3Analyzer.analyze_deepweb_content = analyze_deepweb_content
    ForensicH3Analyzer.correlate_darkweb_locations = correlate_darkweb_locations
    ForensicH3Analyzer.analyze_darkweb_communities = analyze_darkweb_communities

if __name__ == '__main__':
    # Example usage
    deepweb = DeepWebForensics()

    # Analyze sample content
    sample_content = """
    Welcome to the dark web marketplace at http://silkroad3fzhx.onion
    Bitcoin address: bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
    Monero: 4ABC... (truncated)
    Tor exit node: 185.220.101.1
    """

    results = deepweb.comprehensive_deepweb_analysis(sample_content)
    print(json.dumps(results, indent=2))

    deepweb.close()
