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

So: better grounded than the numbers I made up, and not established fact. The
shape of them argues for transcription — requirements land on multiples of 3
(3, 12, 15, 21, 27, 36, 42, 48), weapon damage on 95/100/105/120 — but that is
an impression, not evidence.

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
