#!/usr/bin/env python3
"""Play Shirad's Forge on the phone client, start to finish, and say what
happened.

    tools/harness/playthrough.py                play until the ending
    tools/harness/playthrough.py --rooms 3      stop after the third room
    tools/harness/playthrough.py --verbose      every harness exchange

autoplay.py plays the server's fight code without a phone. This plays the
real client under MicroEmulator (tools/harness/meh.sh in its interactive
mode) against the relay on :8080, the way a person would: it walks by the
phone's own map, opens the phone's "Choose action" list and picks from it,
takes every fight on Auto fight, spends its raises, and reads every dialog.
So doors, triggers, quest switches, crate patches, creatures waking and the
ending are the phone's own. What it decides, it decides from the recovered
tables (the same ones the server sends the phone) and from what the phone
says is live.

Needs the relay running on its own save file, so a run never touches the
heroes of the web game:
    (cd server && EOE_SAVES=/tmp/harness-saves.json python3 -u relay.py 8080 &)
and the same EOE_SAVES here: whether a fight was won is read from the
hero's kill count in that save, not guessed from the phone's dialogs.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "server"))

import handlers           # noqa: E402
import tiers              # noqa: E402
from world import World   # noqa: E402

MEH = os.path.join(HERE, "meh.sh")
JAR = os.path.join(ROOT, "run", "EoE-ShiradsForge.jar")
MAP, MENU, RAISES, ADD, ACTIONS, ENTERING = 10, 8, 14, 15, 32, 36
SLOTS, SLOT_ITEMS, ITEM = 16, 17, 18          # Hero info > Equipped items
LOCKED = handlers._LOCKED                     # grey: the stat is not there yet
LINE = ("sword",)                             # the build: a swordsman
# two of every three raise points to Strength, the third to Dexterity; the
# raise screen lists the abilities in the client's z[] order
STAT_ORDER = ("Strength", "Intelligence", "Dexterity", "Toughness", "Willpower", "Speed")
ENDING = "Shirard's Forge is complete"
# A new hero every run: a name belongs to one account, and each run's phone
# is a new account.
HERO = "Pil" + "".join(chr(97 + int(time.time() * 10) // 26 ** i % 26) for i in range(5))
SAVES = os.environ.get("EOE_SAVES") or os.path.join(ROOT, "server", "saves", "game.json")


def saved():
    """The hero as the server last saved him."""
    try:
        with open(SAVES) as fh:
            return json.load(fh)["heroes"][f"ShiradsForge:{HERO}"]
    except (OSError, ValueError, KeyError):
        return {}


def kills():
    return saved().get("kills", 0)


class Phone:
    """One MicroEmulator session, driven a line at a time."""

    def __init__(self, verbose=False, rms="memory"):
        env = dict(os.environ, MEH_RMS=rms)
        self.p = subprocess.Popen([MEH, JAR, "-"], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  text=True, bufsize=1, env=env)
        self.verbose = verbose
        self.said = []          # every dialog the harness closed, in order
        self.read()

    def read(self):
        lines = []
        for line in self.p.stdout:
            line = line.rstrip("\n")
            if line == "MEH ready":
                return lines
            lines.append(line)
            if line.startswith("SAID "):
                self.said.append(line[5:])
            if self.verbose:
                print("   |", line[:200])
        raise RuntimeError("the emulator stopped:\n" + "\n".join(lines[-20:]))

    def do(self, steps):
        if self.verbose:
            print("  >", steps)
        self.p.stdin.write(steps + "\n")
        self.p.stdin.flush()
        return self.read()

    def state(self):
        for line in reversed(self.do("state")):
            if line.startswith("STATE "):
                d = dict(re.findall(r"(\w+)=([^ ]+)", line))
                items = re.search(r"items=\[(.*)\]", line)
                d["items"] = items.group(1).split(", ") if items else []
                text = re.search(r"text=(.*)$", line)
                d["text"] = text.group(1) if text else ""
                return d
        return {}

    def states(self, ids):
        out, near = {}, 0
        for chunk in range(0, len(ids), 60):
            for line in self.do("states:" + "/".join(map(str, ids[chunk:chunk + 60]))):
                if line.startswith("STATES"):
                    for k, v in re.findall(r"(\d+)=(-?\d+)", line.split("nearby")[0]):
                        out[int(k)] = int(v)
                    near = int(re.search(r"nearby-actions=(-?\d+)", line).group(1))
        return out, near

    def nodes(self):
        """node id -> (location, state), from the phone's creature table."""
        out = {}
        for line in self.do("entities"):
            m = re.match(r"\s+node (\d+) loc=(\d+) state=(-?\d+)", line)
            if m:
                out[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
        return out

    def where(self):
        """node id -> (x, y) where the phone is drawing it now."""
        out = {}
        for line in self.do("where"):
            m = re.match(r"WHERE (\d+) (-?\d+) (-?\d+)", line)
            if m:
                out[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
        return out

    def close(self):
        try:
            self.p.stdin.write("quit\n")
            self.p.stdin.flush()
            self.p.wait(timeout=10)
        except Exception:
            self.p.kill()


class Player:
    def __init__(self, phone, log):
        self.phone = phone
        self.log = log
        self.w = World("ShiradsForge")
        self.rows = {r[0]: r for r in self.w.entity_table()}
        self.creatures = {r[0]: r for r in self.w.real9}
        self.split = 0
        self.tried = {}
        self.fights = []
        self.dialogs = []
        self.finished = False
        self.rooms = []
        self.walled = set()     # doors in this room the hero cannot walk to
        self.raised = True      # something new may be wearable
        self.worn = {}

    # -- reading the tables ------------------------------------------------

    def label(self, r):
        key = int.from_bytes(bytes(r[7:9]), "big")
        return self.w.text(r[1]).get(key, "")

    def box(self, r):
        return tuple(r[2:6])

    def exits(self):
        """state id -> destination, for every doorway."""
        return {sid: r[14] for sid, r in self.rows.items() if len(r) > 14 and r[12] == 4}

    # -- getting back to the map -------------------------------------------

    def settle(self, limit=120, here=None):
        """Answer whatever the phone put up until it is back on the map. A
        fight offered on the way (a creature noticed us) is fought on Auto
        and recorded like any other."""
        fight, said, before = None, [], kills()
        for _ in range(limit):
            self.heard()
            st = self.phone.state()
            u = int(st.get("u", MAP))
            if u == MAP and st.get("inCombat") == "true":
                self.phone.do("wait:1000")        # the fight plays out on the map
                continue
            if u == MAP:
                if fight is not None:
                    won = kills() > before
                    self.fights.append((fight, won))
                    self.log(f"      fight {'won' if won else 'LOST'}")
                return st
            if st.get("text"):
                text = st["text"].replace("|", " / ")
                self.dialogs.append(text)
                said.append(text)
                self.log(f"      says: {text[:150]}")
                if ENDING in st["text"]:
                    self.finished = True
                    self.log("      ENDING: " + text[text.index(ENDING):][:300])
            if u == ENTERING:
                fight = self.w.name(int(st.get("location", 0) or 0)) if st.get("location") else "?"
                self.phone.do("key:-6,wait:1500")          # Auto fight
            elif u == RAISES:
                stat = "Dexterity" if self.split % 3 == 2 else "Strength"
                self.raised = True
                self.phone.do(f"item:{STAT_ORDER.index(stat)},wait:300")
            elif u == ADD:
                self.split += 1                          # counted once added
                self.phone.do("choose:Add,wait:300")    # "Click to add"
            elif u == ACTIONS:
                self.phone.do("choose:Cancel,wait:200")
            else:
                self.phone.do("dismiss,wait:300")
        return self.phone.state()

    def heard(self):
        """Dialogs the harness closed on its own (a walk, a dismiss)."""
        for text in self.phone.said:
            text = text.replace("|", " / ")
            if self.dialogs and self.dialogs[-1] == text:
                continue                    # settle() already read this one
            self.dialogs.append(text)
            self.log(f"      said: {text[:150]}")
            if ENDING in text:
                self.finished = True
                self.log("      ENDING: " + text[text.index(ENDING):][:300])
        self.phone.said.clear()

    # -- gear ---------------------------------------------------------------

    def named(self, entry):
        """The item a list row is about. A row can open with a colour mark
        (handlers._gear_mark: \x06 and three colour bytes) before the name."""
        entry = entry.replace(" (worn)", "")
        for start in (0, 4):
            if self.w.item(entry[start:]) is not None:
                return entry[start:]
        return None

    def worth(self, name, slot):
        """How good a piece is for this swordsman; None if it is not for him.
        The slot list only offers what the hero meets the needs of."""
        it = self.w.item(name)
        if it is None:
            return None
        if slot == 0 and (it.kind != "weapon" or it.cls not in LINE):
            return None
        if slot == 1 and it.kind != "armour":
            return None
        return handlers._gear_value(self.w, it)

    def dress(self):
        """Wear the best weapon and armour the phone offers, through Menu >
        Hero info > Equipped items, the way a player would."""
        st = self.phone.state()
        if int(st.get("u", 0)) != MAP or st.get("inCombat") == "true":
            return self.settle()
        self.phone.do("key:-7,wait:400")
        self.phone.do("choose:Hero info,wait:400")
        self.phone.do("choose:Equipped items,wait:1500")
        for slot in (0, 1):
            if int(self.phone.state().get("u", 0)) != SLOTS:
                break
            self.phone.do(f"item:{slot},wait:1500")
            st = self.phone.state()
            if int(st.get("u", 0)) != SLOT_ITEMS:
                break
            best, pick, worn = None, None, None
            for i, entry in enumerate(st["items"]):
                name = self.named(entry)
                locked = entry.startswith(LOCKED)
                v = None if locked or name is None else self.worth(name, slot)
                if entry.endswith("(worn)"):
                    worn = (v if v is not None else -1, name)
                if v is not None and (best is None or v > best[0]):
                    best, pick = (v, name), i
            if pick is not None and (worn is None or best[0] > worn[0]):
                self.phone.do(f"item:{pick},wait:400")
                self.phone.do("choose:Equip,wait:1500")
                on = saved().get("equipped", {}).get("weapon" if slot == 0 else "armour")
                self.log(f"      {'wears' if on == best[1] else 'COULD NOT WEAR'} {best[1]}")
                self.worn[slot] = on
            else:
                self.phone.do("choose:Back,wait:400")
        for _ in range(6):
            u = int(self.phone.state().get("u", MAP))
            if u not in (MENU, 9, SLOTS, SLOT_ITEMS, ITEM):
                break          # the map, or something only settle() may answer
            self.phone.do("choose:Resume game,wait:600" if u == MENU else "choose:Back,wait:400")
        self.raised = False
        return self.settle()

    # -- one thing to do ---------------------------------------------------

    def walk(self, x, y, timeout=120000):
        out = self.phone.do(f"path:{x}:{y}:{timeout}")
        return next((l for l in out if l.startswith("PATH")), "PATH ?")

    def act(self, label):
        out = self.phone.do(f"act:{label},wait:700")
        for line in out:
            if line.startswith("ACT missing") or line.startswith("ACT no action"):
                self.log(f"      {line[4:]}")
        return any(l == "ACT " + label for l in out)

    def spots(self, loc, x1, y1, x2, y2):
        """The tiles of a trigger box, ground the hero can stand on first
        and nearest the middle first. A box's middle can be a wall: Mira's
        greeting is a strip one tile wide whose centre is solid."""
        mp = self.w.map(loc)
        cx, cy = (x1 + x2 - 1) / 2, (y1 + y2 - 1) / 2
        tiles = [(x, y) for x in range(x1, x2) for y in range(y1, y2)]
        tiles.sort(key=lambda t: (not mp.walkable(*t), abs(t[0] - cx) + abs(t[1] - cy)))
        return tiles

    def todo(self, loc, live, nodes, seen):
        """What is left to do here: (kind, key, x, y, label). Creatures wander
        on the phone, so a fight goes to where the phone draws it now."""
        jobs = []
        for sid, r in self.rows.items():
            if r[1] != loc or live.get(sid) != 2 or r[12] in (4, 10):
                continue
            if self.tried.get(("entity", sid), 0) >= 3:
                continue
            x1, y1, x2, y2 = self.box(r)
            if (x1, y1, x2, y2) == (0, 0, 0, 0):
                continue                      # fires by itself when armed
            lab = self.label(r) if r[6] == 1 else ""
            if r[6] == 1 and not lab:
                continue
            if r[6] not in (0, 1):
                continue
            spots = self.spots(loc, x1, y1, x2, y2)
            jobs.append(("entity", sid, spots[0][0], spots[0][1], lab))
        for node, (nloc, nst) in nodes.items():
            c = self.creatures.get(node)
            if nloc != loc or nst != 2 or c is None or not c[10]:
                continue
            m = self.w.mobs.get(node)
            if m is None or m.npc or self.tried.get(("fight", node), 0) >= 3:
                continue
            lab = self.w.text(loc).get(int.from_bytes(bytes(c[7:9]), "big"), "")
            if lab.startswith("Fight"):
                x, y = seen.get(node, (c[3], c[4]))
                jobs.append(("fight", node, x, y, lab))
        return jobs

    def do_job(self, job, here):
        kind, key, x, y, lab = job
        self.tried[(kind, key)] = self.tried.get((kind, key), 0) + 1
        self.log(f"   {kind} {lab or 'walk in'} at ({x},{y})")
        path = self.walk(x, y)
        if kind == "entity" and path.startswith("PATH none"):
            r = self.rows[key]
            for sx, sy in self.spots(r[1], *self.box(r))[1:6]:
                path = self.walk(sx, sy)
                if not path.startswith("PATH none"):
                    break
        if "doorway" in path:
            return self.settle()
        before = len(self.fights)
        self.settle()
        if kind == "fight" and len(self.fights) > before:
            return self.phone.state()             # it came to us on the way
        if lab:
            if self.act(lab):
                st = self.settle()
                if kind == "entity":
                    self.raised = True           # a crate may have held gear
                    # answered: leave it until something in the world changes
                    self.tried[(kind, key)] = 3
                return st
            self.log(f"      no '{lab}' in reach from here")
        return self.settle()

    # -- the chapter -------------------------------------------------------

    def next_room(self, here, live, done):
        """The next room in route order that the open doors reach, and the
        doorway to take toward it."""
        graph = {}
        for sid, dest in self.exits().items():
            if live.get(sid) == 2 and sid not in self.walled:
                graph.setdefault(self.rows[sid][1], []).append((dest, sid))
        for target in tiers.ROUTE:
            if target in done or target == here:
                continue
            seen, queue = {here: None}, [here]
            while queue:
                cur = queue.pop(0)
                if cur == target:
                    break
                for dest, sid in graph.get(cur, []):
                    if dest not in seen:
                        seen[dest] = (cur, sid)
                        queue.append(dest)
            if target in seen:
                step = target
                while seen[step][0] != here:
                    step = seen[step][0]
                return target, seen[step][1]
        return None, None

    def play(self, max_rooms=None, max_steps=900):
        self.phone.do(f"boot:{HERO}")
        st = self.settle()
        done = set()
        for _ in range(max_steps):
            if self.finished:
                break
            here = int(st.get("location", 0))
            if not self.rooms or self.rooms[-1] != here:
                self.rooms.append(here)
                self.walled.clear()
                self.log(f"\n== {self.w.name(here)} (hero at {st.get('heroX')},{st.get('heroY')})")
            if self.raised:
                st = self.dress()
            live, _ = self.phone.states(sorted(self.rows))
            # Something changed (a wall opened, a barrier fell, a quest
            # moved on): what could not be reached before may be now. A job
            # is finished when the phone says so (state 3), never on its word.
            if live != getattr(self, "last_live", None):
                for job in [j for j in self.tried if j[0] == "entity"]:
                    del self.tried[job]
                self.last_live = live
            nodes = self.phone.nodes()
            jobs = self.todo(here, live, nodes, self.phone.where())
            if jobs:
                hx, hy = int(st.get("heroX", 0)), int(st.get("heroY", 0))
                jobs.sort(key=lambda j: abs(j[2] - hx) + abs(j[3] - hy))
                st = self.do_job(jobs[0], here)
                continue
            done.add(here)
            if max_rooms and len(done) >= max_rooms:
                break
            target, door = self.next_room(here, live, done)
            if door is None:
                self.log("   nothing left that the open doors reach")
                break
            r = self.rows[door]
            self.log(f"   on to {self.w.name(target)} by the door at {self.box(r)[:2]}")
            path = self.walk(r[2], r[3])
            st = self.settle()
            if int(st.get("location", 0)) == here and not path.startswith("PATH stopped"):
                # an open door the hero cannot walk to from this side (a
                # way back in from a room reached some other way)
                self.log(f"      cannot reach that door from here ({path})")
                self.walled.add(door)
        return self


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--rooms", type=int)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    started = time.time()
    phone = Phone(args.verbose)
    lines = []

    def log(text):
        print(text, flush=True)
        lines.append(text)
    try:
        run = Player(phone, log).play(max_rooms=args.rooms)
    finally:
        phone.close()
    won = sum(1 for _, ok in run.fights if ok)
    log(f"\nrooms entered: {len(set(run.rooms))}/18   fights: {won} won, "
        f"{len(run.fights) - won} lost   "
        f"ending reached: {run.finished}   {time.time() - started:.0f}s")
    return 0 if run.finished or args.rooms else 1


if __name__ == "__main__":
    sys.exit(main())
