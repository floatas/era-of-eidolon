"""Shirad's Forge in three tiers, and what its creatures are sized against.

Difficulty belongs to the stretch of route, not to the hero. Each tier has a
reference hero, the level, main ability, life and suit he should carry in,
and the best gear its traders sell. Creatures are sized against that and
never against the hero actually playing:

    life   A creature of weight 30 (a Beetle) takes one turn to kill with
           the tier's best weapon. The weapon a tier opens with, the last
           tier's best, deals about 60% of that, so an encounter of two
           takes one to two turns longer without the upgrade. Gear decides
           how long a fight lasts.

    blow   One turn standing in one creature's shape costs a third of the
           reference life, after the reference suit. More life or a better
           suit survives more mistakes; less survives fewer. Footwork
           decides whether you are hit at all.

So levels, life and armour protect, a hero who has outlevelled a tier feels
it, and the next tier sets the pressure back up. None of this is watAgame's:
their creature numbers were the server's and did not survive. Weight is
theirs, byte 11 of the type 9 row, Skeleton 18 to Fungusman 50.
"""

import json
import os
import statistics

from catalogue import catalogue

# Which game the server plays. "classic" is as close to watAgame's as the
# record allows: a creature strikes anything beside it (the client's own
# contact rule), no attack shapes, no mid-turn habits, no shells, and bosses
# are single fights except Mira, whose second phase is watAgame's own twin.
# "remastered" is ours: shapes, habits, two-phase bosses, shells. Both keep
# the fixes, the tier sizing that stands in for the lost server numbers, the
# gear, crates, trophies and the ending. Set on /balance, kept in
# balance.json; RULESET_OVERRIDE is for tests and tools.
RULESETS = ("classic", "remastered")
RULESET_OVERRIDE = None
_BALANCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "balance.json")


def ruleset():
    if RULESET_OVERRIDE in RULESETS:
        return RULESET_OVERRIDE
    try:
        with open(_BALANCE) as fh:
            chosen = json.load(fh).get("ruleset")
    except (OSError, ValueError, AttributeError):
        chosen = None
    return chosen if chosen in RULESETS else "classic"


def remastered():
    return ruleset() == "remastered"


# lab_data and balance_sim walk the chapter in this order. Stops 1-4 are
# tier I, 5-11 tier II, 12-18 tier III, as tools/tune_gear.py pitched the
# gear: Lava Island's trader opens tier I, Dwarven Hall and Fire Cave tier
# II, The Lair and The Core tier III.
ROUTE = [1, 15, 2, 9, 3, 8, 10, 12, 14, 4, 11, 5, 16, 13, 6, 17, 18, 7]
STOPS = {"I": (1, 4), "II": (5, 11), "III": (12, 18)}
ORDER = ("I", "II", "III")

# Who the tier is built for, on the way in. Life is 40 + 6 a level. The
# main ability assumes two of every three raise points go into it, which
# lands on the Strength tune_gear.py pitched each tier's gear at (3, 17, 33).
REFERENCE = {
    "I":   {"level": 0, "stat": 3,  "life": 40, "suit": "Scrapsuit"},
    "II":  {"level": 4, "stat": 19, "life": 64, "suit": "Snail Shell"},
    "III": {"level": 8, "stat": 35, "life": 88, "suit": "Iron Shell"},
}

# A turn is 720; the reference hero spends 160 of it getting into place.
TURN = 720
WALK = 160
HIT = 10                 # the Hit skill's effect
BEETLE = 30              # the weight that takes exactly one turn
POTENCY_DIV = 3          # world.POTENCY_DIV, repeated to avoid the import cycle
REFERENCE_PRECISION = 70  # Mob.offence()["precision"]


def tier_of(loc):
    """The tier a Shirad's Forge location belongs to, or None."""
    if loc not in ROUTE:
        return None
    stop = ROUTE.index(loc) + 1
    for tier, (lo, hi) in STOPS.items():
        if lo <= stop <= hi:
            return tier
    return None


def before(tier):
    i = ORDER.index(tier)
    return ORDER[i - 1] if i else None


# The swing time at which an ability adds exactly a third of itself.
REF_SWING = 120
# The client reads an action's cost as a u8 (handlers.MAX_COST).
MAX_SWING = 255


def potency_bonus(stat, swing_time=None):
    """What an ability adds to one blow.

    A third of it, scaled by how long the blow takes: a sword (96) adds
    0.8 of that a swing and a hammer (240) twice it, so both add the same
    over a turn. Adding it flat to every blow let fast weapons outgrow slow
    ones as the ability rose, a Corrupter keeping pace with tier II gear at
    Strength 19. With no time given, the flat third stands."""
    if not swing_time:
        return stat // POTENCY_DIV
    return round(stat * swing_time / (POTENCY_DIV * REF_SWING))


def line_of(it):
    """sword, heavy (axes and hammers) or bow: the three lines of weapon."""
    if it is None:
        return None
    if it.cls == "bow":
        return "bow"
    return "sword" if it.cls == "sword" else "heavy"


# What each prize crate holds, planned together with the tier's traders.
#   weapon  the tier's step up in the hero's own line (the weapon in his hand
#           decides: sword, axe and hammer, or bow)
#   suit    the tier's step up in suits
#   spare   any other piece from the tier or below that he does not carry:
#           something to switch to, or to recycle (RECYCLE_PERCENT)
# The steps are on the main path, so nobody misses them; every other crate is
# a spare, so every crate is worth the detour. A step is the cheapest piece
# better than what he wears, from the crate's tier or an earlier one. Past
# tier I no crate holds the dearest piece of a line in its own tier
# (is_top): that stays the trader's. A crate with nothing left to give pays
# a purse (PURSE). Any crate not listed is a spare.
CRATES = {
    # tier I: traders at Lava Island
    69: "weapon",     # Village: a new hero's first box, wearable at once
    240: "suit",      # Lava Island
    # tier II: traders at Dwarven Hall (lower half) and Fire Cave (upper)
    160: "weapon",    # Dwarven Hall
    166: "suit",      # Mira's Hideout
    # tier III: traders at The Lair and The Core
    172: "weapon",    # The Lair
    174: "suit",      # The Core
}
PURSE = {"I": 30, "II": 30, "III": 40}
# Toughness is life (rules: "LP are directly connected to the Toughness
# Ability", no ratio given). The base stays 40 + 6 a level, which the tiers
# are sized against, and every point of Toughness above the starting 3 adds
# TOUGH_LIFE on top: one raise point, +3 Toughness, is 15 life.
# Speed is how fast every action is done (rules: "Speed affects how fast all
# actions are performed"). An action takes SPEED_DIV / (SPEED_DIV - 3 + Speed)
# of its time: Speed 3 changes nothing, Speed 27 is 83% of the time.
# tools/balance_sim.py --variants set both. At 2 life a point Toughness bought
# fewer survivable mistakes than the Dexterity it gave up (half of Dexterity
# is dodging). At SPEED_DIV 200 Speed was slower than Dexterity; at 100 a
# sword with it was both quicker and safer. These make the third raise point
# a real choice: Toughness the tank, Speed the tempo, Dexterity between.
TOUGH_LIFE = 5
SPEED_DIV = 120


def life_for(level, toughness):
    return 40 + 6 * level + TOUGH_LIFE * max(0, toughness - 3)


def speed_scaled(time, speed):
    return max(1, round(time * SPEED_DIV / (SPEED_DIV - 3 + speed)))


# The free kit. Never a spare: one of these in a crate is not a find.
STARTERS = ("Bloody Blade", "Short Bow", "Scrapsuit")
# What Recycle gives back, as a percent of the price. With every crate holding
# an item and every outgrown weapon worth breaking, 70% earned three times
# what a tier's gear costs. run/mkjar.py writes this number into the phone's
# confirmation.
RECYCLE_PERCENT = 30


def crate_role(state):
    return CRATES.get(state, "spare")


def is_top(it):
    """Whether this is the dearest piece of its line (or the dearest suit)
    in its tier: the one a trader keeps for himself, never a crate."""
    t = getattr(it, "tier", None)
    if t is None:
        return False
    kind = "suit" if it.kind == "armour" else line_of(it)
    pool = [i for i in catalogue().get(it.kind) if getattr(i, "tier", None) == t
            and ("suit" if i.kind == "armour" else line_of(i)) == kind]
    return bool(pool) and it.price >= max(i.price for i in pool)


def swing_of(it):
    return min(MAX_SWING, it.time) if it and it.time else 60


def weapon_round(it, stat):
    """Damage a turn with this weapon at this ability, before rolls. The 5%
    crits and half-chance precise hits roughly pay for the misses. A bow is
    Shoot (9), a blade Hit (10)."""
    t = swing_of(it)
    swings = max(1, (TURN - WALK) // t)
    skill = 9 if it.cls == "bow" else HIT
    return swings * max(1, skill + it.effect + potency_bonus(stat, t))


def _melee(tier):
    return [i for i in catalogue().get("weapon")
            if getattr(i, "tier", None) == tier
            and i.cls in ("sword", "axe", "hammer")]


def best_round(tier):
    """What the tier's best sword deals in a turn, at the tier's reference
    Strength. The sword is the yardstick: heavy weapons and bows are tuned a
    little above it on paper to pay for their overkill (tools/tune_gear.py),
    and come out level with it in play."""
    stat = REFERENCE[tier]["stat"]
    got = [weapon_round(i, stat) for i in _melee(tier) if i.cls == "sword"]
    got = got or [weapon_round(i, stat) for i in _melee(tier)]
    return max(got) if got else 30


def entry_round(tier):
    """What the weapon the hero walks in with deals: the last tier's best,
    or the Bloody Blade for the first."""
    stat = REFERENCE[tier]["stat"]
    prev = before(tier)
    pool = _melee(prev) if prev else [catalogue().find("Bloody Blade")]
    got = [weapon_round(i, stat) for i in pool if i]
    return max(got) if got else 30


def species_weights(named_rows):
    """name -> watAgame's weight for that species.

    `named_rows` is (name, byte 11) for every creature row. 28 of 90 rows
    carry 0 there, the unique fights and packs that never return, so a row
    with 0 borrows its species' median. A species with no weight at all
    counts as a Ghost."""
    seen = {}
    for name, w in named_rows:
        if w:
            seen.setdefault(name, []).append(w)
    return {name: int(statistics.median(ws)) for name, ws in seen.items()}


# Species that wear a shell, as a share of the tier's sword blow. Armour comes
# off every blow, so a sword (four blows a turn) loses twice what a hammer or
# a bow (two) does: bring the heavy weapon to the Golems. Skeletons, Gorraks,
# Ghosts and Fire Devils stay soft, so their packs are sword country.
SHELL = {"Beetle": 0.30, "Golem": 0.50}


def sword_blow(tier):
    """One blow of the tier's top sword at the tier's reference Strength."""
    swords = [i for i in _melee(tier) if i.cls == "sword"]
    stat = REFERENCE[tier]["stat"]
    if not swords:
        return 10
    it = max(swords, key=lambda i: weapon_round(i, stat))
    return HIT + it.effect + potency_bonus(stat, swing_of(it))


def shell(tier, species):
    share = SHELL.get(species or "", 0)
    return round(share * sword_blow(tier)) if share else 0


# Turns a Beetle-weight creature lasts against the tier's best weapon, as
# best_round counts it. best_round undercounts what a hero really deals: once
# he is beside a creature he swings the whole 720 rather than walking 160 of
# it, and precise hits and practice titles add more. At 1.0 creatures died
# before they swung back, a starter sword won most of tier III on Auto fight,
# and nothing a creature did mattered (tools/autoplay.py). 1.5 is where
# skipping gear starts to lose.
LIFE_TURNS = 1.5
# How much harder a boss hits than a creature of its tier, turn for turn.
BOSS_FORCE = 1.0


def creature_life(tier, weight, species=None):
    """Weight counts a little less than in proportion, so a Fungusman (50)
    takes about one and a half Beetles, not five thirds, and a pair of them
    is not a slog.

    A shelled species gives up life for its armour, so that the average of
    a sword and a hammer clears it as fast as a soft one: the sword loses
    the whole share a turn, the hammer half of it."""
    life = (weight / BEETLE) ** 0.75 * best_round(tier) * LIFE_TURNS
    life *= 1 - 0.75 * SHELL.get(species or "", 0)
    return max(1, round(life))


# Experience and gold a kill pays, per point of the creature's weight. Prices
# climb from tier to tier (a tier III sword is 516, a tier I 238), so gold
# does too. Experience is set so a full clear ends near level 12.
XP_RATE = {"I": 1.0, "II": 0.6, "III": 1.0}
# Gold is sized so that a tier's kills, crates and recycling buy its top
# weapon and top suit with about a quarter to spare (tools/balance_sim.py
# checks the ledger). Past tier I most of it is what crates hold, broken
# down; creatures carry a little.
GOLD_RATE = {"I": 1.0, "II": 0.3, "III": 0.1}
# A boss pays like a creature of this weight: two Fungusmen and a bit. Paying
# out its pool, as it once did, was worth three levels a boss.
BOSS_WEIGHT = 60


def boss_life(tier, turns):
    """One phase of a boss: this many turns of the tier's best weapon, with
    the same LIFE_TURNS allowance creatures get for what a hero really deals
    (a full turn of swings once he is beside it, precise hits, titles)."""
    return max(1, round(turns * best_round(tier) * LIFE_TURNS))


def _expected(blow, chance, armour):
    """World.strike's average over its 1..100 roll, for a blow that hits."""
    crit = chance // 15
    precise = chance // 2 - crit
    plain = chance - chance // 2
    return (crit * max(0, blow * 2 - armour)
            + precise * max(0, blow * 3 // 2 - armour)
            + plain * max(0, blow - armour)) / 100


def creature_blow(tier, swings, covered, mistakes):
    """The effect a creature strikes with, so that a turn in its shape costs
    the reference hero 1/mistakes of his life after his suit.

    A narrow shape may hit a little harder, because there are more squares
    where it cannot touch you; one that covers you everywhere a little
    softer. The spread is kept small, 0.9x to 1.2x, so a mistake is a
    mistake whichever creature you made it against."""
    ref = REFERENCE[tier]
    suit = catalogue().find(ref["suit"])
    armour = suit.effect if suit else 0
    # the reference hero puts his points in Strength, so his Dexterity of 3
    # avoids 1; an archer's higher Dexterity is his own reward
    chance = max(5, min(98, REFERENCE_PRECISION - 1))
    want = ref["life"] / mistakes * (4.0 / max(1, covered)) ** 0.12 / max(1, swings)
    blow = 1
    while _expected(blow, chance, armour) < want and blow < 999:
        blow += 1
    return blow
