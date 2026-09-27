#!/usr/bin/env python3
"""One creature's compendium page, as a prototype to look at.

    python3 tools/compendium_card.py Golem

Writes assets/compendium/<name>/ — a portrait, a walk loop that circles so
you see every side, and an index.html that lays them out with the shapes.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "server"))
sys.path.insert(0, HERE)

from PIL import Image  # noqa: E402
import handlers  # noqa: E402
from world import World  # noqa: E402
import showcase  # noqa: E402

OUT = os.path.join(ROOT, "assets", "compendium")
TURN = 720


def portrait(w, creature, path, scale=6):
    """The biggest standing frame it has, blown up with hard pixels."""
    have = set(w.res.props(11, creature))
    for anim in (1, 15, 14):
        if anim not in have:
            continue
        got = showcase.frames(w, creature, anim)
        if not got:
            continue
        img = max((f[0] for f in got), key=lambda i: i.width * i.height)
        img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        img.save(path)
        return os.path.basename(path)
    return None


def grid(cells, caption, note):
    """A five-across board with the actor at the middle, facing right."""
    S, G = 26, 2
    span = 5 * S + 4 * G
    parts = [f'<figure class="shape"><svg viewBox="0 0 {span} {span}" '
             f'role="img" aria-label="{caption}">']
    for gy in range(5):
        for gx in range(5):
            x, y = gx - 2, gy - 2
            px, py = gx * (S + G), gy * (S + G)
            me = (x, y) == (0, 0)
            hit = [x, y] in cells or (x, y) in cells
            near = not me and max(abs(x), abs(y)) == 1
            fill = ("var(--me)" if me else "var(--hit)" if hit
                    else "var(--safe)" if near else "var(--void)")
            r = S // 2 if me else 3
            parts.append(f'<rect x="{px}" y="{py}" width="{S}" height="{S}" '
                         f'rx="{r}" fill="{fill}"/>')
    parts.append("</svg>")
    parts.append(f"<figcaption><b>{caption}</b><span>{note}</span></figcaption>")
    parts.append("</figure>")
    return "".join(parts)


def card(game, name):
    w = World(game)
    target = None
    for m in sorted(w.mobs.values(), key=lambda x: x.node):
        nm = handlers.fighter_name(w, m)
        if nm == "It":
            nm = w.creature_name(m.creature) or ""
        if nm.lower() == name.lower():
            target = m
            break
    if target is None:
        raise SystemExit(f"no creature called {name}")

    folder = os.path.join(OUT, name.lower().replace(" ", "-"))
    os.makedirs(folder, exist_ok=True)
    pic = portrait(w, target.creature, os.path.join(folder, "portrait.png"))
    # A small board and a tight circle, blown up hard: the point of the loop
    # is seeing the creature from every side, and on the roomier board used
    # for the sheets it is a speck on a lot of floor.
    gif = "walk.gif" if showcase.walk_gif(
        w, target.creature, os.path.join(folder, "walk.gif"),
        side=5, radius=2, scale=6) else None

    pattern = handlers.pattern_of(w, target)
    theirs = handlers._cells(pattern, 0, 0, 1)
    # THREAT prices the blow — a shape that covers little may hit hard — and
    # carries a floor of 1 so nothing divides by zero. It is not a count of
    # squares, so describing the shape means counting the cells themselves.
    reach = len(theirs)
    adjacent = sum(1 for c in theirs if max(abs(c[0]), abs(c[1])) == 1)
    safe = 8 - adjacent
    swings = max(1, TURN // target.offence()["swing"])
    rooms = sorted({w.name(o.location) for o in w.mobs.values()
                    if (w.creature_name(o.creature) == name
                        or handlers.fighter_name(w, o) == name)})


    html = f"""<!doctype html>
<meta charset="utf-8">
<title>{name} — Compendium</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;800&family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap">
<style>
:root {{
  --ink:#f3e6c4; --dim:#c3b389; --faint:#8b7d5c;
  --ground:#14110e; --panel:#1b1711; --rule:#6e5424; --gold:#f4dc62;
  --hit:#b4532b; --safe:#3d5b3a; --void:#221d16; --me:#e8dcc0;
}}
* {{ box-sizing:border-box }}
body {{ margin:0; background:var(--ground); color:var(--ink);
  font-family:"EB Garamond",Palatino,Georgia,serif; font-size:17px; line-height:1.55 }}
.page {{ max-width:520px; margin:0 auto; padding:34px 30px 60px;
  box-shadow:inset 3px 0 0 var(--rule), inset 4px 0 0 var(--gold) }}
.eyebrow {{ font-family:Cinzel,Georgia,serif; font-size:11px; letter-spacing:.22em;
  text-transform:uppercase; color:var(--faint); margin:0 0 6px }}
h1 {{ font-family:Cinzel,Georgia,serif; font-weight:800; font-size:40px;
  letter-spacing:.02em; margin:0; text-wrap:balance;
  text-shadow:0 2px 0 #000, 0 0 22px rgba(244,220,98,.18) }}
.rule {{ height:1px; background:linear-gradient(90deg,var(--gold),var(--rule),transparent);
  margin:16px 0 22px }}
.plate {{ background:var(--panel); border:1px solid var(--rule); border-radius:3px;
  display:flex; align-items:center; justify-content:center; gap:18px;
  padding:16px 14px; margin:0 0 22px; min-height:180px; overflow:hidden }}
.plate img.portrait {{ image-rendering:pixelated; display:block; max-height:150px;
  flex:0 0 auto }}
.plate img.walk {{ image-rendering:pixelated; display:block; border-left:1px solid var(--rule);
  padding-left:20px; width:100%; max-width:290px; height:auto; flex:1 1 auto;
  min-width:0 }}
.stat {{ display:flex; gap:34px; flex-wrap:nowrap; margin:0 0 22px }}
.stat div {{ display:flex; flex-direction:column }}
.stat b {{ font-family:Cinzel,Georgia,serif; font-size:24px; line-height:1.1 }}
.stat span {{ font-size:11px; letter-spacing:.12em; text-transform:uppercase; color:var(--faint) }}
h2 {{ font-family:Cinzel,Georgia,serif; font-size:13px; letter-spacing:.18em;
  text-transform:uppercase; color:var(--dim); margin:28px 0 12px; font-weight:600 }}
.shapes {{ display:flex; gap:26px; flex-wrap:wrap }}
.shape {{ margin:0 }}
.shape svg {{ width:168px; height:168px; display:block }}
figcaption {{ margin-top:9px; display:flex; flex-direction:column }}
figcaption b {{ font-family:Cinzel,Georgia,serif; font-size:12px; letter-spacing:.1em;
  text-transform:uppercase; font-weight:600 }}
figcaption span {{ font-size:14px; color:var(--dim) }}
p {{ margin:0 0 12px }}
.where {{ color:var(--dim); font-style:italic }}
</style>
<div class="page">
  <p class="eyebrow">Era of Eidolon &middot; Shirard&rsquo;s Forge</p>
  <h1>{name}</h1>
  <div class="rule"></div>

  <div class="plate">
    {'<img class="portrait" src="' + pic + '" alt="' + name + '">' if pic else ''}
    {'<img class="walk" src="' + gif + '" alt="' + name + ' walking">' if gif else ''}
  </div>

  <div class="stat">
    <div><b>{reach}</b><span>squares it reaches</span></div>
    <div><b>{safe}</b><span>safe beside it</span></div>
    <div><b>{swings}</b><span>blows a turn</span></div>
  </div>

  <h2>Where it can reach you</h2>
  <div class="shapes">
    {grid(theirs, name, (f"{adjacent} of the eight squares beside it" if adjacent
          else "nothing next to it — it strikes at arm's length") +
          ", and it picks its facing before the turn plays")}
  </div>

  <h2>How to fight it</h2>
  <p>{'It swings ' + str(swings) + ' times a turn, so each blow is small. Armour comes off every one of them, and earns its price here.' if swings >= 3 else 'It swings ' + str(swings) + ' times a turn, so each blow is large. Stepping out of reach saves the whole of one, which is worth more than armour against it.'}</p>
  <p>{'There is nowhere beside it that is safe.' if adjacent == 8
       else 'It cannot touch anything standing next to it. Close the gap and it has to back off before it can strike.' if adjacent == 0
       else 'Stand on one of the ' + str(safe) + ' squares it cannot turn to, and it spends its turn walking instead of hitting.'}</p>
  <p class="where">Found in {', '.join(rooms) if rooms else 'nowhere we have mapped'}.</p>
</div>
"""
    with open(os.path.join(folder, "index.html"), "w") as fh:
        fh.write(html)
    return folder, pic, gif


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "Golem"
    game = sys.argv[2] if len(sys.argv) > 2 else "ShiradsForge"
    folder, pic, gif = card(game, name)
    print(f"{folder}/index.html")
    print(f"   portrait: {pic}   walk: {gif}")
