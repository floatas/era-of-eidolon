# What is in here

Images the blog post uses, and how they were made. Everything regenerates
from the jars — nothing here was drawn by hand.

Each heavy picture has a `-web` twin, quantised to a 256-colour palette.
Pixel art loses nothing to that and the files are a third of the size, so
**use the `-web` ones on a page** and keep the originals for printing.

## For the post

| file | what it is | made by |
|---|---|---|
| `splashes.png` | the three chapter title screens, dated | pulled straight from the jars |
| `bestiary.png` | all 29 creatures, by chapter | `tools/compendium_card.py` portraits, tiled |
| `turn-timeline.svg` | one 720 turn, five lanes, including thinking | `tools/fight_timeline.py` |
| `ui/chrome.png` | the fight bar and the walking bar, blown up | `fpanel.png` etc. from the jar |
| `ui/items.png` | the 28 item icons | `items.png` from the jar |
| `ShiradsForge-rooms.png` | its 18 rooms, each on its own | `tools/rooms.py` |
| `SterlingLake-rooms.png` | its 17 rooms | `tools/rooms.py` |
| `MistralGrove-rooms.png` | its 18 rooms | `tools/rooms.py` |
| `arena/orumant-screens.png` | logo, town, arena, challenge, mail | from the jar |
| `arena/dagonar-screens.png` | the same, a year later | from the jar |
| `arena/Orumant/torso.png` | the paper-doll torso sheet, cut on its grid | `showcase.arena_sheets` |
| `cards/blackjack.png` | Badaz Blackjack | from the jar |
| `cards/poker.png` | Badaz Poker | from the jar |

## The map

`ShiradsForge-world.png` — the chapter laid out flat, on its real
coordinates. Fourteen shared borders, which fall into four islands: thirteen
rooms locked together, The Forge with Golem Secret, Fire Cave with Ilrik's
Tomb, and Aldor's Outpost on its own. The islands reach each other through
doors in the middle of a map rather than on an edge — portals — and a portal
says nothing about where the next room lies.

Inside an island nothing is nudged: every room is on the coordinates its own
doorways force. Between islands there is nothing to be faithful to, so they
are shelved into rows to keep the sheet from running off the side. Each one
moves as a single rigid piece (`worldmap.shelve`), and the renderer asserts
the seam set is unchanged afterwards.

## The creature cards

`compendium/<chapter>/<creature>/index.html` — 29 of them. Each has a
portrait, a loop of the creature walking a circle so you see every side, the
shape of squares it threatens, and a line on how to fight it. Open the
`index.html`; the walk only animates in a browser.

Portraits and map sprites both use the walk frame facing down and to the
right, so you get the face and a little of the profile rather than the back
of a head.

## Regenerating

    python3 tools/rooms.py MistralGrove
    python3 tools/worldmap.py ShiradsForge
    python3 tools/fight_timeline.py
    python3 tools/compendium_card.py Golem ShiradsForge
