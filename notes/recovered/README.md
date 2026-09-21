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
