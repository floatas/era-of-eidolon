#!/usr/bin/env python3
"""Repack a MIDlet with extra manifest attributes.

FreeJ2ME reads app properties from META-INF/MANIFEST.MF only — it never parses
the .jad — so the `Relay` property has to live in the manifest. Everything else
in the jar is copied byte-for-byte; originals in ../jars/ are never touched.

    python3 mkjar.py ../jars/EoE-ShiradsForge.jar EoE-ShiradsForge.jar \
        Relay=http://127.0.0.1:8080/ INFO=preservation
"""

import shutil
import sys
import zipfile

MANIFEST = "META-INF/MANIFEST.MF"


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    src, dst, kvs = sys.argv[1], sys.argv[2], sys.argv[3:]
    extra = dict(kv.split("=", 1) for kv in kvs)

    with zipfile.ZipFile(src) as zin:
        names = zin.namelist()
        if MANIFEST not in names:
            print(f"no {MANIFEST} in {src}")
            return 1
        mf = zin.read(MANIFEST).decode("utf-8", "replace")

        # drop any existing copies of the keys we are setting, keep the rest
        keep = [ln for ln in mf.splitlines()
                if ln.strip() and ln.split(":", 1)[0].strip() not in extra]
        for k, v in extra.items():
            keep.append(f"{k}: {v}")
        new_mf = "\r\n".join(keep) + "\r\n\r\n"

        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
            for n in names:
                data = new_mf.encode("utf-8") if n == MANIFEST else zin.read(n)
                zout.writestr(zin.getinfo(n), data)

    print(f"{dst}: set " + ", ".join(f"{k}={v}" for k, v in extra.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
