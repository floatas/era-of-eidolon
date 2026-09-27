#!/usr/bin/env python3
"""Choose which of watAgame's 58 items Chapter I actually sells.

The catalogue was written for the Arena, where a hero levels to 49 and
requirements run to 78. A chapter hero reaches ability 34, so two thirds of
the list is unreachable — the timelines in the lab showed 41 of 58 blocked on
ability and not one blocked on price.

So each chapter takes a slice. Chapter I gets a third of the melee (swords,
axes and hammers both, because their speeds differ and that is the choice),
half the bows and a third of the armour, with requirements respread across
the ability the hero actually covers. The rest is held for the sequels, which
is why the file tags all 58 rather than dropping any.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "notes" / "enemies-by-map.json"
OUT = ROOT / "notes" / "chapter-items.json"

# Chapter I, ordered weakest to strongest. Picked to alternate the fast line
# (sword, 96-126 time) against the slow one (axe and hammer, 195-240), so at
# every tier there is a real choice and not simply a better number.
CH1 = {
    "melee": ["Bloody Blade", "Corrupter", "Spike Axe", "Giant Sword",
              "Razor Axe", "Smasher", "Ghost Sword", "Bone Crusher",
              "Beheader Axe", "Doom Hammer"],
    "bow": ["Short Bow", "Medium Bow", "Long Bow", "Heavy Bow",
            "Bolt Bow", "Doombow"],
    "armour": ["Scrapsuit", "Snail Shell", "Iron Shell", "Doom Suit",
               "Trollskin", "Spike Suit"],
}
# The hero starts every ability at 15 and gains one a level, reaching 34 by
# the end of the route. Spread the picks over that, starting below 15 so the
# opening weapons are free of any gate.
LOW, HIGH = 3, 34


def spread(n):
    if n == 1:
        return [LOW]
    return [round(LOW + (HIGH - LOW) * i / (n - 1)) for i in range(n)]


def main():
    data = json.loads(SRC.read_text())
    out = {}
    for kind, items in data["items"].items():
        by_name = {i["name"]: i for i in items}
        chosen = CH1[kind]
        reqs = spread(len(chosen))
        rows = []
        for i, name in enumerate(chosen):
            it = dict(by_name[name])
            it["chapter"] = 1
            it["original_requirement"] = it["requirement"]
            it["requirement"] = reqs[i]
            rows.append(it)
        # everything else, split by watAgame's own requirement ladder
        rest = [i for i in items if i["name"] not in set(chosen)]
        rest.sort(key=lambda i: i["requirement"])
        half = len(rest) // 2
        for n, it in enumerate(rest):
            it = dict(it)
            it["chapter"] = 2 if n < half else 3
            it["original_requirement"] = it["requirement"]
            rows.append(it)
        out[kind] = rows
    OUT.write_text(json.dumps(out, indent=1))
    for kind, rows in out.items():
        ch1 = [r for r in rows if r["chapter"] == 1]
        print(f"{kind:<7} chapter I {len(ch1):>2} of {len(rows):<2} "
              f"effect {min(r['effect'] for r in ch1):>3} to "
              f"{max(r['effect'] for r in ch1):<3} "
              f"req {min(r['requirement'] for r in ch1)} to "
              f"{max(r['requirement'] for r in ch1)}")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
