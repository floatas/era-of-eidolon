#!/usr/bin/env python3
"""The chapter as one continuous plane.

    python3 tools/worldmap.py ShiradsForge

Most doorways are on a map's edge, and the doorway that answers them is on
the opposite edge of the next map — the Village's western door at (0,19)
meets Dune Burrow's eastern one at (11,3). So the locations are not a graph
of separate boards at all. They are tiles of one world, and if you place each
one so its doorway meets its partner's, the whole chapter lays out flat.

What does not lay out flat is a portal: a doorway in the middle of a map, or
two doorways on the same side, which cannot be a shared border. The Forge is
reached that way, and so is Aldor's Outpost. Those are drawn where they fit
and joined with a line.

Only Shirad's Forge has the real table (notes/recovered), so only Shirad's
Forge can be trusted here; the others are laid out from the reconstruction.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "server"))
sys.path.insert(0, HERE)

from render_map import STEP_X, STEP_Y, render  # noqa: E402
from world import World  # noqa: E402

PAD = 64
OUT = os.path.join(os.path.dirname(HERE), "assets")
STEP = {"N": (0, -1), "S": (0, 1), "W": (-1, 0), "E": (1, 0)}
OPPOSITE = {"N": "S", "S": "N", "W": "E", "E": "W"}


def edge(mp, x, y, slack=2):
    """Which side of its map a doorway sits on, if any."""
    sides = []
    if x <= slack:
        sides.append("W")
    if x >= mp.w - 1 - slack:
        sides.append("E")
    if y <= slack:
        sides.append("N")
    if y >= mp.h - 1 - slack:
        sides.append("S")
    return sides


ARCH = 2          # the obstacle the artist draws where a doorway teleports


def is_arch(w, loc, x, y):
    return ((w.map(loc).tile(x, y) & 240) >> 4) == ARCH


def seams(w):
    """Links that are a shared border rather than a portal.

    watAgame marked the two cases differently, and the art says which is
    which. A border carries the red marker tile on at least one side. A
    portal carries obstacle 2 — the stone arch — on BOTH sides: all five of
    Shirad's Forge's portals do, and not one of its fifteen borders does.

    Edge geometry agrees with that and is used as the second test, since a
    border has to be a shared edge to be laid out flat at all.
    """
    out = []
    for a, links in w.EXITS.items():
        for ta, b in links:
            back = [tb for tb, dest in w.EXITS.get(b, []) if dest == a]
            if not back:
                continue
            tb = back[0]
            if is_arch(w, a, *ta) or is_arch(w, b, *tb):
                continue                        # an arch is a teleport
            for sa in edge(w.map(a), *ta):
                if OPPOSITE[sa] in edge(w.map(b), *tb):
                    out.append((a, ta, b, tb, sa))
                    break
    return out


def lay_out(w):
    """Place every location on one tile grid, following the seams."""
    joins = {}
    for a, ta, b, tb, side in seams(w):
        joins.setdefault(a, []).append((ta, b, tb, side))

    def spread(at, queue):
        """Tile outwards from everything in the queue, following borders."""
        while queue:
            a = queue.pop(0)
            ax0, ay0 = at[a]
            for (ax, ay), b, (bx, by), side in joins.get(a, []):
                if b in at:
                    continue
                # the two doorways are the same border seen from either side,
                # so B's sits exactly one step beyond A's:
                #     at[B] + (bx,by) == at[A] + (ax,ay) + step
                dx, dy = STEP[side]
                at[b] = (ax0 + ax - bx + dx, ay0 + ay - by + dy)
                queue.append(b)

    start = w.locations[0]
    at = {start: (0, 0)}
    spread(at, [start])

    # Whatever the borders never reach lies through an arch. Give it its own
    # patch of ground and then keep tiling from there — Golem Secret shares a
    # real border with The Forge, and only looked stranded because The Forge
    # itself is behind a portal.
    portals = []
    while True:
        left = [l for l in w.locations if l not in at]
        if not left:
            break
        far = max((x + w.map(l).w + 8 for l, (x, _) in at.items()), default=0)
        low = min((y for _, (_, y) in at.items()), default=0)
        seed = left[0]
        at[seed] = (far, low)
        portals.append(seed)
        spread(at, [seed])
    return at, portals


def marker_strip(w, fade=0.6):
    """The chapter's red doorway tile, faded, for annotating the doorways
    watAgame left bare."""
    import io
    import re
    ids = [int(n[1:] or "0", 16) for n in w.res.files
           if re.fullmatch(r"4[0-9a-f]*", n)]
    if not ids:
        return None
    sheet = Image.open(io.BytesIO(w.res.get(4, ids[0]))).convert("RGBA")
    strip = sheet.crop((0, (w.marker - 1) * 15, 32, w.marker * 15)).copy()
    strip.putalpha(strip.getchannel("A").point(lambda a: int(a * fade)))
    return strip


def font(size):
    for p in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/System/Library/Fonts/Supplemental/Arial.ttf"):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    game = sys.argv[1] if len(sys.argv) > 1 else "ShiradsForge"
    w = World(game)
    at, portals = lay_out(w)

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
        """Where a location's image goes, in world pixels."""
        gx, gy = at[loc]
        ox = w.map(loc).h * STEP_X + PAD
        tx, ty = trim.get(loc, (0, 0))
        return ((gx - gy) * STEP_X - ox + tx, (gx + gy) * STEP_Y - PAD + ty)

    spots = {loc: place(loc) for loc in imgs}
    xs = [p[0] for p in spots.values()] + [p[0] + imgs[l].size[0]
                                           for l, p in spots.items()]
    ys = [p[1] for p in spots.values()] + [p[1] + imgs[l].size[1]
                                           for l, p in spots.items()]
    margin, top = 80, 300
    sheet = Image.new("RGBA",
                      (int(max(xs) - min(xs)) + margin * 2,
                       int(max(ys) - min(ys)) + margin + top),
                      (8, 8, 12, 255))
    shift = (margin - min(xs), top - min(ys))

    # far to near, so a map in front overlaps the one behind it correctly
    for loc in sorted(imgs, key=lambda l: sum(at[l])):
        x, y = spots[loc]
        sheet.alpha_composite(imgs[loc], (int(x + shift[0]), int(y + shift[1])))

    draw = ImageDraw.Draw(sheet)

    def px(loc, tx, ty):
        gx, gy = at[loc]
        return ((gx + tx - gy - ty) * STEP_X + shift[0],
                (gx + tx + gy + ty) * STEP_Y + shift[1])

    # Every doorway, marked. Half of watAgame's carry the red tile and half
    # are bare ground you would only find by walking into it, so the bare
    # ones are annotated here — on the map, not in the game.
    tile = marker_strip(w)
    for loc in imgs:
        for (tx, ty), _dest in w.EXITS.get(loc, []):
            cx, cy = px(loc, tx, ty)
            if is_arch(w, loc, tx, ty):
                draw.ellipse([cx - 12, cy - 8, cx + 12, cy + 8],
                             outline=(205, 155, 255, 255), width=3)
            elif (w.map(loc).tile(tx, ty) & 15) != w.marker and tile:
                sheet.alpha_composite(tile, (int(cx) - 16, int(cy) - 7))

    joined = {(min(a, b), max(a, b)) for a, _, b, _, _ in seams(w)}
    for a, links in w.EXITS.items():
        for ta, b in links:
            if (min(a, b), max(a, b)) in joined or b not in at or a not in at:
                continue
            back = [tb for tb, d in w.EXITS.get(b, []) if d == a]
            if not back:
                continue
            p, q = px(a, *ta), px(b, *back[0])
            draw.line([p, q], fill=(180, 120, 255, 200), width=3)
            for c in (p, q):
                draw.ellipse([c[0] - 6, c[1] - 6, c[0] + 6, c[1] + 6],
                             fill=(200, 150, 255, 255))

    label, title = font(26), font(46)
    for loc in imgs:
        mp = w.map(loc)
        c = px(loc, mp.w // 2, mp.h // 2)
        text = f"{loc}  {w.name(loc)}"
        tx = c[0] - draw.textlength(text, font=label) / 2
        draw.text((tx + 2, c[1] + 2), text, font=label, fill=(0, 0, 0, 255))
        draw.text((tx, c[1]), text, font=label, fill=(255, 245, 190, 255))

    real = getattr(w, "real1", None)
    head = f"{game} - one continuous world"
    draw.text((margin + 2, 22), head, font=title, fill=(0, 0, 0, 255))
    draw.text((margin, 20), head, font=title, fill=(245, 245, 250, 255))
    sub = (f"{len(seams(w))//2} shared borders laid out flat. A purple ring "
           f"is a stone arch, which teleports; its partner is on the other "
           f"end of the purple line. Faded red tiles are doorways watAgame "
           f"left unmarked.")
    draw.text((margin, 78), sub, font=label, fill=(160, 160, 180, 255))
    draw.text((margin, 112),
              "doorways and placement are watAgame's" if real
              else "doorways are reconstructed, so this layout is a guess",
              font=label, fill=(160, 160, 180, 255))

    path = os.path.join(OUT, f"{game}-world.png")
    sheet.convert("RGB").save(path)
    print(f"{path}  {sheet.size[0]}x{sheet.size[1]}  "
          f"{len(imgs)} locations, {len(seams(w))//2} seams, "
          f"{len(portals)} behind portals")
    return 0


if __name__ == "__main__":
    sys.exit(main())
