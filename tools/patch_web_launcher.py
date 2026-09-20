#!/usr/bin/env python3
"""Teach freej2me-web's launcher to install a jar straight from a URL.

Upstream you install a game by hand through a file picker. For a hosted or
scripted setup we want `index.html?autojar=/EoE-ShiradsForge-web.jar` to fetch
the jar, install it and jump into the game.

The launcher already has everything needed; this just chains the three steps it
performs on a manual upload:

    processGameFile(buffer, name)   parse the jar, build a MIDletLoader
    doAddSaveGame()                 launcherUtil.initApp(...) -> installed
    location -> run?app=<appId>     what the game list links to

The original file is kept alongside as launcher.js.orig.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
JS = os.path.join(HERE, "freej2me-web", "web", "src", "launcher.js")

HOOK_CALL = """    document.getElementById("import-data-file").onchange = doImportData;
    document.getElementById("export-data-btn").onclick = doExportData;

    await eoeAutoInstall();
}"""

HOOK_ORIG = """    document.getElementById("import-data-file").onchange = doImportData;
    document.getElementById("export-data-btn").onclick = doExportData;
}"""

BLOCK = """

/* ---- added: install a jar from ?autojar=<url> and launch it -------------
   Lets the emulator be embedded or scripted without anyone touching the
   file picker. Same-origin fetch, so it works with the relay on one port. */
async function eoeAutoInstall() {
    const url = new URLSearchParams(location.search).get('autojar');
    if (!url) {
        return;
    }
    try {
        document.getElementById("loading").textContent = "Installing " + url + "...";
        document.getElementById("loading").style.display = "";
        const buf = await (await fetch(url)).arrayBuffer();
        await processGameFile(buf, url.split('/').pop());

        // CheerpJ refuses further Java calls while a thread is still running
        // ("Java code still running, check for a missing await"), so let the
        // event loop drain between steps rather than calling back into the
        // loader for the app id.
        await new Promise(r => setTimeout(r, 400));
        await doAddSaveGame();
        await new Promise(r => setTimeout(r, 400));

        // The installed game is now in the list. Match it by name rather than
        // position — the bundled demo games share the list and the order is
        // not insertion order.
        const want = (new URLSearchParams(location.search).get('name') || '').toLowerCase();
        const links = [...document.querySelectorAll('#game-list a')];
        const target = want
            ? links.find(a => a.textContent.toLowerCase().includes(want))
            : links[links.length - 1];
        if (target) {
            location.href = target.href;
        } else {
            document.getElementById("loading").textContent = 'installed - pick it from the list';
        }
    } catch (e) {
        console.error('autojar failed', e);
        document.getElementById("loading").textContent = 'autojar failed: ' + e;
    }
}
"""


def main():
    if not os.path.exists(JS):
        print(f"missing {JS}")
        return 1
    backup = JS + ".orig"
    if not os.path.exists(backup):
        shutil.copy2(JS, backup)
        print(f"kept original at {backup}")

    with open(backup) as fh:
        src = fh.read()

    if HOOK_ORIG not in src:
        print("could not find the end of main() to hook into")
        return 1

    src = src.replace(HOOK_ORIG, HOOK_CALL, 1) + BLOCK
    with open(JS, "w") as fh:
        fh.write(src)
    print(f"patched {JS}: added ?autojar= support")
    return 0


if __name__ == "__main__":
    sys.exit(main())
