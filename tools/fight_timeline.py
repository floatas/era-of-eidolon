#!/usr/bin/env python3
"""The turn, drawn: what a side can fit into 720, and what thinking costs.

    python3 tools/fight_timeline.py

Every number is read from the running game, not typed in here. The one worth
looking at is the thinking band: d.java adds five to the turn clock for every
real second you spend deciding, and ends the turn itself at 720. So the bar
you spend on walking and swinging is the same bar that empties while you look
at the screen — 144 seconds of it, end to end.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "server"))

import handlers                      # noqa: E402
from catalogue import catalogue      # noqa: E402
from world import World              # noqa: E402

W, PAD = 940, 28
LANE_H, GAP = 54, 26
TICK_PER_SECOND = 5                  # d.java: this.ag += n * 5

C = {
    "ink": "#f3e6c4", "dim": "#bda978", "faint": "#7d7054",
    "bg": "#14110e", "lane": "#1d1812", "rule": "#6e5424", "gold": "#f4dc62",
    "move": "#2f6f6b", "blow": "#b4532b", "think": "#4a3f2a", "guard": "#9c7a2e",
}


def bar(x0, y, span, budget, blocks, scale):
    """One side's 720, as a row of what it spent."""
    out = [f'<rect x="{x0}" y="{y}" width="{span}" height="{LANE_H}" '
           f'rx="2" fill="{C["lane"]}" stroke="{C["rule"]}" stroke-width="1"/>']
    at = 0
    for cost, kind, label in blocks:
        if at + cost > budget:
            break
        w = cost * scale
        out.append(f'<rect x="{x0 + at * scale:.1f}" y="{y + 1}" width="{w:.1f}" '
                   f'height="{LANE_H - 2}" fill="{C[kind]}" '
                   f'stroke="{C["bg"]}" stroke-width="1"/>')
        if w > 26:
            out.append(f'<text x="{x0 + at * scale + w / 2:.1f}" y="{y + LANE_H / 2 + 4:.0f}" '
                       f'text-anchor="middle" font-size="11" fill="{C["ink"]}" '
                       f'font-family="IBM Plex Mono, monospace">{label}</text>')
        at += cost
    if at < budget:
        out.append(f'<text x="{x0 + at * scale + 7:.1f}" y="{y + LANE_H / 2 + 4:.0f}" '
                   f'font-size="11" fill="{C["faint"]}" '
                   f'font-family="IBM Plex Mono, monospace">{budget - at} left</text>')
    return "".join(out), at


def main():
    w = World("ShiradsForge")
    budget = handlers.TURN_BUDGET
    move = handlers.MOVE_COST
    blade = next(i for i in catalogue().get("weapon") if i.name == "Bloody Blade")
    axe = next(i for i in catalogue().get("weapon") if i.name == "Doom Hammer")

    skel = next(m for m in w.mobs.values()
                if handlers.fighter_name(w, m) == "Skeleton")
    golem = next(m for m in w.mobs.values()
                 if handlers.fighter_name(w, m) == "Golem")
    sk_t = skel.offence()["swing"]
    go_t = golem.offence()["swing"]

    lanes = [
        ("You, a sword in hand",
         [(move, "move", "step")] * 4
         + [(blade.time, "blow", f"swing {blade.time}")] * 5,
         f"{blade.name}, {blade.time} a swing"),
        ("You, a hammer in hand",
         [(move, "move", "step")] * 4
         + [(axe.time, "blow", f"swing {axe.time}")] * 2,
         f"{axe.name}, {axe.time} a swing"),
        ("A Skeleton, light on its feet",
         [(move, "move", "step")] * 2
         + [(sk_t, "blow", f"blow {sk_t}")] * 3,
         f"a blow every {sk_t}"),
        ("A Golem, slow and heavy",
         [(move, "move", "step")] * 2
         + [(go_t, "blow", f"blow {go_t}")] * 1,
         f"a blow every {go_t}"),
        ("You, thinking about it",
         [(TICK_PER_SECOND * 30, "think", "30 seconds"),
          (TICK_PER_SECOND * 30, "think", "30 seconds"),
          (TICK_PER_SECOND * 30, "think", "30 seconds"),
          (TICK_PER_SECOND * 30, "think", "30 seconds")],
         f"{TICK_PER_SECOND} a second \u2014 {budget // TICK_PER_SECOND}s a turn"),
    ]

    label_w = 210
    span = W - PAD * 2 - label_w
    scale = span / budget
    H = PAD * 2 + 54 + len(lanes) * (LANE_H + GAP + 16)

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.0f}" '
         f'width="{W}" height="{H:.0f}" font-family="Georgia, serif">',
         f'<rect width="{W}" height="{H:.0f}" fill="{C["bg"]}"/>',
         f'<text x="{PAD}" y="{PAD + 16}" font-size="19" fill="{C["ink"]}">'
         f'One turn is {budget}</text>',
         f'<text x="{PAD}" y="{PAD + 38}" font-size="13" fill="{C["dim"]}">'
         f'A step costs {move}. A blow costs what the weapon weighs. '
         f'And the clock runs while you decide.</text>']

    y = PAD + 62
    for name, blocks, note in lanes:
        s.append(f'<text x="{PAD}" y="{y + LANE_H / 2 - 2:.0f}" font-size="13" '
                 f'fill="{C["ink"]}">{name}</text>')
        s.append(f'<text x="{PAD}" y="{y + LANE_H / 2 + 14:.0f}" font-size="11" '
                 f'fill="{C["faint"]}" font-family="IBM Plex Mono, monospace">{note}</text>')
        drawn, used = bar(PAD + label_w, y, span, budget, blocks, scale)
        s.append(drawn)
        y += LANE_H + GAP + 16

    # the scale underneath
    s.append(f'<line x1="{PAD + label_w}" x2="{PAD + label_w + span}" '
             f'y1="{y - GAP - 2:.0f}" y2="{y - GAP - 2:.0f}" stroke="{C["rule"]}"/>')
    for n in range(0, budget + 1, 120):
        x = PAD + label_w + n * scale
        s.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{y - GAP - 2:.0f}" '
                 f'y2="{y - GAP + 3:.0f}" stroke="{C["rule"]}"/>')
        s.append(f'<text x="{x:.1f}" y="{y - GAP + 16:.0f}" text-anchor="middle" '
                 f'font-size="10" fill="{C["faint"]}" '
                 f'font-family="IBM Plex Mono, monospace">{n}</text>')
    s.append("</svg>")

    out = os.path.join(ROOT, "assets", "turn-timeline.svg")
    with open(out, "w") as fh:
        fh.write("".join(s))
    print(f"{out}  {W}x{H:.0f}")
    print(f"   budget {budget}, step {move}, "
          f"{blade.name} {blade.time}, {axe.name} {axe.time}, "
          f"Skeleton {sk_t}, Golem {go_t}")
    print(f"   thinking: {TICK_PER_SECOND} a second "
          f"-> {budget // TICK_PER_SECOND} seconds a turn")


if __name__ == "__main__":
    main()
