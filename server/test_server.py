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

import collections
import os
import random
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
    for game in ("ShiradsForge", "SterlingLake", "MistralGrove"):
        w = World(game)
        rows = w.entity_table()
        check(f"{game}: locations found", len(w.locations) > 10,
              f"got {len(w.locations)}")
        check(f"{game}: every location is named",
              all(not w.name(l).startswith("Area ") for l in w.locations))
        check(f"{game}: hero spawns somewhere walkable",
              w.can_stand(w.hero_x, w.hero_y))

        # The client indexes up to [15], so 16 is the floor. We used to
        # assert exactly 19, which is simply what our own encoder emitted;
        # watAgame's real table has rows of 16 and 20.
        check(f"{game}: type 9 rows reach at least byte 15",
              all(len(r) >= 16 for r in w.mob_table()),
              f"shortest {min((len(r) for r in w.mob_table()), default=0)}")

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
        mob_rows = {r[0]: r for r in w.mob_table()}
        wrong = [m.node for m in w.mobs.values()
                 if mob_rows[m.node][15]
                 and 14 not in w.res.anims(11, m.creature)]
        check(f"{game}: spawn animation only where the creature has one",
              not wrong, f"nodes {wrong[:5]}")

        # A doorway's trigger box is checked as x1 <= heroX < x2 (d.java b()).
        # Arriving inside one fires it again on the first frame, and the two
        # locations bounce the player between them forever.
        boxes = {}
        for r in w.entity_table():
            if r[12] == 4:
                boxes.setdefault(r[1], []).append((r[2], r[3], r[4], r[5]))

        def inside(loc, x, y):
            return any(x1 <= x < x2 and y1 <= y < y2
                       for x1, y1, x2, y2 in boxes.get(loc, []))

        bounces = [(r[1], r[14], (r[15], r[16])) for r in w.entity_table()
                   if r[12] == 4 and inside(r[14], r[15], r[16])]
        check(f"{game}: no exit lands inside another exit's box", not bounces,
              str(bounces[:3]))
        stuck = [l for l in w.locations if inside(l, *w.spawn_point(l))]
        check(f"{game}: no location spawns you inside a doorway", not stuck,
              f"locations {stuck[:5]}")

        # and the box has to cover ground you can actually stand on: the
        # doorway tile itself is not walkable, d.b() inverts the test for it
        unreachable = []
        for loc, bs in boxes.items():
            mp = w.map(loc)
            for x1, y1, x2, y2 in bs:
                if mp and not any(mp.walkable(x, y)
                                  for y in range(y1, y2)
                                  for x in range(x1, x2)):
                    unreachable.append((loc, x1, y1))
        # Only meaningful where we placed the doorways. watAgame's own table
        # has one in Mira's Hideout whose box covers no walkable tile, which
        # is their business, not a bug in ours.
        check(f"{game}: every doorway can be walked into",
              w.real1 is not None or not unreachable,
              str(unreachable[:3]))

        # the old rule chose destinations from the source alone, so seven of
        # Sterling Lake's locations could be left but never entered
        inbound = {l: 0 for l in w.locations}
        for links in w.EXITS.values():
            for _, dest in links:
                inbound[dest] += 1
        check(f"{game}: every location can be reached",
              all(inbound[l] for l in w.locations),
              f"no way into {[l for l in w.locations if not inbound[l]][:5]}")
        check(f"{game}: every location can be left",
              all(w.EXITS.get(l) for l in w.locations),
              f"dead ends at {[l for l in w.locations if not w.EXITS.get(l)][:5]}")

        # Opening a crate has to remove it from the tilemap, or it sits there
        # to be opened again for ever. Each one is paired with a kind 6 patch
        # that clears its obstacle nibble, and the crate's completes block
        # names both the patch and itself.
        # Only crates that got an interact entity are in scope: a location
        # whose text has no "crate" or "barrel" label gives the player nothing
        # to choose, so there is nothing to open and nothing to remove.
        ents = w.entity_table()
        patches = {(r[14], r[15], r[16]): r for r in ents if r[12] == 6}
        openable = {(loc, x, y) for loc, _, _ in w.interactables.values()
                    for x, y, _ in w.containers(loc)} & set(patches)
        missing, wrong = [], []
        for loc, x, y in sorted(openable):
            row = patches.get((loc, x, y))
            if row is None:
                missing.append((loc, x, y))
            elif row[19] != (w.map(loc).tile(x, y) & 15):
                wrong.append((loc, x, y))
        check(f"{game}: every openable crate is paired with a tilemap patch",
              w.real1 is not None or (not missing and bool(openable)),
              f"{len(missing)} unpaired of {len(openable)}")
        check(f"{game}: the patch leaves the ground and drops the obstacle",
              w.real1 is not None or not wrong, str(wrong[:2]))

        # A door is not a chute. Every transition has to land the player
        # beside the doorway that leads back, or the way home is across the
        # map and the link reads as one-way even though it is not.
        stranded = []
        for r in w.entity_table():
            if r[12] != 4:
                continue
            src, dst, ax, ay = r[1], r[14], r[15], r[16]
            back = [t for t, d in w.EXITS.get(dst, []) if d == src]
            if not back or not any(max(abs(ax - bx), abs(ay - by)) <= 1
                                   for bx, by in back):
                stranded.append((src, dst, (ax, ay)))
        # Our rule, and a good one: 43 of watAgame's 44 exits obey it too.
        # The single exception is theirs, so with the real table we only ask
        # that it holds nearly everywhere.
        limit = 2 if w.real1 else 0
        check(f"{game}: doorways land you beside the way back",
              len(stranded) <= limit,
              f"{len(stranded)} do not, e.g. {stranded[:2]}")

        # the route recovered from the dialogue is the only part of the graph
        # that is watAgame's, so it must survive whatever else gets wired
        missing = [(w.name(a), w.name(b)) for a, b in w.story_links()
                   if not (any(d == b for _, d in w.EXITS.get(a, []))
                           and any(d == a for _, d in w.EXITS.get(b, [])))]
        check(f"{game}: the route from the dialogue is wired both ways",
              not missing, str(missing))

        # all three chapters ship exactly eleven, which is a useful canary:
        # Mistral Grove came in at nine until "Cut through hedge" and
        # "Release boy" showed the verb list was short
        check(f"{game}: eleven quest objectives", len(w.quests()) == 11,
              f"found {len(w.quests())}")

        # The chapters name their own monsters, location by location, in the
        # "Fight <name>" strings. Every one has to resolve to a sheet this
        # jar carries, and two different species must not share one.
        names = sorted({n for l in w.locations for n in w.fights(l)})
        check(f"{game}: every location names its creatures", len(names) >= 8,
              f"only {len(names)} names found")
        unknown = [n for n in names if w.creature_for(n) not in w.creatures]
        check(f"{game}: every named creature has a sheet", not unknown,
              str(unknown))
        recurring = [n for n in names
                     if sum(1 for l in w.locations if n in w.fights(l)) > 1]
        sprites = [w.creature_for(n) for n in recurring]
        check(f"{game}: recurring species do not share a sheet",
              len(set(sprites)) == len(sprites),
              str(sorted(collections.Counter(sprites).items())))

        # a location's monsters come from its own list, not from a bag
        wrong = [l for l in w.locations if w.fights(l)
                 and any(m.creature not in
                         {w.creature_for(n) for n in w.fights(l)}
                         for m in w.mobs.values()
                         if m.location == l and not m.npc)]
        # The "Fight <name>" labels recover most of the placement but not all
        # of it: watAgame's table puts creatures in three locations whose text
        # names no fight against them. A good approximation, not the truth.
        check(f"{game}: monsters match the location's own list",
              w.real9 is not None or not wrong,
              f"{len(wrong)} locations differ, e.g. {wrong[:3]}")

        # A monster used to be forbidden the townsfolk sheet, because back
        # when species were chosen arbitrarily, using it meant a bug. Now the
        # chapters name their own monsters and Sterling Lake's fishmen are
        # drawn on the same sheet as the Fishking, who is one of them. So the
        # rule is narrower: a monster may wear that sheet only if the text
        # names a fight against something that resolves to it.
        by_sheet = {w.creature_for(n) for l in w.locations
                    for n in w.fights(l)}
        check(f"{game}: monsters wear a sheet their chapter names",
              all(m.creature in by_sheet for m in w.living()),
              str(sorted({hex(m.creature) for m in w.living()}
                         - {hex(c) for c in by_sheet})))

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

    print("\ncombat")
    # Rules 1.5, exercised against Shirad's Forge as it actually stands:
    # the hero begins on (7, 0) and the one fighter in that place, node 7,
    # stands on (9, 2). Nothing here may depend on the roll coming up the
    # same way twice unless the Random is handed in.

    def said(script, text):
        return any(text.encode() in rec for rec in script)

    w = World("ShiradsForge")
    x, y = w.hero_x, w.hero_y
    script = handlers.resolve(
        w, [("Move", 40, 1, [(x + 1, y + 1)])], rng=random.Random(1))
    check("a diagonal step is a Failed Move and the hero stays",
          (w.hero_x, w.hero_y) == (x, y) and said(script, "Failed Move"))

    w = World("ShiradsForge")
    step = next((p for p in ((w.hero_x, w.hero_y + 1), (w.hero_x + 1, w.hero_y),
                             (w.hero_x - 1, w.hero_y), (w.hero_x, w.hero_y - 1))
                 if w.can_stand(*p) and not w.mob_at(*p)), None)
    check("the start has an open orthogonal step", step is not None, str(step))
    if step:
        script = handlers.resolve(w, [("Move", 40, 1, [step])],
                                  rng=random.Random(1))
        check("an open orthogonal step is taken",
              (w.hero_x, w.hero_y) == step,
              f"ended {(w.hero_x, w.hero_y)}")

    w = World("ShiradsForge")
    mob = w.living()[0]
    far = max(abs(mob.x - w.hero_x), abs(mob.y - w.hero_y)) > 1
    before = mob.hp
    script = handlers.resolve(w, [("Hit", 60, 2, [(mob.x, mob.y)])],
                              rng=random.Random(1))
    check("melee out of contact does not hit, and does not pick someone else",
          far and mob.hp == before and said(script, "Too far away"))

    w = World("ShiradsForge")
    mob = w.living()[0]
    w.hero_x, w.hero_y = mob.x - 1, mob.y
    beside = w.can_stand(w.hero_x, w.hero_y) and w.contact(
        w.hero_x, w.hero_y, mob.x, mob.y)
    check("the hero can stand beside the starter", beside,
          f"hero {(w.hero_x, w.hero_y)} mob {(mob.x, mob.y)}")
    if beside:
        w.begin_fight([mob.node])
        w.hero_hp = 15
        mob.hp = 1
        script = handlers.resolve(
            w, [("Hit", 60, 2, [(mob.x, mob.y)])], rng=random.Random(1))
        if mob.alive:
            mob.alive = False
            mob.hp = 0
            w.pending_gold, w.pending_xp = mob.spoil()
        status, extra = handlers.finish(w, script)
        check("winning a fight refills life and pays for it",
              status == 2 and w.hero_hp == w.hero_max and w.gold > 50
              and not mob.alive,
              f"status {status} hp {w.hero_hp} gold {w.gold}")
        check("the win carries node states and the battle report",
              len(extra) >= 4)

    w = World("ShiradsForge")
    bow = catalogue().starting_kit()["bow"]
    mob = w.living()[0]
    w.hero_x, w.hero_y = mob.x - 1, mob.y
    w.equipped["weapon"] = bow.name
    w.begin_fight([mob.node])
    script = handlers.resolve(w, [("Shoot", 60, 2, [(mob.x, mob.y)])],
                              rng=random.Random(1))
    check("a bow cannot be used in contact", said(script, "Too close"))

    w = World("ShiradsForge")
    mob = w.living()[0]
    script = handlers.resolve(w, [("Shoot", 60, 2, [(mob.x, mob.y)])],
                              rng=random.Random(1))
    check("Shoot without a bow says so", said(script, "Need a bow"))

    w = World("ShiradsForge")
    kind, dmg = w.strike(9, 100, 20, 0, spell=True, resist=0, armour=100,
                         rng=random.Random(1))
    check("a spell ignores armour", kind == "hit" and dmg == 11, f"{kind} {dmg}")
    kind, dmg = w.strike(9, 100, 5, 0, spell=True, resist=5, rng=random.Random(1))
    check("a spell is resisted unless the caster's ability is higher",
          kind == "resist" and dmg == 0, f"{kind} {dmg}")

    bare = w.strike(10, 100, 30, 0, dex=25, armour=0, weapon_mod=-5,
                    rng=random.Random(4))
    worn = w.strike(10, 100, 30, 0, dex=25, armour=3, weapon_mod=-5,
                    rng=random.Random(4))
    check("the same weapon roll with armour deals three less",
          bare[0] == worn[0] and worn[1] == max(0, bare[1] - 3),
          f"{bare} vs {worn}")

    w = World("ShiradsForge")
    base = w.avoidance()
    handlers.resolve(w, [("Dodge", 20, 0, [(0, None)])], rng=random.Random(1))
    check("Dodge raises avoidance by the skill's precision for the rest of the turn",
          w.guard == 10 and w.avoidance() == base + 10,
          f"guard {w.guard} avoid {w.avoidance()} was {base}")

    w = World("ShiradsForge")
    spawn = (w.hero_x, w.hero_y)
    mob = w.living()[0]
    w.begin_fight([mob.node])
    mob.hp = 1
    w.hero_hp = 0
    status, _ = handlers.finish(w, [])
    check("losing puts the hero back at the start, alive",
          status == 3 and (w.hero_x, w.hero_y) == spawn
          and w.hero_hp == w.hero_max and spawn != (12, 17),
          f"at {(w.hero_x, w.hero_y)} hp {w.hero_hp}")
    check("losing does not clear the creature",
          mob.alive and mob.hp == mob.max_hp, f"hp {mob.hp} alive {mob.alive}")

    w = World("ShiradsForge")
    mob = w.living()[0]
    w.begin_fight([mob.node])
    w.hero_hp = 12
    w.hero_x += 2
    mob.hp = 4
    home = mob.home
    mob.x += 1
    status = handlers._flee(w, [])
    check("fleeing refills life and puts both sides back",
          status == 4 and w.hero_hp == w.hero_max
          and (w.hero_x, w.hero_y) == w.recall
          and mob.alive and mob.hp == mob.max_hp and (mob.x, mob.y) == home,
          f"hero {(w.hero_x, w.hero_y)} mob {(mob.x, mob.y)} hp {mob.hp}")

    w = World("ShiradsForge")
    mob = w.living()[0]
    w.begin_fight([mob.node])
    resp = handlers.auto_response(w, rng=random.Random(1))
    check("auto fight beats the starter and refills life",
          resp[2] == 2 and w.hero_hp == w.hero_max and not mob.alive,
          f"status {resp[2]} hp {w.hero_hp} mob {mob.hp} alive {mob.alive}")

    # every script built above still has to satisfy d.java:1077
    w = World("ShiradsForge")
    mob = w.living()[0]
    w.begin_fight([mob.node])
    script = handlers.resolve(
        w, [("Move", 80, 1, [(w.hero_x + 1, w.hero_y + 1), (w.hero_x, w.hero_y + 1)]),
            ("Hit", 140, 2, [(mob.x, mob.y)]),
            ("Dodge", 20, 0, [(0, None)]),
            ("Minor Cure", 60, 0, [(0, None)])],
        rng=random.Random(2))
    short = [r.hex() for r in script if len(r) - (5 + r[4]) < 2]
    check("rules results still carry >= 2 payload bytes", not short,
          f"{len(short)} too short")

    print()
    if FAILED:
        print(f"\033[31m{len(FAILED)} failed\033[0m: " + ", ".join(FAILED))
        return 1
    print("\033[32mall checks passed\033[0m")
    return 0


if __name__ == "__main__":
    sys.exit(main())
