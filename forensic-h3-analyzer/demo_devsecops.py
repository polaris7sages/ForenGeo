#!/usr/bin/env python3
"""DevSecOps demonstration script for ForenGeo.

This script exercises core H3 forensic analysis, map generation, and dark web correlation
without relying on external network services.
"""

import os
from pathlib import Path
from forensic_h3_fixed import ForensicH3Analyzer
from deepweb_forensics import DeepWebForensics

OUTPUT_DB = Path("devsecops_demo.db")
OUTPUT_DIR = Path("devsecops_outputs")

SAMPLE_LOCATIONS = [
    (40.7128, -74.0060, "2024-06-01T08:00:00Z", "device_a", "Browser"),
    (40.7306, -73.9352, "2024-06-01T09:00:00Z", "device_a", "Maps"),
    (40.7580, -73.9855, "2024-06-01T10:00:00Z", "device_b", "Camera"),
    (40.7527, -73.9772, "2024-06-01T11:00:00Z", "device_b", "Mail"),
    (40.7484, -73.9857, "2024-06-01T12:00:00Z", "device_c", "Notes"),
]

SAMPLE_DARKWEB_CONTENT = """
User visited http://silkroad3fzhx.onion and posted a marketplace listing.
Bitcoin payment was requested to bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh.
A Tor exit node 185.220.101.1 was used to route traffic.
Ethereum address 0x32Be343B94f860124dC4fEe278FADBD03915C147 was shared.
"""


def ensure_clean():
    if OUTPUT_DB.exists():
        OUTPUT_DB.unlink()
    if OUTPUT_DIR.exists():
        for child in OUTPUT_DIR.glob("**/*"):
            if child.is_file():
                child.unlink()
        OUTPUT_DIR.rmdir()


def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def main():
    print_section("ForenGeo DevSecOps Capability Demo")
    ensure_clean()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    analyzer = ForensicH3Analyzer(str(OUTPUT_DB))
    print("✅ Initialized forensic database")

    for lat, lon, ts, device, app in SAMPLE_LOCATIONS:
        analyzer.add_location(lat, lon, ts, device, app)
    print(f"✅ Added {len(SAMPLE_LOCATIONS)} sample locations")

    stats = analyzer.get_statistics()
    print(f"📊 Total locations: {stats['total_locations']}")
    print(f"📊 Unique devices: {stats['unique_devices']}")
    print(f"📊 Unique H3 hexes: {stats['unique_hexes']}")

    hotspots = analyzer.hotspot_analysis()
    print(f"🔥 Hotspots found: {len(hotspots)}")
    for rank, (h3_hex, count) in enumerate(list(hotspots.items())[:3], start=1):
        lat, lon = analyzer.h3_to_geo(h3_hex)
        print(f"   {rank}. {h3_hex} @ {lat:.4f},{lon:.4f} ({count} visits)")

    output_map = OUTPUT_DIR / "demo_devsecops_map.html"
    analyzer.create_interactive_map(output_file=str(output_map))
    print(f"🗺️ Created interactive map: {output_map}")

    output_export = OUTPUT_DIR / "demo_devsecops_autopsy.csv"
    analyzer.export_autopsy_csv("DEVSECOPS", str(OUTPUT_DIR))
    print(f"📤 Exported Autopsy CSV to {OUTPUT_DIR}")

    analyzer.close()

    deepweb = DeepWebForensics()
    dark_results = deepweb.comprehensive_deepweb_analysis(SAMPLE_DARKWEB_CONTENT)
    deepweb.close()

    print_section("Deep Web Forensics Summary")
    print(f"Tor exit nodes: {dark_results['analysis']['tor']['analysis'].get('exit_nodes_found', 0)}")
    print(f"Onion domains: {dark_results['analysis']['onion']['analysis'].get('total_domains', 0)}")
    print(f"Crypto addresses: {dark_results['analysis']['crypto']['analysis'].get('total_addresses', 0)}")
    print(f"Marketplace matches: {dark_results['analysis']['marketplace']['analysis'].get('products_found', 0)}")

    print_section("Demo Complete")
    print(f"Open the generated map at: {output_map}")
    print(f"Review export files in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
