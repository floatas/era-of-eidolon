#!/usr/bin/env python3
"""The route, from the doorway table, and the creature curve laid along it.

    python3 tools/route.py                    Shirad's Forge

BALANCE.md step 1. Prints which doors are open at the start, the room order
that follows from them, and mean/max creature power (type 9 bytes 16-19) per
room in that order, so the two can be compared without a picture.
"""

import os
import statistics
import sys
from collections import defaultdict, deque

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "server"))
from world import World  # noqa: E402


def exit_entities(w):
    """(state id, from, to, dormant) for every kind 4 row."""
    later = w.armed_later()
    out = []
    for r in w.real1 or ():
        if len(r) > 14 and r[12] == 4:
            out.append((r[0], r[1], r[14], r[0] in later))
    return out


def main():
    game = sys.argv[1] if len(sys.argv) > 1 else "ShiradsForge"
    w = World(game)
    if not getattr(w, "real1", None):
        print(f"{game}: no recovered type 1 table, nothing to derive from")
        return 1

    doors = exit_entities(w)
    live = defaultdict(set)
    print("doors that start closed:")
    for sid, a, b, dormant in doors:
        if dormant:
            print(f"  {sid:>3}  {w.name(a)} -> {w.name(b)}")
        else:
            live[a].add(b)

    # BFS over the doors a new hero can use
    start = w.locations[0]
    hop, via = {start: 0}, {start: None}
    q = deque([start])
    while q:
        u = q.popleft()
        for v in sorted(live[u]):
            if v not in hop:
                hop[v], via[v] = hop[u] + 1, u
                q.append(v)

    power = defaultdict(list)
    for r in w.real9:
        if len(r) >= 20 and r[12] != 0:          # 0 is the people sheet
            power[r[1]].append(sum(r[16:20]))
    unfit = defaultdict(int)
    for r in w.real9:
        if len(r) < 20 and r[12] not in (0, w.npc_creature):
            unfit[r[1]] += 1

    print("\nhop  room              via               doors  n  unfit   mean  max  min")
    for loc in sorted(w.locations, key=lambda l: (hop.get(l, 99), l)):
        p = power.get(loc, [])
        f = lambda v: f"{v:5.0f}" if p else "    -"
        print(f"{hop.get(loc, '?'):>3}  {w.name(loc):<17} {w.name(via[loc]) if via.get(loc) else '-':<17}"
              f" {len(live[loc]):>3}  {len(p) + unfit[loc]:>2}  {unfit[loc]:>5}  "
              f"{f(statistics.mean(p) if p else 0)} {f(max(p) if p else 0)} {f(min(p) if p else 0)}")

    # does power climb with hop count?
    xs, ys = [], []
    for loc, p in power.items():
        if loc in hop:
            xs.append(hop[loc]); ys.append(statistics.mean(p))
    if len(xs) > 2:
        mx, my = statistics.mean(xs), statistics.mean(ys)
        cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** .5
        print(f"\ncorrelation of room mean power with hop count: {cov / den:+.2f} "
              f"over {len(xs)} rooms  (1 = the curve is depth, 0 = it is not)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
