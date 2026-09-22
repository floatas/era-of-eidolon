#!/usr/bin/env python3
"""Plan Shirad's Forge fights without playing each one by hand.

Each room is checked against the hero who would have walked there: a level,
a weapon and a suit from the real catalogue, all spent into Strength. The
same fight is also run in the starting Scrapsuit at level 0, so a room that
requires the armour shows up as a win when you are ready and a loss when
you are not.

  axe      walk up and Hit, nothing else
  careful  Dodge once a turn, Minor Cure under half life, otherwise Hit

Creature life and blow grow with how far the room is from the Village, and
the blow is set above the armour that room expects. Edit RANKS or EXPECT
and re-run. Nothing here changes the running game.

    python3 tools/fightplan.py
    python3 tools/fightplan.py --profile current
    python3 tools/fightplan.py --trials 200
"""

import argparse
import os
import random
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "server"))

from catalogue import catalogue          # noqa: E402
from world import World                  # noqa: E402

MOVE, HIT, DODGE_COST, CURE_COST = 40, 60, 20, 60
BUDGET = 720
CURE_EFFECT, CURE_PRECISION = 8, 70
DODGE_BONUS = 10

# How far from the Village, counted through the real doors. The row is the
# hero that room expects: level, weapon, armour. All ability points go into
# Strength, which is what an axe-user would do.
EXPECT = [
    (0,  "Bloody Blade", "Scrapsuit"),    # Village
    (2,  "Bloody Blade", "Scrapsuit"),
    (4,  "Bloody Blade", "Snail Shell"),  # first suit worth buying
    (6,  "Longfang",     "Snail Shell"),
    (8,  "Longfang",     "Iron Shell"),
    (10, "Corrupter",    "Iron Shell"),
    (12, "Corrupter",    "Doom Suit"),    # the Forge
]

# Species rank. A later room of the same species is harder because of depth,
# not because the name changed. Longer keys win, so "Fire Devil" beats "Devil".
RANK = {
    "Gorrak": 1, "Beetle": 1,
    "Skeleton": 2, "Fungusman": 2,
    "Fire Devil": 3, "Ghost": 3, "Mira": 3,
    "Golem": 4, "Aldor": 4,
    "Beholder": 5, "Floating": 5, "Shirard": 5, "wizard": 5,
}


def creature_name(w, node):
    for r in w.real9:
        if r[0] == node:
            return w.text(r[1]).get(int.from_bytes(r[5:7], "big"), "?")
    return "?"


def spend_strength(level):
    """Two points a level, every one of them into Strength. Matches d.java:
    +3 under 48, +2 under 78, +1 after."""
    strength = 15
    for _ in range(level * 2):
        strength += 3 if strength < 48 else (2 if strength < 78 else 1)
    return strength


def hero_kit(level, weapon, armour):
    """Life stays 40. Toughness does not raise it yet, so a level only
    changes the blow, through Strength, and the suit you are assumed to wear."""
    c = catalogue()
    blade = c.find(weapon)
    suit = c.find(armour)
    strength = spend_strength(level)
    return {
        "max": 40, "hp": 40,
        "level": level, "str": strength, "dex": 15, "will": 15,
        "weapon": blade.effect if blade else -5,
        "weapon_name": blade.name if blade else weapon,
        "armour": suit.effect if suit else 3,
        "armour_name": suit.name if suit else armour,
        "can_wear": (not suit or suit.requirement <= strength),
        "hit_effect": 10, "hit_precision": 100,
    }


def room_hero(depth):
    level, weapon, armour = EXPECT[min(depth, len(EXPECT) - 1)]
    return hero_kit(level, weapon, armour)


def depths(w):
    """Doors from the recovered table. Unreached rooms count as far, not as
    the tutorial."""
    from collections import deque
    start = w.locations[0]
    dist = {start: 0}
    q = deque([start])
    while q:
        loc = q.popleft()
        for _, dest in w.exits.get(loc, []):
            if dest not in dist and dest in w.locations:
                dist[dest] = dist[loc] + 1
                q.append(dest)
    for loc in w.locations:
        dist.setdefault(loc, len(EXPECT) - 1)
    return dist


def rank_of(name):
    low = name.lower()
    for key in sorted(RANK, key=len, reverse=True):
        if key.lower() in low:
            return RANK[key]
    return 1


def scaled(name, depth, armour_reduce):
    """Life grows with the walk. The blow is set just above the armour the
    room expects, so the suit matters and a bare Scrapsuit does not keep up."""
    rank = rank_of(name)
    life = 20 + 6 * depth + 8 * rank
    blow = armour_reduce + 4 + rank
    return (life, blow, 58 + 2 * rank, 10 + depth + rank,
            0 if rank < 4 else rank - 3, 8 + 2 * rank)


def stable(name):
    h = 0
    for ch in name:
        h = (h * 33 + ord(ch)) & 0xFFFFFFFF
    return h


def lookup(name, profile, mob, depth, armour_reduce):
    if profile == "scaled":
        return scaled(name, depth, armour_reduce)
    off = mob.offence()
    return (mob.max_hp, off["effect"], off["precision"], off["avoid"],
            off["armour"], off["will"])


def strike_weapon(w, effect, precision, potency, avoid, dex, armour, weapon, rng):
    return w.strike(effect, precision, potency, avoid, dex=dex, armour=armour,
                    weapon_mod=weapon, rng=rng)


def one_fight(w, hero, mob, policy, rng, gap=2):
    """`gap` is how many straight steps apart they start. Both walk until
    they are in contact, then spend the rest of each turn swinging."""
    hh, mh = hero["max"], mob[0]
    turns = 0
    while hh > 0 and mh > 0 and turns < 40:
        turns += 1
        guard = 0
        dodged = False
        dist = gap
        t_h = t_m = 0
        # Both walk. A gap of 2 (Gorrak's distance at the village) closes
        # after one step from each of them.
        while dist > 1 and t_h + MOVE <= BUDGET and t_m + MOVE <= BUDGET:
            t_h += MOVE
            t_m += MOVE
            dist -= 2
        while hh > 0 and mh > 0:
            act = policy(hh, hero["max"], dodged)
            cost = {"dodge": DODGE_COST, "cure": CURE_COST}.get(act, HIT)
            hero_can = t_h + cost <= BUDGET
            mob_can = t_m + HIT <= BUDGET
            if not hero_can and not mob_can:
                break
            if hero_can and (not mob_can or t_h <= t_m):
                t_h += cost
                if act == "dodge":
                    guard += DODGE_BONUS
                    dodged = True
                elif act == "cure":
                    if rng.randint(1, 100) <= CURE_PRECISION:
                        hh = min(hero["max"], hh + CURE_EFFECT + hero["will"] // 10)
                else:
                    _, dmg = strike_weapon(
                        w, hero["hit_effect"], hero["hit_precision"], hero["str"],
                        mob[3], hero["dex"], mob[4], hero["weapon"], rng)
                    mh -= dmg
            else:
                t_m += HIT
                _, dmg = w.strike(
                    mob[1], mob[2], 0, hero["dex"] // 2 + guard,
                    armour=hero["armour"], rng=rng)
                hh -= dmg
    if mh <= 0 and hh > 0:
        return "win", hh, turns
    if hh <= 0:
        return "lose", 0, turns
    return "draw", hh, turns


def axe(hp, mx, dodged):
    return "hit"


def careful(hp, mx, dodged):
    if not dodged:
        return "dodge"
    if hp * 2 < mx:
        return "cure"
    return "hit"


def rate(w, hero, stats, policy, trials, loc, name, gap):
    wins = left = 0
    for i in range(trials):
        rng = random.Random((loc << 16) ^ (i * 997) ^ stable(name) ^ policy.__name__.__len__())
        result, hp, _ = one_fight(w, hero, stats, policy, rng, gap)
        wins += result == "win"
        left += hp
    return wins / trials, left / trials


def summarise(w, profile, trials, gap):
    groups = defaultdict(list)
    for mob in w.mobs.values():
        if mob.npc or not mob.alive:
            continue
        groups[(mob.location, creature_name(w, mob.node))].append(mob)

    far = depths(w)
    starter = hero_kit(0, "Bloody Blade", "Scrapsuit")
    print(f"profile {profile}   {trials} trials, start {gap} steps apart")
    print("ready = the level and suit that distance expects. scraps = level 0,")
    print("Bloody Blade, Scrapsuit. Life is 40 either way.")
    print(f"{'where':<18} {'d':>2} {'expects':<22} {'creature':<16} "
          f"{'life':>4} {'blow':>4}  {'axe':>6} {'care':>6} {'in scraps':>9}")
    seen = None
    for loc, name in sorted(groups, key=lambda k: (far[k[0]], k[0], k[1])):
        depth = far[loc]
        hero = room_hero(depth)
        if seen != loc:
            wear = "" if hero["can_wear"] else " (cannot wear yet)"
            print(f"  — {w.name(loc)}  level {hero['level']}  "
                  f"Str {hero['str']}  {hero['weapon_name']} ({hero['weapon']:+d})  "
                  f"{hero['armour_name']} (stops {hero['armour']}){wear}")
            seen = loc
        sample = groups[(loc, name)][0]
        stats = lookup(name, profile, sample, depth, hero["armour"])
        axe_p, _ = rate(w, hero, stats, axe, trials, loc, name, gap)
        care_p, _ = rate(w, hero, stats, careful, trials, loc, name, gap)
        bare_p, _ = rate(w, starter, stats, axe, trials, loc, name + " bare", gap)
        note = ""
        if bare_p < 0.35 and care_p > 0.6:
            note = "  needs the suit"
        elif axe_p > 0.92:
            note = "  axe rarely loses"
        elif care_p < 0.4:
            note = "  hard even if ready"
        print(f"{'':<18} {depth:>2} {'':<22} {name[:16]:<16} "
              f"{stats[0]:>4} {stats[1]:>4}  "
              f"{axe_p*100:>5.0f}% {care_p*100:>5.0f}% {bare_p*100:>8.0f}%{note}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--profile", choices=("scaled", "current"), default="scaled")
    p.add_argument("--trials", type=int, default=60)
    p.add_argument("--gap", type=int, default=2,
                   help="straight steps between hero and creature at the start")
    args = p.parse_args()
    summarise(World("ShiradsForge"), args.profile, args.trials, args.gap)


if __name__ == "__main__":
    main()
