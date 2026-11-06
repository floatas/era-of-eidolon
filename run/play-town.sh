#!/bin/bash
# Launch an Arena town against the local town server.
#   ./play-town.sh              -> Orumant
#   ./play-town.sh Dagonar      -> Dagonar
#
# The phone has the town picture and the menus. Shelves, ranks, help text,
# portraits, clans, and fight boards were not in the jar, so those screens
# open empty. Originals in jars/ are not modified.
# On a computer: arrow keys move, Enter confirms, Escape goes back, and
# letter keys type into a nickname or password. Backspace deletes.
set -euo pipefail
cd "$(dirname "$0")/.."

WHICH="${1:-Orumant}"
PORT="${PORT:-8081}"
BASE="http://127.0.0.1:${PORT}/1/"

case "$WHICH" in
    Orumant)
        SRC=jars/EoE-Orumant-v5.2.10.jar
        OLD=http://81.7.141.67/1/
        DST=run/EoE-Orumant.jar
        ;;
    Dagonar)
        SRC=jars/EoE-Dagonar-v5.4.3.jar
        OLD=http://prod1.eraofeidolon.com/1/
        DST=run/EoE-Dagonar.jar
        ;;
    *)
        echo "usage: ./run/play-town.sh [Orumant|Dagonar]" >&2
        exit 1
        ;;
esac

CONF=freej2me_system/freej2me.conf
if [ -f "$CONF" ]; then
    for n in 0 1 2 3 4 5 6 7 8 9; do
        sed -i '' "s/^input_Num${n}:.*/input_Num${n}:$((48 + n))/" "$CONF"
    done
fi

python3 run/pack_plain.py "$SRC" "$DST" --utf8 "$OLD" "$BASE" --keyboard

if ! lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    mkdir -p server/logs
    python3 -u server/arena.py "$PORT" >> server/logs/arena.log 2>&1 &
    for _ in 1 2 3 4 5 6 7 8 9 10; do
        if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
            break
        fi
        sleep 0.2
    done
fi

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

mkdir -p server/logs
exec java -Dfile.encoding=ISO_8859_1 \
     -cp tools/freej2me-net:tools/freej2me/freej2me.jar \
     EoELauncher "$DST" 2>&1 | tee -a server/logs/emulator.log
