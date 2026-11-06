# Era of Eidolon, put back together

What watAgame shipped, what went missing when their servers stopped, what we
rebuilt, and — kept separate on purpose — what we changed.

---

## The game

Era of Eidolon was a mobile RPG by watAgame of Copenhagen, running from about
2004 to 2008. It came in chapters, each its own J2ME MIDlet: **Shirard's
Forge**, **Sterling Lake**, **Mistral Grove**. Alongside them ran a different
sort of game — the Arena, a player-versus-player duelling ladder, of which
**Dagonar** and **Orumant** survive.

The chapters are single-player. You are one hero, walking an isometric world
of eighteen rooms, fighting creatures a turn at a time, and doing what the
locals ask of you. The whole of Shirad's Forge is one errand: three cogwheels,
hidden across the volcano, that restore the lava streams and bring down a
wizard's statue.

## Why it stopped working

The jar on your phone is not the game. It carries the art and the ground —
the tilemaps, the location text, the creature sprites and their animations,
the quest strings — but it does not carry **the world**.

Two resources never shipped in any build we have:

    type 1   placed entities    doors, triggers, chests, the quest machine
    type 9   creature nodes     every monster, and the square it stands on

Those came from the server, over HTTP, as you walked. So when the servers
went away, a jar that installs perfectly boots to a menu, starts a game, and
stands in an empty world. Every copy of Era of Eidolon on the internet is a
complete game with its contents removed.

## The protocol

The client posts to `prod4.eraofeidolon.com/2/<opcode>.pl` with a binary
body: magic `0xBABE`, then records of `u8 tag, u8 type, u16 len`. There are
28 opcodes, covering login, hero creation, resource fetch, movement, fights,
shops, ability raises and saving. All 28 are implemented here.

One more, **opcode 31**, is sent when a map finishes loading. It is how the
server learns which room you walked into when no art needed fetching.

## What the jar still knows

Enough to rebuild almost everything, because the client had to be told how to
read what the server sent, and that reading is still in the code:

- **tilemaps** — a byte a tile, low nibble the ground, high nibble the
  obstacle. Obstacle 1 is a walk-mask override, 2 a stone arch, 10 a crate,
  11 a barrel.
- **doorways** — a *painted ground tile*, not a flag: index 12 in Shirad's
  Forge, 14 in Sterling Lake, 15 in Mistral Grove, identifiable by colour.
- **animations** — numbered scripts: 14 is walk, 1 stand, 4 swing, 6 die,
  8 cast, 12 bow. Adding 64 gives the away-facing set and bit 7 mirrors it,
  which is how four facings come out of two sprite sets.
- **the turn** — 720 units. A step costs 40, a blow 60, a dodge 20.

## What was recovered

Fifteen jars, and exactly one of them carries the missing tables: a
**176×208 build of Shirad's Forge, version 1.0.0, dated 29 April 2005**,
155 KB against the 64 KB of its sibling, 76 resources against 4. Nothing
marked it out; it was found by listing the resources of every jar we hold and
noticing two names nothing else had.

    type 1   235 entities across 18 locations
    type 9   111 creature nodes

Every entity box falls inside its own map. Every exit's arrival square falls
inside its destination. Every creature stands on its own map, and every
creature id is a sprite sheet the jar carries. The tilemaps of that build are
the same size, room for room, as the 1.1.0 build we play — so the tables
apply directly.

Sterling Lake and Mistral Grove have no such build. Their worlds are
reconstruction, and are marked as such wherever they appear.

## Things the tables turned out to say

**Bytes 16–19 are a patrol box, not a difficulty curve.** They look like one
— the same Beetle reads `12, 6` in Dune Burrow and `32, 33` in The Lair — but
they are `x0, y0, x1, y1`. All 69 creatures that carry them stand inside their
own box; a median box is a tenth of its map, where a random tile falls inside
one 22% of the time; and the rows that carry them are exactly the rows whose
byte 15 says the creature walks. The depth correlation was map size.

**The Crypt is not a small room.** It arrives as a 53-tile cross with two
ghosts, and grows to 147 tiles as you fight. Its chambers are painted in by
tilemap patches, wave by wave, and the creatures standing in them wake at the
same moment. Twenty-two entities for one fight, against two or three for a
typical room.

**Doorways are load boundaries.** Most sit on a map's edge and meet their
partner on the opposite edge of the next map, so the eighteen rooms lay out
flat as one continuous world. The whole thing is 14,294 map cells — about
14 KB — which would have fit in any handset. Splitting it was about the
*download*, over GPRS, a room at a time.

**Eleven creatures start asleep.** A `kind 5` entity switches them on:
Shirard, who does not exist until the cogwheels bring his statue down; the
Crypt's second and third waves; and a twin standing on Mira's own square,
which is her second phase, written as a separate creature rather than a flag.

## What is ours, not theirs

Kept separate because a reconstruction that quietly invents things is worth
less than one that says where it stopped knowing.

**Which creatures wander.** Byte 15 starts the walk animation when a
creature loads, so it paces its patrol box while you explore — and the 69
rows that carry it are exactly the 69 that carry a box. Rooted creatures
stand still until a fight starts; all eleven Fungusmen are rooted, and so are
six of the twenty-eight skeletons. Shirad's Forge sends watAgame's own rows,
so that is theirs. Sterling Lake and Mistral Grove have no such rows, and
there anything that *has* a walk animation is told to wander. That is a guess
standing in for a byte we do not have.

**The server's own numbers.** The tables that held hit points, prices, gold
and experience were the server's. What survives is the Arena's item
catalogue — 203 entries with real times, effects, prices and requirements —
and the client's own turn costs. Everything else is fitted.

**The balance.** The catalogue was written for the Arena, where a duellist
levels to 49 and item requirements run to 78. A chapter hero clears 87
creatures and reaches about level 19, so two thirds of the list is
unreachable. Chapter I now sells a third of the melee, half the bows and a
third of the armour, with requirements respread over the range a chapter hero
actually covers, and the rest held for the sequels.

**The fight.** A creature threatens a shape rather than every square around
it — a Skeleton one square, a Golem three in front, the Beholder four
corners, a Fungusman four at range and none adjacent. It swings at a speed
set by its weight, so light things land several small blows and heavy ones
land two large. That makes armour worth wearing against the quick and
stepping out of reach worth more against the slow. None of this is watAgame's;
their creatures all hit the same way.

**How hard a fight is.** The route is split into three tiers at its
traders, and every creature is sized to its tier. A Beetle takes a turn of
the tier's best weapon, and a turn in a shape costs a third of the life the
tier expects. Pay follows weight and tier. watAgame's creature numbers were
the server's and are gone. Their weights, byte 11, still set how fast a
creature swings and what it pays. See `BALANCE.md`.

**Four bosses, two phases.** Mira, Aldor, the Beholder and Shirard each fight
in two pools, and the second turns the safe squares around. watAgame wrote
Mira's second phase as a separate creature on her square. That twin is now
sent as gone and the phase happens on her own node, one mechanism for all
four. Which bosses, their shapes and their length are ours.

**The ability coefficients.** The rules name every term of a blow and none
of the ratios. An ability adds a third of itself to a blow, scaled by the
swing's time, so it adds the same over a turn to a sword and a hammer:
Strength for a blade, Dexterity for a bow. A spell adds the whole ability,
and the target's resistance is subtracted instead of switching the spell
off. Minor Cure heals by the whole of Willpower. A weapon's own time,
watAgame's number, is what a swing costs.

**Toughness and Speed.** The rules say life is "directly connected" to
Toughness and that Speed "affects how fast all actions are performed", and
give no numbers. Here a point of Toughness above 3 is 5 life, and an action
takes 120 / (117 + Speed) of its time.

**The ending.** Beating Shirard fired a kind 11, which asked the server for a
script and then closed the game. The server drops that from his death
switch; the epilogue in the battle report, and the hero staying in the world
afterwards, are ours.

**Quest rewards.** Dreyfus, Tillic and Milas name their reward out loud: 3,
"a few" and 5 Gold coins. In this economy that read as a mistake. They now
pay 250, 150 and 400, and the run jar's copy of their lines says so. The
original jar is untouched.

**Trophies.** watAgame's chapters kept a score and rankings on their server.
The eighteen trophies and the platinum are ours (`server/trophies.py`).

**Weapons and shells.** Chapter I weapons have their effect and price set so
a sword, an axe or hammer, and a bow are each the right tool somewhere. The
sword is for soft packs, the heavy line and the bow for armour. Beetles and
Golems wear shells to make that true. Weapon times and classes are
watAgame's; their effects, prices and requirements here are ours.

**No room is moved.** Fire Cave, Ilrik's Tomb and Aldor's Outpost were for
a while turned a quarter clockwise, with a bridge laid over Fire Cave's lava,
so that the chapter would lay out as one picture. watAgame had already joined
those rooms by door, so the turn bought nothing but the picture. It is gone:
every grid, door and creature square on the world map is the 2005 jar's, and
the three rooms sit apart on the map because that is where the data puts them.

**Recycle.** The item screen's "Delete" is renamed Recycle in the run jar,
and it returns 30% of the price. The chapters have no way to sell, and a
hero who starts with no gold needs one.

**The map ping.** The client reports a room only when it has to fetch art
for it. The run jar is patched to send opcode 31 on every map load, so the
server always knows where you are.

**The hero.** Rules 1.5 say every ability starts at 15. That is the Arena's
number. A chapter hero now starts at 3, the floor of the item ladder, so that
levelling has somewhere to go. It is the one place the rules are knowingly
set aside.

## What is still missing

- Type 1 and type 9 for Sterling Lake and Mistral Grove. No offline build of
  either is known.
- The Arena server entirely — 64 named CGI endpoints, none implemented.
- Ravarcil, a fourth chapter that was announced and may never have shipped.
- Per-chapter shop stock, the experience curve, prices, and the hero's
  maximum life. All fitted.
- ~~Whether byte 11 of a creature row is hit points or a respawn countdown.~~ Settled: a respawn countdown. See notes/recovered.
  The server reads it as both.
- Any per-creature difficulty. Bytes 16–19 were the last hope for it.
- Whatever watAgame's server said at the end. Every entity kind is decoded
  now; the ending's script was the server's.
