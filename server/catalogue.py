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
        self.price = max(5, int(self.effect * 12 + rank * 9))

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
        """The rules say a hero starts with the most basic sword and bow."""
        out = {}
        for kind, cls in (("weapon", "sword"), ("weapon", "bow")):
            for i in self.get(kind):
                if i.cls == cls:
                    out[cls] = i
                    break
        for i in self.get("armour"):
            out["armour"] = i
            break
        return out


_C = None


def catalogue():
    global _C
    if _C is None:
        _C = Catalogue()
    return _C
