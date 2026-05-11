from datetime import datetime, timedelta  # ADD THIS LINE
import tempfile  # ADD THIS LINE
import h3
import pandas as pd
import sqlite3
import json
import hashlib
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict
import simplekml
import folium
from scipy import stats  # NEW: pip install scipy

class ForensicH3Indexer:
    def __init__(self, db_path: str = "fh3.db", resolution: int = 8):
        self.db_path = Path(db_path)
        self.resolution = resolution
        self.conn = None
        self.chain_of_custody = []
        self._init_db()
        self._load_custody()
    
    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
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
                evidence_id TEXT
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_h3 ON locations(h3_index)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_device ON locations(device_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_time ON locations(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_evidence ON locations(evidence_id)")
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
    
    # ORIGINAL METHODS (unchanged - paste from previous)
    def geohash_location(self, lat: float, lon: float, resolution: Optional[int] = None) -> str:
        if resolution is None: resolution = self.resolution
        try: return h3.latlng_to_cell(lat, lon, resolution)
        except: return ""
    
    def add_location(self, lat: float, lon: float, timestamp: str, device_id: str, 
                    app_name: str = "", metadata: dict = None, evidence_id: str = ""):
        h3_hex = self.geohash_location(lat, lon)
        if not h3_hex: return False
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO locations (timestamp, lat, lon, h3_index, device_id, app_name, metadata, evidence_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, lat, lon, h3_hex, device_id, app_name, 
              json.dumps(metadata or {}), evidence_id))
        self.conn.commit()
        return True
    
    def bulk_import_plist(self, plist_path: str, device_id: str, evidence_id: str = ""):
        import plistlib
        try:
            with open(plist_path, 'rb') as f:
                locations = plistlib.load(f)
            count = 0
            for loc in locations:
                if 'Latitude' in loc and 'Longitude' in loc:
                    self.add_location(loc['Latitude'], loc['Longitude'],
                                    loc.get('Timestamp', ''), device_id,
                                    loc.get('AppName', ''), {}, evidence_id)
                    count += 1
            print(f"✅ Imported {count} locations from {plist_path}")
        except Exception as e:
            print(f"❌ Plist import failed: {e}")
    
    # ALL NEW MISSING FEATURES HERE 👇
    def add_with_hash(self, file_path: str, evidence_id: str):
        """🚨 CHAIN OF CUSTODY - Cryptographic verification"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""): hasher.update(chunk)
        
        custody_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'evidence_id': evidence_id,
            'file_path': str(Path(file_path).absolute()),
            'file_hash': hasher.hexdigest(),
            'user': os.getenv('USER', 'unknown'),
            'operation': 'IMPORT'
        }
        self.chain_of_custody.append(custody_entry)
        self._save_custody()
        
        self.bulk_import_plist(file_path, f"{evidence_id}_{Path(file_path).stem}", evidence_id)
    
    def verify_integrity(self) -> bool:
        """🔒 Verify chain of custody"""
        custody_file = self.db_path.with_suffix('.custody.json')
        if not custody_file.exists(): return False
        
        with open(custody_file) as f: custody = json.load(f)
        for entry in custody:
            p = Path(entry['file_path'])
            if p.exists():
                current_hash = hashlib.sha256(open(p, 'rb').read()).hexdigest()
                if current_hash != entry['file_hash']:
                    print(f"❌ TAMPERED: {entry['file_path']}")
                    return False
        print("✅ Chain of custody VERIFIED")
        return True
    
    def query_hex_neighbors(self, lat: float, lon: float, distance_km: float = 1.0) -> pd.DataFrame:
        center_hex = self.geohash_location(lat, lon)
        ring_size = max(1, int(distance_km / 0.1))
        neighbor_hexes = h3.k_ring(center_hex, ring_size)
        
        cursor = self.conn.cursor()
        hex_list = ','.join('?' * len(neighbor_hexes))
        cursor.execute(f"SELECT * FROM locations WHERE h3_index IN ({hex_list}) ORDER BY timestamp DESC", list(neighbor_hexes))
        columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(cursor.fetchall(), columns=columns)
    
    def hotspot_analysis(self, device_id: str = None, days: int = 30) -> Dict[str, int]:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()[:10]
        cursor = self.conn.cursor()
        if device_id:
            cursor.execute("SELECT h3_index, COUNT(*) as visits FROM locations WHERE device_id=? AND date(timestamp)>? GROUP BY h3_index ORDER BY visits DESC", (device_id, cutoff))
        else:
            cursor.execute(f"SELECT h3_index, COUNT(*) as visits FROM locations WHERE date(timestamp)>? GROUP BY h3_index ORDER BY visits DESC", (cutoff,))
        return {row[0]: row[1] for row in cursor.fetchall()}
    
    def detect_anomalies(self, device_id: str) -> pd.DataFrame:
        """🕵️ ANOMALY DETECTION"""
        baseline = set(self.hotspot_analysis(device_id, 30).keys())
        df = pd.read_sql(f"SELECT h3_index FROM locations WHERE device_id='{device_id}'", self.conn)
        
        anomalies = df[~df['h3_index'].isin(baseline)].value_counts()
        return pd.DataFrame({'hex_id': anomalies.index, 'count': anomalies.values})
    
    def export_autopsy_tsk(self, case_id: str, output_dir: str):
        """🔗 AUTOPSY INTEGRATION"""
        os.makedirs(output_dir, exist_ok=True)
        df = pd.read_sql("SELECT * FROM locations", self.conn)
        df.to_csv(f"{output_dir}/case_{case_id}_locations.csv", index=False)
        print(f"📤 Autopsy export: {output_dir}")
    
    def close(self):
        if self.conn: self.conn.close()