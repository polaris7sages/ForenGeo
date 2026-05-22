import os
from pathlib import Path
from forensic_h3_fixed import ForensicH3Analyzer


def test_core_h3_workflow(tmp_path):
    db_path = tmp_path / "devsecops_test.db"
    analyzer = ForensicH3Analyzer(str(db_path))

    analyzer.add_location(40.7128, -74.0060, "2024-05-07T10:00:00Z", "device-devsecops", "TestApp")
    analyzer.add_location(40.7138, -74.0070, "2024-05-07T11:00:00Z", "device-devsecops", "TestApp")
    analyzer.add_location(40.7148, -74.0080, "2024-05-07T12:00:00Z", "device-devsecops", "TestApp")

    stats = analyzer.get_statistics()
    assert stats["total_locations"] == 3
    assert stats["unique_devices"] == 1
    assert stats["unique_hexes"] >= 1

    h3_index = analyzer.geo_to_h3(40.7128, -74.0060)
    lat, lon = analyzer.h3_to_geo(h3_index)
    assert abs(lat - 40.7128) < 0.1
    assert abs(lon + 74.0060) < 0.1

    results = analyzer.query_hex_neighbors(40.7128, -74.0060, 1.0)
    assert len(results) >= 1

    output_dir = tmp_path / "autopsy"
    analyzer.export_autopsy_csv("DEVSECOPS", str(output_dir))
    assert (output_dir / "case_DEVSECOPS_locations.csv").exists()

    output_map = tmp_path / "devsecops_map.html"
    map_result = analyzer.create_interactive_map(output_file=str(output_map), map_type="heatmap")
    assert map_result is not None
    assert output_map.exists()

    analyzer.close()


def test_phone_osint_and_artifact_analysis(tmp_path):
    analyzer = ForensicH3Analyzer(str(tmp_path / "devsecops_phone.db"))
    sample_text = "+91 98765 43210 called +1-202-555-0143 and shared IMEI: 356938035643809"
    extracted = analyzer.extract_phone_numbers(sample_text)
    assert len(extracted) >= 2
    assert any(item.get('country_code') == '91' for item in extracted)
    assert any(item.get('country_code') == '1' for item in extracted)

    osint = analyzer.phone_osint_enrichment(sample_text)
    assert osint['count'] >= 2

    android_artifact = tmp_path / "android_sample.txt"
    android_artifact.write_text(sample_text, encoding='utf-8')
    android_result = analyzer.analyze_android_artifacts(str(android_artifact), evidence_id='TESTCASE')
    assert 'phone_numbers' in android_result
    assert len(android_result['phone_numbers']) >= 2

    linux_artifact = tmp_path / "linux_sample.log"
    linux_artifact.write_text("ssh login failed for user test from +44 203 123 4567\ncron job started\n", encoding='utf-8')
    linux_result = analyzer.analyze_linux_artifacts(str(linux_artifact), evidence_id='TESTCASE')
    assert 'phone_numbers' in linux_result
    assert len(linux_result['phone_numbers']) >= 1

    analyzer.close()
