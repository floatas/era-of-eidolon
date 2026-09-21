#!/usr/bin/env python3
"""Pull the art out of the jars and show it moving.

    python3 tools/showcase.py              both chapters
    python3 tools/showcase.py ShiradsForge

Writes to assets/showcase/. Nothing here is reconstruction — every pixel and
every frame timing comes out of the jar. It is the game's own art, played
back outside the game.

    walk/        one GIF per creature, walking a circle on a bare floor
    sheets/      contact sheets: creatures, ground, obstacles, interface
"""

import io
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "server"))
sys.path.insert(0, HERE)

from world import World  # noqa: E402

TILE_W, TILE_H = 32, 15
STEP_X, STEP_Y = 16, 8
OUT = os.path.join(os.path.dirname(HERE), "assets", "showcase")

# Animation sets come in pairs: N faces the camera, N+64 faces away, and bit 7
# mirrors either one left-to-right (j.java reads `e & 127` for the script and
# `e & 128` for the flip). Four facings out of one set of art.
AWAY, MIRROR = 64, 128

# The client's own table, from the exploration key handler (d.java:1530-1570).
# It is the only place the game names an animation, and it names walk:
#
#     LEFT  x-1 -> 14          RIGHT x+1 -> 78 | 128
#     UP    y-1 -> 14 | 128    DOWN  y+1 -> 78
FACING = {
    (-1, 0): (0, 0),            # west:  base set, as drawn
    (1, 0):  (AWAY, MIRROR),    # east:  away set, flipped
    (0, -1): (0, MIRROR),       # north: base set, flipped
    (0, 1):  (AWAY, 0),         # south: away set, as drawn
}


def i8(b):
    return b - 256 if b > 127 else b


def only(w, restype):
    """The chapter's single resource of a type, whatever id it filed it under."""
    import re
    ids = [int(n[len(str(restype)):] or "0", 16) for n in w.res.files
           if re.fullmatch(rf"{restype}[0-9a-f]*", n)]
    return w.res.get(restype, ids[0]) if ids else None


def frames(w, creature, anim):
    """Every frame of an animation, as (image, (ox, oy), milliseconds).

    The script is a run of groups: a duration, a part count, then that many
    (dx, dy, frame) triples. Each part is an 8-byte rect in the type 8 table —
    size, where it sits in the type 7 sheet, and its own offset — so one frame
    is several pieces stacked. Duration is in sixteenths of a second.
    """
    sheet_raw = w.res.get(7, creature)
    table = w.res.get(8, creature) or b""
    script = w.res.props(11, creature).get(anim & 127) or b""
    if not sheet_raw or len(script) < 3:
        return []
    sheet = Image.open(io.BytesIO(sheet_raw)).convert("RGBA")
    mirror = bool(anim & 128)

    out, q = [], 1
    while q + 1 < len(script):
        millis = (script[q] & 255) << 4
        count = script[q + 1]
        parts = []
        for n in range(count):
            p = q + 2 + n * 3
            if p + 2 >= len(script):
                break
            dx, dy, frame = i8(script[p]), i8(script[p + 1]), script[p + 2]
            o = frame * 8
            if o + 8 > len(table):
                continue
            pw, ph = table[o], table[o + 1]
            sx = int.from_bytes(table[o + 2:o + 4], "big", signed=True)
            sy = int.from_bytes(table[o + 4:o + 6], "big", signed=True)
            if pw <= 0 or ph <= 0:
                continue
            parts.append((dx + i8(table[o + 6]), dy + i8(table[o + 7]),
                          sheet.crop((sx, sy, sx + pw, sy + ph))))
        if parts:
            x0 = min(p[0] for p in parts)
            y0 = min(p[1] for p in parts)
            x1 = max(p[0] + p[2].width for p in parts)
            y1 = max(p[1] + p[2].height for p in parts)
            img = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
            for px, py, piece in parts:
                img.alpha_composite(piece, (px - x0, py - y0))
            if mirror:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
                x0 = -x1
            out.append((img, (x0, y0), max(40, millis)))
        nxt = q + 2 + count * 3
        if nxt <= q or nxt >= len(script):
            break
        q = nxt
    return out


def floor(w, side=9, ground=None):
    """A bare patch of ground, `side` tiles square, drawn isometrically."""
    sheet = Image.open(io.BytesIO(only(w, 4))).convert("RGBA")
    if ground is None:
        # whichever ground the chapter uses most, so the floor looks native
        counts = {}
        for loc in w.locations:
            mp = w.map(loc)
            if mp:
                for t in mp.tiles:
                    low = t & 15
                    if low:
                        counts[low] = counts.get(low, 0) + 1
        ground = max(counts, key=counts.get) if counts else 1

    pad = 90
    width = side * 2 * STEP_X + pad * 2
    height = side * 2 * STEP_Y + pad * 2 + 40
    ox, oy = side * STEP_X + pad, pad
    img = Image.new("RGBA", (width, height), (14, 14, 20, 255))
    strip = sheet.crop((0, (ground - 1) * TILE_H, TILE_W, ground * TILE_H))
    for y in range(side):
        for x in range(side):
            sx = ox + (x - y) * STEP_X - TILE_W // 2
            sy = oy + (x + y) * STEP_Y - TILE_H // 2
            img.paste(strip, (sx, sy), strip)
    return img, (ox, oy)


def ring(side=9, radius=3):
    """A circle of tiles to walk, centred on the floor."""
    import math
    mid = side // 2
    path = []
    for n in range(24):
        a = 2 * math.pi * n / 24
        path.append((mid + radius * math.cos(a), mid + radius * math.sin(a)))
    return path


def walk_gif(w, creature, path_out, side=9, scale=2):
    """A creature walking a circle, turning to face the way it is going."""
    have = set(w.res.props(11, creature))
    move = 14 if 14 in have else (1 if 1 in have else None)
    if move is None:
        return False

    board, (ox, oy) = floor(w, side)
    spots = ring(side)

    cycles = {}
    for (dx, dy), (away, mirror) in FACING.items():
        if (move + away) in have:
            cycles[(dx, dy)] = frames(w, creature, move + away + mirror)
    if not any(cycles.values()):
        return False

    out, durations, step = [], [], 0
    for n, (fx, fy) in enumerate(spots):
        nx, ny = spots[(n + 1) % len(spots)]
        dx, dy = nx - fx, ny - fy
        # one axis at a time, the way a player holds one key
        face = (0 if abs(dx) < abs(dy) else (1 if dx > 0 else -1),
                0 if abs(dy) <= abs(dx) else (1 if dy > 0 else -1))
        cycle = cycles.get(face) or next(c for c in cycles.values() if c)

        img, (fox, foy), millis = cycle[step % len(cycle)]
        step += 1
        frame = board.copy()
        px = ox + int((fx - fy) * STEP_X)
        py = oy + int((fx + fy) * STEP_Y)
        frame.alpha_composite(img, (px + fox, py + foy))
        if scale != 1:
            frame = frame.resize((frame.width * scale, frame.height * scale),
                                 Image.NEAREST)
        out.append(frame.convert("P", palette=Image.ADAPTIVE))
        durations.append(millis)

    os.makedirs(os.path.dirname(path_out), exist_ok=True)
    out[0].save(path_out, save_all=True, append_images=out[1:],
                duration=durations, loop=0, optimize=True)
    return True


def moves_sheet(w, creature, path_out, scale=2):
    """Every animation a creature has, frame by frame, named.

    This is the sheet the animation map was read off: 2 is not a second idle,
    it is the creature arriving in a burst of fire, and 6 is it falling over
    dead. Nothing in the jar says so — you have to look.
    """
    anims = [a for a in sorted(w.res.props(11, creature)) if a < AWAY]
    if not anims:
        return False
    strips = [(a, frames(w, creature, a)) for a in anims]
    strips = [(a, f) for a, f in strips if f]
    if not strips:
        return False

    cell = max(max(i.width for i, _, _ in f) for _, f in strips) * scale + 18
    high = max(max(i.height for i, _, _ in f) for _, f in strips) * scale + 26
    cols = max(len(f) for _, f in strips)
    label, name = font(13), font(15)
    img = Image.new("RGBA", (150 + cols * cell, len(strips) * high + 10),
                    (16, 16, 22, 255))
    d = ImageDraw.Draw(img)
    for r, (a, fs) in enumerate(strips):
        y = 8 + r * high
        d.text((8, y + high // 2 - 16), f"{a}", font=name,
               fill=(235, 235, 245, 255))
        d.text((38, y + high // 2 - 14), w.ANIM_NAMES.get(a, "?"), font=label,
               fill=(150, 150, 170, 255))
        for c, (spr, (sx, sy), ms) in enumerate(fs):
            big = spr.resize((spr.width * scale, spr.height * scale),
                             Image.NEAREST)
            img.alpha_composite(big, (150 + c * cell + (cell - big.width) // 2,
                                      y + high - 22 - big.height))
            d.text((150 + c * cell + 4, y + high - 20), f"{ms}ms", font=label,
                   fill=(100, 100, 120, 255))
    img.convert("RGB").save(path_out)
    return True


def font(size):
    for p in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/System/Library/Fonts/Supplemental/Arial.ttf"):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def creature_sheet(w, path_out):
    """Every creature, every animation it has, first frame of each."""
    cell, label = 72, font(13)
    ids = list(w.creatures)
    cols = max(len(w.res.props(11, c)) for c in ids) + 1
    img = Image.new("RGBA", (cols * cell + 40, len(ids) * cell + 30),
                    (16, 16, 22, 255))
    d = ImageDraw.Draw(img)
    for r, c in enumerate(ids):
        d.text((6, r * cell + cell // 2), f"{c:#04x}", font=label,
               fill=(220, 220, 230, 255))
        for n, a in enumerate(sorted(w.res.props(11, c))):
            fs = frames(w, c, a)
            if not fs:
                continue
            spr, (sx, sy), _ = fs[0]
            img.alpha_composite(spr, (40 + n * cell + cell // 2 + sx,
                                      r * cell + cell - 12 + sy))
            d.text((40 + n * cell + 4, r * cell + cell - 12), str(a),
                   font=label, fill=(120, 120, 140, 255))
    img.convert("RGB").save(path_out)


def ground_sheet(w, path_out):
    """The chapter's ground palette, as 32x15 strips in one column."""
    sheet = Image.open(io.BytesIO(only(w, 4))).convert("RGBA")
    n = sheet.height // TILE_H
    scale = 3
    img = Image.new("RGBA", (TILE_W * scale + 60, n * (TILE_H * scale + 6) + 10),
                    (16, 16, 22, 255))
    d, label = ImageDraw.Draw(img), font(13)
    for i in range(n):
        strip = sheet.crop((0, i * TILE_H, TILE_W, (i + 1) * TILE_H))
        strip = strip.resize((TILE_W * scale, TILE_H * scale), Image.NEAREST)
        y = 6 + i * (TILE_H * scale + 6)
        img.alpha_composite(strip, (50, y))
        d.text((8, y + 10), str(i + 1), font=label, fill=(200, 200, 215, 255))
    img.convert("RGB").save(path_out)


def obstacle_sheet(w, path_out):
    """Every rock, tree, crate and barrel, from the type 5 sheet and the
    8-bytes-per-entry rect table in type 6."""
    raw, table = only(w, 5), only(w, 6) or b""
    if not raw:
        return
    sheet = Image.open(io.BytesIO(raw)).convert("RGBA")
    items = []
    for i in range(len(table) // 8):
        o = i * 8
        pw, ph = table[o], table[o + 1]
        sx = int.from_bytes(table[o + 2:o + 4], "big", signed=True)
        sy = int.from_bytes(table[o + 4:o + 6], "big", signed=True)
        if pw > 0 and ph > 0:
            items.append((i + 2, sheet.crop((sx, sy, sx + pw, sy + ph))))
    if not items:
        return
    cell = max(max(p.width for _, p in items), max(p.height for _, p in items)) + 16
    cols = 8
    rows = (len(items) + cols - 1) // cols
    img = Image.new("RGBA", (cols * cell, rows * cell + 16), (16, 16, 22, 255))
    d, label = ImageDraw.Draw(img), font(12)
    for n, (idx, piece) in enumerate(items):
        cx, cy = (n % cols) * cell, (n // cols) * cell
        img.alpha_composite(piece, (cx + (cell - piece.width) // 2,
                                    cy + cell - 14 - piece.height))
        d.text((cx + 4, cy + cell - 13), str(idx), font=label,
               fill=(130, 130, 150, 255))
    img.convert("RGB").save(path_out)


def interface_sheet(w, path_out):
    """The chrome: panels, menu, item icons, the splash."""
    names = ["splash.png", "menu.png", "cpanel.png", "fpanel.png",
             "items.png", "symb.png", "icon.png"]
    shots = []
    for n in names:
        raw = w.res.get_file(n) if hasattr(w.res, "get_file") else None
        if raw is None:
            raw = w.res.files.get(n)
        if raw:
            shots.append((n, Image.open(io.BytesIO(raw)).convert("RGBA")))
    if not shots:
        return
    width = max(s.width for _, s in shots) + 140
    height = sum(s.height + 24 for _, s in shots) + 12
    img = Image.new("RGBA", (width, height), (16, 16, 22, 255))
    d, label = ImageDraw.Draw(img), font(14)
    y = 8
    for name, s in shots:
        img.alpha_composite(s, (130, y))
        d.text((8, y + 4), name, font=label, fill=(210, 210, 225, 255))
        y += s.height + 24
    img.convert("RGB").save(path_out)


def main():
    games = sys.argv[1:] or ["ShiradsForge", "SterlingLake"]
    for game in games:
        w = World(game)
        made = 0
        moves = 0
        for c in [0] + list(w.creatures):
            name = "hero" if c == 0 else f"{c:#04x}"
            if walk_gif(w, c, os.path.join(OUT, "walk",
                                           f"{game}-{name}.gif")):
                made += 1
            os.makedirs(os.path.join(OUT, "moves"), exist_ok=True)
            if moves_sheet(w, c, os.path.join(OUT, "moves",
                                              f"{game}-{name}.png")):
                moves += 1
        sheets = os.path.join(OUT, "sheets")
        os.makedirs(sheets, exist_ok=True)
        creature_sheet(w, os.path.join(sheets, f"{game}-creatures.png"))
        ground_sheet(w, os.path.join(sheets, f"{game}-ground.png"))
        obstacle_sheet(w, os.path.join(sheets, f"{game}-obstacles.png"))
        interface_sheet(w, os.path.join(sheets, f"{game}-interface.png"))
        print(f"{game}: {made} walk cycles, {moves} move sheets, "
              f"4 reference sheets -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
