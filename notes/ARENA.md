# The other game: EoE Town / Arena

`jars/EoE-Dagonar-v5.3.3.jar` and `jars/EoE-Orumant-v5.2.10.jar` are not
chapters. They are a different game on a different engine, and finding them
changes what this project is looking at.

    MIDlet-1: EoE Dagonar, /icon.png, com.watAgame.eoe_town.EoETown
    MicroEdition-Profile: MIDP-1.0     MicroEdition-Configuration: CLDC-1.0

Five classes, sixteen PNGs, and the PNG names say what it is: `battlefield`,
`challenge`, `cursor`, `torso`, `legs`, `mail`, `ammu`, `town`. Armour slots, a
challenge screen, a mailbox, a town. This is the gladiator game — the same one
`lachtos/eoe-arena` remakes, and therefore the game whose item and skill
statistics that remake carries (see `eoe-arena/SOURCE.md`).

The chapters — Shirad's Forge, Sterling Lake, Mistral Grove — are the other
half of the series: MIDP-2.0, main class `Main`, isometric, single-player
quests against a binary TLV protocol.

## Its protocol is named, not binary

Where the chapters speak the `0xBABE` tag/type/length protocol in
`protocol/PROTOCOL.md`, the town client calls CGI scripts by name against

    http://81.7.141.67/1/

Sixty-four of them, recovered from the constant pool:

    login register betaentry version ping submit pay errorreport
    charselectcreate charselectchoose charselectdelete
    herostats herosksp heroskspdelete incabil pgethead headlist
    equiplist equipdo buyitem sellitem selllist ilistbuy
    chalissue chalreceive flee fightresult battleping battlereport
    arenachflist arenachslist arenachtlist arenachran getranklist
    clancreate clanedit clanjoin clanleave clankick clanlist
    claninvite clanreject clanhierarchy clanstats myclan
    friendadd friendlist friendremoved invite
    inbox readmail sendmail deletemail mailflist pmessages
    banlist banlistadd banlistremove
    boarddl customget customupload panimscripts wiseman microedition

That is the whole server, described. `herostats`, `equiplist`, `ilistbuy` and
`incabil` are the interesting ones: they are where item and ability numbers
would have crossed the wire, which makes this the one place that could confirm
or contradict the numbers we adopted from the remake.

## What this does not give us

Two engines means two servers. Nothing in `server/` applies here — it decodes
a binary protocol these jars never speak. Reviving the Arena is a separate
piece of work, not an afternoon's adaptation.


## What is in jars/, and what is still out there

Recovered and saved:

    EoE-Dagonar-v5.3.3          the Arena, MIDP-1.0, com.watAgame.eoe_town
    EoE-Orumant-v5.2.10         the same engine, the other town
    EoE-Blackjack-v1.0.0        "Badaz Blackjack", spin-off
    EoE-BadazPoker-v1.0.2       spin-off, from sefan.ru (rebranded in its
                                manifest by the site, game unchanged)
    EoE-ShiradsForge-v1.0.0-midp1   an earlier MIDP-1.0 build of the chapter
    EoE-SterlingLake-v1.1.1-midp1   likewise
    EoE-ShiradsForge-v1.0.0-176x208 the small-screen build, 155 KB against the
                                    64 KB of the other 1.0.0 — a different
                                    binary, not a rename (dertz.in, which
                                    files it under the typo "Edidolon")
    EoE-BadazPoker-v1.0.2-176x208   likewise a distinct build

Known to exist and NOT recovered:

    Mistral Grove v1.1.7        a chapter we did not know about, with MOT
                                128x128 and 176x220 ports
    Dagonar v5.4.3              a later Arena build than the one we have
    Shirad's Forge 176x208      and EoE_Orumant_176x208
    Sterling Lake s40v2/v3a     "online" variants

Every live site that once served these has since dropped them; the copies
survive only inside the Internet Archive item `J2MEArchive`, in `Sites5.7z`
(3.1 GB, the mox.su crawl) and `Find.7z` (26.7 GB, clean versioned releases).
bsdtar extracts nothing from those archives, and the reason turned out to be
more interesting than a missing codec: **the whole hoard is deduplicated with
symlinks**. Every repeated file is stored as a symlink to an absolute path on
the archivist's own machine, `/home/octt/Desktop/Javante/...`. bsdtar wrote the
dangling links and they read as nothing. 7-Zip proper (`brew install
sevenzip`, then `7zz`) shows them for what they are.

The consequence is that the *bodies* nearly all live in `Find.7z`: the copies
in the smaller per-site archives are links pointing into it. Both Dagonar
entries in FSN2.7z, for instance, are links to
`Find/packs-1/TOC Mobile/7210/...` and `Find/sites-x19/arhiva.50webs.com/...`.
So a small download may well yield nothing but links.

The live web is exhausted for Mistral Grove: my-moto.ru, iceload.ru, xwap.me
and andrew-lviv.net all 404 now, mascha2.jw.lt serves a page with no file
behind it, mox.su answers everything with the same error page, seclub.org
redirects away, and dertz.in has never had it.
