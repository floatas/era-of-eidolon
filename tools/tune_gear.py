#!/usr/bin/env python3
"""Set Chapter I weapon effects so a sword, an axe or hammer, and a bow are
each worth carrying.

    python3 tools/tune_gear.py          rewrite notes/chapter-items.json
    python3 tools/tune_gear.py --dry    print, write nothing

Three lines, one choice. Every tier sells each of them, and at the tier's
reference ability (server/tiers.py) the top piece of every line deals the
tier's damage a turn. So the choice between them is never "which is
better", only "which is better here":

    sword    many small blows: safe footwork, no waste on light packs,
             and armour takes a bite out of every one
    heavy    few large blows: armour barely dents them, but a swing roots
             you in place and overkills the small fry
    bow      few large shots from range: armour barely dents them either,
             but not adjacent, not without a clear line, and whoever
             reaches you rings you

Within a line, the cheaper pieces of a tier reach 85% of the target and the
dearest 100%. Equal damage needs equal price, so the price is set the same
way: the top piece of every line in a tier costs the tier's price, the
cheaper ones down to 65% of it. watAgame's prices made the tier III sword
the cheapest top piece by 380 gold, and a sword hero held tier III's best
weapon two rooms before anyone else. Times and classes stay watAgame's.

A turn is 720. The reference hero spends 160 getting into place, and the
weapon's own time (capped at the client's 255) decides how many blows the
rest buys. A blow is the skill (Hit 10, Shoot 9) + effect + the ability's
share for that swing (tiers.potency_bonus), so the ability adds the same
over a turn to every line and the effect is what the line trades.

The starters, the Bloody Blade and the Short Bow, are set to the tier I
opening damage, 30 a turn at ability 3. The Short Bow was -5, which made a
new archer deal a third of what a new swordsman does.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "server"))
import tiers  # noqa: E402

ITEMS = ROOT / "notes" / "chapter-items.json"

# damage a turn for each tier's top piece, at that tier's reference ability
TOP = {"I": 46, "II": 100, "III": 180}
# Two big blows a creature waste half a blow on the last one, about a quarter
# of what a slow weapon deals; five small ones waste little. So the slow lines
# are paid for their overkill on paper, and come out even in play
# (tools/balance_sim.py measures it).
LINE = {"sword": 1.0, "heavy": 1.15, "bow": 1.15}
# what the top piece of each line costs in each tier; the cheapest is LOW_PRICE of it
PRICE = {"I": 240, "II": 460, "III": 760}
LOW_PRICE = 0.65
# what the starters deal at ability 3
STARTER = 30
STARTERS = ("Bloody Blade", "Short Bow")
LOW_SHARE = 0.85


def line(row):
    if row["class"] == "bow":
        return "bow"
    return "sword" if row["class"] == "sword" else "heavy"


def solve(target, time, stat, bow):
    t = min(tiers.MAX_SWING, time)
    swings = max(1, (tiers.TURN - tiers.WALK) // t)
    skill = 9 if bow else tiers.HIT
    return round(target / swings - skill - tiers.potency_bonus(stat, t))


def main():
    dry = "--dry" in sys.argv
    data = json.loads(ITEMS.read_text())
    weapons = [r for k in ("melee", "bow") for r in data[k] if r.get("chapter") == 1]
    for r in weapons:
        if r["name"] in STARTERS:
            r["effect"] = solve(STARTER, r["time"], 3, r["class"] == "bow")
    # The first step up in each line asks for nothing, so the first crate a
    # new hero smashes can hand him something he wears at once.
    for ln in ("sword", "heavy", "bow"):
        first = min((r for r in weapons if r.get("tier") == "I"
                     and line(r) == ln and r["name"] not in STARTERS),
                    key=lambda r: r["price"], default=None)
        if first:
            r_old = first["requirement"]
            first["requirement"] = 3
            if r_old != 3:
                print(f"{first['name']} now asks {first['ability']} 3 (was {r_old})")
    print(f"{'tier':5}{'line':7}{'weapon':14}{'time':>5}{'price':>6}{'share':>7}"
          f"{'effect':>8}{'a turn':>8}")
    for tier in tiers.ORDER:
        stat = tiers.REFERENCE[tier]["stat"]
        for ln in ("sword", "heavy", "bow"):
            group = sorted((r for r in weapons if r.get("tier") == tier
                            and line(r) == ln and r["name"] not in STARTERS),
                           key=lambda r: r["price"])
            for i, r in enumerate(group):
                step = 1.0 if len(group) == 1 else i / (len(group) - 1)
                share = LOW_SHARE + (1 - LOW_SHARE) * step
                r["effect"] = solve(TOP[tier] * LINE[ln] * share, r["time"],
                                    stat, r["class"] == "bow")
                r["price"] = round(PRICE[tier] * (LOW_PRICE + (1 - LOW_PRICE) * step))
                r["recycle"] = r["price"] * tiers.RECYCLE_PERCENT // 100
        for r in sorted((r for r in weapons if r.get("tier") == tier),
                        key=lambda r: (line(r), r["price"])):
            class It:
                pass
            it = It()
            it.time, it.effect, it.cls = r["time"], r["effect"], r["class"]
            got = tiers.weapon_round(it, stat if r["name"] not in STARTERS else 3)
            print(f"{tier:5}{line(r):7}{r['name']:14}{r['time']:>5}{r['price']:>6}"
                  f"{'':>7}{r['effect']:>8}{got:>8}")
        print()
    if dry:
        print("dry run, nothing written")
        return
    ITEMS.write_text(json.dumps(data, indent=1))
    print(f"wrote {ITEMS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
