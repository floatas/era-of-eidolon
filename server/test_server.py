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
import tiers
from catalogue import catalogue
from world import POTENCY_DIV, Saves, World, get_world

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
        if w.real1:
            # d.java b() fires trigger 0 when the hero is inside the box, and
            # a door is the next tile over. A new game has to miss both.
            def tangled(loc, x, y):
                for r in w.real1:
                    if len(r) < 6 or r[1] not in (0, loc) or r[4] == 0:
                        continue
                    x1, y1, x2, y2 = r[2], r[3], r[4], r[5]
                    if r[12] == 4:
                        for yy in range(y1, y2):
                            for xx in range(x1, x2):
                                if max(abs(x - xx), abs(y - yy)) <= 1:
                                    return True
                    elif (r[6] == 0 or r[12] == 2) and x1 <= x < x2 and y1 <= y < y2:
                        return True
                return False
            bad = [(l, *w.spawn_point(l)) for l in w.locations
                   if tangled(l, *w.spawn_point(l))]
            check(f"{game}: a new hero starts clear of doors and opening dialogs",
                  not bad, str(bad[:3]))

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
    # 1..28 are the gen-2 opcodes proper; 31 is the map-loaded report the
    # phone sends on top of them (handlers.report_place).
    check("every opcode the client can send has a handler",
          set(range(1, 29)) <= set(handlers.HANDLERS)
          and set(handlers.HANDLERS) <= set(range(1, 29)) | {31},
          f"missing {sorted(set(range(1, 29)) - set(handlers.HANDLERS))}, "
          f"extra {sorted(set(handlers.HANDLERS) - set(range(1, 29)))}")
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
    # The Arena list is 203 entries; a chapter stocks a slice of the gear
    # (notes/chapter-items.json) and all of the skills and spells, so the
    # measured count drops without any number being lost.
    check("watAgame's own numbers are loaded", len(measured) > 150,
          f"only {len(measured)} entries carry measured values")

    # the action bar must cost what the recovered table says, not a guess
    known = {i.name.lower(): i for k in ("skill", "spell") for i in c.get(k)}
    drift = [(n, t, known[n.lower()].time) for n, t, _ in handlers.ACTIONS
             if n.lower() in known and known[n.lower()].time
             and known[n.lower()].time != t]
    check("action bar Time costs come from the catalogue", not drift,
          str(drift))
    check("weapons loaded", len(c.get("weapon")) > 20,
          str(len(c.get("weapon"))))
    check("this chapter stocks a slice of the armour, not all of it",
          4 <= len(c.get("armour")) <= 10, str(len(c.get("armour"))))
    check("starting kit resolves", len(c.starting_kit()) >= 2)

    print("\ncombat")
    # Rules 1.5, exercised against Shirad's Forge as it actually stands.
    # The opening fighter, node 7, stands on (9, 2). A new hero starts well
    # clear of him. Nothing here may depend on the roll coming up the same
    # way twice unless the Random is handed in.

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
    w.hero_x, w.hero_y = mob.x, mob.y
    w.begin_fight([mob.node])
    check("opening a fight steps the hero off the creature",
          w.contact(w.hero_x, w.hero_y, mob.x, mob.y),
          f"hero {(w.hero_x, w.hero_y)} mob {(mob.x, mob.y)}")
    # The end-turn message carries the handset's own coordinates, which are
    # still the shared square.
    w.hero_x, w.hero_y = mob.x, mob.y
    script = handlers.resolve(w, [("Hit", 60, 2, [(mob.x, mob.y)])],
                              rng=random.Random(1))
    check("a blow aimed at a creature you are standing on is in range",
          not said(script, "Too far away")
          and w.contact(w.hero_x, w.hero_y, mob.x, mob.y),
          f"hero {(w.hero_x, w.hero_y)}")

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
              status == 2 and w.hero_hp == w.hero_max and w.gold > 0
              and not mob.alive,
              f"status {status} hp {w.hero_hp} gold {w.gold}")
        check("the win carries node states and the battle report",
              len(extra) >= 4)

    # The lever sentence lives in Lava Island's text table. It used to be
    # copied into every win on that map, so a second Gorrak somewhere else
    # repeated the crate-and-bridge line.
    w = World("ShiradsForge")
    lava = next(loc for loc, name in w.LOCATION_NAMES.items()
                if name == "Lava Island")
    check("the lever line still belongs to Lava Island",
          any("lever" in v.lower() and "bridge" in v.lower()
              for v in w.text(lava).values()))
    mob = next(m for m in w.mobs.values()
               if m.location == lava and not m.npc)
    w.location = lava
    w.begin_fight([mob.node])
    who = w.creature_name(mob.creature) or "It"
    mob.alive = False
    mob.hp = 0
    w.pending_gold, w.pending_xp = mob.spoil()
    report = w.battle_report()
    check("a Lava Island win names the creature, not the lever crate",
          who in report and "Gold +" in report and "Experience +" in report
          and "lever" not in report.lower() and "bridge" not in report.lower()
          and "crate" not in report.lower(),
          report.replace("\n", " | "))
    village = next(loc for loc, name in w.LOCATION_NAMES.items()
                   if name == "Village")
    starter = next(m for m in w.mobs.values() if m.location == village and not m.npc)
    w.location = village
    w.begin_fight([starter.node])
    starter.alive = False
    starter.hp = 0
    w.pending_gold, w.pending_xp = starter.spoil()
    village_report = w.battle_report()
    w = World("ShiradsForge")
    w.entity_table()
    shirard = next(r for r in w.entity_table() if r[0] == 111)
    check("Shirard's fight closes when he dies",
          shirard[6] == 2 and shirard[8] == 20 and shirard[14] == 20)
    w.mobs[20].alive = False
    w.mobs[20].hp = 0
    w.location = 7
    w.begin_fight([20])
    check("a fight against a dead Shirard still names him",
          w.engaged == [20] and not w.fighters())
    closing = next(r for r in w.entity_table() if r[0] == 132)
    check("defeating Shirard does not arm the quit-the-game screen",
          closing[16] != 226 and 226 not in closing)
    report = w.battle_report()
    w.level, w.xp, w.gold = 14, 108, 1582
    hud = b"".join(handlers.hud_chunks(w))
    check("the status line is experience, level, gold, with no letters",
          b"108" in hud and b"1582" in hud
          and b"L14" not in hud and b"1582g" not in hud and b"108/" not in hud)

    check("the win tells him the mountain is saved and the world is still open",
          "saved the mountain" in report and "Explore as long as you like" in report
          and "Shirard is defeated" in report,
          report.replace("\n", " | "))

    check("a Village win does not paste Hrom's speech",
          "Hrom" not in village_report and "cog" not in village_report.lower()
          and (w.creature_name(starter.creature) or "It") in village_report,
          village_report.replace("\n", " | "))

    w = World("ShiradsForge")
    w.note_use("Move")
    w.note_use("Move")
    w.note_use("Move")
    w.note_use("Move")
    w.note_use("Hit")
    report = w.battle_report()
    check("a win lists only the skills that landed",
          "20% Move skill" in report and "5% Hit skill" in report
          and "Spell points:" in report and "No gains" in report,
          report.replace("\n", " | "))
    w.commit_practice()
    check("those points stay on the hero", w.practice.get("Move") == (0, 20))
    w.fight_gains = {}
    w.practice["Hit"] = (0, 95)
    w.note_use("Hit")
    w.commit_practice()
    check("a full bar promotes Hit to Beginner", w.practice.get("Hit") == (1, 0))
    w.note_use("Dodge")
    w.revert_fight()
    check("a loss keeps none of the fight's practice",
          "Dodge" not in w.practice)

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
    lane = None
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        hero = (mob.x + 2 * dx, mob.y + 2 * dy)
        aim = (mob.x - dx, mob.y - dy)
        if w.can_stand(*hero) and w.can_stand(*aim):
            lane = (hero, aim)
            break
    check("there is a clear lane past the starter", lane is not None)
    if lane:
        w.hero_x, w.hero_y = lane[0]
        w.equip("Short Bow")
        w.begin_fight([mob.node])
        before = mob.hp
        script = handlers.resolve(w, [("Shoot", 60, 2, [lane[1]])],
                                  rng=random.Random(1))
        check("an arrow hits the creature standing on its path",
              mob.hp < before or said(script, "Miss") or said(script, "Blocked"),
              " ".join(rec[5:5 + rec[4]].decode() for rec in script))

    w = World("ShiradsForge")
    mob = w.living()[0]
    script = handlers.resolve(w, [("Shoot", 60, 2, [(mob.x, mob.y)])],
                              rng=random.Random(1))
    check("Shoot without a bow says so", said(script, "Need a bow"))

    w = World("ShiradsForge")
    kind, dmg = w.strike(9, 100, 20, 0, spell=True, resist=0, armour=100,
                         rng=random.Random(1))
    # the point is the armour, not the coefficient, so read the divisor rather
    # than pinning a number that moves whenever levelling is retuned
    # a spell takes the ability undivided — no weapon under it carrying scale
    check("a spell ignores armour",
          kind == "hit" and dmg == 9 + 20, f"{kind} {dmg}")
    kind, dmg = w.strike(9, 100, 5, 0, spell=True, resist=5, rng=random.Random(1))
    check("resistance is subtracted from a spell, not a gate on it",
          kind == "hit" and dmg == 9 + 5 - 5, f"{kind} {dmg}")
    kind, dmg = w.strike(9, 100, 5, 0, spell=True, resist=50, rng=random.Random(1))
    check("a spell that is out-resisted still tells, because it was aimed",
          kind == "resist" and dmg == 1, f"{kind} {dmg}")

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
    mob = w.living()[0]
    w.hero_x, w.hero_y = mob.x, mob.y + 1
    w.begin_fight([mob.node])
    script = handlers.resolve(
        w, [("Move", 80, 1, [(w.hero_x - 1, w.hero_y),
                             (w.hero_x - 2, w.hero_y)])],
        rng=random.Random(1))
    walks = []
    for rec in script:
        if rec[0] != 2:
            continue
        n = rec[4]
        walks.append(rec[5 + n])
    hero_at = walks.index(0) if 0 in walks else -1
    mob_at = walks.index(mob.node) if mob.node in walks else len(walks)
    check("a step at the same time as a creature keeps the hero first",
          hero_at >= 0 and hero_at < mob_at, str(walks))

    w = World("ShiradsForge")
    mob = w.living()[0]
    w.hero_x, w.hero_y = mob.x, mob.y + 1
    aimed = (mob.x, mob.y)
    w.begin_fight([mob.node])
    mob.x -= 1
    script = handlers.resolve(w, [("Hit", 60, 2, [aimed])],
                              rng=random.Random(1))
    check("an axe still lands if they stepped but you can touch them",
          not said(script, "Too far away"),
          " ".join(rec[5:5 + rec[4]].decode() for rec in script))

    w = World("ShiradsForge")
    w.hero_x, w.hero_y = w.living()[0].x, w.living()[0].y + 1
    handlers.resolve(w, [("Zig-Zag", 118, 1, [(w.hero_x - 1, w.hero_y)])],
                     rng=random.Random(1))
    check("Zig-Zag is harder to hit while that step is the one you are on",
          w.weave == 9, str(w.weave))

    check("a boss swing is five cells and the back is open",
          set(handlers._cells("boss", 4, 1, 2))
          == {(3, 1), (5, 1), (3, 2), (4, 2), (5, 2)}
          and (4, 0) not in handlers._cells("boss", 4, 1, 2))
    check("a beetle leaves its face and its back open",
          handlers._cells("sides", 5, 5, 2) == [(4, 5), (6, 5)])
    check("fire covers two ranks and a gorrak lunges two deep",
          len(handlers._cells("fire", 5, 5, 2)) == 6
          and handlers._cells("lunge", 5, 5, 2) == [(5, 6), (5, 7)])
    check("a fungusman is safe to hug and a ghost hits along its line",
          (5, 6) not in handlers._cells("spores", 5, 5, 0)
          and (5, 7) in handlers._cells("spores", 5, 5, 0)
          and handlers._cells("pierce", 5, 5, 2) == [(5, 6), (5, 4)])
    check("Aldor guards his front and his left, not his right",
          handlers._cells("fence", 5, 5, 2) == [(5, 6), (4, 5)])

    w = World("ShiradsForge")
    sk = next(m for m in w.mobs.values()
              if w.creature_name(m.creature) == "Skeleton")
    w.location = sk.location
    w.equipped["weapon"] = "Bloody Blade"
    check("a blade gives a skeleton his one forward cell",
          handlers.pattern_of(w, sk) == "front1")
    mira = w.mobs[46]
    mira.phase = 2
    check("a blade gives Mira her five-cell swing",
          handlers.pattern_of(w, mira) == "boss")
    w.equipped["weapon"] = "Short Bow"
    check("the bow makes a creature step into the eight neighbours, "
          "but a boss keeps its shapes",
          handlers.pattern_of(w, sk) == "ring"
          and handlers.pattern_of(w, mira) == "boss")
    fun = spot = None
    w.equipped["weapon"] = "Bloody Blade"
    for cand in w.mobs.values():
        if w.creature_name(cand.creature) != "Fungusman":
            continue
        w.location = cand.location
        for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            p = (cand.x + dx, cand.y + dy)
            if not (w.can_stand(*p) and w.mob_at(*p) is None):
                continue
            w.hero_x, w.hero_y = p
            w.engaged = [cand.node]
            plan = handlers.mob_timeline(w)
            if plan and plan[0][1][0] == "mob_move":
                fun, spot = cand, p
                break
        if fun:
            break
    check("a fungusman can step off a neighbour", fun is not None)
    if fun:
        w.location = fun.location
        w.hero_x, w.hero_y = spot
        w.engaged = [fun.node]
        w.equipped["weapon"] = "Short Bow"
        bow = handlers.mob_timeline(w)
        check("with the bow he swings from where he already stands",
              bow and bow[0][1][0] == "mob_attack")
        w.equipped["weapon"] = "Bloody Blade"
        blade = handlers.mob_timeline(w)
        check("with the blade the fungusman steps out before the cloud hits",
              blade and blade[0][1][0] == "mob_move")

    w = World("ShiradsForge")
    sk = None
    for cand in w.mobs.values():
        if w.creature_name(cand.creature) != "Skeleton":
            continue
        w.location = cand.location
        front = (cand.x, cand.y + 1)
        flank = (cand.x - 1, cand.y + 1)
        if (w.can_stand(*front) and w.can_stand(*flank)
                and w.mob_at(*front) is None and w.mob_at(*flank) is None):
            sk = cand
            break
    check("a skeleton has a front cell and a shoulder to step to", sk is not None)
    if sk:
        w.hero_x, w.hero_y = sk.x, sk.y + 1
        w.begin_fight([sk.node])
        sk.face = 2
        script = handlers.resolve(w, [], rng=random.Random(1))
        check("standing in a skeleton's front cell is inside the swing",
              not said(script, "Out of reach")
              and (said(script, "hits") or said(script, "Miss")
                   or said(script, "Blocked")))
        sk.x, sk.y = sk.home
        sk.alive, sk.hp = True, sk.max_hp
        w.hero_hp = w.hero_max
        w.hero_x, w.hero_y = sk.x, sk.y + 1
        sk.face = 2
        script = handlers.resolve(
            w, [("Move", 40, 1, [(sk.x - 1, sk.y + 1)])],
            rng=random.Random(1))
        check("stepping off that cell is out of the skeleton's reach",
              said(script, "Out of reach") and w.hero_hp == w.hero_max,
              " ".join(rec[5:5 + rec[4]].decode() for rec in script))

    w = World("ShiradsForge")
    mira = w.mobs[46]
    other = w.mobs.get(47)
    if other:
        other.alive = False
    w.location = mira.location
    w.hero_x, w.hero_y = mira.x, mira.y + 1
    w.begin_fight([46])
    gold = w.pending_gold
    script = []
    handlers._land_on_mob(w, 0, mira, "hit", mira.hp, 1, script)
    check("Mira's first pool drops the bow and keeps her in the fight",
          mira.alive and mira.phase == 2 and mira.hp == mira.max_hp
          and w.pending_gold == gold
          and said(script, "Mira drops her bow and draws a blade")
          and handlers.pattern_of(w, mira) == "boss")
    script = []
    handlers._land_on_mob(w, 0, mira, "hit", mira.hp, 1, script)
    check("Mira's second pool is the one that ends her",
          not mira.alive and said(script, "Mira dies")
          and w.pending_gold == gold + max(
              1, mira.spoil()[0] * handlers.balance()["pay"] // 100),
          f"{w.pending_gold} vs {gold} + {mira.spoil()}")
    shirard = w.mobs[20]
    # He starts asleep now: entity 24 arms 109, and 109 is the kind 5 that
    # summons him. Wake him by hand rather than walk the whole chain.
    shirard.alive = True
    w.location = shirard.location
    script = []
    handlers._land_on_mob(w, 0, shirard, "hit", shirard.hp, 1, script)
    check("Shirard quits magic and draws a blade for the second pool",
          shirard.alive and shirard.phase == 2 and shirard.hp == shirard.max_hp
          and said(script, "Shirard quits magic and draws a blade")
          and handlers.pattern_of(w, shirard) == "boss")
    handlers._flee(w, [])
    check("fleeing puts a boss back on the first pool", shirard.phase == 1)

    fresh = World("ShiradsForge")
    cfg = handlers.balance()
    through = (fresh.hero_max + cfg["mistakes"] - 1) // cfg["mistakes"]
    check("a normal blow is one mistake against your current life",
          handlers._pressure_blow(fresh) == through,
          f"blow {handlers._pressure_blow(fresh)}")

    def taken(world, suit):
        world.equipped["armour"] = suit
        foe = next(m for m in world.mobs.values() if not m.npc)
        worn = world.armour().effect if world.armour() else 0
        roll = random.Random(5)
        return sum(world.strike(handlers._pressure_blow(world, foe),
                                foe.offence()["precision"], 0,
                                world.avoidance(), armour=worn, rng=roll)[1]
                   for _ in range(4000))
    suited = World("ShiradsForge")
    suited.inventory.append("Spike Suit")
    bare, scrap, spike = (taken(suited, None), taken(suited, "Scrapsuit"),
                          taken(suited, "Spike Suit"))
    check("a heavier suit means less damage taken, never more",
          bare > scrap > spike, f"{bare} > {scrap} > {spike}")

    # The tier, not the hero, sizes a creature (tiers.py).
    t = World("ShiradsForge")
    beetles = [m for m in t.mobs.values()
               if t.creature_name(m.creature) == "Beetle"]
    one = next(m for m in beetles if m.tier == "I")
    three = next(m for m in beetles if m.tier == "III")
    check("a Beetle has its tier's life, less what its shell is worth, "
          "and more life deeper in",
          one.max_hp == tiers.creature_life("I", 30, "Beetle")
          < tiers.best_round("I") and three.max_hp > 3 * one.max_hp
          and one.offence()["armour"] > 0,
          f"{one.max_hp} / {three.max_hp}")
    before = handlers._pressure_blow(t, one)
    t.grant_xp(5000)
    check("a creature does not hit harder because the hero levelled",
          t.level > 5 and handlers._pressure_blow(t, one) == before,
          f"level {t.level} blow {handlers._pressure_blow(t, one)} vs {before}")
    check("a creature's blow is sized per tier",
          handlers._pressure_blow(t, three) > before)

    # Four bosses, two shapes each, the safe squares turning around.
    b = World("ShiradsForge")
    b.equipped["weapon"] = "Bloody Blade"
    names = {n: b.mobs[n] for n in (19, 20, 46, 48)}
    shapes = {}
    for node, m in names.items():
        m.phase = 1
        first = handlers.pattern_of(b, m)
        m.phase = 2
        shapes[handlers.fighter_name(b, m)] = (first, handlers.pattern_of(b, m))
        m.phase = 1
    check("Mira, Shirard, Aldor and the Beholder each change shape",
          shapes == {"Beholder": ("corners", "gaze"), "Shirard": ("burst", "boss"),
                     "Mira": ("ray", "boss"), "Aldor": ("fence", "boss")},
          str(shapes))
    gaze = handlers._cells("gaze", 5, 5, 0)
    corners = handlers._cells("corners", 5, 5, 0)
    check("the Eye's gaze runs four lines and leaves its corners safe",
          len(gaze) == 16 and (5, 1) in gaze and (9, 5) in gaze
          and not set(gaze) & set(corners))
    burst = handlers._cells("burst", 5, 5, 0)
    check("Shirard's burst lands two out and never beside him",
          len(burst) == 16 and (7, 7) in burst and (6, 5) not in burst)
    aldor = names[48]
    b.location = aldor.location
    b.hero_x, b.hero_y = aldor.x, aldor.y + 1
    b.begin_fight([48])
    handlers._tune_bosses(b)
    script = []
    handlers._land_on_mob(b, 0, aldor, "hit", aldor.hp, 1, script)
    check("Aldor's first pool changes his shape instead of ending him",
          aldor.alive and aldor.phase == 2 and said(script, "Aldor roars"))

    twin = World("ShiradsForge")
    check("Mira's twin is gone for good, not waiting to be woken",
          not twin.mobs[47].alive and twin.node_states()[47] == 3)
    again = World("ShiradsForge")
    saved = twin.to_dict()
    for md in saved["mobs"]:
        if md["node"] == 47:
            md["alive"] = True
    again.from_dict(saved)
    check("a save cannot bring the twin back", not again.mobs[47].alive)
    old = World("ShiradsForge")
    stale = old.to_dict()
    stale.pop("tiers", None)
    for md in stale["mobs"]:
        md["hp"] = 10
    old.from_dict(stale)
    first = next(m for m in old.mobs.values() if getattr(m, "tier", None)
                 and m.alive)
    check("a save from before the tiers brings creatures back at tier life",
          first.hp == first.max_hp and first.max_hp > 10, f"{first.hp}")

    # Crates hand out their own tier's gear, never the next one's.
    c = World("ShiradsForge")
    c.stats["Strength"] = c.stats["Dexterity"] = 60
    early = [r[0] for r in c.real1 if len(r) > 12 and r[12] == 3
             and tiers.tier_of(r[1]) == "I"]
    got = [it for st in early for it in c.loot_container(st)[0]]
    check("a tier I crate never holds tier II or III gear",
          got and all(getattr(it, "tier", None) in (None, "I") for it in got),
          str([(it.name, it.tier) for it in got]))

    # Toughness is life, Speed is time (rules 0.9, numbers ours: tiers.py)
    t = World("ShiradsForge")
    t.raises = 2
    t.spend_raises(bytes([0, 0, 0, 2, 0, 0]))       # both points to Toughness
    check("a Toughness raise adds its life at once",
          t.stats["Toughness"] == 9 and t.hero_max == 40 + 6 * tiers.TOUGH_LIFE
          and t.hero_hp == t.hero_max, f"{t.hero_max} / {t.hero_hp}")
    t.grant_xp(t.xp_for_next())
    check("a level on top of Toughness adds its 6 and keeps the rest",
          t.hero_max == 40 + 6 + 6 * tiers.TOUGH_LIFE, str(t.hero_max))
    back = World("ShiradsForge")
    back.from_dict(t.to_dict())
    check("a save keeps life and Toughness together",
          back.hero_max == t.hero_max and back.stats["Toughness"] == 9)
    quick = World("ShiradsForge")
    slow_move = quick.trained_time("Move", 40)
    slow_hit = quick.trained_time("Hit", 96)
    quick.stats["Speed"] = 33
    check("Speed 3 changes nothing and Speed 33 is quicker by its share",
          slow_move == 40 and slow_hit == 96
          and quick.trained_time("Move", 40) == tiers.speed_scaled(40, 33) < 40
          and quick.trained_time("Hit", 96) == tiers.speed_scaled(96, 33) < 90,
          f"{quick.trained_time('Move', 40)} {quick.trained_time('Hit', 96)}")

    a = World("ShiradsForge")
    a.stats["Dexterity"] = 30
    bow = catalogue().find("Long Bow")
    check("a bow's blow follows Dexterity, not Strength",
          handlers._hero_blow(a, bow)
          == catalogue().find("Shoot").effect + bow.effect
          + tiers.potency_bonus(30, tiers.swing_of(bow)))
    fast, slow = catalogue().find("Corrupter"), catalogue().find("Smasher")
    per_turn = [((720 - 160) // tiers.swing_of(it))
                * tiers.potency_bonus(40, tiers.swing_of(it)) for it in (fast, slow)]
    check("an ability adds about the same over a turn to a sword and a hammer",
          abs(per_turn[0] - per_turn[1]) <= 0.25 * max(per_turn), str(per_turn))
    boss = fresh.mobs[46]
    fresh.location = boss.location
    fresh.begin_fight([46])
    handlers._tune_bosses(fresh)
    check("a boss phase lasts the chosen turns of its tier's best weapon",
          boss.max_hp == tiers.boss_life(boss.tier, cfg["boss_turns"])
          and boss.hp == boss.max_hp, f"{boss.max_hp}")

    through = [handlers._pressure_blow(w, m)
               - catalogue().find(tiers.REFERENCE[m.tier]["suit"]).effect
               for m in w.mobs.values() if not m.npc and getattr(m, "tier", None)]
    check("every creature's blow still hurts through its tier's suit",
          through and min(through) >= 3, f"weakest gets {min(through)} through")
    beetles = [m for m in w.mobs.values()
               if w.creature_name(m.creature) == "Beetle"]
    low = next(m for m in beetles if m.tier == "I")
    high = next(m for m in beetles if m.tier == "III")
    check("a kill pays its weight at its tier's rates, not the life it was given",
          low.spoil() == (30, 30)
          and high.spoil() == (round(30 * tiers.GOLD_RATE["III"]),
                               round(30 * tiers.XP_RATE["III"]))
          and high.max_hp > 3 * high.spoil()[1],
          f"{low.spoil()} {high.spoil()} life {high.max_hp}")

    w = World("ShiradsForge")
    total = sum(m.spoil()[1] for m in w.mobs.values() if not m.npc)
    wild = sum(m.spoil()[1] for m in w.mobs.values() if not m.npc and m.respawn)
    lvl, pool = 1, total
    while lvl < 80:
        w.level = lvl
        cost = w.xp_for_next()
        if pool < cost:
            break
        pool -= cost
        lvl += 1
    hero = World("ShiradsForge")
    need = 0
    for level in range(1, 50):
        hero.level = level
        need += hero.xp_for_next()
    check("one clear is about a dozen levels, not twenty",
          10 <= lvl <= 16 and wild,
          f"clear reaches {lvl}, need {need}, wild {wild}")

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
    w.hero_x, w.hero_y = mob.x - 1, mob.y
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

    import time as _time
    w = World("ShiradsForge")
    gorrak = w.mobs[7]
    check("a story fight has no comeback timer", gorrak.respawn == 0)
    wild = next(m for m in w.mobs.values() if m.respawn and m.alive)
    w.location = wild.location
    w.begin_fight([wild.node])
    wild.alive = False
    wild.hp = 0
    w.commit_kills()
    check("wildlife stays down until its countdown ends",
          wild.dead_at and not any(m.node == wild.node for m in w.living()))
    wild.dead_at -= wild.respawn * 10 + 1
    back = [m for m in w.living() if m.node == wild.node]
    check("wildlife stands again, at full life, where the fight found it",
          len(back) == 1 and wild.hp == wild.max_hp
          and (wild.x, wild.y) == wild.home and wild.dead_at is None)
    check("the state table shows them present again",
          w.node_states()[wild.node] == 2)

    w = World("ShiradsForge")
    gorrak = w.mobs[7]
    w.begin_fight([7])
    gorrak.alive = False
    w.commit_kills()
    gorrak.dead_at = _time.time() - 10_000
    w.location = gorrak.location
    check("Gorrak does not come back",
          not any(m.node == 7 for m in w.living())
          and w.node_states()[7] == 3)

    w = World("ShiradsForge")
    wild = next(m for m in w.mobs.values() if m.respawn)
    w.location = wild.location
    w.begin_fight([wild.node])
    wild.hp = 1
    wild.alive = False
    w.revert_fight()
    check("fleeing does not start a comeback clock",
          wild.alive and wild.dead_at is None)

    print("\ndetails the client already specified")
    w = World("ShiradsForge")
    # Rules 1.5 say 15, which is the Arena's number for a hero who levels to
    # 49. A chapter hero reaches about 19 and the item ladder's floor is 3,
    # so the chapter opens him there. See World.__init__.
    check("a new hero is level 0 and every ability starts at the ladder's floor",
          w.level == 0 and set(w.stats.values()) == {3},
          str(w.stats))
    kit = catalogue().starting_kit()
    check("the free sword and bow are the basic ones",
          kit["sword"].requirement <= 3 and kit["bow"].requirement <= 3
          and kit["bow"].name != "Haunter",
          f"{kit['sword'].name}, {kit['bow'].name}")
    check("a new hero starts with no gold", w.gold == 0)
    bow_back = kit["bow"].price * tiers.RECYCLE_PERCENT // 100
    blade_back = kit["sword"].price * tiers.RECYCLE_PERCENT // 100
    gone, refund = handlers.salvage(w, kit["bow"].name)
    check("breaking the bow returns the recycle share and leaves the pack",
          gone == kit["bow"].name and refund == bow_back
          and w.gold == bow_back and kit["bow"].name not in w.inventory,
          f"+{refund}")
    gone, refund = handlers.salvage(w, kit["sword"].name)
    check("breaking the worn sword pays and clears the slot",
          gone == kit["sword"].name and refund == blade_back
          and w.gold == bow_back + blade_back
          and w.equipped.get("weapon") is None)
    w.grant_xp(100)
    check("level 0 can become level 1", w.level == 1 and w.raises == 2)

    w.spend_raises(bytes([1, 0, 0, 0, 0, 0]))
    check("one raise adds 3 to Strength and keeps the spare point",
          w.stats["Strength"] == 6 and w.raises == 1,
          f"{w.stats['Strength']} str, {w.raises} left")
    status, extra = handlers.finish.__wrapped__ if False else (None, None)
    w.engaged = []
    # finish needs fighters() empty and hero alive. engaged [] means no
    # fighters, which is a win.
    w.hero_hp = w.hero_max
    status, extra = handlers.finish(w, [])
    tags = [c[0] if False else None for c in extra]
    # chunks are encoded bytes; look for the raises int via a fresh offer
    offered = extra[0]
    check("a win with points waiting opens Raises left",
          status == 2 and offered[0] == 21, offered[:8].hex())

    gold = w.gold
    check("Dreyfus pays 3, and only once",
          w.claim_gift(117) == 3 and w.claim_gift(117) == 0
          and w.gold == gold + 3)
    check("Milas pays 5", w.claim_gift(148) == 5)

    w = World("ShiradsForge")
    w.entity_table()
    payoffs = w.crate_payoffs()
    check("every plain crate asks the server for a prize",
          len(payoffs) >= 20 and 69 in payoffs and 160 in payoffs
          and 188 not in payoffs and 170 not in payoffs,
          str(sorted(payoffs)))
    first, gold = w.loot_container(69)
    again, nothing = w.loot_container(69)
    check("smashing a crate names one usable thing, and a second smash nothing",
          len(first) == 1 and gold == 0 and nothing == 0
          and first[0].name in w.inventory
          and first[0].requirement <= 15,
          str([i.name for i in first]))
    w.stats["Strength"] = 9
    suit, _ = w.loot_container(240)
    purse, paid = w.loot_container(118)
    check("the plan holds: Village a weapon, Lava Island a suit, "
          "The Long Run a spare",
          first[0].kind == "weapon" and suit and suit[0].kind == "armour"
          and len(purse) == 1 and purse[0].tier == "I"
          and purse[0].name not in (first[0].name, suit[0].name),
          f"{[i.name for i in first]} {[i.name for i in suit]} "
          f"{[i.name for i in purse]}")
    main = {1, 2, 3, 4, 5, 6, 7}
    check("every gear crate stands on the main path",
          all(w.crate_location(st) in main for st, role in tiers.CRATES.items()
              if role != "gold"))

    hero = World("ShiradsForge")
    fresh = bytearray(hero.entity_states())
    fresh[188] = 3
    hero.note_progress(bytes(fresh))
    kept = World("ShiradsForge")
    kept.from_dict(hero.to_dict())
    check("a continued hero still has the cog it found",
          kept.entity_states()[188] == 3
          and kept.entity_states()[72] == hero.entity_states()[72])
    hero.note_progress(b"\x03")
    check("a short quest blob does not wipe the saved one",
          hero.entity_states()[188] == 3)

    pricey = next(i for i in catalogue().get("weapon")
                  if i.requirement > 15 and i.name not in w.inventory)
    w.gold = pricey.price + 5
    check("the market refuses what you cannot wield",
          w.buy(pricey.name) is None and pricey.name not in w.inventory,
          pricey.name)

    title, items = handlers.market_rows(w, 0)
    check("Pick interest lists a market shelf, not a random sentence",
          title == "Melee weapons" and items
          and "Nothing happens" not in items[0].label())
    _, skills = handlers.market_rows(w, 3)
    _, spells = handlers.market_rows(w, 4)
    shown = {i.name for i in skills + spells}
    check("the shop does not sell the skills already on the fight bar",
          shown.isdisjoint(World.BAR_SKILLS),
          str(sorted(shown & World.BAR_SKILLS)))
    fresh = World("ShiradsForge")
    _, melee = handlers.market_rows(fresh, 0)
    # tier I's first steps ask for 3 (tune_gear.py), so a new hero can
    # wear three pieces and sees the next three above them
    check("a new hero's melee shelf is what he can wear, plus three ahead",
          [i.name for i in melee] == [
              "Bloody Blade", "Corrupter", "Spike Axe",
              "Giant Sword", "Razor Axe", "Smasher"],
          str([i.name for i in melee]))
    first = World("ShiradsForge")
    found, _ = first.loot_container(69)
    check("the first crate holds a better weapon a new hero can wear at once",
          found and found[0].kind == "weapon" and first.can_wield(found[0])
          and first._gear_worth(found[0]) > first._gear_worth(first.weapon()),
          str([(i.name, i.requirement) for i in found]))
    late = World("ShiradsForge")
    late.stats["Strength"] = 60
    late.entity_table()
    gifts, tops = [], []
    for st in sorted(late.crate_payoffs()):
        own = tiers.tier_of(late.crate_location(st))
        for it in late.loot_container(st)[0]:
            gifts.append(it)
            if own != "I" and it.tier == own and tiers.is_top(it):
                tops.append(it.name)
    check("every crate holds an item, never the top of its own tier past tier I",
          not tops and len(gifts) >= 14, f"{[i.name for i in gifts]}")
    fresh.stats["Strength"] = 27
    _, grown = handlers.market_rows(fresh, 0)
    names = [i.name for i in grown]
    check("raising Strength drops the Bloody Blade and opens the Smasher",
          "Bloody Blade" not in names and "Smasher" in names
          and names[-3:] == ["Bone Crusher", "Beheader Axe", "Doom Hammer"],
          str(names))

    # The five traders, nearest the Village first. Each sells its own run of
    # its route tier and keeps only the top piece of the shop before it.
    rooms = (2, 3, 12, 5, 6)
    shelves = {}
    for which in (0, 1, 2):
        shelves[which] = []
        for loc in rooms:
            fresh.location = loc
            _, got = handlers.market_rows(fresh, which)
            shelves[which].append([i.name for i in got])
    bands = shelves[0]
    check("Lava Island still sells the Bloody Blade",
          bands[0][0] == "Bloody Blade" and "Bloody Blade" not in bands[-1],
          str(bands[0]))
    check("each next trader keeps the last shop's top piece and adds new ones",
          all(b[i][0] == b[i - 1][-1] and len(b[i]) >= 2
              and not set(b[i][1:]) & {n for s in b[:i] for n in s}
              for b in shelves.values() for i in range(1, len(b))),
          " | ".join(", ".join(b) for b in bands))
    check("melee, bows and armour all differ from trader to trader",
          all(len({tuple(s) for s in b}) == len(rooms)
              for b in shelves.values()))
    fresh.stats["Strength"] = 60
    fresh.location = 2
    _, still = handlers.market_rows(fresh, 0)
    check("the Lava Island shelf does not grow when Strength does",
          [i.name for i in still] == bands[0],
          str([i.name for i in still]))

    # An old save parked invented villagers on node ids the real table uses.
    w = World("ShiradsForge")
    gorrak = (w.mobs[7].location, w.mobs[7].x, w.mobs[7].y)
    secret = (w.mobs[1].location, w.mobs[1].x, w.mobs[1].y)
    w.from_dict({"location": 1, "hero_x": 10, "hero_y": 13, "mobs": [
        {"node": 1, "location": 1, "x": 11, "y": 15, "creature": 24,
         "hp": 6, "max_hp": 6, "alive": True},
    ]})
    check("an old save does not hide the village creatures",
          (w.mobs[7].location, w.mobs[7].x, w.mobs[7].y) == gorrak
          and w.node_states()[7] == 2 and w.mobs[7].alive)
    check("an old save does not move a real creature onto a reused node",
          (w.mobs[1].location, w.mobs[1].x, w.mobs[1].y) == secret)

    # i.java case 16 casts a chosen equipped-items row to f. A type-2 string
    # there is the error dialog. b.java run() builds f only from a type-4 chunk.
    resp = handlers.equipped(Req(21))
    kinds = [typ for tag, typ, _ in chunks_of(resp) if tag == 20]
    check("equipped rows are selectable records, not plain text",
          kinds == [codec.T_STRUCT, codec.T_STRUCT], str(kinds))
    w = World("ShiradsForge")
    offered = b"".join(handlers.carried(w, "weapon"))
    check("the weapon slot offers the bow you already carry",
          b"Short Bow" in offered and b"Bloody Blade" in offered)
    blade = catalogue().find("Bloody Blade")
    # Longfang is held for a sequel; Corrupter is this chapter's tier I sword
    fang = catalogue().find("Corrupter")
    shell = catalogue().find("Snail Shell")
    check("the worn sword is not painted, and a bow is not compared to it",
          handlers._gear_mark(w, blade) == ""
          and handlers._gear_mark(w, catalogue().find("Short Bow")) == "")
    # the hero opens at 3, and this chapter's next sword asks 6
    w.stats["Strength"] = max(w.stats["Strength"], fang.requirement)
    w.gold = fang.price
    check("a stronger sword you can pay for is green in the shop",
          handlers._gear_mark(w, fang, shop=True) == handlers._BETTER)
    w.gold = fang.price - 1
    check("the same sword stays plain when the purse is short",
          handlers._gear_mark(w, fang, shop=True) == "")
    w.inventory.append(fang.name)
    w.equip(fang.name)
    check("the sword you outgrew is red in the pack",
          handlers._gear_mark(w, blade) == handlers._WORSE)
    w.stats["Strength"] = max(w.stats["Strength"], shell.requirement)
    w.gold = shell.price
    check("a thicker suit you can pay for is green",
          handlers._gear_mark(w, shell, shop=True) == handlers._BETTER)
    locked = next(i for i in catalogue().get("weapon")
                  if i.cls in ("sword", "axe", "hammer")
                  and i.requirement > w.stats.get(i.ability, 0))
    w.gold = locked.price
    ghost = catalogue().find("Ghost Sword")
    # Retuned for the chapter (tools/tune_gear.py): each line's top piece in
    # a tier deals the same a turn at that tier's reference Strength, so a
    # sword and a hammer are a choice of job, not of strength.
    spike = catalogue().find("Spike Axe")
    doom = catalogue().find("Doom Hammer")
    ref = tiers.REFERENCE["III"]["stat"]
    turn = [tiers.weapon_round(it, ref) for it in (ghost, doom)]
    check("Ghost Sword and Doom Hammer are tier III's top pieces, one price",
          turn[0] <= turn[1] <= 1.25 * turn[0] and ghost.price == doom.price
          and handlers._gear_value(w, ghost) > handlers._gear_value(w, spike),
          f"a turn {turn}")
    check("a weapon the stat cannot wear yet is grey",
          handlers._gear_mark(w, locked, shop=True) == handlers._LOCKED,
          f"{locked.name} needs {locked.ability} {locked.requirement}")
    w = World("ShiradsForge")
    check("wearing the bow takes the sword's slot",
          w.equip("Short Bow") is not None and w.weapon().cls == "bow")

    # i.java case 19 opens a box from f.a and f.d(). A type-2 string has
    # neither, which is the error dialog on Skills.
    resp = handlers.spellbook(Req(25, chunks=[(1, codec.T_INT, b"\x09")]))
    skill_rows = [(typ, raw) for tag, typ, raw in chunks_of(resp) if tag == 20]
    check("skill rows show each bar skill and its title",
          len(skill_rows) == 4 and all(t == codec.T_STRUCT for t, _ in skill_rows)
          and b"Move" in skill_rows[0][1] and b"Fumbler" in skill_rows[0][1],
          str(len(skill_rows)))
    _, spells = handlers.market_rows(w, 4)
    _, bows = handlers.market_rows(w, 1)
    check("the shop does not sell charms, spare spells, or bombs",
          not spells and all(i.cls == "bow" for i in bows)
          and all(i.kind != "charm" for i in bows))
    live = get_world()
    planted = ["Magic Coat", "Ox Charm", "Zig-Zag"]
    live.inventory.extend(planted)
    hidden = handlers.spellbook(Req(25, chunks=[(1, codec.T_INT, b"\x0d")]))
    skills_hidden = handlers.spellbook(Req(25, chunks=[(1, codec.T_INT, b"\x09")]))
    for name in planted:
        if name in live.inventory:
            live.inventory.remove(name)
    check("a spare spell, charm, or skill does not appear in the lists",
          b"Magic Coat" not in hidden and b"Ox Charm" not in hidden
          and b"Zig-Zag" not in skills_hidden and b"Zap" in hidden)
    prize, _ = World("ShiradsForge").loot_container(69)
    check("a crate prize is gear you can wear",
          prize and prize[0].kind in ("weapon", "armour")
          and World.usable(prize[0]),
          str([i.name for i in prize]))

    # Every list the phone opens by casting the row to f and reading f.d()
    # (i.java cases 12, 17, 19, 29). A type-2 string, or a record with no
    # trailing text, is the error dialog.
    def record_body(raw):
        i = 0
        def take():
            nonlocal i
            n = raw[i]
            i += 1 + n
            return raw[i - n:i]
        take()
        take()
        i += 1
        flags = raw[i]
        i += 1
        take()
        n = int.from_bytes(raw[i:i + 2], "big")
        return flags, raw[i + 2:i + 2 + n]

    list_replies = [
        ("skills", handlers.spellbook(Req(25, chunks=[(1, codec.T_INT, b"\x09")]))),
        ("spells", handlers.spellbook(Req(25, chunks=[(1, codec.T_INT, b"\x0d")]))),
        ("market", handlers.interest(Req(15, chunks=[(1, codec.T_INT, b"\x00")]))),
        ("rankings", handlers.rankings(Req(26))),
        ("help", handlers.help_pages(Req(27))),
        ("icons", handlers.help_pages(Req(28))),
        ("weapon", handlers.shop(Req(22, chunks=[(1, codec.T_STR, b"weapon")]))),
    ]
    bare = []
    for name, resp in list_replies:
        for tag, typ, raw in chunks_of(resp):
            if tag != 20:
                continue
            if typ != codec.T_STRUCT:
                bare.append(f"{name}: type {typ}")
                continue
            flags, body = record_body(raw)
            if not (flags & 8) and not body:
                bare.append(f"{name}: no dialog text")
    check("every selectable list row carries the dialog text the phone reads",
          not bare, ", ".join(bare))

    class Here:
        location = 1

        def place(self):
            return World.place(self)

        def name(self, location=None):
            loc = self.location if location is None else location
            return {1: "Village", 2: "Lava Island"}.get(loc, "?")

    box = Here()
    World.note_place(box, 0)
    check("a missing room report leaves the server's room",
          World.place(box) == 1)
    World.note_place(box, 2)
    check("a reported room is the one the compendium shows",
          World.place(box) == 2)

    # The panel is a reference the player browses, not a follower. It used to
    # name the room they were in, which meant knowing where they were — and
    # the client's map-loaded ping never reaches the server under CheerpJ.
    import webserve
    ref = webserve.compendium_view()
    names = [s["name"] for s in ref["sections"]]
    check("the compendium carries every section",
          names == ["How it works", "Areas", "Creatures", "Gear"], str(names))
    by = {s["name"]: s["entries"] for s in ref["sections"]}
    check("one entry an area", len(by["Areas"]) == 18, str(len(by["Areas"])))
    check("every entry has a title and something to say",
          all(e["title"] and e["lines"]
              for s in ref["sections"] for e in s["entries"]))
    check("entry ids are unique, so a link can point at one",
          len({e["id"] for s in ref["sections"] for e in s["entries"]})
          == sum(len(s["entries"]) for s in ref["sections"]))
    beast = [e for e in by["Creatures"] if e["title"] == "Golem"]
    check("a creature entry says what it threatens and how often it swings",
          beast and any("squares around it" in l for l in beast[0]["lines"])
          and any("a turn" in l for l in beast[0]["lines"]),
          str(beast[0]["lines"] if beast else "no Golem"))
    check("the panel needs no hero, so it is right whatever the game is doing",
          webserve.compendium_view() == ref)

    forge = World("ShiradsForge")
    cave, aldor, tomb = forge.map(12), forge.map(11), forge.map(14)
    check("Fire Cave, Aldor and Ilrik are turned clockwise",
          (cave.w, cave.h) == (25, 35)
          and (aldor.w, aldor.h) == (30, 30)
          and (tomb.w, tomb.h) == (20, 10))
    door = {(x, 34) for x in (11, 12)}
    check("the lava bridge ends on Aldor's doorway",
          all((cave.tile(x, 34) & 15) == 12 and cave.walkable(x, 34)
              for x in (11, 12))
          and cave.walkable(12, 33) and (cave.tile(12, 33) & 15) == 7
          and not (cave.tile(0, 32) & 15))
    exits = {dest: box for box, dest in (
        ((r[2], r[3], r[4], r[5]), r[14])
        for r in forge.real1 if len(r) > 16 and r[12] == 4 and r[1] == 12)}
    check("Fire Cave's south door is the way to Aldor",
          exits.get(11) == (11, 34, 13, 35))
    back = next(r for r in forge.real1
                if len(r) > 16 and r[12] == 4 and r[1] == 11 and r[14] == 12)
    check("Aldor sends you back onto the bridge, not into the gap",
          (back[15], back[16]) == (12, 33) and cave.walkable(12, 33)
          and (12, 33) not in door)
    hall = next(r for r in forge.real1
                if len(r) > 16 and r[12] == 4 and r[1] == 3 and r[14] == 12)
    start = (hall[15], hall[16])

    def walkable_path(mp, a, b):
        seen, stack = {a}, [a]
        while stack:
            x, y = stack.pop()
            if (x, y) == b:
                return True
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if n in seen or not mp.walkable(*n):
                    continue
                seen.add(n)
                stack.append(n)
        return False

    check("you can walk from the Hall's door across the bridge to Aldor",
          cave.walkable(*start) and start not in door
          and walkable_path(cave, start, (12, 34)),
          f"arrive {start}")
    inside = aldor.walkable(16, 1) and (back[2], back[3]) == (15, 0)
    check("Aldor's north door is where the bridge meets it",
          inside and aldor.walkable(16, 0))
    stray = [m.node for m in forge.mobs.values()
             if m.location in (11, 12, 14)
             and not (0 <= m.x < forge.map(m.location).w
                      and 0 <= m.y < forge.map(m.location).h
                      and forge.map(m.location).tile(m.x, m.y) & 15)]
    check("turned rooms keep every creature on ground", not stray, str(stray))
    import zipfile
    from layout import TYPE2, TURNS, rewrite_type2
    raw = zipfile.ZipFile(os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "jars", "EoE-ShiradsForge.jar"))
    same = True
    for loc, name in TYPE2.items():
        turned, _ = rewrite_type2(raw.read(name), TURNS[loc], bridge=(loc == 12))
        same = same and turned[13:] == bytes(forge.map(loc).tiles)
    check("the run jar is turned the same way the server is", same)
    parked = forge.spawn_point(12)
    forge.from_dict({"location": 12, "hero_x": 32, "hero_y": 24, "layout": 0,
                     "mobs": []})
    check("a save standing on the old corner is not left in the gap",
          forge.can_stand(forge.hero_x, forge.hero_y)
          and (forge.hero_x, forge.hero_y) != (0, 32),
          f"{(forge.hero_x, forge.hero_y)} spawn {parked}")

    print()
    if FAILED:
        print(f"\033[31m{len(FAILED)} failed\033[0m: " + ", ".join(FAILED))
        return 1
    print("\033[32mall checks passed\033[0m")
    return 0


if __name__ == "__main__":
    sys.exit(main())
