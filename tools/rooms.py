#!/usr/bin/env python3
"""Every room of a chapter, side by side, each on its own.

    python3 tools/rooms.py SterlingLake

Shirard's Forge can be laid out flat, because its doorways were recovered and
they meet edge to edge. The other two chapters cannot: their doors came from
the server with everything else, so nobody knows which room joins which. This
draws them as a plate of separate rooms rather than inventing a geography.

Ground is what you see when you walk in, not the union of everything the room
later becomes, and the creatures are the ones the reconstruction places — so for Sterling Lake and Mistral Grove
the monsters are a guess and the shape of the rooms is not.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "server"))
sys.path.insert(0, HERE)

from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from render_map import render  # noqa: E402
from world import World  # noqa: E402

GAP, HEAD, PAD = 26, 26, 22
BG = (16, 14, 11, 255)


def font(size):
    for p in ("/System/Library/Fonts/Supplemental/Georgia.ttf",
              "/System/Library/Fonts/Supplemental/Times New Roman.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def main():
    game = sys.argv[1] if len(sys.argv) > 1 else "ShiradsForge"
    cap = int(sys.argv[2]) if len(sys.argv) > 2 else 420
    w = World(game)
    painted = 0            # the ground as the player meets it, not revealed
    for loc in w.locations:
        if not any(m.location == loc for m in w.mobs.values()):
            try:
                w.populate_location(loc)
            except Exception:
                pass

    tiles = []
    for loc in w.locations:
        img = render(w, loc, annotate=False, bg=(0, 0, 0, 0))
        if not img:
            continue
        box = img.getbbox()
        if box:
            img = img.crop(box)
        if img.width > cap or img.height > cap:
            r = min(cap / img.width, cap / img.height)
            img = img.resize((max(1, int(img.width * r)),
                              max(1, int(img.height * r))), Image.LANCZOS)
        tiles.append((loc, w.name(loc), img))

    # pack into rows that stay under a sensible sheet width
    maxw = 3 * cap + GAP * 4
    rows, row, wide = [], [], 0
    for t in tiles:
        if row and wide + t[2].width + GAP > maxw:
            rows.append(row)
            row, wide = [], 0
        row.append(t)
        wide += t[2].width + GAP
    if row:
        rows.append(row)

    W = max(sum(t[2].width + GAP for t in r) + GAP for r in rows)
    H = sum(max(t[2].height for t in r) + GAP + HEAD for r in rows) + PAD
    sheet = Image.new("RGBA", (W, H + PAD), BG)

    y = PAD
    spots = []
    for r in rows:
        tall = max(t[2].height for t in r)
        x = GAP
        for loc, name, img in r:
            sheet.alpha_composite(img, (x, y + (tall - img.height)))
            spots.append((x, y + tall + 6, loc, name))
            x += img.width + GAP
        y += tall + HEAD + GAP

    d = ImageDraw.Draw(sheet)
    for x, ty, loc, name in spots:
        d.text((x, ty), f"{loc}  {name}", fill=(232, 220, 186, 255), font=font(15))

    out = os.path.join(ROOT, "assets", f"{game}-rooms.png")
    sheet.convert("RGB").save(out)
    print(f"{out}  {sheet.size[0]}x{sheet.size[1]}  "
          f"{len(tiles)} rooms, {painted} tiles revealed")


if __name__ == "__main__":
    main()
