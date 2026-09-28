#!/usr/bin/env python3
"""Play Shirad's Forge start to finish through the real server code.

    python3 tools/autoplay.py                 the three builds, then the checks
    python3 tools/autoplay.py --build sword   one build, room by room
    python3 tools/autoplay.py --seeds 3       average over more runs
    python3 tools/autoplay.py --strict        exit 1 if a check fails

balance_sim.py plays a model of the fight. This plays the fight: every
encounter goes through the same calls the phone's Auto fight makes
(handlers.open_fight, handlers.resolve on handlers.hero_plan,
handlers.finish), so practice titles, boss phases,
Dodge-free auto play, level-ups, pay and trophies are the game's own. Crates
are smashed with World.loot_container, traders sold from with market_rows
and World.buy, spares broken with handlers.salvage, raises spent with
World.spend_raises. What the phone does on its own (walking, the quest
switches, waking the Crypt's waves and Shirard) is stood in for: the hero
walks the route in tiers.ROUTE order, and a sleeping creature is woken when
its room is reached.

Auto fight is the careless player: it walks up and swings, never Dodges,
never cures, never steps out of a shape. So the checks are about floors and
ceilings, not about what a careful player feels:

    no wall        careless play gets through ordinary encounters: few of
                   them lost three times running
    no pushover    in tiers II and III, few encounters end in one turn with
                   no life lost
    too early      a hero straight out of tier I (about level 4, tier I gear)
                   who walks into The Lair loses most of its fights
    the curve      a full clear ends near level 12

A lost encounter is retried, as a player would, up to three times from
where it began; after that it is left standing and the walk goes on.
"""

import argparse
import contextlib
import io
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "server"))
sys.path.insert(0, HERE)

import handlers                       # noqa: E402
import tiers                          # noqa: E402
from layout import QUEST_GIFTS        # noqa: E402
from world import World               # noqa: E402
from balance_sim import encounters    # noqa: E402

LINES = {"sword": ("sword",), "heavy": ("axe", "hammer"), "bow": ("bow",)}
ATTEMPTS = 3
MAX_TURNS = 40

CHECKS = {
    "wall": 0.20,        # at most this share of ordinary encounters beaten back
    "pushover": 0.40,    # at most this share of tier II/III wins free and quick
    "early": 0.50,       # at most this share of Lair fights won straight out of tier I
    "bosses": 0.50,      # remastered: at most this share of bosses won first try
    "boss_cost": 0.15,   # classic: a boss costs at least this share of life, on average
    "level": (10, 14),   # level at the end of a full clear
}


def quiet():
    """The handlers print a line per fight; keep them off the report."""
    return contextlib.redirect_stdout(io.StringIO())


class Autoplay:
    def __init__(self, build, seed=1, upgrade=True):
        self.build = build
        self.upgrade = upgrade
        self.rng = random.Random(seed)
        self.w = self.fresh()
        self.main = "Dexterity" if build == "bow" else "Strength"
        self.other = "Strength" if build == "bow" else "Dexterity"
        self.split = 0
        if build == "bow":
            self.w.equip("Short Bow")
        self.fights = []

    @staticmethod
    def fresh():
        w = World("ShiradsForge")
        with quiet():
            w.entity_table()
        return w

    # -- between fights ---------------------------------------------------

    def fits(self, it):
        if it.kind != "weapon":
            return True
        if it.cls in LINES[self.build]:
            return True
        own = any(self.w.item(n) and self.w.item(n).cls in LINES[self.build]
                  for n in self.w.inventory)
        return not own and self.build == "heavy" and it.cls == "sword"

    def spend(self):
        w = self.w
        counts = [0] * len(w.STATS)
        while w.raises - sum(counts) > 0:
            stat = self.other if self.split % 3 == 2 else self.main
            self.split += 1
            counts[w.STATS.index(stat)] += 1
        if any(counts):
            w.spend_raises(bytes(counts))

    def wear_best(self):
        if not self.upgrade:
            return
        w = self.w
        for kind, slot in (("weapon", "weapon"), ("armour", "armour")):
            held = w.item(w.equipped.get(slot))
            for name in list(w.inventory):
                it = w.item(name)
                if not it or it.kind != kind or not self.fits(it) or not w.can_wield(it):
                    continue
                if (held is None or not self.fits(held)
                        or handlers._gear_value(w, it) > handlers._gear_value(w, held)):
                    w.equip(it.name)
                    held = it

    def recycle(self):
        w = self.w
        worn = {w.equipped.get("weapon"), w.equipped.get("armour")}
        for name in list(w.inventory):
            it = w.item(name)
            if not it or name in worn or it.kind not in ("weapon", "armour"):
                continue
            if name in tiers.STARTERS and not self.upgrade:
                continue
            held = w.item(w.equipped.get("weapon" if it.kind == "weapon" else "armour"))
            later = (self.fits(it) and not w.can_wield(it) and held is not None
                     and w._gear_worth(it) > w._gear_worth(held))
            if not later:
                handlers.salvage(w, name)

    def shop(self, loc):
        if not self.upgrade:
            return
        w = self.w
        w.location = loc
        w.note_place(loc)
        self.recycle()
        for which in ((1, 2) if self.build == "bow" else (0, 2)):
            _, items = handlers.market_rows(w, which)
            slot = "armour" if which == 2 else "weapon"
            held = w.item(w.equipped.get(slot))
            best = None
            for it in items:
                if (it.name in w.inventory or not self.fits(it) or not w.can_wield(it)
                        or it.price > w.gold):
                    continue
                if held is not None and self.fits(held) and \
                        handlers._gear_value(w, it) <= handlers._gear_value(w, held):
                    continue
                if best is None or handlers._gear_value(w, it) > handlers._gear_value(w, best):
                    best = it
            if best and w.buy(best.name):
                w.equip(best.name)

    def crates(self, loc):
        w = self.w
        for st in sorted(w.prize_crates()):
            if w.crate_location(st) == loc:
                w.loot_container(st)
        self.wear_best()

    # -- a fight, as Auto fight plays it ------------------------------------

    def stand_near(self, group):
        """A square a few steps from the group, where the phone would have
        noticed them and opened the fight."""
        w = self.w
        cx, cy = group[0].x, group[0].y
        taken = {(m.x, m.y) for m in w.mobs.values() if m.location == w.location and m.alive}
        for r in (3, 2, 4, 5, 1):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if max(abs(dx), abs(dy)) != r:
                        continue
                    x, y = cx + dx, cy + dy
                    if (x, y) not in taken and w.can_stand(x, y):
                        return x, y
        return cx, cy

    def one_try(self, group):
        """Returns (result, turns, share of life lost)."""
        w = self.w
        for m in group:
            if getattr(m, "dormant", False) or not m.alive:
                m.alive, m.dormant = True, False
                m.hp = m.max_hp
        w.hero_x, w.hero_y = self.stand_near(group)
        w.hero_hp = w.hero_max
        with quiet():
            handlers.open_fight(w, [m.node for m in group])
            script, turns, low, idle = [], 0, w.hero_hp, 0
            for _ in range(MAX_TURNS):
                if w.hero_hp <= 0 or not w.fighters():
                    break
                before = (w.hero_hp, w.hero_x, w.hero_y,
                          tuple((m.node, m.hp, m.x, m.y) for m in w.fighters()))
                script.extend(handlers.resolve(w, handlers.hero_plan(w), self.rng))
                turns += 1
                low = min(low, w.hero_hp)
                after = (w.hero_hp, w.hero_x, w.hero_y,
                         tuple((m.node, m.hp, m.x, m.y) for m in w.fighters()))
                idle = idle + 1 if after == before else 0
                if idle >= 2:
                    break
            lost = 1 - max(0, low) / w.hero_max
            if w.hero_hp > 0 and not w.fighters():
                handlers.finish(w, script)
                return "won", turns, lost
            if w.hero_hp <= 0:
                return "lost", turns, lost
            handlers._flee(w, script)
            return "stalled", turns, lost

    def fight(self, group, loc):
        tier = tiers.tier_of(loc)
        boss = any(handlers.fighter_name(self.w, m) in handlers.BOSSES for m in group)
        nodes = [m.node for m in group]
        names = sorted({handlers.fighter_name(self.w, m) for m in group})
        for attempt in range(1, ATTEMPTS + 1):
            snap = self.w.to_dict()
            result, turns, lost = self.one_try([self.w.mobs[n] for n in nodes])
            if result == "won":
                break
            # a loss or a flee: back to where it began, as the phone's save would be
            w = self.fresh()
            with quiet():
                w.from_dict(snap)
            w.location = loc
            self.w = w
        self.fights.append(dict(
            room=self.w.name(loc), tier=tier, boss=boss, foes=names, size=len(nodes),
            result=result, attempts=attempt, turns=turns, lost=lost,
            level=self.w.level, stat=self.w.stats[self.main],
            weapon=self.w.weapon().name if self.w.weapon() else "-",
            titles={k: v[0] for k, v in self.w.practice.items() if v[0]}))
        self.spend()
        self.wear_best()

    def room(self, loc):
        w = self.w
        w.location = loc
        w.note_place(loc)
        if loc in handlers.TRADERS:
            self.shop(loc)
        self.crates(loc)
        foes = [m for m in w.mobs.values() if m.location == loc and not m.npc
                and (m.alive or getattr(m, "dormant", False)) and m.node != 47]
        for group in encounters(foes):
            self.fight(group, loc)
            self.w.location = loc
        for state, (gift_loc, _, _, _) in QUEST_GIFTS.items():
            if gift_loc == loc:
                self.w.claim_gift(state)
        if loc in handlers.TRADERS:
            self.shop(loc)

    def walk(self):
        for loc in tiers.ROUTE:
            self.room(loc)
        return self


def share(rows, pred):
    return sum(1 for r in rows if pred(r)) / len(rows) if rows else 0.0


def run_all(seeds):
    return {b: [Autoplay(b, seed=s).walk() for s in range(1, seeds + 1)] for b in LINES}


def report_build(runs):
    run = runs[0]
    print(f"{run.build}, seed 1, Auto fight throughout\n")
    print(f"{'room':16}{'t':>4}  {'foes':24}{'result':>9}{'try':>4}{'turns':>6}{'lost':>6}"
          f"{'lvl':>4}{run.main[:3]:>4}  {'weapon':13} titles")
    for f in run.fights:
        foes = ", ".join(f["foes"])[:23]
        titles = " ".join(f"{k}{v}" for k, v in f["titles"].items())
        print(f"{f['room']:16}{f['tier']:>4}  {foes:24}{f['result']:>9}{f['attempts']:>4}"
              f"{f['turns']:>6}{f['lost']:>6.0%}{f['level']:>4}{f['stat']:>4}  "
              f"{f['weapon']:13} {titles}")
    w = run.w
    print(f"\nend: level {w.level}, life {w.hero_max}, {w.gold}g, "
          f"trophies {len(w.trophies)}/{len(__import__('trophies').TROPHIES)}")


def checks(results, seeds):
    """Classic: Auto fight is simply how the game is fought, so bosses must
    cost real life rather than beat it; and a pure archer is our invention
    (every hero carries a sword and a bow), so the bow run is shown, not
    judged. Remastered: Auto fight is the careless player, and bosses should
    usually beat it."""
    misses = []
    classic = not tiers.remastered()
    print(f"\nAutoplay checks, {tiers.ruleset()} rules, {seeds} run(s) a build, "
          f"Auto fight throughout:\n")
    for build, runs in results.items():
        rows = [f for r in runs for f in r.fights]
        ordinary = [f for f in rows if not f["boss"]]
        # stalled: the auto-fighter could not reach them (the Crypt's later
        # waves stand on floor the phone paints in as the fight goes); that
        # says nothing about balance, so it is shown but not counted
        reached = [f for f in ordinary if f["result"] != "stalled"]
        stalled = len(ordinary) - len(reached)
        wall = share(reached, lambda f: f["result"] == "lost")
        deep = [f for f in rows if f["tier"] in ("II", "III") and f["result"] == "won"]
        push = share(deep, lambda f: f["turns"] <= 1 and f["lost"] == 0)
        end = statistics.mean(r.w.level for r in runs)
        bosses = [f for f in rows if f["boss"]]
        boss_first = share(bosses, lambda f: f["result"] == "won" and f["attempts"] == 1)
        ok_w = wall <= CHECKS["wall"]
        ok_p = push <= CHECKS["pushover"]
        ok_l = CHECKS["level"][0] <= end <= CHECKS["level"][1]
        boss_cost = statistics.mean(f["lost"] for f in bosses) if bosses else 0
        if classic:
            ok_b = boss_cost >= CHECKS["boss_cost"]
            if not ok_b:
                misses.append(f"{build}: bosses cost only {boss_cost:.0%} of life")
        else:
            ok_b = boss_first <= CHECKS["bosses"]
            if not ok_b:
                misses.append(f"{build}: Auto fight wins {boss_first:.0%} of bosses first try")
        info_only = classic and build == "bow"
        for ok, text in ((ok_w, f"{build}: {wall:.0%} of ordinary encounters beaten back"),
                         (ok_p, f"{build}: {push:.0%} of tier II/III wins free in one turn"),
                         (ok_l, f"{build}: ends at level {end:.1f}")):
            if not ok:
                misses.append(text)
        if info_only:
            misses = [m for m in misses if not m.startswith("bow:")]
        mark = (lambda ok: "") if info_only else (lambda ok: "" if ok else " !")
        print(f"  {build:6} beaten back {wall:>4.0%}{mark(ok_w)}   "
              f"free wins {push:>4.0%}{mark(ok_p)}   "
              f"bosses won first try {boss_first:>4.0%}, cost {boss_cost:>4.0%} of life"
              f"{mark(ok_b)}   "
              f"end level {end:>4.1f}{mark(ok_l)}   "
              f"({stalled} out of reach)" + ("   shown, not judged" if info_only else ""))
    # Straight from tier I into The Lair, the way a player can walk there:
    # every Lair creature fought one on one from the same starting point.
    wins = total = 0
    lost = []
    for seed in range(1, seeds + 1):
        early = Autoplay("sword", seed=seed)
        for loc in tiers.ROUTE[:tiers.STOPS["I"][1]]:
            early.room(loc)
        snap = early.w.to_dict()
        lair = [n for n, m in early.w.mobs.items() if m.location == 5 and not m.npc
                and not getattr(m, "dormant", False) and m.alive]
        for node in lair:
            w = Autoplay.fresh()
            with quiet():
                w.from_dict(snap)
            w.location = 5
            early.w = w
            result, _, share_lost = early.one_try([w.mobs[node]])
            total += 1
            wins += result == "won"
            lost.append(share_lost)
    won = wins / total if total else 0
    ok = won <= CHECKS["early"]
    if not ok:
        misses.append(f"straight out of tier I: wins {won:.0%} of Lair fights")
    print(f"\n  straight out of tier I (level {early.w.level}, "
          f"{early.w.weapon().name}) into The Lair: wins {won:.0%} of its fights"
          f"{'' if ok else ' !'}, losing {statistics.mean(lost):.0%} of life on average")
    print(f"\n{len(misses)} check(s) failed" + (":" if misses else ""))
    for m in misses:
        print(f"  - {m}")
    return misses


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--build", choices=tuple(LINES))
    ap.add_argument("--seeds", type=int, default=1)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--ruleset", choices=tiers.RULESETS,
                    help="play this ruleset instead of the one in balance.json")
    args = ap.parse_args()
    if args.ruleset:
        tiers.RULESET_OVERRIDE = args.ruleset
    if args.build:
        report_build([Autoplay(args.build, seed=s).walk() for s in range(1, args.seeds + 1)])
        return 0
    misses = checks(run_all(args.seeds), args.seeds)
    return 1 if (args.strict and misses) else 0


if __name__ == "__main__":
    sys.exit(main())
