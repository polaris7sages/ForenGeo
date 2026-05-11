import h3
import pandas as pd
import sqlite3
import json
import hashlib
import os
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

        neighbor_hexes = self.k_ring(center_hex, k)

        cursor = self.conn.cursor()
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

    def detect_anomalies(self, device_id: str, sensitivity: float = 2.0) -> pd.DataFrame:
        """Statistical anomaly detection using H3 patterns"""
        # Get baseline (frequent locations)
        baseline = set(self.hotspot_analysis(device_id, 30).keys())

        # Get all locations for device
        df = pd.read_sql(f"SELECT * FROM locations WHERE device_id='{device_id}'", self.conn)

        if df.empty:
            return pd.DataFrame()

        # Group by H3 and count
        hex_counts = df['h3_index'].value_counts()

        # Calculate z-scores for anomaly detection
        if len(hex_counts) > 1:
            mean_visits = hex_counts.mean()
            std_visits = hex_counts.std()
            if std_visits > 0:
                z_scores = (hex_counts - mean_visits) / std_visits
                anomalies = hex_counts[z_scores > sensitivity]
            else:
                anomalies = hex_counts[hex_counts > mean_visits + 1]
        else:
            anomalies = hex_counts

        return pd.DataFrame({
            'hex_id': anomalies.index,
            'visit_count': anomalies.values,
            'is_anomaly': True
        })

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
    def create_interactive_map(self, device_id: str = None, output_file: str = 'map.html'):
        """Create interactive Folium map with H3 hexagons"""
        m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)

        query = "SELECT * FROM locations"
        if device_id:
            query += f" WHERE device_id='{device_id}'"

        df = pd.read_sql(query, self.conn)

        if not df.empty:
            # Add location points
            for _, row in df.iterrows():
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=3,
                    color='blue',
                    fill=True,
                    popup=f"Time: {row['timestamp']}<br>Device: {row['device_id']}"
                ).add_to(m)

            # Add H3 hexagons for hotspots
            hotspots = self.hotspot_analysis(device_id)
            for h3_hex, count in hotspots.items():
                if count > 5:  # Only show significant hotspots
                    boundary = self.h3_to_boundary(h3_hex)
                    if boundary:
                        folium.Polygon(
                            locations=boundary,
                            color='red',
                            fill=True,
                            fill_opacity=0.3,
                            popup=f"Visits: {count}"
                        ).add_to(m)

        m.save(output_file)
        print(f"🗺️ Map saved to {output_file}")

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

