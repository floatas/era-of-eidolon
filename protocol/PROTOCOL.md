# Era of Eidolon — client/server protocol

Reverse-engineered from the three surviving JARs (CFR 0.152 + `javap`).
There are **two protocol generations**.

---

## Generation 1 — "town" client (Orumant, 2004, MIDP-1.0)

Class: `com.watAgame.eoe_town.*`, networking in `d.java`.

**Endpoint**

    String P = "http://81.7.141.67/1/";          // b.java:69, public non-final
    URL    = P + "<name>.pl"

Hardcoded raw IP, no DNS name, **no relay hook**. To redirect it you must patch
the constant pool (or intercept the IP with pf/route).

**Transport**: HTTP `POST`, body is a `¦`-delimited (U+00A6 BROKEN BAR) key=value
string, UTF-8. Headers, sent only on `login.pl` and error reports:

    X-User-Agent: <microedition.platform, else JAD "UA", else "no30">
    X-pid:        <JAD "PID-CHKSUM">          (only if present)

**Client identity constants** (build no30 / v5.2.8)

    productid = 01010101
    client    = 01010502
    build     = 5.2.8
    model     = no30

**60 endpoints**

    account/session   login.pl register.pl betaentry.pl version.pl pay.pl
    characters        charselectcreate.pl charselectchoose.pl charselectdelete.pl
                      herostats.pl herosksp.pl heroskspdelete.pl incabil.pl
    arena/combat      arenachflist.pl arenachran.pl arenachtlist.pl arenachslist.pl
                      chalissue.pl chalreceive.pl fightresult.pl battlereport.pl flee.pl
    items             ilistbuy.pl buyitem.pl selllist.pl sellitem.pl
                      equiplist.pl equipdo.pl
    social            friendlist.pl friendadd.pl friendremoved.pl invite.pl
                      banlist.pl banlistadd.pl banlistremove.pl
    mail              inbox.pl readmail.pl deletemail.pl sendmail.pl mailflist.pl
    clans             clancreate.pl clanedit.pl clanjoin.pl clanleave.pl clankick.pl
                      claninvite.pl clanreject.pl clanlist.pl clanstats.pl
                      clanhierarchy.pl myclan.pl
    content/misc      pmessages.pl panimscripts.pl boarddl.pl pgethead.pl headlist.pl
                      customget.pl customupload.pl getranklist.pl wiseman.pl
                      submit.pl errorreport.pl

**Parameters observed**

    accept amount build category charname clanname clanshortname classID client
    dex email equipid gender genericid genericID greeting headflag headid heroidx
    heroname id idx int key langcode login loose mailbody mailid model msg name
    nickname pass phoneno productid ranklistid receivername reqpass spd str
    taunt1 taunt2 taunt3 tou type victory wil

---

## Generation 2 — chapter clients (Sterling Lake, Shirad's Forge, MIDP-2.0)

Networking in `b.java` / `b.class`, method `run()` (CFR fails on it — use
`javap -p -c b.class`).

**Endpoint**

    static String a = "prod";                    // environment prefix, non-final
    URL = "http://" + a + "<N>.eraofeidolon.com/2/" + opcode + ".pl"

    Shirad's Forge  ->  http://prod4.eraofeidolon.com/2/<opcode>.pl
    Sterling Lake   ->  http://prod5.eraofeidolon.com/2/<opcode>.pl

Endpoints are **numbered**, not named: opcodes **1 and 4–28** are used
(`1.pl`, `4.pl` … `28.pl`). The opcode is the first ctor arg of `b`.

**>>> Relay hook — no binary patching needed <<<**

    String relay = MIDlet.getAppProperty("Relay");
    if (relay == null) { target = realUrl; }
    else { target = relay; setRequestProperty("X-relay-url", realUrl); }

Setting `Relay: http://<host>/` in the **JAD** makes the client POST everything
to your host, with the original URL passed in the `X-relay-url` header. This is
the intended path for standing up a replacement server.

Also read from the JAD: `INFO` (sent as field 8 of the handshake).

**Transport**: HTTP `POST`, **binary** body (not form-encoded):

    writeByte(0)
    writeByte(0)
    writeShort(len(B))     // B = static byte[] session/preamble blob
    write(B)
    ... then the request's own typed fields

**Handshake fields** (`i.java`, the version/hello message)

    1 = <varies>          5 = 2
    2 = "1.1.0"           6 = "s700"            (screen/device profile)
    3 = 1                 7 = microedition.platform
    4 = 4                 8 = JAD "INFO"

---

## Status of the hosts

    eraofeidolon.com      NXDOMAIN (lapsed; squatted by an unrelated site in 2019)
    prod4/prod5           NXDOMAIN
    81.7.141.67           no longer serving
    No numbered host was ever crawled by the Wayback Machine — there are
    no captured server responses to replay.

## On reaching Dagonar and Ravarcil

The Orumant client is a **generic** town client (`eoe_town`), but it carries its
own town-specific art (`splash` = "Era of Eidolon — ORUMANT" + Queen Sorena) and
town-specific intro text naming Sorena and Orumant. **No town-selection parameter
exists in the binary** — the only structured identifier sent is
`productid=01010101`, which is almost certainly the server-side key
(plausibly game/region/town/variant as four byte-pairs).

Conclusion: Dagonar and Ravarcil were separate builds with their own art, and
cannot be reconstructed from the Orumant JAR. They must be found as files.

---

# VERIFIED — gen-2 wire format (captured live, 2026-09-20)

Decompiled cleanly by **Vineflower** (CFR fails on `run()`); source in
`decompiled-vf/`. Confirmed byte-for-byte against a real capture.

## Request

    [ if B != null: 00 00 <u16 len> <B> ]    session blob, echoed verbatim
    <TLV chunk> <TLV chunk> ...              bare stream, no header, no count

Opcode is in the URL (`<opcode>.pl`), never in the body.

## Response

    u16 magic  = 0xBABE            (client throws IOException "Magic number" otherwise)
    u8  status                     MUST be non-zero, else "Second login detected!"
    u8  pad
    i32 bytecount                  added to the client's traffic meter
    u16 chunkcount
    <chunkcount TLV chunks>

## TLV chunk

    u8 tag, u8 type, u16 len, <len bytes>

    type 1   int     len 1/2/4 -> signed byte/short/int
    type 2,3 string  hand-rolled UTF-8, no length prefix (b.java:448/481)
    type 4   struct  'f'
    type 5   resource push: u16 key, payload; restype = key>>8, id = key & 0xFF
             key>>8:  1,9 -> byte[][]   3 -> hashtable   5,7 -> PNG
                      10 -> table       11 -> hashtable  else -> raw bytes
    other    raw bytes

## Reserved response tags (b.java run(), tag switch)

    0 -> stored as B, the session blob; echoed on every later request
    1 -> queued message dialog      2 -> immediate message
    4 -> static f (String)          5 -> static h (int)
    6 -> static e (String)          7 -> static g (String)
    3 and all others -> this.d hashtable keyed by tag; screens read from it

## Retry behaviour

Up to 3 retries, backoff `1000 << attempt` ms. `rc500` is fatal — never
return HTTP 500 from a replacement server.

## Captured opcode 1 (hello) — Shirad's Forge

    ff 01 0001 00                tag 255  int    0
    02 02 0005 "1.1.0"           tag 2    string MIDlet-Version
    03 01 0001 01                tag 3    int    1
    04 01 0001 04                tag 4    int    4
    05 01 0001 02                tag 5    int    2
    06 02 0004 "s700"            tag 6    string device profile
    07 02 002e "<platform>"      tag 7    string microedition.platform
    08 02 000c "preservation"    tag 8    string JAD/manifest INFO property

A bare `BABE 01 00 00000000 0000` (status 1, no chunks) is enough to get the
client past the handshake and into **character creation**.

## Opcodes observed live (Shirad's Forge)

    1   hello/handshake
    5   create hero      tag1 = name (string), tag2 = gender (int)
    8   enter world      tag1 = 2, tag2 = 0000, tag3 = resource want-list
    20  hero sheet (tag1=1) / score info (tag1=2)
    21  equipped items
    25  skills (tag1=9) / spells (tag1=13)
    26  rankings

`tag 255` is a **per-session sequence counter**, incremented on every request.

### The want-list (opcode 8, tag 3)

A flat array of u16 `(restype << 8) | id` keys — 72 of them for Shirad's Forge.
Every one is already present in the jar, so this is the client declaring what it
*has*, not what it lacks.

### The resp(8) NPE

`i.java` case 8 builds the map screen from two byte[][] resources:

    key 0x0100 (type 1, id 0)  -> "/10"  -- NOT in any jar
    key 0x0900 (type 9, id 0)  -> "/90"  -- NOT in any jar

CORRECTION: resource names are "/" + restype + hex(id), so type 1 id 0 is "/10",
not "/100". The file "100" in the jar is type **10** id 0 (the quest/objective
table: "Find 3rd cogwheel", "Defeat Shirard", ...). The jar carries resource
types 0,2,3,4,5,6,7,8,10,11 and **no type 1 or 9 at all**.

The second is fetched with `c(9, 0, null)` — a **null** want-vector — so a miss
dereferences null and throws. That is the `resp(8)` NullPointerException. The
resource was server-supplied and is simply gone.

Pushing a type-5 chunk with key `0x0900` and a valid byte[][] body
(`u8 count`, then `u8 len` + bytes per row; count 0 is legal) clears the NPE and
the client reaches the **Main menu**. See `server/handlers.py`.


## What the jar does not contain: the world

`d.java:105` builds the map screen from exactly the two server-only tables:

    var4 = type 1 id 0   placed entities
    var5 = type 9 id 0   map nodes

Record layout, from how d.java indexes them:

    type 1: [0] location id   [1] region (compared to current)
            [6] kind (2,3)    [12] kind (6,8,9)
            [13] name length  [14..] name bytes
    type 9: [0] location id   [11] flag

Plus per-session state that only the server held, read straight off the
opcode-8 response: tag 21 and tag 25 (byte[] per-node state), tags 22/23/24
(location id, x<<8, y<<8), tags 26/27 (ints).

So the jars ship the engine, the art, the sprites, the UI and the quest text —
but not the map. Level layout and object placement were downloaded every
session. Reviving these games means **authoring the world tables**, not just
replaying a protocol.


---

# CORRECTION: the levels ARE in the jar

An earlier note here concluded "the jars ship the engine but not the map."
That was wrong, and the error was reading only types 1 and 9. Dumping every
resource type (`tools/dump_world.py`) shows the chapter is almost entirely
self-contained:

    type 2   TILEMAPS        18 levels. 13-byte header, then width*height
                             tile bytes. 12x6 up to 35x50. Verified: every
                             file is exactly 13 + w*h bytes.
    type 3   LOCATION TEXT   keyed string table (u16 key, u16 len, bytes):
                             location name, encounter titles, full NPC
                             dialogue, action labels ("Fight Gorrak",
                             "Destroy Crate", "Trade", "Talk to Hrom")
    type 10  QUEST TABLE     objectives
    type 7   creature sprite )  same id across all three =
    type 8   creature anim   )  the creature catalogue
    type 11  creature props  )
    type 4,5,6  UI and tileset graphics
    type 0   hero sprite data

Shirad's Forge has 18 locations, named in type 3: Village, Lava Island,
Dwarven Hall, Mira's Hideout, The Lair, ... with the complete three-cogwheel
quest line, Hrom the dwarf, Mira the rogue and Shirard himself, dialogue intact.

## What is actually missing

Only two tables, both server-supplied:

    type 1  placed entities  [0] location id, [1] region, [6] kind,
                             [12] kind (6,8,9), [13] name len, [14..] name
    type 9  map nodes        [0] location id, [11] flag

Plus the per-session state on the opcode-8 response (tags 21, 25 = per-node
state arrays; 22/23/24 = location id and x/y).

So the missing piece is **which entity stands where**, not the world itself.
The maps, the art, the dialogue, the quests and the creature catalogue are all
present. And the type 3 text constrains the answer heavily: location 0x01 is a
village containing a Gorrak and an NPC named Hrom, and so on for all 18.

Reconstructing types 1 and 9 is therefore a bounded authoring job against a
known record layout, informed by text the game still carries.

---

# The turn loop (how to actually get in-game)

Three things gate progress, in order:

**1. opcode 8 must push both world tables.** `i.java` case 8 fetches type 1 id 0
and type 9 id 0 with a *null* want-vector, so a cache miss dereferences null.

**2. opcode 8 must return status 2, not 1.** The map screen is built as
`new d(..., var2, var2.c == 2)`, and that last flag becomes `d.k`. In `d.a()`:

    if (this.k) { this.a(new byte[0], false); }   // fires the first opcode 12

With status 1, `d.k` is false, no opcode 12 is ever sent, `d.c` stays false and
**every movement key is ignored** — the hero only turns on the spot.

**3. opcode 12 is the turn loop.** Client sends (d.java:678):

    tag 1 = action bytes
    tag 2 = byte[] of (nodeId, x, y) triples, one per entity in aF
    tag 3 = 1 when var2

Server replies, consumed by `d.a(b)` at d.java:708:

    tags 30..35 -> Vectors of strings, the six action menus
    tag 20, 21  -> ints
    tag 22      -> repeated chunks, one byte[8] per entity:
                   [0] node id  [1] x  [2] y
                   [3][4] l (u16)  [5][6] m (u16)  [7] anim

It ends `this.ac = (j) this.aF.elementAt(1)`, so **at least two entities must be
listed** (hero + one more) or it throws; and each node id must exist in `d.n`,
i.e. come from the type 9 table with its tag-25 state set to 1 or 2.

Then `this.c = true` and the game is interactive.

## Verified end to end

With `server/handlers.py` as written: title screen -> create hero -> main menu
-> **the Village renders** (isometric tilemap, hero sprite, HUD) -> Start game
-> **turn-based combat**, with health and action-point bars, the movement grid
and the full action bar (move / melee / ranged / shield / spell / skill / item).

All of it served by our own server. The only authored data is one 19-byte type 9
record placing a single creature.

---

# Why movement appeared broken (and the fix)

Two separate bugs, both in our data rather than the client.

## 1. Action-bar entries must be `f` records, not strings

Combat input is a state machine on `d.ab` (d.java:1297):

    ab 4  LEFT/RIGHT move along the action bar; FIRE opens a slot (ab -> 3)
    ab 3  FIRE activates the highlighted entry
    ab 1  PATH mode   - arrows walk a route, each step charged this.ak
    ab 2  TARGET mode - arrows move a target cursor
    ab 0  change target

Activation only happens for `var9 instanceof f`:

    byte[] var15 = (byte[]) var12.k;
    this.ak = (var15[0] & 255) << 8 | var15[1] & 255;   // time cost
    if (var15[2] == 2 || var15[2] == 1) { ... this.ab = var15[2]; }

So an action sent as a plain string is **inert** — it renders, it highlights,
and pressing fire does nothing at all. Tags 30..35 must be **type 4** chunks
carrying `f` records whose `k` payload is:

    k[0],k[1]  u16 time cost, against a 720-unit turn budget
    k[2]       1 = path/move, 2 = target

`enc_f()` in server/handlers.py encodes one.

## 2. Tags 20/21 are the arena centre, not spare ints

    this.Z = var1.b(20);   this.aa = var1.b(21);

The cursor is clamped to a diamond around (Z, aa) (d.java:1390):

    Math.abs(x - Z) + Math.abs(y - aa) + ... < 6

Send 0,0 and the playable area sits at the map origin while the hero stands
wherever tags 23/24 put them — the grid draws in the wrong corner and nothing
is reachable. Set them to the hero's tile.

## Verified

Village -> Start game -> combat -> action bar -> Movement menu -> Move ->
arrow keys lay a blue path across the grid, with the action-point bar draining
30 units per step.

---

# The full turn cycle (working end to end)

    opcode 8   enter world   -> status 2, world tables, hero position
    opcode 12  turn state    -> action bar (f records), entity list
      ...player queues actions...
    opcode 13  end turn      -> animation script
      ...client plays it back, then d.b(b) switches on the status...

## Opcode 13 request (d.java:768)

Tag 1 carries the whole queued action stack, one after another:

    u8 len + name bytes      f.b, the action's name
    u16 timestamp            this.ag when it was queued
    u8 mode                  f.k[2]: 1 = path, 2 = target
    payload                  mode 1: u8 stepCount, then (x,y) per step
                             mode 2: x, y

Note the client re-adds tag 1 on **every** loop iteration with a growing
buffer, so take the last chunk, not the first.

`d.d(b)` also attaches the client's own view: tag 10 entity states, 11 location,
12/13 hero x/y, 14 node states, 15/16 saved position.

## Opcode 13 reply

Repeated tag 20 chunks, each one animation step (d.java:1073):

    [0] kind   [1] duration (<<4 ms)   [2] 1 = refresh after
    [3] 0 = green text, else red       [4] message length
    [5..]      message, then payload at p = 5 + [4]

    kind 0  set animations:  p[0] count, then (node, anim) pairs
    kind 1  attack:          p[0] attacker, p[1] anim, p[2] victim count,
                             then (node, dmgHi, dmgLo) per victim
    kind 2  walk:            p[0] node, p[1] x, p[2] y, p[3] anim
    kind 4  teleport:        p[0] node, p[1] x, p[2] y
    kind 6  remove:          p[0] count, then node ids

Status drives `d.b(b)`: **1 = new turn**, 2 = fight won, 3 = lost, 4 = fled.

## The invisible-entity trap

`j.a(Graphics,...)` draws nothing when `(this.e & 63) == 0`, and `e` starts at
zero. It is set from `a` by `o()` at the start of every turn, and `a` comes from
the **anim byte of the tag 22 records** (opcode 12) — or, for mobs created in
`k()`, from **type 9 field [13]**.

Send 0 for either and the entity exists, occupies its tile, blocks movement and
takes part in the turn — but is never drawn. Use a valid anim id: the keys of
the type 11 props table. Hero and creatures share 1, 2, 4, 6, 14, 15, 17
(the +64 values are mirrored facings). 1 = idle, 2 = walk, 4 = attack.
An id the table lacks throws "Unable to get anim".

## Verified working

Title -> create hero -> main menu -> Village -> combat with **both sprites
drawn** (armoured hero, Gorrak) -> Movement -> arrow keys lay a path, action
points draining 30/step -> queue -> End turn -> opcode 13 -> the hero walks the
route -> "New turn starts".

---

# The game has TWO modes, and the server chooses

This is the thing that took longest to see. `d.c` gates everything:

    d.c == true   COMBAT. Turn-based. Arrows drive a tile cursor, actions are
                  queued on a 720-unit time budget, End turn sends opcode 13.
    d.c == false  EXPLORATION. Free velocity-based walking, the adventure HUD,
                  and **this is the only mode where type 1 entities fire**
                  (d.b() starts `if (!this.c && ...)`).

Entering the world always lands in combat: the first opcode 12 runs `d.a(b)`,
which ends `this.c = true`. You leave combat by answering **opcode 13 with
status 2** — `d.b(b)` case 2 calls `a(var1, tag28)`, and its `!var1.i` branch
sets `c = false`.

That is not a workaround; it is the game's design. The Village's own type 3
text opens with "Gorrak attacks" — you start mid-fight, win, and the world
opens up.

## Status 2 (victory) needs specific chunks

    tag 21  int; if non-zero the client then reads tag 22 as a byte[6]
    tag 23  byte[]  the new node-state array. MUST be present or d.l goes null
    tag 24  String  battle report (optional)
    tag 28  byte[]  node ids to remove (may be empty)

## Two crashes worth knowing about

**Every tag 20 result record needs at least 2 payload bytes.** The playback
loop reads `as[p]` and `as[p+1]` *before* switching on the kind (d.java:1077),
so even a no-op record throws ArrayIndexOutOfBounds without them.

**Action-bar slots 0..5 must contain only `f` records.** While a slot is open
the client casts every entry to `f` unguarded (d.java:1059) — and when a menu
arrives empty it inserts the *String* `"Empty"` itself, which then throws
ClassCastException. So every slot needs at least one real `f`; never send a
bare string and never leave one of the six empty.

## Exploration input (d.java:1528)

    UP    a.k = -45, anim 142      DOWN   a.k = 45, anim 78
    LEFT  a.j = -45, anim 14       RIGHT  a.j = 45, anim 206

Velocity-based, so it needs a held key — tapping starts and stops it. FIRE
opens a "Choose action" menu built from `d.S`, the nearby trigger-1 entities.

## Tilemap header, fully decoded (13 bytes)

    i8 ?   i16 ?   u16 walk mask low nibble (d.aB)
    u16 walk mask high nibble (d.aC)
    u16 name key  -> the location's name in its type 3 table
    i16 width   i16 height   then width*height tiles

    walkable(x,y):  ((aB >> (t & 15)) & (aC >> ((t & 240) >> 4)) & 1) == 1
                    XOR ((t & 240) == 16)

High nibble 1 flips the test: those are the "red tiles marked with green
arrows" the Village text describes. Shirad's Forge has 4 in the Village and
1 in each of the other locations.

---

# Accounts and save/resume — how the original did it

All of this is still in the client; nothing had to be invented.

    i.java:95    on startup it reads a byte[] token from a RecordStore
                 named "key"
    i.java:105   on hello (opcode 1) it sends that token as tag 1, if present
    i.java:475   whenever an opcode 1/2/19 reply has status 1 or 5 and carries
                 a byte[] in tag 21, it overwrites its stored key with it
    i.java:490   the opcode 1 reply's tag 20 is the account's hero list.
                 Empty  -> jump straight to the create-hero screen
                 Filled -> show "Select hero" (plus "Delete hero", and
                           "Create hero" when there is only one)

So the account lives on the server and the handset holds only a token. That is
why nothing survived the shutdown: the phones never had the characters.

## The flow

    opcode 1   tag 1  = stored token (absent on a fresh install)
      reply    tag 0  = session blob, echoed on every later request
               tag 20 = one `f` per hero; f.b() is the name sent back
               tag 21 = the token to persist  (status must be 1 or 5)

    opcode 4   tag 1 = chosen hero name.  status 1 -> main menu (screen 8)
    opcode 5   tag 1 = name, tag 2 = gender.  status 1 -> main menu

## A trap on opcode 5

Status 2 is **not** an error dialog. i.java case 5 writes tag 20 straight into
the name field (`((c)var1).a(0).d`) — it is the server *suggesting a name*.
Return an error string there and the client will dutifully put it in the box
and submit it as the hero's name on the next press. Ask me how I know.

## Our implementation

`server/world.py` keeps `saves/game.json`:

    accounts: token -> [hero names]
    heroes:   name  -> serialised World (location, position, hp, every mob)

The session blob is `"<token>:<hero>"`, so one echoed field identifies both the
account and the character. State is written after every completed turn.

---

# `l` and `m` are max-HP and damage, not current and max

An easy field to get backwards, and it looks like a rendering bug rather than
a data one.

In the tag 22 entity rows of the opcode 12 reply:

    [3][4] -> j.l      [5][6] -> j.m

From `j.a(int damage, int colour)`:

    this.m = Math.min(this.l, this.m + damage);

So **l is max HP and m is accumulated damage**: m = 0 is untouched, m = l is
dead. Healing is just negative damage (the value is read sign-extended as
`as[i] << 8 | as[i+1] & 255`, so a negative short works as-is).

The HUD makes the same assumption (d.java:319):

    var1.setColor(0);                                  // black
    var12 = this.a.l > 0 ? var10.m * 109 / var10.l : 109;
    var1.fillRect(119 - var12, 2, var12, 5);

It paints a **black** bar of width `m * 109 / l` over an already-full panel
graphic — black is the *missing* health, not the remaining health. Send
l = m = maxHP (the obvious-looking "current, max") and the bar blacks out
completely while the character is actually at full health. The per-entity bars
above each creature behave the same way: black instead of green.

---

# Running it in a browser

Works, end to end: CheerpJ runs FreeJ2ME, FreeJ2ME runs the MIDlet, and the
MIDlet talks to our server through the browser's own fetch.

## The two things that had to be built

**1. freej2me-web has no HTTP at all.** Its
`javax.microedition.io.Connector.open()` throws ConnectionNotFoundException for
every scheme except `sms://` — worse than the desktop build's stub. So
`tools/freej2me-web-net/` adds a real `HttpConnectionImpl` on `java.net` plus a
`Connector` that dispatches http/https to it, and `tools/patch_web_jar.py`
injects both into `freej2me-web.jar`.

**Confirmed: CheerpJ does map `java.net.HttpURLConnection` onto browser fetch.**
Their docs only mention the fetch API explicitly, so this was the main unknown.
It works unchanged.

**2. Same-origin, by construction.** CheerpJ obeys the browser's origin rules,
so `server/webserve.py` serves the emulator *and* `/relay` from one port. The
jar's `Relay` manifest property points at `http://localhost:8000/relay`, which
is same-origin with the page — no CORS, no proxy, no Tailscale.

## Server requirements

* **Range** support — CheerpJ fetches its runtime and the jars with byte ranges.
* **Clean URLs** — the launcher links to `/run`, not `/run.html`.
* **No COOP/COEP.** Setting `Cross-Origin-Embedder-Policy: require-corp` blocks
  CheerpJ's own runtime, which loads from their CDN and does not send CORP.
  The page then hangs forever on "Loading CheerpJ...".

## Scripted install

`tools/patch_web_launcher.py` adds `?autojar=<url>&name=<substring>` to the
launcher, so a jar can be installed and launched without touching the file
picker — needed for embedding, and for automating tests.

One CheerpJ constraint to respect: you cannot call into Java while a Java
thread is still running ("Java code still running, check for a missing await"),
so the install steps let the event loop drain between calls instead of asking
the loader for the app id straight after parsing.

    ./run/web.sh        then open the URL it prints

---

# Running more than one chapter

Both gen-2 chapters work against the same server, with nothing chapter-specific
in the code. `server/world.py` reads it all out of whichever jar it is given:

    locations   the type 2 ids present in the jar
    names       each tilemap's header carries the string key for its own name
                (field aD) into that location's type 3 table
    exits       the high-nibble-1 tiles, clustered so adjacent ones count once
    creatures   the ids shared by types 7/8/11

Which gives, for free:

    Shirad's Forge  18 locations  Village, Lava Island, Dwarven Hall,
                                  Mira's Hideout, The Lair, The Core,
                                  The Forge, Old Shrine, The Long Run,
                                  Cave of Doom, Aldor's Outpost, Fire Cave,
                                  The Evil Eye, Ilrik's Tomb, Dune Burrow,
                                  Crypt, Lava Pit, Golem Secret
    Sterling Lake   17 locations  Harbour, Sea Kelp, Holy Site, Beach,
                                  Shallows, Pirate Den, Snake Pit, Killer Bay,
                                  The Pier, Gold Island, Port Kull, The Wreck,
                                  Point Murk, The Nest, The Grave,
                                  Isle of Dead, The Deep

The relay tells them apart by the `X-relay-url` host — prod4 is Shirad's Forge,
prod5 is Sterling Lake — and heroes are scoped per chapter, because the
original ran them as separate servers with separate accounts.

    ./run/play.sh SterlingLake
    GAME=SterlingLake ./run/drive.sh

## What will NOT work: the gen-1 town clients

Orumant (and presumably Dagonar and Ravarcil) speak the **first** protocol:
named `.pl` endpoints, `¦`-delimited text bodies, no relay hook, and a
hardcoded raw IP instead of a hostname. None of the gen-2 server applies. They
would need a second server implementing the 60 named endpoints documented
above, plus constant-pool patching or a pf redirect to reach it.

## Two bugs this shook out

**Cross-chapter save leakage.** Heroes used to be keyed by bare name, so a
Sterling Lake hero called "Hero" loaded a Shirad's Forge world of the same
name. The symptom is a very clear client-side error naming the resources it
could not find — "Unable to get resources from server: 201 301 718 818 b18",
i.e. location 1 and creature 0x18, which exist only in the other chapter.

**A silently mismatched patch.** `st.create_hero(key, name)` never gained its
`game` argument because a scripted replacement was written with the wrong
indentation, so every hero landed in the default chapter. Worth checking that
an edit actually applied, not just that the script reported success.

---

# Logging, and what can and cannot be captured

**The gen-2 client never reports its own errors to the server.** `i.java:669`
only builds a dialog; the `errorreport.pl` endpoint existed in gen 1 and was
dropped. So an in-game "Error" box leaves no server-side trace. Plan around it.

What IS captured, now written to disk automatically:

    server/logs/relay.log     every request decoded, every response, the world
                              state after each turn, and any handler exception
    server/logs/emulator.log  the emulator's own stdout: our [net] lines,
                              FreeJ2ME's missing-resource warnings, and any
                              stack trace it prints itself
    server/capture/*.bin      every request body, raw

## Reading an in-game Error box

The title line names where it happened, and the last line is the opcode and
MIDlet version:

    run_s      the animation/playback thread   (g.java:110)
    resp(N)    processing the reply to opcode N (g.java:158)
    key(N)     handling key N                   (g.java:78)
    key_s(N)   same, outer catch
    net(N)     network failure on opcode N      (i.java:466)
    sN vX.Y.Z  the opcode and the MIDlet version

So `run_s / Unable to get anim 4 for monster id 1 / s10 v1.1.1` means: the
playback thread tried to animate node 1 with anim 4, and that creature's type
11 props table has no entry 4.

## Animation ids are per creature and NOT uniform

This is the trap behind that error. Each creature's valid ids are the keys of
its own type 11 table:

    Shirad's Forge  0x2a  has no 2 — it cannot walk
    Sterling Lake   0x3a  has no 4 — it cannot use the attack animation
                    0x37  has no 4

j.java throws `Unable to get anim N for monster id M` rather than degrading, so
the server must never send an id the creature lacks. `World.anim(creature,
kind)` picks from that creature's own table with a fallback chain
(attack: 4, 5, 6, 3, 2, 1), and every animation the server emits now goes
through it.

---

# CORRECTION: the character system is not lost, it is in the client

An earlier assessment here said items, XP, levelling, shops and NPCs were
"absent entirely". That was wrong — most of the *rules* are compiled into the
MIDlet as static tables (d.java:27-37):

    y[]  the six action-bar categories
         Movement, Melee attack, Ranged attack, Defence,
         Offence spells, Defensive spells
    z[]  the six stats
         Strength, Intelligence, Dexterity, Toughness, Willpower, Speed
    A[]  what each stat does, verbatim:
         Strength      +weapon damage, +carry more weight, +heavier weapons
         Intelligence  +effect to all spells cast on foe
         Dexterity     +hit chance, +defense, +complex weapon
         Toughness     +life points
         Willpower     +spell resistance, +protect spells cheaper prices
         Speed         +faster when using skills and spells in fight
    b[]  the shop categories
         Melee weapons, Missile weapons, Armours, Skills, Spells

and `d.a(int)` carries the raise-cost curve: a stat below 48 costs 3 points per
raise, below 78 costs 2, above that 1. `d.c(b)` reads the six stat values as a
byte[6] in tag 22, with the number of unspent raises in tag 21.

## The dead menus are trivial to fill

Every one of them renders a server-formatted string or list (i.java:619-660):

    20  h(30, tag23 = title, tag20 = body)      hero sheet / score info
    21  list from tag 20                        equipped items
    25  list from tag 20, title tag 21          skills (tag1=9) / spells (13)
    26  list from tag 20, title tag 21          rankings
    27  list from tag 20, title tag 21          help
    22  list from tag 20, title 21, int tag 22
    16  buy

So the client does no interpretation at all: the server writes the text. All of
the above are now implemented, plus XP, levels, gold and the stat block.

## What IS genuinely lost

    the item catalogue      names, stats, prices, equip slots
    the skill/spell lists   their costs and effects
    creature stats          hp, damage, xp value
    the XP curve            actual numbers
    type 1 / type 9         where everything stood in the world

These were all server-side rows. The systems that consume them survive, so
they can be authored against known shapes rather than guessed at.

---

# The official rules document recovers most of the "lost" design

`notes/EOE-GAME-RULES-0.2.pdf` — 8 pages, pulled from the 2004 site — is
watAgame's own design spec. It is for the arena MMO rather than the single
player chapters, so clans, respect and Power Hour do not apply, but the
character, item and combat systems are the same engine.

## What it pins down

    abilities      start at 5. Strength, Dexterity, Intelligence, Speed,
                   Toughness, Charisma
    levels         hero starts at level 0; 49 levels; 4 ability points each;
                   "ability scores increase faster at low values than at high"
                   — which is exactly the client's <48 costs 3, <78 costs 2,
                   else 1 curve
    life points    tied to Toughness, FULLY regenerated after each fight
    weight         equipment weight slows you down

    turn           3 phases: Situation overview, Choose actions, Results.
                   Both players choose simultaneously, blind. 20 seconds to
                   choose; each action consumes part of that budget. Actions
                   resolve in timeline order.
    movement       1 square per segment, NO DIAGONALS, cannot enter or end on
                   an occupied square; ties go to the faster timeline
    hit chance     skill with that weapon + Dexterity vs opponent's avoidance
                   -> base chance, then a random roll
    damage         skill effect + weapon + Strength = base; a low roll (a
                   precise hit) multiplies it
    spells         always hit, but can be resisted (caster ability vs target's)
    armour         reduces melee and missile damage only, never spell damage
    shields        need a free hand; a two-handed weapon auto-unequips a shield

    skills         4 categories: Move, Melee, Missile, Defence
    spells         5 categories: Mystic, Pain, Protect, Bless, Curse
    weapons        melee: Sword (fast, low damage, high I)
                          Axe (a blend, high D)
                          Hammer (slow, highest damage, high St)
                   missile: Bow (high D, two-handed, needs LoS)
                            Bomb (targets a square, no LoS, blast radius 1)
                   traps:  Mine, placed with "Place Mine", cleared with
                           "Remove mine"
                   plus Armour, Shields, Charms
    schema         every skill, spell and item has: Name, Description,
                   Ability requirements, Time (Ti), Effect
    titles         Fumbler, Beginner, Trained, Experienced, Master, Expert,
                   Sensei — per skill/spell, with a Promotion% toward the next

## One evolution between generations

The PDF lists **Charisma** (reduces the cost of buying spells, skills and
items). The gen-2 client's stat table has **Willpower** in that slot, described
as "+spell resistance, +protect spells cheaper prices" — so the two were merged
when the chapter games were built.

## What this leaves genuinely open

Only the numbers and the lists: the actual effect values, time costs, prices
and ability requirements, the specific item/skill/spell names, and creature
stats. The framework they slot into is fully specified.

---

# The official site had the catalogue, and the Wayback Machine kept it

`notes/site/` — scraped from eraofeidolon.com. The pages that matter:

    ?go=game&type=items&itemtype=1..6   weapons, armour, skills, spells,
                                        traps/bombs, charms
    ?go=game&type=skills                the skill list
    ?go=game&type=spells                the spell list
    files/EOE_Game_Rules_0.9.pdf        the FINAL rules (titled 1.5 inside)

Readable in `notes/CATALOGUE.md` (70 KB), machine-readable in
`notes/site/catalogue.json`. **305 entries:**

    64  weapons        sword / axe / hammer / bow / bomb classes
    18  armour         Scrapsuit -> ... -> Blood Armour
    47  skills         move / melee / missile / defence
    64  spells         tagged by category, e.g. "1 - Blink (spectral)"
    18  charms         each states its exact bonus
    23  gladiators     the named arena opponents, with backstories
    71  overview-page duplicates of the skill and spell lists

Note `itemtype=5` is not an item category at all — it is the **Gladiator
roster**: The Gimp, Scarboy, Eliana, Swifter and the rest, the NPC opponents
of the arena. That is the closest thing we have to a creature list.

The items are **numbered in progression order** and tagged by class —
"1 - Bloody Blade (sword)", "2 - Longfang (sword)", "5 - Giant Sword (sword)" —
and grouped by which town sells them (Orumant, Dagonar, Ravarcil). Armour runs
Scrapsuit -> Snail Shell -> Iron Shell -> Doom Suit -> Spike Suit -> Blood
Armour. Charms state their effect **numerically**: Force Stone +3 Strength,
Hunter Gem +3 Dexterity, Mage Ring +3 Intelligence.

## Two rules versions, and they show the evolution

`EOE-GAME-RULES-0.2.pdf` (2004) and `EOE-GAME-RULES-0.9.pdf` (titled "Game
Rules version 1.5" inside). The later one matches OUR client generation:

    0.2                              1.5
    Charisma                         Willpower
    4 ability points per level       2 ability points per level
    spells: Mystic, Pain, Protect,   spells: Intelligence-based (Bane,
            Bless, Curse                     Spectral) and Willpower-based
                                             (Spirit, Guardian)
    items: Weapons, Armour,          items: Close combat, Ranged attack,
           Shields, Charms, Traps           Armour, Magic items

1.5's Willpower is described as "reduces the cost of spells, skills and items /
chance of resisting hostile spells / effect of Spirit and Guardian spells" —
which is exactly what the gen-2 client's own stat table says. It also adds
critical hits to Dexterity, and documents the handset controls.

## What is still missing after all this

Only the per-item numbers: effect values, Time (Ti) costs, prices and the
ability requirements for each of the 167 catalogued things. Those were rendered
by the server in the Market and Academy screens and never published. Everything
else — names, classes, descriptions, progression order, which town sold what,
and the formulas they feed — is recovered.

---

# Type 1 records have FOUR trailing blocks, not one

This one costs you an ArrayIndexOutOfBounds that looks nothing like its cause.
After the kind switch, `a(Object)` (d.java:964) walks three more lists:

    p    = 14 + [13]                          block 1, read by d.b()
    var12 = 14 + [13] + 1 + rec[14 + [13]]    block 2
    var15 = var12 + rec[var12] + 1            block 3
    var20 = var15 + rec[var15] + 1            block 4

each being `u8 count` followed by that many bytes:

    block 1  prerequisites — count, then [mode, ids...]. mode 0 checks the
             d.i entity states, 1 checks the d.l node states; every id listed
             must already be state 3 or the entity will not fire
    block 2  ids to ARM      — state 1 becomes 2
    block 3  ids to COMPLETE — state 2 becomes 3, and fires any kind 6 tilemap
                               patch belonging to them
    block 4  ids to DISABLE  — anything not already 3 becomes 4

Those three lists are the quest graph: finishing one entity arms the next,
marks itself done, and switches off whatever it replaces. That is how "destroy
the crate -> a lever appears -> the bridge rises" was wired without any
server round trip.

`var12` is computed unconditionally, so a record that stops after block 1 is
read one byte past its end — on a 19-byte record, "Index 19 out of bounds for
length 19".

# Opcode 10 is the on-demand resource fetch

When `k()` is missing anything for the location it is loading, it builds a
want-list of u16 `(restype << 8 | id)` keys and sends them as tag 1 of opcode
10 (d.java:282), then waits with `d.T` false — the "Please wait..." screen.
Reply with type-5 resource pushes. If a second pass still finds them missing it
throws "Unable to get resources from server:" listing the keys in hex, which is
a genuinely helpful error.

# Type 1 and type 9 describe the WHOLE world, not one location

Both are fetched once, at opcode 8, and never re-requested — which is why each
record carries a location field. Send only the current location's rows and
everything else is empty: no monsters anywhere else, and no way back.
