# Working on this cheaply

Read this first in a new session. It is here because the expensive part of
this project is not the work, it is carrying the history of the work.

## The loop

    tools/check.sh              0.8s   tests, chapter summary, anomalies
    tools/probe.py <game> [loc] 0.3s   what is actually in a location
    tools/fightplan.py          ~20s   is each fight winnable when you reach it
    server/test_server.py       0.1s   the assertions alone
    tools/harness/regress.py    ~60s   boots all three chapters and plays them
    tools/atlas.py <game>       ~20s   redraw a sheet, only when a human will look

The first four print text. The last two make pictures. Pictures are for
people, not for checking: a screenshot costs more to look at than most fixes
cost to make. `probe.py ShiradsForge 16` would have answered "the Crypt is
missing its tiles" in one command; three crops of a PNG answered it eventually
and cost perhaps fifty times as much.

## What to reach for

| question | command |
|---|---|
| did I break anything | `tools/check.sh` |
| what is in this room | `tools/probe.py <game> <loc>` |
| where do its doors go, and are they marked | same |
| is a creature standing somewhere impossible | `tools/check.sh`, anomalies |
| can a level-4 hero survive Dwarven Hall | `tools/fightplan.py` |
| does the game still boot and play | `tools/harness/regress.py` |
| does it *look* right | `tools/atlas.py`, and only then |

## Ground rules that keep it cheap

**Ask for the number, not the picture.** Almost every question about the world
has a numeric answer. Render when you want to enjoy it.

**Batch the changes.** Four fixes then one look beats four rounds of fix,
render, look.

**Start a new session per subject.** The history is the cost multiplier, and
the notes in this folder carry what matters: `recovered/` for the real tables,
`FLOW.md` for the route, `MISSING.md` for what is still gone, `ARENA.md` for
the other engine, `eoe-arena/SOURCE.md` for where the numbers came from.

**One chapter is ground truth.** Shirad's Forge runs on watAgame's own tables;
the other two are reconstruction. Any rule you invent can be tested against
the chapter where the answer is known.
