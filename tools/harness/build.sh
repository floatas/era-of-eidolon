#!/bin/sh
# Compile the headless harness and its Nokia stub.
set -e
root=$(cd "$(dirname "$0")/../.." && pwd)
lib="$root/tools/microemu"
javac=${JAVAC:-/opt/homebrew/opt/openjdk/bin/javac}
cp=$(find "$lib" -name '*.jar' ! -name '*sources*' | tr '\n' ':')
"$javac" -nowarn -d "$root/tools/harness/nokia" \
    "$root/tools/harness/nokia/com/nokia/mid/ui/DeviceControl.java"
"$javac" -nowarn -d "$root/tools/harness/mepatch" -cp "$cp" \
    "$root/tools/harness/mepatch/org/microemu/device/ui/EventDispatcher.java"
"$javac" -nowarn -d "$root/tools/harness" -cp "$cp" "$root/tools/harness/MEHarness.java"
