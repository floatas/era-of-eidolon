#!/usr/bin/env python3
"""Dump what the server actually computes, for the balance page to draw.

The page used to carry its own copy of the rules and drifted from the code
within a day. This asks the server instead: creature weights and swing times
come from Mob, patterns and threat counts from handlers, gear from the
chapter catalogue. Only the levers are recomputed in the page, using the same
formulas, and those are named where they appear.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
sys.path.insert(0, os.path.join(ROOT, "server"))

import handlers          # noqa: E402
from catalogue import catalogue   # noqa: E402
from world import POTENCY_DIV, World   # noqa: E402

from tiers import ROUTE   # noqa: E402  one route, kept in server/tiers.py
TIERS = [("I", 1, 4, [3]), ("II", 5, 11, [5, 8]), ("III", 12, 18, [12, 15])]
N8 = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]


def main():
    w = World("ShiradsForge")
    enemies = json.load(open(os.path.join(ROOT, "notes", "enemies-by-map.json")))

    # One row per fighter. The named ones share sprite sheets with the
    # townsfolk — Shirard is sheet 34 and Mira, Aldor and Mira's twin are all
    # sheet 0 — so the node is what tells them apart, not the art.
    seen, creatures = set(), []

    def row(m, name, pattern, note=None):
        covered = handlers.THREAT.get(pattern, 8)
        return {
            "name": name, "note": note,
            "weight": getattr(m, "weight", m.max_hp),
            "swing": m.offence()["swing"],
            "swings": max(1, handlers.TURN_BUDGET // m.offence()["swing"]),
            "pattern": pattern, "covered": covered, "safe": 8 - covered,
            "boss": name in handlers.BOSSES,
        }

    for m in sorted(w.mobs.values(), key=lambda x: x.node):
        named = handlers.fighter_name(w, m)
        name = named if named != "It" else (w.creature_name(m.creature)
                                            or f"sheet{m.creature}")
        # node 47 is Mira's twin, asleep for good now that the change of
        # shape happens on her own node. Nothing unnamed and dormant belongs
        # in a bestiary.
        if name in seen or (not m.alive and named == "It"
                            and not w.creature_name(m.creature)):
            continue
        seen.add(name)
        if name in handlers.BOSSES:
            # they do not die the first time: at nothing left they come back
            # with a full bar and a different shape (handlers._kill)
            m.phase = 1
            creatures.append(row(m, name, handlers.pattern_of(w, m),
                                 "first bar \u2014 " + handlers.BOSSES[name]))
            m.phase = 2
            creatures.append(row(m, name + " \u00b7 second bar",
                                 handlers.pattern_of(w, m),
                                 "after the change"))
            m.phase = 1
        else:
            creatures.append(row(m, name, handlers.pattern_of(w, m)))

    # the squares each shape threatens, as offsets, straight from _cells so
    # the drawing cannot disagree with the fight
    shapes = {}
    for pattern in sorted(handlers.THREAT):
        cells = handlers._cells(pattern, 0, 0, 1)   # facing east
        shapes[pattern] = [[x, y] for x, y in cells]

    kinds = {"melee": [], "bow": [], "armour": []}
    for it in catalogue().get("weapon") + catalogue().get("armour"):
        if not World.usable(it) or it.name in World.BAR_SKILLS:
            continue
        key = ("armour" if it.kind == "armour"
               else "bow" if it.cls == "bow" else "melee")
        if it.cls in ("sword", "axe", "hammer", "bow", None) or it.kind == "armour":
            kinds[key].append({
                "name": it.name, "cls": it.cls, "effect": it.effect,
                "time": it.time or 0, "price": it.price,
                "requirement": it.requirement, "ability": it.ability,
            })
    for v in kinds.values():
        v.sort(key=lambda i: (i["requirement"], i["price"]))

    rooms = []
    for i, loc in enumerate(ROUTE):
        m = enemies["map"][loc]
        rooms.append({
            "ord": i + 1, "loc": loc, "name": m["name"],
            "kills": sum(e["count"] for e in m["enemies"]),
            "gold": sum(e["gold"] * e["count"] for e in m["enemies"]),
            "xp": sum(e["experience"] * e["count"] for e in m["enemies"]),
            "foes": [{"name": e["name"], "count": e["count"],
                      "health": e["health"], "damage": e["damage"]}
                     for e in m["enemies"]],
            "shop": loc in (2, 3, 12, 5, 6),
        })

    out = {
        "route": rooms,
        "creatures": sorted(creatures, key=lambda c: c["weight"]),
        "items": kinds,
        "levels": enemies["levels"],
        "shapes": shapes,
        "tiers": [{"name": n, "from": a, "to": b, "shops": s}
                  for n, a, b, s in TIERS],
        "rules": {
            "turn": handlers.TURN_BUDGET,
            "move": handlers.MOVE_COST,
            "hitEffect": (catalogue().find("Hit").effect
                          if catalogue().find("Hit") else 10),
            "potencyDiv": POTENCY_DIV,
            "mistakes": handlers.balance()["mistakes"],
            "referenceSwings": handlers.REFERENCE_SWINGS,
            "startAbility": 3,
            "startLife": 40,
            "lifePerLevel": 6,
            "traders": [2, 3, 12, 5, 6],
        },
    }
    dest = sys.argv[1] if len(sys.argv) > 1 else "-"
    text = json.dumps(out, separators=(",", ":"))
    if dest == "-":
        print(text)
    else:
        open(dest, "w").write(text)
        print(f"{len(text)} bytes -> {dest}", file=sys.stderr)
        for k, v in kinds.items():
            print(f"  {k}: {len(v)}", file=sys.stderr)
        print(f"  creatures: {len(creatures)}  rooms: {len(rooms)}", file=sys.stderr)


if __name__ == "__main__":
    main()
