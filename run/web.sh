#!/bin/bash
# Play Era of Eidolon in a browser.
#
# One origin serves both the CheerpJ emulator and the game server, so the
# MIDlet's HTTP is same-origin and no CORS is involved.
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${PORT:-8000}"
GAME="${1:-ShiradsForge}"

# Real HTTP for the web build (upstream has none) and ?autojar= support.
python3 tools/patch_web_jar.py
python3 tools/patch_web_launcher.py

# A jar whose Relay points back at this origin.
python3 run/mkjar.py "jars/EoE-${GAME}.jar" "run/EoE-${GAME}-web.jar" \
    "Relay=http://localhost:${PORT}/relay" "INFO=web"
cp "run/EoE-${GAME}-web.jar" "tools/freej2me-web/web/EoE.jar"

echo
echo "  open http://localhost:${PORT}/?autojar=/EoE.jar&name=shirard"
echo
exec python3 server/webserve.py "$PORT"
