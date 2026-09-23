# Balancing: the plan, and where it stands

Read `DEVFLOW.md` first for the tools. This is the design we settled on and
how far it got.

## The shape of the problem

Shirad's Forge runs on watAgame's own tables, so **difficulty is given, not
invented**. Bytes 16-19 of each creature row climb with depth — the same
Beetle reads 12/6 in Dune Burrow and 32/33 in The Lair — and hit points are
per species (Skeleton 18, Ghost 20, Gorrak 24, Beetle 30, Golem 36-50,
Fungusman 50). Only the **player side** is missing: the experience curve,
gold, prices and what each shop stocks.

That halves the job. Do not invent difficulty. Solve progression to fit it.

## What the chapter actually is

- **62 creatures with hit points, and nothing respawns.** The nine kind 5
  "activate nodes" entities are all one-shot, and three of them are the
  Crypt's three-wave fight (nodes 108+109, then 110+111, then 112). So total
  experience and total gold are exactly computable, not estimated.
- **Ten fight groups**, of 13, 9, 9, 8, 6, 6, 4, 4, 2 and 1.
- **32 crates and barrels**, positions real, cut into the tilemaps.
- **Around ten to twelve levels** is the right range: a hero gains 2 ability
  points a level and each adds 3 while the score is under 48, so +6 of stat
  per level. Creature power runs from a sum of 18 to 118. The hero has to
  climb about 60 points of stat to keep up. Level 49 is the *Arena's* cap,
  not a chapter's.

## The design

**Crates hand out the critical path. Gold buys options.**

watAgame did this already: Mistral Grove's crates hold the sickle blade, the
sickle handle and the altar key — items you cannot finish without. So the gear
each gate demands is *found*, and no purchase can lock a player out. That
matters because **there is no selling in the chapters** — the Market buys
only, and opcode 24 deletes an item for nothing.

- **Main chain crates** guarantee the gate gear
- **Side room crates** hold upgrades, so the eleven optional rooms pay without
  ever being required
- **Gold buys tactical options** — skills and spells, not raw power. That is
  what makes "beatable with the right strategy" true rather than a slogan:
  the player buys the strategies.

Ability requirements are watAgame's own purchase gate and they still apply, so
a low-level hero physically cannot buy far above his tier.

## The bar, as a testable rule

> A gate fight should be **lost by `axe` and won by `careful`**, using only
> the gear obtainable by the time the route reaches it.

Bands: trash ≥85% on `axe`; gates 30-50% on `axe` but 70%+ on `careful`;
bosses under 20% on `axe`. Avoid tuning anything to a coin flip — 45% reads as
luck, not difficulty. And **no fight may be unwinnable** by every strategy.

## Done

- Creatures fight with their real numbers where they have them.
  `Mob.offence()` returns `fitted: False` for those and `fitted: True` for
  the fallback. Eleven Fungusmen have hit points and no curve data at all, so
  they are always fitted — do not make them the gate fights.

## Next

1. **Route order.** Derive it from the real doorway graph, then check it
   against their stat curve: if mean creature power per room agrees with
   distance from the Village, that is the intended route, inferred from their
   numbers rather than assumed.
2. **Crate loot** placed along that route.
3. **Experience curve** solved against the fixed 62-kill budget so the hero
   tracks the creature curve, reaching the boss with the margin above.
4. **Make the bar a check** in `fightplan.py`, so it is guaranteed rather than
   hoped for.

## A warning

Bytes 16-19 are a difficulty curve, certainly. What they *mean* is unsettled —
see `recovered/README.md`. I read them as abilities and Rules 1.5 contradicted
it. Use them as the curve they are; do not name them.

Sterling Lake and Mistral Grove have none of this data. Balance Shirad's Forge
first and tune the others to its curve.
