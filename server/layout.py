"""Shirad's Forge: the quest rewards, and reading an older save.

The three detached rooms — Fire Cave, Ilrik's Tomb and Aldor's Outpost —
were turned a quarter-turn clockwise here for a while, with a bridge laid
across Fire Cave's lava, so that the four rooms of the chapter would seam
into one picture. The doors watAgame shipped already joined them (Fire
Cave's south-east corner to Aldor's west edge), so the turn bought nothing
but the picture, and cost the chapter its original shape. It is gone: the
grids, doors and creature squares are the 2005 jar's, untouched, and the
world map shows those three rooms detached because that is how they are.

What is left here is the one deliberate change to the chapter's contents —
the three optional quests pay a sum that means something in this economy —
and `migrate_save`, which reads a save written while the rooms were turned.

The jar in jars/ was never modified. The server applies the text change as
it loads, and run/mkjar.py writes the same change into the run jar.
"""

# location -> the room's height in the jar, used to undo the old turn
ORIG_H = {11: 30, 12: 25, 14: 20}


def unrot_point(x, y, height):
    """Undo one quarter-turn clockwise. `height` is the grid's own height."""
    return y, height - 1 - x


def migrate_save(world, saved):
    """A save written while the three rooms were turned, read upright again.

    Positions in those rooms move back with the grid. A square that only
    existed because of the old lava bridge drops the hero on the room's
    spawn instead.
    """
    if world.game != "ShiradsForge" or saved.get("layout", 0) != 1:
        return saved
    saved = dict(saved)
    loc = saved.get("location")
    if loc in ORIG_H:
        x, y = unrot_point(saved.get("hero_x", 0), saved.get("hero_y", 0),
                           ORIG_H[loc])
        mp = world.map(loc)
        if mp is None or not mp.walkable(x, y):
            x, y = world.spawn_point(loc)
        saved["hero_x"], saved["hero_y"] = x, y
        rec = saved.get("recall")
        if rec and len(rec) == 2:
            rx, ry = unrot_point(rec[0], rec[1], ORIG_H[loc])
            if mp is not None and mp.walkable(rx, ry):
                saved["recall"] = [rx, ry]
            else:
                saved["recall"] = [x, y]
    mobs = []
    for md in saved.get("mobs") or []:
        md = dict(md)
        ml = md.get("location")
        if ml in ORIG_H:
            md["x"], md["y"] = unrot_point(md.get("x", 0), md.get("y", 0),
                                           ORIG_H[ml])
            home = md.get("home")
            if home and len(home) == 2:
                md["home"] = list(unrot_point(home[0], home[1], ORIG_H[ml]))
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

