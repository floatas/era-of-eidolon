#!/usr/bin/env python3
"""Town server for Orumant and Dagonar.

The town client POSTs broken-bar (U+00A6) fields to named scripts under /1/.
A body has to start with that character or the phone retries and then shows
"rsp". After stripping one leading bar, five fields are mandatory wherever
the phone calls b(): status, session, then three integers. Login with an
unknown key is the exception: the body after that strip must be exactly "0",
which opens the welcome screen and does not call b().

Nothing here is a recovered watAgame table. Any nickname and any password
are accepted, and an unknown name is registered, so a visitor can walk in.
Accounts, heroes, mail, and friend names are only what this process was
told by the phone. Shelves,
rankings, help articles, portraits, clans, and fight boards were not in the
jars, so those screens open empty or say so. boarddl.pl is answered with a
header and no board; the phone cannot draw a fight from that, which is the
point.
"""

import json
import os
import secrets
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
SAVE = os.path.join(HERE, "saves", "arena.json")
LOGS = os.path.join(HERE, "logs")

BAR = "\u00a6"
SHELF = "Nothing on this shelf was preserved."
CLANS = "Clans were not preserved."
# Column 3 of a shop row is parsed as a watgreet record id. Record 1 is the
# version the phone compares; record 2 is the sentence above, written by the
# first pmessages reply. Fire on a shelf shows that sentence.
SHELF_ROW = ("", "", "Nothing preserved", "2")
NOTICE = ("", "", "Nothing preserved", "0")


def frame(status, sid, *payload):
    parts = [str(status), str(sid), "0", "0", "0"]
    parts.extend("" if p is None else str(p) for p in payload)
    return BAR + BAR.join(parts)


def y_list(sid, rows, title="", subtitle=""):
    flat = []
    for row in rows:
        flat.extend(row)
    return frame("1", sid, str(len(rows)), title, subtitle, *flat)


def parse_fields(raw):
    if isinstance(raw, bytes):
        text = raw.decode("utf-8", "replace")
    else:
        text = raw or ""
    out = {}
    for part in text.split(BAR):
        if "=" in part:
            key, val = part.split("=", 1)
            out[key] = val
    return out


def clean(text):
    return (text or "").replace(BAR, " ").replace("\r", " ").replace("\n", " ")


class Store:
    def __init__(self, path):
        self.path = path
        self.lock = threading.Lock()
        self.data = {
            "accounts": {},
            "heroes": {},
            "mail": [],
            "sessions": {},
            "next_mail": 1,
        }
        self._load()

    def _load(self):
        if not self.path:
            return
        try:
            with open(self.path) as fh:
                saved = json.load(fh)
        except (OSError, json.JSONDecodeError):
            return
        if isinstance(saved, dict):
            self.data.update(saved)

    def _save(self):
        if not self.path:
            return
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(self.data, fh, indent=1)
        os.replace(tmp, self.path)

    def session(self, fields):
        sid = fields.get("id") or ""
        sessions = self.data["sessions"]
        if sid and sid in sessions:
            return sid, sessions[sid]
        sid = secrets.token_hex(8)
        rec = {"account": None, "hero": None}
        sessions[sid] = rec
        self._save()
        return sid, rec

    def account(self, rec):
        key = rec.get("account")
        if not key:
            return None
        return self.data["accounts"].get(key)

    def by_nick(self, nickname):
        return self.data["accounts"].get((nickname or "").lower())

    def by_key(self, key):
        if not key:
            return None
        for acc in self.data["accounts"].values():
            if acc.get("key") == key:
                return acc
        return None

    def hero(self, name):
        if not name:
            return None
        return self.data["heroes"].get(name.lower())

    def slots(self, acc):
        if not acc:
            return "", ""
        slots = list(acc.get("slots") or ["", ""])
        while len(slots) < 2:
            slots.append("")
        return slots[0], slots[1]

    def bind(self, rec, acc):
        rec["account"] = acc["nickname"].lower()
        slots = [s for s in (acc.get("slots") or []) if s]
        if rec.get("hero") not in slots:
            rec["hero"] = slots[0] if slots else None

    def register(self, rec, nickname, password):
        nick = clean(nickname).strip()
        if not nick:
            return None, "Enter a nickname."
        # A name that already exists is the same door as login. The password
        # is not checked: this server has no account list to validate against.
        existing = self.by_nick(nick)
        if existing:
            self.bind(rec, existing)
            self._save()
            return existing, ""
        acc = {
            "nickname": nick,
            "password": password or "",
            "key": secrets.token_hex(8),
            "slots": ["", ""],
        }
        self.data["accounts"][nick.lower()] = acc
        self.bind(rec, acc)
        self._save()
        return acc, ""

    def login_password(self, rec, nickname, password):
        nick = clean(nickname).strip()
        if not nick:
            return None
        acc = self.by_nick(nick)
        if not acc:
            acc = {
                "nickname": nick,
                "password": password or "",
                "key": secrets.token_hex(8),
                "slots": ["", ""],
            }
            self.data["accounts"][nick.lower()] = acc
        self.bind(rec, acc)
        self._save()
        return acc

    def create_hero(self, rec, name, gender):
        acc = self.account(rec)
        if not acc:
            return False, ""
        name = clean(name).strip()
        if not name:
            return False, ""
        if self.hero(name) and self.hero(name).get("account") != acc["nickname"].lower():
            return False, _suggest(name, self.data["heroes"])
        slots = list(acc.get("slots") or ["", ""])
        while len(slots) < 2:
            slots.append("")
        low = [s.lower() for s in slots]
        if name.lower() in low:
            return False, _suggest(name, self.data["heroes"])
        try:
            slot = slots.index("")
        except ValueError:
            return False, _suggest(name, self.data["heroes"])
        slots[slot] = name
        acc["slots"] = slots[:2]
        self.data["heroes"][name.lower()] = {
            "name": name,
            "gender": clean(gender),
            "account": acc["nickname"].lower(),
            "custom": [""] * 7,
            "friends": [],
            "bans": [],
        }
        rec["hero"] = name
        self._save()
        return True, ""

    def choose_hero(self, rec, name):
        acc = self.account(rec)
        if not acc:
            return False
        slots = [s for s in (acc.get("slots") or []) if s]
        for slot in slots:
            if slot.lower() == (name or "").lower():
                rec["hero"] = slot
                self._save()
                return True
        return False

    def delete_hero(self, rec, name):
        acc = self.account(rec)
        if not acc or not name:
            return False
        slots = list(acc.get("slots") or ["", ""])
        hit = False
        for i, slot in enumerate(slots):
            if slot.lower() == name.lower():
                slots[i] = ""
                hit = True
        if not hit:
            return False
        acc["slots"] = slots
        self.data["heroes"].pop(name.lower(), None)
        if (rec.get("hero") or "").lower() == name.lower():
            rec["hero"] = next((s for s in slots if s), None)
        self._save()
        return True

    def active(self, rec):
        return self.hero(rec.get("hero"))


def _suggest(name, heroes):
    stem = clean(name).strip() or "Hero"
    n = 2
    while f"{stem}{n}".lower() in heroes:
        n += 1
    return f"{stem}{n}"


def _gender_word(token):
    if token == "m":
        return "Male"
    if token == "f":
        return "Female"
    return token or ""


def handle(script, body, store):
    """Return the response body for one town script. `script` is the filename."""
    script = (script or "").rsplit("/", 1)[-1]
    fields = parse_fields(body)
    with store.lock:
        return _dispatch(script, fields, store)


def _dispatch(script, fields, store):
    sid, rec = store.session(fields)
    acc = store.account(rec)
    hero = store.active(rec)

    if script == "version.pl":
        # Greet record 1 and script record 1 are compared to these. An empty
        # news field skips the popup. Do not send status 2: that is the paywall.
        return frame("1", sid, "1", "1")

    if script == "login.pl" and "login" not in fields:
        found = store.by_key(fields.get("key", ""))
        if not found:
            return BAR + "0"
        store.bind(rec, found)
        a, b = store.slots(found)
        return frame("1", sid, a, b, found["nickname"])

    if script == "login.pl":
        found = store.login_password(rec, fields.get("login", ""), fields.get("pass", ""))
        if not found:
            return frame("0", sid, "Enter a nickname.")
        a, b = store.slots(found)
        return frame("1", sid, a, b, found["key"])

    if script == "register.pl":
        found, err = store.register(rec, fields.get("nickname", ""), fields.get("reqpass", ""))
        if not found:
            return frame("0", sid, err)
        a, b = store.slots(found)
        return frame("1", sid, a, b, found["key"])

    if script == "pay.pl":
        # The phone only reaches this from a prompt we never send. Acknowledge
        # with the heroes it already has so the slot list is not wiped.
        a, b = store.slots(acc)
        nick = acc["nickname"] if acc else ""
        return frame("1", sid, a, b, nick)

    if script == "charselectcreate.pl":
        ok, suggestion = store.create_hero(rec, fields.get("charname", ""), fields.get("gender", ""))
        if not ok:
            return frame("0", sid, suggestion)
        return frame("1", sid)

    if script == "charselectchoose.pl":
        if store.choose_hero(rec, fields.get("charname", "")):
            return frame("1", sid)
        return frame("0", sid)

    if script == "charselectdelete.pl":
        if store.delete_hero(rec, fields.get("charname", "")):
            return frame("1", sid)
        return frame("0", sid)

    if script == "pmessages.pl":
        # idx 1 is stored first, so its first field becomes watgreet record 1
        # and must stay "1". The second field becomes record 2, which shelf
        # rows point at. Later indexes only append; they add nothing.
        if fields.get("idx", "1") == "1":
            return frame("1", sid, "1", SHELF)
        return frame("1", sid)

    if script == "panimscripts.pl":
        # Record 1 must match the script version. A real fight script was
        # never captured, so this record is only the version token.
        return frame("1", sid, "1")

    if script == "herostats.pl":
        rows = []
        if hero:
            rows.append(("", "", "Name: " + hero["name"], ""))
            word = _gender_word(hero.get("gender", ""))
            if word:
                rows.append(("", "", "Gender: " + word, ""))
        rows.append(("", "", "Stats, gold, and gear were not preserved.", ""))
        return y_list(sid, rows)

    if script == "customget.pl":
        custom = (hero or {}).get("custom") or [""] * 7
        custom = (list(custom) + [""] * 7)[:7]
        return frame("1", sid, *custom)

    if script == "customupload.pl":
        if hero is not None:
            hero["custom"] = [
                clean(fields.get("greeting", "")),
                clean(fields.get("victory", "")),
                clean(fields.get("loose", "")),
                (hero.get("custom") or [""] * 7)[3],
                clean(fields.get("taunt1", "")),
                clean(fields.get("taunt2", "")),
                clean(fields.get("taunt3", "")),
            ]
            store._save()
        return frame("1", sid)

    if script == "headlist.pl":
        return y_list(sid, [("", "", "No portraits kept", "")])

    if script == "pgethead.pl":
        # Status 1 makes the phone parse image bytes it does not have.
        return frame("0", sid)

    if script in ("ilistbuy.pl", "selllist.pl"):
        return y_list(sid, [SHELF_ROW])

    if script == "sellitem.pl":
        return y_list(sid, [SHELF_ROW])

    if script == "buyitem.pl":
        return frame("0", sid, "That item is not in the preserved shop.")

    if script == "equiplist.pl":
        # Screen 123 fires even when the list is empty, so one row has to be
        # there. equipdo does not grant it.
        return y_list(sid, [(" ", "", "Nothing kept", "")])

    if script == "equipdo.pl":
        return frame("1", sid)

    if script in ("heroskspdelete.pl", "incabil.pl"):
        return frame("1", sid)

    if script == "herosksp.pl":
        # Opcode 40 forces classID 1 and then indexes the row. Other class
        # ids open a screen that already checks for an empty list.
        if fields.get("classID", "") == "1":
            return y_list(sid, [(
                "", "", "Nothing preserved",
                "No skills or spells were preserved.",
            )])
        return y_list(sid, [])

    if script in ("arenachflist.pl", "arenachtlist.pl", "arenachslist.pl"):
        return y_list(sid, [("", "", "No opponents preserved", "0")])

    if script == "arenachran.pl":
        # No count prefix: the phone takes the leftover fields four at a time.
        # Zero rows makes the next keypress divide by zero.
        return frame("1", sid, "", "", "No ranking preserved", "0")

    if script in ("getranklist.pl", "battlereport.pl", "clanstats.pl",
                  "clanhierarchy.pl", "clanlist.pl"):
        return y_list(sid, [])

    if script == "wiseman.pl":
        return y_list(sid, [(
            "", "Help text for this category was not kept.",
            "Not preserved", "",
        )])

    if script == "inbox.pl":
        mine = _inbox(store, hero)
        if not mine:
            return frame("0", sid)
        flat = []
        for mail in mine:
            flat.extend((mail["sender"], "1" if mail.get("read") else "0", str(mail["id"])))
        return frame("1", sid, str(len(mine)), *flat)

    if script == "readmail.pl":
        mail = _mail_by_id(store, fields.get("mailid", ""))
        if not mail:
            return frame("0", sid)
        mail["read"] = True
        store._save()
        return frame("1", sid, "Mail", mail["body"])

    if script == "deletemail.pl":
        mid = fields.get("mailid", "")
        store.data["mail"] = [m for m in store.data["mail"] if str(m["id"]) != mid]
        store._save()
        return frame("1", sid)

    if script == "sendmail.pl":
        _send_mail(store, hero, acc, fields.get("receivername", ""), fields.get("mailbody", ""))
        return frame("1", sid)

    if script == "mailflist.pl":
        names = _other_heroes(store, hero)
        return frame("1", sid, str(len(names)), *names)

    if script in ("friendadd.pl",):
        _add_name(hero, "friends", fields.get("name", ""))
        store._save()
        return frame("1", sid)

    if script == "friendlist.pl":
        names = (hero or {}).get("friends") or []
        if not names:
            return y_list(sid, [("", "", "No friends added", "0")])
        return y_list(sid, [("", "", n, "") for n in names])

    if script == "friendremoved.pl":
        _drop_name(hero, "friends", fields.get("name", ""))
        store._save()
        return frame("1", sid)

    if script == "banlistadd.pl":
        _add_name(hero, "bans", fields.get("name", ""))
        store._save()
        return frame("1", sid)

    if script == "banlist.pl":
        names = (hero or {}).get("bans") or []
        if not names:
            return y_list(sid, [("", "", "No names blocked", "0")])
        return y_list(sid, [("", "", n, "") for n in names])

    if script == "banlistremove.pl":
        _drop_name(hero, "bans", fields.get("name", ""))
        store._save()
        return frame("1", sid)

    if script == "invite.pl":
        return frame("1", sid, "Invitations are not delivered.")

    if script == "betaentry.pl":
        a, b = store.slots(acc)
        return frame("1", sid, a, b)

    if script == "clancreate.pl":
        return frame("1", sid, CLANS)

    if script == "claninvite.pl":
        # The phone parses this field as a greeting id. 0 is an empty popup.
        return frame("1", sid, "0")

    if script in ("myclan.pl", "clanjoin.pl"):
        # Flag 1 shows the message and steps back. Flags 3 and 4 would open
        # a clan screen we have no roster for.
        return frame("1", sid, "1", "", "", CLANS)

    if script in ("clankick.pl", "clanreject.pl"):
        return frame("1", sid)

    if script == "clanleave.pl":
        return frame("0", sid)

    if script == "clanedit.pl":
        return frame("0", sid)

    if script == "chalissue.pl":
        # 0..4 index a missing greeting. Anything else is a bad parse.
        return frame("0", sid)

    if script == "chalreceive.pl":
        # Any status other than 0 starts a board download.
        return frame("0", sid)

    if script == "boarddl.pl":
        return frame("1", sid)

    if script == "submit.pl":
        return frame("0", sid)

    if script == "flee.pl":
        return frame("1", sid)

    if script == "fightresult.pl":
        return frame("0", sid)

    if script in ("ping.pl", "battleping.pl", "errorreport.pl"):
        return frame("1", sid)

    return frame("1", sid)


def _inbox(store, hero):
    if not hero:
        return []
    who = hero["name"].lower()
    return [m for m in store.data["mail"] if m.get("to", "").lower() == who]


def _mail_by_id(store, mid):
    for mail in store.data["mail"]:
        if str(mail["id"]) == str(mid):
            return mail
    return None


def _send_mail(store, hero, acc, receiver, body):
    to = clean(receiver).strip()
    text = clean(body)
    if not to or not text:
        return
    sender = hero["name"] if hero else (acc["nickname"] if acc else "")
    if not sender:
        return
    mid = store.data.get("next_mail", 1)
    store.data["next_mail"] = mid + 1
    store.data["mail"].append({
        "id": mid,
        "sender": sender,
        "to": to,
        "body": text,
        "read": False,
    })
    store._save()


def _other_heroes(store, hero):
    me = (hero or {}).get("name", "").lower()
    names = []
    for rec in store.data["heroes"].values():
        if rec["name"].lower() != me:
            names.append(rec["name"])
    return names


def _add_name(hero, key, name):
    name = clean(name).strip()
    if not hero or not name:
        return
    have = hero.setdefault(key, [])
    if name.lower() not in (n.lower() for n in have):
        have.append(name)


def _drop_name(hero, key, name):
    if not hero or not name:
        return
    hero[key] = [n for n in hero.get(key, []) if n.lower() != name.lower()]


class Handler(BaseHTTPRequestHandler):
    store = None

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        script = self.path.split("?", 1)[0]
        relay = self.headers.get("X-relay-url")
        if relay:
            script = relay
        try:
            reply = handle(script, body, self.store)
        except Exception as exc:
            print(f"arena {script} failed: {exc}", flush=True)
            reply = BAR + "1" + BAR + "0" + BAR + "0" + BAR + "0" + BAR + "0"
        data = reply.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        name = script.rsplit("/", 1)[-1] or "/"
        status = reply.split(BAR)[1] if reply.startswith(BAR) and BAR in reply[1:] else reply[1:8]
        print(f"{name} -> {status} ({len(data)} bytes)", flush=True)

    def log_message(self, fmt, *args):
        return


def main(argv):
    port = int(argv[1]) if len(argv) > 1 else 8081
    os.makedirs(LOGS, exist_ok=True)
    Handler.store = Store(SAVE)
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"arena on http://127.0.0.1:{port}/1/  save {SAVE}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main(sys.argv)
