# What is still missing

One list. Shirad's Forge is the chapter being played. The other two chapters
and the Arena are recorded at the bottom so they are not forgotten.

Checked against the code on 27 September 2026. Where a note elsewhere
disagrees with this one, this one and `server/` are current.

## Shirad's Forge — in place

The early 176×208 jar holds the world: 18 tilemaps, the text, the quests,
235 placed entities (doors, crates, the lava bridge, the fight triggers) and
111 creatures with squares and names. The phone keeps the quest log itself.

Three rooms, Fire Cave, Ilrik's Tomb and Aldor's Outpost, are stored
north-up in that jar and play turned a quarter clockwise. Fire Cave's lava
bridge is moved to meet Aldor's door once it turns. `server/layout.py` does
this on load. `run/mkjar.py` rewrites the run jar the same way, and an old
save is moved with it. The jar in `jars/` is untouched.

Eleven creatures start dormant and wake when their kind 5 entity fires:
Shirard, the Crypt's second and third waves, and Mira's twin, who is her
second phase.

**Fights.** Straight steps, a bow needs a clear view, a spell takes the
exact square it names and ignores armour, Dodge lasts the turn, and both
sides share the 720 clock. A weapon's own time is what a swing costs, so a
sword swings about twice for each axe blow. A creature swings two to four
times a turn by weight. Each species threatens a shape, not every
square: a Skeleton one square in front, a Golem three, the Beholder the four
corners, a Fungusman four squares at range. With a bow in hand, every
creature threatens the full ring. Stepping out of the shape is the dodge.
Mira, Aldor, the Beholder and Shirard each fight two phases, and the
second phase turns the safe squares around. A bow no longer flattens their
shapes.

**The hero.** Level 0, every ability 3, no gold, 40 life plus 6 a level. The
free kit is the Bloody Blade, the Short Bow and the Scrapsuit. A win opens
**Raises left** (2 points a level; one point adds 3 / 2 / 1). A level costs
60 + 20 × level experience. A kill pays by the species' weight and its
tier. Dreyfus pays 3 gold, Milas 5, Tillic 3. Other
checkpoints stay silent, because the jar already showed the line.

**Items.** Chapter I sells 22 of watAgame's weapons and suits, retuned
(`notes/chapter-items.json`). The five traders sell the route tier they
stand in, Lava Island I, Dwarven Hall and Fire Cave II, The Lair and The
Core III. Every shop sells something different. A crate gives gold and the next step up in the hero's
own line, one weapon and one suit a tier. "Delete" on an item is now
**Recycle** and returns 30% of the price (`tiers.RECYCLE_PERCENT`). The phone's own string is patched
to say so.

**Armour** subtracts from every blow taken. Until 27 September it made you
take more.

**How hard.** The route is three tiers, and creatures are sized to theirs,
never to the hero (`server/tiers.py`, `BALANCE.md`). `/balance` on the web
server writes `server/balance.json`, which holds three dials:
- turns standing in one shape before you fall, 3 by default;
- turns one boss phase lasts with the tier's best weapon, 2 by default;
- pay, 100% by default.

Every crate holds an item (`tiers.CRATES`): a weapon step and a suit step on
the main path, a spare to switch to or recycle everywhere else. The first
crate gives a weapon a new hero can wear. Bows draw on Dexterity. Every tier sells
a sword, a heavy weapon and a bow of equal worth, and Beetles and Golems
wear shells, so each weapon has rooms where it is the right one. Mira's watAgame
twin (node 47) is sent as gone, since her phases happen on her own node.

**The side panel** is a flat reference to the chapter (`server/compendium.py`).
It no longer tries to follow the player, because under CheerpJ the map
loaded ping never arrives.

## Shirad's Forge — still open

**What byte 11 of a creature row is.** It no longer decides a creature's
life, which the tier does. It still decides how fast a creature swings and
what it pays. The code reads it both as hit points
and as the respawn countdown. The two readings have different evidence:
- Per species it is constant (Skeleton 18, Ghost 20, Gorrak 24, Beetle 30,
  Golem 36–50, Fungusman 50), which looks like life.
- It is 0 on 28 of 90 rows, exactly the unique fights and packs that never
  come back, which looks like a timer.

A row with 0 borrows its species' median.

**How hard a creature is.** Bytes 16–19 turned out to be a patrol box, so
no watAgame number for creature strength is left. The tier model in
`BALANCE.md` is ours.

**The experience curve.** 60 + 20 × level is ours. A full clear ends near
level 12 (`tools/balance_sim.py`). Level 49, the Arena's ceiling, is out of
reach in one chapter, and that is deliberate.

**Weight and prices.** Toughness now sets life and Speed shortens every
action (`tiers.py`, numbers ours). The rules' other two ability effects are
not in: heavy gear slowing a hero unless his Strength carries it, and
Willpower lowering prices and resisting spells.

**The fight bar.** It is always Move, Hit, Shoot, Dodge, Zap, Minor Cure. A
skill you buy is listed under Skills and cannot be used in a fight. Bombs,
traps and charms have no effect, and a charm has nowhere to be worn. The bar
has exactly six slots, so a bought skill would have to replace the starter
of the same kind. That replacement rule has not been chosen. Minor Cure
asks for Willpower 12 in the catalogue, but the bar does not check it.

**Skill titles.** The battle report's Promotion percentages are ours (5% a
landed use, a title every 100%, +1 effect and −5% time a title). See
`compendium.md`.

**What the trader stocked.** The Chapter I slice and its requirements are
chosen by `tools/pick_items.py` and `tools/tune_gear.py`, not recovered. Which
of the 305 catalogue entries this chapter really sold is not in the jar.

**A few screens that are still ours.** The icon overview in Help is guessed.
Kind 11, the one entity that asked the server to run a script, has no script.
The twenty-five checkpoints may have carried an extra sentence on top of the
jar's own line. Only the three gold sums were written down.

**Undecoded entities.** Nineteen: six of kind 7, four of kind 8, four of
kind 9, five of kind 10.

**The compendium.** The side panel reference exists, and
`tools/compendium_card.py` draws one creature's page as a prototype. The
player book in `compendium.md` is not written.

## The other games

**Sterling Lake and Mistral Grove** play on reconstructed doors and
reconstructed creatures. No jar of either contains the placement tables.
The same hero rules, blow sizing and Chapter I gear slice apply, since
nothing in that code asks which chapter is running. The shapes and the boss
phases are Shirad's Forge only, so there every creature threatens the full
ring. Their shops, gifts and
creature numbers are the same open questions, with less to anchor them.
Sterling Lake's island "just North of" the Harbour fits three candidates and
is left unwired.

**The Arena** (Dagonar, Orumant) is a different game. Its server is gone:
animation scripts, custom heads, clans, rankings, Respect, mail, duels. None
of its 64 CGI endpoints is implemented. **Ravarcil**, the third town, is in
no archive and was probably never released.

**Builds still out there**: Mistral Grove's 128×128 and 176×220 ports,
Dagonar 5.4.3, and the Sterling Lake "online" variants. The best lead is
`Find.7z` in the Internet Archive item `J2MEArchive`. See `ARENA.md` for how
to open it, and `recovered/README.md` for the two file names to look for.
