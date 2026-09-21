# The balance table, recovered

`items_exported.json` and `skills_exported.json` are MongoDB exports taken from
[lachtos/eoe-arena](https://github.com/lachtos/eoe-arena), a fan remake of
watAgame's *Era of Eidolon Arena*. Its author states the assets came from the
original game and that they do not own them; we keep these two files here for
the same reason we keep the jars.

**Why they matter.** Until now every number this server used — damage, Time
cost, price, ability requirement — was invented, because the official site
published item *names and descriptions* but never their statistics. These
exports carry statistics.

**How much to trust them.** The *text* is certainly watAgame's: 171 of the 202
matching descriptions are byte-identical to the ones we scraped off
eraofeidolon.com, and the 31 that differ are small wording variants — "made
and used in Ravacil" where our capture says "in Eidolon" — so the remake's
author worked from a different capture of the same official copy, most likely
the Arena's own pages rather than ours.

The *numbers* have no such proof. What can be established:

- No page in `notes/site/` carries a stat table, so they did not come from the
  capture we have.
- The MongoDB ObjectIds date the rows. All 107 skills were created within
  **8 seconds** of each other — one bulk insert. The 99 items were created over
  **47 hours**, which is a person entering and revising them one at a time.
- The repo adds both files in its initial commit with no note about where they
  came from, and its README says nothing beyond how to import them.
- Their ids are per-type sequences (id 2 is Short Bow), not the site's single
  numbering (item 2 is Longfang), so the site's ordering was not their source.

That pattern fits a player reading stats off the Arena's own shop screen and
typing them in — the Arena was a gladiator game built around buying equipment,
so its UI almost certainly showed damage, precision, speed, weight and ability
requirements. It fits an author inventing a tuning table by hand about equally
well. It does not fit a dump of watAgame's server, which would not take two
days to enter.

**Cross-checked, and the verdict changed.** All of the above was written
before testing the numbers against the two things we hold independently: the
official rules PDF and the official site's own listings. Four checks, none of
which they had to pass.

**1. The fields are the documented ones.** The PDF's SKILL CHARACTERISTICS
section names exactly *Ability requirements*, *Time (Ti)* and *Effect*, and
adds "Items have the same characteristics as skills". The export carries
`req`, `speed` and `value`.

**2. The spell categories match, on an unlabelled array index.** The PDF puts
Spectral and Bane under INTELLIGENCE BASED, Guardian and Spirit under
WILLPOWER BASED. In the export a requirement is a bare six-slot array —
`[0,0,0,24,0,0]`, nothing named. Against the site's own categories:

    bane      Intelligence 19/19        guardian  Willpower 19/19
    spectral  Intelligence 12/12        spirit    Willpower 12/12

Sixty-two spells, four categories, no exceptions. Gear agrees too: swords and
hammers on Strength, bows and bombs on Dexterity.

**3. The requirements rise with the site's own ordering.** Read each list in
document order — they restart at 1 per class, which is why sorting by the
printed number scrambles them into two interleaved series — and 165 of 171
steps rise. The six exceptions are single adjacent swaps.

**4. The steps are irregular.** Increments run 2, 3, 4, 6, 8, 9, 10, 12, 13,
15, 18, 20, 21, 24, 27, 33, mean 7.6. A number derived from an item's rank
would come out of a formula and step smoothly. This is what hand tuning looks
like.

To fabricate this you would have to invent a rising per-class curve matching
an ordering you had no reason to encode, and then place the
Intelligence/Willpower split correctly sixty-two times in an array slot with
no name on it. **These are watAgame's numbers.** There is still no provenance
statement anywhere, so it is not proof — but the reading that someone made
them up does not survive the evidence.

**Shape.**

    items   id type name value1 value2 weight req[6] desc
    skills  id type name value precision speed energy req[6] desc enabled

    item type   1 melee  2 bow  3 armour  4 charm  5 bomb  6 trap
    skill type  1 melee  2 missile  3 movement  4 defence
                5 teleport  6 protective magic  7 offensive magic  8 healing

`value1` on a weapon is a damage **percentage** (95-120), `value2` its
precision; on armour `value1` is flat damage reduction. Skills carry damage
(`value`), `precision`, and `speed`, which is the Time cost — the one number
the whole turn economy is built on.

`req` is six long and indexes abilities in the Arena's own order, not ours:

    1 Strength   2 Dexterity   3 Intelligence   4 Willpower

Index 0 and 5 are unused in every row.

**And a second caveat.** Even taken at face value, the Arena was a separate
product from the chapter RPGs — same world, same items, a different game around
them. These numbers would be the Arena's, not the chapters'.
