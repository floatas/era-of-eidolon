#!/usr/bin/env python3
"""What the town client will accept, checked without the emulator.

The parser below is b.java b() plus the login special case in a(int, String):
a leading broken bar, then either the exact text "0" or five header fields
whose last three parse as integers. Each check names the screen that breaks
when the field is wrong.
"""

import os
import sys
import tempfile
import threading
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import arena

FAILED = []
BAR = arena.BAR


def check(name, cond, detail=""):
    if cond:
        print(f"  \033[32mok\033[0m   {name}")
    else:
        print(f"  \033[31mFAIL\033[0m {name}" + (f"  — {detail}" if detail else ""))
        FAILED.append(name)


def client_take(body):
    """The phone's read of one response. Raises the same way a short body would."""
    if not body.startswith(BAR):
        raise AssertionError("phone shows rsp: body does not start with ¦")
    rest = body[1:]
    if rest == "0":
        return {"welcome": True, "rest": []}
    parts = rest.split(BAR)
    if len(parts) < 5:
        raise AssertionError(f"b() needs 5 fields, got {parts}")
    status, sid = parts[0], parts[1]
    int(parts[2])
    int(parts[3])
    int(parts[4])
    return {"welcome": False, "status": status, "sid": sid, "rest": parts[5:]}


def post(store, script, body, sid=None):
    raw = body
    if sid:
        raw = f"{BAR}id={sid}{body}"
    reply = arena.handle(script, raw.encode("utf-8"), store)
    return client_take(reply), reply


def y_rows(taken):
    count = int(taken["rest"][0])
    title, subtitle = taken["rest"][1], taken["rest"][2]
    flat = taken["rest"][3:]
    if len(flat) != count * 4:
        raise AssertionError(f"y() wants {count * 4} cells, got {len(flat)}")
    rows = [flat[i:i + 4] for i in range(0, len(flat), 4)]
    return title, subtitle, rows


def main():
    path = os.path.join(tempfile.mkdtemp(), "arena.json")
    store = arena.Store(path)

    print("boot")
    ver, _ = post(store, "version.pl", f"{BAR}client=02010502{BAR}build=5.3.3")
    check("version status 1, greet 1, script 1, no news popup",
          ver["status"] == "1" and ver["rest"][:2] == ["1", "1"] and len(ver["rest"]) == 2,
          str(ver))
    sid = ver["sid"]

    welcome, raw = post(store, "login.pl", f"{BAR}key=", sid)
    check("unknown key is exactly ¦0, which opens the welcome screen",
          welcome.get("welcome") and raw == BAR + "0", repr(raw))

    reg, _ = post(store, "register.pl",
                  f"{BAR}nickname=Ada{BAR}reqpass=secret", sid)
    check("register gives j(3) two hero slots and a key",
          reg["status"] == "1" and reg["rest"][:2] == ["", ""] and len(reg["rest"][2]) >= 8,
          str(reg["rest"]))
    key = reg["rest"][2]

    taken, again = post(store, "register.pl",
                        f"{BAR}nickname=Ada{BAR}reqpass=other", sid)
    check("a taken nickname logs into the existing account",
          taken["status"] == "1" and taken["rest"][:3] == ["", "", key],
          str(taken["rest"]))

    for idx, expect in (("1", ["1", arena.SHELF]), ("2", []), ("3", [])):
        got, _ = post(store, "pmessages.pl", f"{BAR}idx={idx}", sid)
        check(f"pmessages idx {idx} stores {expect or 'nothing'}",
              got["status"] == "1" and got["rest"] == expect, str(got["rest"]))
    scripts, _ = post(store, "panimscripts.pl", f"{BAR}model=02", sid)
    check("panimscripts record 1 is the version token only",
          scripts["rest"] == ["1"], str(scripts["rest"]))

    created, _ = post(store, "charselectcreate.pl",
                      f"{BAR}charname=Ada{BAR}gender=m", sid)
    check("create accepts the name the phone already typed",
          created["status"] == "1" and created["rest"] == [], str(created))
    dup, _ = post(store, "charselectcreate.pl",
                  f"{BAR}charname=Ada{BAR}gender=f", sid)
    check("a duplicate hero name is rejected and a different one is suggested",
          dup["status"] == "0" and dup["rest"] and dup["rest"][0] != "Ada",
          str(dup["rest"]))

    print("town menus")
    stats, _ = post(store, "herostats.pl", "", sid)
    _, _, rows = y_rows(stats)
    labels = [r[2] for r in rows]
    check("hero sheet shows the typed name and gender",
          any(x == "Name: Ada" for x in labels) and any(x == "Gender: Male" for x in labels),
          str(labels))
    check("hero sheet does not invent stats or gold",
          any("not preserved" in x for x in labels)
          and not any(ch.isdigit() for x in labels for ch in x),
          str(labels))

    inbox, _ = post(store, "inbox.pl", "", sid)
    check("empty inbox is status 0, the phone's own No mail screen",
          inbox["status"] == "0", str(inbox))

    shop, _ = post(store, "ilistbuy.pl", f"{BAR}classID=9", sid)
    _, _, rows = y_rows(shop)
    check("every shelf is one preserved-nothing row pointing at greet record 2",
          len(rows) == 1 and rows[0][2] == "Nothing preserved" and rows[0][3] == "2",
          str(rows))
    sell, _ = post(store, "selllist.pl", "", sid)
    _, _, rows = y_rows(sell)
    check("sell list is the same empty shelf", len(rows) == 1 and rows[0][3] == "2")

    buy, _ = post(store, "buyitem.pl", f"{BAR}genericID=1", sid)
    check("buy refuses and does not claim a purchase",
          buy["status"] == "0" and "not in the preserved shop" in buy["rest"][0],
          str(buy["rest"]))

    equip, _ = post(store, "equiplist.pl", f"{BAR}equipid=0", sid)
    _, _, rows = y_rows(equip)
    check("equipment list has one row so fire does not index off the end",
          len(rows) == 1 and rows[0][2] == "Nothing kept", str(rows))

    skills, _ = post(store, "herosksp.pl", f"{BAR}classID=1", sid)
    _, _, rows = y_rows(skills)
    check("the skill screen that indexes its row says nothing was preserved",
          len(rows) == 1 and rows[0][3] == "No skills or spells were preserved.",
          str(rows))
    other, _ = post(store, "herosksp.pl", f"{BAR}classID=9", sid)
    _, _, rows = y_rows(other)
    check("a skill class the phone already bounds may be an empty list", rows == [])

    foes, _ = post(store, "arenachflist.pl", "", sid)
    _, _, rows = y_rows(foes)
    check("arena list has one row whose flag does not start a challenge",
          len(rows) == 1 and rows[0][3] == "0" and "opponents" in rows[0][2],
          str(rows))
    rank, _ = post(store, "arenachran.pl", "", sid)
    check("ranking has a multiple of 4 fields and at least one row",
          rank["status"] == "1" and len(rank["rest"]) >= 4 and len(rank["rest"]) % 4 == 0
          and rank["rest"][2] == "No ranking preserved" and rank["rest"][3] == "0",
          str(rank["rest"]))

    wise, _ = post(store, "wiseman.pl", f"{BAR}category=0", sid)
    _, _, rows = y_rows(wise)
    check("help fire shows a kept-nothing sentence from the row itself",
          len(rows) == 1 and "not kept" in rows[0][1], str(rows))

    clans, _ = post(store, "myclan.pl", "", sid)
    check("clan opens onto a message and not a roster",
          clans["status"] == "1" and clans["rest"][:3] == ["1", "", ""]
          and clans["rest"][3] == arena.CLANS,
          str(clans["rest"]))
    made, _ = post(store, "clancreate.pl", f"{BAR}clanname=Wolves{BAR}clanshortname=WLV", sid)
    check("creating a clan is refused in the message, and no clan is stored",
          made["status"] == "1" and made["rest"] == [arena.CLANS]
          and "Wolves" not in open(path).read(),
          str(made["rest"]))

    board, _ = post(store, "boarddl.pl", "", sid)
    check("a fight board is not invented", board["status"] == "1" and board["rest"] == [])
    chal, _ = post(store, "chalissue.pl", f"{BAR}name=Someone", sid)
    check("a challenge does not pick a fight script", chal["status"] == "0")
    recv, _ = post(store, "chalreceive.pl", f"{BAR}name=Someone{BAR}accept=y", sid)
    check("accepting a challenge does not download a board", recv["status"] == "0")

    custom, _ = post(store, "customget.pl", "", sid)
    check("customget is exactly 7 strings",
          custom["status"] == "1" and len(custom["rest"]) == 7, str(custom["rest"]))
    up, _ = post(store, "customupload.pl",
                 f"{BAR}taunt1=Hello{BAR}taunt2={BAR}taunt3={BAR}greeting={BAR}victory={BAR}loose=",
                 sid)
    check("a typed taunt is acknowledged", up["status"] == "1")
    custom, _ = post(store, "customget.pl", "", sid)
    check("the typed taunt comes back, and no portrait is invented",
          custom["rest"][4] == "Hello" and custom["rest"][3] == "", str(custom["rest"]))
    head, _ = post(store, "pgethead.pl", f"{BAR}headflag=3", sid)
    check("portrait download is skipped", head["status"] == "0")

    print("mail and friends, only what was typed")
    added, _ = post(store, "friendadd.pl", f"{BAR}name=Brynn", sid)
    flist, _ = post(store, "friendlist.pl", "", sid)
    _, _, rows = y_rows(flist)
    check("a typed friend is listed",
          added["status"] == "1" and [r[2] for r in rows] == ["Brynn"], str(rows))
    gone, _ = post(store, "friendremoved.pl", f"{BAR}name=No friends added", sid)
    flist, _ = post(store, "friendlist.pl", "", sid)
    _, _, rows = y_rows(flist)
    check("removing a name that was never added leaves the real one",
          gone["status"] == "1" and [r[2] for r in rows] == ["Brynn"])

    # A second hero, on a second account, so mail has a real recipient.
    sid2 = client_take(arena.handle(
        "version.pl", f"{BAR}client=1".encode(), store))["sid"]
    bob, _ = post(store, "register.pl", f"{BAR}nickname=Bob{BAR}reqpass=secret", sid2)
    post(store, "charselectcreate.pl", f"{BAR}charname=Bob{BAR}gender=f", sid2)
    post(store, "sendmail.pl", f"{BAR}receivername=Bob{BAR}mailbody=Hello Bob", sid)
    bob_in, _ = post(store, "inbox.pl", "", sid2)
    check("mail the phone sent is listed to the hero it named",
          bob_in["status"] == "1" and bob_in["rest"][0] == "1"
          and bob_in["rest"][1:4] == ["Ada", "0", "1"],
          str(bob_in["rest"]))
    read, _ = post(store, "readmail.pl", f"{BAR}mailid=1", sid2)
    check("reading mail returns a title and the typed body",
          read["status"] == "1" and read["rest"][1] == "Hello Bob", str(read["rest"]))
    ada_in, _ = post(store, "inbox.pl", "", sid)
    check("the sender's own inbox stays the empty screen", ada_in["status"] == "0")

    print("the key still finds the hero after the phone forgot watkey")
    fresh = client_take(arena.handle("version.pl", b"", store))["sid"]
    back, _ = post(store, "login.pl", f"{BAR}login=Ada{BAR}pass=secret", fresh)
    check("password login returns the same key and the hero in slot 0",
          back["status"] == "1" and back["rest"][:3] == ["Ada", "", key],
          str(back["rest"]))
    wrong, _ = post(store, "login.pl", f"{BAR}login=Ada{BAR}pass=not-the-password", fresh)
    check("a different password is still let in",
          wrong["status"] == "1" and wrong["rest"][:3] == ["Ada", "", key],
          str(wrong["rest"]))
    fresh_nick = client_take(arena.handle("version.pl", b"", store))["sid"]
    minted, _ = post(store, "login.pl", f"{BAR}login=Nia{BAR}pass=anything", fresh_nick)
    check("an unknown nickname is registered and let in",
          minted["status"] == "1" and minted["rest"][:2] == ["", ""] and len(minted["rest"][2]) >= 8,
          str(minted["rest"]))
    nia_key = minted["rest"][2]
    minted_again, _ = post(store, "login.pl", f"{BAR}login=Nia{BAR}pass=other", fresh_nick)
    check("the same nickname comes back with the key it was given",
          minted_again["status"] == "1" and minted_again["rest"][2] == nia_key,
          str(minted_again["rest"]))
    bykey, _ = post(store, "login.pl", f"{BAR}key={key}", fresh)
    check("a known key returns j(2): both slots and the nickname",
          bykey["status"] == "1" and bykey["rest"] == ["Ada", "", "Ada"],
          str(bykey["rest"]))

    ping, _ = post(store, "ping.pl", f"{BAR}onlinestatus=4", sid)
    check("ping is five header fields and does not drop the session",
          ping["status"] == "1" and ping["sid"] == sid and ping["rest"] == [])

    print("http")
    httpd = arena.ThreadingHTTPServer(("127.0.0.1", 0), arena.Handler)
    arena.Handler.store = store
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/1/version.pl",
        data=f"{BAR}client=1".encode("utf-8"),
        method="POST")
    with urllib.request.urlopen(req, timeout=5) as resp:
        raw = resp.read().decode("utf-8")
        code = resp.status
    httpd.shutdown()
    got = client_take(raw)
    check("POST /1/version.pl answers 200 and a bar body",
          code == 200 and got["status"] == "1" and got["rest"][:2] == ["1", "1"],
          raw[:40])

    # Bob was registered. Confirm the save file reloads.
    store2 = arena.Store(path)
    sid3 = client_take(arena.handle("version.pl", b"", store2))["sid"]
    back, _ = post(store2, "login.pl", f"{BAR}login=Bob{BAR}pass=secret", sid3)
    check("the save reloads Bob",
          back["status"] == "1" and back["rest"][0] == "Bob", str(back["rest"]))

    if FAILED:
        print(f"\n{len(FAILED)} FAILED")
        return 1
    print("\nall arena checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
