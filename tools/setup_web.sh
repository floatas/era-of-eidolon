#!/bin/bash
# Fetch the browser emulator (freej2me-web) and apply this project's edits.
#
# tools/freej2me-web is a clone of zb3/freej2me-web (GPL-3.0) and is not kept in
# this repo. Our changes to it live in tools/freej2me-web.patch (keyboard input in
# FreeJ2ME.java, the page frame in run.html, scaling in main.js) and
# tools/freej2me-web-extra/. run/web.sh calls this, then tools/patch_web_jar.py
# and tools/patch_web_launcher.py do the rest. Safe to run again.
set -euo pipefail
cd "$(dirname "$0")/.."

DIR=tools/freej2me-web
UPSTREAM=https://github.com/zb3/freej2me-web.git
COMMIT=c19416e   # "Use newer CheerpJ version to fix UTF-8 file names bug"

if [ ! -d "$DIR/.git" ]; then
    git clone --quiet "$UPSTREAM" "$DIR"
    git -C "$DIR" checkout --quiet "$COMMIT"
fi

if git -C "$DIR" apply --check ../freej2me-web.patch 2>/dev/null; then
    git -C "$DIR" apply ../freej2me-web.patch
    echo "applied tools/freej2me-web.patch"
elif git -C "$DIR" apply --reverse --check ../freej2me-web.patch 2>/dev/null; then
    :   # already applied
else
    echo "tools/freej2me-web.patch does not apply to $DIR; is it at $COMMIT?" >&2
    exit 1
fi

mkdir -p "$DIR/web/frame"
cp tools/freej2me-web-extra/frame/* "$DIR/web/frame/"
