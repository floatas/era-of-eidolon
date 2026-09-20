#!/bin/bash
# Drive the game from launch to a committed move, via synthetic keystrokes.
# Useful for testing the server loop without hand-playing every time.
#
#   ./drive.sh            launch, create hero, enter combat
#   ./drive.sh move       ... then lay a 3-tile path and end the turn
#
# Screenshots land in /tmp/eoe-*.png.
set -uo pipefail
cd "$(dirname "$0")/.."

snap() {
    local b x y w h
    # Raise it first — screencapture -R grabs whatever is on top at those
    # coordinates, so an unfocused window yields a picture of the terminal.
    osascript -e 'tell application "System Events" to set frontmost of (first process whose name is "java") to true' >/dev/null 2>&1
    sleep 0.4
    b=$(osascript -e 'tell application "System Events" to tell (first process whose name is "java") to get {position, size} of window 1' 2>/dev/null) || return
    x=$(echo "$b" | cut -d, -f1 | tr -d ' '); y=$(echo "$b" | cut -d, -f2 | tr -d ' ')
    w=$(echo "$b" | cut -d, -f3 | tr -d ' '); h=$(echo "$b" | cut -d, -f4 | tr -d ' ')
    screencapture -x -o -R"${x},${y},${w},${h}" "/tmp/eoe-$1.png"
}

key() { osascript -e "tell application \"System Events\" to key code $1" >/dev/null 2>&1; sleep "${2:-0.5}"; }
typ() { osascript -e "tell application \"System Events\" to keystroke \"$1\"" >/dev/null 2>&1; sleep "${2:-0.5}"; }
focus() { osascript -e 'tell application "System Events" to set frontmost of (first process whose name is "java") to true' >/dev/null 2>&1; sleep 0.5; }

ENTER=36; UP=126; DOWN=125; LEFT=123; RIGHT=124

pkill -f EoELauncher 2>/dev/null; sleep 1
GAME="${GAME:-ShiradsForge}" ./run/play.sh "${GAME:-ShiradsForge}" > /tmp/eoe-fj.log 2>&1 &
sleep 14
focus

key $ENTER 2.5          # title screen
# Multi-tap the hero name. Same key within 1000ms cycles the letter, a
# different key commits immediately (c.java), so leave a gap between repeats.
typ 2 1.2               # a
typ 6 1.2               # m
typ 2 1.2               # a
key $DOWN 0.5; key $ENTER 1.2    # gender
key $DOWN 0.5; key $ENTER 1.5    # create hero
key $DOWN 0.4; key $ENTER 3      # main menu -> Start game
key $ENTER 4.5                   # enter the world
snap combat

if [ "${1:-}" = "attack" ]; then
    # Slot 1 is Attack (mode 2 = pick a target tile). In cursor mode RIGHT is
    # +x and DOWN is +y (d.java:1297), so from the hero at 12,17 two RIGHTs
    # land on the Gorrak at 14,17.
    key $RIGHT 0.5      # action bar: slot 0 -> slot 1
    key $ENTER 1.2      # open the Attack slot
    key $ENTER 1.2      # activate -> target mode
    key $RIGHT 0.5; key $RIGHT 0.5
    snap target
    key $ENTER 1.2      # queue the attack
    for _ in 1 2 3 4 5; do key $RIGHT 0.35; done   # -> End turn slot
    key $ENTER 1.0
    key $ENTER 3.5
    snap result
fi

if [ "${1:-}" = "move" ]; then
    key $ENTER 1.2      # open the Movement slot
    key $ENTER 1.2      # activate Move -> path mode
    key $UP 0.5; key $UP 0.5; key $UP 0.5
    snap path
    key $ENTER 1.2      # queue the action
    # Slot 6 is the End turn / Try to flee menu (d.java constructor). With two
    # entities the bar wraps at 7, so six RIGHTs from slot 0 lands on it.
    for _ in 1 2 3 4 5 6; do key $RIGHT 0.35; done
    key $ENTER 1.0
    key $ENTER 3.0      # End turn -> opcode 13
    snap result
fi

echo "screenshots: /tmp/eoe-*.png"

if [ "${1:-}" = "fight" ]; then
    # Attack whatever is adjacent, end turn, repeat until the area is clear.
    for round in 1 2 3 4 5; do
        key $RIGHT 0.4          # action bar -> Attack
        key $ENTER 1.0          # open the slot
        key $ENTER 1.0          # activate -> target mode
        key $ENTER 1.0          # queue on the current tile
        for _ in 1 2 3 4 5; do key $RIGHT 0.3; done
        key $ENTER 0.9
        key $ENTER 3.5          # End turn
        snap "fight$round"
    done
fi
