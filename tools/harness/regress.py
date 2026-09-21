#!/usr/bin/env python3
"""Everything that can be checked without a person watching.

    tools/harness/regress.py

Runs the server's own assertions, then plays the game: boots a hero, walks,
crosses a doorway, saves, and resumes. Every bug this project has hit was
found by hand; this is the part of that which a machine can repeat.

The emulator runs are the slow half, about twelve seconds a chapter, so
server-only changes are still better checked with test_server.py alone.
"""

import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEH = os.path.join(ROOT, "tools", "harness", "meh.sh")
RELAY = "http://127.0.0.1:8080/"

GREEN, RED, DIM, OFF = "\033[32m", "\033[31m", "\033[2m", "\033[0m"
FAILED = []


def check(name, cond, detail=""):
    print(f"  {GREEN}ok{OFF}   {name}" if cond
          else f"  {RED}FAIL{OFF} {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        FAILED.append(name)


def relay_up():
    try:
        urllib.request.urlopen(RELAY, timeout=2)
        return True
    except urllib.error.HTTPError:
        return True
    except OSError:
        return False


def play(jar, script, rms="memory"):
    """Run one scripted session and return its STATE lines as dicts."""
    env = dict(os.environ, MEH_RMS=rms)
    out = subprocess.run([MEH, os.path.join(ROOT, "run", jar), script],
                         capture_output=True, text=True, env=env,
                         timeout=180).stdout
    states = []
    for line in out.splitlines():
        if line.startswith("STATE "):
            d = dict(re.findall(r"(\w+)=(\S+)", line))
            states.append(d)
    return states, out


def chapter(jar, name):
    print(f"\n{name}")
    hero = "Regress"

    # boot, look around, walk
    states, out = play(jar, f"boot:{hero},state,goto:99:99:6000,state")
    check(f"{name}: boots to the map",
          bool(states) and states[0].get("screen") == "d",
          states[0] if states else "no state at all")
    if not states or states[0].get("screen") != "d":
        print(DIM + out.strip()[-400:] + OFF)
        return
    first = states[0]
    check(f"{name}: starts out of combat", first.get("inCombat") == "false")
    check(f"{name}: the map is loaded", first.get("loaded") == "true")
    check(f"{name}: something is drawn besides the hero",
          int(first.get("entities", 0)) > 1, first.get("entities"))
    last = states[-1]
    check(f"{name}: the hero walks",
          (last.get("heroX"), last.get("heroY"))
          != (first.get("heroX"), first.get("heroY")),
          f"stayed at {first.get('heroX')},{first.get('heroY')}")
    check(f"{name}: no error dialog while walking",
          "NullPointerException" not in out and "Unable to get" not in out,
          next((l for l in out.splitlines() if "text=" in l), ""))


def transition():
    print("\ncrossing a doorway, and coming back to it")
    # the doorway north-east of the Shirad's Forge spawn. goto steers by the
    # hero's real position, so the walk does not depend on emulator timing.
    walk = "boot:Keeper,goto:10:10,wait:2500,state"
    states, out = play("EoE-ShiradsForge.jar", walk)
    moved = states and states[-1].get("location") != "1"
    check("a doorway moves you to another location", bool(moved),
          states[-1].get("location") if states else "no state")
    if not moved:
        return
    where = (states[-1]["location"], states[-1]["heroX"], states[-1]["heroY"])

    # ... and save there, on a record store that survives the run
    states, out = play("EoE-ShiradsForge.jar",
                       walk + ",key:-7,wait:900,choose:Save & exit,wait:900,"
                              "choose:Save & exit,wait:1500", rms="file")
    check("Save & exit reaches the server", "opcode=9" in relay_tail(),
          "no opcode 9 in the relay log")

    states, out = play("EoE-ShiradsForge.jar", "boot:Keeper,state", rms="file")
    back = (states[-1].get("location"), states[-1].get("heroX"),
            states[-1].get("heroY")) if states else None
    check("resuming puts you back where you saved", back == where,
          f"saved at {where}, resumed at {back}")


def relay_tail(lines=40):
    path = os.path.join(ROOT, "server", "logs", "relay.log")
    try:
        with open(path, errors="replace") as fh:
            return "".join(fh.readlines()[-lines:])
    except OSError:
        return ""


def main():
    print("server")
    rc = subprocess.run([sys.executable,
                         os.path.join(ROOT, "server", "test_server.py")],
                        capture_output=True, text=True)
    failed = [l for l in rc.stdout.splitlines() if "FAIL" in l]
    check("test_server.py passes", rc.returncode == 0,
          f"{len(failed)} checks failed; run it directly")

    if not relay_up():
        print(f"\n{RED}relay is not running{OFF} — start it with:"
              f"\n  (cd server && python3 -u relay.py 8080 &)")
        return 2

    for jar, name in (("EoE-ShiradsForge.jar", "Shirad's Forge"),
                      ("EoE-SterlingLake.jar", "Sterling Lake"),
                      ("EoE-MistralGrove.jar", "Mistral Grove")):
        chapter(jar, name)
    transition()

    print()
    if FAILED:
        print(f"{RED}{len(FAILED)} failed{OFF}: " + ", ".join(FAILED))
        return 1
    print(f"{GREEN}all checks passed{OFF}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
