"""Trophies for Shirad's Forge, and a platinum for all of them.

Ours entirely: watAgame's chapters had a score and rankings on their server,
not trophies. Everything a trophy asks for is something the server already
sees: a kill and the weapon that made it, a crate, a trader, a recycle, the
room the phone reports, and the phone's own quest switches (d.i), which ride
along on every fight and save.

A trophy is earned once and kept in the save. The phone has no pop-up, so a
new trophy is announced in the next text the phone shows from the server:
the battle report after a fight, or a crate's message. The web player's
side panel lists them all with their progress (panel()).

This module reads a World and never imports one, so world.py and
handlers.py can both call it.
"""

# id, name, tier, what it asks for
TROPHIES = [
    ("first_blood", "First Blood", "bronze", "Win a fight."),
    ("recycler", "Recycler", "bronze", "Recycle an item."),
    ("customer", "Customer", "bronze", "Buy something from a trader."),
    ("blade", "Blade", "bronze", "Slay a creature with a sword."),
    ("heavy", "Heavy Hand", "bronze", "Slay a creature with an axe or a hammer."),
    ("marksman", "Marksman", "bronze", "Slay a creature with a bow."),
    ("spellbinder", "Spellbinder", "bronze", "Slay a creature with Zap."),
    ("untouchable", "Untouchable", "silver", "Win a fight without losing any life."),
    ("cogwheels", "Cogwheels", "silver", "Find all three cogwheels."),
    ("mira", "Mira", "silver", "Defeat Mira."),
    ("aldor", "Aldor", "silver", "Defeat Aldor."),
    ("beholder", "The Beholder", "silver", "Defeat the Beholder."),
    ("explorer", "Explorer", "silver", "Set foot in every room of the chapter."),
    ("crypt", "The Crypt", "silver", "Clear all three waves of the Crypt."),
    ("secrets", "Secret Keeper", "gold", "Find every hidden room."),
    ("treasure", "Treasure Hunter", "gold", "Open every crate."),
    ("quests", "Every Quest", "gold", "Finish every quest, the optional ones too."),
    ("forge", "Shirard's Forge", "gold", "Defeat Shirard."),
    ("platinum", "Platinum", "platinum", "Earn every other trophy."),
]
BY_ID = {t[0]: t for t in TROPHIES}
TIER_ORDER = ("bronze", "silver", "gold", "platinum")

# Shirad's Forge's facts the trophies are checked against.
BOSS_NODES = {46: "mira", 48: "aldor", 19: "beholder", 20: "forge"}
# the kind 8 quest items that are the cogwheels (protocol/PROTOCOL.md)
COGWHEELS = (188, 218, 219)
# The rooms whose only way in is a door that starts shut (Ilrik's Tomb, The
# Evil Eye, the Crypt), and Golem Secret, which says so in its name.
SECRETS = (14, 13, 16, 18)
CRYPT = 16
# weapon line of the killing blow -> trophy
KILL_TROPHY = {"sword": "blade", "heavy": "heavy", "bow": "marksman",
               "zap": "spellbinder"}


def _held(w):
    held = getattr(w, "trophies", None)
    if held is None:
        held = w.trophies = {}
    return held


def earn(w, tid):
    """Grant one trophy if it is new. Returns True when it was."""
    if getattr(w, "game", "") != "ShiradsForge" or tid not in BY_ID:
        return False
    held = _held(w)
    if tid in held:
        return False
    held[tid] = len(held) + 1
    news = getattr(w, "trophy_news", None)
    if news is None:
        news = w.trophy_news = []
    news.append(tid)
    if tid != "platinum" and all(t[0] in held for t in TROPHIES if t[0] != "platinum"):
        earn(w, "platinum")
    return True


# -- what the save already knows ------------------------------------------

def _quests(w):
    """(entity state id, main?) for every entity carrying a quest line.
    d.h() lists a quest while its entity is at 2; it is done at 3."""
    out = []
    for r in getattr(w, "real1", None) or ():
        if len(r) > 11 and r[11] in (1, 2) and ((r[9] << 8) | r[10]):
            out.append((r[0], r[11] == 1))
    return out


def _state(w, sid):
    prog = getattr(w, "progress", None)
    return prog[sid] if prog and sid < len(prog) else 0


def _crates(w):
    return w.prize_crates() if hasattr(w, "prize_crates") else set()


def _crypt_foes(w):
    """The Crypt's creatures a hero can kill. The one a kind 7 sends away
    (the 'Talk to ghost' spirit) is not a fight."""
    gone = set()
    for r in getattr(w, "real1", None) or ():
        if len(r) > 13 and r[12] == 7:
            gone.update(r[14:14 + r[13]])
    return {m.node for m in w.mobs.values()
            if m.location == CRYPT and not m.npc and m.node not in gone}


def progress(w):
    """tid -> (done, total) for the trophies that count something."""
    slain = set(getattr(w, "slain", ()))
    visited = set(getattr(w, "visited", ()))
    opened = set(getattr(w, "opened", ()))
    quests = _quests(w)
    crates = _crates(w)
    crypt = _crypt_foes(w)
    return {
        "cogwheels": (sum(1 for s in COGWHEELS if _state(w, s) == 3), len(COGWHEELS)),
        "explorer": (len(visited & set(w.locations)), len(w.locations)),
        "secrets": (len(visited & set(SECRETS)), len(SECRETS)),
        "treasure": (len(opened & crates), len(crates)),
        "quests": (sum(1 for s, _ in quests if _state(w, s) == 3), len(quests)),
        "crypt": (len(crypt & slain), len(crypt)),
    }


def check(w):
    """Grant whatever the hero's state now earns. Cheap enough to call after
    anything that can change it."""
    if getattr(w, "game", "") != "ShiradsForge":
        return
    for tid, (done, total) in progress(w).items():
        if total and done >= total:
            earn(w, tid)
    slain = set(getattr(w, "slain", ()))
    for node, tid in BOSS_NODES.items():
        if node in slain:
            earn(w, tid)
    if getattr(w, "finished", False):
        earn(w, "forge")


def killed(w, node, line):
    """A creature died to the hero's blow, arrow or spell."""
    slain = getattr(w, "slain", None)
    if slain is None:
        slain = w.slain = []
    if node not in slain:
        slain.append(node)
    if line in KILL_TROPHY:
        earn(w, KILL_TROPHY[line])
    check(w)


def news(w):
    """Lines announcing the trophies earned since the last announcement."""
    fresh = getattr(w, "trophy_news", None) or []
    w.trophy_news = []
    lines = []
    for tid in fresh:
        _, name, tier, _ = BY_ID[tid]
        lines.append(f"Trophy: {name} ({tier})")
    return lines


def panel(w):
    """The side panel's Trophies section: every trophy, earned or not, with
    what it asks for and how far along the hero is."""
    live = w is not None and getattr(w, "game", "") == "ShiradsForge"
    held = _held(w) if live else {}
    counts = progress(w) if live else {}
    earned = len(held)
    entries = []
    for tier in TIER_ORDER:
        for tid, name, t, how in TROPHIES:
            if t != tier:
                continue
            got = tid in held
            lines = [f"{tier.capitalize()} · {'Earned' if got else 'Not yet'}", how]
            if tid in counts and not got:
                done, total = counts[tid]
                lines.append(f"{done} of {total} so far.")
            entries.append({"id": f"trophy-{tid}",
                            "title": ("✓ " if got else "· ") + name,
                            "lines": lines})
    return {"name": f"Trophies {earned}/{len(TROPHIES)}", "entries": entries}
