#!/usr/bin/env bash
set -u

pid=790294
run="route3_all5_no_table_type_cached100_second_stage_2026_06_25_001533"

echo "--- child ps ---"
ps -p "$pid" -o pid,ppid,stat,etime,time,%cpu,%mem,cmd || true

echo "--- child fds count ---"
ls "/proc/${pid}/fd" 2>/dev/null | wc -l || true

echo "--- child tcp sockets ---"
ss -tpn 2>/dev/null | grep "$pid" || true

echo "--- recent segment files ---"
cd /home/chenyue/Wikidata_Framework_aws || exit 1
find "outputs/recipe_segments/${run}" -maxdepth 1 -type f -printf '%TY-%Tm-%Td %TH:%TM:%TS %s %p\n' 2>/dev/null | sort || true

echo "--- state stats ---"
python3 - <<'PY'
import json
from pathlib import Path
run = "route3_all5_no_table_type_cached100_second_stage_2026_06_25_001533"
path = Path("/home/chenyue/Wikidata_Framework_aws/outputs/recipe_segments") / run / "01_alltypes_100_state.json"
data = json.loads(path.read_text(encoding="utf-8"))
print(json.dumps(data.get("stats", {}), indent=2))
print("recent_events:")
for event in data.get("events", [])[-8:]:
    print(event)
PY
