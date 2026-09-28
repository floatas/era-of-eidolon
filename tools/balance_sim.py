#!/usr/bin/env python3
"""Play Shirad's Forge end to end on the server's own combat maths, and say
whether the result meets the balance targets.

    python3 tools/balance_sim.py                 the three builds, room by room
    python3 tools/balance_sim.py --build sword   one build in full: sword, heavy, bow
    python3 tools/balance_sim.py --trials 400    steadier averages
    python3 tools/balance_sim.py --strict        exit 1 if a target is missed

Three builds, one per line of weapon (tools/tune_gear.py): a Strength hero
who only buys swords, one who only buys axes and hammers, and a Dexterity
hero who only buys bows. Each is meant to be the quickest somewhere and
never stuck anywhere.

This replaces fightplan.py, which modelled a fight the server no longer has.
Everything that decides a number is imported, not copied: World.strike,
Mob.offence and spoil, handlers._pressure_blow, swing_cost, _gear_value,
_tune_bosses' sizing, market_rows, balance(), World.grant_xp and
loot_container, and the tier model in server/tiers.py. Change the game and
this follows.

The walk. Rooms in tiers.ROUTE order. Every fight is one creature, as in
the game: however close its neighbours stand, the hero engages one at a time. Dormant creatures
count, because each is a fight the player meets. Every crate is smashed on
arrival. At a trader the hero buys the best weapon, then the best suit, his
purse and stat allow, and wears the best he carries. Two of every three
raise points go to Strength (Dexterity for the bow), the third to the other.

A fight. The hero spends 160 of each 720-unit turn walking and the rest
swinging at the nearest creature. Damage taken is given three ways, because
where the hero stands decides it and nothing here plays that part:

    mistake  one turn in one creature's shape, for the hero as he is: the
             price of a wrong square
    duel     an encounter fought one creature at a time without ever
             stepping out of a shape
    brawl    an encounter all at once, every creature swinging every chance

    careful  footwork, approximated: a blow is safe from its target when
             stepping in, swinging and stepping out (the swing + 80)
             fits between two of the target's swings; otherwise each of
             the target's swings in that window lands. An archer's first
             shot at each creature is free, while it walks in. The rest of
             the encounter is assumed kept out of their shapes.

Not modelled: Dodge, Minor Cure, respawns, practice titles, crowding.

The tier check. For each room, an encounter is also timed with the tier's
reference hero holding the tier's best weapon and then the one the tier
opens with. The design says the first is one to three turns and the second
one to two turns more: gear decides how long, footwork decides whether.
"""

import argparse
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "server"))

import handlers                       # noqa: E402
import tiers                          # noqa: E402
from catalogue import catalogue       # noqa: E402
from world import World               # noqa: E402

TURN = handlers.TURN_BUDGET
WALK = tiers.WALK
REACH = 4

TARGETS = {
    # turns per encounter with the tier's best weapon, reference hero
    "best_turns": (0.8, 3.5),
    # how much longer the tier's opening weapon takes, as a multiple
    "entry_ratio": (1.25, 2.2),
    # a boss, both phases, with the hero's own gear
    "boss_turns": (3.0, 7.0),
    # in a room, the slowest build against the quickest
    "build_spread": (1.0, 1.8),
    # rooms in which each build is the quickest
    "build_wins": 3,
    # share of the reference life one turn in the worst shape costs
    "mistake": (0.25, 0.45),
    # level at the end of a full clear
    "end_level": (10, 14),
    # a tier's gold (kills, crates and recycling) against its top weapon in
    # the build's line plus its top suit; the last tier may run richer, as
    # there is nothing after it to buy ahead into
    "tier_gold": (1.0, 1.9),
}
TIER_SLACK = 0.35


def encounters(foes):
    """One creature to a fight. The game engages a single creature at a time,
    however close its neighbours stand; the first version of this chained
    everything within reach into one fight, and made archers look hopeless
    against "packs" that the game never fields."""
    return [[m] for m in sorted(foes, key=lambda m: m.node)]


class Run:
    LINES = {"sword": ("sword",), "heavy": ("axe", "hammer"), "bow": ("bow",)}

    def __init__(self, build, trials, seed=7, other=None):
        self.w = World("ShiradsForge")
        self.build = build
        self.trials = trials
        self.rng = random.Random(seed)
        self.main = "Dexterity" if build == "bow" else "Strength"
        self.other = other or ("Strength" if build == "bow" else "Dexterity")
        self.label = "Shoot" if build == "bow" else "Hit"
        self.split = 0
        if build == "bow":
            self.w.equip("Short Bow")
        self.rows = []
        self.shops = []
        self.bosses = []
        self.loot = []
        self.ledger = {t: dict(kills=0, crates=0, recycled=0, quests=0, spent=0,
                               found=[], bought=[], sold=[])
                       for t in tiers.ORDER}

    # -- the hero between fights -------------------------------------------

    def spend(self):
        w = self.w
        while w.raises > 0:
            stat = self.other if self.split % 3 == 2 else self.main
            self.split += 1
            w.stats[stat] += w.raise_cost(stat)
            w.raises -= 1

    def fits(self, it):
        """His own line; until he owns one of it, any blade he is handed
        (a heavy hero takes the Corrupter from the Village crate rather
        than keep swinging the Bloody Blade)."""
        if it.kind != "weapon":
            return True
        if it.cls in self.LINES[self.build]:
            return True
        own = any(self.w.item(n) and self.w.item(n).cls in self.LINES[self.build]
                  for n in self.w.inventory)
        return (not own and self.build == "heavy"
                and it.cls in ("sword", "axe", "hammer"))

    def wear_best(self):
        w = self.w
        for kind, slot in (("weapon", "weapon"), ("armour", "armour")):
            held = w.item(w.equipped.get(slot))
            for name in w.inventory:
                it = w.item(name)
                if not it or it.kind != kind or not self.fits(it) or not w.can_wield(it):
                    continue
                if (held is None or not self.fits(held)
                        or handlers._gear_value(w, it) > handlers._gear_value(w, held)):
                    w.equip(it.name)
                    held = it

    def recycle(self, tier):
        """Break everything he carries and will not use: not worn, and not a
        piece of his own line (or a suit) better than what he wears that he
        is still growing into. tiers.RECYCLE_PERCENT back, as the phone says."""
        w = self.w
        worn = {w.equipped.get("weapon"), w.equipped.get("armour")}
        for name in list(w.inventory):
            it = w.item(name)
            if not it or name in worn or it.kind not in ("weapon", "armour"):
                continue
            held = w.item(w.equipped.get("weapon" if it.kind == "weapon" else "armour"))
            later = (self.fits(it) and not w.can_wield(it) and held is not None
                     and w._gear_worth(it) > w._gear_worth(held))
            if later:
                continue
            gone, refund = handlers.salvage(w, name)
            if gone:
                self.ledger[tier]["recycled"] += refund
                self.ledger[tier]["sold"].append(gone)

    def shop(self, loc):
        w = self.w
        w.location = loc
        w.note_place(loc)
        tier = handlers.TRADER_TIERS[handlers.TRADERS.index(loc)]
        self.recycle(tier)
        arrived = dict(gold=w.gold, stat=w.stats[self.main], level=w.level,
                       tier=tier, name=w.name(loc), bought=[], cheapest=None)
        for which in ((1, 2) if self.build == "bow" else (0, 2)):
            _, items = handlers.market_rows(w, which)
            slot = "armour" if which == 2 else "weapon"
            held = w.item(w.equipped.get(slot))
            better = [it for it in items if it.name not in w.inventory
                      and self.fits(it)
                      and (held is None or not self.fits(held)
                           or handlers._gear_value(w, it)
                           > handlers._gear_value(w, held))]
            reachable = [it for it in better if w.can_wield(it)]
            if reachable:
                low = min(it.price for it in reachable)
                arrived["cheapest"] = min(low, arrived["cheapest"] or low)
            best = None
            for it in reachable:
                if it.price > w.gold:
                    continue
                if best is None or handlers._gear_value(w, it) > handlers._gear_value(w, best):
                    best = it
            if best:
                w.gold -= best.price
                w.inventory.append(best.name)
                w.equip(best.name)
                arrived["bought"].append(best.name)
                self.ledger[tier]["spent"] += best.price
                self.ledger[tier]["bought"].append(best.name)
        self.shops.append(arrived)

    def crates(self, loc):
        """Smash every prize crate in the room, the way the server knows them:
        crate_payoffs() after entity_table() has armed the silent ones, plus
        the labelled kind-3 crates. Logs what each held."""
        w = self.w
        if not hasattr(w, "_extra_crate_locs"):
            w.entity_table()
        states = set(w.crate_payoffs())
        for r in w.real1 or ():
            if len(r) > 12 and r[12] == 3 and "crate" in w.entity_label(r[0]).lower():
                states.add(r[0])
        got = 0
        for st in sorted(states):
            if w.crate_location(st) != loc:
                continue
            found, gold = w.loot_container(st)
            got += gold
            self.loot.append((w.name(loc), st, [it.name for it in found], gold))
            led = self.ledger[tiers.tier_of(loc)]
            led["crates"] += gold
            led["found"] += [it.name for it in found]
        self.wear_best()
        return got

    # -- one fight -----------------------------------------------------------

    def hero_swing(self, w, target, weapon=None):
        label = "Shoot" if (weapon or w.weapon()).cls == "bow" else "Hit"
        it = catalogue().find(label)
        wpn = weapon or w.weapon()
        off = target.offence()
        potency = w.stats["Dexterity" if label == "Shoot" else "Strength"]
        return w.strike(w.trained_effect(label, it.effect), it.precision,
                        potency, off["avoid"], dex=w.stats["Dexterity"],
                        armour=off["armour"], weapon_mod=wpn.effect,
                        rng=self.rng)[1]

    def mob_swing(self, w, m):
        arm = w.armour().effect if w.armour() else 0
        return w.strike(handlers._pressure_blow(w, m), m.offence()["precision"],
                        0, w.avoidance(), armour=arm, rng=self.rng)[1]

    def mistake(self, w, m):
        """Expected life lost for one turn in this creature's shape."""
        swings = max(1, TURN // m.offence()["swing"])
        n = 600
        return swings * sum(self.mob_swing(w, m) for _ in range(n)) / n

    def exposed(self, target, swing_t, bow, first, move=None):
        """How many of the target's swings land during one careful blow."""
        if bow and first:
            return 0
        window = swing_t + 2 * (move or handlers.MOVE_COST)
        interval = target.offence()["swing"]
        return 0 if window < interval else window // interval

    def clear(self, w, foes, hp, weapon=None):
        """One encounter to the end: (turns, duel, brawl, careful damage)."""
        wpn = weapon or w.weapon()
        bow = bool(wpn and wpn.cls == "bow")
        # what the bar charges this hero, practice and Speed included
        label = "Shoot" if bow else "Hit"
        raw = min(handlers.MAX_COST, wpn.time) if wpn and wpn.time else 60
        swing_t = w.trained_time(label, raw)
        move = w.trained_time("Move", handlers.MOVE_COST)
        walk = 4 * move
        per_turn = max(1, (TURN - walk) // swing_t)
        left = dict(hp)
        order = list(foes)
        died = {}
        turns = 0
        careful = 0.0
        shot_at = set()
        while order and turns < 40:
            for k in range(per_turn):
                if not order:
                    break
                target = order[0]
                for _ in range(self.exposed(target, swing_t, bow,
                                            target.node not in shot_at, move)):
                    careful += self.mob_swing(w, target)
                shot_at.add(target.node)
                left[target.node] -= self.hero_swing(w, target, wpn)
                if left[target.node] <= 0:
                    died[target.node] = turns * TURN + walk + (k + 1) * swing_t
                    order.pop(0)
            turns += 1
        end = turns * TURN
        duel = brawl = 0.0
        start = 0.0
        for m in foes:
            gone = died.get(m.node, end)
            brawl += sum(self.mob_swing(w, m)
                         for _ in range(int(gone // m.offence()["swing"])))
            duel += sum(self.mob_swing(w, m)
                        for _ in range(max(0, int((gone - start) // m.offence()["swing"]))))
            start = gone
        last = max(died.values()) if len(died) == len(foes) else end
        return last / TURN, duel, brawl, careful

    def timed(self, w, group, hp, weapon=None):
        runs = [self.clear(w, group, hp, weapon) for _ in range(self.trials)]
        return tuple(statistics.mean(r[i] for r in runs) for i in range(4))

    def reference(self, tier):
        """A fresh World holding the tier's reference hero."""
        ref = tiers.REFERENCE[tier]
        r = World("ShiradsForge")
        r.level = ref["level"]
        r.hero_max = r.hero_hp = ref["life"]
        r.stats["Strength"] = ref["stat"]
        r.inventory.append(ref["suit"])
        r.equip(ref["suit"])
        return r

    def tier_weapons(self, tier):
        stat = tiers.REFERENCE[tier]["stat"]
        best = max(tiers._melee(tier), key=lambda i: tiers.weapon_round(i, stat))
        prev = tiers.before(tier)
        pool = tiers._melee(prev) if prev else [catalogue().find("Bloody Blade")]
        entry = max(pool, key=lambda i: tiers.weapon_round(i, stat))
        return best, entry

    # -- the walk ------------------------------------------------------------

    def room(self, loc):
        w = self.w
        w.location = loc
        crate_gold = self.crates(loc)
        foes = [m for m in w.mobs.values() if m.location == loc and not m.npc
                and (m.alive or getattr(m, "dormant", False))]
        if not foes:
            w.gold += crate_gold
            return
        tier = tiers.tier_of(loc)
        for m in foes:
            if handlers.fighter_name(w, m) in handlers.BOSSES:
                m.boss = True
                m.max_hp = m.hp = tiers.boss_life(tier, handlers.balance()["boss_turns"])
        hp = {m.node: m.max_hp * (2 if getattr(m, "boss", False) else 1) for m in foes}
        groups = encounters(foes)
        own = [self.timed(w, g, {m.node: hp[m.node] for m in g}) for g in groups]
        ref = self.reference(tier)
        best, entry = self.tier_weapons(tier)
        with_best = [self.timed(ref, g, {m.node: hp[m.node] for m in g}, best)[0]
                     for g in groups if not any(getattr(m, "boss", False) for m in g)]
        with_entry = [self.timed(ref, g, {m.node: hp[m.node] for m in g}, entry)[0]
                      for g in groups if not any(getattr(m, "boss", False) for m in g)]
        worst = max(foes, key=lambda m: self.mistake(ref, m))
        pay = handlers.balance()["pay"]
        xp = gold = 0
        for m in foes:
            g, x = m.spoil()
            xp += max(1, x * pay // 100)
            gold += max(1, g * pay // 100)
        for g, t in zip(groups, own):
            for m in g:
                if getattr(m, "boss", False):
                    self.bosses.append((handlers.fighter_name(w, m), w.name(loc), t[0]))
        names = {}
        for m in foes:
            n = handlers.fighter_name(w, m)
            names[n] = names.get(n, 0) + 1
        self.rows.append(dict(
            room=w.name(loc), tier=tier, n=len(foes), enc=len(groups),
            biggest=max(len(g) for g in groups), level=w.level,
            stat=w.stats[self.main], hero=w.hero_max,
            weapon=w.weapon().name if w.weapon() else "-",
            armour=w.armour().name if w.armour() else "-",
            turns=statistics.mean(t[0] for t in own),
            best=statistics.mean(with_best) if with_best else None,
            entry=statistics.mean(with_entry) if with_entry else None,
            ref_mistake=self.mistake(ref, worst) / ref.hero_max,
            mistake=self.mistake(w, worst) / w.hero_max,
            worst=handlers.fighter_name(w, worst),
            duel=max(t[1] for t in own) / w.hero_max,
            brawl=max(t[2] for t in own) / w.hero_max,
            careful=sum(t[3] for t in own) / w.hero_max,
            xp=xp, gold=gold + crate_gold,
            foes=", ".join(f"{k} x{v}" if v > 1 else k for k, v in names.items())))
        w.grant_xp(xp)
        w.gold += gold + crate_gold
        self.ledger[tier]["kills"] += gold
        # an optional quest's reward, paid in the room where it is handed in
        from layout import QUEST_GIFTS
        for state, (gift_loc, _, _, _) in QUEST_GIFTS.items():
            if gift_loc == loc:
                self.ledger[tier]["quests"] += w.claim_gift(state)
        self.spend()
        self.wear_best()

    def walk(self):
        """A trader's room is shopped on arrival and again once cleared,
        since the player is standing next to the counter with the spoils."""
        for loc in tiers.ROUTE:
            if loc in handlers.TRADERS:
                self.shop(loc)
            self.room(loc)
            if loc in handlers.TRADERS:
                self.shop(loc)
        return self


def within(v, rng):
    return v is not None and rng[0] <= v <= rng[1]


def pct(v):
    return f"{v:.0%}"


def report(run):
    w = run.w
    misses = []
    print(f"Shirad's Forge, {run.build} build, {run.trials} trials an encounter, "
          f"balance {handlers.balance()}\n")
    print(f"{'room':16}{'t':>4}{'foes':>5}{'enc':>4}{'lvl':>4}{run.main[:3]:>4}{'hp':>4}"
          f"  {'weapon':13}{'armour':12}{'turns':>6}{'best':>6}{'entry':>6}"
          f"{'mistake':>9}{'duel':>6}{'brawl':>6}{'xp':>5}{'gold':>5}")
    for r in run.rows:
        b_ok = r["best"] is None or within(r["best"], TARGETS["best_turns"])
        ratio = r["entry"] / r["best"] if r["entry"] else None
        e_ok = r["entry"] is None or within(ratio, TARGETS["entry_ratio"])
        m_ok = within(r["ref_mistake"], TARGETS["mistake"])
        if not b_ok:
            misses.append(f"{r['room']}: {r['best']:.1f} turns an encounter with the "
                          f"tier's best weapon, target {TARGETS['best_turns']}")
        if not e_ok:
            misses.append(f"{r['room']}: the tier's opening weapon takes "
                          f"{ratio:.2f}x as long ({r['entry'] - r['best']:+.1f} turns), "
                          f"target {TARGETS['entry_ratio'][0]}-{TARGETS['entry_ratio'][1]}x")
        if not m_ok:
            misses.append(f"{r['room']}: a turn in the {r['worst']}'s shape costs the "
                          f"reference hero {pct(r['ref_mistake'])} of life")
        best = "-" if r["best"] is None else f"{r['best']:.1f}"
        entry = "-" if r["entry"] is None else f"{r['entry']:.1f}"
        print(f"{r['room']:16}{r['tier']:>4}{r['n']:>5}{r['enc']:>4}{r['level']:>4}"
              f"{r['stat']:>4}{r['hero']:>4}  {r['weapon']:13}{r['armour']:12}"
              f"{r['turns']:>6.1f}{best:>5}{'' if b_ok else '!':1}{entry:>5}{'' if e_ok else '!':1}"
              f"{pct(r['ref_mistake']):>5}{'' if m_ok else '!':1}{pct(r['mistake']):>4}"
              f"{pct(r['duel']):>6}{pct(r['brawl']):>6}{r['xp']:>5}{r['gold']:>5}")
    print("""
  turns        mean turns an encounter, the hero as he is
  best, entry  the same with the tier's reference hero and its best weapon,
               then the weapon the tier opens with
  mistake      one turn in the worst shape here: reference hero, then the
               hero as he is, as a share of life
  duel, brawl  the worst encounter fought toe to toe, one at a time / at once
  !            outside the target
""")
    print("bosses, both phases, the hero's own gear:")
    for name, room, t in run.bosses:
        ok = within(t, TARGETS["boss_turns"])
        if not ok:
            misses.append(f"{name}: {t:.1f} turns, target {TARGETS['boss_turns']}")
        print(f"  {name:10} {room:16} {t:4.1f} turns{'' if ok else ' !'}")

    print("\ncrates, in the order smashed (tiers.CRATES):")
    for room, st, items, gold in run.loot:
        print(f"  {room:16} {st:>3}  {tiers.crate_role(st):7}"
              f"{', '.join(items) or '(purse)':14} +{gold}g")

    print("\neach tier's ledger:")
    for t, led in run.ledger.items():
        top_w = max((it.price for it in catalogue().get("weapon")
                     if it.tier == t and run.fits(it) and it.cls in Run.LINES[run.build]),
                    default=0)
        top_s = max((it.price for it in catalogue().get("armour") if it.tier == t),
                    default=0)
        earned = led["kills"] + led["crates"] + led["recycled"]
        ratio = earned / max(1, top_w + top_s)
        ok = within(ratio, TARGETS["tier_gold"])
        if not ok:
            misses.append(f"tier {t}: {earned}g earned is {ratio:.2f}x its top "
                          f"weapon and suit ({top_w + top_s}g)")
        quest = (f" + optional quests {led['quests']}"
                 f" = {(earned + led['quests']) / max(1, top_w + top_s):.2f}x"
                 if led["quests"] else "")
        print(f"  tier {t:4} gold in {earned:>5} (kills {led['kills']}, crates "
              f"{led['crates']}, recycled {led['recycled']}) = {ratio:.2f}x top gear"
              f"{'' if ok else ' !'}{quest}, spent {led['spent']:>5}\n"
              f"             found {', '.join(led['found']) or '-'}\n"
              f"             bought {', '.join(led['bought']) or '-'}; "
              f"recycled {', '.join(led['sold']) or '-'}")

    print("\ntraders, on arrival:")
    seen = set()
    for s in run.shops:
        want = tiers.REFERENCE[s["tier"]]["stat"]
        first = s["tier"] not in seen
        seen.add(s["tier"])
        note = ""
        if first and want > 3:
            lo, hi = want * (1 - TIER_SLACK), want * (1 + TIER_SLACK)
            if not lo <= s["stat"] <= hi:
                note = f"  ! tier expects {run.main} {want}"
                misses.append(f"{s['name']}: arrives with {run.main} {s['stat']}, "
                              f"tier {s['tier']} expects {want}")
        afford = ("nothing better he can wield" if s["cheapest"] is None
                  else f"cheapest upgrade {s['cheapest']}g")
        if s["cheapest"] is not None and s["cheapest"] > s["gold"]:
            misses.append(f"{s['name']}: {s['gold']}g on arrival, {afford}")
            afford += " !"
        print(f"  {s['name']:14} tier {s['tier']:4} level {s['level']:>2}  "
              f"{run.main} {s['stat']:>3}  {s['gold']:>5}g  {afford}; "
              f"bought {', '.join(s['bought']) or 'nothing'}{note}")

    lvl_ok = within(w.level, TARGETS["end_level"])
    if not lvl_ok:
        misses.append(f"ends at level {w.level}, target {TARGETS['end_level']}")
    print(f"\nend: level {w.level}{'' if lvl_ok else ' !'}, {run.main} "
          f"{w.stats[run.main]}, life {w.hero_max}, {w.gold}g unspent")
    print(f"\n{len(misses)} target(s) missed" + (":" if misses else ""))
    for m in misses:
        print(f"  - {m}")
    return misses


def compare(trials):
    """The three builds side by side: turns an encounter and careful damage
    for a whole room, as a share of life, each with its own gear and level."""
    runs = {b: Run(b, trials).walk() for b in Run.LINES}
    misses = []
    wins = {b: 0 for b in runs}
    print(f"Shirad's Forge, three builds, {trials} trials an encounter, "
          f"balance {handlers.balance()}\n")
    print(f"{'room':16}{'t':>4}  " + "".join(f"{b:>16}" for b in runs)
          + "   quickest   spread")
    print(f"{'':20}" + "".join(f"{'turns careful':>16}" for _ in runs))
    for i, row in enumerate(runs["sword"].rows):
        cells = {b: runs[b].rows[i] for b in runs}
        quick = min(cells, key=lambda b: cells[b]["turns"])
        spread = max(c["turns"] for c in cells.values()) / max(0.1, cells[quick]["turns"])
        near = [b for b in cells if cells[b]["turns"] <= cells[quick]["turns"] * 1.05]
        for b in near:
            wins[b] += 1
        ok = within(spread, TARGETS["build_spread"])
        if not ok:
            slow = max(cells, key=lambda b: cells[b]["turns"])
            misses.append(f"{row['room']}: {slow} takes {spread:.2f}x as long as {quick}")
        print(f"{row['room']:16}{row['tier']:>4}  "
              + "".join(f"{cells[b]['turns']:>9.1f}{pct(cells[b]['careful']):>7}"
                        for b in runs)
              + f"   {'/'.join(near):9}{spread:>6.2f}{'' if ok else '!'}")
    print("\n  turns: mean turns an encounter. careful: life lost over the room with")
    print("  the footwork each weapon allows (see the top of this file). Quickest")
    print("  counts every build within 5% of the best.\n")
    for b, run in runs.items():
        n = wins[b]
        ok = n >= TARGETS["build_wins"]
        if not ok:
            misses.append(f"{b} is the quickest in only {n} room(s)")
        bosses = ", ".join(f"{name} {t:.1f}" for name, _, t in run.bosses)
        print(f"  {b:6} quickest in {n:>2} rooms{'' if ok else ' !'}; ends level "
              f"{run.w.level}, {run.main} {run.w.stats[run.main]}, "
              f"{run.w.gold}g spare; bosses {bosses}")
    print(f"\n{len(misses)} target(s) missed" + (":" if misses else ""))
    for m in misses:
        print(f"  - {m}")
    return misses


def variants(trials):
    """Each weapon line with its third raise point in Dexterity (or Strength
    for the bow), Toughness or Speed. A variant should be a real choice: none
    more than 15% slower than the quickest of its line, except Toughness,
    which trades up to 20% of its tempo for at least 20% more survivable
    mistakes; and Speed clearly quicker than the base."""
    misses = []
    print(f"Raise variants: two points of three to the main ability, the "
          f"third as named. {trials} trials an encounter.\n")
    print(f"{'line':7}{'third point':13}{'turns':>7}{'careful':>9}{'mistakes':>10}"
          f"{'life':>6}{'Spd':>5}{'spare':>7}   bosses")
    for line in Run.LINES:
        base = "Strength" if line == "bow" else "Dexterity"
        rows = {}
        for other in (base, "Toughness", "Speed"):
            run = Run(line, trials, other=other).walk()
            turns = statistics.mean(r["turns"] for r in run.rows)
            careful = sum(r["careful"] for r in run.rows)
            # how many turns in the worst shape he survives, averaged over rooms
            falls = statistics.mean(1 / max(0.01, r["mistake"]) for r in run.rows)
            rows[other] = (turns, careful, falls, run)
        quickest = min(v[0] for v in rows.values())
        for other, (turns, careful, falls, run) in rows.items():
            slow = turns / quickest
            ok = slow <= (1.20 if other == "Toughness" else 1.15)
            if not ok:
                misses.append(f"{line} with {other}: {slow:.2f}x the quickest turns")
            bosses = ", ".join(f"{n} {t:.1f}" for n, _, t in run.bosses)
            print(f"{line:7}{other:13}{turns:>7.2f}{careful:>8.0%}{'' if ok else '!':1}"
                  f"{falls:>9.1f}{run.w.hero_max:>7}{run.w.stats['Speed']:>5}"
                  f"{run.w.gold:>7}   {bosses}")
        base_falls = rows[base][2]
        if rows["Toughness"][2] < 1.2 * base_falls:
            misses.append(f"{line}: Toughness survives only "
                          f"{rows['Toughness'][2] / base_falls:.2f}x the mistakes")
        if rows["Speed"][0] > 0.97 * rows[base][0]:
            misses.append(f"{line}: Speed is not quicker than {base}")
        print()
    print("  turns: mean turns an encounter over the chapter. careful: life lost,")
    print("  summed over rooms, with the footwork each weapon allows. mistakes: turns")
    print("  in the worst shape he survives from full life, averaged over rooms.")
    print(f"\n{len(misses)} target(s) missed" + (":" if misses else ""))
    for m in misses:
        print(f"  - {m}")
    return misses


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--build", choices=("sword", "heavy", "bow", "blade"))
    ap.add_argument("--trials", type=int, default=120)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--variants", action="store_true",
                    help="each line with its third point in Dex/Str, Toughness or Speed")
    args = ap.parse_args()
    if args.variants:
        misses = variants(args.trials)
    elif args.build:
        build = "sword" if args.build == "blade" else args.build
        misses = report(Run(build, args.trials).walk())
    else:
        misses = compare(args.trials)
    return 1 if (args.strict and misses) else 0


if __name__ == "__main__":
    sys.exit(main())
