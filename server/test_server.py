#!/usr/bin/env python3
"""Fast checks for the server. No emulator, no window, no waiting.

    python3 server/test_server.py

Most of the bugs in this project were server-side data errors — a record one
byte short, a field that meant damage rather than health, an animation id a
creature did not have. All of those are catchable here, in under a second,
instead of fifteen seconds of emulator boot followed by squinting at a
screenshot.

The checks assert against what the decompiled client actually does, with the
source line noted, so a failure says which client expectation was broken.
"""

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import codec
import handlers
from catalogue import catalogue
from world import World

FAILED = []


def check(name, cond, detail=""):
    if cond:
        print(f"  \033[32mok\033[0m   {name}")
    else:
        print(f"  \033[31mFAIL\033[0m {name}" + (f"  — {detail}" if detail else ""))
        FAILED.append(name)


class Req:
    """Enough of relay.Req to drive a handler."""

    def __init__(self, opcode, chunks=(), game="ShiradsForge", session=None):
        self.opcode = opcode
        self.game = game
        self.session = session
        self.chunks = list(chunks)
        self.body = b""

    def all(self, tag):
        return [raw for t, _, raw in self.chunks if t == tag]

    def get(self, tag, default=b""):
        v = self.all(tag)
        return v[-1] if v else default

    def int_(self, tag, default=0):
        raw = self.get(tag)
        return int.from_bytes(raw, "big", signed=True) if raw else default


def frame(resp):
    """magic, status, chunk count — the header the client validates."""
    magic = struct.unpack_from(">H", resp)[0]
    status = resp[2]
    count = struct.unpack_from(">H", resp, 8)[0]
    return magic, status, count


def chunks_of(resp):
    return codec.parse_chunks(resp[10:])


def main():
    print("world")
    for game in ("ShiradsForge", "SterlingLake"):
        w = World(game)
        rows = w.entity_table()
        check(f"{game}: locations found", len(w.locations) > 10,
              f"got {len(w.locations)}")
        check(f"{game}: every location is named",
              all(not w.name(l).startswith("Area ") for l in w.locations))
        check(f"{game}: hero spawns somewhere walkable",
              w.can_stand(w.hero_x, w.hero_y))

        # type 9 rows are fixed width; the client indexes up to [15]
        check(f"{game}: type 9 rows are 19 bytes",
              all(len(r) == 19 for r in w.mob_table()))

        # a(Object) computes the second trailing block unconditionally at
        # 14 + [13] + 1 + rec[14 + [13]] — a short record reads past its end
        bad = []
        for r in rows:
            p = 14 + r[13]
            v12 = p + 1 + r[p]
            if v12 >= len(r):
                bad.append(r.hex())
                continue
            v15 = v12 + r[v12] + 1
            v20 = v15 + r[v15] + 1 if v15 < len(r) else len(r)
            if v20 + (r[v20] if v20 < len(r) else 0) >= len(r):
                bad.append(r.hex())
        check(f"{game}: type 1 records carry all four blocks", not bad,
              f"{len(bad)} short, e.g. {bad[0] if bad else ''}")

        # j.java throws "Unable to get anim N" rather than degrading
        anims_ok = all(
            w.anim(m.creature, k) in w.res.anims(11, m.creature)
            for m in w.mobs.values() for k in ("idle", "walk", "attack"))
        check(f"{game}: every animation id exists for its creature", anims_ok)

        # byte 15 starts animation 14 on spawn (d.java:226); the townsfolk
        # sheet has no animation 14, and asking kills the client's paint thread
        rows = {r[0]: r for r in w.mob_table()}
        wrong = [m.node for m in w.mobs.values()
                 if rows[m.node][15]
                 and 14 not in w.res.anims(11, m.creature)]
        check(f"{game}: spawn animation only where the creature has one",
              not wrong, f"nodes {wrong[:5]}")

        # monsters must not borrow the townsfolk sheet
        check(f"{game}: monsters are not NPCs",
              all(m.creature != w.npc_creature for m in w.living()))

        # nodes index the tag 21/25 arrays and d.n, sized from tag 25
        top = max((m.node for m in w.mobs.values()), default=0)
        check(f"{game}: node ids fit the state arrays",
              top < len(w.node_states()), f"max node {top}")

    print("\nhandlers")
    check("every opcode the client can send has a handler",
          set(handlers.HANDLERS) == set(range(1, 29)),
          f"missing {sorted(set(range(1, 29)) - set(handlers.HANDLERS))}")
    for op in range(1, 29):
        resp = handlers.dispatch(Req(op))
        magic, status, count = frame(resp)
        check(f"opcode {op}: well-formed frame",
              magic == 0xBABE and len(resp) >= 10,
              f"magic {magic:#x}")
        check(f"opcode {op}: status is non-zero", status != 0,
              "status 0 reads as 'Second login detected!'")

    # d.java:1077 reads as[p] and as[p+1] before switching on the kind
    w = World()
    acts = [("Move", 100, 1, [(w.hero_x, w.hero_y + 1)])]
    script = handlers.resolve(w, acts)
    short = [r.hex() for r in script if len(r) - (5 + r[4]) < 2]
    check("turn results carry >= 2 payload bytes", not short,
          f"{len(short)} too short")

    # d.a(b) ends on aF.elementAt(1)
    rows = handlers.entity_rows(World())
    check("opcode 12 lists at least two entities", len(rows) >= 2,
          f"got {len(rows)}")
    check("opcode 12 rows are 8 bytes", all(len(r) == 8 for r in rows))

    # l is max HP and m is accumulated damage, not current and max
    w2 = World()
    w2.hero_hp = w2.hero_max - 7
    row = handlers.entity_rows(w2)[0]
    check("hero row sends max HP and damage",
          int.from_bytes(row[3:5], "big") == w2.hero_max
          and int.from_bytes(row[5:7], "big") == 7,
          f"l={int.from_bytes(row[3:5],'big')} m={int.from_bytes(row[5:7],'big')}")

    # slots 0..5 are cast to f unguarded while a slot is open (d.java:1059)
    resp = handlers.dispatch(Req(12))
    action_tags = {t for t, typ, _ in chunks_of(resp) if 30 <= t <= 35}
    types = {typ for t, typ, _ in chunks_of(resp) if 30 <= t <= 35}
    check("all six action slots are present", action_tags == set(range(30, 36)),
          str(sorted(action_tags)))
    check("all six action slots are f records (type 4)", types == {4},
          f"types {sorted(types)}")

    print("\ncatalogue")
    c = catalogue()
    measured = [i for k in ("weapon", "armour", "charm", "skill", "spell")
                for i in c.get(k) if i.measured]
    check("watAgame's own numbers are loaded", len(measured) > 190,
          f"only {len(measured)} entries carry measured values")

    # the action bar must cost what the recovered table says, not a guess
    known = {i.name.lower(): i for k in ("skill", "spell") for i in c.get(k)}
    drift = [(n, t, known[n.lower()].time) for n, t, _ in handlers.ACTIONS
             if n.lower() in known and known[n.lower()].time
             and known[n.lower()].time != t]
    check("action bar Time costs come from the catalogue", not drift,
          str(drift))
    check("weapons loaded", len(c.get("weapon")) > 50)
    check("armour loaded", len(c.get("armour")) > 10)
    check("starting kit resolves", len(c.starting_kit()) >= 2)

    print()
    if FAILED:
        print(f"\033[31m{len(FAILED)} failed\033[0m: " + ", ".join(FAILED))
        return 1
    print("\033[32mall checks passed\033[0m")
    return 0


if __name__ == "__main__":
    sys.exit(main())
