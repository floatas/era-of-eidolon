#!/usr/bin/env python3
"""The Shirad's Forge compendium: every creature and boss, and each tier's
traders and gear crates, on one page to keep open on a phone while playing.

    python3 tools/compendium_book.py

Writes assets/compendium/book/index.html and its pictures in img/. Every
number is read from the server as it stands (world, handlers, tiers), so
run it again after a balance change and the book follows.
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "server"))
sys.path.insert(0, HERE)

import handlers          # noqa: E402
import tiers             # noqa: E402
from catalogue import catalogue   # noqa: E402
from world import World  # noqa: E402
import showcase          # noqa: E402
from compendium_card import portrait   # noqa: E402

OUT = os.path.join(ROOT, "assets", "compendium", "book")
IMG = os.path.join(OUT, "img")
TURN = handlers.TURN_BUDGET
STEP_OUT = 2 * handlers.MOVE_COST       # stepping in and back out again
REF_HIT_CHANCE = tiers.REFERENCE_PRECISION - 1

BOSS_NODES = {46: "Mira", 48: "Aldor", 19: "Beholder", 20: "Shirard"}
BOSS_TITLE = {"Beholder": "The Beholder"}
# What to do in each phase, in the order the shapes come (handlers.BOSS_SHAPES).
BOSS_ADVICE = {
    "Mira": ("She shoots down the line she faces, two to five squares out. "
             "Close in: nothing beside her is hit.",
             "Blade in hand, she covers the three squares in front and both "
             "shoulders. Get behind her."),
    "Aldor": ("He guards his front and one shoulder. Take the other shoulder "
              "or his back.",
              "He swings wide: front, both front corners and both shoulders. "
              "Only the three squares behind him are safe."),
    "Beholder": ("It strikes the four diagonals. Stand square on, beside it, "
                 "and it cannot touch you.",
                 "It glares down the four straight lines, up to four squares. "
                 "Now only the diagonals are safe."),
    "Shirard": ("A burst lands on the ring two squares out. Step in beside him "
                "and it passes over you.",
                "He draws a blade: front, both front corners and both "
                "shoulders. Get behind him."),
}
SHAPE_WORDS = {
    "front1": "the one square in front",
    "front3": "the three squares in front",
    "sides": "both shoulders, left and right",
    "fire": "two rows of three in front",
    "lunge": "two squares straight ahead",
    "spores": "four squares two away, straight out",
    "pierce": "the square in front and the one behind",
    "corners": "the four diagonals",
    "fence": "the front and one shoulder",
    "ray": "a line two to five squares ahead",
    "gaze": "four straight lines, one to four squares out",
    "burst": "the ring two squares out",
    "boss": "front, both front corners and both shoulders",
    "ring": "all eight squares around it",
}


def slug(name):
    return name.lower().replace(" ", "-").replace("'", "")


def esc(s):
    return html.escape(str(s))


def pictures(w, sheet):
    """portrait and walk loop for one sprite sheet, shared by whoever wears it."""
    os.makedirs(IMG, exist_ok=True)
    pic = portrait(w, sheet, os.path.join(IMG, f"sheet-{sheet}.png"), scale=5)
    gif_name = f"sheet-{sheet}-walk.gif"
    gif = gif_name if showcase.walk_gif(
        w, sheet, os.path.join(IMG, gif_name), side=5, radius=2, scale=4) else None
    return (f"img/{pic}" if pic else None), (f"img/{gif}" if gif else None)


def grid(cells, label):
    """The creature in the middle, facing right; red where it strikes."""
    reach = max([max(abs(x), abs(y)) for x, y in cells] + [2])
    n = 2 * reach + 1
    size, gap = 22, 2
    span = n * size + (n - 1) * gap
    hit = {tuple(c) for c in cells}
    out = [f'<svg class="grid" viewBox="0 0 {span} {span}" role="img" '
           f'aria-label="{esc(label)}">']
    for gy in range(n):
        for gx in range(n):
            x, y = gx - reach, gy - reach
            px, py = gx * (size + gap), gy * (size + gap)
            if (x, y) == (0, 0):
                out.append(f'<rect x="{px}" y="{py}" width="{size}" height="{size}" '
                           f'rx="{size // 2}" fill="var(--me)"/>')
                cx, cy = px + size / 2, py + size / 2
                out.append(f'<path d="M{cx - 4} {cy - 6} L{cx + 7} {cy} L{cx - 4} {cy + 6} Z" '
                           f'fill="var(--ground)"/>')
                continue
            near = max(abs(x), abs(y)) == 1
            fill = ("var(--hit)" if (x, y) in hit
                    else "var(--safe)" if near else "var(--void)")
            out.append(f'<rect x="{px}" y="{py}" width="{size}" height="{size}" '
                       f'rx="3" fill="{fill}"/>')
    out.append("</svg>")
    return "".join(out)


def shape_facts(pattern):
    cells = handlers._cells(pattern, 0, 0, 1)
    adjacent = sum(1 for x, y in cells if max(abs(x), abs(y)) == 1)
    return cells, adjacent, 8 - adjacent


def turn_cost(w, m, tier):
    """Share of the tier's expected life one turn in this shape costs."""
    ref = tiers.REFERENCE[tier]
    suit = catalogue().find(ref["suit"])
    blow = handlers._pressure_blow(w, m)
    swings = max(1, TURN // m.offence()["swing"])
    per = tiers._expected(blow, REF_HIT_CHANCE, suit.effect if suit else 0)
    return swings * per / ref["life"]


def top_of(line, tier):
    got = [i for i in catalogue().get("weapon")
           if getattr(i, "tier", None) == tier and tiers.line_of(i) == line]
    return max(got, key=lambda i: i.price) if got else None


def blow_of(it, tier):
    stat = tiers.REFERENCE[tier]["stat"]
    skill = 9 if it.cls == "bow" else tiers.HIT
    return skill + it.effect + tiers.potency_bonus(stat, tiers.swing_of(it))


def verdict(m, tier):
    """Which weapon to bring, and why, from the numbers."""
    shell = m.offence()["armour"]
    interval = m.offence()["swing"]
    sword = top_of("sword", tier)
    heavy = top_of("heavy", tier)
    if shell:
        s = round(100 * shell / blow_of(sword, tier)) if sword else 0
        h = round(100 * shell / blow_of(heavy, tier)) if heavy else 0
        return ("Heavy weapon or bow",
                f"Its shell takes {shell} off every blow: about {s}% of a "
                f"{sword.name}'s, {h}% of a {heavy.name}'s. Big blows lose "
                f"least. Zap ignores the shell.")
    reach = tiers.ORDER[:tiers.ORDER.index(tier) + 1]
    blades = sorted((i for i in catalogue().get("weapon")
                     if getattr(i, "tier", None) in reach and i.cls != "bow"
                     and tiers.swing_of(i) + STEP_OUT < interval),
                    key=lambda i: (tiers.swing_of(i), i.name))
    if heavy and tiers.swing_of(heavy) + STEP_OUT < interval:
        return ("Anything",
                f"No shell, and it swings only every {interval}: even a heavy "
                f"blow fits between two of its swings if you step in and out.")
    fit = ", ".join(sorted({i.name for i in blades})) or "nothing you can buy by then"
    return ("Sword",
            f"No shell, so small blows lose nothing and waste little on the "
            f"kill. It swings every {interval}: a blow that fits between two "
            f"swings, stepping in and out, lets you hit it untouched. That is "
            f"{fit}.")


def creature_cards(w):
    by = {}
    for m in sorted(w.mobs.values(), key=lambda x: x.node):
        if m.npc or m.node in BOSS_NODES:
            continue
        name = handlers.fighter_name(w, m)
        if name in ("It", None) or not getattr(m, "tier", None):
            continue
        by.setdefault(name, []).append(m)
    order = sorted(by, key=lambda n: (min(tiers.ORDER.index(m.tier) for m in by[n]),
                                      min(tiers.ROUTE.index(m.location) for m in by[n])))
    cards = {}
    for name in order:
        ms = by[name]
        m0 = ms[0]
        pic, gif = pictures(w, m0.creature)
        pattern = handlers.PATTERNS.get(name, "ring")
        cells, adjacent, safe = shape_facts(pattern)
        blows = max(1, TURN // m0.offence()["swing"])
        rows = []
        for tier in tiers.ORDER:
            here = [m for m in ms if m.tier == tier]
            if not here:
                continue
            lives = sorted({m.max_hp for m in here})
            life = f"{lives[0]}" if len(lives) == 1 else f"{lives[0]}–{lives[-1]}"
            rooms = []
            for loc in tiers.ROUTE:
                n = sum(1 for m in here if m.location == loc)
                if n:
                    rooms.append(f"{esc(w.name(loc))}&nbsp;{n}")
            gold, xp = here[0].spoil()
            rows.append(
                f'<tr><th scope="row">{tier}</th><td class="num">{life}</td>'
                f'<td class="num">{here[0].offence()["armour"] or "–"}</td>'
                f'<td class="num">{round(100 * turn_cost(w, here[0], tier))}%</td>'
                f'<td class="num">{gold}g&nbsp;·&nbsp;{xp}xp</td>'
                f'<td class="rooms">{", ".join(rooms)}</td></tr>')
        # advice for the gear you have when you first meet it
        earliest = min(ms, key=lambda m: tiers.ORDER.index(m.tier))
        bring, why = verdict(earliest, earliest.tier)
        shelled = any(m.offence()["armour"] for m in ms)
        tag = '<span class="tag shell">Shelled</span>' if shelled else ""
        first = min((m.location for m in ms), key=tiers.ROUTE.index)
        cards[name] = (first, pic, f'''
<article class="card" id="{slug(name)}">
  <header class="card-head">
    {f'<img class="portrait" src="{pic}" alt="" width="60" height="60">' if pic else ''}
    <div>
      <h3>{esc(name)} {tag}</h3>
      <p class="kind">{blows} blows a turn · strikes {SHAPE_WORDS.get(pattern, pattern)}</p>
    </div>
  </header>
  <div class="body">
    <figure class="shape">
      {grid(cells, f"{name} strikes {SHAPE_WORDS.get(pattern, pattern)}")}
      <figcaption>{"Safe on " + str(safe) + " of the 8 squares beside it" if safe else "Nowhere beside it is safe"}</figcaption>
    </figure>
    {f'<img class="walk" src="{gif}" alt="{esc(name)} walking" loading="lazy">' if gif else ''}
  </div>
  <p class="bring"><span>Bring</span> {esc(bring)}</p>
  <p class="why">{esc(why)}</p>
  <div class="scroll"><table>
    <thead><tr><th>Tier</th><th>Life</th><th>Shell</th><th>A turn in reach</th><th>Pays</th><th>Where</th></tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table></div>
</article>''')
    return cards


def boss_cards(w):
    cards = {}
    cfg = handlers.balance()
    for node, name in BOSS_NODES.items():
        m = w.mobs[node]
        tier = m.tier
        pic, gif = pictures(w, m.creature)
        m.boss = True
        pool = tiers.boss_life(tier, cfg["boss_turns"])
        gold, xp = m.spoil()
        blows = max(1, TURN // m.offence()["swing"])
        phases = []
        for i, pattern in enumerate(handlers.BOSS_SHAPES[name]):
            cells, adjacent, safe = shape_facts(pattern)
            m.phase = i + 1
            cost = round(100 * turn_cost(w, m, tier))
            phases.append(f'''
    <figure class="phase">
      <figcaption><b>Phase {i + 1}</b> · {SHAPE_WORDS[pattern]}</figcaption>
      {grid(cells, f"{name}, phase {i + 1}: {SHAPE_WORDS[pattern]}")}
      <p>{esc(BOSS_ADVICE[name][i])}</p>
      <p class="small">A turn in reach costs about {cost}% of a tier {tier} hero's life.</p>
    </figure>''')
        m.phase = 1
        title = BOSS_TITLE.get(name, name)
        cards[name] = (m.location, pic, f'''
<article class="card boss" id="{slug(name)}">
  <header class="card-head">
    {f'<img class="portrait" src="{pic}" alt="" width="60" height="60">' if pic else ''}
    <div>
      <h3>{esc(title)} <span class="tag">Boss · tier {tier}</span></h3>
      <p class="kind">{esc(w.name(m.location))} · {blows} blows a turn · two phases of {pool} life</p>
    </div>
  </header>
  <p class="change">When the first bar empties: <q>{esc(handlers.BOSSES[name])}</q>. The bar refills and the safe squares change.</p>
  <div class="phases">{"".join(phases)}</div>
  <p class="small">Pays {gold}g and {xp}xp once, when the second bar empties. Fleeing resets it to phase 1.</p>
</article>''')
    return cards


CSS = """
:root {
  color-scheme: dark;
  --ground:#15120e; --panel:#1d1913; --panel2:#241f17; --rule:#5b4726;
  --ink:#efe3c4; --dim:#bdad86; --faint:#8a7c5b; --gold:#e8c85c;
  --hit:#b8522c; --safe:#3e5d3a; --void:#26201a; --me:#eadfc2;
}
* { box-sizing:border-box }
html { background:var(--ground) }
body { margin:0; background:var(--ground); color:var(--ink);
  font-family:"EB Garamond",Palatino,Georgia,serif; font-size:17px; line-height:1.5;
  padding-inline:16px }
.page { max-width:600px; margin:0 auto; padding-block:24px 64px }
.eyebrow, .kind small, th, .tag, .bring span, .crates span, .shop li span,
nav a, figcaption b { font-family:Cinzel,Georgia,serif; letter-spacing:.12em }
.eyebrow { font-size:11px; text-transform:uppercase; color:var(--faint); margin:0 0 4px }
h1 { font-family:Cinzel,Georgia,serif; font-weight:800; font-size:34px; margin:0;
  line-height:1.1; text-wrap:balance; text-shadow:0 2px 0 #000 }
.lede { color:var(--dim); margin:10px 0 0; max-width:60ch }
h2 { font-family:Cinzel,Georgia,serif; font-size:13px; font-weight:600;
  letter-spacing:.2em; text-transform:uppercase; color:var(--gold);
  margin:36px 0 12px; padding-bottom:6px; border-bottom:1px solid var(--rule) }
nav { position:sticky; top:env(safe-area-inset-top, 0px); z-index:5;
  background:var(--ground); margin:18px -16px 0; padding:10px 16px;
  display:flex; gap:8px; overflow-x:auto; border-bottom:1px solid var(--rule);
  scrollbar-width:none }
nav a { flex:0 0 auto; display:flex; align-items:center; gap:6px; color:var(--ink);
  text-decoration:none; font-size:11px; text-transform:uppercase;
  border:1px solid var(--rule); border-radius:999px; padding:4px 10px 4px 4px;
  background:var(--panel) }
nav a.plain { padding-left:10px }
nav img { width:22px; height:22px; object-fit:contain; image-rendering:pixelated }
nav a:focus-visible, a:focus-visible { outline:2px solid var(--gold); outline-offset:2px }
.legend { display:flex; flex-wrap:wrap; gap:14px; font-size:14px; color:var(--dim); margin:14px 0 0 }
.legend i { display:inline-block; width:12px; height:12px; border-radius:2px;
  vertical-align:-1px; margin-right:6px }
.card { background:var(--panel); border:1px solid var(--rule); border-radius:4px;
  padding:16px; margin:0 0 16px; scroll-margin-top:64px }
.card-head { display:flex; gap:12px; align-items:center }
.portrait { width:60px; height:60px; object-fit:contain; image-rendering:pixelated;
  background:var(--panel2); border-radius:3px; flex:0 0 auto }
h3 { font-family:Cinzel,Georgia,serif; font-size:21px; font-weight:800; margin:0;
  text-wrap:balance; display:flex; flex-wrap:wrap; align-items:center; gap:8px }
.kind { color:var(--dim); font-size:15px; margin:2px 0 0 }
.tag { font-size:10px; text-transform:uppercase; font-weight:600; color:var(--ground);
  background:var(--gold); border-radius:999px; padding:2px 8px }
.tag.shell { background:#8fa3ad }
.body { display:flex; gap:14px; align-items:center; margin:14px 0 10px; flex-wrap:wrap }
.shape { margin:0; display:flex; flex-direction:column; gap:6px }
.grid { width:132px; height:auto; display:block }
.shape figcaption, .small { font-size:14px; color:var(--dim) }
.walk { image-rendering:pixelated; flex:1 1 160px; min-width:0; max-width:240px;
  height:auto; border-left:1px solid var(--rule); padding-left:14px }
.bring { margin:8px 0 2px; font-size:18px }
.bring span, .crates span, .shop li span { font-size:10px; text-transform:uppercase;
  color:var(--gold); margin-right:6px }
.why { margin:0 0 12px; color:var(--ink) }
.scroll { overflow-x:auto }
table { border-collapse:collapse; width:100%; font-size:14px; font-variant-numeric:tabular-nums }
th { font-size:10px; text-transform:uppercase; color:var(--faint); text-align:left;
  font-weight:600; padding:4px 8px 4px 0; border-bottom:1px solid var(--rule) }
td { padding:5px 8px 5px 0; border-bottom:1px solid #2c261c; vertical-align:top }
tbody th { font-size:13px; color:var(--ink); border-bottom:1px solid #2c261c }
td.num { white-space:nowrap }
td.rooms { color:var(--dim) }
.change { margin:12px 0; color:var(--dim) }
.change q { color:var(--ink); font-style:italic }
.phases { display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px }
.phase { margin:0; background:var(--panel2); border-radius:3px; padding:12px;
  display:flex; flex-direction:column; gap:8px }
.phase figcaption { font-size:14px; color:var(--dim) }
.phase figcaption b { font-size:11px; text-transform:uppercase; color:var(--gold) }
.phase p { margin:0 }
.tier { margin:0 0 22px }
.tier h3 { font-size:19px }
.route { font-size:14px; color:var(--dim); margin:6px 0 10px }
.shop { border-left:2px solid var(--rule); padding-left:12px; margin:0 0 10px }
.shop h4 { font-family:Cinzel,Georgia,serif; font-size:13px; letter-spacing:.08em; margin:0 0 4px }
.shop ul { list-style:none; margin:0; padding:0; display:grid; gap:4px; font-size:15px }
.shop small { color:var(--faint); font-variant-numeric:tabular-nums }
.crates { font-size:15px; color:var(--dim) }
footer { margin-top:40px; font-size:13px; color:var(--faint) }
@media (prefers-reduced-motion: reduce) { .walk { display:none } }
"""


CSS += """
.layout { max-width:600px; margin:0 auto }
.guide p { max-width:62ch }
.guide h3 { font-size:19px; margin:22px 0 8px }
.guide ul { padding-left:20px; margin:0 0 12px }
.guide li { margin:0 0 4px }
.phone { font-family:"IBM Plex Mono",Menlo,monospace; font-size:14px;
  background:#0d0b09; border:1px solid var(--rule); border-radius:3px;
  padding:10px 12px; display:grid; gap:6px; margin:0 0 12px; overflow-x:auto }
.phone .worse { color:#ff7070 } .phone .better { color:#82d282 } .phone .locked { color:#9a9a9a }
.room { border-left:2px solid var(--rule); padding:2px 0 2px 12px; margin:18px 0 12px }
.room h4 { font-family:Cinzel,Georgia,serif; font-size:15px; letter-spacing:.06em; margin:0 }
.room p { margin:2px 0 0; font-size:15px; color:var(--dim) }
.room a { color:var(--ink) }
.badge { font-family:Cinzel,Georgia,serif; font-size:9px; letter-spacing:.12em;
  text-transform:uppercase; border:1px solid var(--rule); border-radius:999px;
  padding:1px 7px; margin-left:6px; color:var(--gold); vertical-align:2px }
.tierhead { background:var(--panel2); border:1px solid var(--rule); border-radius:4px;
  padding:14px 16px; margin:28px 0 10px }
.tierhead h3 { font-size:22px }
nav .group { display:contents }
@media (min-width: 920px) {
  .layout { display:grid; grid-template-columns:200px minmax(0, 600px); gap:36px;
    max-width:880px }
  nav { position:sticky; top:calc(env(safe-area-inset-top, 0px) + 16px); align-self:start;
    flex-direction:column; margin:0; padding:0; border:0; overflow:visible;
    max-height:calc(100vh - 32px); overflow-y:auto; gap:4px }
  nav a { border:0; background:none; padding:2px 0; font-size:11px }
  nav a.plain { padding-left:0 }
  nav .group { display:flex; flex-direction:column; gap:2px; margin-top:10px }
  nav a.tierlink { font-size:10px; letter-spacing:.2em; color:var(--gold) }
  .page { padding-block:32px 64px }
}
"""


def hero_section(w):
    stats = ", ".join(f"{k} {v}" for k, v in w.stats.items())
    worn = [w.equipped.get("weapon"), w.equipped.get("armour")]
    costs = []
    for lvl in range(4):
        w.level = lvl
        costs.append(str(w.xp_for_next()))
    w.level = 0
    return f'''
<section class="guide" id="hero">
  <h2>Your hero</h2>
  <p>You start at level 0 with {w.hero_max} life, {w.gold} gold and every ability at 3 ({esc(stats)}). You carry the {esc(worn[0])} and wear the {esc(worn[1])}; the Short Bow is in your pack for when you want it.</p>
  <h3>Levels</h3>
  <p>A level costs {", ".join(costs)}… experience, twenty more each time. A kill pays by the creature and its tier; a boss pays once, when it finally falls. Each level gives 6 more life (plus whatever Toughness adds), a full heal and <b>2 raise points</b>. One point adds 3 to an ability under 48, 2 under 78 and 1 above that. A full clear of the chapter lands you near level 12.</p>
  <h3>What each ability does</h3>
  <div class="scroll"><table>
    <thead><tr><th>Ability</th><th>Does</th></tr></thead>
    <tbody>
      <tr><th scope="row">Strength</th><td>Adds to every blade blow (see Weapons). Blades and all suits ask for it.</td></tr>
      <tr><th scope="row">Dexterity</th><td>Adds to every bow shot. Half of it is added to your chance to hit with anything, and half of it to your chance to be missed. Bows ask for it.</td></tr>
      <tr><th scope="row">Intelligence</th><td>All of it goes into Zap's damage.</td></tr>
      <tr><th scope="row">Willpower</th><td>All of it goes into Minor Cure's healing.</td></tr>
      <tr><th scope="row">Toughness</th><td>Life. Every point above 3 adds {tiers.TOUGH_LIFE}, so one raise point (+3) is {3 * tiers.TOUGH_LIFE} life, about two levels' worth.</td></tr>
      <tr><th scope="row">Speed</th><td>Every action is quicker: moving, swinging, shooting, dodging, casting. At Speed 27 an action takes {round(100 * tiers.speed_scaled(1000, 27) / 1000)}% of its time; the fight bar shows the times you actually pay.</td></tr>
    </tbody>
  </table></div>
  <h3>Where to put the third point</h3>
  <p>Put two of every three points into your weapon's ability: Strength for a blade, Dexterity for a bow. The third point is a choice of style, and all three work:</p>
  <ul>
    <li><b>Dexterity</b> (Strength for an archer): you hit and dodge more often, or wear better suits. The all-rounder.</li>
    <li><b>Toughness</b>: the tank. About twice the life by the end of the chapter and a third more mistakes survived, at the cost of fights running a little longer.</li>
    <li><b>Speed</b>: the tempo fighter. Fights end sooner and bosses fall faster, and a sword's shorter swing fits between more enemy blows. Fewer mistakes are survivable.</li>
  </ul>
</section>'''


def fight_section(w):
    c = catalogue()
    zap, cure, dodge = c.find("Zap"), c.find("Minor Cure"), c.find("Dodge")
    return f'''
<section class="guide" id="fight">
  <h2>The fight</h2>
  <p>A turn is {TURN} units. You plan yours, then both sides play out on the same clock: your blows and theirs land in time order. Walking into place usually takes a few steps first.</p>
  <h3>The fight bar</h3>
  <div class="scroll"><table>
    <thead><tr><th>Action</th><th>Takes</th><th>What it does</th></tr></thead>
    <tbody>
      <tr><th scope="row">Move</th><td class="num">{handlers.MOVE_COST} a step</td><td>Straight steps only.</td></tr>
      <tr><th scope="row">Hit</th><td class="num">the blade's Ti</td><td>A blow at a creature beside you.</td></tr>
      <tr><th scope="row">Shoot</th><td class="num">the bow's Ti</td><td>Needs a bow in hand, a clear line, and the target not beside you. The arrow takes the first creature on the line.</td></tr>
      <tr><th scope="row">Dodge</th><td class="num">{dodge.time}</td><td>Adds {dodge.precision} to your chance to be missed for the rest of the turn.</td></tr>
      <tr><th scope="row">Zap</th><td class="num">{zap.time}</td><td>A ray onto the exact square you name, anywhere in sight. Ignores armour and shells. Deals {zap.effect} + Intelligence, less the target's resistance.</td></tr>
      <tr><th scope="row">Minor Cure</th><td class="num">{cure.time}</td><td>Heals {cure.effect} + Willpower. Works {cure.precision}% of the time.</td></tr>
    </tbody>
  </table></div>
  <h3>Hitting and being hit</h3>
  <p>Your blow lands 100 + half your Dexterity − the creature's avoidance (about 12 to 16) times in a hundred. Half of the blows that land are precise (×1.5) and one in fifteen is a critical (×2). A creature's blow lands 70 − your avoidance (half your Dexterity, plus Dodge). Your suit takes its E off every blow that lands.</p>
  <h3>Shapes</h3>
  <p>No creature strikes every square around it. Each one strikes its own shape, shown on its card, drawn facing right. It picks its facing before the turn plays and walks until its shape covers the square you started on. Step off that shape before its blow lands and the blow misses: <i>Out of reach</i>. One whole turn standing inside a shape costs about a third of the life you are expected to have in that tier. Hold a bow and every ordinary creature instead walks up and strikes all eight squares around it. Bosses keep their shapes.</p>
  <h3>Practice</h3>
  <p>Every action and every weapon line has a title: Fumbler, Beginner, Trained, Experienced, Master, Expert, Sensei. Each use that lands adds 5% towards the next one, kept only if you win the fight. Each title adds 1 to that action's effect and takes 5% off its time.</p>
</section>'''


def weapons_section(w):
    stat = tiers.REFERENCE["III"]["stat"]
    sword, heavy, bow = (top_of(l, "III") for l in ("sword", "heavy", "bow"))
    usable = TURN - tiers.WALK

    def per(it):
        t = tiers.swing_of(it)
        return t, usable // t, tiers.potency_bonus(stat, t)
    st, sn, sb = per(sword)
    ht, hn, hb = per(heavy)
    return f'''
<section class="guide" id="weapons">
  <h2>Three kinds of weapon</h2>
  <p>Every trader tier sells a sword, an axe or hammer, and a bow at each price, and the best of each deals the same damage over a turn. What separates them is the job.</p>
  <div class="scroll"><table>
    <thead><tr><th>Kind</th><th>Swing</th><th>Blows</th><th>Best against</th><th>The catch</th></tr></thead>
    <tbody>
      <tr><th scope="row">Sword</th><td class="num">96–126</td><td class="num">4–5</td><td>Soft packs: Gorraks, Skeletons, Ghosts, Fire Devils. Small blows waste little on each kill, and a short swing fits between a creature's blows.</td><td>A shell takes a big bite out of every small blow.</td></tr>
      <tr><th scope="row">Axe, hammer</th><td class="num">195–240</td><td class="num">2</td><td>Shells (Beetles, Golems), big single creatures, bosses.</td><td>A long swing roots you in place, and quick creatures land a blow while you swing.</td></tr>
      <tr><th scope="row">Bow</th><td class="num">255</td><td class="num">2</td><td>Shells, and creatures on their way to you: your first shot at each is free while it walks in.</td><td>Nothing beside you, a clear line needed, creatures strike all eight squares, and better suits need Strength.</td></tr>
    </tbody>
  </table></div>
  <h3>How your ability adds</h3>
  <p>A blow adds a third of your Strength (Dexterity for a bow), scaled by how long the swing takes against 120. At Strength {stat} the {esc(sword.name)} (Ti{st}) adds {sb} to each of its {sn} blows a turn, about {sb * sn}; the {esc(heavy.name)} (Ti{ht}) adds {hb} to each of its {hn}, about {hb * hn}. Raising your ability helps every weapon about equally, so pick the weapon for the job and the ability for the weapon.</p>
  <h3>The footwork rule</h3>
  <p>A blow is safe from its target when stepping in, swinging and stepping out ({STEP_OUT} + the swing) is shorter than the time between two of its blows. Each creature's card says which blades manage it.</p>
</section>'''


def items_section(w):
    c = catalogue()
    fresh = World("ShiradsForge")
    blade, corr, giant = c.find("Bloody Blade"), c.find("Corrupter"), c.find("Giant Sword")
    shell = c.find("Snail Shell")
    return f'''
<section class="guide" id="items">
  <h2>Items and shops</h2>
  <h3>Reading a market line</h3>
  <div class="phone" aria-label="Market lines as the phone shows them">
    <span class="better">{esc(corr.label())}</span>
    <span class="locked">{esc(giant.label())}</span>
    <span>{esc(shell.label())}</span>
  </div>
  <ul>
    <li><b>E</b> on a weapon is added to every blow; it can be negative on a cheap weapon. On a suit it is taken off every blow you take.</li>
    <li><b>Ti</b> is how much of the {TURN}-unit turn one swing takes. Suits have none.</li>
    <li>The price comes last. What a piece asks for is not on the line: buying one you cannot wear yet tells you, as in <i>You need {esc(giant.ability)} {giant.requirement}.</i></li>
  </ul>
  <h3>The colours</h3>
  <ul>
    <li><span class="phone-inline better">Green</span>: better than what you wear in that slot, and you can pay for it.</li>
    <li><span class="phone-inline worse">Red</span>: worse than what you wear.</li>
    <li><span class="phone-inline locked">Grey</span>: your ability is still too low to wear it.</li>
    <li>No colour: a different kind of weapon from yours, or better but beyond your purse.</li>
  </ul>
  <p>A weapon is compared by the damage it deals over a turn, not by its E, so a fast sword with a small E can be green next to a hammer with a big one.</p>
  <h3>Selling</h3>
  <p>Traders do not buy. <b>Recycle</b> on an item breaks it and gives you {tiers.RECYCLE_PERCENT}% of its price. It is the only way to turn gear back into gold, and every crate holds something worth keeping or breaking.</p>
  <h3>Traders and crates</h3>
  <p>Five traders, one plan per tier. Each trader sells its own tier; where a tier has two, the nearer one sells the cheaper half and the further one the better half, and each keeps the best piece of the shop before it. Every crate holds an item. A few on the main path hold the next step up for you: a better weapon of the kind in your hand, or a better suit. Every other crate holds a spare from that tier or below that you do not carry yet: switch to it, or recycle it for gold. Past tier I no crate holds the best piece of its tier, which is the trader's. The first crate in the Village gives a new hero a better weapon he can wear at once.</p>
  <p class="small">Charms, bombs and the other skills and spells in the catalogue do nothing in this chapter and are not sold.</p>
</section>'''


def route_section(w, cards, bosses):
    by_room = {}
    for name, (loc, pic, card) in {**cards, **bosses}.items():
        by_room.setdefault(loc, []).append(card)
    out, nav = [], []
    roles = {"weapon": "Gear crate: weapon step", "suit": "Gear crate: suit step"}
    for tier in tiers.ORDER:
        ref = tiers.REFERENCE[tier]
        lo, hi = tiers.STOPS[tier]
        rooms = tiers.ROUTE[lo - 1:hi]
        shops = []
        for i, loc in enumerate(handlers.TRADERS):
            if handlers.TRADER_TIERS[i] != tier:
                continue
            w.location = loc
            w.note_place(loc)
            lines = []
            for which, label in ((0, "Melee"), (1, "Bows"), (2, "Suits")):
                _, items = handlers.market_rows(w, which)
                lines.append(f'<li><span>{label}</span> ' + ", ".join(
                    f"{esc(it.name)} <small>{it.price}g · {it.ability[:3]} {it.requirement}</small>"
                    for it in items) + "</li>")
            shops.append(f'<div class="shop"><h4>{esc(w.name(loc))}</h4><ul>{"".join(lines)}</ul></div>')
        out.append(f'''
<section id="tier-{tier.lower()}">
  <div class="tierhead">
    <h3>Tier {tier}</h3>
    <p class="kind">Arrive around level {ref["level"]} with {ref["life"]} life, main ability {ref["stat"]} and a {esc(ref["suit"])}.</p>
  </div>
  {"".join(shops)}''')
        group = [f'<a class="plain tierlink" href="#tier-{tier.lower()}">Tier {tier}</a>']
        for loc in rooms:
            here = [m for m in w.mobs.values() if m.location == loc and not m.npc
                    and (m.alive or getattr(m, "dormant", False))]
            counts = {}
            for m in here:
                n = handlers.fighter_name(w, m)
                counts[n] = counts.get(n, 0) + 1
            foes = ", ".join(
                f'<a href="#{slug(n)}">{esc(BOSS_TITLE.get(n, n))}</a>'
                + (f" ×{k}" if k > 1 else "") for n, k in counts.items())
            badges = ""
            if loc in handlers.TRADERS:
                badges += '<span class="badge">Trader</span>'
            gear = [roles[r] for st, r in tiers.CRATES.items()
                    if r != "gold" and w.crate_location(st) == loc]
            spare = sum(1 for st in w.crate_payoffs() | set(
                r[0] for r in w.real1 if len(r) > 12 and r[12] == 3
                and "crate" in w.entity_label(r[0]).lower())
                if w.crate_location(st) == loc and tiers.crate_role(st) == "spare")
            notes = gear + ([f"{spare} crate{'s' if spare > 1 else ''} with a spare"]
                            if spare else [])
            out.append(f'''
  <div class="room" id="room-{loc}">
    <h4>{esc(w.name(loc))}{badges}</h4>
    <p>{foes or "No fights."}{(" · " + " · ".join(notes)) if notes else ""}</p>
  </div>''')
            for card in by_room.get(loc, []):
                out.append(card)
            for name, (first, pic, _) in {**cards, **bosses}.items():
                if first == loc:
                    group.append(f'<a href="#{slug(name)}">'
                                 + (f'<img src="{pic}" alt="">' if pic else "")
                                 + f"{esc(BOSS_TITLE.get(name, name))}</a>")
        out.append("</section>")
        nav.append(f'<div class="group">{"".join(group)}</div>')
    return "".join(out), "".join(nav)


def build():
    w = World("ShiradsForge")
    w.entity_table()
    w.equipped["weapon"] = "Bloody Blade"
    cards = creature_cards(w)
    bosses = boss_cards(w)
    route, route_nav = route_section(w, cards, bosses)
    guide = (hero_section(World("ShiradsForge")) + fight_section(w)
             + weapons_section(w) + items_section(w))
    nav = ('<div class="group"><a class="plain tierlink" href="#hero">Start here</a>'
           '<a class="plain" href="#hero">Your hero</a>'
           '<a class="plain" href="#fight">The fight</a>'
           '<a class="plain" href="#weapons">Weapons</a>'
           '<a class="plain" href="#items">Items &amp; shops</a></div>' + route_nav)
    page = f"""<title>Shirard's Forge Companion</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;800&family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=IBM+Plex+Mono&display=swap">
<style>{CSS}</style>
<div class="layout">
  <nav aria-label="Contents">{nav}</nav>
  <div class="page">
    <p class="eyebrow">Era of Eidolon · Shirard's Forge</p>
    <h1>Shirard's Forge Companion</h1>
    <p class="lede">Everything the game does not tell you, in the order you need it: your hero, how a fight works, the three kinds of weapon, the shops, and then the route, room by room, with each creature where you first meet it.</p>
    {guide}
    <h2 id="route">The route</h2>
    <p class="small">Rooms in the order the chapter is meant to be walked. A creature's card appears where you first meet it. On each card, red squares are where it strikes, green are safe squares beside it, and the pale circle is the creature itself, facing right.</p>
    {route}
    <footer>Built from the reconstruction server's own numbers by tools/compendium_book.py. Rerun it after a balance change.</footer>
  </div>
</div>
"""
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "index.html"), "w") as fh:
        fh.write(page)
    return OUT


if __name__ == "__main__":
    out = build()
    print(os.path.join(out, "index.html"))
