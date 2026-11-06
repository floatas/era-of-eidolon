#!/usr/bin/env python3
"""Copy a MIDlet without the chapter patches.

run/mkjar.py rewrites Shirard's Forge text and maps and pokes d.class.
Town and card jars must not go through that. This copies the zip, sets
manifest keys, and replaces exact Java Utf8 constants. Originals in jars/
are never modified.

    python3 run/pack_plain.py SRC DST --utf8 OLD NEW [--manifest Key=Value]
"""

import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkjar

MANIFEST = "META-INF/MANIFEST.MF"
CONFIG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "config")
TEMPLATE = os.path.join(CONFIG, "Sterling Lake", "game.conf")


def pack(src, dst, utf8=None, manifest=None, config=True, keyboard=False):
    utf8 = utf8 or {}
    manifest = manifest or {}
    with zipfile.ZipFile(src) as zin:
        names = zin.namelist()
        mf = zin.read(MANIFEST).decode("utf-8", "replace") if MANIFEST in names else ""
        keep = []
        for ln in mf.splitlines():
            if not ln.strip():
                continue
            if ln.split(":", 1)[0].strip() in manifest:
                continue
            keep.append(ln)
        for key, val in manifest.items():
            keep.append(f"{key}: {val}")
        new_mf = ("\r\n".join(keep) + "\r\n\r\n") if keep else mf
        midlet = ""
        for ln in new_mf.splitlines():
            if ln.startswith("MIDlet-Name:"):
                midlet = ln.split(":", 1)[1].strip()
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
            for n in names:
                data = new_mf.encode("utf-8") if n == MANIFEST else zin.read(n)
                if n.endswith(".class") and utf8:
                    data = mkjar.rewrite_strings(data, utf8)
                zout.writestr(zin.getinfo(n), data)
    if config and midlet and os.path.isfile(TEMPLATE):
        dest = os.path.join(CONFIG, midlet, "game.conf")
        if not os.path.exists(dest):
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(TEMPLATE) as src_fh, open(dest, "w") as dst_fh:
                dst_fh.write(src_fh.read())
    if keyboard:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        asm = os.path.join(root, "tools", "microemu", "asm-3.3.1.jar")
        subprocess_check(asm, dst)
    return midlet


def subprocess_check(asm, jar):
    import subprocess
    cmd = ["java", "-cp", asm + os.pathsep + os.path.dirname(os.path.abspath(__file__)),
           "KeyboardPatch", jar]
    subprocess.check_call(cmd)


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    src, dst = argv[1], argv[2]
    utf8 = {}
    manifest = {}
    keyboard = False
    i = 3
    while i < len(argv):
        if argv[i] == "--utf8" and i + 2 < len(argv):
            utf8[argv[i + 1]] = argv[i + 2]
            i += 3
        elif argv[i] == "--manifest" and i + 1 < len(argv):
            key, val = argv[i + 1].split("=", 1)
            manifest[key] = val
            i += 2
        elif argv[i] == "--keyboard":
            keyboard = True
            i += 1
        else:
            print(f"unrecognised {argv[i]}")
            return 1
    name = pack(src, dst, utf8, manifest, keyboard=keyboard)
    print(f"{dst}: MIDlet-Name={name}"
          + ("" if not utf8 else "  utf8=" + ",".join(utf8.values())))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
