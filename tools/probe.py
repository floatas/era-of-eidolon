#!/usr/bin/env python3
"""Answer a question about a location without rendering anything.

    python3 tools/probe.py ShiradsForge 16
    python3 tools/probe.py ShiradsForge          every location, one line each

Looking at a picture to find out what is in a room costs far more than
printing it. This prints it.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "server"))
from world import World  # noqa: E402

ARCH = 2


def door_kind(w, loc, x, y):
    t = w.map(loc).tile(x, y)
    if (t & 15) == w.marker:
        return "red tile"
    if ((t & 240) >> 4) == ARCH:
        return "arch"
    return "unmarked"


def one(w, loc):
    mp = w.map(loc)
    ground = sum(1 for t in mp.tiles if t & 15)
    print(f"{loc}  {w.name(loc)}   {mp.w}x{mp.h}, {ground}/{len(mp.tiles)} "
          f"tiles have ground")

    sx, sy = w.spawn_point(loc)
    fired = []
    for r in getattr(w, "real1", None) or ():
        if len(r) < 6 or r[1] not in (0, loc) or r[6] != 0 or r[4] == 0:
            continue
        if r[2] <= sx < r[4] and r[3] <= sy < r[5]:
            fired.append(f"state {r[0]} kind {r[12]}")
    print(f"  spawn ({sx},{sy})"
          + (f"   AUTO-FIRES {', '.join(fired)}" if fired else ""))

    doors = w.EXITS.get(loc, [])
    print(f"  doorways ({len(doors)})")
    for (x, y), dest in doors:
        back = [t for t, d in w.EXITS.get(dest, []) if d == loc]
        print(f"    ({x:>2},{y:>2}) {door_kind(w, loc, x, y):<9} -> {dest} "
              f"{w.name(dest)}{'' if back else '   ONE WAY'}")

    here = [m for m in w.mobs.values() if m.location == loc]
    named = {}
    for n in w.fights(loc):
        named.setdefault(w.creature_for(n), n)
    print(f"  creatures ({sum(1 for m in here if m.alive)} present, "
          f"{sum(1 for m in here if not m.alive)} held back)")
    for m in sorted(here, key=lambda m: m.node):
        void = "" if mp.tile(m.x, m.y) & 15 else "  ON VOID"
        state = "" if m.alive else "  held back"
        kind = "townsfolk" if m.npc else named.get(m.creature, hex(m.creature))
        print(f"    node {m.node:>3} ({m.x:>2},{m.y:>2}) {kind:<12} "
              f"hp {m.hp:<3}{state}{void}")

    cont = w.containers(loc)
    if cont:
        print(f"  containers ({len(cont)}): "
              + ", ".join(f"{k} at ({x},{y})" for x, y, k in cont[:8]))
    labels = [v for _, v in w.action_labels(loc)]
    if labels:
        print(f"  actions: {', '.join(labels)}")


def main():
    game = sys.argv[1] if len(sys.argv) > 1 else "ShiradsForge"
    w = World(game)
    real = " (watAgame's tables)" if getattr(w, "real1", None) else " (reconstructed)"
    if len(sys.argv) > 2:
        one(w, int(sys.argv[2]))
        return 0
    print(f"{game}{real}: {len(w.locations)} locations")
    for loc in w.locations:
        mp = w.map(loc)
        doors = w.EXITS.get(loc, [])
        here = [m for m in w.mobs.values() if m.location == loc]
        kinds = {door_kind(w, loc, x, y) for (x, y), _ in doors}
        print(f"  {loc:>2} {w.name(loc):<16} {mp.w:>2}x{mp.h:<2} "
              f"{len(doors)} doors ({'+'.join(sorted(kinds)) or '-'})  "
              f"{sum(1 for m in here if m.alive)} creatures  "
              f"{len(w.containers(loc))} crates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
