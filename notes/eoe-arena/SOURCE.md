# The balance table, recovered

`items_exported.json` and `skills_exported.json` are MongoDB exports taken from
[lachtos/eoe-arena](https://github.com/lachtos/eoe-arena), a fan remake of
watAgame's *Era of Eidolon Arena*. Its author states the assets came from the
original game and that they do not own them; we keep these two files here for
the same reason we keep the jars.

**Why they matter.** Until now every number this server used — damage, Time
cost, price, ability requirement — was invented, because the official site
published item *names and descriptions* but never their statistics. These
exports carry the statistics. 202 of their 206 entries match a name already in
`notes/CATALOGUE.md`, which is what makes them believable: it is the same item
set, not a remake's own invention.

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

**Caveat worth keeping in mind.** The Arena was a separate product from the
chapter RPGs — same world, same items, a different game around them. These
numbers are the Arena's. They are vastly better grounded than the ones I made
up, and they are not certainly the chapters'.
