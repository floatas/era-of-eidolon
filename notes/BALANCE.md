# Balancing: the plan, and where it stands

Read `DEVFLOW.md` first for the tools. This is the design we settled on and
how far it got. Rewritten on 27 September 2026, after the premise changed.

## The premise changed

The first version of this plan said difficulty was given and only the player
side was missing, because bytes 16–19 of each creature row seemed to climb
with depth. They do not encode difficulty. They are a patrol box, x0, y0,
x1, y1, and the climb was map size. See `RECONSTRUCTION.md`.

So **difficulty is ours after all.** The only per-creature number watAgame
left is byte 11, and that may be a respawn timer rather than life (see
`MISSING.md`).

## What the chapter is

- **Around 62 creatures carry a byte 11 value.** The nine kind 5 activations
  are one-shot, and three of them are the Crypt's three waves. Total
  experience and gold are computable, not estimated.
- **Ten fight groups**, of 13, 9, 9, 8, 6, 6, 4, 4, 2 and 1.
- **32 crates and barrels**, positions real, cut into the tilemaps.
- **The route**, from `tools/route.py`: every main-chain door starts open,
  and what is gated is the objective chain. In hops from the Village:

      0 Village   1 Lava Island   2 Dwarven Hall   3 Mira's Hideout
      4 The Lair  4 The Core      5 The Forge

  The Lair and The Core are siblings off the Hideout. Six exits start
  dormant, all of them side doors or shortcuts. The chain is Hrom, then
  cogwheel 1, then cogwheel 2, then Mira, then cogwheel 3, then Shirard.

## The principle

**The tier is the difficulty. Gear decides how long a fight lasts. Footwork
decides whether you get hit.**

The route is three tiers, each with its own traders: Lava Island (I), Dwarven
Hall and Fire Cave (II), The Lair and The Core (III). Creatures are sized to
their tier, never to the hero playing (`server/tiers.py`):

- **Life.** A Beetle-weight creature takes one turn to kill with the tier's
  best weapon. The weapon the tier opens with, the last tier's best, is
  slower, so skipping an upgrade costs a turn or two an encounter, not the
  fight. Weight counts at the ¾ power, so a Fungusman is about one and a
  half Beetles.
- **Blow.** One turn standing in one creature's shape costs a third of the
  life the tier expects you to carry in, after the tier's suit. Narrow shapes
  hit up to 1.2× harder, the full ring 0.9×. Levels, life and a better suit
  let you survive more mistakes. Out of every shape you take nothing, so a
  careful player can always win.
- **Pay.** Experience and gold follow the species' weight and the tier, not
  the life it was given. Otherwise the hero outgrows the next tier. A boss
  pays like weight 60. A level costs 60 + 20 × level.
- **Bosses.** Mira, Aldor, the Beholder and Shirard each fight two phases.
  A phase is `boss_turns` turns of the tier's best weapon, and the second
  phase turns the safe squares around (`handlers.BOSS_SHAPES`):

      Mira      ray (a line 2-5 ahead): close in      then front + sides: get behind
      Shirard   burst (the ring 2 out): step beside   then front + sides
      Aldor     front and one shoulder                then front + sides
      Beholder  its four diagonals: stand square on   then a gaze down four lines: diagonals only

  A boss keeps its shapes even against a bow. Mira's watAgame twin (node 47)
  is sent as gone, because her phases happen on her own node.
- **Crates and traders are one plan per tier.** Every crate holds an item, planned with each tier's traders (`tiers.CRATES`):
  
      tier I    Village 69 weapon step · Lava Island 240 suit step · 1 spare
      tier II   Dwarven Hall 160 weapon step · Mira's Hideout 166 suit step · 12 spares
      tier III  The Lair 172 weapon step · The Core 174 suit step · 9 spares
  
  A step is the cheapest piece better than what the hero wears, from the line
  of the weapon in his hand or in suits, from the crate's tier or earlier. A
  spare is any other piece from the crate's tier or below that he does not
  carry, one he has not found in a crate before while there is one: to switch
  to, or to recycle. Never the free kit, and past tier I never the dearest
  piece of its line in the crate's own tier, which stays the trader's. A step
  he has already bought becomes a spare. Only with nothing left does a crate
  pay a purse. Tier I's first step in each line asks for 3, so the Village
  crate gives a new hero a weapon he can wear at once. Three crates that
  opened onto nothing (one on Lava Island, two in the Crypt) now hold items
  like the rest.
- **Gold** is sized so each tier's kills, crates and recycling buy its top
  weapon and top suit with a quarter to three quarters to spare. Past tier I
  most of it is what the crates hold, broken down: creatures pay
  `tiers.GOLD_RATE` 1.0 / 0.3 / 0.1 per point of weight, and **Recycle
  returns 30%** (`tiers.RECYCLE_PERCENT`, written into the phone's text by
  `run/mkjar.py`). At 70% every crate and every outgrown weapon earned three
  times what a tier's gear costs. The simulator recycles whatever a build
  does not use and checks the ledger: 1.2–1.8× in every tier for every build.
  The three optional quests pay on top (Dreyfus 250 and Tillic 150 in tier
  II, Milas 400 in tier III; `layout.QUEST_GIFTS`), taking a hero who does
  them to about 2× a tier's top gear: optional content makes you richer.
- **Three lines of weapon, each with a job.** Every tier sells a sword, an
  axe or hammer, and a bow at each price, and their top pieces cost the
  same (`tools/tune_gear.py`). On paper the heavy line and the bow deal 15%
  more a turn than the sword, to pay for the half blow they waste on each
  kill; in play the three come out level. An ability adds the same over a
  turn whatever the weapon's speed: a blow gets a third of it, scaled by
  its swing time against 120 (`tiers.potency_bonus`). So what separates
  the lines is the job, not the damage:

      sword   quickest on soft packs (Skeletons, Gorraks, the Crypt). A short
              swing fits between a creature's blows, so footwork keeps it
              clean. Armour bites every one of its small blows.
      heavy   quickest on shells and big single creatures (Golems, Beetles,
              Fungusmen). A long swing gets hit by light, fast creatures.
      bow     level with heavy against shells, and safer: the first shot at
              each creature is free while it walks in. Needs a clear line, no
              shot adjacent, and wears light suits because suits need Strength.

- **Shells.** Beetles and Golems wear armour worth 30% and 50% of the tier's
  sword blow (`tiers.SHELL`), and give up life to match, so an average of
  sword and hammer clears them as fast as a soft creature.
- **Toughness and Speed do something.** Toughness is life: every point
  above 3 adds `tiers.TOUGH_LIFE` (5) on top of 40 + 6 a level. Speed is
  tempo: every action takes 120 / (117 + Speed) of its time
  (`tiers.speed_scaled`, through `World.trained_time`, which the fight bar
  sends the phone). `balance_sim.py --variants` gives each weapon line its
  third raise point in Dexterity (Strength for the bow), Toughness or Speed:
  Toughness ends at 217 life against 112 and survives 25–40% more mistakes
  for 8–16% slower fights; Speed is 4–10% quicker and survives fewer. All
  targets met. At +2 a point Toughness bought less safety than the Dexterity
  it gave up, since half of Dexterity is dodging.
- **Dodge and Minor Cure have a price.** Both could be queued as often as
  the clock allowed. Five Dodges (100 of the turn) cut a creature's hit
  chance from 69% to 19%; two or three Minor Cures undid a whole turn
  standing in a shape. Now each further Dodge in a turn adds half the last
  (+10, +5, +2, +1), and Minor Cure takes 150 (`Catalogue.CHAPTER_TIMES`),
  so it is the emergency button unless the hero raises Willpower for it.
  The simulator plays neither, so the targets above are unaffected.
- **A creature's avoidance and spell resistance** follow its species'
  weight, not its tier-sized life. Reading life made tier III creatures
  dodge 40% of blows and ignore Zap. Zap ignores armour, so a hero with some
  Intelligence has an answer to shells whatever he carries.

The reference hero per tier (`tiers.REFERENCE`): level 0 / 4 / 8, life
40 / 64 / 88, main ability 3 / 19 / 35, suit Scrapsuit / Snail Shell / Iron
Shell. The three `/balance` dials are turns in a shape to fall (3), turns
a boss phase lasts (2), and pay (100%).

## Measured, 27 September 2026

`python3 tools/balance_sim.py` runs all three builds and compares them room
by room; `--build sword|heavy|bow` shows one build in full against every
target. All comparison targets are met:

- No build is ever more than 1.4× slower than the quickest in any room.
- The sword is quickest in 13 rooms, heavy in 8, the bow in 5, counting
  ties within 5%. Heavy and bow win The Core, Fire Cave, Cave of Doom and
  Dune Burrow. The sword wins the Skeleton and Gorrak rooms and the Crypt.
- All three end at level 12, main ability 50, with a weapon and suit
  bought each tier and 1,100–1,600 gold spare. Bosses take 2.8–3.9 turns.
- A mistake costs 32–45% of the reference hero's life.

Left, all small: first arrival at Lava Island and Dwarven Hall is short
of the cheapest upgrade (the simulator buys after clearing the room, so it
only bites if the player never goes back). Aldor falls in 2.8 turns to a
sword, just under 3. Ilrik's Tomb's lone Skeletons die in 0.8 turns.

## Next

1. **Play it.** The simulator's footwork is an approximation: a blow counts
   as safe when stepping in, swinging and stepping out fits between two of
   the creature's swings. A real run through each boss and a Skeleton pack
   with each weapon is the check that the shapes and the timing read as
   intended.
2. **The Giant Sword swings in 120**, too slow to fit between a Skeleton's
   blows (180 apart, less the 80 of stepping in and out), so a swordsman
   loses his footwork edge in tier II, the Skeleton tier. Shortening it to
   about 100 would keep the sword the Skeleton weapon.
3. **Gold on first arrival** at a shop, if play shows players do not go back.
4. `regress.py` boots all three chapters. Its doorway walk fails because its
   `goto` steers in a straight line and the Village has a wall at (8,12)
   between the start and the north door. That's the harness, not the game.

## The bar we meant to hold

> A gate fight should be **lost by `axe` and won by `careful`**, using only
> the gear obtainable by the time the route reaches it.

With creatures sized to the tier, `axe` (toe to toe) loses about a third of
life a creature-turn in a shape, and `careful` loses nothing. The duel and
brawl columns in `balance_sim.py` show what `axe` costs each encounter.

## Sterling Lake and Mistral Grove

Neither has tiers, creature rows or boss phases. They keep the older fight:
every creature threatens the full ring and its blow is sized to the hero's
life. They share the Chapter I gear slice and the bow's Dexterity. Balance
Shirad's Forge first and carry its rules across.
