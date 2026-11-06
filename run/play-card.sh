#!/bin/bash
# Launch a Badaz card game.
#   ./play-card.sh              -> Poker
#   ./play-card.sh Blackjack    -> Blackjack
#
# After the splash (about four seconds) the phone asks Online or Offline.
# Offline opens the town and the Gaming Den deals a local table. Online
# asks for a nickname and a password. New user stores it, and Existing
# user has to type the same one. Then a hero name. Goblin is you
# against the offline opponents. Public waits for a second player. Gold is
# kept in server/saves/cards.sqlite. Rankings, mail, and the shop were not
# in the jars. This does not point the jar at the chapter relay.
# On a computer: arrow keys move, Enter confirms, Escape goes back, and
# letter keys type into a nickname or password. Backspace deletes.
set -euo pipefail
cd "$(dirname "$0")/.."

WHICH="${1:-Poker}"
PORT="${PORT:-8082}"
# The phone builds http://prod + this host. The "prod" constant is cleared
# so the request is http://127.0.0.1:PORT/3/<opcode>.pl. Blackjack has no
# Relay property, so both jars are pointed here the same way.
BASE="127.0.0.1:${PORT}/3/"
case "$WHICH" in
    Poker)
        SRC=jars/EoE-BadazPoker-v1.0.2.jar
        OLD=11.eraofeidolon.com/3/
        DST=run/EoE-BadazPoker.jar
        ;;
    Blackjack)
        SRC=jars/EoE-Blackjack-v1.0.0.jar
        OLD=10.eraofeidolon.com/3/
        DST=run/EoE-Blackjack.jar
        ;;
    *)
        echo "usage: ./run/play-card.sh [Poker|Blackjack]" >&2
        exit 1
        ;;
esac

CONF=freej2me_system/freej2me.conf
if [ -f "$CONF" ]; then
    for n in 0 1 2 3 4 5 6 7 8 9; do
        sed -i '' "s/^input_Num${n}:.*/input_Num${n}:$((48 + n))/" "$CONF"
    done
fi

python3 run/pack_plain.py "$SRC" "$DST" --utf8 "$OLD" "$BASE" --utf8 prod "" --keyboard

if ! lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    mkdir -p server/logs
    python3 -u server/cards.py "$PORT" >> server/logs/cards.log 2>&1 &
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
