# Shirad's Forge compendium

The player book is `tools/compendium_book.py`. It writes one page,
`assets/compendium/book/index.html` with its pictures in `img/`, from the
server's own numbers, in the order a player needs it:

1. Your hero: start, levels, raise points, what each ability does
2. The fight: the turn clock, the fight bar, hitting, shapes, practice
3. Three kinds of weapon, how an ability scales with swing time, footwork
4. Items and shops: reading a market line, the colours, Recycle, crates
5. The route, tier by tier and room by room, with each creature's card
   where it is first met and each boss where it stands

It is published as a private artifact to keep open on a phone while playing:
https://claude.ai/artifact/JDWufrjvErRDTHZEF9TGgg. Rerun the tool after a
balance change and republish.

`tools/compendium_card.py <creature>` was the first prototype, one creature
at a time (Beholder, Fungusman, Golem and Skeleton, in `assets/compendium/`).
Its numbers predate the tier model.

What follows is the item behaviour worth keeping, and where the other parts
already live.

## Items the phone shows

A Market line is the name, then E, then Ti, then the price. Opening the line
shows the old catalogue story, which has no numbers.

E on a weapon is its damage as a distance from a normal weapon. The Arena
stored that as a percent, and 100 means no change. The line prints the percent
with 100 taken off:

- Bloody Blade is 95, so the line says E-5. A hit loses 5.
- Spike Axe is 115, so the line says E15. A hit gains 15.
- Longfang is 100, so E is left off. A zero is not printed, and a plus is not
  printed either. That is why one line has a dash and the next does not.

E on armour is different. It is how many points of a blow the suit stops.
Scrapsuit is E3.

Ti is how much of the 720-point turn a swing takes. Armour has no Ti.

The Strength or Dexterity a piece asks for is not on the line. It appears only
if the buy is refused: "You need Strength 21."

## What this chapter actually uses

The fight bar is Move, Hit, Shoot, Dodge, Zap, and Minor Cure. Zap is the only
damage spell. It is a ray: any square in sight, including the next square, and
armour does not stop it. Minor Cure heals and needs no target.

Charms have no slot and no fight effect. Bombs, traps, and every other spell
or skill do nothing here. The shop, the crates, and the Skills and Spells
screens do not offer them. Every crate holds an item: a weapon or suit
step in the hero's own line on the main path, a spare from that tier or
below everywhere else. See `usable-items.md`.

Away from a trader, melee and armour follow Strength and bows follow
Dexterity. A shelf shows what he can wear, then the next three pieces above
that stat. A piece leaves once his stat is more than 12 above what it asks
for.

The five traders do not share that shelf. Each sells its own tier of the
route: Lava Island tier I, Dwarven Hall and Fire Cave tier II, The Lair and
The Core tier III. Two shops in a tier split it, weaker half first, and each
shop keeps the top piece of the one before. So every shop sells something
new, and Fire Cave (the side door in the Hall) is worth the detour without
being required. The full list is in `usable-items.md`.

A shelf row is coloured against what the hero wears in that role. Grey
means the stat is out of reach. Red means it is worse. Green means it is
better and the purse can pay. A weapon is compared by the damage it deals
in a turn, not by its effect, because a fast sword can out-deal a slow axe.

The catalogue itself is the Arena's, split by town. Orumant is Blissmor.
Dagonar is Vulcor, this chapter's region. Ravarcil was never written. The
shelf above is ours: usable gear, ordered by the stat it asks for. Only the
Chapter I slice is stocked (`chapter-items.json`).

## Battle report

The original post-fight screen, from the Shirard's Forge page screenshot, is not
the one we send. Ours names who fell and the gold and experience. Theirs was:

```
Battle report
You gain:
  * 8%
  * 1
Weapon points:
  10% Bow usage
Skill points:
  5% Hit skill
  15% Dodge skill
  20% Move skill
  10% Shoot skill
Spell points:
  No gains
```

Each skill, spell, and weapon keeps its own percent. The rules call that
Promotion: how close that one skill is to its next title. The titles run
Fumbler, Beginner, Trained, Experienced, Master, Expert, Sensei. A higher
title makes that skill hit harder and take less of the turn.

This fight raised only what was used, and not by the same amount. Move moved
the most, Hit the least, and the spells, which were not cast, say "No gains".
So practice of a skill is what fills its bar. The rules do not say whether a
hit counts for more than a miss. The different sizes on this one screen are
the evidence we have.

Both rules PDFs (0.2 and 0.9) stop there. Promotion% is "how close your hero
is to the next title." A higher title makes the skill stronger and faster.
They never say how many points a use is worth, or what a title adds to Effect
and Time. The words "Skill points", "Weapon points", "Bow usage" and "No
gains" are not in any jar or decompiled client. The phone only displays the
string the server sends as tag 24 under the title "Battle report".

Hero info, Skills and Spells ask the server for a list. We answer with the
name and the catalogue story. There is no title and no percent on that
screen, and the six bar actions are not even listed, because they are not
items in the pack. The hero sheet shows level, experience, gold and the six
abilities, and any skill that has already been practised.

What we do with that, since the original server is gone: a landed use adds
5% to that skill. A miss, a fizzle, a resisted spell, or a step that fails
adds nothing. The points are kept when the fight is won and dropped when it
is lost. At 100% the title advances and the percent starts over. Each title
adds 1 to the skill's effect and takes 5% off its time. The win report lists
the gains. Hero info, Skills and Spells shows the title and the percent.

## Still to write

Enemies, the map, and the quests are not copied here yet.

- Creatures and where they stand: `notes/ShiradsForge-world.txt`
- The joined map: `assets/ShiradsForge-world.png`
- The quest chain and where it walks: `notes/FLOW.md`
- The full Arena lists, including what this chapter hides: `notes/CATALOGUE.md`
  and `notes/usable-items.md`
