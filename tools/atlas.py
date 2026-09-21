#!/usr/bin/env python3
"""Every location of a chapter on one sheet, joined at its doorways.

    python3 tools/atlas.py SterlingLake
    python3 tools/atlas.py ShiradsForge

Each location is drawn the way the handset drew it, then placed so that the
doorway it leaves by sits next to the doorway it arrives at, with a line
between the two. The result is the map of the chapter that the game never
showed you: it only ever rendered one location at a time.

One honest caveat. The tilemaps are real, straight out of the jar. Which
doorway leads where is NOT — that lived in the type 1 tables the server sent,
and those are gone. world.py reconstructs a plausible graph (see
_build_exits), so the shape of this atlas is ours and the pieces are
watAgame's.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "server"))
sys.path.insert(0, HERE)

from render_map import STEP_X, STEP_Y, render  # noqa: E402
from world import World  # noqa: E402

PAD = 64          # render_map's own margin; the tile origin sits inside it
GAP = 40          # clear space between two joined locations
OUT = os.path.join(os.path.dirname(HERE), "assets")


def font(size):
    """A readable label on a canvas thousands of pixels wide. PIL's built-in
    bitmap font is 11px and vanishes at this scale."""
    for path in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                 "/System/Library/Fonts/Supplemental/Arial.ttf",
                 "/Library/Fonts/Arial.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def tile_px(w, loc, x, y):
    """Where a tile lands inside that location's rendered image."""
    mp = w.map(loc)
    return (mp.h * STEP_X + PAD + (x - y) * STEP_X, PAD + (x + y) * STEP_Y)


def centre_px(w, loc):
    mp = w.map(loc)
    return tile_px(w, loc, mp.w // 2, mp.h // 2)


# What each marker means, and — the part that matters — whether the position
# is watAgame's or ours.
MARKERS = {
    "crate":  ((205, 160,  90), "crates and barrels, from the tilemap"),
    "barrel": ((205, 160,  90), None),
    "spawn":  ((250, 250, 250), "where the player arrives (reconstructed)"),
    "foe":    ((225,  80,  80), "creatures (reconstructed)"),
    "npc":    (( 90, 205, 225), "townsfolk (reconstructed)"),
}


def markers(w, loc):
    """Everything worth drawing on a location.

    Only the containers are real. Crates and barrels are cut into the tilemap
    itself — the obstacle nibble says which — so those squares are exactly
    where watAgame put them. Every creature and every arrival point is this
    server's invention, because the tables that held them were the ones the
    real server sent.
    """
    out = [((x, y), kind) for x, y, kind in w.containers(loc)]
    out.append((w.spawn_point(loc), "spawn"))
    if not any(m.location == loc for m in w.mobs.values()):
        w.populate_location(loc)
    for m in w.mobs.values():
        if m.location == loc:
            out.append(((m.x, m.y), "npc" if getattr(m, "label", None) else "foe"))
    return out


def way_back(w, loc, to):
    """The doorway in `loc` that leads to `to`, if it has one."""
    for tile, dest in w.EXITS.get(loc, []):
        if dest == to:
            return tile
    return None


def overlaps(box, placed, slack=24):
    ax1, ay1, ax2, ay2 = box
    for bx1, by1, bx2, by2 in placed:
        if (ax1 < bx2 - slack and bx1 < ax2 - slack
                and ay1 < by2 - slack and by1 < ay2 - slack):
            return True
    return False


def layout(w, imgs):
    """Breadth-first from the busiest location, pushing each neighbour out
    along the direction of the doorway that reaches it."""
    graph = {loc: list(w.EXITS.get(loc, [])) for loc in imgs}
    root = max(graph, key=lambda l: len(graph[l]))

    pos = {root: (0, 0)}
    boxes = [(0, 0) + imgs[root].size]
    edges = []
    queue = [root]
    seen = {root}

    while queue:
        loc = queue.pop(0)
        lx, ly = pos[loc]
        for tile, dest in graph.get(loc, []):
            if dest in seen or dest not in imgs:
                continue
            # the doorway we leave by, in world pixels
            dx, dy = tile_px(w, loc, *tile)
            door = (lx + dx, ly + dy)
            cx, cy = centre_px(w, loc)
            away = (dx - cx, dy - cy)
            norm = max(1.0, (away[0] ** 2 + away[1] ** 2) ** 0.5)
            step = (away[0] / norm, away[1] / norm)

            # the doorway we arrive at, inside the destination's own image
            back = way_back(w, dest, loc)
            ax, ay = (tile_px(w, dest, *back) if back
                      else centre_px(w, dest))

            img = imgs[dest]
            push = GAP
            while True:
                ox = door[0] + step[0] * push - ax
                oy = door[1] + step[1] * push - ay
                box = (ox, oy, ox + img.size[0], oy + img.size[1])
                if not overlaps(box, boxes) or push > 4000:
                    break
                push += 40

            pos[dest] = (ox, oy)
            boxes.append(box)
            edges.append((door, (ox + ax, oy + ay)))
            seen.add(dest)
            queue.append(dest)

    # The walk above is a spanning tree — it only follows an edge to a
    # location it has not placed yet. Every other doorway is a real link too,
    # so draw those as well once everything has a position.
    drawn = {(a, b) for a, b in
             [(min(e), max(e)) for e in
              [(tuple(x), tuple(y)) for x, y in edges]]}
    for loc in list(pos):
        lx, ly = pos[loc]
        for tile, dest in graph.get(loc, []):
            if dest not in pos:
                continue
            dx, dy = tile_px(w, loc, *tile)
            # the graph is not symmetric — a doorway can lead somewhere that
            # has no doorway back — so fall back to any doorway, then the
            # middle of the map
            back = way_back(w, dest, loc)
            if not back:
                others = [t for t, _ in graph.get(dest, [])]
                back = others[0] if others else None
            bx, by = (tile_px(w, dest, *back) if back else centre_px(w, dest))
            a = (lx + dx, ly + dy)
            b = (pos[dest][0] + bx, pos[dest][1] + by)
            key = (min(a, b), max(a, b))
            if key in drawn:
                continue
            drawn.add(key)
            edges.append((a, b))

    # anything the graph never reaches still deserves to be on the sheet
    far_right = max((b[2] for b in boxes), default=0)
    stray_y = 0
    for loc in imgs:
        if loc not in pos:
            pos[loc] = (far_right + GAP, stray_y)
            stray_y += imgs[loc].size[1] + GAP
    return pos, edges, root, seen


def main():
    game = sys.argv[1] if len(sys.argv) > 1 else "SterlingLake"
    w = World(game)

    imgs = {}
    for loc in w.locations:
        img = render(w, loc, annotate=False, bg=(0, 0, 0, 0))
        if img:
            imgs[loc] = img
    if not imgs:
        print("no maps")
        return 1

    pos, edges, root, reached = layout(w, imgs)
    # the right-hand column is whatever the walk never reached: the
    # reconstructed graph simply gives these no way in
    stray = [l for l in imgs if l not in reached]

    xs = [pos[l][0] for l in imgs] + [pos[l][0] + imgs[l].size[0] for l in imgs]
    ys = [pos[l][1] for l in imgs] + [pos[l][1] + imgs[l].size[1] for l in imgs]
    margin = 60
    width = int(max(xs) - min(xs)) + margin * 2
    height = int(max(ys) - min(ys)) + margin * 2
    shift = (margin - min(xs), margin - min(ys))

    sheet = Image.new("RGBA", (width, height), (8, 8, 12, 255))
    for loc, img in imgs.items():
        x, y = pos[loc]
        sheet.alpha_composite(img, (int(x + shift[0]), int(y + shift[1])))

    draw = ImageDraw.Draw(sheet)

    for loc in imgs:
        x, y = pos[loc]
        for (tx, ty), kind in markers(w, loc):
            px, py = tile_px(w, loc, tx, ty)
            px += x + shift[0]
            py += y + shift[1] + STEP_Y   # sit on the tile, not above it
            colour = MARKERS[kind][0] + (255,)
            if kind in ("crate", "barrel"):
                draw.rectangle([px - 5, py - 5, px + 5, py + 5],
                               outline=colour, width=3)
            elif kind == "spawn":
                draw.ellipse([px - 8, py - 8, px + 8, py + 8],
                             outline=colour, width=3)
            else:
                draw.ellipse([px - 6, py - 6, px + 6, py + 6], fill=colour,
                             outline=(0, 0, 0, 255))

    for (ax, ay), (bx, by) in edges:
        draw.line([(ax + shift[0], ay + shift[1]),
                   (bx + shift[0], by + shift[1])],
                  fill=(255, 210, 90, 220), width=3)
        for px, py in ((ax, ay), (bx, by)):
            draw.ellipse([px + shift[0] - 5, py + shift[1] - 5,
                          px + shift[0] + 5, py + shift[1] + 5],
                         fill=(255, 210, 90, 255))

    label_font, title_font = font(30), font(46)
    for loc, img in imgs.items():
        x, y = pos[loc]
        cx, _ = centre_px(w, loc)
        label = f"{loc}  {w.name(loc)}"
        tx = x + shift[0] + cx - draw.textlength(label, font=label_font) / 2
        ty = y + shift[1] + 14
        draw.text((tx + 2, ty + 2), label, font=label_font, fill=(0, 0, 0, 255))
        draw.text((tx, ty), label, font=label_font,
                  fill=(255, 235, 140, 255) if loc == root
                  else (235, 235, 245, 255))

    title = f"{game} - {len(imgs)} locations, {len(edges)} doorways"
    draw.text((margin + 2, 22), title, font=title_font, fill=(0, 0, 0, 255))
    draw.text((margin, 20), title, font=title_font, fill=(245, 245, 250, 255))
    note = ("tilemaps from the jar; which doorway leads where is "
            "reconstructed, not original")
    draw.text((margin, 20 + 56), note, font=label_font, fill=(150, 150, 165, 255))
    legend_y = 20 + 56 + 38
    for kind, (colour, caption) in MARKERS.items():
        if not caption:
            continue
        draw.ellipse([margin + 4, legend_y + 8, margin + 18, legend_y + 22],
                     fill=colour + (255,))
        draw.text((margin + 30, legend_y + 4), caption, font=label_font,
                  fill=(190, 190, 205, 255))
        legend_y += 34

    if stray:
        draw.text((margin, legend_y + 6),
                  f"right-hand column: {len(stray)} locations the "
                  f"reconstructed graph gives no way into",
                  font=label_font, fill=(150, 150, 165, 255))

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{game}-atlas.png")
    sheet.convert("RGB").save(path)
    print(f"{path}  {width}x{height}  "
          f"{len(imgs)} locations, {len(edges)} joins")
    return 0


if __name__ == "__main__":
    sys.exit(main())
