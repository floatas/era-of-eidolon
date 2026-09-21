# What is still missing

An honest inventory, written after the archive stopped growing.

## Have

Seven titles in fifteen jars: the chapters **Shirad's Forge**, **Sterling
Lake** and **Mistral Grove** (all three play), the Arena towns **Dagonar** and
**Orumant**, and the spin-offs **Badaz Blackjack** and **Badaz Poker**.

All thirteen pages of the official site, including `costs`, `faq` and
`gamerules`, which 503'd on the first attempt. Both versions of the rules PDF.
The 305-entry catalogue. The gen-2 wire protocol, fully documented and
reimplemented across all 28 opcodes. The gen-1 Arena's 64 endpoint names.
Every tilemap, sprite sheet, animation script, text table and quest in every
chapter.

## Missing, and not coming back

**The type 1 tables — what stood where.** Placed entities for all three
chapters: which entity triggers which quest step, where each doorway leads,
and the transitions that were never painted on the map. Partly reconstructed:
each chapter's main chain is recovered from its own dialogue (see FLOW.md),
seven or eight locations of the eighteen. Where the remaining side chambers
hang off that chain is not recoverable from anything in the jars.

**The type 9 tables — who stood where.** Creature placement: which creature on
which tile, with what hit points, in what group. Every monster this server
puts on a map is our invention.

**The Arena server, entirely.** Sixty-four endpoints of it. The parts that
hurt most are not the ladder but the assets it served:

- `panimscripts` — the Arena downloaded its animation scripts, so we have
  torso, legs and weapon art with nothing to drive it
- `pgethead`, `headlist`, `customupload` — every player's custom head, the
  one piece of visual identity the game had
- clans, rankings, Respect, mail, the Blood Duel results

**Ravarcil.** Announced as the third regional town — Blissmor/Sorena/Orumant,
Vulcor/Furyana/Dagonar, Mystor/Arsenica/Ravarcil — and present in no archive
under either spelling, across nine independent source sites and a 120 GB
hoard that holds everything else in the series several times over. The
likeliest reading is that it was never released.

**Item statistics for the chapters.** The site published names and
descriptions and never numbers. What we use comes from a remake of the Arena
and its provenance is unproven — see `eoe-arena/SOURCE.md`.

**The balance curve.** Experience thresholds, shop prices, monster hit points,
how a level-1 hero is meant to fare against the first thing it meets. All
ours.

## Not missing, but worth writing down

The site published what the game cost to play, which is why the protocol is
as tight as it is:

> Average consumption is less than 0,1 Mb per hour
>
> Denmark CBB 0,14 Euro/hour · UK Orange 0,2 · USA Verizon 0,35 ·
> Germany Vodafone 0,4 · Sweden Telia 0,50 · Italy Vodafone 0,6

A hundred kilobytes an hour for a live multiplayer RPG. Every design decision
in `protocol/PROTOCOL.md` — two-byte resource keys, a shared text table, the
whole world shipped in the jar and only the placements sent — follows from
that line.
