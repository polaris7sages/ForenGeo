#!/usr/bin/env python3
"""Generate KML exports for all devices and global export."""
from forensic_h3_fixed import ForensicH3Analyzer
from pathlib import Path
import os

DB_PATH = Path('.fh3.db')
OUTPUT_DIR = Path('maps')
OUTPUT_DIR.mkdir(exist_ok=True)

analyzer = ForensicH3Analyzer(str(DB_PATH))

# Global export
global_kml = OUTPUT_DIR / 'forengeo_export_all.kml'
print(f"Exporting global KML to {global_kml}")
analyzer.export_kml(None, str(global_kml))

# Per-device exports
cursor = analyzer.conn.cursor()
cursor.execute("SELECT DISTINCT device_id FROM locations")
rows = cursor.fetchall()
for (device_id,) in rows:
    if not device_id:
        continue
    safe_id = device_id.replace(' ', '_').replace('/', '_')
    out_file = OUTPUT_DIR / f'forengeo_export_{safe_id}.kml'
    print(f"Exporting device KML for {device_id} -> {out_file}")
    analyzer.export_kml(device_id, str(out_file))

print("Done generating KML exports.")
