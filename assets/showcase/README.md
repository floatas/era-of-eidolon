# The art, outside the game

Everything here comes out of the jars unchanged: the sprites, the frame
timings, the ground, the interface. Nothing in this folder is reconstruction.
`python3 tools/showcase.py` rebuilds it.

    walk/    one GIF per creature, walking a circle on a bare 9x9 floor
    moves/   every animation a creature has, frame by frame, named and timed
    sheets/  the chapter's creatures, ground palette, obstacles, interface

## How a sprite is stored

A creature is not an image. It is three resources sharing an id:

    type 7    a PNG sheet of parts
    type 8    8 bytes per part: width, height, x and y in the sheet, offset
    type 11   the animation scripts, keyed by animation id

A script is a run of groups — `duration, part count, then that many
(dx, dy, part)` triples — so a single frame is half a dozen pieces stacked,
and duration is in sixteenths of a second. That is why the Arena filed its
art as torso.png and legs.png: these characters are assembled, not drawn.

## What the animation ids mean

The client names exactly one of them, in its exploration key handler
(d.java:1530-1570), which turns the four directions into four animations:

    LEFT   x-1   anim 14           RIGHT  x+1   anim 206 = 78 | 128
    UP     y-1   anim 142 = 14|128 DOWN   y+1   anim 78  = 14 + 64

So **14 is walk**, **+64 is the set facing away from the camera**, and **bit 7
mirrors** either one. Four facings out of one set of art.

The rest were read off the frames themselves, in `moves/`:

| id | meaning | id | meaning |
|----|---------|----|---------|
| 1  | stand | 12 | draw a bow |
| 2  | a burst of fire — see below | 14 | walk |
| 4  | swing | 15 | stand, one frame |
| 5  | stagger back | 17 | arrow |
| 6  | fall down dead | 18 | burning arrow |
| 7  | die, and a spirit rises | 19 | stone |
| 8  | cast | 20 | flame |
| 9  | thrust | 21 | fireball |
| 10, 11 | throw | 22 | explosion |
|    |  | 23 | green splash |

They mean the same thing for every creature, which is worth saying because a
comment in `world.py` used to claim the opposite.

**Animation 2 is the one I cannot settle.** The creature stands, a fireball
engulfs it, and then it is either standing again or gone, depending on which
creature. That is either arriving in a burst of fire or being destroyed by
one. Nothing in the jar says which, so it is labelled "fire burst" rather
than guessed at.

A creature has only some of these. The townsfolk sheet has no walk at all,
which is why they stand where they are put — and why asking for one a
creature lacks kills the client's animation thread with "Unable to get anim N
for monster id M".

## Armour is not drawn. Weapons are.

A natural question, and the answer differs between the two games.

**The chapters** give the hero exactly one appearance. `d.java` loads his
sheet from the hardcoded resource `/70` in three places and never branches on
anything (lines 161, 254, 1641). Armour changes damage reduction and a line in
your inventory; it does not change a pixel.

**The Arena** really does assemble its gladiator, but not out of armour. Its
compositor (`decompiled-arena/.../b.java`, the `a(Graphics, int[][], boolean)`
method) stacks four pieces:

    head     7 wide    per player, downloaded (pgethead.pl)
    torso   16 x 14    torso.png, 40 poses
    legs    12 wide    legs.png, 17 poses
    weapon  13 wide    weapons.png, 18 of them, drawn only in some poses

`arena/` has all four, cut on exactly that grid. Look at the torso sheet and
the point is obvious: every one of the forty cells wears the same grey plate.
The poses change — holding, drawing a bow, bleeding, casting, dying,
exploding — the armour never does.

So what another player could see of your kit was **the weapon in your hand**,
and what made you look like *you* was **your head**, which the client fetched
from the server per player. Those heads are gone with it.

`mail.png` is not chainmail. It is the icon for your messages, next to
`read.png`.
