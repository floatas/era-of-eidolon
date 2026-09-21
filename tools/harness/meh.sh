#!/bin/sh
# Run a jar headless under MicroEmulator and print what the game did.
#
#   tools/harness/meh.sh run/EoE-ShiradsForge.jar "boot:Scout,state"
#
# MEH_RMS=file keeps records between runs (resume an existing hero);
# the default, memory, starts every run from a clean account.
#
# The emulator jars are not in the repo; the first run fetches them.
set -e
root=$(cd "$(dirname "$0")/../.." && pwd)
lib="$root/tools/microemu"

fetch() {
    url=$1
    file=$lib/$(basename "$url")
    [ -f "$file" ] || curl -sSLf -o "$file" "$url"
}

if [ ! -f "$lib/microemu-javase-2.0.4.jar" ] || [ ! -f "$lib/asm-3.3.1.jar" ]; then
    mkdir -p "$lib"
    base=https://repo1.maven.org/maven2
    for m in javase javase-swing cldc midp device-large injected; do
        fetch "$base/org/microemu/microemu-$m/2.0.4/microemu-$m-2.0.4.jar"
    done
    # MicroEmulator rewrites the MIDlet's bytecode as it loads it
    for a in asm asm-commons asm-tree; do
        fetch "$base/asm/$a/3.3.1/$a-3.3.1.jar"
    done
fi

java=${JAVA:-/opt/homebrew/opt/openjdk/bin/java}
cp=$(find "$lib" -name '*.jar' ! -name '*sources*' | tr '\n' ':')
exec "$java" \
    -Djava.awt.headless=true \
    -Dmeh.rms="${MEH_RMS:-memory}" \
    -cp "$root/tools/harness:$root/tools/harness/nokia:$cp" MEHarness "$@"
