"""The item, skill and spell catalogue, from watAgame's own site.

`notes/site/catalogue.json` was scraped from eraofeidolon.com via the Wayback
Machine. It has every name, class and description, in the order the game listed
them — which is progression order, weakest first.

What it does NOT have is the numbers. Effect, Time cost, price and ability
requirements were only ever rendered in-game, by the server, in the Market and
Academy screens, and were never published. So those are derived here from
position in the list plus the qualitative balance the rules document states:

    Sword   fast, lower damage, often high Intelligence
    Axe     a blend of the two, often high Dexterity
    Hammer  slow, highest damage, high Strength
    Bow     high Dexterity, two-handed, needs line of sight
    Bomb    targets a square, no line of sight, blast radius 1

Everything here is therefore honest reconstruction: the names and their order
are the game's, the numbers are ours.
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(os.path.dirname(HERE), "notes", "site", "catalogue.json")

# Class -> (damage multiplier, time multiplier, the ability it keys off).
# Straight from EOE_Game_Rules, "Items".
WEAPON_CLASS = {
    "sword":  (1.0, 1.0, "Intelligence"),
    "axe":    (1.3, 1.25, "Dexterity"),
    "hammer": (1.7, 1.6, "Strength"),
    "bow":    (1.1, 1.15, "Dexterity"),
    "bomb":   (1.5, 1.4, "Strength"),
    "trap":   (1.2, 1.3, "Intelligence"),
    "mine":   (1.2, 1.3, "Intelligence"),
}


def _parse(name):
    """Entries look like "12 - Fell Blade (sword)" or "3 - Iron Shell"."""
    m = re.match(r"^\s*(\d+)\s*-\s*(.+?)\s*(?:\(([^)]+)\))?\s*$", name)
    if not m:
        return None
    return int(m.group(1)), m.group(2), (m.group(3) or "").lower().strip()


# --------------------------------------------------- the recovered numbers
#
# notes/eoe-arena/ holds watAgame's own item and skill statistics, exported
# from the Arena's database (see SOURCE.md there). Where a name matches, these
# replace the values this file used to guess. Roughly 200 of our 203 entries
# are covered, so the guesses below now only fill gaps.

ARENA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "notes", "eoe-arena")
# which slice of that catalogue this chapter sells (tools/pick_items.py)
CHAPTER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "notes", "chapter-items.json")

# req[] indexes abilities in the Arena's order, which is not ours.
ARENA_ABILITY = {1: "Strength", 2: "Dexterity",
                 3: "Intelligence", 4: "Willpower"}


def _load_jsonl(name):
    out = {}
    try:
        with open(os.path.join(ARENA_DIR, name)) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    row = json.loads(line)
                    out[row["name"].lower()] = row
    except OSError:
        pass
    return out


_ARENA_ITEMS = _load_jsonl("items_exported.json")
_ARENA_SKILLS = _load_jsonl("skills_exported.json")


def _requirement(req):
    """The one ability a row actually asks for, and how much of it."""
    for i, v in enumerate(req or []):
        if v and i in ARENA_ABILITY:
            return ARENA_ABILITY[i], int(v)
    return None, 0


class Item:
    def __init__(self, kind, rank, name, cls, desc):
        self.kind = kind          # weapon / armour / charm / skill / spell
        self.rank = rank          # position in the game's own list
        self.name = name
        self.cls = cls
        self.desc = desc

        dmg, tim, ability = WEAPON_CLASS.get(cls, (1.0, 1.0, "Strength"))
        self.ability = ability
        if kind == "weapon":
            self.effect = int(round((3 + rank * 1.4) * dmg))
            self.time = int(round((90 + rank * 6) * tim))
            self.requirement = max(5, int(4 + rank * 1.6))
        elif kind == "armour":
            self.effect = int(round(1 + rank * 1.3))     # damage reduction
            self.time = 0
            self.ability = "Strength"                    # weight -> Strength
            self.requirement = max(5, int(4 + rank * 1.8))
        elif kind == "charm":
            self.effect = 3                              # every charm states +3
            self.time = 0
            self.requirement = 0
        else:                                            # skill / spell
            self.effect = int(round(2 + rank * 1.1))
            self.time = int(round(70 + rank * 8))
            self.requirement = max(5, int(4 + rank * 1.4))
        self.precision = 100
        self.weight = 0
        self.measured = False
        self._adopt_arena()
        self.price = max(5, int(self.effect * 12 + rank * 9)
                         if not self.measured
                         else self.weight * 14 + self.requirement * 6)
        # which stretch of the route a chapter sells it on, from
        # chapter-items.json; None for anything the chapter file does not tune
        self.tier = None

    def _adopt_arena(self):
        """Replace the guesses with watAgame's numbers, where we have them."""
        row = _ARENA_SKILLS.get(self.name.lower()) \
            or _ARENA_ITEMS.get(self.name.lower())
        if not row:
            return
        self.measured = True
        ability, need = _requirement(row.get("req"))
        if ability:
            self.ability, self.requirement = ability, need
        self.weight = int(row.get("weight", 0) or 0)

        if "speed" in row:                       # a skill or spell
            self.effect = int(row.get("value", 0) or 0)
            self.time = int(row.get("speed", 0) or 0)
            self.precision = int(row.get("precision", 100) or 100)
            self.energy = int(row.get("energy", 0) or 0)
            return

        v1 = int(row.get("value1", 0) or 0)
        v2 = int(row.get("value2", 0) or 0)
        if self.kind == "armour":
            self.effect, self.time = v1, 0       # v1 is flat damage reduction
        elif self.kind == "charm":
            self.effect, self.time = v2 // 10 or 3, 0
        else:
            # A weapon's value1 is a damage PERCENTAGE, 95-120. The rules add
            # weapon to skill and Strength rather than multiplying, so carry
            # it as the modifier it is.
            self.effect = v1 - 100
            self.precision = v2 or 100

    def label(self):
        bits = [self.name]
        if self.effect:
            bits.append(f"E{self.effect}")
        if self.time:
            bits.append(f"Ti{self.time}")
        bits.append(f"{self.price}g")
        return " ".join(bits)

    def __repr__(self):
        return f"<{self.kind} {self.rank} {self.name}>"


class Catalogue:
    #  page key -> what it actually is
    KINDS = {"items1": "weapon", "items2": "armour", "items3": "skill",
             "items4": "spell", "items6": "charm", "items5": "gladiator"}

    def __init__(self, path=PATH):
        self.by_kind = {v: [] for v in self.KINDS.values()}
        try:
            raw = json.load(open(path))
        except (OSError, ValueError):
            raw = {}
        for page, kind in self.KINDS.items():
            for e in raw.get(page, []):
                p = _parse(e["name"])
                if not p:
                    continue          # the "Introduction" blurb
                rank, name, cls = p
                self.by_kind[kind].append(
                    Item(kind, rank, name, cls, e["description"]))
        for v in self.by_kind.values():
            v.sort(key=lambda i: i.rank)
        self._apply_chapter()

    # Fight-bar actions whose time the chapter sets. Minor Cure at the
    # Arena's 60 could be queued a dozen times a turn and out-heal standing
    # in any creature's shape; at 150, about a heavy swing, two casts to undo
    # one turn in a shape cost 40% of the turn, so it is the emergency
    # button. A hero who raises Willpower heals 30-40 a cast and pays for it
    # in raise points, as a Toughness hero does.
    CHAPTER_TIMES = {"Minor Cure": 150}

    def _apply_chapter(self):
        """Keep only what this chapter sells, at this chapter's requirements.

        watAgame wrote one catalogue for the Arena, where a duellist levels
        to 49 and requirements run to 78. A chapter hero clears 87 creatures,
        reaches about level 19, and starts every ability at the catalogue's
        own floor of 3. Against the Arena ladder that leaves almost the whole
        list unwieldable — the shop shelf empties and crates have nothing to
        drop.

        notes/chapter-items.json is the split: a third of the melee keeping
        swords, axes and hammers so speed stays a choice, half the bows, a
        third of the armour, requirements respread over what a chapter hero
        covers, and the rest tagged for the two sequels. Anything held back
        is dropped here, so shops and crates never offer it.

        The file is optional: without it the full Arena catalogue stands, as
        it did before.
        """
        for kind in ("skill", "spell"):
            for it in self.by_kind.get(kind, []):
                if it.name in self.CHAPTER_TIMES:
                    it.time = self.CHAPTER_TIMES[it.name]
        try:
            with open(CHAPTER_PATH) as fh:
                rows = json.load(fh)
        except (OSError, ValueError):
            return
        want = {}
        for group in rows.values():
            for r in group:
                want[r["name"].lower()] = r
        for kind, items in self.by_kind.items():
            if kind not in ("weapon", "armour"):
                continue          # skills and spells are the bar, not stock
            keep = []
            for it in items:
                r = want.get(it.name.lower())
                if r is None:
                    keep.append(it)      # not in the split at all: leave it
                elif r.get("chapter") == 1:
                    # requirement, effect and weapon price are retuned for
                    # the chapter (tools/pick_items.py, tools/tune_gear.py);
                    # time and class stay watAgame's.
                    it.requirement = r["requirement"]
                    if r.get("effect") is not None:
                        it.effect = r["effect"]
                    it.tier = r.get("tier")
                    # tune_gear.py sets weapon prices so every line's top
                    # piece in a tier costs the same; suits keep watAgame's
                    if r.get("price"):
                        it.price = r["price"]
                    keep.append(it)
                # chapter 2 and 3 are simply not stocked here
            self.by_kind[kind] = keep

    def get(self, kind):
        return self.by_kind.get(kind, [])

    def find(self, name):
        for v in self.by_kind.values():
            for i in v:
                if i.name.lower() == name.lower():
                    return i
        return None

    def affordable(self, kind, gold, limit=12):
        return [i for i in self.get(kind) if i.price <= gold][:limit]

    def starting_kit(self):
        """The rules say a hero starts with the most basic sword and bow.

        Basic means the lowest requirement, then the earliest in the
        catalogue. List order is not that: Haunter is a late bow that
        happens to be filed first.
        """
        out = {}
        for cls in ("sword", "bow"):
            picks = [i for i in self.get("weapon") if i.cls == cls]
            if picks:
                out[cls] = min(picks, key=lambda i: (i.requirement, i.rank))
        armours = self.get("armour")
        if armours:
            out["armour"] = min(armours, key=lambda i: (i.requirement, i.rank))
        return out


_C = None


def catalogue():
    global _C
    if _C is None:
        _C = Catalogue()
    return _C
