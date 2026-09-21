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
