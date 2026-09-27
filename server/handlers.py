"""Per-opcode response handlers.

Hot-reloaded on every request by relay.py — edit freely while the game runs.
(relay.py itself is NOT reloaded; restart it after editing that.)

A handler takes (req) and returns bytes (a full response frame), or None to
fall through to the default. `req` has .opcode .game .chunks .body .session
plus .get(tag) / .all(tag) / .int_(tag).

Nothing here is guessed: build each handler from what the client's parser
expects, in ../decompiled-vf/. See ../protocol/PROTOCOL.md.

Reserved response tags (b.java run(), tag switch):
    0 -> session blob B, echoed back on every later request
    1 -> queued message dialog   2 -> immediate message
    4 -> static f   5 -> static h (int)   6 -> static e   7 -> static g
    3 and anything else -> this.d hashtable, keyed by tag
"""

import json
import os
import random
import struct
from collections import deque

from codec import (build_response, chunk_int, chunk_str, chunk_raw,
                   enc_utf8, T_STRUCT)
from catalogue import catalogue
from world import POTENCY_DIV, get_world, saves, World
import tiers

HANDLERS = {}


def session_world(req):
    """Which hero this request belongs to.

    Response tag 0 sets the client's session blob B, which it then echoes on
    every later request (b.java run(), tag 0). We put "<accountkey>:<hero>" in
    it, so the server knows both without any extra state on the handset —
    the same division the original used, where the phone held only a token.
    """
    blob = (req.session or b"").decode("utf-8", "replace")
    key, _, hero = blob.partition(":")
    if hero:
        st = saves()
        w = st.world(hero, req.game)
        st.touch(hero, req.game)
        return w, key, hero
    return get_world(), key, None


def handler(opcode):
    def deco(fn):
        HANDLERS[opcode] = fn
        return fn
    return deco


# ---------------------------------------------------------------- world data
#
# Resource names are "/" + restype + hex(id). Type 1 id 0 is "/10" and type 9
# id 0 is "/90"; NEITHER ships in any jar — both were served at runtime. Every
# other world resource IS local (tools/dump_world.py): type 2 tilemaps, type 3
# location text, type 10 quests, type 7/8/11 creature sprite/anim/props.
#
#   TYPE 1 - placed entities. Variable length.
#     [0] state index   [1] location (0 = global)
#     [6] trigger kind: 2 = on node id, 3 = on monster group
#     [8] trigger target   [9][10] u16 text key -> type 3 dialogue
#     [11] quest state  [12] kind   [13] tail length
#     kind 6 is a TILEMAP PATCH, not an exit (d.java b(byte[])):
#       [14] location  [15] x  [16] y  [17] w  [18] h  [19..] w*h tiles
#     kind 9 carries an embedded `f` record at [14..14+[13]]
#
#   TYPE 9 - map nodes / monsters. 19 bytes fixed.
#     [0] node index  [1] location  [2] group  [3] x  [4] y
#     [11] respawn seed  [12] creature id  [13] initial anim  [15] active

# Entities only draw when (e & 63) != 0 (j.java a(Graphics,...)). `e` is set
# from `a` by o() at the start of each turn, and `a` comes from the anim byte
# of the tag 22 records — or, for mobs built in k(), from type 9 field [13].
# Send 0 and the entity is present, blocks movement, takes its turn, and is
# never drawn. Valid ids are the keys of the type 11 props table.
# Only ever send an animation id the creature actually has — see
# World.anim(). A missing one throws inside the client's animation thread:
#   "Unable to get anim 4 for monster id 1"
ANIM_IDLE = 1

TURN_BUDGET = 720

# The six server-supplied action-bar slots, in the order the client draws them
# (its own icons: move, melee, ranged, shield, spell, skill). mode 1 = walk a
# path, 2 = pick a target tile, 0 = act on the current target with no cursor.
# The slot TITLES come from the client (d.java:27):
#   Movement, Melee attack, Ranged attack, Defence, Offence spells,
#   Defensive spells
# The entries inside them are real skills, one per category, chosen as the
# cheapest of their type — the ones a new hero would actually own. Their Time
# costs are watAgame's own (notes/eoe-arena), not guesses: Move is 40 a tile
# and Hit is 60, so a turn is eighteen steps or twelve blows, not the
# twenty-four and six the invented numbers gave.
#
# "Defensive spells" could be either protective magic or healing; a solo hero
# needs the heal, so that slot is Minor Cure.
_SLOTS = [
    ("Move",       1),
    ("Hit",        2),
    ("Shoot",      2),
    ("Dodge",      0),
    ("Zap",        2),
    ("Minor Cure", 0),
]

# what to fall back to if a name is ever missing from the catalogue
_SLOT_FALLBACK = {"Move": 40, "Hit": 60, "Shoot": 60,
                  "Dodge": 40, "Zap": 60, "Minor Cure": 60}


def _action_table():
    c = catalogue()
    known = {i.name.lower(): i for k in ("skill", "spell")
             for i in c.get(k)}
    out = []
    for name, mode in _SLOTS:
        it = known.get(name.lower())
        out.append((name, it.time if it and it.time else _SLOT_FALLBACK[name],
                    mode))
    return out


ACTIONS = _action_table()
MOVE_COST = ACTIONS[0][1]
ATTACK_COST = ACTIONS[1][1]

# The client reads an action's cost as a u8, so nothing may exceed 255. Three
# bows do (Fire Bow 297, Giant Bow 304, Striker is fine at 248).
MAX_COST = 255


def swing_cost(w, label="Hit"):
    """What one blow of this weapon costs of the 720-unit turn.

    watAgame recorded a time on every weapon and it trades against effect —
    96 for the Bloody Blade against 211 for the Smasher, correlating at
    +0.65 across the melee list. Swords swing twice for what an axe swings
    once. Charging the flat skill time threw that whole axis away.

    Only the hero pays this; creatures carry no weapon and keep the skill
    cost.
    """
    if label not in ("Hit", "Shoot"):
        return ATTACK_COST
    it = w.weapon()
    if it and getattr(it, "time", 0):
        return min(MAX_COST, it.time)
    return ATTACK_COST


def byte_table(rows=()):
    """Encode a byte[][] the way g.b(DataInputStream) reads it."""
    out = bytes([len(rows)])
    for r in rows:
        out += bytes([len(r)]) + bytes(r)
    return out


def enc_f(label, name="", f=0, g=0, desc="", k=b""):
    """An `f` record (f.java, the DataInputStream constructor):

        u8 len + bytes -> a (label)      u8 len + bytes -> b (name)
        i8 -> f                          u8 -> g
        u8 len + bytes -> c (desc)       u16 len + bytes -> k (payload)

    For an action-bar entry the k payload is what makes it usable:
        k[0],k[1]  u16 time cost      k[2]  1 = path/move, 2 = target
    An action sent as a plain string is inert — the client checks `instanceof f`
    and silently does nothing.
    """
    def s(x):
        b = x.encode("utf-8")
        return bytes([len(b)]) + b
    return (s(label) + s(name) + bytes([f & 0xFF, g & 0xFF]) + s(desc)
            + struct.pack(">H", len(k)) + k)


def chunk_f(tag, *args, **kw):
    return chunk_raw(tag, 4, enc_f(*args, **kw))


def push_resource(tag, key, payload):
    """A type-5 chunk: u16 resource key, then the resource body."""
    return chunk_raw(tag, 5, struct.pack(">H", key) + payload)


# ------------------------------------------------------- turn-result records
#
# d.java:1073 plays back the Vector in tag 20 of the opcode 13 reply:
#
#   [0] kind  [1] duration (<<4 ms)  [2] 1 = refresh after
#   [3] 0 = green text, else red     [4] message length
#   [5..] message, then payload at p = 5 + [4]
#
#   kind 0  set anims: p[0] count, then (node, anim) pairs
#   kind 1  attack:    p[0] attacker, p[1] anim, p[2] victims,
#                      then (node, dmgHi, dmgLo) each
#   kind 2  walk:      p[0] node, p[1] x, p[2] y, p[3] anim
#   kind 4  teleport:  p[0] node, p[1] x, p[2] y
#   kind 6  remove:    p[0] count, then node ids

def result(kind, payload, msg="", dur=220, refresh=0, red=False):
    """The playback loop reads as[p] and as[p+1] *before* switching on the kind
    (d.java:1077), so every record needs at least two payload bytes no matter
    what kind it is. A shorter one throws ArrayIndexOutOfBounds inside the
    client's animation thread."""
    m = msg.encode("utf-8")
    payload = bytes(payload)
    if len(payload) < 2:
        payload += bytes(2 - len(payload))
    return bytes([kind, dur, refresh, 1 if red else 0, len(m)]) + m + payload


def res_walk(node, x, y, anim=None):
    # dur is held for dur<<4 ms. 110 is 1.76s, so each square can be seen.
    return result(2, [node, x, y, ANIM_IDLE if anim is None else anim], dur=110)


def res_attack(attacker, victims, anim=ANIM_IDLE, msg="", red=True, dur=220):
    p = [attacker, anim, len(victims)]
    for node, dmg in victims:
        p += [node, (dmg >> 8) & 0xFF, dmg & 0xFF]
    return result(1, p, msg=msg, red=red, dur=dur)


def res_remove(nodes):
    return result(6, [len(nodes)] + list(nodes), dur=40)


def parse_actions(buf):
    """Undo d.java:768's serialisation of the queued action stack:

        u8 len + name bytes    u16 timestamp    u8 mode
        mode 1: u8 stepCount, then (x,y) per step
        mode 2: x, y
    """
    out, i = [], 0
    while i < len(buf):
        nlen = buf[i]
        i += 1
        if i + nlen + 3 > len(buf):
            break
        name = buf[i:i + nlen].decode("utf-8", "replace")
        i += nlen
        ts = int.from_bytes(buf[i:i + 2], "big")
        i += 2
        mode = buf[i]
        i += 1
        if mode == 1:
            if i >= len(buf):
                break
            steps, i = buf[i], i + 1
            pts = []
            for _ in range(steps):
                if i + 1 >= len(buf):
                    break
                pts.append((buf[i], buf[i + 1]))
                i += 2
            out.append((name, ts, mode, pts))
        elif mode == 2:
            if i + 1 >= len(buf):
                break
            out.append((name, ts, mode, [(buf[i], buf[i + 1])]))
            i += 2
        else:
            # mode 0 queues with a single byte: the current target's node id
            # (d.java:1489, new byte[]{(byte) this.ac.b}).
            node = buf[i] if i < len(buf) else 0
            i += 1
            out.append((name, ts, mode, [(node, None)]))
    return out


# ------------------------------------------------------------------ handlers

@handler(1)
def hello(req):
    """Opcode 1 — hello, and the whole save/resume mechanism.

    The client sends its stored token as tag 1 if it has one (i.java:95-108).
    We answer with:
        tag 0   session blob, echoed on every later request
        tag 20  the account's heroes, as `f` records — i.java case 1 shows
                "Select hero" for these, or jumps to create-hero if empty
        tag 21  a byte[] token; the client writes it to its "key" RecordStore
                (i.java:475) and sends it back on the next launch

    Status must be 1 or 5 for the client to store the key at all.
    """
    st = saves()
    key = req.get(1).decode("utf-8", "replace") if req.get(1) else ""
    if not st.known(key):
        key = st.new_key()

    heroes = st.heroes(key, req.game)
    chunks = [chunk_raw(0, 0, key.encode()),
              chunk_raw(21, 0, key.encode())]
    for name in heroes:
        chunks.append(chunk_f(20, name, name))
    print(f"    \033[35mhello: account {key} heroes={heroes or '(none)'}\033[0m")
    return build_response(status=1, chunks=chunks)


@handler(4)
def select_hero(req):
    """Opcode 4 — the player picked an existing hero (tag 1 = its name).
    Status 1 sends them to the main menu (i.java case 4 -> screen 8)."""
    st = saves()
    blob = (req.session or b"").decode("utf-8", "replace")
    key = blob.partition(":")[0]
    name = req.get(1).decode("utf-8", "replace")
    if name not in st.heroes(key, req.game):
        return build_response(status=2, chunks=[chunk_str(20, "No such hero.")])
    w = st.world(name)
    # Where the panel thinks you are is remembered across a session, so a
    # hero resumed into a different room than the last one left kept showing
    # the old name until something else happened to carry a room id. The
    # save knows where he is standing; say so.
    w.note_place(w.location)
    w.shop_view = None
    w.shop_which = None
    print(f"    \033[35mresume: {name} in "
          f"{w.LOCATION_NAMES.get(w.location, w.location)} "
          f"({w.hero_x},{w.hero_y}) hp {w.hero_hp}/{w.hero_max}\033[0m")
    return build_response(status=1, chunks=[
        chunk_raw(0, 0, f"{key}:{name}".encode())])


@handler(5)
def create_hero(req):
    """Opcode 5 — create a hero (tag 1 = name, tag 2 = gender)."""
    st = saves()
    blob = (req.session or b"").decode("utf-8", "replace")
    key = blob.partition(":")[0] or st.new_key()
    name = req.get(1).decode("utf-8", "replace").strip()

    # Status 2 here is NOT an error dialog: i.java case 5 writes tag 20 straight
    # into the name field (`((c)var1).a(0).d`). It is the server suggesting a
    # name. So an empty or taken name gets a suggestion, not a complaint.
    if not name or st.taken(key, name, req.game):
        suggestion = name or "Hero"
        n = 1
        while st.taken(key, suggestion, req.game):
            n += 1
            suggestion = f"{name or 'Hero'}{n}"
        return build_response(status=2, chunks=[chunk_str(20, suggestion)])

    # req.game comes from the X-relay-url host: prod4 is Shirad's Forge,
    # prod5 is Sterling Lake. A hero belongs to whichever chapter made it.
    st.create_hero(key, name, req.game)
    print(f"    \033[35mnew hero: {name} ({req.game}) on account {key}\033[0m")
    return build_response(status=1, chunks=[
        chunk_raw(0, 0, f"{key}:{name}".encode())])

@handler(8)
def enter_world(req):
    """Opcode 8 — enter the game world.

    i.java case 8 fetches type 1 id 0 and type 9 id 0 with a null want-vector,
    so a cache miss dereferences null: the "resp(8)" NPE. Both must be pushed.
    d.java:105 then reads two byte[] straight off this response and
    dereferences the second without a null check:

        this.i = (byte[]) var6.d.get(21)   this.l = (byte[]) var6.d.get(25)
        this.n = new j[this.l.length]      <- NPE if tag 25 is absent

    The status picks the mode: i.java case 8 passes `var2.c == 2` to the map
    screen as its "in combat" flag. Status 1 is free-roam exploration, which is
    how the game should start; status 2 drops the player straight into a fight.

    This was status 2 for a long while, because with status 1 nothing appeared
    to respond to the movement keys. That turned out not to be the mode at all
    — the first step killed the client's paint thread on a missing animation
    (see Mob.record), and a dead paint thread looks exactly like a game that
    ignores input.
    """
    w, _, _ = session_world(req)
    return build_response(status=1, chunks=[
        push_resource(1, 0x0100, byte_table(w.entity_table())),  # type 1
        push_resource(3, 0x0900, byte_table(w.mob_table())),   # type 9
        chunk_raw(21, 0, w.entity_states()),
        chunk_raw(25, 0, w.node_states()),
        chunk_int(22, w.location),
        chunk_int(23, w.hero_x),
        chunk_int(24, w.hero_y),
        # d.java stores these as W,X: the square "Try to flee" returns to.
        chunk_int(26, w.hero_x),
        chunk_int(27, w.hero_y),
    ] + hud_chunks(w))


def sync(req, w):
    """The client attaches its own view of the world to outgoing messages via
    d.d(b): tag 11 = location, 12/13 = hero x/y, 10/14 = the state arrays.

    Location changes happen entirely client-side — a kind 4 exit sets d.I and
    reloads the map without asking us — so this is how the server finds out
    the player walked through a door."""
    # Tag 10 is d.i, the quest switches. Tag 14 is which creatures are dead.
    # Both ride along on Save & exit and on the fight request.
    blob = req.get(10) if hasattr(req, "get") else b""
    if blob:
        w.note_progress(blob)
    nodes = req.get(14) if hasattr(req, "get") else b""
    if nodes:
        for m in w.mobs.values():
            if m.node < len(nodes):
                m.alive = nodes[m.node] != 3
    loc = req.int_(11) if hasattr(req, "int_") else 0
    if loc and loc != w.location:
        w.travel(loc)
        w.note_place(w.location)
        return True
    x, y = req.int_(12), req.int_(13)
    if x or y:
        w.hero_x, w.hero_y = x, y
    w.note_place(w.location)
    return False


def entity_rows(w):
    """tag 22 of the opcode 12 reply — one byte[8] per entity (d.java:722):

        [0] node  [1] x  [2] y  [3][4] l  [5][6] m  [7] anim

    l and m are NOT current/max. From j.a(int,int):

        this.m = Math.min(this.l, this.m + damage)

    so **l is max HP and m is accumulated damage** — 0 means untouched, l means
    dead. The HUD confirms it (d.java:319): it paints a BLACK bar of width
    m * 109 / l over a full-looking panel, i.e. black is the missing part.
    Sending l = m = maxHP therefore blacks the whole bar out.
    """
    def row(node, x, y, cur, mx, anim=ANIM_IDLE):
        dmg = max(0, mx - cur)
        return bytes([node, x, y, mx >> 8, mx & 0xFF,
                      dmg >> 8, dmg & 0xFF, anim])

    rows = [row(0, w.hero_x, w.hero_y, w.hero_hp, w.hero_max, w.anim(0))]
    for m in w.fighters():
        rows.append(row(m.node, m.x, m.y, m.hp, m.max_hp, w.anim(m.creature)))
    if len(rows) == 1:                     # never leave aF with a lone hero
        rows.append(row(0, w.hero_x, w.hero_y, w.hero_hp, w.hero_max))
    return rows


@handler(12)
def turn(req):
    """Opcode 12 — turn state. Consumed by d.a(b) (d.java:708):

        tags 30..35 -> the six action menus
        tag 20, 21  -> the arena centre; the cursor is clamped to a diamond
                       around it, so 0,0 puts the playable area at the map
                       origin and nothing is reachable
        tag 22      -> repeated, one byte[8] per entity
    """
    w, _, hero = session_world(req)
    sync(req, w)
    # Tag 1 is the node ids the player engaged (one byte each). Tag 3 = 1
    # is "Auto fight": i.java then delivers THIS response to d.b, the result
    # handler, so it must be a finished fight and never status 1.
    w.begin_fight(list(req.get(1)), req.get(2))
    for m in w.fighters():
        m.phase = 1
        m.rest = False
    _tune_bosses(w)
    if req.int_(3) == 1:
        resp = auto_response(w, rng=random)
        if hero:
            saves().save(hero, w.game)
        return resp
    chunks = [chunk_int(20, w.hero_x), chunk_int(21, w.hero_y)]
    chunks += [chunk_raw(22, 0, r) for r in entity_rows(w)]
    # Every one of slots 0..5 must hold at least one `f`. While a slot is open
    # the client casts each entry to f unguarded (d.java:1059) — and when a
    # menu arrives empty it inserts the *String* "Empty" itself, which then
    # throws ClassCastException. So: no empty slots, no plain strings.
    for tag, (label, cost, mode) in zip(range(30, 36), ACTIONS):
        # the bar must show the same price the turn will charge
        cost = w.trained_time(label, swing_cost(w, label) if label in ("Hit", "Shoot") else cost)
        chunks.append(chunk_f(tag, label, label, k=bytes([0, cost, mode])))
    return build_response(status=1, chunks=chunks)


# ------------------------------------------------------------- turn resolution
#
# This is a TIMELINE, not "I move, then you move". d.java:1045 advances the
# turn clock in real time:
#
#     this.ag += secondsElapsed * 5;
#     if (this.ag > 720) { this.j(); }        // auto end turn
#
# and every queued action is stamped with the clock *after* its cost is added
# (d.java:1354). So a turn is 720 units of time that both sides spend: yours on
# actions (and on thinking — deliberating really does cost you), theirs on
# whatever the creatures do. The server's job is to merge both into one ordered
# script, which is why the client bothers to send the timestamps at all.

# d.java af, the queue entry "Try to flee" writes instead of an action.
FLEE = bytes((1, 102, 0, 0))
MELEE_CLS = ("sword", "axe", "hammer")


def _note(script, text, red=True, anim=None, node=0):
    payload = [0, 0] if anim is None else [1, node, anim]
    script.append(result(0, payload, msg=text, red=red))


def _step_toward(w, x, y, tx, ty, blocked):
    """One orthogonal step that gets closer. Diagonals are illegal, and a
    blocked axis tries the other before the creature gives up."""
    dx, dy = tx - x, ty - y
    cands = []
    if dx and abs(dx) >= abs(dy):
        cands.append((x + (1 if dx > 0 else -1), y))
    if dy:
        cands.append((x, y + (1 if dy > 0 else -1)))
    if dx and abs(dx) < abs(dy):
        cands.append((x + (1 if dx > 0 else -1), y))
    seen = []
    for nx, ny in cands:
        if (nx, ny) in seen:
            continue
        seen.append((nx, ny))
        if (nx, ny) in blocked or not w.can_stand(nx, ny):
            continue
        return nx, ny
    return None


def _step_away(w, x, y, tx, ty, blocked):
    opts = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    opts.sort(key=lambda p: -(abs(p[0] - tx) + abs(p[1] - ty)))
    for nx, ny in opts:
        if (nx, ny) in blocked or not w.can_stand(nx, ny):
            continue
        return nx, ny
    return None


def _blocked(w):
    tiles = {(m.x, m.y) for m in w.fighters()}
    tiles |= {(m.x, m.y) for m in w.npcs()}
    return tiles


def hero_timeline(w, actions):
    """(time, event) for everything the player queued, in clock order."""
    events = []
    for name, ts, mode, pts in sorted(actions, key=lambda a: a[1]):
        if mode == 1:
            # Spread the walk across the time the client charged for it, so a
            # long route genuinely takes longer than a short one. Zig-Zag
            # costs more per step than Move, which is the whole of its price.
            step = max(1, w.trained_time("Move", MOVE_COST))
            if name == "Zig-Zag":
                it = catalogue().find(name)
                step = max(step, it.time if it else 118)
            for i, (x, y) in enumerate(pts):
                events.append((ts - (len(pts) - 1 - i) * step,
                               ("move", name, x, y)))
        elif mode == 2 and pts:
            events.append((ts, ("attack", name, pts[0][0], pts[0][1])))
        elif mode == 0:
            events.append((ts, ("self", name)))
    return events


# North, east, south, west. A shape is read off the way the creature faces.
DIRS = ((0, -1), (1, 0), (0, 1), (-1, 0))
# The walk anim's high bits are how the phone turns a sprite: mirror, away.
FACE_BITS = (128, 64 | 128, 64, 0)

PATTERNS = {
    "Skeleton": "front1",
    "Golem": "front3",
    "Beetle": "sides",
    "Fire Devil": "fire",
    "Gorrak": "lunge",
    "Fungusman": "spores",
    "Ghost": "pierce",
    "Beholder": "corners",
    "Aldor": "fence",
}
# One line, drawn on the fight bar with no wrapping, so it has to fit
# the 240-wide screen and still name the old weapon and the new one.
BOSSES = {
    "Mira": "Mira drops her bow and draws a blade",
    "Shirard": "Shirard quits magic and draws a blade",
    "Aldor": "Aldor roars and swings wide",
    "Beholder": "The Eye glares down four lines",
}
# Each phase turns the safe squares around, so the second half of a boss
# is a new fight to read, not the first one with a longer bar:
#   Mira      shoots down her line; close in. Then a blade in front and at
#             both sides; get behind her.
#   Shirard   a burst two squares out; step in beside him. Then the blade.
#   Aldor     his front and one shoulder. Then front, both front corners
#             and both shoulders.
#   Beholder  its four diagonals; stand square on. Then a gaze down the
#             four straight lines; only the diagonals are safe.
BOSS_SHAPES = {
    "Mira": ("ray", "boss"),
    "Shirard": ("burst", "boss"),
    "Aldor": ("fence", "boss"),
    "Beholder": ("corners", "gaze"),
}

# How hard the chapter is. The page at /balance writes this file.
# mistakes:   turns standing in one creature's shape that empty the life a
#             hero is expected to carry into that tier (tiers.REFERENCE).
# boss_turns: turns one boss phase lasts with the tier's best weapon.
# pay: gold and experience as a percent of what a kill is worth.
BALANCE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "balance.json")
DEFAULT_BALANCE = {"mistakes": 3, "boss_turns": 2, "pay": 100}


def balance():
    data = {}
    try:
        with open(BALANCE_PATH) as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        data = {}
    out = dict(DEFAULT_BALANCE)
    for key in out:
        try:
            out[key] = int(data.get(key, out[key]))
        except (TypeError, ValueError):
            pass
    out["mistakes"] = min(8, max(1, out["mistakes"]))
    out["boss_turns"] = min(8, max(1, out["boss_turns"]))
    out["pay"] = min(300, max(10, out["pay"]))
    return out


def _hero_blow(w, weapon=None):
    """A plain blow with this weapon, or the one in hand. No crit.

    A blade is Hit plus Strength; a bow is Shoot plus Dexterity."""
    weapon = weapon or w.weapon()
    if weapon and weapon.cls == "bow":
        it, stat = catalogue().find("Shoot"), "Dexterity"
    else:
        it, stat = catalogue().find("Hit"), "Strength"
    effect = it.effect if it else 10
    mod = weapon.effect if weapon and (weapon.cls in MELEE_CLS
                                       or weapon.cls == "bow") else 0
    return max(1, effect + mod + tiers.potency_bonus(w.stats.get(stat, 15),
                                                     tiers.swing_of(weapon)))


# How many of the eight squares round a creature each shape threatens. It
# prices the blow: a shape you can step out of may hit hard, because there
# are squares where it cannot touch you at all; one that covers you wherever
# you stand has to be gentle.
THREAT = {"front1": 1, "lunge": 1, "spores": 1, "ray": 1,
          "fence": 2, "pierce": 2, "sides": 2,
          "front3": 3, "fire": 3, "corners": 4, "gaze": 4, "burst": 4,
          "boss": 5, "ring": 8}
# A creature swinging this often is the reference the blow is pitched at.
REFERENCE_SWINGS = 2


def _pressure_blow(w, m=None):
    """The effect to feed strike() so a normal hit, after armour, is one
    mistake. Crits and precise hits still hurt more. Dodge still matters.

    Given the creature, two things shape it further, and both keep the
    damage a whole turn deals about level — what changes is how it arrives.

    How often it swings. A light body swings four times a turn and a heavy
    one twice (Mob.swing_time), so the quick ones land several small hits
    where the slow ones land one or two large. Armour subtracts from every
    blow, so it earns its price against the quick; stepping out of reach
    avoids a whole blow, so it is worth more against the slow. That gives
    the two defences different jobs instead of both being generally good.

    How much it covers. A Skeleton threatens one of the eight squares round
    it and may hit very hard, because seven squares are safe. A creature
    covering all eight cannot, because there is nowhere to stand.
    """
    cfg = balance()
    tier = getattr(m, "tier", None) if m is not None else None
    if tier:
        # Sized to the tier, never to the hero: see tiers.py. Levels, life
        # and a better suit are what carry him through more mistakes.
        return tiers.creature_blow(
            tier, max(1, TURN_BUDGET // m.offence()["swing"]),
            THREAT.get(pattern_of(w, m), 8), cfg["mistakes"])
    through = max(1, (w.hero_max + cfg["mistakes"] - 1) // cfg["mistakes"])
    if m is not None:
        swings = max(1, TURN_BUDGET // m.offence()["swing"])
        covered = THREAT.get(pattern_of(w, m), 8)
        through = max(1, round(through * (8.0 / covered) ** 0.4
                               * REFERENCE_SWINGS / swings))
    # The blow is sized before armour, and strike() takes armour off after
    # the precise and critical multipliers. Adding the suit back on here, as
    # this once did, cancelled it on a plain hit and made every precise hit
    # and crit worse by half the suit: the Spike Suit cost more life a blow
    # than wearing nothing.
    return through


def _tune_bosses(w):
    """Each phase lasts boss_turns turns of the tier's best weapon, so
    better gear shortens a boss the way it shortens everything else, and a
    hero behind on gear takes a turn or two longer. Both phases share the
    size. A boss pays its phase pool once, when the second one ends."""
    if getattr(w, "game", "") != "ShiradsForge":
        return
    for m in w.fighters():
        if fighter_name(w, m) not in BOSSES:
            continue
        pool = tiers.boss_life(getattr(m, "tier", None) or "I",
                               balance()["boss_turns"])
        m.boss = True
        m.max_hp = pool
        m.hp = pool
        m.fight_hp = pool


def balance_page():
    """The whole control. Three numbers, and what they come to in each tier."""
    cfg = balance()
    rows = []
    for tier in tiers.ORDER:
        ref = tiers.REFERENCE[tier]
        suit = catalogue().find(ref["suit"])
        per_blow = tiers.creature_blow(tier, 2, 4, cfg["mistakes"])
        rows.append(
            f"<tr><td>{tier}</td><td>{ref['level']}</td><td>{ref['life']}</td>"
            f"<td>{ref['suit']} ({suit.effect if suit else 0})</td>"
            f"<td>{per_blow}</td>"
            f"<td>{tiers.creature_life(tier, tiers.BEETLE)}</td>"
            f"<td>{tiers.best_round(tier)} / {tiers.entry_round(tier)}</td>"
            f"<td>{tiers.boss_life(tier, cfg['boss_turns'])}</td></tr>")
    table = "\n".join(rows)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Balance</title>
<style>
  body {{ font: 20px/1.4 Georgia, serif; margin: 32px auto; max-width: 38em; color: #1a1a1a; padding: 0 16px; }}
  label {{ display: block; margin: 18px 0; }}
  input {{ font: inherit; width: 4em; }}
  button {{ font: inherit; padding: 4px 16px; }}
  p {{ color: #333; }}
  table {{ border-collapse: collapse; font-size: 16px; }}
  td, th {{ padding: 4px 10px; border-bottom: 1px solid #ddd; text-align: right; }}
</style></head><body>
<h1>How hard</h1>
<form method="post" action="/balance">
  <label>Standing in one creature's shape, you fall in
    <input name="mistakes" type="number" min="1" max="8" value="{cfg['mistakes']}">
    turns.</label>
  <label>A boss phase lasts
    <input name="boss_turns" type="number" min="1" max="8" value="{cfg['boss_turns']}">
    turns with the tier's best weapon.</label>
  <label>A kill pays
    <input name="pay" type="number" min="10" max="300" value="{cfg['pay']}">
    % of what it is worth, in gold and in experience.</label>
  <button type="submit">Save</button>
</form>
<p>The chapter is three tiers of the route, each with its own traders. Creatures are sized to the tier, never to you. A Beetle-weight creature takes one turn with the tier's best weapon and about two with the weapon the tier opens with, so skipping an upgrade costs a turn or two a fight, not the fight.</p>
<p>A turn in a shape costs the life the tier expects you to carry in, divided by the dial, after the tier's suit. More levels or a better suit mean you survive more mistakes. Out of every shape you take nothing.</p>
<table>
<tr><th>tier</th><th>level</th><th>life</th><th>suit</th><th>blow</th><th>Beetle</th><th>best / entry a turn</th><th>boss phase</th></tr>
{table}
</table>
<p>Blow is a two-swing creature with a four-square shape; narrow shapes hit up to a third harder, wide ones a little softer. Levels come from weight, not life, so the hero does not outgrow the next tier. <code>tools/balance_sim.py</code> checks all of it.</p>
</body></html>"""


def fighter_name(w, m):
    """The name a blow should use. Bosses share a sheet with other people,
    so the node is what says Mira from a townsman."""
    if getattr(w, "game", "") == "ShiradsForge":
        named = {20: "Shirard", 46: "Mira", 48: "Aldor", 19: "Beholder"}
        if m.node in named:
            return named[m.node]
    return w.creature_name(m.creature) or "It"


def _bow_equipped(w):
    """One weapon slot. The bow is in hand, or it is not."""
    weapon = w.weapon()
    return bool(weapon and weapon.cls == "bow")


def pattern_of(w, m):
    """Which cells this creature threatens.

    A blade gives each creature its own shape. The bow gives every one of
    them the eight neighbours: they walk toward the square you are standing
    on and swing from there, so the arrow has a line to meet. Other chapters
    keep that ring for both weapons.
    """
    if getattr(w, "game", "") != "ShiradsForge":
        return "ring"
    name = fighter_name(w, m)
    # A boss keeps its shapes whatever the hero holds: reading them is the
    # fight.
    if name in BOSS_SHAPES:
        return BOSS_SHAPES[name][0 if getattr(m, "phase", 1) < 2 else 1]
    if _bow_equipped(w):
        return "ring"
    return PATTERNS.get(name, "ring")


def _face_toward(x, y, hx, hy):
    dx, dy = hx - x, hy - y
    if dx == 0 and dy == 0:
        return 2
    if abs(dx) >= abs(dy):
        return 1 if dx > 0 else 3
    return 2 if dy > 0 else 0


def _faced(anim, face):
    return (anim & 63) | FACE_BITS[face & 3]


def _cells(pattern, x, y, face):
    dx, dy = DIRS[face]
    lx, ly = -dy, dx
    front = [(x + dx, y + dy),
             (x + dx + lx, y + dy + ly),
             (x + dx - lx, y + dy - ly)]
    if pattern == "front1":
        return front[:1]
    if pattern == "front3":
        return front
    if pattern == "boss":
        return front + [(x + lx, y + ly), (x - lx, y - ly)]
    if pattern == "sides":
        return [(x + lx, y + ly), (x - lx, y - ly)]
    if pattern == "fire":
        return front + [(cx + dx, cy + dy) for cx, cy in front]
    if pattern == "lunge":
        return [(x + dx, y + dy), (x + 2 * dx, y + 2 * dy)]
    if pattern == "pierce":
        return [(x + dx, y + dy), (x - dx, y - dy)]
    if pattern == "fence":
        return [(x + dx, y + dy), (x + lx, y + ly)]
    if pattern == "spores":
        return [(x + 2, y), (x - 2, y), (x, y + 2), (x, y - 2)]
    if pattern == "corners":
        return [(x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1)]
    if pattern == "ray":
        return [(x + dx * d, y + dy * d) for d in range(2, 6)]
    if pattern == "gaze":
        return [(x + ax * d, y + ay * d) for ax, ay in DIRS for d in range(1, 5)]
    if pattern == "burst":
        return [(x + ax, y + ay) for ax in range(-2, 3) for ay in range(-2, 3)
                if max(abs(ax), abs(ay)) == 2]
    cells = []
    for ay in (-1, 0, 1):
        for ax in (-1, 0, 1):
            if ax or ay:
                cells.append((x + ax, y + ay))
    return cells


def _covers(w, pattern, x, y, face, hx, hy):
    if (hx, hy) not in _cells(pattern, x, y, face):
        return False
    if max(abs(hx - x), abs(hy - y)) > 1 and not w.line_of_sight(x, y, hx, hy):
        return False
    return True


def _best_stance(w, pattern, x, y, face0, hx, hy, blocked):
    """The shortest walk that puts the hero in the shape, and the facing
    that does it. Turning in place is cheaper than a step. None if nothing
    within eight steps covers them."""
    q = deque([(x, y, 0)])
    seen = {(x, y)}
    parent = {}
    best = None
    fixed = pattern in ("corners", "ring", "spores", "gaze", "burst")
    while q:
        cx, cy, dist = q.popleft()
        for face in ((face0,) if fixed else range(4)):
            if not _covers(w, pattern, cx, cy, face, hx, hy):
                continue
            score = dist * 10 + (0 if face == face0 else 1)
            if best is None or score < best[0]:
                best = (score, cx, cy, face)
        if dist >= 8:
            continue
        for dx, dy in DIRS:
            nx, ny = cx + dx, cy + dy
            if (nx, ny) in seen or (nx, ny) in blocked or (nx, ny) == (hx, hy):
                continue
            if not w.can_stand(nx, ny):
                continue
            seen.add((nx, ny))
            parent[(nx, ny)] = (cx, cy)
            q.append((nx, ny, dist + 1))
    if best is None:
        return None
    _, bx, by, face = best
    path = []
    cur = (bx, by)
    while cur != (x, y):
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path, face


def mob_timeline(w):
    """The creature's plan, chosen blind from where everyone is standing now.

    It walks until its own shape covers the square you occupy, then swings.
    It does not know which way you will step. A shoulder that is safe
    against the facing it committed to stays safe for the rest of the turn.
    """
    events = []
    reserved = {(w.hero_x, w.hero_y)} | _blocked(w)
    hx, hy = w.hero_x, w.hero_y
    for m in w.fighters():
        t, x, y = 0, m.x, m.y
        face = getattr(m, "face", None)
        if face is None:
            face = _face_toward(x, y, hx, hy)
        reserved.discard((x, y))
        pattern = pattern_of(w, m)
        stance = _best_stance(w, pattern, x, y, face, hx, hy, reserved)
        if stance:
            path, aim = stance
            arrived = True
            for nx, ny in path:
                if t + MOVE_COST > TURN_BUDGET:
                    arrived = False
                    break
                t += MOVE_COST
                events.append((t, ("mob_move", m.node, nx, ny)))
                face = _face_toward(x, y, nx, ny)
                x, y = nx, ny
                reserved.add((x, y))
            # The last step may not be the facing that covers. Turning
            # after they arrive is free, and the swing uses that facing.
            if arrived:
                face = aim
        else:
            while t + MOVE_COST <= TURN_BUDGET:
                nxt = _step_toward(w, x, y, hx, hy, reserved)
                if nxt is None:
                    break
                t += MOVE_COST
                events.append((t, ("mob_move", m.node, nxt[0], nxt[1])))
                face = _face_toward(x, y, nxt[0], nxt[1])
                x, y = nxt
                reserved.add((x, y))
                if _covers(w, pattern, x, y, face, hx, hy):
                    break
        # the creature's own swing, not a flat cost shared with the hero
        blow_time = m.offence()["swing"]
        while (t + blow_time <= TURN_BUDGET
               and _covers(w, pattern, x, y, face, hx, hy)):
            t += blow_time
            events.append((t, ("mob_attack", m.node, face)))
        reserved.add((x, y))
    return events


def hero_plan(w):
    """What Auto fight queues for the hero: close and Hit with a melee
    weapon, or keep a bow out of contact and Shoot. One turn of it."""
    mobs = w.fighters()
    if not mobs:
        return []
    target = min(mobs, key=lambda m: (abs(m.x - w.hero_x) + abs(m.y - w.hero_y),
                                       m.node))
    bow = w.weapon() is not None and w.weapon().cls == "bow"
    blocked = _blocked(w)
    x, y = w.hero_x, w.hero_y
    t = 0
    actions, steps = [], []
    # what the fight bar charges this hero: practice and Speed included
    move = w.trained_time("Move", MOVE_COST)
    shot = w.trained_time("Shoot", swing_cost(w, "Shoot"))
    blow = w.trained_time("Hit", swing_cost(w, "Hit"))

    def flush(upto):
        if steps:
            actions.append(("Move", upto, 1, list(steps)))
            steps.clear()

    while t < TURN_BUDGET:
        touching = w.contact(x, y, target.x, target.y)
        if bow and touching:
            nxt = _step_away(w, x, y, target.x, target.y, blocked)
            if nxt is None or t + move > TURN_BUDGET:
                break
            t += move
            x, y = nxt
            steps.append((x, y))
            continue
        if bow and w.line_of_sight(x, y, target.x, target.y):
            if t + shot > TURN_BUDGET:
                break
            t += shot
            flush(t - shot)
            actions.append(("Shoot", t, 2, [(target.x, target.y)]))
            continue
        if not bow and touching:
            if t + blow > TURN_BUDGET:
                break
            t += blow
            flush(t - blow)
            actions.append(("Hit", t, 2, [(target.x, target.y)]))
            continue
        nxt = _step_toward(w, x, y, target.x, target.y, blocked)
        if nxt is None or t + move > TURN_BUDGET:
            break
        t += move
        x, y = nxt
        steps.append((x, y))
    flush(t)
    return actions


def _corpse_at(w, tx, ty):
    return any(m.location == w.location and (m.x, m.y) == (tx, ty) and not m.alive
               for m in w.mobs.values())


def _kill(w, target, script):
    name = fighter_name(w, target)
    # A boss (BOSSES) has a second pool in the same fight. The first
    # time they drop, they stay on the board and change shape. The quest
    # hears about the death only when the second pool is gone.
    if name in BOSSES and getattr(target, "phase", 1) < 2:
        target.phase = 2
        target.hp = target.max_hp
        target.rest = True
        script.append(res_attack(
            target.node, [(target.node, -target.max_hp)],
            anim=_faced(w.anim(target.creature, "attack"),
                        getattr(target, "face", 2)),
            msg=BOSSES[name], red=False, dur=255))
        return
    target.alive = False
    target.hp = 0
    gold, xp = target.spoil()
    pay = balance()["pay"]
    gold = max(1, gold * pay // 100)
    xp = max(1, xp * pay // 100)
    w.pending_gold += gold
    w.pending_xp += xp
    script.append(result(0, [1, target.node, w.anim(target.creature, "die")],
                         dur=240, msg=f"{name} dies  +{xp} XP", red=False))
    script.append(res_remove([target.node]))


def _land_on_mob(w, attacker, target, outcome, dmg, anim, script):
    words = {"miss": "Miss", "fizzle": "Fizzle", "resist": "Resisted"}
    if outcome in words:
        _note(script, words[outcome], anim=anim, node=attacker)
        return
    if dmg <= 0:
        _note(script, "Blocked", anim=anim, node=attacker)
        return
    target.hp -= dmg
    label = {"crit": "CRIT", "precise": "Precise"}.get(outcome, "")
    # The status line above the action bar is the one place the game tells
    # you what just happened, and it was saying "-7" with no idea what to.
    # Now that the chapters name their own creatures, use the name.
    who = fighter_name(w, target)
    msg = f"{label} {who} -{dmg}".strip()
    script.append(res_attack(attacker, [(target.node, dmg)], anim=anim, msg=msg))
    if target.hp <= 0:
        _kill(w, target, script)


def _aimed(w, tx, ty):
    """The fighter still standing on the square the action was aimed at.
    A corpse means the blow already landed earlier in this turn."""
    target = w.mob_at(tx, ty, include_npcs=False)
    if target is not None and (w.engaged is None or target.node in w.engaged):
        return target
    return None


def _arrow_target(w, tx, ty):
    """The first fighter an arrow meets on the way to the aimed square.

    Same steps as line_of_sight: the longer axis, and Y when they match.
    A wall stops the shot. A creature standing on any square the arrow
    enters, including the one it was aimed at, is the one that is hit.
    Returns (fighter or None, blocked)."""
    mp = w.map()
    if not mp or (w.hero_x, w.hero_y) == (tx, ty):
        return None, not mp
    x, y = w.hero_x, w.hero_y
    while (x, y) != (tx, ty):
        if abs(x - tx) > abs(y - ty):
            x += -1 if x > tx else 1
        elif y > ty:
            y -= 1
        else:
            y += 1
        if not mp.walkable(x, y):
            return None, True
        who = _aimed(w, x, y)
        if who is not None:
            return who, False
    return None, False


def _hero_attack(w, name, tx, ty, script, rng):
    it = catalogue().find(name) if name else None
    cls = it.cls if it else ""
    kind = it.kind if it else "skill"
    # The weapon is required whether or not the target is still there.
    # What the square holds is checked after that, at the moment the
    # action comes up on the timeline.
    if kind == "spell" or cls in ("bane", "spectral"):
        # The three attacks differ in what they ask of you, not only in what
        # they do. A blow needs you adjacent. An arrow is forgiving: it walks
        # the line and takes the first fighter it meets, so aiming past a
        # creature still hits it. A spell takes the named square and nothing
        # else — miss the square and the cast is spent.
        #
        # All three need a clear line. The client's own cursor is capped to a
        # 39-square diamond round the hero (d.java:1392, four right and down,
        # three left and up), so a spell was never artillery: it is a short,
        # exact, armour-ignoring strike. Aiming does skip the client's
        # b(x, y) — but that reads the tilemap's walk mask, so it only lets
        # the cursor rest on a wall or a crate, which says nothing about
        # seeing the target.
        target = _aimed(w, tx, ty)
        if target is None:
            if not _corpse_at(w, tx, ty):
                _note(script, "Too far away")
            return
        if not w.line_of_sight(w.hero_x, w.hero_y, target.x, target.y):
            _note(script, "No line of sight")
            return
        off = target.offence()
        outcome, dmg = w.strike(
            w.trained_effect(name, it.effect if it else 9),
            it.precision if it else 100,
            w.stats["Intelligence"], 0, spell=True, resist=off["will"], rng=rng)
        _land_on_mob(w, 0, target, outcome, dmg, w.anim(0, "cast"), script)
        if outcome == "hit":
            w.note_use(name)
        return
    if cls == "long range":
        weapon = w.weapon()
        if weapon is None or weapon.cls != "bow":
            _note(script, "Need a bow")
            return
        target, blocked = _arrow_target(w, tx, ty)
        if blocked:
            _note(script, "No line of sight")
            return
        if target is None:
            if not _corpse_at(w, tx, ty):
                _note(script, "Too far away")
            return
        if w.contact(w.hero_x, w.hero_y, target.x, target.y):
            _note(script, "Too close")
            return
        off = target.offence()
        # A bow draws on Dexterity for its force as well as its aim. With
        # Strength behind it, an archer who raised the ability his bows ask
        # for hit for 11 all chapter.
        outcome, dmg = w.strike(
            w.trained_effect(name, it.effect if it else 9),
            it.precision if it else 100,
            w.stats["Dexterity"], off["avoid"], dex=w.stats["Dexterity"],
            armour=off["armour"], swing_time=swing_cost(w, "Shoot"),
            weapon_mod=weapon.effect + w.practice_rank("Bow"), rng=rng)
        _land_on_mob(w, 0, target, outcome, dmg, w.anim(0, "bow"), script)
        if outcome in ("hit", "precise", "crit"):
            w.note_use(name)
            w.note_use("Bow")
        return
    weapon = w.weapon()
    if weapon is None or weapon.cls not in MELEE_CLS:
        _note(script, "Need a melee weapon")
        return
    # An axe does not travel. It lands on whoever you can still touch.
    # The square you named picks which one when several are in reach, and
    # it still counts if they stepped from that square to another you touch.
    target = _melee_target(w, tx, ty)
    if target is None:
        if not _corpse_at(w, tx, ty):
            _note(script, "Too far away")
        return
    off = target.offence()
    outcome, dmg = w.strike(
        w.trained_effect(name, it.effect if it else 10),
        it.precision if it else 100,
        w.stats["Strength"], off["avoid"], dex=w.stats["Dexterity"],
        armour=off["armour"], swing_time=swing_cost(w, "Hit"),
        weapon_mod=weapon.effect + w.practice_rank(weapon.cls.capitalize()),
        rng=rng)
    _land_on_mob(w, 0, target, outcome, dmg, w.anim(0, "attack"), script)
    if outcome in ("hit", "precise", "crit"):
        w.note_use(name)
        w.note_use(weapon.cls.capitalize())


def _melee_target(w, tx, ty):
    """Who an axe or hammer reaches at the moment the blow comes up."""
    touching = [m for m in w.fighters()
                if w.contact(w.hero_x, w.hero_y, m.x, m.y)]
    on_square = _aimed(w, tx, ty)
    if on_square is not None and on_square in touching:
        return on_square
    if not touching:
        return None
    touching.sort(key=lambda m: (max(abs(m.x - tx), abs(m.y - ty)), m.node))
    return touching[0]


def _heal(w, it, script, rng):
    roll = rng.randint(1, 100)
    if roll > (it.precision if it else 100):
        _note(script, "Fizzle")
        return
    w.note_use(it.name if it else "Minor Cure")
    # Healing alone takes the ability undivided. Every other use of potency is
    # divided (POTENCY_DIV) because it rides on top of gear that already
    # carries the scale; a heal has no gear behind it, so the ability is the
    # whole of it. At //10 a cure returned 9 against blows landing for 30 and
    # cost a full blow to cast — nobody would ever choose it. Undivided it
    # restores 23 at Willpower 15 and 42 at 34: one blow spent to undo one
    # blow taken, and a reason to raise Willpower at all.
    amount = max(0, w.trained_effect(it.name if it else "Minor Cure",
                                      it.effect if it else 8)
                 + w.stats["Willpower"])
    amount = min(amount, w.hero_max - w.hero_hp)
    w.hero_hp += amount
    script.append(res_attack(0, [(0, -amount)], anim=w.anim(0, "cast"),
                             msg=f"+{amount}", red=False))


def _self_act(w, name, script, rng):
    it = catalogue().find(name) if name else None
    if it and it.cls == "spirit":
        _heal(w, it, script, rng)
        return
    # A blow or a defence ends the zig-zag. You are no longer on that step.
    w.weave = 0
    # Defence chosen early still applies to blows later on this timeline.
    # A higher title dodges a little more and is counted as a landed use.
    # Each further defence in the same turn adds half what the last one did
    # (+10, +5, +2, +1): five Dodges at 20 apiece used to buy +50, a creature
    # hitting one time in five for a fifth of the turn, which made opening
    # every turn with them the only sensible play.
    base = (it.precision if it else 10) + w.practice_rank(name or "Dodge")
    n = getattr(w, "defences", 0)
    gain = base >> n
    w.guard += gain
    w.defences = n + 1
    if gain:
        w.note_use(name or "Dodge")
        _note(script, name or "Dodge", red=False)
    else:
        _note(script, "No more to dodge", red=False)


def _hero_move(w, name, x, y, script):
    orthogonal = abs(x - w.hero_x) + abs(y - w.hero_y) == 1
    if not orthogonal or not w.can_stand(x, y) or w.occupied(x, y):
        _note(script, "Failed Move")
        return
    w.hero_x, w.hero_y = x, y
    w.note_use(name or "Move")
    if name == "Zig-Zag":
        it = catalogue().find(name)
        w.weave = it.effect if it else 9
    else:
        w.weave = 0
    script.append(res_walk(0, x, y, w.anim(0, "walk")))


def _mob_attack(w, m, script, rng, face):
    if not m.alive:
        return
    m.face = face
    shape = pattern_of(w, m)
    kind = "bow" if shape == "ray" else "cast" if shape == "burst" else "attack"
    anim = _faced(w.anim(m.creature, kind), face)
    # The swing was aimed at the square you held when the turn opened.
    # Stepping off that shape is the whole of the dodge.
    if not _covers(w, pattern_of(w, m), m.x, m.y, face, w.hero_x, w.hero_y):
        _note(script, "Out of reach", red=False, anim=anim, node=m.node)
        return
    off = m.offence()
    armour = w.armour().effect if w.armour() else 0
    # Every creature hits this hard, on purpose. The map's own numbers made
    # a beetle on the first island deadlier than Shirard. The shape is the
    # difficulty now; the blow is sized to the life you have.
    outcome, dmg = w.strike(
        _pressure_blow(w, m), off["precision"], 0,
        w.avoidance() + getattr(w, "weave", 0),
        armour=armour, rng=rng)
    if outcome == "miss" or dmg <= 0:
        # A creature missing is good news, so the line is green.
        _note(script, "Miss" if outcome == "miss" else "Blocked",
              red=False, anim=anim, node=m.node)
        return
    w.hero_hp = max(0, w.hero_hp - dmg)
    label = {"crit": "CRIT", "precise": "Precise"}.get(outcome, "")
    who = fighter_name(w, m)
    script.append(res_attack(m.node, [(0, dmg)], anim=anim,
                             msg=f"{label} {who} hits -{dmg}".strip()))


def _play(w, events, script, rng):
    for _, ev in events:
        if w.hero_hp <= 0:
            return
        kind = ev[0]
        if kind == "move":
            _hero_move(w, ev[1], ev[2], ev[3], script)
        elif kind == "attack":
            w.weave = 0
            _hero_attack(w, ev[1], ev[2], ev[3], script, rng)
        elif kind == "self":
            _self_act(w, ev[1], script, rng)
        elif kind == "mob_move":
            _, node, x, y = ev
            m = w.mobs.get(node)
            if not m or not m.alive or getattr(m, "rest", False):
                continue
            if w.occupied(x, y) or not w.can_stand(x, y):
                continue
            if abs(x - m.x) + abs(y - m.y) != 1:
                continue
            m.face = _face_toward(m.x, m.y, x, y)
            m.x, m.y = x, y
            script.append(res_walk(node, x, y,
                                   _faced(w.anim(m.creature, "walk"), m.face)))
        elif kind == "mob_attack":
            m = w.mobs.get(ev[1])
            if m and m.alive and not getattr(m, "rest", False):
                _mob_attack(w, m, script, rng, ev[2])


def resolve(w, actions, rng=None):
    """Both plans were made blind. Play them as one list, earliest first.

    The creature's plan is fixed from where everyone stood when the turn
    was closed, then merged with the queue. Equal times keep the hero's
    event first. A dead hero takes no further actions.
    """
    rng = rng or random
    w.guard = 0
    w.defences = 0
    w.weave = 0
    for m in w.mobs.values():
        m.rest = False
    script = []
    # The client re-sends its own coordinates on the end-turn message, which
    # puts the hero back on the creature after begin_fight moved them off.
    off = w.step_off_fighter()
    if off:
        script.append(res_walk(0, off[0], off[1], w.anim(0, "walk")))
    events = hero_timeline(w, actions) + mob_timeline(w)
    events.sort(key=lambda e: e[0])
    _play(w, events, script, rng)
    return script


def _regen(w, script):
    """Life points come back in full once the fight is over."""
    healed = w.hero_max - max(0, w.hero_hp)
    if healed > 0 and w.hero_hp > 0:
        script.append(res_attack(0, [(0, -healed)], anim=w.anim(0),
                                 msg=f"+{healed}", red=False))
    w.hero_hp = w.hero_max


def finish(w, script):
    """Status and the extra tags d.b(b) requires once a fight is over.

    2 won, 3 lost, 1 still going. Rewards are paid only for a win; a loss
    or a flee puts the creatures back where the fight found them.
    """
    if w.hero_hp <= 0:
        w.revert_fight()
        _calm_phases(w)
        w.hero_hp = w.hero_max
        start = w.locations[0] if w.locations else w.location
        w.location = start
        w.note_place(start)
        w.hero_x, w.hero_y = w.spawn_point(start)
        w.recall = (w.hero_x, w.hero_y)
        return 3, [chunk_int(25, w.location),
                   chunk_int(26, w.hero_x), chunk_int(27, w.hero_y)] + hud_chunks(w)
    if w.engaged is not None and not w.fighters():
        _regen(w, script)
        report = w.battle_report()
        w.commit_practice()
        leveled = w.grant_xp(w.pending_xp)
        w.gold += w.pending_gold
        w.pending_gold = 0
        w.pending_xp = 0
        if leveled:
            report += f"\nLevel {w.level}!"
            _note(script, f"Level {w.level}!", red=False)
        w.commit_kills()
        dead = bytes(n for n in (w.engaged or [])
                     if n in w.mobs and not w.mobs[n].alive)
        w.engaged = None
        # tag 21 opens "Raises left" (d.c). tag 22 is the six scores, in
        # z[] order, and the screen NPEs if it is missing while 21 is set.
        # tag 23 replaces d.l and must be a byte[]. tag 28 is who died.
        offer = [chunk_int(21, w.raises)]
        if w.raises:
            offer.append(chunk_raw(22, 0, bytes(
                w.stats[s] & 0xFF for s in w.STATS)))
        return 2, offer + [
            chunk_raw(23, 0, w.node_states()),
            chunk_str(24, report),
            chunk_raw(28, 0, dead)] + hud_chunks(w)
    return 1, []


def hud_chunks(w):
    """The walk-around panel. b.java run() stores these on every reply:

    tag 5  int 0..255   how full the bottom bar is
    tag 6  string       left number, experience so far
    tag 4  string       middle, the level
    tag 7  string       right number, gold

    Nothing was sending them, so the bar stayed black and the numbers blank.
    The combat strip is separate: life is the red bar, time is the gold one,
    and both of those are drawn by the phone from the fight itself.
    """
    need = max(1, w.xp_for_next())
    filled = min(255, w.xp * 255 // need)
    return [
        chunk_int(5, filled),
        chunk_str(6, str(w.xp)),
        chunk_str(4, str(w.level)),
        chunk_str(7, str(w.gold)),
    ]


def _log_world(w, status):
    where = w.LOCATION_NAMES.get(w.location, w.location)
    mobs = "  ".join(f"mob{m.node}({m.x},{m.y}) hp {m.hp}" for m in w.living())
    print(f"    \033[35mworld: {where} hero({w.hero_x},{w.hero_y}) "
          f"hp {w.hero_hp}/{w.hero_max}  {mobs}  -> status {status}\033[0m")


def _calm_phases(w):
    """A lost fight or a flee puts a boss back on their first pool."""
    for m in w.mobs.values():
        m.phase = 1
        m.rest = False


def _flee(w, script):
    healed = w.hero_max - w.hero_hp
    w.revert_fight()
    _calm_phases(w)
    w.hero_x, w.hero_y = w.recall
    if healed > 0:
        # Show the recovery before the client's own "You flee" dialog.
        w.hero_hp = w.hero_max - healed
        _regen(w, script)
    else:
        w.hero_hp = w.hero_max
    return 4


def auto_response(w, rng=None, req=None):
    """Auto fight never enters the combat UI. i.java case 12 sees the
    request's i flag still set and hands this reply to d.b, which only
    knows how to finish a fight — status 1 would build a turn on menus
    that were never filled in."""
    rng = rng or random
    script = []
    idle = 0
    for _ in range(40):
        if w.hero_hp <= 0 or not w.fighters():
            break
        before = (w.hero_hp, w.hero_x, w.hero_y,
                  tuple((m.node, m.hp, m.x, m.y) for m in w.fighters()))
        script.extend(resolve(w, hero_plan(w), rng))
        after = (w.hero_hp, w.hero_x, w.hero_y,
                 tuple((m.node, m.hp, m.x, m.y) for m in w.fighters()))
        idle = idle + 1 if after == before else 0
        if idle >= 2:
            break
    origin = getattr(w, "fight_at", (w.hero_x, w.hero_y))
    if w.hero_hp > 0 and w.fighters():
        status = _flee(w, script)
        extra = []
    else:
        status, extra = finish(w, script)
        # Auto fight never plays the movement script (i.java sends this
        # reply to d.b, not d.e), so the hero is still on the square the
        # fight started on. A loss already moved them via tags 26/27.
        if status == 2:
            w.hero_x, w.hero_y = origin
    _log_world(w, status)
    if not script:
        script.append(result(0, [0, 0]))
    return build_response(status=status,
                          chunks=[chunk_raw(20, 0, r) for r in script] + extra)


@handler(13)
def end_turn(req):
    """Opcode 13 — end turn. d.java j() writes one tag 1 per queued action
    and resets the buffer in between, so the chunks are concatenated.

    The reply is the animation script in repeated tag 20 chunks, and a
    status d.b(b) switches on:

        1 = new turn   2 = fight won   3 = lost   4 = fled
    """
    w, _, hero = session_world(req)
    sync(req, w)
    raw = b"".join(req.all(1))
    if raw == FLEE:
        script = []
        status = _flee(w, script)
        extra = []
        acts = []
    else:
        acts = parse_actions(raw)
        script = resolve(w, acts)
        status, extra = finish(w, script)
    if acts:
        print("    \033[35mactions: " +
              ", ".join(f"{n}(mode {m}){p}" for n, _, m, p in acts) + "\033[0m")
    if not script:
        script.append(result(0, [0, 0]))
    _log_world(w, status)
    if hero:
        saves().save(hero, w.game)
    chunks = [chunk_raw(20, 0, r) for r in script] + extra
    return build_response(status=status, chunks=chunks)


# --- the menus that were returning nothing ------------------------------------
#
# All of these render a server-formatted string or list (i.java:619-660), so the
# plumbing is trivial; only the content had to be reconstructed.
#
#   20  h(30, tag23 title, tag20 body)     hero sheet / score info
#   21  list from tag 20                   equipped items
#   25  list from tag 20, title tag 21     skills (tag1=9) / spells (tag1=13)
#   26  list from tag 20, title tag 21     rankings
#   27  list from tag 20, title tag 21     help

@handler(20)
def hero_sheet(req):
    w, _, hero = session_world(req)
    which = req.int_(1)
    if which == 2:
        # w.name() with no argument is the LOCATION's name, not the hero's
        body = (f"{hero or 'Hero'}\n\nLevel {w.level}\n"
                f"XP {w.xp}/{w.xp_for_next()}\n"
                f"Gold {w.gold}\nCreatures here: {len(w.living())}")
        title = "Score info"
    else:
        body, title = w.hero_sheet(), "Hero sheet"
    return build_response(status=1, chunks=[
        chunk_str(23, title), chunk_str(20, body)])


def choice_row(label, value, detail="", disabled=False):
    """One list row the handset can select.

    b.java run() type 4 builds an f. A plain string in the same list is only
    drawn; choosing it is cast to f and the client shows its error dialog
    (i.java case 16). label is what you see, value is what comes back in
    tag 1 (f.b). The signed byte -1 means no item icon.

    Choosing row 0 clears the parent line and does not write a name back
    (i.java case 17). A disabled row (g bit 8, f.c()) ignores that press.
    Any later row opens a dialog whose body is f.d(), the trailing bytes.
    A missing body is a blank box.
    """
    def piece(text):
        raw = enc_utf8(text)
        return bytes([len(raw)]) + raw

    extra = enc_utf8(detail) if detail else b""
    payload = (piece(label) + piece(value) + bytes([0xFF, 8 if disabled else 0])
               + piece("") + struct.pack(">H", len(extra)) + extra)
    return chunk_raw(20, T_STRUCT, payload)


@handler(21)
def equipped(req):
    """Opcode 21 — Equipped items. i.java case 21 makes a list from tag 20.

    Each row opens opcode 22 with the slot name, which lists what you carry
    for that slot. Gold stays on the hero sheet; a gold line here is not a
    thing you can wear.
    """
    w, _, _ = session_world(req)
    rows = []
    for slot in ("weapon", "armour"):
        it = w.item(w.equipped.get(slot))
        shown = it.label() if it else "nothing"
        rows.append(choice_row(f"{slot.title()}: {shown}", slot))
    return build_response(status=1, chunks=rows)


# How far below the hero's stat a piece may sit before the shelf drops it,
# and how many pieces past that stat stay visible. Used only when the hero
# is not standing at one of the five traders. 12 is the step from the
# Bloody Blade (3) to the Longfang (15).
SHOP_KEEP = 12
SHOP_AHEAD = 3

# The five traders, in the order you can walk to them from the Village.
# Fire Cave is the side door in Dwarven Hall, so it comes before the Lair.
TRADERS = (2, 3, 12, 5, 6)
# The route tier each trader sells, as tools/tune_gear.py pitched the gear:
# Lava Island opens the chapter, Dwarven Hall and Fire Cave share the middle,
# The Lair and The Core share the end.
TRADER_TIERS = ("I", "II", "II", "III", "III")


def _trader_tier(w):
    """Which trader the hero is standing with, or None away from all five."""
    loc = w.place() if hasattr(w, "place") else w.location
    try:
        return TRADERS.index(loc)
    except ValueError:
        return None


def _trader_band(items, tier, tiers=5):
    """One trader's slice of a shelf, slid toward the expensive end.

    A long list shows ten pieces. A short one shows about a third, so the
    bows still change from room to room. Neighbouring traders share the
    join: the next shop keeps the top of the last one and adds what comes
    after it.
    """
    ranked = sorted(items, key=lambda i: (i.requirement, i.rank, i.name))
    n = len(ranked)
    if n == 0:
        return []
    span = n if n <= 6 else min(10, max(5, (n + 1) // 3))
    if span >= n or tiers <= 1:
        return ranked
    tier = 0 if tier < 0 else (tiers - 1 if tier >= tiers else tier)
    start = round(tier * (n - span) / (tiers - 1))
    return ranked[start:start + span]


def _trader_stock(items, trader):
    """What one trader sells from this shelf, when the gear carries a tier.

    Each tier's pieces, weakest first, are dealt out in runs to the traders
    of that tier, so two shops in the same tier sell different things and
    the one further along sells the stronger half. Each shop also keeps the
    top piece of the shop before it, so skipping a side room such as Fire
    Cave never loses a piece for good. None when the items carry no tier;
    the caller falls back to the sliding band.
    """
    ranked = sorted(items, key=lambda i: (i.requirement, i.rank, i.name))
    if not ranked or any(i.tier is None for i in ranked):
        return None
    runs = []
    for tier in dict.fromkeys(TRADER_TIERS):
        shops = TRADER_TIERS.count(tier)
        pieces = [i for i in ranked if i.tier == tier]
        size, extra = divmod(len(pieces), shops)
        at = 0
        for n in range(shops):
            take = size + (1 if n < extra else 0)
            runs.append(pieces[at:at + take])
            at += take
    trader = min(max(trader, 0), len(runs) - 1)
    before = next((r[-1] for r in reversed(runs[:trader]) if r), None)
    return ([before] if before else []) + runs[trader]


def _shop_window(items, stat):
    """Gear he can wear, plus the next few he has not reached.

    Sorted by requirement. Anything more than SHOP_KEEP below his stat has
    left. The following SHOP_AHEAD pieces are shown even though he cannot
    wear them yet.
    """
    ranked = sorted(items, key=lambda i: (i.requirement, i.rank, i.name))
    floor = stat - SHOP_KEEP
    worn = [i for i in ranked if floor <= i.requirement <= stat]
    ahead = [i for i in ranked if i.requirement > stat][:SHOP_AHEAD]
    window = worn + ahead
    return window[-14:]


def show_shop(w, which):
    """The companion's shop page. A later map report clears it."""
    title, items = market_rows(w, which)
    seq = getattr(w, "shop_seq", 0) + 1
    w.shop_seq = seq
    w.shop_which = which
    w.shop_view = {
        "seq": seq,
        "title": title,
        "items": [{
            "name": it.name,
            "price": it.price,
            "effect": it.effect,
            "ability": it.ability,
            "requirement": it.requirement,
            "description": _plain(it.desc),
        } for it in items],
    }


def market_rows(w, which):
    """One shelf. d.java b[] is Melee, Missile, Armours, Skills, Spells.

    Melee and armour follow Strength. Bows follow Dexterity. At one of the
    five traders the shelf is that room's band instead: further from the
    Village, higher requirements, with the previous shop's top end kept.
    """
    kinds = ["weapon", "weapon", "armour", "skill", "spell"]
    kind = kinds[which] if 0 <= which < len(kinds) else "weapon"
    title = w.SHOP_CATEGORIES[which] if 0 <= which < 5 else "Market"
    items = [i for i in catalogue().get(kind)
             if World.usable(i) and i.name not in World.BAR_SKILLS
             and (which != 1 or i.cls == "bow")]
    if which == 0:
        items = [i for i in items if i.cls in ("sword", "axe", "hammer")]
    if which in (0, 1, 2):
        tier = _trader_tier(w)
        if tier is None:
            stat_name = "Dexterity" if which == 1 else "Strength"
            items = _shop_window(items, w.stats.get(stat_name, 0))
        else:
            stock = _trader_stock(items, tier)
            items = stock if stock is not None else _trader_band(items, tier)
    return title, items[:14]


def _mark(r, g, b):
    """c.java draws \\u0006 then three colour bytes, and skips them for width."""
    return "\u0006" + chr(r) + chr(g) + chr(b)


_WORSE = _mark(255, 112, 112)
_BETTER = _mark(130, 210, 130)
_LOCKED = _mark(154, 154, 154)
_MELEE = ("sword", "axe", "hammer")


def _same_role(it, held):
    if it.kind == "armour" and held.kind == "armour":
        return True
    if it.cls in _MELEE and held.cls in _MELEE:
        return True
    return it.cls == held.cls


def _gear_value(w, it):
    """What a piece is worth in the role it fills, for better/worse marks.

    Armour is its effect: it subtracts the same from every blow. A weapon
    is what it deals in a turn, because effect alone stopped meaning
    anything once a swing cost the weapon's own time: a Ghost Sword at +23
    swings four times where a Doom Hammer at +70 swings twice, and at the
    same price they deal a turn alike. Marking the hammer better for its
    bigger number would be a lie.
    """
    if it.kind == "armour":
        return it.effect
    swings = max(1, (TURN_BUDGET - MOVE_COST * 4) // tiers.swing_of(it))
    return swings * _hero_blow(w, it)


def _gear_mark(w, it, shop=False):
    """Grey when the required stat is still out of reach. Otherwise red when
    it is worse than the piece worn in that role, and green when it is
    better and a shop row is one the purse can pay."""
    if it is None:
        return ""
    if it.kind in ("weapon", "armour", "skill", "spell") and not w.can_wield(it):
        return _LOCKED
    if it.kind not in ("weapon", "armour"):
        return ""
    slot = "armour" if it.kind == "armour" else "weapon"
    held = w.item(w.equipped.get(slot))
    if held is not None and not _same_role(it, held):
        return ""
    if held is not None and held.name == it.name:
        return ""
    if held is not None and _gear_value(w, it) < _gear_value(w, held):
        return _WORSE
    if ((held is None or _gear_value(w, it) > _gear_value(w, held))
            and w.can_wield(it)):
        if shop and it.price > w.gold:
            return ""
        return _BETTER
    return ""


def shelf_chunks(w, items):
    """Market rows the phone can open. Case 12 reads f.a and f.d()."""
    if not items:
        return [choice_row("Nothing in stock", "none", "Nothing in stock.")]
    return [choice_row(_gear_mark(w, it, shop=True) + it.label(), it.name,
                       _plain(it.desc) or it.name)
            for it in items]


def carried(w, slot):
    """Items in the pack that fit one worn slot, as selectable rows.

    The top line is disabled. The phone treats row 0 as 'clear this slot'
    and blanks the line above it.
    """
    rows = [choice_row("Choose an item below", slot, disabled=True)]
    for name in w.inventory:
        it = w.item(name)
        if it is None:
            continue
        if slot == "armour" and it.kind != "armour":
            continue
        if slot == "weapon" and it.kind != "weapon":
            continue
        worn = " (worn)" if w.equipped.get(slot) == it.name else ""
        detail = f"Wear {it.name}."
        if worn:
            detail = f"{it.name} is already worn."
        rows.append(choice_row(_gear_mark(w, it) + it.name + worn, it.name, detail))
    return rows


@handler(22)
def shop(req):
    """Opcode 22 — what can go in the slot you just picked.

    i.java case 16 sends f.b, which for the equipped list is "weapon" or
    "armour". The reply is a list (tag 20) under tag 21, and choosing a row
    sends that row's value to opcode 23. A numeric tag is the old market
    shelf, kept so a category index still renders.
    """
    w, _, _ = session_world(req)
    raw = req.get(1)
    slot = raw.decode("utf-8", "replace") if raw in (b"weapon", b"armour") else ""
    if slot:
        title = "Weapon" if slot == "weapon" else "Armour"
        rows = carried(w, slot) or [
            choice_row("Nothing held", slot, "Nothing in this slot.",
                       disabled=True)]
        return build_response(status=1, chunks=[
            chunk_str(21, title), chunk_int(22, 0)] + rows)
    which = req.int_(1)
    title, items = market_rows(w, which)
    show_shop(w, which)
    return build_response(status=1, chunks=[
        chunk_str(21, f"{title} ({w.gold}g)"), chunk_int(22, 0)] +
        shelf_chunks(w, items))


@handler(16)
def buy(req):
    """Opcode 16 — buy. The client drops the bought row from the shop list and
    shows tag 21, then goes back."""
    w, _, hero = session_world(req)
    name = req.get(1).decode("utf-8", "replace").split(" ")[0:99]
    wanted = " ".join(n for n in name if not n.endswith("g")
                      and not n.startswith(("E", "Ti"))).strip()
    looked = w.item(wanted)
    if looked and not World.usable(looked):
        msg = "That cannot be used."
    elif looked and not w.can_wield(looked):
        msg = f"You need {looked.ability} {looked.requirement}."
    else:
        it = w.buy(wanted)
        msg = (f"Bought {it.name} for {it.price}g." if it
               else "You cannot afford that.")
    if hero:
        saves().save(hero, w.game)
    if getattr(w, "shop_which", None) is not None:
        show_shop(w, w.shop_which)
    return build_response(status=1, chunks=[chunk_str(21, msg)] + hud_chunks(w))


@handler(23)
def equip(req):
    """Opcode 23 — equip. Status 1 makes the client swap the row in place."""
    w, _, hero = session_world(req)
    raw = req.get(1).decode("utf-8", "replace")
    wanted = raw.split(":")[-1].split(" E")[0].strip(" -")
    it = w.equip(wanted)
    if hero:
        saves().save(hero, w.game)
    return build_response(status=1 if it else 2,
                          chunks=[chunk_str(20, it.name if it else "Not held")])


@handler(10)
def fetch_resources(req):
    """Opcode 10 — the on-demand resource fetch, and the reason a location
    change hangs on "Please wait..." without it.

    d.java:282: when k() finds it is missing anything for the location it is
    loading, it builds a want-list of u16 (restype << 8 | id) keys, sends them
    as tag 1, and waits. Until the reply lands, d.T stays false and the screen
    never comes back.

    Everything it asks for is in the jar except types 1 and 9, which are ours.
    """
    w, _, _ = session_world(req)
    # After the first map, this fetch carries the room the phone is loading
    # (d.java d(b), tag 11). Remember it for the compendium. travel() is not
    # called: that would also move the hero to the doorway square.
    w.note_place(req.int_(11))
    raw = req.get(1)
    keys = [int.from_bytes(raw[i:i + 2], "big") for i in range(0, len(raw) - 1, 2)]

    chunks, served, missing = [], [], []
    for k in keys:
        restype, rid = k >> 8, k & 0xFF
        if restype == 1 and rid == 0:
            body = byte_table(w.entity_table())
        elif restype == 9 and rid == 0:
            body = byte_table(w.mob_table())
        else:
            body = w.res.get(restype, rid)
        if body is None:
            missing.append(f"{restype}:{rid:02x}")
            continue
        chunks.append(push_resource(3, k, body))
        served.append(f"{restype}:{rid:02x}")

    print(f"    \033[35mresources: served {len(served)}"
          + (f", MISSING {' '.join(missing)}" if missing else "")
          + f"  ({sum(len(c) for c in chunks)}B)\033[0m")
    return build_response(status=1, chunks=chunks)


@handler(31)
def report_place(req):
    """Opcode 31 — sent when a map finishes loading, even if no art was missing.

    The phone builds it like a fight's location block (d.java d(b)), so
    tag 11 is the room. It does not move the hero: travel() would put him
    on the doorway square. A fresh room also leaves the shop page.
    """
    w, _, _ = session_world(req)
    loc = req.int_(11)
    if loc:
        w.note_place(loc)
        w.shop_view = None
        w.shop_which = None
    return build_response(status=1, chunks=[])


@handler(11)
def interact(req):
    """Opcode 11 — a type 1 kind-3 entity was used. tag 1 is its state index
    (d.java:907, `new b(11, this).b(1, var2[0])`).

    The reply goes to d.c(b): a non-zero tag 21 opens the stat-raise screen
    with the six abilities as a byte[6] in tag 22. Message tags 1 and 2 are
    handled generically by the client, so they are how a crate or an NPC
    actually says something.
    """
    w, _, hero = session_world(req)
    sync(req, w)
    state = req.int_(1)
    # Shirad's kind-3 rows are checkpoints. The phone already showed the
    # line and flipped the quest switch. The reply pays a stated gift, if
    # the line named one, and otherwise stays quiet. A second sentence
    # here would cover the jar's own text.
    if w.real1:
        if state == w.ENDING.get(w.game):
            w.finished = True
            if hero:
                saves().save(hero, w.game)
            print(f"    \033[35mchapter complete: level {w.level}\033[0m")
            return build_response(status=1, chunks=[chunk_str(2, w.ending_text())]
                                  + hud_chunks(w))
        label = w.entity_label(state)
        if (state in w.crate_payoffs()
                or "crate" in label.lower() or "barrel" in label.lower()):
            found, gold = w.loot_container(state)
            if found or gold:
                lines = ["You smash it open.", "", "Inside:"]
                for it in found:
                    if it.kind == "skill":
                        lines.append(f"{it.name}, a {it.cls} skill")
                    elif it.kind == "spell":
                        lines.append(f"{it.name}, a spell")
                    elif it.kind == "weapon":
                        lines.append(f"{it.name}, a {it.cls}")
                    elif it.kind == "armour":
                        lines.append(f"{it.name}, armour")
                    else:
                        lines.append(f"{it.name}, a {it.kind}")
                if gold:
                    lines.append(f"{gold} gold")
                body = "\n".join(lines)
            else:
                body = "Nothing left inside."
            if hero:
                saves().save(hero, w.game)
            print(f"    \033[35mcrate {state}: "
                  f"{[it.name for it in found] or 'empty'} +{gold}g\033[0m")
            # Tag 2 is shown at once (b.java run(), tag 2). Tag 1 only queues.
            return build_response(status=1, chunks=[chunk_str(2, body)] + hud_chunks(w))
        paid = w.claim_gift(state)
        if hero:
            saves().save(hero, w.game)
        if paid:
            print(f"    \033[35mgift: state {state} +{paid} gold\033[0m")
        return build_response(status=1, chunks=[])

    entry = getattr(w, "interactables", {}).get(state)
    chunks = []

    if entry:
        loc, label, _ = entry
        text = w.text(loc)
        low = label.lower()

        if low.startswith("trade"):
            body = (f"The trader looks you over.\n\nYou have {w.gold} gold.\n"
                    f"Visit the Market from the menu to spend it.")
        elif low.startswith(("talk", "speak")):
            who = label.split()[-1].lower()
            body = next((v for v in text.values()
                         if v.lower().startswith(who + ":")), None) \
                or next((v for v in text.values() if ":" in v and len(v) > 40),
                        "They have nothing to say.")
        else:
            # a crate, a barrel: prefer a line that talks about opening one
            body = next((v for k, v in sorted(text.items())
                         if len(v) > 30
                         and any(word in v.lower()
                                 for word in ("crate", "barrel", "inside"))),
                        "You find nothing.")
            if "cogwheel" in body.lower() or "lever" in body.lower():
                w.gold += 10
        chunks.append(chunk_str(1, body[:250]))
    elif w.raises:
        chunks += [chunk_int(21, w.raises),
                   chunk_raw(22, 0, bytes(min(255, w.stats[s]) for s in w.STATS))]
    else:
        chunks.append(chunk_str(1, "Nothing happens."))

    if hero:
        saves().save(hero, w.game)
    print(f"    \033[35minteract: state {state} -> "
          f"{entry[1] if entry else 'unknown'}\033[0m")
    return build_response(status=1, chunks=chunks)


# --- the rest of the opcode table --------------------------------------------
#
# Response shapes are all from i.java's a(e, b, Throwable), which is the one
# method that says what every reply is allowed to look like:
#
#    2, 3   like 1: status 1 -> the hero list from tag 20
#    6      no response screen; the client has already dropped the hero
#    7, 28  list from tag 20, title tag 21 -> screen 29
#    9      pops the screen; the payload is the client's own snapshot
#   14      no response screen
#   15      list from tag 20, title tag 21 -> screen 12
#   17      screen 33
#   18      status 1 -> main menu; status 2 -> h(23, tag 20) + Balance/Cancel
#   19      like 1: status 4 -> screen 33
#   24      no response screen; the row is already gone client-side
#   26      list from tag 20, title tag 21 -> screen 29
#
# "No response screen" still needs a well-formed non-zero frame: status 0 reads
# as "Second login detected!" and throws the player out.


@handler(2)
@handler(3)
def account(req):
    """Opcodes 2 and 3 — the original login and registration, which took a
    username and password against watAgame's account server.

    There is no account server to check against, and the client is happy with
    the token model opcode 1 already uses, so both answer exactly as 1 does:
    here is your key, here are your heroes. Opcode 3 is re-dispatched by the
    client as 2 (i.java case 3), so they must agree.
    """
    return hello(req)


@handler(6)
def delete_hero(req):
    """Opcode 6 — delete a hero (tag 1 = its name). The client removes the row
    itself before asking, so the reply only has to be well formed."""
    st = saves()
    _, key, _ = session_world(req)
    name = req.get(1).decode("utf-8", "replace").strip()
    slot = st._slot(key, req.game)
    if name in slot:
        slot.remove(name)
        st.data["heroes"].pop(f"{req.game}:{name}", None)
        st.live.pop(f"{req.game}:{name}", None)
        st.flush()
    print(f"    \033[35mdelete hero: {name!r} -> {slot}\033[0m")
    return build_response(status=1, chunks=[])


@handler(9)
def save_game(req):
    """Opcode 9 — Save & exit, and the only place the client volunteers its
    own view of the world (d.java d(b)):

        tag 10  byte[]  entity states, d.i
        tag 11  int     location          tag 12/13  hero x, y
        tag 14  byte[]  node states, d.l
        tag 15/16 int   camera

    Taking these rather than our own bookkeeping means a save records where
    the player actually was, including anything they triggered in a location
    we never heard about.
    """
    w, _, hero = session_world(req)
    sync(req, w)
    if req.get(11):
        w.location = req.int_(11)
        w.hero_x, w.hero_y = req.int_(12), req.int_(13)
        w.note_place(w.location)
    nodes = req.get(14)
    for m in w.mobs.values():
        if m.node < len(nodes):
            m.alive = nodes[m.node] != 3
    if hero:
        saves().save(hero, w.game)
    print(f"    \033[35msave: {hero} at {w.location} ({w.hero_x},{w.hero_y})"
          f" {sum(1 for m in w.mobs.values() if m.alive)} alive\033[0m")
    return build_response(status=1, chunks=[])


@handler(14)
def spend_raises(req):
    """Opcode 14 — d.f(). Tag 1 is six bytes, points just spent on each
    ability, in z[] order. "Save points for later" sends the same message
    with only the points already spent."""
    w, _, hero = session_world(req)
    raw = req.get(1)
    if len(raw) == 6:
        w.spend_raises(raw)
        if hero:
            saves().save(hero, w.game)
        print(f"    \033[35mraises: {list(raw)} left {w.raises} "
              f"{[w.stats[s] for s in w.STATS]}\033[0m")
    return build_response(status=1, chunks=[])


@handler(15)
def interest(req):
    """Opcode 15 — "Pick interest" (type 1 kind 10). The list the phone
    shows is d.b[], the five market shelves, and this reply is that shelf."""
    w, _, _ = session_world(req)
    sync(req, w)
    which = req.int_(1)
    if not 0 <= which < 5:
        return build_response(status=1, chunks=[chunk_str(21, "Interest")])
    title, items = market_rows(w, which)
    show_shop(w, which)
    return build_response(status=1, chunks=[chunk_str(21, title)] +
                          shelf_chunks(w, items))


@handler(17)
def scripted(req):
    """Opcode 17 — a type 1 entity of kind 11, the one kind that asked the
    server what should happen. Its script is lost, and whatever this answers
    the phone then opens screen 33, which quits the game. Shirad's Forge's
    only kind 11, the ending, is served as kind 3 (World.ENDING), so this
    is only reached by a phone holding an older entity table."""
    print(f"    \033[35mscripted entity: tag1={req.int_(1)}\033[0m")
    return build_response(status=1, chunks=[])


@handler(18)
def bank(req):
    """Opcode 18 — the coin purse. Status 2 keeps the dialog up with the text
    from tag 20; status 1 drops back to the main menu."""
    w, _, hero = session_world(req)
    if req.int_(1) != 1:
        return build_response(status=1, chunks=[])
    return build_response(status=2, chunks=[
        chunk_str(20, f"{hero or 'Hero'}\n\nGold: {w.gold}\n"
                      f"Level {w.level}, XP {w.xp}/{w.xp_for_next()}")])


@handler(19)
def accept_offer(req):
    """Opcode 19 — the player accepted whatever offer opcode 1 status 5 made.
    Status 4 sends them to screen 33."""
    return build_response(status=4, chunks=[])


def salvage(w, wanted):
    """Break a held piece. Returns its name and tiers.RECYCLE_PERCENT of its price, rounded
    down. A new hero starts with no gold because this is what the kit is for."""
    wanted = (wanted or "").split(":")[-1].split(" E")[0].strip(" -")
    gone = None
    for name in list(w.inventory):
        if wanted and name.lower().startswith(wanted.lower()[:12]):
            w.inventory.remove(name)
            for slot, held in list(w.equipped.items()):
                if held == name:
                    w.equipped[slot] = None
            gone = name
            break
    refund = 0
    if gone:
        it = w.item(gone)
        if it:
            refund = it.price * tiers.RECYCLE_PERCENT // 100
            w.gold += refund
    return gone, refund


@handler(24)
def delete_item(req):
    """Opcode 24 — drop an item (tag 1 = its name)."""
    w, _, hero = session_world(req)
    raw = req.get(1).decode("utf-8", "replace")
    gone, refund = salvage(w, raw)
    if hero:
        saves().save(hero, w.game)
    print(f"    \033[35mdelete item: {raw!r} -> {gone} +{refund}g\033[0m")
    # The phone removes the row itself and does not read this reply.
    # The purse and the shop title are where the gold shows up.
    return build_response(status=1, chunks=[chunk_str(21, f"+{refund}g")]
                          + hud_chunks(w))


def _plain(text, limit=180):
    """Dialog bodies are drawn as text. Control characters are layout codes."""
    cleaned = "".join(ch if ch >= " " else " " for ch in (text or ""))
    cleaned = " ".join(cleaned.split())
    return (cleaned[:limit] or " ").strip()


@handler(25)
def spellbook(req):
    """Opcode 25 — Skills (tag 1 = 9) or Spells (tag 1 = 13).

    The reply is screen 19. Choosing a row opens a box from f.a and f.d()
    (i.java case 19). A plain string has neither, so the phone shows its
    error dialog. The box body has to be the trailing bytes of the record.
    """
    w, _, _ = session_world(req)
    spells = req.int_(1) == 13
    kind = "spell" if spells else "skill"
    title = "Spells" if spells else "Skills"
    bar = ("Zap", "Minor Cure") if spells else ("Move", "Hit", "Shoot", "Dodge")
    rows = []
    for name in bar:
        rank = w.practice_rank(name)
        title = World.TITLES[rank]
        nxt = World.TITLES[rank + 1] if rank + 1 < len(World.TITLES) else None
        _, pct = w.practice.get(name, (0, 0))
        if nxt:
            body = (f"{title}. {pct}% toward {nxt}. "
                    "A landed use adds 5%. Each title hits harder and takes less of the turn.")
        else:
            body = f"{title}. This can go no higher."
        rows.append(choice_row(f"{name}, {w.practice_label(name)}", name, body))
    return build_response(status=1, chunks=[
        chunk_str(21, title)] + rows[:14])


@handler(26)
def rankings(req):
    """Opcode 26 — the ladder. The original ranked every player on the
    servers; ours ranks the heroes this install has created, which is at
    least true."""
    st = saves()
    rows = []
    for slot, saved in st.data["heroes"].items():
        if ":" not in slot:
            continue
        game, _, name = slot.partition(":")
        rows.append((saved.get("level", 1), saved.get("xp", 0), name, game))
    rows.sort(reverse=True)
    lines = [f"{n}. {name} - level {lvl}, {xp} XP ({game})"
             for n, (lvl, xp, name, game) in enumerate(rows[:12], 1)]
    lines = lines or ["No heroes yet."]
    return build_response(status=1, chunks=[chunk_str(21, "Rankings")] + [
        choice_row(l, l, l) for l in lines])


HELP_TOPICS = [
    "Move with the direction keys. You cannot move diagonally.",
    "A turn gives you 720 time. A step costs 40. A blow or a shot costs 60.",
    "Actions sit on the bar at the bottom. Pick one, then pick a target.",
    "A close attack needs you next to the creature, with a sword, axe or hammer.",
    "A bow needs a clear view, and cannot be used while you are next to the target.",
    "Red tiles marked with arrows lead to the next location.",
    "Gold buys weapons and armour at the Market.",
    "A level gives 2 ability points. After a win you can spend them or save them.",
    "Save & exit writes your hero. Start game picks up where you left off.",
]


@handler(7)
@handler(27)
@handler(28)
def help_pages(req):
    """Opcodes 27 (Help), 7 and 28 (the icon overviews it links to). All three
    are a list from tag 20 under the tag 21 title; the client adds its own
    navigation rows."""
    page = req.int_(1)
    if req.opcode == 27:
        return build_response(status=1, chunks=[chunk_str(21, "Help")] + [
            choice_row(t, t, t) for t in HELP_TOPICS])
    icons = ["Sword - melee attack", "Bow - missile attack",
             "Shield - block, halves the next hit", "Flame - offensive spell",
             "Heart - healing spell", "Boot - move", "Hand - use or open",
             "Skull - the creature is dead"]
    if page == 6659:
        icons = ["Green arrow - an exit to another location",
                 "Chest - a container you can open",
                 "Star - a quest entity", "Coin - gold on the ground"]
    return build_response(status=1, chunks=[chunk_str(21, "Icon overview")] + [
        choice_row(i, i, i) for i in icons])



def default(req):
    """Minimal well-formed frame. status=1 so the client does not read it as a
    duplicate login; no chunks, so we learn what breaks."""
    return build_response(status=1, chunks=[])


def dispatch(req):
    fn = HANDLERS.get(req.opcode)
    return (fn(req) if fn else None) or default(req)
