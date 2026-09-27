#!/usr/bin/env python3
"""The side panel's contents: everything about the chapter, to be browsed.

It used to follow the player, which meant guessing where they were from
whatever request happened to carry a room id. Under CheerpJ the client's
"I have loaded a map" ping never reaches the server at all, so the panel sat
on a stale room and looked broken.

So it does not follow any more. It is a reference: the player opens what they
want. Nothing here depends on the session, which is why it can be built once
and served flat.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tiers  # noqa: E402

TURN = 720


def _plural(n, one, many=None):
    return f"{n} {one if n == 1 else (many or one + 's')}"


def _areas(w, handlers):
    out = []
    for loc in w.locations:
        mp = w.map(loc)
        if not mp:
            continue
        w.location = loc
        here = [m for m in w.mobs.values() if m.location == loc]
        live = [m for m in here if m.alive]
        waiting = [m for m in here if not m.alive and getattr(m, "dormant", False)]
        kinds = {}
        for m in live:
            n = handlers.fighter_name(w, m)
            if n == "It":
                n = w.creature_name(m.creature) or "something"
            kinds[n] = kinds.get(n, 0) + 1
        lines = []
        for (x, y), dest in w.EXITS.get(loc, []):
            d = dest[0] if isinstance(dest, tuple) else dest
            lines.append(f"A way out at ({x},{y}) leads to {w.name(d)}.")
        if kinds:
            lines.append("Here: " + ", ".join(
                f"{n} ×{c}" if c > 1 else n for n, c in sorted(kinds.items())))
        if waiting:
            lines.append(f"{_plural(len(waiting), 'creature')} not here yet; "
                         "something has to wake them.")
        crates = w.containers(loc)
        if crates:
            lines.append(_plural(len(crates), "crate") + " to break open.")
        for _k, txt in sorted(w.res.strings(3, loc).items()):
            if len(txt) > 40 and not txt.startswith(("Fight", "Talk", "Use")):
                lines.append(txt)
        out.append({"id": f"area-{loc}", "title": w.name(loc), "lines": lines})
    return out


def _creatures(w, handlers):
    seen, out = set(), []
    for m in sorted(w.mobs.values(), key=lambda x: x.node):
        named = handlers.fighter_name(w, m)
        name = named if named != "It" else (w.creature_name(m.creature) or "")
        if not name or name in seen:
            continue
        seen.add(name)
        pattern = handlers.pattern_of(w, m)
        covered = handlers.THREAT.get(pattern, 8)
        swings = max(1, TURN // m.offence()["swing"])
        where = sorted({w.name(o.location) for o in w.mobs.values()
                        if w.creature_name(o.creature) == name
                        or handlers.fighter_name(w, o) == name})
        lines = [
            f"Threatens {covered} of the eight squares around it, "
            f"so {8 - covered} are safe while it faces where it faces.",
            f"Swings {_plural(swings, 'time')} a turn.",
        ]
        if swings >= 3:
            lines.append("Quick, so each blow is small — armour subtracts from "
                         "every one of them, and is worth wearing here.")
        else:
            lines.append("Slow and heavy, so each blow is large — stepping out "
                         "of reach saves the whole of one.")
        if covered == 8:
            lines.append("There is nowhere beside it that is safe.")
        if where:
            lines.append("Found in: " + ", ".join(where[:6]))
        out.append({"id": f"foe-{name}", "title": name, "lines": lines})
    return out


def _gear(w, catalogue):
    out = []
    for kind, label in (("weapon", "Weapons"), ("armour", "Armour")):
        for it in sorted(catalogue().get(kind),
                         key=lambda i: (i.requirement, i.price)):
            if not w.usable(it) or it.name in w.BAR_SKILLS:
                continue
            lines = []
            if it.kind == "armour":
                lines.append(f"Takes {it.effect} off every blow that lands.")
            else:
                swings = max(1, (TURN - 160) // (it.time or 60))
                lines.append(f"Adds {it.effect} to a blow.")
                lines.append(f"One swing costs {it.time or 60} of the "
                             f"{TURN}-unit turn, so about "
                             f"{_plural(swings, 'blow')} a turn after walking.")
            lines.append(f"Needs {it.ability} {it.requirement}. "
                         f"Costs {it.price} gold; breaking it returns "
                         f"{tiers.RECYCLE_PERCENT}%.")
            out.append({"id": f"gear-{it.name}", "title": it.name,
                        "lines": lines, "group": label})
    return out


def _rules():
    return [
        {"id": "rule-turn", "title": "The turn", "lines": [
            f"A turn is {TURN}. A step costs 40, a blow what your weapon takes "
            "to swing, a dodge 20, a cure 60.",
            "Both sides choose blind and everything happens in time order, so "
            "you are planning against where a creature stands now, not where "
            "it will be.",
        ]},
        {"id": "rule-shape", "title": "Where a creature can reach", "lines": [
            "A creature threatens a shape, not every square around it. A "
            "skeleton reaches one square in front; a golem three; the "
            "beholder only its four corners; a fungusman four squares at "
            "arm's length and none at all beside it.",
            "It picks its facing before the turn plays and cannot change it, "
            "so a square that is safe when the turn starts stays safe.",
            "The wider a shape, the softer it hits. A shape you can step out "
            "of hits hard, because there is somewhere to stand.",
        ]},
        {"id": "rule-defence", "title": "Armour or footwork", "lines": [
            "Armour comes off every blow, so it earns its price against quick "
            "creatures that swing three or four times a turn.",
            "Stepping out of reach avoids a whole blow, so it is worth more "
            "against slow ones that swing twice and hit hard.",
            "They answer different creatures. Carrying both is the point.",
        ]},
        {"id": "rule-colour", "title": "The marks in a shop", "lines": [
            "Green is better than what you are carrying and you can pay for it.",
            "Red is worse than what you are carrying.",
            "Grey means the ability it asks for is still out of reach.",
            "Better is measured over a whole turn, not by the number on the "
            "item: a fast sword with a small number beats a slow axe with a "
            "big one.",
        ]},
    ]


def build(game="ShiradsForge"):
    from world import World
    from catalogue import catalogue
    import handlers
    w = World(game)
    return {"game": game, "sections": [
        {"name": "How it works", "entries": _rules()},
        {"name": "Areas", "entries": _areas(w, handlers)},
        {"name": "Creatures", "entries": _creatures(w, handlers)},
        {"name": "Gear", "entries": _gear(w, catalogue)},
    ]}


_CACHE = {}


def reference(game="ShiradsForge"):
    if game not in _CACHE:
        _CACHE[game] = build(game)
    return _CACHE[game]
