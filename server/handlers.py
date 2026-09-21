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

MOVE_COST = 30       # per tile, against the 720-unit turn budget
ATTACK_COST = 120
TURN_BUDGET = 720

# The six server-supplied action-bar slots, in the order the client draws them
# (its own icons: move, melee, ranged, shield, spell, skill). mode 1 = walk a
# path, 2 = pick a target tile, 0 = act on the current target with no cursor.
# The slot TITLES come from the client (d.java:27):
#   Movement, Melee attack, Ranged attack, Defence, Offence spells,
#   Defensive spells
# These are the entries inside each, named to match their category.
ACTIONS = [
    ("Move",     MOVE_COST,   1),
    ("Strike",   ATTACK_COST, 2),
    ("Shoot",    100,         2),
    ("Block",    60,          0),
    ("Firebolt", 150,         2),
    ("Mend",     90,          0),
]


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

    status 2 (not 1) sets d.k, and d.a() then fires the first opcode 12 — the
    turn loop. With status 1 d.c stays false and movement keys do nothing.
    """
    w, _, _ = session_world(req)
    return build_response(status=2, chunks=[
        push_resource(1, 0x0100, byte_table(w.entity_table())),  # type 1
        push_resource(3, 0x0900, byte_table(w.mob_table())),   # type 9
        chunk_raw(21, 0, w.entity_states()),
        chunk_raw(25, 0, w.node_states()),
        chunk_int(22, w.location),
        chunk_int(23, w.hero_x),
        chunk_int(24, w.hero_y),
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
    for m in w.living():
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
    w, _, _ = session_world(req)
    sync(req, w)
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

MOB_BUDGET = 360      # creatures get half a turn's worth of time
MOB_MOVE = 60
MOB_ATTACK = 180


def hero_timeline(w, actions):
    """(time, fn) events for everything the player queued, in clock order."""
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
            events.append((ts, ("attack", pts[0][0], pts[0][1])))
        elif mode == 0:
            events.append((ts, ("self", name)))
    return events


def mob_timeline(w):
    """Creatures spend their own budget closing the distance and swinging."""
    events = []
    for m in w.living():
        t, x, y = 0, m.x, m.y
        while t < MOB_BUDGET:
            dx, dy = w.hero_x - x, w.hero_y - y
            if max(abs(dx), abs(dy)) <= 1:
                t += MOB_ATTACK
                if t > MOB_BUDGET:
                    break
                events.append((t, ("mob_attack", m.node)))
            else:
                t += MOB_MOVE
                if t > MOB_BUDGET:
                    break
                nx = x + (1 if dx > 0 else -1 if dx < 0 else 0)
                ny = y + (1 if dy > 0 else -1 if dy < 0 else 0)
                events.append((t, ("mob_move", m.node, nx, ny)))
                x, y = nx, ny
    return events


def resolve(w, actions):
    """Merge both timelines and play them out in order."""
    script = []
    for _, ev in sorted(hero_timeline(w, actions) + mob_timeline(w),
                        key=lambda e: e[0]):
        kind = ev[0]

        if kind == "move":
            _, x, y = ev
            if not w.can_stand(x, y) or w.mob_at(x, y):   # NPCs block too
                continue          # blocked: skip this step, keep the rest
            w.hero_x, w.hero_y = x, y
            script.append(res_walk(0, x, y, w.anim(0, "walk")))

        elif kind == "attack":
            _, tx, ty = ev
            target = w.mob_at(tx, ty, include_npcs=False)
            if target is None:
                near = [m for m in w.living()
                        if max(abs(m.x - w.hero_x), abs(m.y - w.hero_y)) <= 1]
                target = near[0] if near else None
            if target is None:
                script.append(result(0, [0], msg="Out of reach"))
                continue
            dmg, crit = w.attack_damage()
            target.hp -= dmg
            script.append(res_attack(0, [(target.node, dmg)],
                                     anim=w.anim(0, "attack"),
                                     msg=("CRIT -%d" % dmg) if crit else f"-{dmg}"))
            if target.hp <= 0:
                target.alive = False
                script.append(res_remove([target.node]))
                w.gold += 5
                if w.grant_xp(40):
                    script.append(result(0, [0], msg=f"Level {w.level}!"))

        elif kind == "self":
            if ev[1] == "Mend":
                heal = min(6, w.hero_max - w.hero_hp)
                w.hero_hp += heal
                script.append(res_attack(0, [(0, -heal)],
                                         anim=w.anim(0, "idle"),
                                         msg=f"+{heal}", red=False))
            else:
                script.append(result(0, [0], msg="Braced"))

        elif kind == "mob_move":
            _, node, x, y = ev
            m = w.mobs.get(node)
            if not m or not m.alive or w.occupied(x, y) or not w.can_stand(x, y):
                continue
            m.x, m.y = x, y
            script.append(res_walk(node, x, y, w.anim(m.creature, "walk")))

        elif kind == "mob_attack":
            m = w.mobs.get(ev[1])
            if not m or not m.alive:
                continue
            if max(abs(m.x - w.hero_x), abs(m.y - w.hero_y)) > 1:
                continue          # the hero moved away first
            # Armour reduces melee and missile damage, never spells.
            dmg = w.damage_taken(random.randint(3, 8))
            w.hero_hp = max(0, w.hero_hp - dmg)
            script.append(res_attack(m.node, [(0, dmg)],
                                     anim=w.anim(m.creature, "attack"),
                                     msg=f"-{dmg}"))

    return script


@handler(13)
def end_turn(req):
    """Opcode 13 — end turn. tag 1 carries the whole queued action stack; note
    the client re-adds it on every loop iteration with a growing buffer, so the
    LAST chunk is the complete one. We answer with the animation script in
    repeated tag 20 chunks, and a status d.b(b) switches on:

        1 = new turn   2 = fight won   3 = lost   4 = fled
    """
    w, _, hero = session_world(req)
    sync(req, w)
    acts = parse_actions(req.get(1))
    if acts:
        print("    \033[35mactions: " +
              ", ".join(f"{n}(mode {m}){p}" for n, _, m, p in acts) + "\033[0m")
    script = resolve(w, acts)
    if not script:
        script.append(result(0, [0]))

    status = 1
    if not w.living():
        status = 2                                  # everything here is dead
    elif w.hero_hp <= 0:
        status = 3
        w.hero_hp = w.hero_max
        w.hero_x, w.hero_y = 12, 17

    print(f"    \033[35mworld: {w.LOCATION_NAMES.get(w.location, w.location)} "
          f"hero({w.hero_x},{w.hero_y}) hp {w.hero_hp}/{w.hero_max}  "
          + "  ".join(f"mob{m.node}({m.x},{m.y}) hp {m.hp}" for m in w.living())
          + f"  -> status {status}\033[0m")

    if hero:
        saves().save(hero, w.game)

    chunks = [chunk_raw(20, 0, r) for r in script]
    if status == 3:
        chunks += [chunk_int(25, w.location),
                   chunk_int(26, w.hero_x), chunk_int(27, w.hero_y)]
    if status == 2:
        # d.b(b) case 2 (the win path) is what drops the game out of combat and
        # back into exploration, where entities and exits actually fire:
        #   c(var1)                      tag 21 int; if non-zero it then reads
        #                                tag 22 as a byte[6]
        #   this.l = d.get(23)           MUST be a byte[] or l goes null
        #   this.a(var1, d.get(28))      nodes to remove; !var1.i sets c = false
        dead = bytes(m.node for m in w.mobs.values()
                     if not m.alive and m.location == w.location)
        chunks += [chunk_int(21, 0),
                   chunk_raw(23, 0, w.node_states()),
                   chunk_str(24, w.victory_text()),
                   chunk_raw(28, 0, dead)]
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
    w, _, _ = session_world(req)
    which = req.int_(1)
    if which == 2:
        body = (f"{w.name()}\n\nLevel {w.level}\nXP {w.xp}/{w.xp_for_next()}\n"
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


def default(req):
    """Minimal well-formed frame. status=1 so the client does not read it as a
    duplicate login; no chunks, so we learn what breaks."""
    return build_response(status=1, chunks=[])


def dispatch(req):
    fn = HANDLERS.get(req.opcode)
    return (fn(req) if fn else None) or default(req)
