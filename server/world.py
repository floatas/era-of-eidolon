"""Server-side game state for Era of Eidolon.

The client is a renderer: it holds no hero, no inventory, no world state. All of
that lived on watAgame's servers and is gone, so this is where it gets rebuilt.

Everything here is driven by data that *did* survive inside the chapter jar —
tilemaps, location text, the creature catalogue. See tools/dump_world.py.
"""

import os
import random
import re
import struct
import zipfile

from catalogue import catalogue

JARS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "jars")
DEFAULT_GAME = "ShiradsForge"


def jar_path(game=DEFAULT_GAME):
    return os.path.join(JARS, f"EoE-{game}.jar")


# --------------------------------------------------------------- jar resources

class Resources:
    """Reads the "<restype><hex id>" files out of a chapter jar."""

    def __init__(self, path=None):
        path = path or jar_path()
        with zipfile.ZipFile(path) as z:
            self.files = {n: z.read(n) for n in z.namelist() if "/" not in n}

    def get(self, restype, rid):
        return self.files.get(f"{restype}{rid:x}")

    def strings(self, restype, rid):
        """Keyed string table: u16 key, u16 len, bytes (g.java a(in,len,bool))."""
        b = self.get(restype, rid)
        out = {}
        if not b:
            return out
        i = 0
        while i + 4 <= len(b):
            key = int.from_bytes(b[i:i + 2], "big")
            ln = int.from_bytes(b[i + 2:i + 4], "big")
            i += 4
            if i + ln > len(b):
                break
            try:
                out[key] = b[i:i + ln].decode("utf-8")
            except UnicodeDecodeError:
                pass
            i += ln
        return out

    def props(self, restype, rid):
        """Props table: u8 count, then u8 key, u8 len, bytes. Returns the
        whole thing — anims() only wants the keys, but the bodies are the
        animation scripts themselves."""
        b = self.get(restype, rid)
        out, i = {}, 1
        if not b:
            return out
        for _ in range(b[0]):
            if i + 1 >= len(b):
                break
            key, n = b[i], b[i + 1]
            out[key] = b[i + 2:i + 2 + n]
            i += 2 + n
        return out

    def anims(self, restype, rid):
        """Props table: u8 count, then u8 key, u8 len, bytes."""
        b = self.get(restype, rid)
        if not b:
            return set()
        out, i = set(), 1
        for _ in range(b[0]):
            if i + 1 >= len(b):
                break
            out.add(b[i])
            i += 2 + b[i + 1]
        return out


class TileMap:
    """A type 2 resource. 13-byte header then width*height tile bytes:

        i8  unknown           i16 unknown
        u16 walk mask, low nibble    (d.aB)
        u16 walk mask, high nibble   (d.aC)
        u16 unknown                  (d.aD)
        i16 width   i16 height
    """

    HEADER = 13

    def __init__(self, blob):
        (_, _, self.mask_lo, self.mask_hi, self.aD,
         self.w, self.h) = struct.unpack_from(">bhHHHhh", blob, 0)
        self.tiles = blob[self.HEADER:self.HEADER + self.w * self.h]

    def tile(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.tiles[y * self.w + x]
        return 0

    def walkable(self, x, y):
        """d.java:b(int,int), transcribed exactly."""
        t = self.tile(x, y)
        base = (self.mask_lo >> (t & 15)) & (self.mask_hi >> ((t & 240) >> 4)) & 1
        return bool((base == 1) ^ ((t & 240) == 16))

    def obstacle(self, x, y):
        """The tile's HIGH nibble picks an obstacle sprite (d.java:551):
        `(tile & 240) >> 4`, where 0 is bare ground, 1 is an exit tile, and
        anything >= 2 indexes the 8-bytes-per-entry table in type 6 id 2.
        For Shirad's Forge that makes 10 a wooden crate and 11 a barrel."""
        return (self.tile(x, y) & 240) >> 4

    CRATE, BARREL = 10, 11

    def is_override(self, x, y):
        """High nibble 1 flips the walkability test for this tile.

        Not a doorway, which is what this used to be called. It is how the
        artist opens ground that the walk mask closes and closes ground it
        opens — the Harbour's nine are its piers, laid over water. The
        doorways are a GROUND tile: see World.marker.
        """
        return (self.tile(x, y) & 240) == 16


# ------------------------------------------------------------------ game state

class Mob:
    def __init__(self, node, location, x, y, creature, hp=12, anim=1,
                 npc=False):
        self.npc = npc
        self.node = node
        self.location = location
        self.x, self.y = x, y
        self.creature = creature
        self.hp = self.max_hp = hp
        self.anim = anim
        self.alive = True

    # d.java:226 reads byte 15 and, when it is set, starts the WALK animation
    # on the creature: `this.n[id].a(14, true)`. Only creatures that move have
    # one. Setting it for a townsperson kills the paint thread with "Unable to
    # get anim 14 for monster id N" the moment the hero moves.
    ANIM_ON_SPAWN = 14

    def record(self, animated=True):
        """A 19-byte type 9 row."""
        r = bytearray(19)
        r[0] = self.node
        r[1] = self.location
        r[3] = self.x
        r[4] = self.y
        r[12] = self.creature
        r[13] = self.anim
        r[15] = 1 if animated else 0
        return r


class World:
    """One player's game in one chapter.

    Nothing here is specific to a chapter: the locations, their names, their
    exits and the creature catalogue are all read out of the jar. That is what
    lets the same server run Shirad's Forge and Sterling Lake — and any other
    gen-2 chapter, if one ever turns up.
    """

    def __init__(self, game=DEFAULT_GAME, res=None):
        self.game = game
        self.res = res or Resources(jar_path(game))
        self.maps = {}
        self._marker = None
        self._names = {}
        self.locations = sorted(
            int(n[1:], 16) for n in self.res.files
            if re.fullmatch(r"2[0-9a-f]+", n) and not n.startswith(("10", "11")))
        self.creatures = sorted(
            int(n[1:], 16) for n in self.res.files
            if re.fullmatch(r"7[0-9a-f]+", n) and not n.startswith(("10", "11"))
            and int(n[1:], 16) != 0)          # 0 is the hero's own sprite
        self.exits = self._build_exits()

        # EOE_START_LOC drops a new hero straight into a location, which is
        # how a scripted test reaches something twenty tiles of maze away.
        start = os.environ.get("EOE_START_LOC")
        self.location = (int(start) if start and int(start) in self.locations
                         else (self.locations[0] if self.locations else 1))
        self.hero_x, self.hero_y = self.spawn_point(self.location)
        self.hero_hp = self.hero_max = 40

        # The character system is NOT lost — it is in the client, d.java:27-37:
        #   y[] the six action-bar categories
        #   z[] the six stat names
        #   A[] what each stat actually does
        #   b[] the shop categories
        # and d.a(int) has the raise-cost curve: a stat under 48 costs 3 per
        # point, under 78 costs 2, above that 1. What is missing is the item
        # and spell catalogue, which the server sent.
        self.stats = dict(zip(self.STATS, [30, 20, 25, 30, 20, 25]))
        self.level = 1
        self.xp = 0
        self.gold = 50
        self.raises = 0

        # "Your hero starts with the most basic sword as a default" and the
        # same for bows — EOE GAME RULES, Items.
        kit = catalogue().starting_kit()
        self.inventory = [i.name for i in kit.values()]
        self.equipped = {
            "weapon": kit.get("sword").name if kit.get("sword") else None,
            "armour": kit.get("armour").name if kit.get("armour") else None,
        }
        self.mobs = {}
        self.next_node = 1
        # Node ids index into the tag-21 and tag-25 state arrays and into
        # d.n (sized from tag 25), and they are global across the whole world,
        # not per location.
        # Both state arrays are indexed by a u8, so 255 is the ceiling. 128
        # was fine until doorways started carrying a patch entity each.
        self.node_count = 200
        self.populate()

    # -- map access ---------------------------------------------------------

    def map(self, location=None):
        loc = self.location if location is None else location
        if loc not in self.maps:
            blob = self.res.get(2, loc)
            self.maps[loc] = TileMap(blob) if blob else None
        return self.maps[loc]

    # Objectives read as imperatives — the verb is what separates them from
    # the quest ITEM names and descriptions sharing the same table.
    QUEST_VERBS = ("seek", "find", "rescue", "restore", "defeat", "clear",
                   "return", "slay", "get", "save", "help", "bring", "kill",
                   "destroy", "deliver", "escort", "recover",
                   # Mistral Grove needed these, which is a good argument for
                   # checking a new chapter against the list rather than
                   # assuming the list is finished
                   "cut", "release", "open", "close", "break", "steal",
                   "collect", "reach", "enter", "light", "free", "talk")

    def quests(self):
        """The chapter's quest objectives, in key order.

        These ship in the jar, in the global text table (type 10 id 0). What
        did NOT ship is which entity hands out which one, or whether it counts
        as a main quest — that lived in the type 1 rows the server sent, so
        the log is assembled here rather than recovered.
        """
        out = []
        for key, txt in sorted(self.res.strings(10, 0).items()):
            first = txt.split()[0].lower().strip(".,!") if txt.split() else ""
            if len(txt) < 60 and first in self.QUEST_VERBS:
                out.append((key, txt))
        return out

    def text(self, location=None):
        return self.res.strings(3, self.location if location is None else location)

    def name(self, location=None):
        """The location's own name. A tilemap's header carries the string key
        for it (field aD), which indexes that location's type 3 table."""
        loc = self.location if location is None else location
        if loc not in self._names:
            mp = self.map(loc)
            self._names[loc] = self.text(loc).get(mp.aD, f"Area {loc:#x}") if mp \
                else f"Area {loc:#x}"
        return self._names[loc]

    @property
    def LOCATION_NAMES(self):
        return {l: self.name(l) for l in self.locations}

    # -- geography ----------------------------------------------------------

    @property
    def marker(self):
        """The ground index of the doorway tile — the red one with the green
        arrows the help text describes.

        It is a painted GROUND tile, not a flag in the high nibble, and its
        index differs per chapter: 12 in Shirad's Forge, 14 in Sterling Lake.
        Rather than hardcode that, find it in the type 4 sheet by its own
        colours. Nothing else in either palette is 70% red and a quarter
        green; the two chapters score identically because it is the same
        piece of art filed at a different index.
        """
        if self._marker is None:
            import io
            from PIL import Image
            ids = [int(n[1:] or "0", 16) for n in self.res.files
                   if re.fullmatch(r"4[0-9a-f]*", n)]
            best = (0, 1)
            if ids:
                sheet = Image.open(io.BytesIO(self.res.get(4, ids[0])))
                sheet = sheet.convert("RGBA")
                for i in range(sheet.height // 15):
                    strip = sheet.crop((0, i * 15, 32, (i + 1) * 15))
                    red = green = n = 0
                    for r, g, b, a in list(strip.getdata()):
                        if a < 128:
                            continue
                        n += 1
                        red += r > 150 and g < 90 and b < 90
                        green += g > 150 and r < 120 and b < 120
                    if n and (red / n) * (green / n) > best[0]:
                        best = ((red / n) * (green / n), i + 1)
            self._marker = best[1]
        return self._marker

    def exit_tiles(self, location):
        """Every doorway the artist painted in a location. Adjacent ones are
        one doorway, so collapse them into clusters."""
        mp = self.map(location)
        if not mp:
            return []
        raw = [(x, y) for y in range(mp.h) for x in range(mp.w)
               if (mp.tile(x, y) & 15) == self.marker]
        clusters = []
        for x, y in raw:
            for c in clusters:
                if any(abs(x - cx) <= 1 and abs(y - cy) <= 1 for cx, cy in c):
                    c.append((x, y))
                    break
            else:
                clusters.append([(x, y)])
        return [c[0] for c in clusters]

    # The route as watAgame wrote it, recovered from the chapters' own
    # dialogue rather than from the lost tables. Every one of these is a
    # location naming another location out loud; the quotes and their text
    # keys are in notes/FLOW.md. Sterling Lake's hints name a direction but
    # not a place, so it gets none.
    STORY_ROUTE = {
        "ShiradsForge": [
            ("Village", "Lava Island"),        # "the 1st one on a small island"
            ("Lava Island", "Dwarven Hall"),   # "Dwarven Hall North of here"
            ("Dwarven Hall", "Mira's Hideout"),  # "the cave North of here"
            ("Mira's Hideout", "The Lair"),    # "the Lair East of here"
            ("The Lair", "The Core"),          # "when you go through the Core"
            ("The Core", "The Forge"),         # "the Forge somewhere to the North"
        ],
        "MistralGrove": [
            ("Outskirts", "Mirror Pool"),      # "the small pond called Mirror Pool"
            ("Mirror Pool", "Spiderwood"),     # "the first part is in Spiderwood"
            ("Spiderwood", "Hollow Hill"),     # the handle is in Hollow Hill's crate
            ("Hollow Hill", "The Hedge"),      # "your way is blocked by a magical hedge"
            ("The Hedge", "Mistral Grove"),    # "the altar at Mistral Grove"
            ("Mistral Grove", "Deadwood"),     # "the Deadwood North of here"
        ],
    }

    def story_links(self):
        """The main chain, as location ids.

        Two chapters give their route away in dialogue, and in both the route
        is exactly the location ids in order:

            Village 1, Lava Island 2, Dwarven Hall 3, Mira's Hideout 4,
            The Lair 5, The Core 6, The Forge 7
            Outskirts 40, Mirror Pool 41, Spiderwood 42, Hollow Hill 43,
            The Hedge 44, Reaperwood 45, Mistral Grove 46, Deadwood 47

        watAgame numbered their locations in the order you walk them. So the
        chain is the run of consecutive ids up to the last place the script
        names, and the dialogue is what tells us where that run ends — after
        it come the side chambers, which the script never mentions and which
        each have a single doorway.

        Reaperwood is the case that proves the rule: nothing says a word
        about it, but it sits at 45 between The Hedge and Mistral Grove, and
        chaining by id puts it where it belongs.
        """
        by_name = {}
        for loc in self.locations:
            by_name.setdefault(self.name(loc), loc)
        named = [by_name[n] for pair in self.STORY_ROUTE.get(self.game, ())
                 for n in pair if n in by_name]
        if not named:
            return []
        end = self.locations.index(max(named))
        chain = self.locations[:end + 1]
        return list(zip(chain, chain[1:]))

    def _build_exits(self):
        """Wire the locations together.

        Which doorway led where lived in the lost type 1 tables, so this is a
        reconstruction. The rule it replaces linked each doorway to "the next
        location in id order", which chose destinations purely as a function
        of the source: Sterling Lake's Harbour ended up with twelve ways in
        and Gold Island with none, and seven locations could be left but never
        entered.

        This builds a hub and spokes instead, and guarantees two things that
        the old rule did not: every location can be reached, and every
        location can be left.

        A doorway does not actually need a red exit tile. The trigger is a
        type 1 bounding box (see exit_entity), and the tiles are only the
        artist showing you where the boxes were. So a location the artist
        never marked still gets one, invented on walkable ground.
        """
        locs = list(self.locations)
        if len(locs) < 2:
            return {loc: [] for loc in locs}

        marked = {loc: list(self.exit_tiles(loc)) for loc in locs}
        hub = max(locs, key=lambda l: (len(marked[l]), -l))
        spokes = [l for l in locs if l != hub]

        out = {loc: [] for loc in locs}
        spent = {loc: 0 for loc in locs}
        wired = set()

        def doorway(loc):
            """The next unused doorway in this location."""
            n = spent[loc]
            spent[loc] += 1
            if n < len(marked[loc]):
                return marked[loc][n]
            return self._invent_doorway(loc, [t for t, _ in out[loc]]
                                        + marked[loc])

        # The route the dialogue gives us goes in first and is never
        # overridden: these are the only links in the project that are
        # watAgame's rather than ours.
        for a, b in self.story_links():
            if a in out and b in out:
                out[a].append((doorway(a), b))
                out[b].append((doorway(b), a))
                wired.add(a)
                wired.add(b)

        # the hub reaches as far as its own doorways allow, and each of those
        # keeps one doorway for the way back
        reach = max(1, len(marked[hub]))
        spokes = [l for l in spokes if l not in wired] or spokes
        attached = []
        for dest in spokes[:reach]:
            out[hub].append((doorway(hub), dest))
            out[dest].append((doorway(dest), hub))
            attached.append(dest)

        # whatever is left hangs off the chain, so nothing is stranded
        prev = attached[-1] if attached else hub
        for dest in spokes[reach:]:
            out[prev].append((doorway(prev), dest))
            out[dest].append((doorway(dest), prev))
            prev = dest

        # Now spend the doorways the artist drew and the structure above did
        # not need. Where they lead is ours either way, but a door that
        # watAgame put on the map is better used than left shut while we
        # invent one somewhere else. Pair them off, spare with spare.
        spare = [l for l in locs for _ in range(len(marked[l]) - spent[l])
                 if spent[l] < len(marked[l])]
        for a, b in zip(spare[0::2], spare[1::2]):
            if a == b or any(d == b for _, d in out[a]):
                continue
            out[a].append((doorway(a), b))
            out[b].append((doorway(b), a))

        # an odd one out still beats leaving a drawn door shut; the far end of
        # that link is invented, this end is the artist's
        for loc in locs:
            if spent[loc] < len(marked[loc]):
                other = hub if loc != hub else spokes[0]
                out[loc].append((doorway(loc), other))
                out[other].append((doorway(other), loc))

        return out

    def _invent_doorway(self, location, avoid):
        """A walkable tile to put a doorway on, well clear of the others."""
        mp = self.map(location)
        if not mp:
            return (1, 1)
        best = None
        for y in range(mp.h):
            for x in range(mp.w):
                if not mp.walkable(x, y) or (mp.tile(x, y) & 15) == self.marker:
                    continue
                near = min((max(abs(x - ax), abs(y - ay))
                            for ax, ay in avoid), default=99)
                if near <= EXIT_RADIUS + 2:
                    continue
                # hug the edge: doorways belong at the rim of a map, not in
                # the middle of it
                rim = min(x, y, mp.w - 1 - x, mp.h - 1 - y)
                score = (rim, -near)
                if best is None or score < best[0]:
                    best = (score, (x, y))
        return best[1] if best else (1, 1)

    EXITS = property(lambda self: self.exits)

    def doorway_tiles(self, location):
        """Every doorway in a location: the ones the artist marked, plus any
        this server had to invent to keep the chapter connected."""
        wired = [t for t, _ in getattr(self, "exits", {}).get(location, [])]
        return wired or list(self.exit_tiles(location))

    def spawn_point(self, location):
        """A walkable tile to stand on: just outside a doorway's trigger box if
        there is one, else near the middle.

        Standing next to it rather than on it is the whole point: arrive on a
        doorway and it fires again the instant the map loads, and the two
        locations bounce the player back and forth forever.
        """
        mp = self.map(location)
        if not mp:
            return 1, 1
        exits = list(self.doorway_tiles(location))

        def clear(x, y):
            if not mp.walkable(x, y) or (mp.tile(x, y) & 15) == self.marker:
                return False
            return all(max(abs(x - ex), abs(y - ey)) > EXIT_RADIUS
                       for ex, ey in exits)

        # the first ring outside every trigger box, nearest doorway first
        r = EXIT_RADIUS + 1
        for (ex, ey) in exits:
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if max(abs(dx), abs(dy)) != r:
                        continue
                    if clear(ex + dx, ey + dy):
                        return ex + dx, ey + dy
        cx, cy = mp.w // 2, mp.h // 2
        best = None
        for y in range(mp.h):
            for x in range(mp.w):
                if clear(x, y):
                    d = abs(x - cx) + abs(y - cy)
                    if best is None or d < best[0]:
                        best = (d, x, y)
        return (best[1], best[2]) if best else (1, 1)

    def arrival(self, location, came_from=None):
        """Where to drop the hero when entering a location.

        Beside the doorway that leads BACK to where they came from, which is
        the whole difference between a door and a chute. Without the
        `came_from` half of it every route into a location lands on the same
        tile, so half the time the player steps out next to some other
        chapter's doorway and the way home is across the map — it reads as
        one-way even though the link is not.

        Never ON the doorway: that fires it again as the map loads and the
        two locations bounce the player back and forth.
        """
        mp = self.map(location)
        if mp and came_from is not None:
            back = [t for t, dest in self.exits.get(location, [])
                    if dest == came_from]
            doors = {t for t, _ in self.exits.get(location, [])}
            for bx, by in back:
                for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0),
                               (1, 1), (-1, -1), (1, -1), (-1, 1)):
                    x, y = bx + dx, by + dy
                    if (0 <= x < mp.w and 0 <= y < mp.h
                            and mp.walkable(x, y) and (x, y) not in doors):
                        return x, y
        return self.spawn_point(location)

    # -- population ---------------------------------------------------------

    def populate(self):
        """Populate EVERY location, not just the current one.

        The client fetches type 1 and type 9 exactly once, at opcode 8, and
        never asks again — which is why each record carries a location field.
        One table describes the whole world. Filling in only the current
        location leaves every other one empty, so travelling somewhere new
        strands you there with no monsters and no way back.
        """
        self.mobs.clear()
        self.next_node = 1
        for loc in self.locations:
            self.populate_location(loc)
            self.place_npcs(loc)

    def place_npcs(self, loc):
        """One standing figure per "Talk to ..." label the location carries.

        They are ordinary type 9 nodes using the townsfolk sheet, with their
        node state left at 1: k() renders anything at state 1 or 2, but only
        state 2 goes into aF, so these are visible and never fight.
        """
        creature = self.npc_creature
        mp = self.map(loc)
        if creature is None or not mp:
            return
        ax, ay = self.spawn_point(loc)
        spots = [(2, -1), (-2, 1), (1, 2), (-1, -2), (3, 0), (0, 3)]
        talkers = [(k, v) for k, v in self.action_labels(loc)
                   if v.lower().startswith(("talk", "speak", "trade"))]
        for (key, label), (dx, dy) in zip(talkers, spots):
            x, y = ax + dx, ay + dy
            if not mp.walkable(x, y) or self.mob_at(x, y, loc):
                x, y = ax, ay
            m = Mob(self.next_node, loc, x, y, creature, hp=1, npc=True)
            m.anim = self.anim(creature, "idle")
            m.label = label
            m.text_key = key
            self.mobs[m.node] = m
            self.next_node += 1

    # Which creature fights where, recovered from each chapter's own text.
    # Every location's type 3 table carries the action labels it needs, and
    # among them are the "Fight <name>" lines the context menu shows. So the
    # jar states, exactly, that Beetles are in Lava Island, The Lair, Fire
    # Cave, Dune Burrow and Lava Pit — and nowhere else. That is the species
    # half of the lost type 9 table, and it was sitting in the strings all
    # along.
    FIGHT = re.compile(r"Fight ([A-Za-z][A-Za-z' ]{0,18})$")

    def fights(self, location):
        """The creature names that fight in a location, as the game names
        them. Authoritative: this is watAgame's own text."""
        out = []
        for _, v in sorted(self.text(location).items()):
            m = self.FIGHT.fullmatch(v.strip())
            if m and m.group(1) not in out:
                out.append(m.group(1))
        return out

    # Which sheet draws which name is NOT stated anywhere, so this is read off
    # the art and is inference, not recovery. The ones here are unmistakable —
    # a skeleton, a crab, a swarm of flies, a fishman with a trident, a spark
    # of light, a stand of tree trunks. Anything absent falls back to a stable
    # arbitrary choice, which still beats the old behaviour of picking a
    # different species every time a location was populated.
    CREATURE_SPRITE = {
        # Shirad's Forge
        "Skeleton": 0x1d, "Beetle": 0x19, "Ghost": 0x1b, "Beholder": 0x23,
        "Gorrak": 0x1c, "Fire Devil": 0x2a, "Fungusman": 0x20, "Golem": 0x18,
        # Sterling Lake — 0x3c is the fishman sheet, and the Fishking is a
        # fishman, which is why it doubles as the chapter's NPC art
        "Fishman": 0x3c, "Sandleech": 0x33, "Crab": 0x3a, "Swarm": 0x37,
        "Aquamental": 0x2f, "Black Eye": 0x3b, "Jaques": 0x3b,
        # Mistral Grove
        "will o' wisp": 0x45, "treeman": 0x43, "spider": 0x42,
        "demon dog": 0x40, "reaperweed": 0x41, "Trix": 0x44,
        "guard": 0x3f, "Salar": 0x3f,
    }

    def creature_for(self, name):
        """A sheet for a creature name, the same one every time."""
        if not hasattr(self, "_species"):
            self._species = {}
        if name in self._species:
            return self._species[name]
        pinned = self.CREATURE_SPRITE.get(name)
        if pinned in self.creatures:
            self._species[name] = pinned
            return pinned
        # A name the text uses in only one place, spelled like a proper noun,
        # is a person or a boss rather than a species — Mira, Shirard, Aldor —
        # and those wear the chapter's people sheet.
        here = sum(1 for l in self.locations if name in self.fights(l))
        if here == 1 and name[:1].isupper() and self.npc_creature:
            self._species[name] = self.npc_creature
            return self.npc_creature
        fighters = [c for c in self.creatures if c != self.npc_creature]
        taken = set(self._species.values())
        spare = [c for c in fighters
                 if c not in taken and c not in self.CREATURE_SPRITE.values()]
        pool = spare or [c for c in fighters if c not in taken] or fighters
        pick = pool[sum(map(ord, name)) % len(pool)]
        self._species[name] = pick
        return pick

    def populate_location(self, loc):
        """Which creatures a chapter has is in its jar (types 7/8/11 share an
        id per creature); where they stood was in the lost tables, so scatter a
        couple on walkable ground near where the player arrives."""
        mp = self.map(loc)
        if not mp or not self.creatures:
            return
        ax, ay = self.spawn_point(loc)
        # Deterministic per location, so a save reloads the same encounter.
        rng = random.Random(f"{self.game}:{loc}")
        # The species are the location's own — the tiles they stand on are
        # still ours, because that half of type 9 really is gone.
        named = [self.creature_for(n) for n in self.fights(loc)]
        fighters = named or [c for c in self.creatures
                             if c != self.npc_creature]
        if not fighters:
            return
        placed = 0
        for _ in range(max(1, min(2, len(fighters)))):
            creature = fighters[placed % len(fighters)]
            for _ in range(80):
                x, y = ax + rng.randint(-5, 5), ay + rng.randint(-5, 5)
                if (x, y) == (ax, ay) or self.mob_at(x, y, loc):
                    continue
                if mp.walkable(x, y) and (mp.tile(x, y) & 15) != self.marker:
                    m = Mob(self.next_node, loc, x, y, creature,
                            hp=6 + 2 * placed + 2 * self.locations.index(loc))
                    m.anim = self.anim(creature, "idle")
                    self.mobs[m.node] = m
                    self.next_node += 1
                    placed += 1
                    break

    STATS = ["Strength", "Intelligence", "Dexterity",
             "Toughness", "Willpower", "Speed"]

    # d.java:29-36, verbatim from the game.
    STAT_HELP = {
        "Strength":     "+weapon damage, +carry more weight, +heavier weapons",
        "Intelligence": "+effect to all spells cast on foe",
        "Dexterity":    "+hit chance, +defense, +complex weapon",
        "Toughness":    "+life points",
        "Willpower":    "+spell resistance, +protect spells cheaper prices",
        "Speed":        "+faster when using skills and spells in fight",
    }

    SHOP_CATEGORIES = ["Melee weapons", "Missile weapons", "Armours",
                       "Skills", "Spells", "Back"]

    def raise_cost(self, stat):
        """d.a(int): under 48 a point buys 3, under 78 buys 2, else 1."""
        v = self.stats.get(stat, 0)
        return 3 if v < 48 else (2 if v < 78 else 1)

    def xp_for_next(self):
        return 100 * self.level

    def grant_xp(self, amount):
        self.xp += amount
        gained = 0
        while self.xp >= self.xp_for_next():
            self.xp -= self.xp_for_next()
            self.level += 1
            self.raises += 3
            self.hero_max += 6
            self.hero_hp = self.hero_max
            gained += 1
        return gained

    # -- equipment ----------------------------------------------------------

    def item(self, name):
        return catalogue().find(name) if name else None

    def weapon(self):
        return self.item(self.equipped.get("weapon"))

    def armour(self):
        return self.item(self.equipped.get("armour"))

    def attack_damage(self):
        """Rules: base = skill effect + weapon + Strength; a low roll (a
        precise hit) multiplies it. Dexterity governs the critical chance."""
        w = self.weapon()
        base = (w.effect if w else 2) + self.stats["Strength"] // 6
        crit = random.random() < min(0.35, self.stats["Dexterity"] / 200)
        dmg = base + random.randint(0, max(1, base // 3))
        return (int(dmg * 1.8), True) if crit else (dmg, False)

    def damage_taken(self, raw):
        """Armour reduces melee and missile damage. It never touches spells."""
        a = self.armour()
        return max(1, raw - (a.effect if a else 0))

    def equip(self, name):
        it = self.item(name)
        if not it or it.name not in self.inventory:
            return None
        slot = "armour" if it.kind == "armour" else "weapon"
        self.equipped[slot] = it.name
        return it

    def buy(self, name):
        it = self.item(name)
        if not it or it.price > self.gold or it.name in self.inventory:
            return None
        self.gold -= it.price
        self.inventory.append(it.name)
        return it

    def hero_sheet(self):
        w, a = self.weapon(), self.armour()
        lines = [f"Level {self.level}   XP {self.xp}/{self.xp_for_next()}",
                 f"Life {self.hero_hp}/{self.hero_max}   Gold {self.gold}",
                 f"Weapon: {w.name if w else 'none'}"
                 + (f" (E{w.effect})" if w else ""),
                 f"Armour: {a.name if a else 'none'}"
                 + (f" (-{a.effect})" if a else ""), ""]
        for st in self.STATS:
            lines.append(f"{st}: {self.stats[st]}")
        if self.raises:
            lines += ["", f"Raises left: {self.raises}"]
        return "\n".join(lines)

    # What each animation id MEANS, which took a while to pin down.
    #
    # The client names exactly one of them. Its exploration key handler
    # (d.java:1530-1570) turns the four directions into four animations:
    #
    #     LEFT   x-1   anim 14         RIGHT  x+1   anim 206 = 78 | 128
    #     UP     y-1   anim 142 = 14|128   DOWN   y+1   anim 78  = 14 + 64
    #
    # So 14 is walk, +64 is the set facing away from the camera, and bit 7
    # mirrors either one (j.java reads `e & 127` for the script, `e & 128`
    # for the flip). Everything else was read off the art itself, frame by
    # frame, with tools/showcase.py — and the ids turn out to mean the same
    # thing for every creature, which an earlier comment here denied:
    #
    #      1 stand      2 a burst of fire *            4 swing
    #      5 stagger    6 fall down dead               7 die, spirit rises
    #      8 cast       9 thrust      10/11 throw      12 draw a bow
    #     14 walk      15 stand, one frame
    #     17-23 projectiles and impacts: arrow, burning arrow, stone,
    #           flame, fireball, explosion, green splash
    #
    # * 2 is the one that is genuinely unclear. The creature stands, a
    #   fireball engulfs it, and then — depending on the creature — it is
    #   either standing again or gone. That is either arriving in a burst of
    #   fire or being destroyed by one, and nothing in the jar says which.
    #
    # A creature has only some of these. Asking for one it lacks throws
    # "Unable to get anim N for monster id M" inside the client's animation
    # thread, which the game shows as an Error dialog — so always go through
    # anim(), never a literal.
    ANIM_STAND, ANIM_APPEAR, ANIM_SWING = 1, 2, 4
    ANIM_STAGGER, ANIM_DIE, ANIM_WALK = 5, 6, 14
    ANIM_AWAY, ANIM_MIRROR = 64, 128

    ANIM_NAMES = {
        1: "stand", 2: "fire burst", 4: "swing", 5: "stagger", 6: "die",
        7: "die (spirit)", 8: "cast", 9: "thrust", 10: "throw",
        11: "throw", 12: "bow", 14: "walk", 15: "stand (1 frame)",
        17: "arrow",
        18: "burning arrow", 19: "stone", 20: "flame", 21: "fireball",
        22: "explosion", 23: "splash",
    }

    ANIM_PREFS = {
        "idle":   (1, 15, 14),
        "walk":   (14, 1, 15),
        "attack": (4, 9, 12, 8, 10, 1),
        "hurt":   (5, 6, 1),
        "die":    (6, 7, 5),
    }

    @property
    def npc_creature(self):
        """The townsfolk sheet. Every fighting creature has the combat
        animations 14/15/17; the NPC sheet instead has 3, which nothing else
        does — 0x0e in Shirad's Forge, 0x3c in Sterling Lake."""
        for c in self.creatures:
            if 3 in self.res.anims(11, c):
                return c
        return None

    def containers(self, location):
        """Every crate and barrel on a map, found by its obstacle nibble."""
        mp = self.map(location)
        if not mp:
            return []
        out = []
        for y in range(mp.h):
            for x in range(mp.w):
                o = mp.obstacle(x, y)
                if o == TileMap.CRATE:
                    out.append((x, y, "crate"))
                elif o == TileMap.BARREL:
                    out.append((x, y, "barrel"))
        return out

    def anim(self, creature, kind="idle"):
        """A valid animation id for this creature, degrading gracefully."""
        have = self.res.anims(11, creature)
        for a in self.ANIM_PREFS.get(kind, (1,)):
            if a in have:
                return a
        return min(have) if have else 1

    def victory_text(self):
        """Prefer a real line from the location's own type 3 table."""
        t = self.text()
        for key in (0x1974, 0x1988, 0x198a):
            if key in t:
                return t[key][:200]
        return "The way is clear."

    def add_mob(self, x, y, creature, hp=12):
        m = Mob(self.next_node, self.location, x, y, creature, hp=hp)
        self.mobs[m.node] = m
        self.next_node += 1
        return m

    # -- queries ------------------------------------------------------------

    def living(self):
        """Fighting creatures here. NPCs are nodes too, but they never fight,
        so they stay out of the combat list and out of tag 22."""
        return [m for m in self.mobs.values()
                if m.alive and m.location == self.location and not m.npc]

    def npcs(self):
        return [m for m in self.mobs.values()
                if m.alive and m.location == self.location and m.npc]

    def mob_at(self, x, y, location=None, include_npcs=True):
        loc = self.location if location is None else location
        for m in self.mobs.values():
            if m.alive and m.location == loc and m.x == x and m.y == y \
                    and (include_npcs or not m.npc):
                return m
        return None

    def occupied(self, x, y):
        return (x, y) == (self.hero_x, self.hero_y) or self.mob_at(x, y)

    def can_stand(self, x, y):
        mp = self.map()
        return bool(mp and mp.walkable(x, y))

    # -- state arrays the client needs --------------------------------------

    def node_states(self):
        """tag 25 -> d.l, covering every location like the table it indexes.

        State 2, not 1. k() renders anything at 1 or 2, but only state 2 is
        added to aF — and the draw loop walks aF (d.java:528), so a node at
        state 1 exists, blocks movement and takes its turn while never being
        drawn. 3 means gone.
        """
        s = bytearray(self.node_count)
        for m in self.mobs.values():
            s[m.node] = 2 if m.alive else 3
        return bytes(s)

    # -- type 1 entities ----------------------------------------------------

    # Which exit tile leads where. The tiles themselves come from the maps
    # (high nibble 1 = the "red tiles marked with green arrows" the Village
    # text tells you about); the destinations are a reconstruction.
    def entity_table(self):
        """The type 1 resource for this location: currently its exits.

        Set EOE_TEST_EXIT=1 to widen every doorway's trigger box by 3 tiles,
        so a transition fires almost as soon as you can walk. Useful because
        reaching a real doorway means winning a fight first and then crossing
        the map.
        """
        # EOE_TEST_EXIT=1 widens every doorway so transitions are easy to
        # reach. =2 additionally makes them teleport WITHIN the location, which
        # takes d.java's `var2[14] == this.L` branch: no map reload, no
        # resource fetch. That isolates "does the entity fire at all" from
        # "does the location reload work".
        mode = os.environ.get("EOE_TEST_EXIT", "")
        pad = 3 if mode else EXIT_RADIUS
        local = mode == "2"
        # The quest log is built client-side out of these rows (d.h()), so an
        # objective only exists as far as the game is concerned if some entity
        # carries its text key. Hand them out one per location, in key order,
        # so the log fills as the player travels.
        quests = self.quests()
        quest_for = {loc: quests[i][0] for i, loc in
                     enumerate(self.locations[:len(quests)])}

        painted = {loc: set(self.exit_tiles(loc)) for loc in self.locations}
        rows, state = [], 1
        for loc in self.locations:
            for n, ((x, y), dest) in enumerate(self.EXITS.get(loc, [])):
                dx, dy = self.arrival(dest, came_from=loc)
                if local:
                    mp = self.map(loc)
                    dest = loc
                    dx, dy = (mp.w // 2, mp.h // 2) if mp else (dx, dy)
                rows.append(exit_entity(state, loc, x, y, dest, dx, dy,
                                        radius=pad,
                                        quest=quest_for.get(loc)
                                        if n == 0 else None))
                state += 1
                # A doorway we had to invent has no red tile on it, so the
                # way back is invisible: you walk onto ordinary ground and
                # the map changes. Paint one, using the game's own mechanism
                # and the chapter's own art — a kind 6 patch covering the
                # whole map, which fires as soon as the location loads.
                if (x, y) not in painted.get(loc, ()):
                    mp = self.map(loc)
                    if mp:
                        tile = (mp.tile(x, y) & 240) | self.marker
                        rows.append(patch_entity(state, loc, x, y,
                                                 bytes([tile]),
                                                 box=(0, 0, mp.w, mp.h)))
                        state += 1
        # Interactables, built from the location's own action labels. The
        # crates and NPCs are drawn into the tilemap, so their real positions
        # were in the lost table; these are placed near where you arrive so
        # they are at least reachable.
        self.interactables = {}
        for loc in self.locations:
            mp = self.map(loc)
            if not mp:
                continue
            labels = dict(self.action_labels(loc))
            by_text = {v.lower(): k for k, v in labels.items()}

            # Crates and barrels sit on known tiles, so their entities go
            # exactly where the art is.
            for x, y, what in self.containers(loc):
                key = next((k for t, k in by_text.items() if what in t), None)
                if key is None:
                    continue
                # A crate is part of the tilemap, so the only way to make one
                # go away is to patch the map. Completing a kind 6 entity
                # applies its patch (d.java:976-988), so the crate is paired
                # with a patch that clears its obstacle nibble, and opening it
                # completes both: the crate vanishes and cannot be used twice.
                patch = state
                rows.append(patch_entity(patch, loc, x, y,
                                         bytes([self.map(loc).tile(x, y) & 15])))
                state += 1
                rows.append(interact_entity(state, loc, x, y, key,
                                            completes=(patch, state)))
                self.interactables[state] = (loc, labels[key], key)
                state += 1

            # The talkers stand where place_npcs() put them.
            for m in self.mobs.values():
                if m.location == loc and m.npc and getattr(m, "text_key", None):
                    rows.append(interact_entity(state, loc, m.x, m.y,
                                                m.text_key))
                    self.interactables[state] = (loc, m.label, m.text_key)
                    state += 1

        self.entity_count = state
        return rows

    ACTION_VERBS = ("destroy", "talk", "speak", "trade", "use", "search",
                    "open", "pick", "read")

    def action_labels(self, location):
        """The short command-like strings in a location's text table. These
        are the labels the lost entities carried: "Destroy Crate", "Talk to
        Hrom", "Trade". Fights are excluded — those are kind 2, not kind 3."""
        out = []
        for key, v in sorted(self.text(location).items()):
            low = v.lower()
            if len(v) < 26 and ":" not in v and "\n" not in v \
                    and low.startswith(self.ACTION_VERBS):
                out.append((key, v))
        return out

    def entity_states(self):
        """tag 21 -> d.i. An entity only fires while its state is 2
        (d.java b()), so everything armed has to be marked here."""
        s = bytearray(self.node_count)
        for i in range(1, getattr(self, "entity_count", 1)):
            s[i] = 2
        return bytes(s)

    def mob_table(self):
        """The type 9 resource: every node in the WHOLE world."""
        return [m.record(Mob.ANIM_ON_SPAWN in self.res.anims(11, m.creature))
                for m in self.mobs.values()]


# handlers.py is reloaded on every request, so the live game cannot live there —
# it would reset with each message. world.py is imported, never reloaded, so the
# singleton survives.
_INSTANCE = None


def get_world(reset=False):
    global _INSTANCE
    if _INSTANCE is None or reset:
        _INSTANCE = World()
    return _INSTANCE


# ------------------------------------------------------------ type 1 entities
#
# Layout recovered from d.java b() (the proximity scan) and a(Object) (the
# dispatch):
#
#   [0]  state index, into d.i (tag 21). MUST be 2 for the entity to fire.
#   [1]  location, or 0 for any
#   [2][3][4][5]  bounding box x1,y1,x2,y2. x2 == 0 means "no box, always on"
#   [6]  trigger: 0 = fire automatically when the hero is inside the box
#                 1 = offer it in the context list instead
#                 2 = on node id, 3 = on monster group
#   [8]  trigger target id
#   [9][10]  u16 quest-item key      [11] quest state
#   [12] kind:
#        1 = show a message   [14][15] u16 text key into the type 3 table
#        2 = start a fight    [13] count, [14..] node ids
#        3 = ask the server   sends opcode 11 with tag 1 = [0]
#        4 = EXIT             [14] destination location, [15] x, [16] y
#        5 = activate nodes   [14..] node ids
#        6 = tilemap patch    [14] loc [15] x [16] y [17] w [18] h [19..] tiles
#   [13] length of that tail
#
# and then FOUR length-prefixed blocks, each "u8 count" followed by that many
# bytes. Miss any of them and the client walks off the end of the record —
# `a(Object)` computes the second block's offset as
# `14 + [13] + 1 + rec[14 + [13]]` unconditionally, which on a record with only
# one block lands exactly one past the end:
#   "ArrayIndexOutOfBoundsException: Index 19 out of bounds for length 19".
#
#   block 1  prerequisites. count, then [mode, ids...] where mode 0 checks the
#            d.i entity states and 1 checks the d.l node states; every listed
#            id must already be state 3 or the entity does not fire (d.b())
#   block 2  ids to ARM      — state 1 becomes 2
#   block 3  ids to COMPLETE — state 2 becomes 3 (and fires any kind 6 patch
#                              belonging to them)
#   block 4  ids to DISABLE  — anything not already 3 becomes 4
#
# Together those three lists are the quest graph: finishing one entity can open
# the next, mark itself done, and switch off whatever it replaces.

def _block(ids=()):
    return bytes([len(ids)]) + bytes(ids)


def entity(state, location, kind, tail=b"", box=None, trigger=0,
           prereq=(), arms=(), completes=(), disables=(), quest=None,
           quest_kind=1):
    r = bytearray(14)
    r[0] = state
    r[1] = location
    if box:
        r[2], r[3], r[4], r[5] = box
    r[6] = trigger
    if quest:
        # d.h() builds the quest log from these three bytes: [9][10] is the
        # u16 text key of the objective and [11] says which list it goes in,
        # 1 for main and 2 for optional. It only reads rows whose state is 2.
        r[9], r[10] = (quest >> 8) & 0xFF, quest & 0xFF
        r[11] = quest_kind
    r[12] = kind
    r[13] = len(tail)
    r += bytes(tail)
    # block 1 carries the mode byte ahead of the ids, so its count includes it
    r += bytes([len(prereq) + 1, 0]) + bytes(prereq)
    r += _block(arms) + _block(completes) + _block(disables)
    return r


# How far the trigger box reaches around a doorway tile. Zero: a doorway is
# ordinary walkable ground with a red tile painted on it, so the box is the
# tile, and you step on it to use it. (This was 1 while doorways were being
# looked for in the high nibble, which finds the walk-mask overrides instead —
# piers and the like — and those really cannot be stood on.)
EXIT_RADIUS = 0


def exit_entity(state, location, x, y, dest, dx, dy, radius=EXIT_RADIUS,
                quest=None):
    """A red exit tile.

    The trigger is this bounding box, NOT the tile's appearance — d.b() checks
    `x1 <= heroX < x2 && y1 <= heroY < y2` and nothing about the tilemap. The
    red-and-green tiles are only the artist telling you where the boxes are.

    radius widens the box further, which is how EOE_TEST_EXIT makes
    transitions testable without walking across a 40x40 map to find a doorway.
    """
    return entity(state, location, kind=4, tail=bytes([dest, dx, dy]),
                  box=(max(0, x - radius), max(0, y - radius),
                       x + 1 + radius, y + 1 + radius),
                  quest=quest)


def patch_entity(state, location, x, y, tiles, w=1, h=1, box=None):
    """A kind 6 entity: a rectangle of the tilemap, replaced.

    d.java b(byte[]) copies `[18]` rows of `[17]` bytes from offset 19 into
    the live map at `[15],[16]`, so the payload is loc, x, y, w, h and then
    the tiles themselves.

    Its box is the patched tile. That is deliberate: a crate's tile is an
    obstacle, so nobody can stand on it, so the entity never fires by entry
    and only ever runs when something completes it.
    """
    return entity(state, location, kind=6,
                  tail=bytes([location, x, y, w, h]) + bytes(tiles),
                  box=box or (x, y, x + 1, y + 1))


def interact_entity(state, location, x, y, label_key, w=2, h=2,
                    completes=()):
    """Something you can walk up to and use — a crate, an NPC.

    trigger 1 puts it in d.S instead of firing on entry, and pressing the
    action key in exploration builds a "Choose action" menu out of everything
    in range (d.java:1539). The label comes from the text key at [7][8], so
    these read exactly as the game wrote them: "Destroy Crate", "Talk to Hrom".

    kind 3 sends opcode 11 with the entity's state index, which is how the
    server gets to decide what was inside.
    """
    r = entity(state, location, kind=3, tail=b"",
               box=(max(0, x - 1), max(0, y - 1), x + w, y + h), trigger=1,
               completes=completes)
    r[7] = (label_key >> 8) & 0xFF
    r[8] = label_key & 0xFF
    return r


def message_entity(state, location, x, y, text_key, w=1, h=1):
    return entity(state, location, kind=1,
                  tail=bytes([(text_key >> 8) & 0xFF, text_key & 0xFF]),
                  box=(x, y, x + w, y + h))


def _travel(self, location):
    """Follow the player through an exit. The world is already populated
    everywhere, so this only moves our idea of where the hero is."""
    self.location = location
    self.hero_x, self.hero_y = self.arrival(location)


def _refresh_npcs(self):
    """Re-place the townsfolk after loading a save.

    from_dict() restores the saved mob list wholesale, and saves written
    before NPCs existed simply have none — so they would never reappear.
    """
    for loc in self.locations:
        if not any(m.npc and m.location == loc for m in self.mobs.values()):
            self.place_npcs(loc)


World.refresh_npcs = _refresh_npcs
World.travel = _travel


# ----------------------------------------------------------------- persistence
#
# How the original did it, recovered from i.java:
#
#   * The client keeps a byte[] token in a RecordStore called "key" (i.java:95).
#   * On hello (opcode 1) it sends that token as tag 1, if it has one.
#   * Whenever an opcode 1/2/19 reply has status 1 or 5 and carries a byte[] in
#     tag 21, the client overwrites its stored key with it (i.java:475).
#   * The opcode 1 reply's tag 20 is the account's hero list. Empty -> the
#     client jumps straight to the create-hero screen; otherwise it shows
#     "Select hero", and picking one sends opcode 4 with tag 1 = that name.
#
# So the account lives on the server and the handset only ever holds a token.
# We keep the same shape: a key file per account, a world per hero.

import json
import uuid

SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves")


def _world_to_dict(self):
    return {
        "game": self.game,
        "location": self.location,
        "hero_x": self.hero_x, "hero_y": self.hero_y,
        "hero_hp": self.hero_hp, "hero_max": self.hero_max,
        "next_node": self.next_node,
        "stats": self.stats, "level": self.level, "xp": self.xp,
        "gold": self.gold, "raises": self.raises,
        "inventory": self.inventory, "equipped": self.equipped,
        "mobs": [{"node": m.node, "location": m.location, "x": m.x, "y": m.y,
                  "creature": m.creature, "hp": m.hp, "max_hp": m.max_hp,
                  "alive": m.alive, "npc": m.npc,
                  "label": getattr(m, "label", None),
                  "text_key": getattr(m, "text_key", None)}
                 for m in self.mobs.values()],
    }


def _world_from_dict(self, d):
    self.location = d.get("location", self.location)
    self.hero_x = d.get("hero_x", self.hero_x)
    self.hero_y = d.get("hero_y", self.hero_y)
    self.hero_hp = d.get("hero_hp", self.hero_max)
    self.hero_max = d.get("hero_max", self.hero_max)
    self.next_node = d.get("next_node", 1)
    self.stats.update(d.get("stats") or {})
    self.level = d.get("level", 1)
    self.xp = d.get("xp", 0)
    self.gold = d.get("gold", 50)
    self.raises = d.get("raises", 0)
    self.inventory = d.get("inventory") or self.inventory
    self.equipped = d.get("equipped") or self.equipped
    self.refresh_npcs()
    self.mobs = {}
    for md in d.get("mobs", []):
        m = Mob(md["node"], md["location"], md["x"], md["y"], md["creature"],
                hp=md.get("max_hp", 12), npc=md.get("npc", False))
        m.hp = md.get("hp", m.max_hp)
        m.alive = md.get("alive", True)
        if md.get("label"):
            m.label = md["label"]
        if md.get("text_key"):
            m.text_key = md["text_key"]
        self.mobs[m.node] = m
    return self


World.to_dict = _world_to_dict
World.from_dict = _world_from_dict


class Saves:
    """accounts: key -> {game: [hero names]}.  heroes: "game:name" -> World.

    Heroes are scoped to a chapter because the original was: prod4 served
    Shirad's Forge and prod5 Sterling Lake, as separate servers with separate
    accounts. The client only ever sees the list for whichever chapter it is.
    """

    def __init__(self, path=None):
        self.path = path or os.path.join(SAVE_DIR, "game.json")
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.data = {"accounts": {}, "heroes": {}}
        if os.path.exists(self.path):
            try:
                with open(self.path) as fh:
                    self.data = json.load(fh)
            except (ValueError, OSError):
                pass
        self.live = {}          # hero name -> live World

    def flush(self):
        tmp = self.path + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(self.data, fh, indent=1)
        os.replace(tmp, self.path)

    # -- accounts -----------------------------------------------------------

    def new_key(self):
        key = uuid.uuid4().hex[:16]
        self.data["accounts"][key] = {}
        self.flush()
        return key

    def known(self, key):
        return key in self.data["accounts"]

    def _slot(self, key, game):
        acct = self.data["accounts"].setdefault(key, {})
        if isinstance(acct, list):          # migrate the old flat format
            acct = {DEFAULT_GAME: acct}
            self.data["accounts"][key] = acct
        return acct.setdefault(game, [])

    def heroes(self, key, game=DEFAULT_GAME):
        return list(self._slot(key, game))

    # -- heroes -------------------------------------------------------------

    def create_hero(self, key, name, game=DEFAULT_GAME):
        slot = self._slot(key, game)
        if name in slot:
            return False
        slot.append(name)
        self.data["heroes"][f"{game}:{name}"] = World(game).to_dict()
        self.flush()
        return True

    def taken(self, key, name, game=DEFAULT_GAME):
        return name in self._slot(key, game)

    def world(self, name, game=None):
        """The live World for a hero, restored from disk on first use. A hero
        belongs to one chapter, recorded in the save."""
        game = game or DEFAULT_GAME
        slot = f"{game}:{name}"
        if slot not in self.live:
            saved = self.data["heroes"].get(slot)
            if saved is None:
                # Pre-chapter-scoping saves were keyed by bare name. Only adopt
                # one if it belongs to this chapter, or a hero from another
                # chapter with the same name loads the wrong world entirely —
                # the client then asks for resource ids that do not exist in
                # its jar ("Unable to get resources from server").
                legacy = self.data["heroes"].get(name)
                if legacy and (legacy.get("game") or DEFAULT_GAME) == game:
                    saved = legacy
            saved = saved or {}
            w = World(saved.get("game") or game)
            if saved:
                w.from_dict(saved)
            self.live[slot] = w
        return self.live[slot]

    def save(self, name, game=DEFAULT_GAME):
        slot = f"{game}:{name}"
        if slot in self.live:
            self.data["heroes"][slot] = self.live[slot].to_dict()
            self.flush()


_SAVES = None


def saves():
    global _SAVES
    if _SAVES is None:
        _SAVES = Saves()
    return _SAVES
