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

import random
import struct

from codec import build_response, chunk_int, chunk_str, chunk_raw
from catalogue import catalogue
from world import get_world, saves

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
        return saves().world(hero, req.game), key, hero
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

def result(kind, payload, msg="", dur=18, refresh=0, red=False):
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
    return result(2, [node, x, y, ANIM_IDLE if anim is None else anim])


def res_attack(attacker, victims, anim=ANIM_IDLE, msg="", red=True):
    p = [attacker, anim, len(victims)]
    for node, dmg in victims:
        p += [node, (dmg >> 8) & 0xFF, dmg & 0xFF]
    return result(1, p, msg=msg, red=red, dur=24)


def res_remove(nodes):
    return result(6, [len(nodes)] + list(nodes), dur=8)


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
    ])


def sync(req, w):
    """The client attaches its own view of the world to outgoing messages via
    d.d(b): tag 11 = location, 12/13 = hero x/y, 10/14 = the state arrays.

    Location changes happen entirely client-side — a kind 4 exit sets d.I and
    reloads the map without asking us — so this is how the server finds out
    the player walked through a door."""
    loc = req.int_(11) if hasattr(req, "int_") else 0
    if loc and loc != w.location:
        w.travel(loc)
        return True
    x, y = req.int_(12), req.int_(13)
    if x or y:
        w.hero_x, w.hero_y = x, y
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
            # long route genuinely takes longer than a short one.
            step = max(1, MOVE_COST)
            for i, (x, y) in enumerate(pts):
                events.append((ts - (len(pts) - 1 - i) * step,
                               ("move", x, y)))
        elif mode == 2 and pts:
            events.append((ts, ("attack", name, pts[0][0], pts[0][1])))
        elif mode == 0:
            events.append((ts, ("self", name)))
    return events


def mob_timeline(w):
    """Both sides share the 720 budget. Creatures close, then swing, and
    they choose blind against where the hero is standing now."""
    events = []
    reserved = {(w.hero_x, w.hero_y)} | _blocked(w)
    for m in w.fighters():
        t, x, y = 0, m.x, m.y
        reserved.discard((x, y))
        while True:
            if w.contact(x, y, w.hero_x, w.hero_y):
                if t + ATTACK_COST > TURN_BUDGET:
                    break
                t += ATTACK_COST
                events.append((t, ("mob_attack", m.node)))
            else:
                nxt = _step_toward(w, x, y, w.hero_x, w.hero_y, reserved)
                if nxt is None or t + MOVE_COST > TURN_BUDGET:
                    break
                t += MOVE_COST
                events.append((t, ("mob_move", m.node, nxt[0], nxt[1])))
                x, y = nxt
                reserved.add((x, y))
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

    def flush(upto):
        if steps:
            actions.append(("Move", upto, 1, list(steps)))
            steps.clear()

    while t < TURN_BUDGET:
        touching = w.contact(x, y, target.x, target.y)
        if bow and touching:
            nxt = _step_away(w, x, y, target.x, target.y, blocked)
            if nxt is None or t + MOVE_COST > TURN_BUDGET:
                break
            t += MOVE_COST
            x, y = nxt
            steps.append((x, y))
            continue
        if bow and w.line_of_sight(x, y, target.x, target.y):
            if t + ATTACK_COST > TURN_BUDGET:
                break
            t += ATTACK_COST
            flush(t - ATTACK_COST)
            actions.append(("Shoot", t, 2, [(target.x, target.y)]))
            continue
        if not bow and touching:
            if t + ATTACK_COST > TURN_BUDGET:
                break
            t += ATTACK_COST
            flush(t - ATTACK_COST)
            actions.append(("Hit", t, 2, [(target.x, target.y)]))
            continue
        nxt = _step_toward(w, x, y, target.x, target.y, blocked)
        if nxt is None or t + MOVE_COST > TURN_BUDGET:
            break
        t += MOVE_COST
        x, y = nxt
        steps.append((x, y))
    flush(t)
    return actions


def _corpse_at(w, tx, ty):
    return any(m.location == w.location and (m.x, m.y) == (tx, ty) and not m.alive
               for m in w.mobs.values())


def _kill(w, target, script):
    target.alive = False
    target.hp = 0
    gold, xp = target.spoil()
    w.pending_gold += gold
    w.pending_xp += xp
    script.append(result(0, [1, target.node, w.anim(target.creature, "die")], dur=12))
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
    msg = f"{label} -{dmg}".strip()
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


def _hero_attack(w, name, tx, ty, script, rng):
    it = catalogue().find(name) if name else None
    cls = it.cls if it else ""
    kind = it.kind if it else "skill"
    # The weapon is required whether or not the target is still there.
    # What the square holds is checked after that, at the moment the
    # action comes up on the timeline.
    if kind == "spell" or cls in ("bane", "spectral"):
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
            it.effect if it else 9, it.precision if it else 100,
            w.stats["Intelligence"], 0, spell=True, resist=off["will"], rng=rng)
        _land_on_mob(w, 0, target, outcome, dmg, w.anim(0, "cast"), script)
        return
    if cls == "long range":
        weapon = w.weapon()
        if weapon is None or weapon.cls != "bow":
            _note(script, "Need a bow")
            return
        target = _aimed(w, tx, ty)
        if target is None:
            if not _corpse_at(w, tx, ty):
                _note(script, "Too far away")
            return
        if w.contact(w.hero_x, w.hero_y, target.x, target.y):
            _note(script, "Too close")
            return
        if not w.line_of_sight(w.hero_x, w.hero_y, target.x, target.y):
            _note(script, "No line of sight")
            return
        off = target.offence()
        outcome, dmg = w.strike(
            it.effect if it else 9, it.precision if it else 100,
            w.stats["Strength"], off["avoid"], dex=w.stats["Dexterity"],
            armour=off["armour"], weapon_mod=weapon.effect, rng=rng)
        _land_on_mob(w, 0, target, outcome, dmg, w.anim(0, "bow"), script)
        return
    weapon = w.weapon()
    if weapon is None or weapon.cls not in MELEE_CLS:
        _note(script, "Need a melee weapon")
        return
    target = _aimed(w, tx, ty)
    if target is None or not w.contact(w.hero_x, w.hero_y, target.x, target.y):
        if target is not None or not _corpse_at(w, tx, ty):
            _note(script, "Too far away")
        return
    off = target.offence()
    outcome, dmg = w.strike(
        it.effect if it else 10, it.precision if it else 100,
        w.stats["Strength"], off["avoid"], dex=w.stats["Dexterity"],
        armour=off["armour"], weapon_mod=weapon.effect, rng=rng)
    _land_on_mob(w, 0, target, outcome, dmg, w.anim(0, "attack"), script)


def _heal(w, it, script, rng):
    roll = rng.randint(1, 100)
    if roll > (it.precision if it else 100):
        _note(script, "Fizzle")
        return
    amount = max(0, (it.effect if it else 8) + w.stats["Willpower"] // 10)
    amount = min(amount, w.hero_max - w.hero_hp)
    w.hero_hp += amount
    script.append(res_attack(0, [(0, -amount)], anim=w.anim(0, "cast"),
                             msg=f"+{amount}", red=False))


def _self_act(w, name, script, rng):
    it = catalogue().find(name) if name else None
    if it and it.cls == "spirit":
        _heal(w, it, script, rng)
        return
    # Defence chosen early still applies to blows later on this timeline.
    w.guard += it.precision if it else 10
    _note(script, name or "Dodge", red=False)


def _hero_move(w, x, y, script):
    orthogonal = abs(x - w.hero_x) + abs(y - w.hero_y) == 1
    if not orthogonal or not w.can_stand(x, y) or w.occupied(x, y):
        _note(script, "Failed Move")
        return
    w.hero_x, w.hero_y = x, y
    script.append(res_walk(0, x, y, w.anim(0, "walk")))


def _mob_attack(w, m, script, rng):
    if not m.alive or not w.contact(m.x, m.y, w.hero_x, w.hero_y):
        return
    off = m.offence()
    armour = w.armour().effect if w.armour() else 0
    outcome, dmg = w.strike(
        off["effect"], off["precision"], 0, w.avoidance(),
        armour=armour, rng=rng)
    anim = w.anim(m.creature, "attack")
    if outcome == "miss" or dmg <= 0:
        # A creature missing is good news, so the line is green.
        _note(script, "Miss" if outcome == "miss" else "Blocked",
              red=False, anim=anim, node=m.node)
        return
    w.hero_hp = max(0, w.hero_hp - dmg)
    label = {"crit": "CRIT", "precise": "Precise"}.get(outcome, "")
    script.append(res_attack(m.node, [(0, dmg)], anim=anim,
                             msg=f"{label} -{dmg}".strip()))


def resolve(w, actions, rng=None):
    """Merge both timelines and play them in time order.

    Equal timestamps keep the hero's event first: the list is built that
    way and the sort is stable. A dead hero takes no further actions.
    """
    rng = rng or random
    w.guard = 0
    script = []
    events = hero_timeline(w, actions) + mob_timeline(w)
    events.sort(key=lambda e: e[0])
    for _, ev in events:
        if w.hero_hp <= 0:
            break
        kind = ev[0]
        if kind == "move":
            _hero_move(w, ev[1], ev[2], script)
        elif kind == "attack":
            _hero_attack(w, ev[1], ev[2], ev[3], script, rng)
        elif kind == "self":
            _self_act(w, ev[1], script, rng)
        elif kind == "mob_move":
            _, node, x, y = ev
            m = w.mobs.get(node)
            if not m or not m.alive or w.occupied(x, y) or not w.can_stand(x, y):
                continue
            if abs(x - m.x) + abs(y - m.y) != 1:
                continue
            m.x, m.y = x, y
            script.append(res_walk(node, x, y, w.anim(m.creature, "walk")))
        elif kind == "mob_attack":
            m = w.mobs.get(ev[1])
            if m:
                _mob_attack(w, m, script, rng)
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
        w.hero_hp = w.hero_max
        start = w.locations[0] if w.locations else w.location
        w.location = start
        w.hero_x, w.hero_y = w.spawn_point(start)
        w.recall = (w.hero_x, w.hero_y)
        return 3, [chunk_int(25, w.location),
                   chunk_int(26, w.hero_x), chunk_int(27, w.hero_y)]
    if w.engaged is not None and not w.fighters():
        _regen(w, script)
        report = w.battle_report()
        leveled = w.grant_xp(w.pending_xp)
        w.gold += w.pending_gold
        w.pending_gold = 0
        w.pending_xp = 0
        if leveled:
            report += f"\nLevel {w.level}!"
            _note(script, f"Level {w.level}!", red=False)
        dead = bytes(n for n in (w.engaged or [])
                     if n in w.mobs and not w.mobs[n].alive)
        w.engaged = None
        # tag 23 replaces d.l and must be a byte[]. tag 28 is who died.
        return 2, [chunk_int(21, 0),
                   chunk_raw(23, 0, w.node_states()),
                   chunk_str(24, report),
                   chunk_raw(28, 0, dead)]
    return 1, []


def _log_world(w, status):
    where = w.LOCATION_NAMES.get(w.location, w.location)
    mobs = "  ".join(f"mob{m.node}({m.x},{m.y}) hp {m.hp}" for m in w.living())
    print(f"    \033[35mworld: {where} hero({w.hero_x},{w.hero_y}) "
          f"hp {w.hero_hp}/{w.hero_max}  {mobs}  -> status {status}\033[0m")


def _flee(w, script):
    healed = w.hero_max - w.hero_hp
    w.revert_fight()
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


@handler(21)
def equipped(req):
    """Opcode 21 — Equipped items. i.java case 21 makes a list from tag 20."""
    w, _, _ = session_world(req)
    rows = []
    for slot in ("weapon", "armour"):
        it = w.item(w.equipped.get(slot))
        rows.append(f"{slot.title()}: {it.label() if it else 'nothing'}")
    rows.append(f"Gold: {w.gold}")
    rows += [f"- {n}" for n in w.inventory
             if n not in w.equipped.values()]
    return build_response(status=1,
                          chunks=[chunk_str(20, r) for r in rows])


@handler(22)
def shop(req):
    """Opcode 22 — a Market category. The client renders tag 20 as a list with
    the title from tag 21 and the selected index from tag 22.

    Categories are the client's own (d.java:37): Melee weapons, Missile
    weapons, Armours, Skills, Spells.
    """
    w, _, _ = session_world(req)
    which = req.int_(1)
    kinds = ["weapon", "weapon", "armour", "skill", "spell"]
    kind = kinds[which] if 0 <= which < len(kinds) else "weapon"
    title = w.SHOP_CATEGORIES[which] if 0 <= which < 5 else "Market"

    items = [i for i in catalogue().get(kind)
             if which != 1 or i.cls in ("bow", "bomb")]
    if which == 0:
        items = [i for i in items if i.cls in ("sword", "axe", "hammer")]
    rows = [i.label() for i in items[:14]] or ["Nothing in stock"]
    return build_response(status=1, chunks=[
        chunk_str(21, f"{title} ({w.gold}g)"), chunk_int(22, 0)] +
        [chunk_str(20, r) for r in rows])


@handler(16)
def buy(req):
    """Opcode 16 — buy. The client drops the bought row from the shop list and
    shows tag 21, then goes back."""
    w, _, hero = session_world(req)
    name = req.get(1).decode("utf-8", "replace").split(" ")[0:99]
    wanted = " ".join(n for n in name if not n.endswith("g")
                      and not n.startswith(("E", "Ti"))).strip()
    it = w.buy(wanted)
    if hero:
        saves().save(hero, w.game)
    msg = (f"Bought {it.name} for {it.price}g." if it
           else "You cannot afford that.")
    return build_response(status=1, chunks=[chunk_str(21, msg)])


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
    state = req.int_(1)
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
    if req.get(11):
        w.location = req.int_(11)
        w.hero_x, w.hero_y = req.int_(12), req.int_(13)
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
def map_message(req):
    """Opcode 14 — a string typed on the map screen (d.java f(), field aI).
    Whatever it addressed is gone; log it and acknowledge."""
    text = req.get(1).decode("utf-8", "replace")
    print(f"    \033[35mmap message: {text!r}\033[0m")
    return build_response(status=1, chunks=[])


@handler(15)
def interest(req):
    """Opcode 15 — the detail behind a "Pick interest" row (type 1 entity kind
    10). The client renders tag 20 as a list under the tag 21 title."""
    w, _, _ = session_world(req)
    which = req.int_(1)
    lines = [l for l in w.text().values() if 20 < len(l) < 200]
    body = lines[which % len(lines)] if lines else "Nothing of interest."
    return build_response(status=1, chunks=[
        chunk_str(21, "Interest"),
        chunk_str(20, body[:200])])


@handler(17)
def scripted(req):
    """Opcode 17 — a type 1 entity of kind 11, the one kind that asked the
    server what should happen. Its script is lost; the client only needs a
    valid frame, and shows screen 33 either way."""
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


@handler(24)
def delete_item(req):
    """Opcode 24 — drop an item (tag 1 = its name)."""
    w, _, hero = session_world(req)
    raw = req.get(1).decode("utf-8", "replace")
    wanted = raw.split(":")[-1].split(" E")[0].strip(" -")
    gone = w.drop(wanted) if hasattr(w, "drop") else None
    if gone is None:
        for name in list(w.inventory):
            if name.lower().startswith(wanted.lower()[:12]):
                w.inventory.remove(name)
                for slot, held in list(w.equipped.items()):
                    if held == name:
                        w.equipped[slot] = None
                gone = name
                break
    if hero:
        saves().save(hero, w.game)
    print(f"    \033[35mdelete item: {wanted!r} -> {gone}\033[0m")
    return build_response(status=1, chunks=[])


@handler(25)
def spellbook(req):
    """Opcode 25 — Skills (tag 1 = 9) or Spells (tag 1 = 13), rendered as a
    list under the tag 21 title. Both come out of the recovered catalogue."""
    w, _, _ = session_world(req)
    spells = req.int_(1) == 13
    kind = "spell" if spells else "skill"
    title = "Spells" if spells else "Skills"
    known = [w.item(n) for n in w.inventory]
    rows = [i.label() for i in known if i and i.kind == kind]
    if not rows:
        rows = [f"None learned.", f"The Market sells {title.lower()}."]
    return build_response(status=1, chunks=[
        chunk_str(21, title)] + [chunk_str(20, r) for r in rows[:14]])


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
    return build_response(status=1, chunks=[
        chunk_str(21, "Rankings")] +
        [chunk_str(20, l) for l in lines or ["No heroes yet."]])


HELP_TOPICS = [
    "Move with the direction keys. Walk into a creature to attack it.",
    "A turn gives you 720 time. Moving costs 30 a tile, a strike 120.",
    "Actions sit on the bar at the bottom; pick one, then pick a target.",
    "Crates and barrels can be opened by standing next to them.",
    "Red tiles marked with arrows lead to the next location.",
    "Gold buys weapons, armour, skills and spells at the Market.",
    "Save & exit writes your hero; Start game picks up where you left off.",
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
        return build_response(status=1, chunks=[chunk_str(21, "Help")] +
                              [chunk_str(20, t) for t in HELP_TOPICS])
    icons = ["Sword - melee attack", "Bow - missile attack",
             "Shield - block, halves the next hit", "Flame - offensive spell",
             "Heart - healing spell", "Boot - move", "Hand - use or open",
             "Skull - the creature is dead"]
    if page == 6659:
        icons = ["Green arrow - an exit to another location",
                 "Chest - a container you can open",
                 "Star - a quest entity", "Coin - gold on the ground"]
    return build_response(status=1, chunks=[
        chunk_str(21, "Icon overview")] +
        [chunk_str(20, i) for i in icons])



def default(req):
    """Minimal well-formed frame. status=1 so the client does not read it as a
    duplicate login; no chunks, so we learn what breaks."""
    return build_response(status=1, chunks=[])


def dispatch(req):
    fn = HANDLERS.get(req.opcode)
    return (fn(req) if fn else None) or default(req)
