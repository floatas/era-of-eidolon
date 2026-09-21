#!/usr/bin/env python3
"""Render a location's tilemap to a PNG, the way the game draws it.

Transcribed from d.java's own draw loop, so what comes out should match what
the handset showed:

    ground    tile & 15, index-1 into the type 4 id 0 sheet, 32x15 strips
              (d.java:415). 0 means nothing at all — void.
    obstacle  (tile & 240) >> 4. 0 is bare ground, 1 is an exit tile, and 2+
              indexes the 8-bytes-per-entry rect table in type 6 id 2 into the
              obstacle sheet in type 5 id 2 (d.java:551)
    position  screenX = (x - y) * 16,  screenY = (x + y) * 8

Usage:
    python3 tools/render_map.py                      every location
    python3 tools/render_map.py ShiradsForge 1       just the Village
"""

import io
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "server"))

from world import World  # noqa: E402

TILE_W, TILE_H = 32, 15
STEP_X, STEP_Y = 16, 8
OUT = os.path.join(os.path.dirname(HERE), "assets", "maps")


def render(w, loc, annotate=True):
    mp = w.map(loc)
    if not mp:
        return None
    # Shirad's Forge hardcodes (4,0), (5,2), (6,2); Sterling Lake's build uses
    # (4,1), (5,0x30), (6,0x30). Each chapter has exactly one of each, so find
    # them rather than assuming.
    def only(restype):
        import re
        ids = [int(n[len(str(restype)):] or "0", 16) for n in w.res.files
               if re.fullmatch(rf"{restype}[0-9a-f]*", n)]
        return w.res.get(restype, ids[0]) if ids else None

    ground = Image.open(io.BytesIO(only(4))).convert("RGBA")
    obs_sheet = only(5)
    obs = Image.open(io.BytesIO(obs_sheet)).convert("RGBA") if obs_sheet else None
    table = only(6) or b""

    # the whole diamond, plus room for tall obstacles hanging above their tile
    pad = 64
    width = (mp.w + mp.h) * STEP_X + pad * 2
    height = (mp.w + mp.h) * STEP_Y + pad * 2
    ox = mp.h * STEP_X + pad
    oy = pad

    img = Image.new("RGBA", (width, height), (10, 10, 16, 255))

    def screen(x, y):
        return (ox + (x - y) * STEP_X - TILE_W // 2,
                oy + (x + y) * STEP_Y - TILE_H // 2)

    # Painter's order: back to front, or tall obstacles overlap wrongly.
    order = sorted(((x, y) for y in range(mp.h) for x in range(mp.w)),
                   key=lambda p: p[0] + p[1])

    for x, y in order:
        t = mp.tile(x, y)
        low = t & 15
        if not low:
            continue                       # void
        sx, sy = screen(x, y)
        img.paste(ground.crop((0, (low - 1) * TILE_H, TILE_W, low * TILE_H)),
                  (sx, sy), ground.crop((0, (low - 1) * TILE_H,
                                         TILE_W, low * TILE_H)))

    for x, y in order:
        idx = mp.obstacle(x, y)
        if idx < 2 or obs is None:
            continue
        o = (idx - 2) * 8
        if o + 8 > len(table):
            continue
        ow, oh = table[o], table[o + 1]
        sxr = int.from_bytes(table[o + 2:o + 4], "big", signed=True)
        syr = int.from_bytes(table[o + 4:o + 6], "big", signed=True)
        dx = int.from_bytes(table[o + 6:o + 7], "big", signed=True)
        dy = int.from_bytes(table[o + 7:o + 8], "big", signed=True)
        if ow <= 0 or oh <= 0:
            continue
        spr = obs.crop((sxr, syr, min(obs.width, sxr + ow),
                        min(obs.height, syr + oh)))
        sx, sy = screen(x, y)
        img.paste(spr, (sx + dx, sy + dy), spr)

    if annotate:
        d = ImageDraw.Draw(img)
        for x, y in order:
            if mp.is_exit(x, y):
                sx, sy = screen(x, y)
                d.ellipse((sx + 8, sy + 2, sx + 24, sy + 14),
                          outline=(80, 255, 80, 255), width=2)
        for m in w.mobs.values():
            if m.location != loc:
                continue
            sx, sy = screen(m.x, m.y)
            colour = (120, 200, 255, 255) if m.npc else (255, 90, 90, 255)
            d.ellipse((sx + 10, sy + 2, sx + 22, sy + 14), fill=colour)
        hx, hy = w.spawn_point(loc)
        sx, sy = screen(hx, hy)
        d.ellipse((sx + 8, sy, sx + 24, sy + 16), outline=(255, 230, 80, 255),
                  width=3)

    return img


def main():
    game = sys.argv[1] if len(sys.argv) > 1 else "ShiradsForge"
    w = World(game)
    w.entity_table()                      # so NPCs exist for the overlay
    only = int(sys.argv[2]) if len(sys.argv) > 2 else None
    os.makedirs(OUT, exist_ok=True)
    for loc in w.locations:
        if only is not None and loc != only:
            continue
        img = render(w, loc)
        if img is None:
            continue
        name = w.name(loc).replace("/", "-").replace("'", "")
        path = os.path.join(OUT, f"{game}-{loc:02x}-{name}.png")
        img.save(path)
        print(f"  {name:18} {w.map(loc).w:>2}x{w.map(loc).h:<2} -> {path}")


if __name__ == "__main__":
    main()
