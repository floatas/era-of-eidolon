"""Where a tile lands on screen, taken from the phone's own draw loop.

d.java draws the ground, then the scenery, then the creatures, and the three
do not share one corner.

A ground tile is 32 wide and 15 tall. Its top-left is

    ((x - y) * 16, (x + y) * 8)

with the picture's top-left as the anchor (Graphics anchor 20).

Scenery is the high nibble of the tile, looked up in the type 6 rect table
and cut from the type 5 sheet. Before that pass the loop does `n19 += 16;
n25 = n20 + 8`, so a tree or a crate is drawn 16 right and 8 down from the
ground tile, plus the rect's own dx, dy.

A creature standing on the tile is drawn at the diamond point itself,
(x - y) * 16, (x + y) * 8, and each body part hangs off that point by the
offsets in its animation. That point is the middle of the ground tile, not
its top-left.
"""

STEP_X, STEP_Y = 16, 8
TILE_W, TILE_H = 32, 15
# The shift applied once, before every obstacle, in d.java.
OBSTACLE_SHIFT = (16, 8)


def diamond(x, y):
    """The point the phone uses for a creature on this tile."""
    return ((x - y) * STEP_X, (x + y) * STEP_Y)


def ground_top_left(x, y):
    """Top-left of the 32x15 floor picture, so it is centred on the diamond."""
    dx, dy = diamond(x, y)
    return (dx - TILE_W // 2, dy - TILE_H // 2)


def obstacle_top_left(x, y, dx=0, dy=0):
    """Top-left of a piece of scenery on this tile."""
    gx, gy = ground_top_left(x, y)
    sx, sy = OBSTACLE_SHIFT
    return (gx + sx + dx, gy + sy + dy)
