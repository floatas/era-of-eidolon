# Descriptors without their jars

Twenty `.jad` files crawled from mox.su in 2010, recovered from the Internet
Archive item `J2MEArchive` (`Sites5.7z`). mox.su was a WAP download site, and
the crawl caught its descriptors but not the jars they point at. The site is
still up; every one of those URLs now returns the same 1,414-byte error page.

They are worth keeping anyway. A `.jad` is watAgame's own manifest, so each one
is primary evidence of a build we do not have — its exact version, profile and
jar size:

    Mistral Grove            1.1.7   MIDP-2.0   162389 bytes   (MOT 176x220)
    Mistral Grove            1.1.7   MIDP-2.0                  (MOT 128x128)
    Mistral Grove ROADKILL   1.1.7   MIDP-1.0   159726 bytes   (S60)

That matters for Mistral Grove in particular: MIDP-2.0, main class `Main`,
~160 KB — the same engine as Shirad's Forge and Sterling Lake, not the
MIDP-1.0 town engine of Dagonar and Orumant. If the jar turns up, the server
in `server/` has a fair chance of running it unchanged.

`../j2mearchive-eoe.txt` is the Era of Eidolon slice of that item's 184 MB
recursive listing: every path, under the archive that holds it, so the search
can be repeated without downloading the listing again.
