"""Shirad's Forge: three rooms turned clockwise, and the lava bridge moved.

Fire Cave, Ilrik's Tomb and Aldor's Outpost are stored north-up in the
2005 jar. Play turns each grid one quarter clockwise. Fire Cave's old
corner door to Aldor then sits on the west edge, so that door — and the
grey span that led to it — is laid across the lava on the south edge,
where Aldor's own door is the north edge.

The jar in jars/ stays the original. The server applies this as it
loads, and the run jar is rewritten the same way so the phone draws it.
"""

import struct

# location -> quarter-turns clockwise
TURNS = {11: 1, 12: 1, 14: 1}
# original height, so a save from before the turn can be read
ORIG_H = {11: 30, 12: 25, 14: 20}
# type 2 resource names in the jar
TYPE2 = {11: "2b", 12: "2c", 14: "2e"}

# Fire Cave, original coordinates, before the turn. The south-edge span
# is what lands in front of Aldor's door once the room turns.
_BRIDGE = {
    (30, 24): 0, (31, 24): 0, (32, 24): 0,
    (31, 23): 0x04,
    (30, 22): 0x03,
    (30, 11): 0x07, (30, 12): 0x07, (30, 13): 0x07,
    (31, 11): 0x07, (31, 12): 0x07, (31, 13): 0x07,
    (32, 12): 0x07, (32, 13): 0x07,
    (33, 12): 0x07, (33, 13): 0x07,
    (34, 12): 0x0C, (34, 13): 0x0C,
}


def rot_point(x, y, height):
    """One quarter-turn clockwise. `height` is the grid's height before it."""
    return height - 1 - y, x


def rot_box(x1, y1, x2, y2, height):
    """An [x1, x2) by [y1, y2) box, one quarter-turn clockwise."""
    return height - y2, x1, height - y1, x2


def _rot_tiles(tiles, w, h):
    out = bytearray(w * h)
    for y in range(h):
        row = y * w
        for x in range(w):
            nx = h - 1 - y
            ny = x
            out[ny * h + nx] = tiles[row + x]
    return out, h, w


def _rot_patch(x, y, w, h, tiles, map_h):
    """A w*h patch rectangle, turned with the map it paints."""
    placed = []
    for ly in range(h):
        for lx in range(w):
            nx, ny = rot_point(x + lx, y + ly, map_h)
            placed.append((nx, ny, tiles[ly * w + lx]))
    minx = min(p[0] for p in placed)
    miny = min(p[1] for p in placed)
    maxx = max(p[0] for p in placed)
    maxy = max(p[1] for p in placed)
    nw, nh = maxx - minx + 1, maxy - miny + 1
    out = bytearray(nw * nh)
    for nx, ny, tile in placed:
        out[(ny - miny) * nw + (nx - minx)] = tile
    return minx, miny, nw, nh, out


def rewrite_type2(blob, turns, bridge=False):
    """Header plus tiles, turned. Returns the new blob and the original size."""
    w, h = struct.unpack_from(">hh", blob, 9)
    n = w * h
    tiles = bytearray(blob[13:13 + n])
    if bridge:
        if (w, h) != (35, 25):
            raise ValueError(f"Fire Cave is {w}x{h}, expected 35x25")
        for (x, y), tile in _BRIDGE.items():
            tiles[y * w + x] = tile
    ow, oh = w, h
    for _ in range(turns % 4):
        tiles, w, h = _rot_tiles(tiles, w, h)
    header = bytearray(blob[:13])
    struct.pack_into(">hh", header, 9, w, h)
    return bytes(header) + bytes(tiles) + blob[13 + n:], (ow, oh)


def _transform_row(row, heights):
    if len(row) < 14:
        return row
    r = bytearray(row)
    loc = r[1]
    if loc in heights and r[4] != 0:
        r[2], r[3], r[4], r[5] = rot_box(r[2], r[3], r[4], r[5], heights[loc])
    kind, tail = r[12], r[13]
    if kind == 4 and tail >= 3 and len(r) >= 17:
        dest = r[14]
        if dest in heights:
            r[15], r[16] = rot_point(r[15], r[16], heights[dest])
        # The cave's door to Aldor is the south span, not the turned corner.
        if loc == 12 and dest == 11:
            r[2], r[3], r[4], r[5] = 11, 34, 13, 35
        # Coming back lands on that span, not in the gap the corner left.
        if loc == 11 and dest == 12:
            r[15], r[16] = 12, 33
    if kind == 6 and tail >= 6 and len(r) >= 19 and r[17] and r[18]:
        ploc = r[14]
        if ploc in heights:
            w, h = r[17], r[18]
            raw = bytes(r[19:19 + w * h])
            if len(raw) == w * h:
                nx, ny, nw, nh, out = _rot_patch(r[15], r[16], w, h, raw,
                                                 heights[ploc])
                r[15], r[16], r[17], r[18] = nx, ny, nw, nh
                r[19:19 + len(out)] = out
    return bytes(r)


def _transform_mob(row, heights):
    if len(row) < 5 or row[1] not in heights:
        return row
    r = bytearray(row)
    r[3], r[4] = rot_point(r[3], r[4], heights[row[1]])
    # [18] == 0 means no leash (the phone skips the box).
    if len(r) >= 20 and r[18]:
        r[16], r[17], r[18], r[19] = rot_box(
            r[16], r[17], r[18], r[19], heights[row[1]])
    return bytes(r)


def apply_forge_layout(res, rows, mobs):
    """Turn the three rooms inside a loaded chapter. In place."""
    heights = {}
    for loc, turns in TURNS.items():
        name = TYPE2[loc]
        blob = res.files.get(name)
        if blob is None:
            continue
        rewritten, (_, oh) = rewrite_type2(blob, turns, bridge=(loc == 12))
        res.files[name] = rewritten
        heights[loc] = oh
    if rows:
        for i, row in enumerate(rows):
            rows[i] = _transform_row(row, heights)
    if mobs:
        for i, row in enumerate(mobs):
            mobs[i] = _transform_mob(row, heights)
    return heights


def migrate_save(world, saved):
    """A save from before the turn, read in the turned rooms.

    Positions on the three rooms move with the grid. A square the bridge
    edit emptied drops the hero on that room's spawn instead.
    """
    if world.game != "ShiradsForge" or saved.get("layout", 0) >= 1:
        return saved
    saved = dict(saved)
    loc = saved.get("location")
    if loc in ORIG_H:
        x, y = rot_point(saved.get("hero_x", 0), saved.get("hero_y", 0),
                         ORIG_H[loc])
        mp = world.map(loc)
        if mp is None or not mp.walkable(x, y):
            x, y = world.spawn_point(loc)
        saved["hero_x"], saved["hero_y"] = x, y
        rec = saved.get("recall")
        if rec and len(rec) == 2:
            rx, ry = rot_point(rec[0], rec[1], ORIG_H[loc])
            if mp is not None and mp.walkable(rx, ry):
                saved["recall"] = [rx, ry]
            else:
                saved["recall"] = [x, y]
    mobs = []
    for md in saved.get("mobs") or []:
        md = dict(md)
        ml = md.get("location")
        if ml in ORIG_H:
            md["x"], md["y"] = rot_point(md.get("x", 0), md.get("y", 0),
                                         ORIG_H[ml])
            home = md.get("home")
            if home and len(home) == 2:
                md["home"] = list(rot_point(home[0], home[1], ORIG_H[ml]))
        mobs.append(md)
    saved["mobs"] = mobs
    return saved


# -- the three optional quests' rewards -------------------------------------
#
# Dreyfus, Tillic and Milas each name their reward out loud, in the jar's
# own text: 3, "a few" and 5 Gold coins. That was watAgame's economy; in
# this one a tier II weapon costs 300-460 and 3 gold reads as a mistake.
# The sums are raised, and the lines rewritten to say them: here for the
# server (apply_forge_texts) and in the run jar (run/mkjar.py), from this
# one table, so what a character says is always what he pays.
#
#   checkpoint state -> (location, text key, gold, the line as it now reads)
QUEST_GIFTS = {
    117: (8, 0x197E, 250,
          "Dreyfus: Good, good! I can see that you have put all the undead "
          "creatures to rest.\n\nAs a token of my gratitude please take these "
          "250 Gold coins. Go in peace."),
    136: (12, 0x1984, 150,
          "Tillic: Wow, it must really have taken all your strength to defeat "
          "those two fire devils, but you did it! I would like to give you "
          "these 150 Gold coins as a token of my appreciation."),
    148: (13, 0x1981, 400,
          "Milas: Hurrah, you actually managed to slay the beholder! I would "
          "never have thought that. Please take these 400 Gold coins as a "
          "reward for helping me out. Now I can return to my home."),
}


def text_patches():
    """type 3 resource name -> {text key: new line}."""
    out = {}
    for loc, key, _, line in QUEST_GIFTS.values():
        out.setdefault(f"3{loc:x}", {})[key] = line
    return out


def rewrite_strings(blob, patches):
    """A keyed string table (u16 key, u16 len, utf-8) with some lines
    replaced. Everything else is copied as it was, in order."""
    out, i = bytearray(), 0
    while i + 4 <= len(blob):
        key = int.from_bytes(blob[i:i + 2], "big")
        ln = int.from_bytes(blob[i + 2:i + 4], "big")
        body = bytes(blob[i + 4:i + 4 + ln])
        if key in patches:
            body = patches[key].encode("utf-8")
        out += key.to_bytes(2, "big") + len(body).to_bytes(2, "big") + body
        i += 4 + ln
    out += blob[i:]
    return bytes(out)


def apply_forge_texts(res):
    """Rewrite the loaded chapter's lines the same way the run jar is. In place."""
    for name, patches in text_patches().items():
        blob = res.files.get(name)
        if blob is not None:
            res.files[name] = rewrite_strings(blob, patches)

