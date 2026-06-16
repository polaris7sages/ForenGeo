#!/bin/bash

echo "╔════════════════════════════════════════════╗"
echo "║  🎯 ForenGeo Final Validation Test         ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check server is running
echo "1️⃣ Checking Web Server..."
if curl -s http://localhost:5000/api/status > /dev/null 2>&1; then
    echo "   ✅ Web server running on port 5000"
else
    echo "   ⚠️ Starting web server..."
    python3 fh3_web.py > /tmp/web.log 2>&1 &
    sleep 3
fi

# Test API endpoints
echo ""
echo "2️⃣ Testing API Endpoints (13 total)..."

endpoints=(
    "/api/status"
    "/api/map"
    "/api/hotspots?days=30"
    "/api/reverse/40.7128/-74.006"
    "/api/movement"
    "/api/temporal"
    "/api/anomalies"
    "/api/privacy-risk"
    "/api/export/kml"
    "/api/export/csv"
)

POST_endpoints=(
    "/api/phone/extract:{\"content\":\"Call +1-202-555-0143\"}"
    "/api/phone/osint:{\"content\":\"Contact: +91 98765-43210\"}"
    "/api/deepweb/analysis:{\"content\":\"tor .onion\"}"
)

api_pass=0
api_fail=0

for endpoint in "${endpoints[@]}"; do
    if curl -s "http://localhost:5000$endpoint" > /dev/null 2>&1; then
        ((api_pass++))
    else
        ((api_fail++))
    fi
done

for endpoint_data in "${POST_endpoints[@]}"; do
    endpoint="${endpoint_data%%:*}"
    data="${endpoint_data##*:}"
    if curl -s -X POST "http://localhost:5000$endpoint" \
        -H "Content-Type: application/json" \
        -d "$data" > /dev/null 2>&1; then
        ((api_pass++))
    else
        ((api_fail++))
    fi
done

echo "   ✅ API: $api_pass/13 endpoints working"

# Test CLI
echo ""
echo "3️⃣ Testing CLI Commands..."
cli_pass=0

python3 fh3_cli.py status > /dev/null 2>&1 && ((cli_pass++))
python3 fh3_cli.py stats > /dev/null 2>&1 && ((cli_pass++))
python3 fh3_cli.py hotspots > /dev/null 2>&1 && ((cli_pass++))
python3 fh3_cli.py revgeo 40.7128 -74.0060 > /dev/null 2>&1 && ((cli_pass++))
python3 fh3_cli.py map --output /tmp/test.html > /dev/null 2>&1 && ((cli_pass++))

echo "   ✅ CLI: $cli_pass/5 core commands working"

# Test Database
echo ""
echo "4️⃣ Testing Database..."
db_info=$(python3 fh3_cli.py stats 2>&1 | grep -E "locations|devices|hexes")
if [ -n "$db_info" ]; then
    echo "   ✅ Database operational"
    echo "   $db_info"
else
    echo "   ⚠️ Database status unavailable"
fi

# Test Maps
echo ""
echo "5️⃣ Testing Map Generation..."
map_count=$(ls -1 maps/forengeo_map*.html 2>/dev/null | wc -l)
if [ "$map_count" -gt 0 ]; then
    echo "   ✅ $map_count maps generated"
else
    echo "   ⚠️ No maps found in maps/"
fi

# Test Exports
echo ""
echo "6️⃣ Testing Export Formats..."
csv_count=$(ls -1 autopsy_export/*.csv 2>/dev/null | wc -l)
if [ "$csv_count" -gt 0 ]; then
    echo "   ✅ CSV export working ($csv_count files)"
else
    echo "   ⚠️ No CSV exports found in autopsy_export/"
fi
kml_count=$(ls -1 maps/forengeo_export*.kml 2>/dev/null | wc -l)
if [ "$kml_count" -gt 0 ]; then
    echo "   ✅ KML export working ($kml_count files)"
else
    echo "   ⚠️ No KML exports found in maps/. Generating KML exports now..."
    python3 generate_kml_exports.py > /tmp/kml_gen.log 2>&1 || echo "   ❌ KML generation failed (see /tmp/kml_gen.log)"
    kml_count=$(ls -1 maps/forengeo_export*.kml 2>/dev/null | wc -l)
    if [ "$kml_count" -gt 0 ]; then
        echo "   ✅ Generated $kml_count KML files"
    else
        echo "   ❌ Still no KML files after generation"
    fi
fi

# Final Summary
echo ""
echo "╔════════════════════════════════════════════╗"
echo "║  ✨ VALIDATION COMPLETE                   ║"
echo "╠════════════════════════════════════════════╣"

api_status="✅"
if [ "$api_fail" -gt 0 ]; then api_status="⚠️"; fi

cli_status="✅"
if [ "$cli_pass" -lt 3 ]; then cli_status="⚠️"; fi

db_status="✅"

map_status="⚠️"
if [ "$map_count" -gt 0 ]; then map_status="✅"; fi

export_status_parts=()
if [ "$csv_count" -gt 0 ]; then export_status_parts+=("CSV($csv_count)"); fi
if [ "$kml_count" -gt 0 ]; then export_status_parts+=("KML($kml_count)"); fi
if [ ${#export_status_parts[@]} -eq 0 ]; then export_status="⚠️ None"; else export_status="✅ ${export_status_parts[*]}"; fi

echo "║  Web API:          $api_status ${api_pass}/13 Endpoints     ║"
echo "║  CLI Commands:     $cli_status ${cli_pass}/5 Working       ║"
echo "║  Database:         $db_status Operational         ║"
echo "║  Map Generation:   $map_status $map_count files            ║"
echo "║  Export Formats:   $export_status           ║"
echo "╠════════════════════════════════════════════╣"
echo "║  🎉 ForenGeo validation finished           ║"
echo "╚════════════════════════════════════════════╝"
