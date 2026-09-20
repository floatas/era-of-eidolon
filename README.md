# Era of Eidolon — preservation archive

watAgame ApS (Copenhagen, founded 2003). One of the first genuinely *online* mobile
RPGs; J2ME MIDlets for Nokia S30/S40/S60, Sony Ericsson and Siemens handsets.
Servers dead; `eraofeidolon.com` lapsed and was squatted in 2019.

## World structure (from the archived official site, 2004)

Three regions, each ruled by one of three sisters, each with a capital town:

| Region  | Release | Queen    | Town     |
|---------|---------|----------|----------|
| Blissmor| first   | Sorena   | Orumant  |
| Vulcor  | second  | Furyana  | Dagonar  |
| Mystor  | third   | Arsenica | Ravarcil |

Later standalone chapters: **Sterling Lake**, **Shirad's Forge** (the latter billed
as concluding the three-kingdoms arc).

## What's in jars/

| File | MIDlet-Name | Version | Vendor | Source |
|------|-------------|---------|--------|--------|
| `EoE-Orumant-no30-trial.jar` | EoE Orumant | 5.2.8 (MIDP-1.0) | watAgame | Wayback, wap.pokeplay.com, capture 2004-12-29 |
| `EoE-SterlingLake.jar` | Sterling Lake | 1.1.1 (MIDP-2.0) | watAgame /brought to you by pascha | dertz.in |
| `EoE-ShiradsForge.jar` | Shirard's Forge | 1.1.0 (MIDP-2.0) | watAgame /brought by pascha | dertz.in |

Still missing: **Dagonar**, **Ravarcil**, and the full (non-trial) Orumant.
Not present in the Kahvibreak / Flashpoint J2ME corpus (checked all 7,543 titles
in the M5-Dev/j2me-vault mirror — zero Eidolon entries). These are genuinely rare.

## Server endpoints (extracted from bytecode)

    Orumant        http://81.7.141.67/1/
    Shirad's Forge http://4.eraofeidolon.com/2/
    Sterling Lake  http://5.eraofeidolon.com/2/

Superseded — see `protocol/PROTOCOL.md` for the full reverse-engineered protocol.
Short version: the real gen-2 hosts are `prod4.eraofeidolon.com` and
`prod5.eraofeidolon.com` (the `prod` prefix is a separate static field), endpoints
are numbered `<opcode>.pl`, and **both gen-2 clients honour a `Relay` JAD property
plus an `X-relay-url` header** — so they can be redirected to a local server with
no binary patching. Orumant (gen 1) has no relay hook and a hardcoded raw IP.

Dagonar and Ravarcil cannot be derived from the Orumant JAR: it carries its own
town art and intro text, and no town-selection parameter exists in the binary.

## Project layout

    jars/        original untouched MIDlets
    extracted/   unzipped jar contents, per game
    decompiled/  CFR 0.152 Java sources, per game
    assets/      all 30 PNGs, prefixed by game
    protocol/    PROTOCOL.md + javap disassembly of the gen-2 network thread
    notes/       official 2004 site pages, game-rules PDF, 7 JAD descriptors
    tools/       freej2me 1.52, cfr.jar

## Current playability

FreeJ2ME-Plus 1.52 in `tools/freej2me` (needs Java; tested on JDK 11 arm64):

    java -jar -Dfile.encoding=ISO_8859_1 tools/freej2me/freej2me.jar jars/<file>.jar

- **Orumant** — boots, splash screen renders (title + Queen Sorena), then stalls
  on HTTP to 81.7.141.67.
- **Sterling Lake** / **Shirad's Forge** — boot, then sit on
  `Loading... / Retry no: N / 0.00 MB`, streaming assets from the dead hosts.

All three are **server-blocked, not emulator-blocked**. Making them playable means
standing up a replacement content server and redirecting the hardcoded host.

## notes/

- `EOE-GAME-RULES-0.2.pdf` — official 8-page rules document (2004)
- `site-world.html`, `site-story.html`, `site-game.html` — archived official site
- `*.jad` — 7 MIDlet descriptors (Nokia S30/S40/S60, SonyEricsson K500/K700/T610, Siemens M55)
EOE
ls -R . | head -30; echo; du -sh .
## Asset completeness (measured)

Resource key is `"/" + type + Integer.toHexString(id)` (`g.java:368`). On a miss,
`g.d(type,id,vector)` adds `(type<<8)|id` to a **want-list** the client sends to
the server — so any resource not in the JAR was streamed on demand.

**Orumant — thin client, no game content.**
5 classes + 16 PNGs, zero data resources. The PNGs are UI chrome and paper-doll
parts only (`torso`, `legs`, `weapons`, `ammu`, `battlefield`, `town`,
`background`). Every bit of actual game content came from `81.7.141.67`.
Nothing to salvage offline beyond the art.

**Sterling Lake / Shirad's Forge — look chapter-complete.**
74 and 66 bundled resources respectively, plus 7 PNGs and a MIDI each.

    type        Shirad's Forge          Sterling Lake
    0,4,5,6,10  single ids              single ids
    2, 3        0x01-0x12 contiguous    0x14-0x24 contiguous
    7, 8, 11    11 ids, sparse          9 ids, sparse

Two things say this is a curated per-chapter slice rather than a partial cache:
types 2/3 are **contiguous** within each game and the two games occupy
**disjoint** ranges (0x01-0x12 vs 0x14-0x24), i.e. a shared global catalogue
carved into chapters; and types 7/8/11 carry the **same sparse id set as each
other** within a game (three parallel views of one cast — sprite/palette/stats),
which is coherent, not random.

Caveat: this cannot be *proven* without a server, because the engine is designed
to fetch anything it lacks. But the blocker for these two is the session
handshake, not missing art.

## Running against a local server

FreeJ2ME-Plus's `HttpConnectionImpl` is a **stub** — `connect()` only logs,
`getResponseCode()` returns a hardcoded 200, and `openInputStream()` returns the
literal bytes `resource://!blank`. It never touches the network, so any MIDlet
speaking a real protocol fails its first sanity check and retries forever.

`tools/freej2me-net/` holds a drop-in replacement with real networking. Put it
ahead of freej2me.jar on the classpath and it shadows the stub:

    javac -cp tools/freej2me/freej2me.jar -d tools/freej2me-net \
          tools/freej2me-net/javax/microedition/io/HttpConnectionImpl.java

    # 1. relay
    python3 server/relay.py 8080

    # 2. patched jar (originals in jars/ stay untouched)
    cd run && python3 mkjar.py ../jars/EoE-ShiradsForge.jar EoE-ShiradsForge.jar \
        Relay=http://127.0.0.1:8080/ INFO=preservation

    # 3. game
    java -Dfile.encoding=ISO_8859_1 \
         -cp tools/freej2me-net:tools/freej2me/freej2me.jar \
         org.recompile.freej2me.FreeJ2ME run/EoE-ShiradsForge.jar

Note: FreeJ2ME *does* read an accompanying `.jad`, but the `Relay` property only
takes effect from the jar manifest, which is what `mkjar.py` writes.

**The catalogue is recovered.** 167 named weapons, armours, skills, spells and
charms scraped from the official site via the Wayback Machine
(`notes/CATALOGUE.md`), plus both versions of watAgame's own rules PDF in
`notes/`. Only the per-item numbers were never published.

**Character system**: the six stats, their descriptions, the raise-cost curve
and the shop categories are all compiled into the client and have been
recovered — see the CORRECTION section in `protocol/PROTOCOL.md`. Hero sheet,
skills, spells, rankings and help are implemented; XP, levels and gold work.

**Logs** land in `server/logs/` — `relay.log` (decoded protocol + world state
per turn) and `emulator.log`. Note the client never reports its own errors
upstream, so in-game Error boxes are screen-only; `protocol/PROTOCOL.md`
explains how to read them.

**It also runs in a browser** — `./run/web.sh`, then open the URL it prints.
CheerpJ runs FreeJ2ME, and the emulator and game server share one origin so the
MIDlet's HTTP needs no CORS. See `protocol/PROTOCOL.md`.

**Save and resume work** the way the original did — the client stores a token,
the server owns the account, and "Select hero" comes back on relaunch. Saves
live in `server/saves/game.json`.

**Status: Shirad's Forge plays.** Both game modes work — turn-based combat
(path movement on an action-point budget, attacks, damage, death, healing,
creature AI) and free-roam exploration with the adventure HUD, reached by
winning a fight. `server/world.py` holds the game state: the 18 tilemaps and
their walkability, creature spawns, and the type 1 entity tables (exits).

Older summary: Title screen, character creation, main
menu, the Village rendering from its own tilemap, turn-based combat with both
sprites drawn, path-based movement with action points, and a complete
end-turn round trip. All served by `server/relay.py`;
`server/handlers.py` is hot-reloaded per request (relay.py itself is not —
restart it after editing).

    python3 server/relay.py 8080      # terminal 1
    ./run/play.sh                     # terminal 2
    ./run/drive.sh move               # or: script the whole thing
