# The lost tables, found

`ShiradsForge-type1.bin` and `ShiradsForge-type9.bin` are the two resources
this whole project has been reconstructing: what stood where, and who stood
where. They are watAgame's, not ours.

They came out of `jars/EoE-ShiradsForge-v1.0.0-176x208.jar`.

## Why they exist at all

Every other build fetches these from the server — that is the entire reason
the chapters needed one, and the reason losing it hurt. But version 1.0.0 for
176x208 screens ships them **in the jar**, as resources `10` (type 1 id 0) and
`90` (type 9 id 0). An early build, before the tables moved server-side.

Nothing marked it out. It is 155 KB against the 64 KB of the other 1.0.0
build, and the only way to find it was to list the resources of all fifteen
jars and notice two names nothing else had.

## What is in them

    type 1   235 entities across all 18 locations, 6152 bytes
             kinds: 80 messages, 44 exits, 42 tilemap patches, 25 usables,
             11 auto-fires, 9 node activations, 6, 5, 4, 4, 4, 1 of the rest
    type 9   111 creature nodes, 2164 bytes, 2 to 16 per location

The exits are paired both ways with exact arrival coordinates:

    loc 1 box (8,0)-(9,1)     -> loc 2 at (26,48)
    loc 2 box (26,49)-(28,50) -> loc 1 at (8,1)

## That they are genuine, and that they fit the build we play

- 235 of 235 entity boxes lie inside their own location's map
- 44 of 44 exit arrivals lie inside the destination's map
- every creature id is a sheet this jar carries; every location id is real
- 111 of 111 creature positions are on their map

And the tilemaps of 1.0.0-176x208 are the same size, map for map, as the
1.1.0 build we actually play. Same world, smaller screen. So these tables
apply directly.

## What this replaces

Everything in `FLOW.md` about deriving the route from dialogue, every
invented doorway, the hub-and-spokes graph, the scattered creatures — all of
that was reconstruction for Shirad's Forge and can now be checked against the
real thing. Sterling Lake and Mistral Grove still have no such build, so for
them the reconstruction stands.

## Why this build and not the others

It is not chronology. Shirad's Forge 1.0.0 exists in two packagings with the
same version, both dated 29 April 2005, and only one carries the tables:

    EoE-ShiradsForge-v1.0.0-midp1.jar     63 KB    4 resources   no tables
    EoE-ShiradsForge-v1.0.0-176x208.jar  155 KB   76 resources   TABLES

Sorting every jar we hold by what it carries gives three kinds of build:

**Thin — 4 resources.** One tilemap-less shell that downloads the entire world
as it plays. Every MIDP-1.0 chapter build we have is one of these: Shirad's
Forge, Sterling Lake and Mistral Grove alike.

**Data-local — 66 to 77 resources, no type 1 or 9.** Tilemaps, text, sprites
and animation all in the jar; only *what stands where* comes from the server.
This is what the MIDP-2.0 builds are, and what we play.

**Fully offline — 76 resources including type 1 and 9.** Exactly one jar in
fifteen.

So the split is per handset, not per release. A guess at why, and it is only a
guess: the site published what the game cost to play, a tenth of a megabyte an
hour billed by the operator, from 0,14 Euro in Denmark to 0,60 in Italy. A
build that needs no connection costs nothing to run, and 176x208 was the
S60 screen of the phones sold where that mattered most.

## What to look for, if anyone ever looks again

A chapter jar that is both data-local **and** contains resources named `10`
and `90`. That is the whole signature — two file names nothing else has.

Sterling Lake and Mistral Grove have no such build among the fifteen we hold,
and the candidates are gone: Mistral Grove's Motorola 128x128 and 176x220
adaptations survive only as descriptors on mox.su, whose jars are dead on the
live web and absent from the Wayback Machine's copy of that site.

## The type 9 row, decoded

Most of it the client reads, so the meaning is not a guess:

    [0]     node id
    [1]     location
    [2]     group id          d.java:848 — a type 1 entity with trigger 3
                              fires when a member of group N dies, which is
                              how "clear the room" objectives work. Shirad's
                              Forge has 10 groups, of 13, 9, 9, 8, 6, 6, 4,
                              4, 2 and 1 creatures.
    [3][4]  x, y
    [5:7]   u16 text key      what it says when it notices you
    [7:9]   u16 text key      its action label, "Fight Beetle"
    [9]     notice radius     d.java:622. Step within this many tiles, with
                              line of sight, and its text fires and the
                              encounter starts. 0 means it never speaks
                              first. This is why Hrom shouts for help the
                              moment you leave the Village.
    [10]    reach radius      same loop: within this many tiles it joins the
                              "Choose action" list, so you can fight or talk
                              to it. 0 means never.
    [11]    hit points        Skeleton 18, Ghost 20, Gorrak 24, Beetle 30,
                              Golem 36-50, Fungusman 50. Per species.
    [12]    sprite sheet
    [13]    animation
    [15]    moves             starts the walk animation on load
    [16..19]                  only in the 20-byte rows, and the client never
                              reads them at all

## The four the client never reads

They were the server's, which is why they survive only here. They are per
creature rather than per species, and they climb with depth: a Beetle in Dune
Burrow is 0, 0, 12, 6 and a Beetle in The Lair is 26, 27, 32, 33. That is a
difficulty curve, written down.

The hero has a row too — 17, 13, 21, 17.

Four numbers, and exactly four abilities matter for combat once hit points are
already given at [11]: Strength, Dexterity, Intelligence and Willpower, which
are also the only four any item asks for. Reading them as
**Intelligence, Willpower, Strength, Dexterity** is the order that makes sense
of the values: beasts come out with no magic at all (the Dune Burrow beetle is
Int 0, Wil 0, Str 12, Dex 6), the fire devil has some (Int 8, Wil 0, Str 16,
Dex 10), and the hero reads as a balanced starter leaning slightly to
Strength. Every other ordering gives beetles intelligence and no strength.

That last part is inference. The client cannot settle it, because it never
looks at these bytes.
