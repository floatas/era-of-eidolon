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

    def is_exit(self, x, y):
        """High nibble 1 flips the walkability test — in practice these are the
        'red tiles marked with green arrows' that move you between locations."""
        return (self.tile(x, y) & 240) == 16


# ------------------------------------------------------------------ game state

class Mob:
    def __init__(self, node, location, x, y, creature, hp=12, anim=1):
        self.node = node
        self.location = location
        self.x, self.y = x, y
        self.creature = creature
        self.hp = self.max_hp = hp
        self.anim = anim
        self.alive = True

    def record(self):
        """A 19-byte type 9 row."""
        r = bytearray(19)
        r[0] = self.node
        r[1] = self.location
        r[3] = self.x
        r[4] = self.y
        r[12] = self.creature
        r[13] = self.anim
        r[15] = 1
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
        self._names = {}
        self.locations = sorted(
            int(n[1:], 16) for n in self.res.files
            if re.fullmatch(r"2[0-9a-f]+", n) and not n.startswith(("10", "11")))
        self.creatures = sorted(
            int(n[1:], 16) for n in self.res.files
            if re.fullmatch(r"7[0-9a-f]+", n) and not n.startswith(("10", "11"))
            and int(n[1:], 16) != 0)          # 0 is the hero's own sprite
        self.exits = self._build_exits()

        self.location = self.locations[0] if self.locations else 1
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
        self.mobs = {}
        self.next_node = 1
        self.node_count = 32
        self.populate()

    # -- map access ---------------------------------------------------------

    def map(self, location=None):
        loc = self.location if location is None else location
        if loc not in self.maps:
            blob = self.res.get(2, loc)
            self.maps[loc] = TileMap(blob) if blob else None
        return self.maps[loc]

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

    def exit_tiles(self, location):
        """The 'red tiles marked with green arrows'. Adjacent ones are one
        doorway, so collapse them into clusters."""
        mp = self.map(location)
        if not mp:
            return []
        raw = [(x, y) for y in range(mp.h) for x in range(mp.w) if mp.is_exit(x, y)]
        clusters = []
        for x, y in raw:
            for c in clusters:
                if any(abs(x - cx) <= 1 and abs(y - cy) <= 1 for cx, cy in c):
                    c.append((x, y))
                    break
            else:
                clusters.append([(x, y)])
        return [c[0] for c in clusters]

    def _build_exits(self):
        """Wire the locations together. The real game's layout is in the lost
        type 1 tables, so this links each doorway to the next location in id
        order and always keeps a way back to the first."""
        out = {}
        for i, loc in enumerate(self.locations):
            tiles = self.exit_tiles(loc)
            if not tiles:
                continue
            links = []
            for n, tile in enumerate(tiles):
                if loc == self.locations[0]:
                    dest = self.locations[(n + 1) % len(self.locations)]
                else:
                    dest = self.locations[0] if n == 0 else \
                        self.locations[(i + n) % len(self.locations)]
                if dest != loc:
                    links.append((tile, dest))
            out[loc] = links
        return out

    EXITS = property(lambda self: self.exits)

    def spawn_point(self, location):
        """A walkable tile to stand on: next to a doorway if there is one (but
        not on it, or you would bounce straight back), else near the middle."""
        mp = self.map(location)
        if not mp:
            return 1, 1
        for (ex, ey) in self.exit_tiles(location):
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1)):
                x, y = ex + dx, ey + dy
                if mp.walkable(x, y) and not mp.is_exit(x, y):
                    return x, y
        cx, cy = mp.w // 2, mp.h // 2
        best = None
        for y in range(mp.h):
            for x in range(mp.w):
                if mp.walkable(x, y) and not mp.is_exit(x, y):
                    d = abs(x - cx) + abs(y - cy)
                    if best is None or d < best[0]:
                        best = (d, x, y)
        return (best[1], best[2]) if best else (1, 1)

    def arrival(self, location):
        return self.spawn_point(location)

    # -- population ---------------------------------------------------------

    def populate(self):
        """Place creatures near the player. Which creatures a chapter has is in
        its jar (types 7/8/11 share an id per creature); where they stood is in
        the lost type 1/9 tables, so this scatters a couple of them on walkable
        ground within sight."""
        self.mobs.clear()
        self.next_node = 1
        mp = self.map()
        if not mp or not self.creatures:
            return
        # Deterministic per location, so a save reloads the same encounter.
        rng = random.Random(f"{self.game}:{self.location}")
        picks = [self.creatures[rng.randrange(len(self.creatures))]
                 for _ in range(2)]
        placed = 0
        for creature in picks:
            for _ in range(60):
                x = self.hero_x + rng.randint(-5, 5)
                y = self.hero_y + rng.randint(-5, 5)
                if (x, y) == (self.hero_x, self.hero_y):
                    continue
                if mp.walkable(x, y) and not mp.is_exit(x, y) \
                        and not self.mob_at(x, y):
                    m = self.add_mob(x, y, creature, hp=6 + 2 * placed)
                    m.anim = self.anim(creature, "idle")
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

    def hero_sheet(self):
        lines = [f"Level {self.level}   XP {self.xp}/{self.xp_for_next()}",
                 f"Life {self.hero_hp}/{self.hero_max}   Gold {self.gold}", ""]
        for st in self.STATS:
            lines.append(f"{st}: {self.stats[st]}")
        if self.raises:
            lines += ["", f"Raises left: {self.raises}"]
        return "\n".join(lines)

    # Animation ids are per creature — the keys of its type 11 props table —
    # and they are NOT uniform. Sterling Lake's 0x3a and 0x37 have no attack
    # (4); Shirad's Forge's 0x2a has no walk (2). Asking for one a creature
    # lacks throws "Unable to get anim N for monster id M" inside the client's
    # animation thread, which the game shows as an Error dialog.
    ANIM_PREFS = {
        "idle":   (1, 2, 5, 14),
        "walk":   (2, 1, 5, 14),
        "attack": (4, 5, 6, 3, 2, 1),
        "hurt":   (5, 6, 1),
    }

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
        return [m for m in self.mobs.values()
                if m.alive and m.location == self.location]

    def mob_at(self, x, y):
        for m in self.living():
            if m.x == x and m.y == y:
                return m
        return None

    def occupied(self, x, y):
        return (x, y) == (self.hero_x, self.hero_y) or self.mob_at(x, y)

    def can_stand(self, x, y):
        mp = self.map()
        return bool(mp and mp.walkable(x, y))

    # -- state arrays the client needs --------------------------------------

    def node_states(self):
        """tag 25 -> d.l. 1 or 2 = present, 3 = gone (d.java:216)."""
        s = bytearray(self.node_count)
        for m in self.mobs.values():
            if m.location == self.location:
                s[m.node] = 1 if m.alive else 3
        return bytes(s)

    # -- type 1 entities ----------------------------------------------------

    # Which exit tile leads where. The tiles themselves come from the maps
    # (high nibble 1 = the "red tiles marked with green arrows" the Village
    # text tells you about); the destinations are a reconstruction.
    EXITS = {
        1: [((10, 10), 2), ((20, 26), 3), ((15, 31), 4), ((12, 33), 5)],
        2: [((28, 4), 1)],
        3: [((28, 0), 1)],
        4: [((29, 23), 1)],
        5: [((3, 4), 1)],
    }

    def arrival(self, location):
        """Where to drop the hero when entering a location: next to its exit
        tile but not on it, or the map centre if there is none. Landing on the
        tile would re-fire the exit and bounce straight back."""
        mp = self.map(location)
        if not mp:
            return 1, 1
        tiles = [t for t, _ in self.EXITS.get(location, [])]
        for (ex, ey) in tiles:
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1)):
                x, y = ex + dx, ey + dy
                if mp.walkable(x, y) and not mp.is_exit(x, y):
                    return x, y
        for y in range(mp.h // 2, mp.h):
            for x in range(mp.w // 2, mp.w):
                if mp.walkable(x, y):
                    return x, y
        return 1, 1

    def entity_table(self):
        """The type 1 resource for this location: its exits, plus one sign
        carrying a real line from the location's own type 3 text."""
        rows, state = [], 1
        for (x, y), dest in self.EXITS.get(self.location, []):
            dx, dy = self.arrival(dest)
            rows.append(exit_entity(state, self.location, x, y, dest, dx, dy))
            state += 1
        self.entity_count = state
        return rows

    def entity_states(self):
        """tag 21 -> d.i. An entity only fires while its state is 2
        (d.java b()), so everything armed has to be marked here."""
        s = bytearray(self.node_count)
        for i in range(1, getattr(self, "entity_count", 1)):
            s[i] = 2
        return bytes(s)

    def mob_table(self):
        """The type 9 resource: every node in this location, alive or not."""
        return [m.record() for m in self.mobs.values()
                if m.location == self.location]


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
#   then at p = 14 + [13]:
#        [p]   prerequisite count N (the loop runs 1..N-1, so N=1 means none)
#        [p+1] 0 = check d.i states, 1 = check d.l states
#        [p+2..] node ids that must already be state 3

def entity(state, location, kind, tail=b"", box=None, trigger=0, prereq=()):
    r = bytearray(14)
    r[0] = state
    r[1] = location
    if box:
        r[2], r[3], r[4], r[5] = box
    r[6] = trigger
    r[12] = kind
    r[13] = len(tail)
    r += bytes(tail)
    r += bytes([len(prereq) + 1, 0]) + bytes(prereq)
    return r


def exit_entity(state, location, x, y, dest, dx, dy):
    """A red exit tile. The box is the single tile, so stepping on it fires."""
    return entity(state, location, kind=4, tail=bytes([dest, dx, dy]),
                  box=(x, y, x + 1, y + 1))


def message_entity(state, location, x, y, text_key, w=1, h=1):
    return entity(state, location, kind=1,
                  tail=bytes([(text_key >> 8) & 0xFF, text_key & 0xFF]),
                  box=(x, y, x + w, y + h))


def _travel(self, location):
    """Follow the player through an exit: new map, new population, new state."""
    self.location = location
    self.hero_x, self.hero_y = self.arrival(location)
    self.populate()


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
        "mobs": [{"node": m.node, "location": m.location, "x": m.x, "y": m.y,
                  "creature": m.creature, "hp": m.hp, "max_hp": m.max_hp,
                  "alive": m.alive} for m in self.mobs.values()],
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
    self.mobs = {}
    for md in d.get("mobs", []):
        m = Mob(md["node"], md["location"], md["x"], md["y"], md["creature"],
                hp=md.get("max_hp", 12))
        m.hp = md.get("hp", m.max_hp)
        m.alive = md.get("alive", True)
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
