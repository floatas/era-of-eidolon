# The route, recovered from the dialogue

Which doorway leads where was in the type 1 tables, and those are gone. But
watAgame's writers put the route in the script, and the script ships in the
jar. Shirad's Forge tells you the whole main chain, with compass directions,
in its own location text (type 3):

| where | key | what it says |
|-------|-----|--------------|
| Village | `0x1971` | "He is near the small lava streams **North of here**." — Hrom, who then speaks in Lava Island |
| Village | `0x1974` | "Shirard has placed the 1st one on a **small island**" |
| Lava Island | `0x1976` | "Maybe it's in the **Dwarven Hall North of here**" |
| Dwarven Hall | `0x1977` | "perhaps **Mira** can help you. She is the rogue that hides in the cave **North of here**" |
| Mira's Hideout | `0x197a` | "the 3rd cogwheel is hidden in a cave called **the Lair East of here**" |
| The Lair | `0x1989` | "place them in Shirard's statue, which is in **the Forge** somewhere to the **North**. Beware of his minions when you go through **the Core**!" |

Which gives the route as watAgame wrote it:

    Village -> Lava Island -> Dwarven Hall -> Mira's Hideout -> The Lair
            -> The Core -> The Forge

Seven of the eighteen locations, in order. It also explains The Forge having
no painted doorway at all: it is the last room, behind the Core, reached when
the lava stream is restored.

The other eleven — Old Shrine, The Long Run, Cave of Doom, Aldor's Outpost,
Fire Cave, The Evil Eye, Ilrik's Tomb, Dune Burrow, Crypt, Lava Pit, Golem
Secret — are named in no dialogue at all, and each has exactly one painted
doorway. They are side chambers, and where they hang off the chain is not
recoverable from anything in the jar.

## Mistral Grove says as much, and settles the rule

    Outskirts      0x1be5  "seek out the druid, Horus ... He hangs out near
                            the small pond that is called Mirror Pool"
    Mirror Pool    0x1bfa  "You need a special sickle to cut through the hedge.
                            ... the first part is in the area called Spiderwood"
    Spiderwood     0x1c00  "the sharp, curved blade of a sickle"
    Hollow Hill    0x1c02  "a short wooden rod that looks like the handle"
    The Hedge      0x1bf3  "your way is blocked by some a magical hedge!"
    The Hedge      0x1bfb  "release the boy from the altar at Mistral Grove"
    Mistral Grove  0x1c1e  "She is probably hiding in the Deadwood North of here"

    Outskirts -> Mirror Pool -> Spiderwood -> Hollow Hill -> The Hedge
              -> Mistral Grove -> Deadwood

Now put the two routes next to their location ids:

    Village 1, Lava Island 2, Dwarven Hall 3, Mira's Hideout 4,
    The Lair 5, The Core 6, The Forge 7
    Outskirts 40, Mirror Pool 41, Spiderwood 42, Hollow Hill 43,
    The Hedge 44, Reaperwood 45, Mistral Grove 46, Deadwood 47

**watAgame numbered their locations in the order you walk them.** Two
chapters, two independent scripts, and in both the dialogue order is the id
order exactly. The chain is therefore the run of consecutive ids up to the
last place the script names; everything after it is a side chamber, never
mentioned, with a single doorway each.

Reaperwood is the case that proves it. Nothing in the game says a word about
it, but it sits at 45 between The Hedge and Mistral Grove, and chaining by id
puts it exactly where it belongs.

## Sterling Lake says less

    Harbour     0x1a26  "one can be found on the small island just North of here"
    Sea Kelp    0x1a34  the Fishking asks you to find the Holy Icon
    Pirate Den  0x1a58  "return it to the Fishking who is waiting at the Holy Site"
    The Deep    0x1a??  "a water beast has risen from the deep and is ruining the pier"

Enough to order the story — Fishking, then Black Eye at the Pirate Den, then
back to the Holy Site — but not to name which island is north of the Harbour.
Three candidates fit. Left unwired rather than guessed.
