#!/usr/bin/env python3
"""Inject real HTTP support into freej2me-web's jar.

The upstream web build has no networking at all: its
javax.microedition.io.Connector.open() throws ConnectionNotFoundException for
every scheme except sms://. This replaces that class and adds an
HttpConnectionImpl built on java.net, which CheerpJ maps onto browser fetch.

    javac --release 8 -cp freej2me-web/web/freej2me-web.jar \
          -d tools/freej2me-web-net \
          tools/freej2me-web-net/javax/microedition/io/*.java
    python3 tools/patch_web_jar.py
"""

import os
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "freej2me-web", "web", "freej2me-web.jar")
PATCH = os.path.join(HERE, "freej2me-web-net")

CLASSES = [
    "javax/microedition/io/Connector.class",
    "javax/microedition/io/Connector$fakeIS.class",
    "javax/microedition/io/Connector$DummyOutputStream.class",
    "javax/microedition/io/HttpConnectionImpl.class",
]


def compile_net():
    """Build the HTTP classes as Java 8 (the .class files are not kept in git)."""
    base = os.path.join(PATCH, "javax", "microedition", "io")
    sources = [os.path.join(base, n) for n in sorted(os.listdir(base)) if n.endswith(".java")]
    against = SRC + ".orig" if os.path.exists(SRC + ".orig") else SRC
    subprocess.check_call([
        "javac", "--release", "8", "-cp", against, "-d", PATCH, *sources,
    ])


def compile_keyboard():
    """The browser emulator reads keys in FreeJ2ME. Rebuild that class as Java 8."""
    source = os.path.join(HERE, "freej2me-web", "src", "org", "recompile",
                          "freej2me", "FreeJ2ME.java")
    subprocess.check_call([
        "javac", "--release", "8", "-cp", SRC, "-d", PATCH, source,
    ])
    out = os.path.join(PATCH, "org", "recompile", "freej2me")
    found = []
    for name in sorted(os.listdir(out)):
        if name.startswith("FreeJ2ME") and name.endswith(".class"):
            found.append("org/recompile/freej2me/" + name)
    if not found:
        raise SystemExit("FreeJ2ME did not compile")
    return found


def main():
    if not os.path.exists(SRC):
        print(f"missing {SRC}")
        return 1
    compile_net()
    classes = CLASSES + compile_keyboard()
    backup = SRC + ".orig"
    if not os.path.exists(backup):
        shutil.copy2(SRC, backup)
        print(f"kept original at {backup}")

    new = {}
    for rel in classes:
        path = os.path.join(PATCH, rel)
        if not os.path.exists(path):
            print(f"missing compiled class: {path}")
            return 1
        with open(path, "rb") as fh:
            new[rel] = fh.read()

    tmp = SRC + ".tmp"
    with zipfile.ZipFile(backup) as zin, \
            zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename in new:
                continue
            zout.writestr(item, zin.read(item.filename))
        for rel, data in new.items():
            zout.writestr(rel, data)

    os.replace(tmp, SRC)
    print(f"patched {SRC}: " + ", ".join(os.path.basename(c) for c in classes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
