#!/bin/sh
# The cheap loop: everything that can be known without the emulator or a
# picture. Under two seconds, a couple of dozen lines.
#
#   tools/check.sh
set -e
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"

python3 server/test_server.py | grep -E 'FAIL|passed|failed' || true
echo
for g in ShiradsForge SterlingLake MistralGrove; do
    python3 tools/probe.py "$g" | head -1
done
echo
python3 - <<'PY'
import os, sys
sys.path.insert(0, os.path.join(os.getcwd(), "server"))
from world import World
print("anomalies")
found = False
for g in ("ShiradsForge", "SterlingLake", "MistralGrove"):
    w = World(g)
    inbound = {l: 0 for l in w.locations}
    for links in w.EXITS.values():
        for _, d in links:
            inbound[d] += 1
    for l in w.locations:
        mp = w.map(l)
        bad = []
        if not inbound[l]:
            bad.append("no way in")
        if not w.EXITS.get(l):
            bad.append("no way out")
        oneway = [d for (x, y), d in w.EXITS.get(l, [])
                  if not any(dd == l for _, dd in w.EXITS.get(d, []))]
        if oneway:
            bad.append(f"one-way to {oneway}")
        void = [m.node for m in w.mobs.values()
                if m.location == l and m.alive and not (mp.tile(m.x, m.y) & 15)]
        if void:
            bad.append(f"creatures on void {void}")
        if bad:
            found = True
            print(f"  {g} {l} {w.name(l)}: {'; '.join(bad)}")
if not found:
    print("  none")
PY
