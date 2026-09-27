# Items in Chapter I

What Shirad's Forge actually offers, as the server computes it on 27
September 2026. The numbers come from `notes/chapter-items.json`, which
`server/catalogue.py` reads. Every other chapter reads it too.

A new hero has every ability at **3** and **no gold**. He starts with the
Bloody Blade, the Short Bow and the Scrapsuit. **Recycle** (the item
screen's old "Delete") breaks a piece and returns 30% of its price. That is
the only way to turn gear back into gold, since traders do not buy.

## The fight bar

Always Move, Hit, Shoot, Dodge, Zap, Minor Cure. These are not items in the
pack and are never sold or dropped. The bar does not check requirements, so
Minor Cure works at Willpower 3 even though the catalogue asks for 12.

| Button | Time | Effect | Notes |
|---|---:|---:|---|
| Move | 40 | 0 | one straight step |
| Hit | 60 | 10 | the weapon's own time replaces this when a melee weapon is held |
| Shoot | 60 | 9 | the bow's own time replaces this; adds a third of Dexterity |
| Dodge | 20 | 0 | lasts the turn |
| Zap | 60 | 9 | a ray, any square in sight, ignores armour; adds the whole of Intelligence, less the target's resistance |
| Minor Cure | 60 | 8 | heals effect + the whole of Willpower |

No other skill or spell has an effect in a fight, so the Skills and Spells
shelves are empty and crates never drop one.

## Gear

22 pieces, a slice of the Arena catalogue chosen by `tools/pick_items.py`,
with requirements respread from 3 to 34. `tools/tune_gear.py` then sets
every weapon's effect and price: in each tier the top sword, the top axe or
hammer and the top bow cost the same, and deal the same a turn at the
tier's reference ability, the heavy line and the bow 15% more on paper to
pay for their overkill. Cheaper pieces in a line reach 85% for 65% of the
price. **Req** is the chapter's requirement, **Arena** watAgame's.
Time and class are watAgame's. Suits keep watAgame's prices.

Effect on a weapon adds to every blow. A blow also adds a third of
Strength (Dexterity for a bow), scaled by the swing's time against 120, so
the ability adds the same over a turn to a sword and a hammer. Effect on a
suit comes off every blow taken. **A turn** is damage a turn at the tier's
reference ability (3 / 19 / 35).

| Name | Class | Tier | Req | Arena | Effect | Time | Price | A turn |
|---|---|---|---|---:|---:|---:|---:|---:|
| Bloody Blade | sword | I | 3 Str | 3 | -5 | 96 | 32g | 30 |
| Corrupter | sword | I | 3 Str | 21 | -2 | 96 | 240g | 45 |
| Spike Axe | axe | I | 3 Str | 18 | +14 | 195 | 240g | 52 |
| Giant Sword | sword | II | 13 Str | 36 | +9 | 120 | 460g | 100 |
| Razor Axe | axe | II | 17 Str | 27 | +28 | 202 | 299g | 98 |
| Smasher | hammer | II | 20 Str | 27 | +36 | 211 | 460g | 114 |
| Ghost Sword | sword | III | 24 Str | 44 | +23 | 126 | 760g | 180 |
| Bone Crusher | hammer | III | 27 Str | 39 | +57 | 221 | 494g | 176 |
| Beheader Axe | axe | III | 31 Str | 42 | +65 | 218 | 627g | 192 |
| Doom Hammer | hammer | III | 34 Str | 56 | +70 | 240 | 760g | 206 |
| Short Bow | bow | I | 3 Dex | 3 | +4 | 255 | 32g | 30 |
| Medium Bow | bow | I | 3 Dex | 18 | +15 | 262 | 240g | 52 |
| Long Bow | bow | II | 15 Dex | 27 | +27 | 269 | 299g | 98 |
| Heavy Bow | bow | II | 22 Dex | 39 | +35 | 283 | 460g | 114 |
| Bolt Bow | bow | III | 28 Dex | 42 | +54 | 290 | 494g | 176 |
| Doombow | bow | III | 34 Dex | 74 | +69 | 255 | 760g | 206 |
| Scrapsuit | — | I | 3 Str | 3 | +3 | — | 32g | — |
| Snail Shell | — | I | 9 Str | 12 | +4 | — | 100g | — |
| Iron Shell | — | II | 15 Str | 21 | +6 | — | 182g | — |
| Doom Suit | — | II | 22 Str | 30 | +8 | — | 292g | — |
| Trollskin | — | III | 28 Str | 36 | +10 | — | 356g | — |
| Spike Suit | — | III | 34 Str | 39 | +13 | — | 388g | — |

Held back for the sequels, and never stocked or dropped here: 19 melee,
6 bows, 11 armour. Bombs are not offered at all.

## Where it comes from

**Traders.** Five of them, in route order: Lava Island, Dwarven Hall, Fire
Cave, The Lair, The Core. Each sells its route tier: Lava Island tier I,
Dwarven Hall and Fire Cave tier II, The Lair and The Core tier III. Two shops
in the same tier split it, and the one further along gets the stronger half.
Each shop also keeps the top piece of the shop before it, so skipping Fire
Cave loses nothing for good (`handlers._trader_stock`):

    Lava Island    Bloody Blade, Corrupter, Spike Axe | Short, Medium Bow   | Scrapsuit, Snail Shell
    Dwarven Hall   Spike Axe, Giant Sword, Razor Axe   | Medium, Long Bow    | Snail Shell, Iron Shell
    Fire Cave      Razor Axe, Smasher                  | Long, Heavy Bow     | Iron Shell, Doom Suit
    The Lair       Smasher, Ghost Sword, Bone Crusher  | Heavy, Bolt Bow     | Doom Suit, Trollskin
    The Core       Bone Crusher, Beheader Axe, Doom Hammer | Bolt Bow, Doombow | Trollskin, Spike Suit

Away from a trader, the shelf is what he can wear plus the next three above
his stat, and a piece leaves once his stat is 12 above its requirement.

**Crates.** Every crate holds an item, planned with each tier's traders (`tiers.CRATES`):

    tier I    Village 69 weapon step · Lava Island 240 suit step · 1 spare
    tier II   Dwarven Hall 160 weapon step · Mira's Hideout 166 suit step · 12 spares
    tier III  The Lair 172 weapon step · The Core 174 suit step · 9 spares

A step is the cheapest piece better than what the hero wears, from the line
of the weapon in his hand or in suits, from the crate's tier or earlier. A
spare is any other piece from the crate's tier or below that he does not
carry, one he has not found in a crate before while there is one: to switch
to, or to recycle. Never the free kit, and past tier I never the dearest
piece of its line in the crate's own tier, which stays the trader's. A step
he has already bought becomes a spare. Only with nothing left does a crate
pay a purse. Tier I's first step in each line asks for 3, so the Village
crate gives a new hero a weapon he can wear at once. Three crates that
opened onto nothing (one on Lava Island, two in the Crypt) now hold items
like the rest.

**Charms.** The catalogue still holds 17 of them. None has a slot or
any effect, and none is offered.
