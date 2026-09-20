#!/usr/bin/env python3
"""Dump the world data that ships inside an Era of Eidolon chapter jar.

Resource files are named "<restype><hex id>" (the client asks for them as
"/" + restype + Integer.toHexString(id)).

    type 2  tilemap      13-byte header, then width*height tile bytes
    type 3  location text  keyed string table: u16 key, u16 len, bytes
    type 10 quest table    same keyed-string format
    type 7/8/11  creature sprite / animation / properties (same id per creature)

    type 1  placed entities )  not in any jar - these were served at runtime
    type 9  map nodes       )

Usage: python3 dump_world.py ../extracted/EoE-ShiradsForge
"""

import os
import re
import sys


def parse_strings(b):
    """g.java a(DataInputStream,len,false): u16 key, u16 len, len bytes."""
    out, i = [], 0
    while i + 4 <= len(b):
        key = int.from_bytes(b[i:i + 2], "big")
        ln = int.from_bytes(b[i + 2:i + 4], "big")
        i += 4
        if i + ln > len(b):
            break
        out.append((key, b[i:i + ln]))
        i += ln
    return out


def printable(raw):
    try:
        s = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return s if s and sum(c.isprintable() for c in s) >= len(s) * 0.8 else None


def main(root):
    files = {f for f in os.listdir(root) if re.fullmatch(r"[0-9a-f]+", f)}

    def read(name):
        with open(os.path.join(root, name), "rb") as fh:
            return fh.read()

    print("=" * 72)
    print("TILEMAPS (type 2)")
    print("=" * 72)
    maps = sorted((int(f[1:], 16), f) for f in files
                  if f[0] == "2" and not f.startswith(("10", "11")))
    for mid, f in maps:
        b = read(f)
        w, h = b[10], b[12]
        tiles = b[13:13 + w * h]
        distinct = len(set(tiles))
        print(f"  location 0x{mid:02x}  {w:>2} x {h:<2}  "
              f"{len(tiles):>5} tiles, {distinct} distinct")

    print()
    print("=" * 72)
    print("LOCATION TEXT (type 3)")
    print("=" * 72)
    for lid, f in sorted((int(f[1:], 16), f) for f in files if f[0] == "3"):
        print(f"\n  --- location 0x{lid:02x} ---")
        for key, raw in parse_strings(read(f)):
            s = printable(raw)
            if s:
                s = s.replace("\n", " / ")
                print(f"    [{key:04x}] {s[:150]}")

    print()
    print("=" * 72)
    print("QUESTS / OBJECTIVES (type 10 id 0)")
    print("=" * 72)
    if "100" in files:
        for key, raw in parse_strings(read("100")):
            s = printable(raw)
            if s:
                print(f"    [{key:04x}] {s[:150]}")

    print()
    print("=" * 72)
    print("CREATURE CATALOGUE (types 7/8/11, shared ids)")
    print("=" * 72)
    ids = sorted({int(f[1:], 16) for f in files
                  if f[0] == "7" and not f.startswith(("10", "11"))})
    for cid in ids:
        parts = [t for t, pre in (("sprite", "7"), ("anim", "8"), ("props", "11"))
                 if f"{pre}{cid:x}" in files]
        print(f"  id 0x{cid:02x}: " + ", ".join(parts))

    print()
    print("MISSING (server-supplied, lost): type 1 (placed entities), "
          "type 9 (map nodes)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../extracted/EoE-ShiradsForge")
