#!/bin/bash
# Play Era of Eidolon in a browser.
#
# One origin serves both the CheerpJ emulator and the game server, so the
# MIDlet's HTTP is same-origin and no CORS is involved.
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${PORT:-8000}"
GAME="${1:-ShiradsForge}"
# Baked into the jar. Use the public name when the page is not on this machine.
HOST="${HOST:-localhost:${PORT}}"

# Real HTTP for the web build (upstream has none) and ?autojar= support.
python3 tools/patch_web_jar.py
python3 tools/patch_web_launcher.py

# Chapters keep the relay. The online jars take a keyboard and talk to this
# same origin: /3/ for the card tables, /1/ for the towns.
NAME=shirard
case "$GAME" in
    ShiradsForge|SterlingLake|MistralGrove)
        python3 run/mkjar.py "jars/EoE-${GAME}.jar" "run/EoE-${GAME}-web.jar" \
            "Relay=http://${HOST}/relay" "INFO=web"
        DST="run/EoE-${GAME}-web.jar"
        case "$GAME" in
            SterlingLake) NAME=sterling ;;
            MistralGrove) NAME=mistral ;;
        esac
        ;;
    Poker)
        python3 run/pack_plain.py jars/EoE-BadazPoker-v1.0.2.jar run/EoE-BadazPoker-web.jar \
            --utf8 11.eraofeidolon.com/3/ "${HOST}/3/" --utf8 prod "" --keyboard
        DST=run/EoE-BadazPoker-web.jar
        NAME=poker
        ;;
    Blackjack)
        python3 run/pack_plain.py jars/EoE-Blackjack-v1.0.0.jar run/EoE-Blackjack-web.jar \
            --utf8 10.eraofeidolon.com/3/ "${HOST}/3/" --utf8 prod "" --keyboard
        DST=run/EoE-Blackjack-web.jar
        NAME=blackjack
        ;;
    Orumant)
        python3 run/pack_plain.py jars/EoE-Orumant-v5.2.10.jar run/EoE-Orumant-web.jar \
            --utf8 http://81.7.141.67/1/ "http://${HOST}/1/" --keyboard
        DST=run/EoE-Orumant-web.jar
        NAME=orumant
        ;;
    Dagonar)
        python3 run/pack_plain.py jars/EoE-Dagonar-v5.4.3.jar run/EoE-Dagonar-web.jar \
            --utf8 http://prod1.eraofeidolon.com/1/ "http://${HOST}/1/" --keyboard
        DST=run/EoE-Dagonar-web.jar
        NAME=dagonar
        ;;
    *)
        echo "usage: ./run/web.sh [ShiradsForge|SterlingLake|MistralGrove|Poker|Blackjack|Orumant|Dagonar]" >&2
        exit 1
        ;;
esac
cp "$DST" "tools/freej2me-web/web/EoE.jar"

echo
echo "  open http://localhost:${PORT}/?autojar=/EoE.jar&name=${NAME}"
echo
echo "  Arrow keys move, Enter confirms, Escape goes back."
echo "  In Poker, Blackjack, Orumant, and Dagonar, letter keys type."
echo
exec python3 server/webserve.py "$PORT"
