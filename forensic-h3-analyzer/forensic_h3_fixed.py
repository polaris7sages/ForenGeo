import h3
import pandas as pd
import sqlite3
import json
import hashlib
import os
import re
import socket
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict, Counter
import simplekml
import folium
from scipy import stats
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import math
from map_visualizer import MapVisualizer

class ForensicH3Analyzer:
    """
    Advanced H3Geo Forensic & OSINT Analyzer
    Leverages full H3 potential for geospatial intelligence, digital forensics, and daily life analysis
    """

    def __init__(self, db_path: str = "fh3.db", resolution: int = 9):
        self.db_path = Path(db_path)
        self.resolution = resolution
        self.conn = None
        self.chain_of_custody = []
        self.geolocator = Nominatim(user_agent="ForenGeo-Analyzer")
        self._init_db()
        self._load_custody()

    def _init_db(self):
        """Initialize SQLite database with enhanced schema"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()

        # Enhanced locations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                lat REAL,
                lon REAL,
                h3_index TEXT,
                device_id TEXT,
                app_name TEXT,
                metadata TEXT,
                evidence_id TEXT,
                altitude REAL DEFAULT 0,
                accuracy REAL DEFAULT 0,
                speed REAL DEFAULT 0,
                heading REAL DEFAULT 0
            )
        """)

        # POI and OSINT data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS poi_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                h3_index TEXT,
                poi_type TEXT,
                name TEXT,
                address TEXT,
                category TEXT,
                source TEXT,
                last_updated TEXT
            )
        """)

        # Phone OSINT table for Indian and international phone number intelligence
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS phone_osint (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT UNIQUE,
                normalized TEXT,
                country_code TEXT,
                region TEXT,
                carrier TEXT,
                is_valid INTEGER,
                type TEXT,
                international TEXT,
                source TEXT,
                metadata TEXT,
                last_updated TEXT
            )
        """)

        # OSINT entity graph and relationship tables for Bellingcat/Maltego-style intelligence
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS osint_entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT,
                entity_value TEXT,
                normalized_value TEXT,
                metadata TEXT,
                first_seen TEXT,
                last_seen TEXT,
                evidence_id TEXT,
                UNIQUE(entity_type, entity_value)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS osint_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_entity_id INTEGER,
                target_entity_id INTEGER,
                relationship_type TEXT,
                evidence_id TEXT,
                timestamp TEXT,
                FOREIGN KEY(source_entity_id) REFERENCES osint_entities(id),
                FOREIGN KEY(target_entity_id) REFERENCES osint_entities(id)
            )
        """)

        # Android forensic artifact table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS android_artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                artifact_type TEXT,
                key TEXT,
                value TEXT,
                evidence_id TEXT,
                timestamp TEXT,
                metadata TEXT
            )
        """)

        # Linux forensic artifact table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS linux_artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                artifact_type TEXT,
                key TEXT,
                value TEXT,
                evidence_id TEXT,
                timestamp TEXT,
                metadata TEXT
            )
        """)

        # Movement patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movement_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                pattern_type TEXT,
                start_hex TEXT,
                end_hex TEXT,
                frequency INTEGER,
                avg_speed REAL,
                time_of_day TEXT
            )
        """)

        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_h3 ON locations(h3_index)",
            "CREATE INDEX IF NOT EXISTS idx_device ON locations(device_id)",
            "CREATE INDEX IF NOT EXISTS idx_time ON locations(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_evidence ON locations(evidence_id)",
            "CREATE INDEX IF NOT EXISTS idx_poi_h3 ON poi_data(h3_index)",
            "CREATE INDEX IF NOT EXISTS idx_phone_number ON phone_osint(phone_number)",
            "CREATE INDEX IF NOT EXISTS idx_entity_value ON osint_entities(entity_type, entity_value)",
            "CREATE INDEX IF NOT EXISTS idx_relationship_source ON osint_relationships(source_entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_relationship_target ON osint_relationships(target_entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_android_file ON android_artifacts(file_path)",
            "CREATE INDEX IF NOT EXISTS idx_linux_file ON linux_artifacts(file_path)",
            "CREATE INDEX IF NOT EXISTS idx_movement_device ON movement_patterns(device_id)"
        ]

        for idx in indexes:
            cursor.execute(idx)

        self.conn.commit()

    def _load_custody(self):
        custody_file = self.db_path.with_suffix('.custody.json')
        if custody_file.exists():
            with open(custody_file) as f:
                self.chain_of_custody = json.load(f)

    def _save_custody(self):
        custody_file = self.db_path.with_suffix('.custody.json')
        with open(custody_file, 'w') as f:
            json.dump(self.chain_of_custody, f, indent=2)

    # CORE H3 FUNCTIONS
    def geo_to_h3(self, lat: float, lon: float, resolution: Optional[int] = None) -> str:
        """Convert lat/lon to H3 index"""
        if resolution is None:
            resolution = self.resolution
        try:
            return h3.latlng_to_cell(lat, lon, resolution)
        except Exception as e:
            print(f"❌ H3 conversion failed: {e}")
            return ""

    def h3_to_geo(self, h3_index: str) -> Tuple[float, float]:
        """Convert H3 index to lat/lon center"""
        try:
            lat, lon = h3.cell_to_latlng(h3_index)
            return (lat, lon)
        except:
            return (0.0, 0.0)

    def h3_to_boundary(self, h3_index: str) -> List[Tuple[float, float]]:
        """Get H3 hexagon boundary coordinates"""
        try:
            boundary = h3.cell_to_boundary(h3_index)
            return [(lat, lng) for lat, lng in boundary]
        except:
            return []

    def get_h3_resolution(self, h3_index: str) -> int:
        """Get resolution of H3 index"""
        return h3.get_resolution(h3_index)

    def h3_distance(self, h3_a: str, h3_b: str) -> int:
        """Calculate grid distance between two H3 indices"""
        return h3.grid_distance(h3_a, h3_b)

    def h3_edge_length(self, resolution: int, unit: str = 'km') -> float:
        """Get average edge length of H3 hexagon at resolution"""
        return h3.average_hexagon_edge_length(resolution, unit)

    def polyfill_area(self, geojson: dict, resolution: int) -> List[str]:
        """Fill polygon with H3 hexagons"""
        try:
            # H3 v4 API for polygon filling
            from h3 import Polygon
            poly = Polygon(geojson['coordinates'][0])
            return h3.cells_in_polygon(poly, resolution)
        except Exception as e:
            print(f"❌ Polyfill failed: {e}")
            return []

    def k_ring(self, h3_index: str, k: int) -> List[str]:
        """Get k-ring of hexagons around center"""
        return h3.grid_ring(h3_index, k)

    def hex_range(self, h3_index: str, k: int) -> List[str]:
        """Get hexagons within k distance (faster than k_ring for large k)"""
        return h3.grid_disk(h3_index, k)

    def h3_line(self, start: str, end: str) -> List[str]:
        """Get H3 indices along line between two points"""
        return h3.grid_path_cells(start, end)

    # DATA INGESTION
    def add_location(self, lat: float, lon: float, timestamp: str, device_id: str,
                    app_name: str = "", metadata: dict = None, evidence_id: str = "",
                    altitude: float = 0, accuracy: float = 0, speed: float = 0, heading: float = 0):
        """Add single location with enhanced metadata"""
        h3_hex = self.geo_to_h3(lat, lon)
        if not h3_hex:
            return False

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO locations (timestamp, lat, lon, h3_index, device_id, app_name,
                                 metadata, evidence_id, altitude, accuracy, speed, heading)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, lat, lon, h3_hex, device_id, app_name,
              json.dumps(metadata or {}), evidence_id, altitude, accuracy, speed, heading))
        self.conn.commit()
        return True

    def bulk_import_csv(self, csv_path: str, device_id: str, evidence_id: str = ""):
        """Import locations from CSV file"""
        try:
            df = pd.read_csv(csv_path)
            count = 0
            for _, row in df.iterrows():
                if 'lat' in row and 'lon' in row:
                    self.add_location(
                        row['lat'], row['lon'],
                        row.get('timestamp', datetime.now().isoformat()),
                        device_id,
                        row.get('app_name', ''),
                        row.to_dict(),
                        evidence_id,
                        row.get('altitude', 0),
                        row.get('accuracy', 0),
                        row.get('speed', 0),
                        row.get('heading', 0)
                    )
                    count += 1
            print(f"✅ Imported {count} locations from {csv_path}")
        except Exception as e:
            print(f"❌ CSV import failed: {e}")

    def bulk_import_plist(self, plist_path: str, device_id: str, evidence_id: str = ""):
        """Import from iOS plist format"""
        try:
            import plistlib
            with open(plist_path, 'rb') as f:
                data = plistlib.load(f)

            count = 0
            locations = data if isinstance(data, list) else data.get('locations', [])

            for loc in locations:
                if isinstance(loc, dict) and 'Latitude' in loc and 'Longitude' in loc:
                    self.add_location(
                        loc['Latitude'], loc['Longitude'],
                        loc.get('Timestamp', datetime.now().isoformat()),
                        device_id,
                        loc.get('AppName', ''),
                        loc,
                        evidence_id,
                        loc.get('Altitude', 0),
                        loc.get('HorizontalAccuracy', 0),
                        loc.get('Speed', 0),
                        loc.get('Course', 0)
                    )
                    count += 1
            print(f"✅ Imported {count} locations from {plist_path}")
        except Exception as e:
            print(f"❌ Plist import failed: {e}")

    def add_with_hash(self, file_path: str, evidence_id: str):
        """Import with chain of custody verification"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)

        custody_entry = {
            'timestamp': datetime.now().isoformat(),
            'evidence_id': evidence_id,
            'file_path': str(Path(file_path).absolute()),
            'file_hash': hasher.hexdigest(),
            'user': os.getenv('USER', 'unknown'),
            'operation': 'IMPORT'
        }
        self.chain_of_custody.append(custody_entry)
        self._save_custody()

        if file_path.endswith('.plist'):
            self.bulk_import_plist(file_path, f"{evidence_id}_{Path(file_path).stem}", evidence_id)
        elif file_path.endswith('.csv'):
            self.bulk_import_csv(file_path, f"{evidence_id}_{Path(file_path).stem}", evidence_id)

    # OSINT & GEOCODING FEATURES
    def reverse_geocode(self, lat: float, lon: float) -> dict:
        """Reverse geocode coordinates to address using Nominatim"""
        try:
            location = self.geolocator.reverse((lat, lon))
            if location:
                return {
                    'address': location.address,
                    'raw': location.raw
                }
        except Exception as e:
            print(f"❌ Reverse geocoding failed: {e}")
        return {'address': 'Unknown', 'raw': {}}

    def geocode_address(self, address: str) -> Tuple[float, float]:
        """Geocode address to coordinates"""
        try:
            location = self.geolocator.geocode(address)
            if location:
                return (location.latitude, location.longitude)
        except Exception as e:
            print(f"❌ Geocoding failed: {e}")
        return (0.0, 0.0)

    def get_weather_data(self, lat: float, lon: float, api_key: str = None) -> dict:
        """Get weather data for location (requires OpenWeatherMap API key)"""
        if not api_key:
            return {'error': 'API key required for weather data'}

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"❌ Weather API failed: {e}")
        return {'error': 'Weather data unavailable'}

    def search_poi_nearby(self, lat: float, lon: float, radius: int = 1000, poi_type: str = 'amenity') -> List[dict]:
        """Search for Points of Interest using Overpass API"""
        try:
            overpass_url = "http://overpass-api.de/api/interpreter"
            query = f"""
            [out:json];
            (
              node["{poi_type}"](around:{radius},{lat},{lon});
              way["{poi_type}"](around:{radius},{lat},{lon});
              relation["{poi_type}"](around:{radius},{lat},{lon});
            );
            out center;
            """
            response = requests.post(overpass_url, data={'data': query})
            if response.status_code == 200:
                data = response.json()
                pois = []
                for element in data.get('elements', []):
                    if 'tags' in element:
                        poi = {
                            'name': element['tags'].get('name', 'Unknown'),
                            'type': poi_type,
                            'lat': element.get('lat', element.get('center', {}).get('lat', 0)),
                            'lon': element.get('lon', element.get('center', {}).get('lon', 0)),
                            'tags': element['tags']
                        }
                        pois.append(poi)
                return pois
        except Exception as e:
            print(f"❌ POI search failed: {e}")
        return []

    def store_poi_data(self, h3_index: str, pois: List[dict], source: str = 'overpass'):
        """Store POI data in database"""
        cursor = self.conn.cursor()
        for poi in pois:
            cursor.execute("""
                INSERT INTO poi_data (h3_index, poi_type, name, address, category, source, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (h3_index, poi.get('type', ''), poi.get('name', ''),
                  poi.get('address', ''), poi.get('category', ''),
                  source, datetime.now().isoformat()))
        self.conn.commit()

    def _is_sqlite_file(self, file_path: str) -> bool:
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)
            return header.startswith(b'SQLite format 3')
        except Exception:
            return False

    def normalize_phone_number(self, phone_number: str) -> str:
        """Normalize phone numbers to E.164-like format with Indian fallback."""
        if not phone_number:
            return ''

        cleaned = ''.join(ch for ch in phone_number if ch.isdigit() or ch == '+')
        if cleaned.startswith('00'):
            cleaned = '+' + cleaned[2:]

        digits = ''.join(ch for ch in cleaned if ch.isdigit())
        if cleaned.startswith('+'):
            return '+' + digits
        if len(digits) == 10 and digits[0] in '6789':
            return '+91' + digits
        if len(digits) == 11 and digits.startswith('0'):
            if digits[1] in '6789':
                return '+91' + digits[1:]
            return '+' + digits[1:]
        if 11 <= len(digits) <= 15:
            return '+' + digits
        return digits

    def classify_phone_number(self, phone_number: str) -> Dict[str, any]:
        """Classify a phone number as Indian or international and enrich with carrier/country."""
        normalized = self.normalize_phone_number(phone_number)
        details = {
            'phone_number': phone_number,
            'normalized': normalized,
            'country_code': None,
            'region': None,
            'carrier': None,
            'is_valid': False,
            'type': 'unknown',
            'international': None
        }

        try:
            import phonenumbers
            from phonenumbers import carrier, geocoder, PhoneNumberFormat, NumberParseException

            parsed = None
            if normalized.startswith('+'):
                parsed = phonenumbers.parse(normalized, None)
            else:
                parsed = phonenumbers.parse(phone_number, 'IN')

            details['country_code'] = str(parsed.country_code)
            details['region'] = geocoder.description_for_number(parsed, 'en') or phonenumbers.region_code_for_number(parsed)
            details['carrier'] = carrier.name_for_number(parsed, 'en')
            details['is_valid'] = phonenumbers.is_valid_number(parsed)
            details['type'] = phonenumbers.number_type(parsed).name if hasattr(phonenumbers.number_type(parsed), 'name') else str(phonenumbers.number_type(parsed))
            details['international'] = '+' + str(parsed.country_code)

            if details['country_code'] == '91':
                details['type'] = 'Indian'

        except Exception:
            country_match = re.match(r'^\+(\d{1,3})', normalized)
            details['country_code'] = country_match.group(1) if country_match else None
            details['international'] = '+' + details['country_code'] if details['country_code'] else None
            if details['country_code'] == '91' or (len(normalized) == 13 and normalized.startswith('+91')):
                details['type'] = 'Indian'
            details['is_valid'] = bool(re.match(r'^(?:\+91\d{10}|\+?\d{10,14})$', normalized))

        if not details['international'] and normalized.startswith('+'):
            details['international'] = normalized[:normalized.find(' ') if ' ' in normalized else len(normalized)]

        return details

    def extract_phone_numbers(self, text: str) -> List[Dict[str, any]]:
        """Extract Indian and international phone numbers from raw text."""
        if not text:
            return []

        normalized_text = text.replace('\u200e', '').replace('\u200f', '')
        results = []
        seen = set()

        try:
            import phonenumbers
            from phonenumbers import carrier, geocoder, PhoneNumberFormat, PhoneNumberMatcher

            for match in PhoneNumberMatcher(normalized_text, None):
                normalized = phonenumbers.format_number(match.number, PhoneNumberFormat.E164)
                if normalized in seen:
                    continue
                seen.add(normalized)
                details = self.classify_phone_number(normalized)
                details['raw'] = match.raw_string
                details['carrier'] = carrier.name_for_number(match.number, 'en')
                details['region'] = geocoder.description_for_number(match.number, 'en')
                results.append(details)

        except Exception:
            patterns = [
                r'(?:(?:\+91|91|0)[\s-]?[6-9]\d{9})',
                r'(?:(?:\+\d{1,3}|\d{1,4})[\s-]?(?:\d[\s-]?){6,12}\d)'
            ]
            for pattern in patterns:
                for match in re.findall(pattern, normalized_text):
                    normalized = self.normalize_phone_number(match)
                    if normalized in seen or not normalized:
                        continue
                    seen.add(normalized)
                    details = self.classify_phone_number(normalized)
                    details['raw'] = match
                    results.append(details)

        return results

    def store_phone_osint(self, phone_data: dict, source: str = 'text'):
        """Store or update phone OSINT metadata in the database."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO phone_osint
            (phone_number, normalized, country_code, region, carrier, is_valid, type, international, source, metadata, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            phone_data.get('phone_number'),
            phone_data.get('normalized'),
            phone_data.get('country_code'),
            phone_data.get('region'),
            phone_data.get('carrier'),
            int(phone_data.get('is_valid', False)),
            phone_data.get('type'),
            phone_data.get('international'),
            source,
            json.dumps(phone_data),
            datetime.now().isoformat()
        ))
        self.conn.commit()

    def phone_osint_enrichment(self, content: str) -> Dict[str, any]:
        """Extract and enrich phone numbers from content for OSINT investigations."""
        phones = self.extract_phone_numbers(content)
        for phone in phones:
            self.store_phone_osint(phone)
        return {'count': len(phones), 'numbers': phones}

    def phone_osint_lookup(self, phone_number: str) -> Dict[str, any]:
        """Lookup OSINT metadata for a single phone number."""
        details = self.classify_phone_number(phone_number)
        self.store_phone_osint(details)
        return details

    def extract_osint_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract OSINT entity types from raw text."""
        if not text:
            return {
                'urls': [],
                'domains': [],
                'emails': [],
                'ips': [],
                'phones': [],
                'bitcoin_addresses': [],
                'onion_domains': [],
                'hashtags': []
            }

        text = text.replace('\u200e', '').replace('\u200f', '')
        urls = list({match[0] for match in re.findall(r'\b(https?://[^\s"\)\]]+)', text, re.IGNORECASE)})
        emails = list({match for match in re.findall(r'[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}', text)})
        ips = list({match for match in re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)})
        bitcoin_addresses = list({match for match in re.findall(r'\b(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}\b', text)})
        onion_domains = list({match for match in re.findall(r'\b[a-z2-7]{16}\.onion\b|\b[a-z2-7]{56}\.onion\b', text, re.IGNORECASE)})
        hashtags = list({match for match in re.findall(r'#[A-Za-z0-9_]+', text)})
        phones = self.extract_phone_numbers(text)

        # Domains from URLs and standalone domain names
        domains = set()
        for url in urls:
            try:
                parsed = re.sub(r'^https?://', '', url, flags=re.IGNORECASE).split('/')[0]
                domains.add(self._normalize_domain(parsed))
            except Exception:
                continue

        for match in re.findall(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b', text):
            domain = self._normalize_domain(match)
            if domain and '.' in domain and not re.match(r'\d+\.\d+\.\d+\.\d+', domain):
                domains.add(domain)

        return {
            'urls': urls,
            'domains': sorted(domains),
            'emails': emails,
            'ips': ips,
            'phones': phones,
            'bitcoin_addresses': bitcoin_addresses,
            'onion_domains': onion_domains,
            'hashtags': hashtags
        }

    def _normalize_domain(self, domain: str) -> str:
        domain = domain.strip().lower()
        domain = re.sub(r'^www\.', '', domain)
        domain = re.sub(r'[\.:,;!\)\]\(\"]+$', '', domain)
        return domain

    def resolve_domain(self, domain: str) -> Dict[str, any]:
        """Resolve a domain to IP addresses."""
        try:
            addresses = socket.gethostbyname_ex(domain)[2]
            return {'resolved_ips': addresses}
        except Exception as e:
            return {'resolved_ips': [], 'error': str(e)}

    def whois_lookup(self, domain: str) -> Dict[str, any]:
        """Perform WHOIS lookup for a domain."""
        try:
            import whois
            w = whois.whois(domain)
            return {
                'domain_name': w.domain_name,
                'registrar': getattr(w, 'registrar', None),
                'creation_date': getattr(w, 'creation_date', None),
                'expiration_date': getattr(w, 'expiration_date', None),
                'name_servers': getattr(w, 'name_servers', None),
                'status': getattr(w, 'status', None),
                'emails': getattr(w, 'emails', None)
            }
        except Exception as e:
            return {'error': str(e)}

    def ip_geolocate(self, ip_address: str) -> Dict[str, any]:
        """Geolocate an IP address using free IP info services."""
        try:
            response = requests.get(f'https://ipinfo.io/{ip_address}/json', timeout=10)
            if response.status_code == 200:
                data = response.json()
                loc = data.get('loc', '')
                latitude, longitude = (None, None)
                if loc:
                    latitude, longitude = loc.split(',')
                return {
                    'ip': ip_address,
                    'city': data.get('city'),
                    'region': data.get('region'),
                    'country': data.get('country'),
                    'org': data.get('org'),
                    'latitude': float(latitude) if latitude else None,
                    'longitude': float(longitude) if longitude else None,
                    'raw': data
                }
        except Exception as e:
            return {'error': str(e), 'ip': ip_address}
        return {'ip': ip_address, 'error': 'No IP geolocation available'}

    def store_osint_entity(self, entity_type: str, entity_value: str, metadata: dict = None, evidence_id: str = '') -> int:
        """Store an OSINT entity and return its database ID."""
        normalized_value = entity_value.strip().lower()
        cursor = self.conn.cursor()
        existing = cursor.execute(
            "SELECT id FROM osint_entities WHERE entity_type = ? AND entity_value = ?",
            (entity_type, entity_value)
        ).fetchone()
        now = datetime.now().isoformat()
        if existing:
            entity_id = existing[0]
            cursor.execute(
                "UPDATE osint_entities SET metadata = ?, last_seen = ?, evidence_id = ? WHERE id = ?",
                (json.dumps(metadata or {}), now, evidence_id, entity_id)
            )
        else:
            cursor.execute(
                "INSERT INTO osint_entities (entity_type, entity_value, normalized_value, metadata, first_seen, last_seen, evidence_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (entity_type, entity_value, normalized_value, json.dumps(metadata or {}), now, now, evidence_id)
            )
            entity_id = cursor.lastrowid
        self.conn.commit()
        return entity_id

    def store_osint_relationship(self, source_entity_id: int, target_entity_id: int, relationship_type: str, evidence_id: str = '') -> int:
        """Store a relationship between two OSINT entities."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO osint_relationships (source_entity_id, target_entity_id, relationship_type, evidence_id, timestamp) VALUES (?, ?, ?, ?, ?)",
            (source_entity_id, target_entity_id, relationship_type, evidence_id, datetime.now().isoformat())
        )
        self.conn.commit()
        return cursor.lastrowid

    def analyze_osint_text(self, content: str, evidence_id: str = '') -> Dict[str, any]:
        """Run a Bellingcat-style OSINT entity extraction and relationship analysis."""
        entities = self.extract_osint_entities(content)
        summary = {
            'entities': {},
            'relationships': [],
            'enrichment': {}
        }

        # Persist extracted entities
        entity_ids = {}
        for entity_type in ['urls', 'domains', 'emails', 'ips', 'phones', 'bitcoin_addresses', 'onion_domains', 'hashtags']:
            values = entities.get(entity_type, [])
            summary['entities'][entity_type] = []
            for item in values:
                metadata = {}
                if entity_type == 'domains':
                    whois_data = self.whois_lookup(item)
                    dns_info = self.resolve_domain(item)
                    metadata.update({'whois': whois_data, 'dns': dns_info})
                    summary['enrichment'][item] = {'whois': whois_data, 'dns': dns_info}
                elif entity_type == 'ips':
                    geo = self.ip_geolocate(item)
                    metadata.update({'geo': geo})
                    summary['enrichment'][item] = geo
                elif entity_type == 'phones':
                    phone_metadata = self.classify_phone_number(item.get('normalized') if isinstance(item, dict) else item)
                    metadata.update({'phone': phone_metadata})
                    summary['enrichment'][item if isinstance(item, str) else item.get('normalized')] = phone_metadata
                entity_value = item if isinstance(item, str) else item.get('normalized', item)
                entity_id = self.store_osint_entity(entity_type, entity_value, metadata, evidence_id)
                entity_ids[f'{entity_type}:{entity_value}'] = entity_id
                summary['entities'][entity_type].append({'value': entity_value, 'metadata': metadata})

        # Build simple relationships
        for email in entities.get('emails', []):
            for domain in entities.get('domains', []):
                email_id = entity_ids.get(f'emails:{email}')
                domain_id = entity_ids.get(f'domains:{domain}')
                if email_id and domain_id:
                    rel_id = self.store_osint_relationship(email_id, domain_id, 'email-hosts', evidence_id)
                    summary['relationships'].append({'source': email, 'target': domain, 'type': 'email-hosts', 'id': rel_id})

        for ip in entities.get('ips', []):
            for domain in entities.get('domains', []):
                ip_id = entity_ids.get(f'ips:{ip}')
                domain_id = entity_ids.get(f'domains:{domain}')
                if ip_id and domain_id:
                    rel_id = self.store_osint_relationship(domain_id, ip_id, 'domain-resolves-to', evidence_id)
                    summary['relationships'].append({'source': domain, 'target': ip, 'type': 'domain-resolves-to', 'id': rel_id})

        for phone in entities.get('phones', []):
            phone_value = phone.get('normalized') if isinstance(phone, dict) else phone
            phone_id = entity_ids.get(f'phones:{phone_value}')
            if not phone_id:
                continue
            for domain in entities.get('domains', []):
                domain_id = entity_ids.get(f'domains:{domain}')
                if domain_id:
                    rel_id = self.store_osint_relationship(phone_id, domain_id, 'phone-linked-domain', evidence_id)
                    summary['relationships'].append({
                        'source': phone_value,
                        'target': domain,
                        'type': 'phone-linked-domain',
                        'id': rel_id
                    })

        return summary

    def get_osint_entities(self) -> List[dict]:
        cursor = self.conn.cursor()
        rows = cursor.execute('SELECT entity_type, entity_value, metadata, first_seen, last_seen, evidence_id FROM osint_entities').fetchall()
        return [{'entity_type': row[0], 'entity_value': row[1], 'metadata': json.loads(row[2]) if row[2] else {}, 'first_seen': row[3], 'last_seen': row[4], 'evidence_id': row[5]} for row in rows]

    def get_osint_graph(self) -> Dict[str, any]:
        nodes = []
        edges = []
        cursor = self.conn.cursor()
        entity_rows = cursor.execute('SELECT id, entity_type, entity_value, metadata FROM osint_entities').fetchall()
        for row in entity_rows:
            metadata = json.loads(row[3]) if row[3] else {}
            nodes.append({'id': row[0], 'type': row[1], 'value': row[2], 'metadata': metadata})
        rel_rows = cursor.execute('SELECT source_entity_id, target_entity_id, relationship_type FROM osint_relationships').fetchall()
        for row in rel_rows:
            edges.append({'source': row[0], 'target': row[1], 'relationship_type': row[2]})
        return {'nodes': nodes, 'edges': edges}

    def export_entity_graph_json(self, output_file: str = 'entity_graph.json') -> str:
        graph = self.get_osint_graph()
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(graph, f, indent=2)
        return output_file

    def create_entity_map(self, output_file: str = 'entity_map.html') -> str:
        cursor = self.conn.cursor()
        rows = cursor.execute('SELECT entity_type, entity_value, metadata FROM osint_entities').fetchall()
        markers = []
        for entity_type, entity_value, metadata_json in rows:
            metadata = json.loads(metadata_json or '{}')
            loc = None
            if isinstance(metadata, dict):
                geo = metadata.get('geo') or metadata.get('phone', {})
                if isinstance(geo, dict) and geo.get('latitude') and geo.get('longitude'):
                    loc = (geo.get('latitude'), geo.get('longitude'))
            if loc:
                markers.append({'type': entity_type, 'value': entity_value, 'lat': loc[0], 'lon': loc[1], 'metadata': metadata})

        if not markers:
            print('⚠️ No geolocated OSINT entities to map')
            return None

        df = pd.DataFrame(markers)
        visualizer = MapVisualizer()
        return visualizer.create_entity_map(df, output_file)

    def export_maltego_graph(self, output_file: str = 'maltego_graph.json') -> str:
        return self.export_entity_graph_json(output_file)

    def analyze_android_artifacts(self, file_path: str, evidence_id: str = '') -> Dict[str, any]:
        """Analyze Android artifact files and extract phone numbers, IMEIs, Android IDs, and metadata."""
        if not Path(file_path).exists():
            return {'error': f'File not found: {file_path}'}

        result = {
            'file_path': file_path,
            'artifact_type': 'android',
            'phone_numbers': [],
            'imei': [],
            'android_ids': [],
            'tables': [],
            'errors': []
        }

        try:
            if self._is_sqlite_file(file_path) or file_path.lower().endswith('.db'):
                conn = sqlite3.connect(file_path)
                tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
                result['tables'] = tables
                for table in tables:
                    try:
                        rows = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 1000", conn)
                        text = ' '.join(rows.astype(str).fillna('').values.flatten())
                        result['phone_numbers'].extend(self.extract_phone_numbers(text))
                        result['imei'].extend(re.findall(r'\b(?:IMEI[:=\s]*)(\d{15})\b', text, re.IGNORECASE))
                        result['android_ids'].extend(re.findall(r'\b[a-fA-F0-9]{16,64}\b', text))
                    except Exception:
                        continue
                conn.close()
            else:
                content = Path(file_path).read_text(errors='ignore')
                result['phone_numbers'] = self.extract_phone_numbers(content)
                result['imei'] = re.findall(r'\b(?:IMEI[:=\s]*)(\d{15})\b', content, re.IGNORECASE)
                result['android_ids'] = re.findall(r'\b[a-fA-F0-9]{16,64}\b', content)

            cursor = self.conn.cursor()
            for phone in result['phone_numbers']:
                self.store_phone_osint(phone, source='android_artifact')
            for phone in result['phone_numbers']:
                cursor.execute("""
                    INSERT INTO android_artifacts (file_path, artifact_type, key, value, evidence_id, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_path,
                    'phone_number',
                    phone.get('phone_number'),
                    phone.get('normalized'),
                    evidence_id,
                    datetime.now().isoformat(),
                    json.dumps(phone)
                ))
            for imei in result['imei']:
                cursor.execute("""
                    INSERT INTO android_artifacts (file_path, artifact_type, key, value, evidence_id, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_path,
                    'imei',
                    'imei',
                    imei,
                    evidence_id,
                    datetime.now().isoformat(),
                    json.dumps({'imei': imei})
                ))
            self.conn.commit()

        except Exception as e:
            result['errors'].append(str(e))

        return result

    def analyze_linux_artifacts(self, file_path: str, keywords: List[str] = None, evidence_id: str = '') -> Dict[str, any]:
        """Analyze Linux logs and artifacts for suspicious activity and phone-related OSINT."""
        if not Path(file_path).exists():
            return {'error': f'File not found: {file_path}'}

        keywords = keywords or ['ssh', 'sudo', 'failed password', 'accepted password', 'cron', 'systemd', 'login', 'logout', 'usb']
        result = {
            'file_path': file_path,
            'artifact_type': 'linux',
            'matched_lines': [],
            'phone_numbers': [],
            'keywords': keywords,
            'errors': []
        }

        try:
            content = Path(file_path).read_text(errors='ignore')
            lines = []
            for line in content.splitlines():
                low = line.lower()
                if any(keyword in low for keyword in keywords) or re.search(r'\+?\d[\d\s\-]{7,}\d', line):
                    lines.append(line)
            result['matched_lines'] = lines[:100]
            result['phone_numbers'] = self.extract_phone_numbers(content)

            cursor = self.conn.cursor()
            for phone in result['phone_numbers']:
                self.store_phone_osint(phone, source='linux_artifact')
                cursor.execute("""
                    INSERT INTO linux_artifacts (file_path, artifact_type, key, value, evidence_id, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_path,
                    'phone_number',
                    phone.get('phone_number'),
                    phone.get('normalized'),
                    evidence_id,
                    datetime.now().isoformat(),
                    json.dumps(phone)
                ))
            for line in result['matched_lines']:
                cursor.execute("""
                    INSERT INTO linux_artifacts (file_path, artifact_type, key, value, evidence_id, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_path,
                    'matched_line',
                    line[:100],
                    line,
                    evidence_id,
                    datetime.now().isoformat(),
                    json.dumps({'line': line})
                ))
            self.conn.commit()

        except Exception as e:
            result['errors'].append(str(e))

        return result

    # ADVANCED H3 ANALYSIS
    def query_hex_neighbors(self, lat: float, lon: float, distance_km: float = 1.0,
                           resolution: Optional[int] = None) -> pd.DataFrame:
        """Query locations within H3 distance"""
        center_hex = self.geo_to_h3(lat, lon, resolution)
        if not center_hex:
            return pd.DataFrame()

        # Calculate k based on distance and resolution
        edge_len = self.h3_edge_length(self.get_h3_resolution(center_hex), 'km')
        k = max(1, int(distance_km / (edge_len * 1.5)))  # Approximate

        neighbor_hexes = self.hex_range(center_hex, k)

        cursor = self.conn.cursor()
        if not neighbor_hexes:
            return pd.DataFrame()
        hex_list = ','.join('?' * len(neighbor_hexes))
        cursor.execute(f"SELECT * FROM locations WHERE h3_index IN ({hex_list}) ORDER BY timestamp DESC",
                      list(neighbor_hexes))
        columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(cursor.fetchall(), columns=columns)

    def hotspot_analysis(self, device_id: str = None, days: int = 30,
                        resolution: Optional[int] = None) -> Dict[str, int]:
        """Advanced hotspot analysis with H3 clustering"""
        if resolution is None:
            resolution = self.resolution

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()[:10]
        cursor = self.conn.cursor()

        query = """
        SELECT h3_index, COUNT(*) as visits
        FROM locations
        WHERE date(timestamp) > ?
        """
        params = [cutoff]

        if device_id:
            query += " AND device_id = ?"
            params.append(device_id)

        query += " GROUP BY h3_index ORDER BY visits DESC"

        cursor.execute(query, params)
        return {row[0]: row[1] for row in cursor.fetchall()}

    def detect_anomalies(self, device_id: str, sensitivity: float = 2.0, use_ml: bool = True) -> pd.DataFrame:
        """Advanced anomaly detection using statistical and ML methods"""
        # Get all locations for device
        df = pd.read_sql(f"SELECT * FROM locations WHERE device_id='{device_id}'", self.conn)

        if df.empty:
            return pd.DataFrame()

        # Group by H3 and count
        hex_counts = df['h3_index'].value_counts()

        anomalies = pd.DataFrame()

        # Statistical anomaly detection (z-score)
        if len(hex_counts) > 1:
            mean_visits = hex_counts.mean()
            std_visits = hex_counts.std()
            if std_visits > 0:
                z_scores = (hex_counts - mean_visits) / std_visits
                stat_anomalies = hex_counts[z_scores > sensitivity]
            else:
                stat_anomalies = hex_counts[hex_counts > mean_visits + 1]
        else:
            stat_anomalies = hex_counts

        # ML-based anomaly detection (Isolation Forest)
        if use_ml and len(hex_counts) > 10:  # Need sufficient data for ML
            try:
                from sklearn.ensemble import IsolationForest
                import numpy as np

                # Prepare features: visit count, hex resolution, etc.
                features = []
                for hex_id, count in hex_counts.items():
                    resolution = self.get_h3_resolution(hex_id)
                    # Add more features if available
                    features.append([count, resolution])

                features = np.array(features)

                # Train Isolation Forest
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                predictions = iso_forest.fit_predict(features)

                # Anomalies are marked as -1
                ml_anomalies = hex_counts.iloc[np.where(predictions == -1)[0]]

                # Combine statistical and ML anomalies
                all_anomalies = pd.concat([stat_anomalies, ml_anomalies]).drop_duplicates()
                anomalies = pd.DataFrame({
                    'hex_id': all_anomalies.index,
                    'visit_count': all_anomalies.values,
                    'is_anomaly': True,
                    'detection_method': ['statistical' if h in stat_anomalies.index else 'ml' for h in all_anomalies.index]
                })
            except ImportError:
                print("⚠️ scikit-learn not available, using statistical detection only")
                anomalies = pd.DataFrame({
                    'hex_id': stat_anomalies.index,
                    'visit_count': stat_anomalies.values,
                    'is_anomaly': True,
                    'detection_method': 'statistical'
                })
        else:
            anomalies = pd.DataFrame({
                'hex_id': stat_anomalies.index,
                'visit_count': stat_anomalies.values,
                'is_anomaly': True,
                'detection_method': 'statistical'
            })

        return anomalies

    def analyze_movement_patterns(self, device_id: str) -> Dict[str, any]:
        """Analyze movement patterns using H3 trajectories"""
        df = pd.read_sql(f"""
            SELECT timestamp, h3_index, lat, lon, speed
            FROM locations
            WHERE device_id='{device_id}'
            ORDER BY timestamp
        """, self.conn)

        if df.empty:
            return {'error': 'No data for device'}

        patterns = {
            'total_points': len(df),
            'unique_hexes': df['h3_index'].nunique(),
            'time_span': (pd.to_datetime(df['timestamp'].max()) - pd.to_datetime(df['timestamp'].min())).days,
            'avg_speed': df['speed'].mean(),
            'max_speed': df['speed'].max()
        }

        # Detect home/work locations (most frequent at night/morning)
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        night_locations = df[(df['hour'] >= 22) | (df['hour'] <= 6)]['h3_index'].value_counts()
        morning_locations = df[(df['hour'] >= 6) & (df['hour'] <= 10)]['h3_index'].value_counts()

        patterns['potential_home'] = night_locations.idxmax() if not night_locations.empty else None
        patterns['potential_work'] = morning_locations.idxmax() if not morning_locations.empty else None

        return patterns

    def privacy_risk_assessment(self, device_id: str) -> Dict[str, any]:
        """Assess privacy risks based on location patterns"""
        patterns = self.analyze_movement_patterns(device_id)
        hotspots = self.hotspot_analysis(device_id)

        risks = {
            'tracking_risk': 'High' if patterns.get('unique_hexes', 0) > 100 else 'Low',
            'location_diversity': patterns.get('unique_hexes', 0),
            'temporal_coverage': patterns.get('time_span', 0),
            'hotspot_count': len(hotspots),
            'most_visited_hex': max(hotspots, key=hotspots.get) if hotspots else None
        }

        # Calculate entropy (location randomness)
        if hotspots:
            total_visits = sum(hotspots.values())
            probabilities = [count/total_visits for count in hotspots.values()]
            entropy = -sum(p * math.log2(p) for p in probabilities)
            risks['location_entropy'] = entropy
            risks['predictability'] = 'High' if entropy < 2 else 'Low'

        return risks

    def temporal_analysis(self, device_id: str, time_window: str = 'hour') -> pd.DataFrame:
        """Analyze location patterns by time"""
        df = pd.read_sql(f"SELECT * FROM locations WHERE device_id='{device_id}'", self.conn)
        if df.empty:
            return pd.DataFrame()

        df['timestamp'] = pd.to_datetime(df['timestamp'])

        if time_window == 'hour':
            df['time_group'] = df['timestamp'].dt.hour
        elif time_window == 'day':
            df['time_group'] = df['timestamp'].dt.dayofweek
        elif time_window == 'month':
            df['time_group'] = df['timestamp'].dt.month

        return df.groupby(['time_group', 'h3_index']).size().reset_index(name='count')

    # VISUALIZATION & EXPORT
    def create_interactive_map(self, device_id: str = None, output_file: str = 'map.html', map_type: str = 'multi'):
        """Create interactive Folium map with H3 hexagons and advanced visualizations
        
        Args:
            device_id: Filter by device ID (optional)
            output_file: Output HTML file path
            map_type: Type of map - 'multi' (default), 'heatmap', 'hexagon', 'cluster', 'trajectory', 'comparison'
        """
        query = "SELECT * FROM locations"
        params = []
        if device_id:
            query += " WHERE device_id = ?"
            params.append(device_id)

        df = pd.read_sql(query, self.conn, params=params)
        
        if df.empty:
            print("⚠️ No location data available")
            return None

        visualizer = MapVisualizer()
        
        if map_type == 'heatmap':
            return visualizer.create_heatmap(df, output_file)
        elif map_type == 'hexagon':
            hotspots = self.hotspot_analysis(device_id)
            return visualizer.create_hexagon_map(hotspots, output_file)
        elif map_type == 'cluster':
            return visualizer.create_cluster_map(df, output_file)
        elif map_type == 'trajectory':
            return visualizer.create_trajectory_map(df, output_file)
        elif map_type == 'osint':
            return self.create_entity_map(output_file)
        elif map_type == 'multi':
            hotspots = self.hotspot_analysis(device_id)
            return visualizer.create_multi_layer_map(df, hotspots, output_file)
        elif map_type == 'comparison':
            # Get all devices
            devices_query = "SELECT DISTINCT device_id FROM locations"
            devices = [row[0] for row in self.conn.execute(devices_query).fetchall()]
            devices_data = {}
            for dev_id in devices:
                dev_query = "SELECT * FROM locations WHERE device_id = ?"
                devices_data[dev_id] = pd.read_sql(dev_query, self.conn, params=[dev_id])
            return visualizer.create_comparison_map(devices_data, output_file)
        else:
            # Default to multi-layer
            hotspots = self.hotspot_analysis(device_id)
            return visualizer.create_multi_layer_map(df, hotspots, output_file)

    def export_kml(self, device_id: str = None, output_file: str = 'locations.kml'):
        """Export locations to KML for Google Earth"""
        kml = simplekml.Kml()

        query = "SELECT * FROM locations"
        if device_id:
            query += f" WHERE device_id='{device_id}'"

        df = pd.read_sql(query, self.conn)

        for _, row in df.iterrows():
            pnt = kml.newpoint()
            pnt.coords = [(row['lon'], row['lat'])]
            pnt.name = f"{row['device_id']} - {row['timestamp']}"

        kml.save(output_file)
        print(f"📍 KML exported to {output_file}")

    def export_autopsy_csv(self, case_id: str, output_dir: str = 'autopsy_export'):
        """Export for Autopsy forensic tool"""
        os.makedirs(output_dir, exist_ok=True)
        df = pd.read_sql("SELECT * FROM locations", self.conn)
        df.to_csv(f"{output_dir}/case_{case_id}_locations.csv", index=False)
        print(f"📤 Autopsy export: {output_dir}")

    # UTILITY FUNCTIONS
    def verify_integrity(self) -> bool:
        """Verify chain of custody"""
        custody_file = self.db_path.with_suffix('.custody.json')
        if not custody_file.exists():
            return False

        with open(custody_file) as f:
            custody = json.load(f)

        for entry in custody:
            p = Path(entry['file_path'])
            if p.exists():
                current_hash = hashlib.sha256(open(p, 'rb').read()).hexdigest()
                if current_hash != entry['file_hash']:
                    print(f"❌ TAMPERED: {entry['file_path']}")
                    return False
        print("✅ Chain of custody VERIFIED")
        return True

    def get_statistics(self) -> dict:
        """Get database statistics"""
        cursor = self.conn.cursor()
        stats = {}

        cursor.execute("SELECT COUNT(*) FROM locations")
        stats['total_locations'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT device_id) FROM locations")
        stats['unique_devices'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT h3_index) FROM locations")
        stats['unique_hexes'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM poi_data")
        stats['poi_entries'] = cursor.fetchone()[0]

        return stats

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

