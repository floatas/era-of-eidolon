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
reached that way. Those are drawn where they fit and joined with a line.

Only Shirad's Forge has the real table (notes/recovered), so only Shirad's
Forge can be trusted here; the others are laid out from the reconstruction.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "server"))
sys.path.insert(0, HERE)

from atlas import markers, sprite  # noqa: E402
from iso import STEP_X, STEP_Y  # noqa: E402
from render_map import render  # noqa: E402
from world import World  # noqa: E402

PAD = 64
OUT = os.path.join(os.path.dirname(HERE), "assets")
STEP = {"N": (0, -1), "S": (0, 1), "W": (-1, 0), "E": (1, 0)}
OPPOSITE = {"N": "S", "S": "N", "W": "E", "E": "W"}


def edge(mp, x, y):
    """Which side of its map a doorway sits on, if any.

    Only the last tile of a side counts. A door flush with one side and a
    couple of tiles in from another is just that one side — calling it both
    glued Aldor's west door onto Fire Cave's south edge.
    """
    sides = []
    if x == 0:
        sides.append("W")
    if x == mp.w - 1:
        sides.append("E")
    if y == 0:
        sides.append("N")
    if y == mp.h - 1:
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


def _ground(w, loc, origin):
    """World tiles this map actually draws, given where its (0, 0) sits."""
    gx, gy = origin
    mp = w.map(loc)
    out = set()
    for y in range(mp.h):
        for x in range(mp.w):
            if mp.tile(x, y) & 15:
                out.add((gx + x, gy + y))
    return out


def _overlaps_placed(w, at, loc, origin):
    """True when this placement would paint over ground already laid down."""
    tiles = _ground(w, loc, origin)
    for other, oorigin in at.items():
        if tiles & _ground(w, other, oorigin):
            return True
    return False


def lay_out(w):
    """Place every location on one tile grid, following the seams.

    The route the chapter states out loud is laid first — the Lair really
    is east of Mira's Hideout — and a later border is kept only when its
    ground does not cover a room already placed. Fire Cave's door in the
    east wall of Dwarven Hall is real, but honouring it as a shared edge
    sets Fire Cave and Ilrik's Tomb down on top of The Lair. They are drawn
    as their own patch instead, and the door is marked as a portal.
    """
    joins = {}
    for a, ta, b, tb, side in seams(w):
        joins.setdefault(a, []).append((ta, b, tb, side))

    story = set()
    for a, b in w.story_links():
        story.add((a, b))
        story.add((b, a))

    def spread(at, queue, only_story):
        """Tile outwards. Never onto ground that is already occupied."""
        while queue:
            a = queue.pop(0)
            pending = []
            order = sorted(joins.get(a, []),
                           key=lambda j: (0 if (a, j[1]) in story else 1, j[1]))
            for (ax, ay), b, (bx, by), side in order:
                if b in at:
                    continue
                if only_story and (a, b) not in story:
                    continue
                # the two doorways are the same border seen from either side,
                # so B sits exactly one step beyond A:
                #     at[B] + (bx, by) == at[A] + (ax, ay) + step
                ax0, ay0 = at[a]
                dx, dy = STEP[side]
                origin = (ax0 + ax - bx + dx, ay0 + ay - by + dy)
                if _overlaps_placed(w, at, b, origin):
                    continue
                at[b] = origin
                pending.append(b)
            queue.extend(pending)

    start = w.locations[0]
    at = {start: (0, 0)}
    spread(at, [start], only_story=True)
    spread(at, list(at), only_story=False)

    # Whatever the borders never reach, or could not be laid flat without
    # covering another room, gets its own patch. Golem Secret shares a real
    # border with The Forge, and only looked stranded because The Forge
    # itself is behind a portal.
    portals = []
    while True:
        left = [l for l in w.locations if l not in at]
        if not left:
            break
        far = max((x + w.map(l).w + 8 for l, (x, _) in at.items()), default=0)
        low = min((y for _, (_, y) in at.items()), default=0)
        seed = left[0]
        origin = (far, low)
        while _overlaps_placed(w, at, seed, origin):
            origin = (origin[0] + w.map(seed).w + 8, low)
        at[seed] = origin
        portals.append(seed)
        spread(at, [seed], only_story=False)
    return at, portals


def flat_pairs(w, at):
    """Seams whose two maps really do sit one step apart in this layout."""
    out = set()
    for a, ta, b, tb, side in seams(w):
        if a not in at or b not in at:
            continue
        ax, ay = ta
        bx, by = tb
        dx, dy = STEP[side]
        exp = (at[a][0] + ax - bx + dx, at[a][1] + ay - by + dy)
        if at[b] == exp:
            out.add((min(a, b), max(a, b)))
    return out


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


def turn_xy(x, y, width, height, turns):
    """Same quarter-turns clockwise as render_map._Turned."""
    w, h = width, height
    for _ in range(turns % 4):
        x, y = h - 1 - y, x
        w, h = h, w
    return x, y, w, h


def proposed(w, at):
    """Where the turned rooms sit. The grids themselves are already turned
    by the time a World exists — see server/layout.py — so this only places
    them. Turning again here would spin Fire Cave twice.
    """
    hall = at[3]
    fc = (hall[0] + 40, hall[1] + 7)
    at[12] = fc
    at[14] = (fc[0] + 25, fc[1] + 10)
    at[11] = (fc[0] + 12 - 16, fc[1] + 35)
    return at, {}, {}


def main():
    game = sys.argv[1] if len(sys.argv) > 1 else "ShiradsForge"
    trial = "--proposed" in sys.argv
    w = World(game)
    # Draw the world as it can ever be, not as it is on arrival: sixteen of
    # the eighteen rooms have their ground rewritten during play, and the
    # Crypt nearly triples. See World.reveal_all_patches.
    painted = w.reveal_all_patches()
    at, portals = lay_out(w)
    turns, doors = {}, {}
    if trial:
        at, turns, doors = proposed(w, at)
        portals = [p for p in portals if p not in (11, 12, 14)]

    def shown(loc, x, y, dest=None):
        if dest is not None and (loc, dest) in doors:
            return doors[(loc, dest)]
        t = turns.get(loc, 0)
        if not t:
            return x, y
        mp = w.map(loc)
        x, y, _, _ = turn_xy(x, y, mp.w, mp.h, t)
        return x, y

    def footprint(loc):
        mp = w.map(loc)
        tw, th = mp.w, mp.h
        for _ in range(turns.get(loc, 0)):
            tw, th = th, tw
        return tw, th

    imgs, trim = {}, {}
    for loc in w.locations:
        img = render(w, loc, annotate=False, bg=(0, 0, 0, 0),
                     turns=turns.get(loc, 0))
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
        _, th = footprint(loc)
        ox = th * STEP_X + PAD
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

    # Everything that stands on the ground, drawn back to front across the
    # whole world rather than per map, so a creature near the front of one
    # location correctly overlaps the location behind it.
    standing = []
    for loc in imgs:
        for (tx, ty), kind, creature in markers(w, loc):
            if kind == "door":
                dest = next((d for (sx, sy), d in w.EXITS.get(loc, [])
                             if (sx, sy) == (tx, ty)), None)
                # The dot is the old corner. A door this layout moved is
                # already drawn as its own tile, so the dot would be left
                # behind in the gap the bridge just vacated.
                if dest is not None and (loc, dest) in doors:
                    continue
            tx, ty = shown(loc, tx, ty)
            gx, gy = at[loc]
            standing.append((gx + tx + gy + ty, loc, tx, ty, kind, creature))
    for _, loc, tx, ty, kind, creature in sorted(standing):
        cx, cy = px(loc, tx, ty)
        if kind in ("crate", "barrel"):
            draw.rectangle([cx - 6, cy - 6, cx + 6, cy + 6],
                           outline=(205, 160, 90, 255), width=2)
            continue
        if kind == "spawn":
            draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8],
                         outline=(250, 250, 250, 255), width=3)
            continue
        drawn = sprite(w, creature) if creature is not None else None
        if drawn:
            img2, (ox2, oy2) = drawn
            if kind == "waiting":
                # faded, so you can see what it is and that it is not there yet
                ghost = img2.copy()
                alpha = ghost.getchannel("A").point(lambda v: v * 40 // 100)
                ghost.putalpha(alpha)
                sheet.alpha_composite(ghost, (int(cx + ox2), int(cy + oy2)))
                draw.ellipse([cx - 7, cy - 4, cx + 7, cy + 4],
                             outline=(150, 190, 235, 210), width=1)
            else:
                sheet.alpha_composite(img2, (int(cx + ox2), int(cy + oy2)))
        elif kind == "waiting":
            draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6],
                         outline=(150, 190, 235, 210), width=2)
        else:
            draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6],
                         fill=(225, 80, 80, 255), outline=(0, 0, 0, 255))

    # Every doorway, marked. Half of watAgame's carry the red tile and half
    # are bare ground you would only find by walking into it, so the bare
    # ones are annotated here — on the map, not in the game.
    tile = marker_strip(w)
    for loc in imgs:
        for (ox, oy), dest in w.EXITS.get(loc, []):
            tx, ty = shown(loc, ox, oy, dest)
            cx, cy = px(loc, tx, ty)
            if is_arch(w, loc, ox, oy):
                draw.ellipse([cx - 12, cy - 8, cx + 12, cy + 8],
                             outline=(205, 155, 255, 255), width=3)
            elif (w.map(loc).tile(ox, oy) & 15) != w.marker and tile:
                sheet.alpha_composite(tile, (int(cx) - 16, int(cy) - 7))

    # A portal is drawn the way a road map shows a junction that leaves the
    # page: a ring where it stands and the number of the place it goes. A
    # line across the whole world only looked like a road.
    joined = flat_pairs(w, at)
    if trial:
        joined |= {(3, 12), (11, 12), (12, 14)}
    jog = set()
    stub = font(22)
    for a, links in w.EXITS.items():
        for ta, b in links:
            pair = (min(a, b), max(a, b))
            if pair in joined or a not in at or b not in at:
                continue
            if pair in jog:
                back = shown(b, *next(t for t, d in w.EXITS.get(b, []) if d == a), a)
                ax, ay = px(a, *shown(a, *ta, b))
                bx, by = px(b, *back)
                draw.line([(ax, ay), (bx, by)], fill=(255, 210, 90, 220), width=3)
                continue
            ta = shown(a, *ta, b)
            cx, cy = px(a, *ta)
            draw.ellipse([cx - 13, cy - 9, cx + 13, cy + 9],
                         outline=(205, 155, 255, 255), width=3)
            tag = f"->{b}"
            draw.text((cx + 17, cy - 11), tag, font=stub, fill=(0, 0, 0, 255))
            draw.text((cx + 16, cy - 12), tag, font=stub,
                      fill=(215, 175, 255, 255))

    label, title = font(26), font(46)
    for loc in imgs:
        mp = w.map(loc)
        # the middle of the GROUND, not of the rectangle: the Crypt fills
        # only the left third of its 20x10 map, so its geometric centre is
        # out in the void
        drawn_tiles = [shown(loc, x, y)
                       for y in range(mp.h) for x in range(mp.w)
                       if mp.tile(x, y) & 15]
        if drawn_tiles:
            mx = sum(t[0] for t in drawn_tiles) // len(drawn_tiles)
            my = sum(t[1] for t in drawn_tiles) // len(drawn_tiles)
        else:
            mx, my = mp.w // 2, mp.h // 2
        c = px(loc, mx, my)
        text = f"{loc}  {w.name(loc)}"
        tx = c[0] - draw.textlength(text, font=label) / 2
        draw.text((tx + 2, c[1] + 2), text, font=label, fill=(0, 0, 0, 255))
        draw.text((tx, c[1]), text, font=label, fill=(255, 245, 190, 255))

    real = getattr(w, "real1", None)
    if trial:
        head = f"{game} - trial layout"
        sub = ("11, 12 and 14 turned clockwise. The stone bridge by the "
               "Long Run arch now crosses the lava to Aldor's door.")
    else:
        head = f"{game} - one continuous world"
        sub = (f"{len(joined)} shared borders laid out flat. A purple ring "
               f"is a portal, labelled with the location it reaches. Faded red "
               f"tiles are doorways watAgame left unmarked.")
    draw.text((margin + 2, 22), head, font=title, fill=(0, 0, 0, 255))
    draw.text((margin, 20), head, font=title, fill=(245, 245, 250, 255))
    draw.text((margin, 78), sub, font=label, fill=(160, 160, 180, 255))
    draw.text((margin, 112),
              "creatures, townsfolk, crates and doorways are all watAgame's, "
              "from the tables an early build shipped locally" if real
              else "doorways and creature positions are reconstructed, "
                   "so this layout is a guess",
              font=label, fill=(160, 160, 180, 255))

    path = os.path.join(OUT, f"{game}-world{'-proposed' if trial else ''}.png")
    sheet.convert("RGB").save(path)
    print(f"{path}  {sheet.size[0]}x{sheet.size[1]}  "
          f"{len(imgs)} locations, {len(joined)} seams, "
          f"{len(portals)} behind portals")
    return 0


if __name__ == "__main__":
    sys.exit(main())
