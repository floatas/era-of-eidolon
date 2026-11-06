#!/usr/bin/env python3
"""The chapter as one sheet, to print or hang.

    python3 tools/poster.py ShiradsForge

Two differences from worldmap.py, and both are deliberate.

The ground is every tile the world ever has, patches applied, so nothing is
hidden behind a quest step. And the handful of rooms that cannot share a
border with anything — the ones worldmap.py exiles to their own patch — are
drawn tucked against the body of the world instead of stranded off to one
side, so the sheet packs into a rectangle you can frame.

That makes it a picture rather than evidence: the seams are real, the tucked
rooms are not. worldmap.py stays honest about which is which.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "server"))
sys.path.insert(0, HERE)

from PIL import Image  # noqa: E402
import worldmap  # noqa: E402
from render_map import STEP_X, STEP_Y, render  # noqa: E402
from world import World  # noqa: E402
from atlas import markers, sprite  # noqa: E402

PAD = 24
# tiles of air to leave round a room that has no real border with anything
CLEAR = 3


def pack(w, at, portals):
    """Slide every stranded room against the body of the world.

    Tries the squares around what is already placed, nearest first, and
    keeps the first that leaves a clear gap all round. The gap matters: a
    room that cannot share a border with anything must not be drawn touching
    one, or the sheet claims a join that is not there. The Forge is reached
    through a portal, not a doorway, and should read as its own island.
    """
    if not portals:
        return at
    body = {l: o for l, o in at.items() if l not in portals}
    if not body:
        return at
    xs = [o[0] for o in body.values()]
    ys = [o[1] for o in body.values()]
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)
    for loc in sorted(portals, key=lambda l: -w.map(l).w * w.map(l).h):
        mp = w.map(loc)
        best = None
        lo_x = int(min(xs)) - mp.w - 4
        hi_x = int(max(o[0] + w.map(l).w for l, o in body.items())) + 4
        lo_y = int(min(ys)) - mp.h - 4
        hi_y = int(max(o[1] + w.map(l).h for l, o in body.items())) + 4
        for gy in range(lo_y, hi_y + 1, 2):
            for gx in range(lo_x, hi_x + 1, 2):
                # keep CLEAR tiles of air on every side, so a tucked room
                # is near the world without appearing to join it
                if any(worldmap._overlaps_placed(
                        w, body, loc, (gx + ox, gy + oy))
                        for ox in (-CLEAR, 0, CLEAR)
                        for oy in (-CLEAR, 0, CLEAR)):
                    continue
                d = (gx + mp.w / 2 - cx) ** 2 + (gy + mp.h / 2 - cy) ** 2
                if best is None or d < best[0]:
                    best = (d, (gx, gy))
        if best:
            at[loc] = best[1]
            body[loc] = best[1]
    return at


def main():
    game = sys.argv[1] if len(sys.argv) > 1 else "ShiradsForge"
    w = World(game)
    painted = w.reveal_all_patches()
    at, portals = worldmap.lay_out(w)
    at = pack(w, at, portals)

    imgs, trim = {}, {}
    for loc in w.locations:
        img = render(w, loc, annotate=False, bg=(0, 0, 0, 0))
        if not img:
            continue
        box = img.getbbox()
        if box:
            trim[loc] = (box[0], box[1])
            img = img.crop(box)
        imgs[loc] = img

    def place(loc):
        gx, gy = at[loc]
        ox = w.map(loc).h * STEP_X + worldmap.PAD
        tx, ty = trim.get(loc, (0, 0))
        return ((gx - gy) * STEP_X - ox + tx, (gx + gy) * STEP_Y - worldmap.PAD + ty)

    spots = {loc: place(loc) for loc in imgs}
    xs = [p[0] for p in spots.values()] + [p[0] + imgs[l].size[0]
                                           for l, p in spots.items()]
    ys = [p[1] for p in spots.values()] + [p[1] + imgs[l].size[1]
                                           for l, p in spots.items()]
    sheet = Image.new("RGBA",
                      (int(max(xs) - min(xs)) + PAD * 2,
                       int(max(ys) - min(ys)) + PAD * 2),
                      (8, 8, 12, 255))
    shift = (PAD - min(xs), PAD - min(ys))

    for loc in sorted(imgs, key=lambda l: sum(at[l])):
        x, y = spots[loc]
        sheet.alpha_composite(imgs[loc], (int(x + shift[0]), int(y + shift[1])))

    # the creatures, back to front across the whole sheet
    standing = []
    for loc in imgs:
        for (tx, ty), kind, creature in markers(w, loc):
            if kind in ("door", "spawn"):
                continue
            gx, gy = at[loc]
            standing.append((gx + tx + gy + ty, loc, tx, ty, kind, creature))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(sheet)
    for _, loc, tx, ty, kind, creature in sorted(standing):
        gx, gy = at[loc]
        cx = (gx + tx - gy - ty) * STEP_X + shift[0]
        cy = (gx + tx + gy + ty) * STEP_Y + shift[1] + STEP_Y
        if kind in ("crate", "barrel"):
            continue                       # already cut into the tilemap
        drawn = sprite(w, creature) if creature is not None else None
        if not drawn:
            continue
        img2, (ox2, oy2) = drawn
        if kind == "waiting":
            img2 = img2.copy()
            img2.putalpha(img2.getchannel("A").point(lambda v: v * 55 // 100))
        sheet.alpha_composite(img2, (int(cx + ox2), int(cy + oy2)))

    box = sheet.getbbox()
    out = os.path.join(ROOT, "assets", f"{game}-poster.png")
    sheet.save(out)
    print(f"{out}  {sheet.size[0]}x{sheet.size[1]}  "
          f"{len(imgs)} rooms, {len(portals)} tucked in, {painted} tiles revealed")


if __name__ == "__main__":
    main()
