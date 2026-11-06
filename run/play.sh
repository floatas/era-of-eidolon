#!/bin/bash
# Launch an Era of Eidolon chapter against the local relay.
#   ./play.sh                 -> Shirad's Forge
#   ./play.sh SterlingLake    -> Sterling Lake
set -euo pipefail
cd "$(dirname "$0")/.."

GAME="${1:-ShiradsForge}"
RELAY="${RELAY:-http://127.0.0.1:8080/}"

# FreeJ2ME persists its key mapping in freej2me.conf and loads it at startup,
# overriding anything set before main(). Stock binds phone 0-9 to VK_NUMPAD0..9
# (96-105), which a laptop without a numeric keypad cannot produce — and the
# game enters hero names by multi-tap, so those keys are essential. Rebind to
# the top-row digits (VK_0..VK_9 = 48..57) every launch.
CONF=freej2me_system/freej2me.conf
if [ -f "$CONF" ]; then
    for n in 0 1 2 3 4 5 6 7 8 9; do
        sed -i '' "s/^input_Num${n}:.*/input_Num${n}:$((48 + n))/" "$CONF"
    done
fi

# Repack with the Relay property (FreeJ2ME reads it from the jar manifest, not
# the .jad). Originals in jars/ are never modified.
python3 run/mkjar.py "jars/EoE-${GAME}.jar" "run/EoE-${GAME}.jar" \
    "Relay=${RELAY}" "INFO=preservation"

# Start the relay when the jar points at this machine and nothing answers
# there yet, the way play-card.sh and play-town.sh start theirs. Without it
# the phone sits on "Loading..." for ever.
case "$RELAY" in
    http://127.0.0.1:*|http://localhost:*)
        PORT="${RELAY#http://*:}"
        PORT="${PORT%%/*}"
        if ! lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
            mkdir -p server/logs
            python3 -u server/relay.py "$PORT" >/dev/null 2>&1 &
            for _ in 1 2 3 4 5 6 7 8 9 10; do
                if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
                    break
                fi
                sleep 0.2
            done
        fi
        ;;
esac

# FreeJ2ME drops soft keys unless phone:Standard is set for this MIDlet-Name.
# Forge and Sterling Lake already have a config; copy Sterling's for a chapter
# that does not (Mistral Grove). Never overwrite one that is already there.
python3 - << PY
import os, zipfile
jar = "run/EoE-${GAME}.jar"
template = "config/Sterling Lake/game.conf"
with zipfile.ZipFile(jar) as z:
    mf = z.read("META-INF/MANIFEST.MF").decode("utf-8", "replace")
name = ""
for ln in mf.splitlines():
    if ln.startswith("MIDlet-Name:"):
        name = ln.split(":", 1)[1].strip()
dest = os.path.join("config", name, "game.conf")
if name and os.path.isfile(template) and not os.path.exists(dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(template) as src, open(dest, "w") as out:
        out.write(src.read())
PY

# FreeJ2ME scales the LCD to the frame and preserves aspect (its resize()), so
# simply enlarging the window zooms the game. The phone screen is 240x320 and
# the frame adds a little chrome; SCALE=2 gives a crisp 2x with no distortion.
SCALE="${SCALE:-2}"
(
    sleep 9
    osascript <<OSA >/dev/null 2>&1
tell application "System Events" to tell (first process whose name is "java")
  set position of window 1 to {60, 60}
  set size of window 1 to {$((240 * SCALE)), $((348 * SCALE))}
end tell
OSA
) &

# EoELauncher remaps the phone keypad off the numpad; the freej2me-net dir
# shadows FreeJ2ME's stubbed HttpConnectionImpl with one that really connects.
# Keep the emulator's own output too: the [net] lines from our
# HttpConnectionImpl, FreeJ2ME's missing-resource warnings, and any stack
# trace it prints. The game's own Error dialogs are not in here — gen 2 never
# reports them anywhere but the screen.
mkdir -p server/logs
exec java -Dfile.encoding=ISO_8859_1 \
     -cp tools/freej2me-net:tools/freej2me/freej2me.jar \
     EoELauncher "run/EoE-${GAME}.jar" 2>&1 | tee -a server/logs/emulator.log
