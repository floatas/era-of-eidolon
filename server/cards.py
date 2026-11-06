#!/usr/bin/env python3
"""Badaz Poker and Badaz Blackjack, online.

Both phones POST a tag/type/length body to /3/<opcode>.pl and refuse a
reply that does not open with 0xBABE. Hello (1) asks New user or Existing
user. Register (3) stores the nickname and password. Login (2) opens that
account only when the password matches. A wrong password stays on the
sign-in screen.

Heroes, gold, and the password live in SQLite. Gold is in the phone's chip
units: the screen shows n/10 gold and n%10 silver. A new hero starts with
1000, which is 100 gold. The goblin table is the hero against the offline
opponents. The public table waits until two people sit. Mail, rankings,
portraits, and the shop were not in the jars.

The dealer answers the tags the phone already parses. It is not a recovered
watAgame table dump.
"""

import os
import secrets
import sqlite3
import sys
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import dealer

HERE = os.path.dirname(os.path.abspath(__file__))
SAVE = os.path.join(HERE, "saves", "cards.sqlite")
LOGS = os.path.join(HERE, "logs")

MAGIC = 0xBABE
LIST_OPS = {27, 37, 38, 40, 50, 52, 54, 55, 56, 57, 58, 60}
NOTE = "That screen was not preserved."
HELLO = "Passwords are checked. New user creates the account."
START_GOLD = dealer.BUY_IN * 10


def field_int(tag, n):
    if -128 <= n <= 127:
        body = bytes([n & 0xFF])
    elif -32768 <= n <= 32767:
        body = int(n).to_bytes(2, "big", signed=True)
    else:
        body = int(n).to_bytes(4, "big", signed=True)
    return bytes([tag, 1]) + len(body).to_bytes(2, "big") + body


def field_str(tag, text):
    raw = (text or "").encode("utf-8")
    return bytes([tag, 2]) + len(raw).to_bytes(2, "big") + raw


def field_bytes(tag, blob):
    blob = bytes(blob)
    return bytes([tag, 0]) + len(blob).to_bytes(2, "big") + blob


def field_row(tag, name):
    """A text row. The phone shows the first string and sends it back on select.

    Type 4 is read by the row constructor, which does not use the length
    field as a byte count. The length is still the payload size so the next
    field starts where that constructor stops.
    """
    raw = (name or "").encode("utf-8")[:255]
    payload = bytes([len(raw)]) + raw + bytes([0, 0xFF, 0, 0, 0, 0])
    return bytes([tag, 4]) + len(payload).to_bytes(2, "big") + payload


def encode(kind, tag, value):
    if kind == "i":
        return field_int(tag, int(value))
    if kind == "s":
        return field_str(tag, value)
    if kind == "r":
        return field_row(tag, value)
    return field_bytes(tag, value)


def frame(status, fields):
    head = (
        MAGIC.to_bytes(2, "big")
        + bytes([status & 0xFF, 0])
        + (0).to_bytes(4, "big")
        + len(fields).to_bytes(2, "big")
    )
    return head + b"".join(fields)


def parse_request(body):
    """The fields the phone writes: tag, type, short length, then the value."""
    if isinstance(body, str):
        body = body.encode("latin1")
    fields = {}
    i = 0
    n = len(body)
    while i + 4 <= n:
        tag = body[i]
        typ = body[i + 1]
        ln = int.from_bytes(body[i + 2:i + 4], "big")
        i += 4
        if typ == 1:
            if ln == 1 and i + 1 <= n:
                val = int.from_bytes(body[i:i + 1], "big", signed=True)
                i += 1
            elif ln == 2 and i + 2 <= n:
                val = int.from_bytes(body[i:i + 2], "big", signed=True)
                i += 2
            elif ln == 4 and i + 4 <= n:
                val = int.from_bytes(body[i:i + 4], "big", signed=True)
                i += 4
            else:
                break
        elif typ in (2, 3):
            if i + ln > n:
                break
            val = body[i:i + ln].decode("utf-8", "replace")
            i += ln
        else:
            if i + ln > n:
                break
            val = bytes(body[i:i + ln])
            i += ln
        fields.setdefault(tag, []).append(val)
    return fields


def opcode_of(script):
    name = (script or "").split("?", 1)[0].rsplit("/", 1)[-1]
    if name.endswith(".pl"):
        name = name[:-3]
    try:
        return int(name)
    except ValueError:
        return -1


def _first(fields, tag, kind):
    for val in fields.get(tag) or []:
        if isinstance(val, kind):
            return val
    return None


def _money(n):
    n = int(n or 0)
    return "%d gold %d silver" % (n // 10, n % 10)


class Store:
    def __init__(self, path):
        self.path = path
        self.lock = __import__("threading").Lock()
        parent = os.path.dirname(path) if path and path != ":memory:" else ""
        if parent:
            os.makedirs(parent, exist_ok=True)
        self.db = sqlite3.connect(path or ":memory:", check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self._init()
        self.rooms = dealer.Rooms(self)

    def _init(self):
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                nick_key TEXT PRIMARY KEY,
                nickname TEXT NOT NULL,
                password TEXT NOT NULL,
                created INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS heroes (
                name_key TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                account TEXT NOT NULL,
                gender INTEGER NOT NULL DEFAULT 1,
                gold INTEGER NOT NULL,
                in_play INTEGER NOT NULL DEFAULT 0,
                committed INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                account TEXT,
                hero TEXT,
                game INTEGER NOT NULL DEFAULT 11
            );
            """
        )
        # A restart must not keep a pot. Chips that were on a table go home.
        self.db.execute(
            """
            UPDATE heroes
               SET gold = gold + in_play + committed,
                   in_play = 0,
                   committed = 0
             WHERE in_play != 0 OR committed != 0
            """
        )
        self.db.commit()

    def session(self, token):
        if not token:
            token = secrets.token_bytes(8)
        key = token.hex()
        row = self.db.execute("SELECT * FROM sessions WHERE token=?", (key,)).fetchone()
        if not row:
            self.db.execute(
                "INSERT INTO sessions (token, account, hero, game) VALUES (?,?,?,?)",
                (key, None, None, 11),
            )
            self.db.commit()
            rec = {"token": key, "account": None, "hero": None, "game": 11}
        else:
            rec = {
                "token": key,
                "account": row["account"],
                "hero": row["hero"],
                "game": row["game"] or 11,
            }
        return token, rec

    def note_game(self, rec, game):
        if game not in (10, 11):
            return
        rec["game"] = game
        self.db.execute("UPDATE sessions SET game=? WHERE token=?", (game, rec["token"]))
        self.db.commit()

    def account(self, rec):
        nick = rec.get("account")
        if not nick:
            return None
        row = self.db.execute("SELECT * FROM accounts WHERE nick_key=?", (nick,)).fetchone()
        if not row:
            return None
        heroes = [
            r["name"]
            for r in self.db.execute(
                "SELECT name FROM heroes WHERE account=? ORDER BY rowid", (nick,)
            )
        ]
        return {"nickname": row["nickname"], "password": row["password"], "heroes": heroes}

    def by_nick(self, nickname):
        return self.account({"account": (nickname or "").strip().lower()})

    def _bind(self, rec, key):
        rec["account"] = key
        owned = [
            r["name"]
            for r in self.db.execute(
                "SELECT name FROM heroes WHERE account=? ORDER BY rowid", (key,)
            )
        ]
        if rec.get("hero") not in owned:
            rec["hero"] = owned[0] if owned else None
        self.db.execute(
            "UPDATE sessions SET account=?, hero=? WHERE token=?",
            (key, rec.get("hero"), rec["token"]),
        )
        self.db.commit()
        return self.account(rec)

    def _named(self, nickname, password):
        nick = (nickname or "").strip()
        if not nick:
            return None, None, "Type a nickname."
        if not password:
            return None, None, "Type a password."
        return nick, nick.lower(), None

    def login(self, rec, nickname, password):
        """Existing user. The stored password has to match."""
        nick, key, err = self._named(nickname, password)
        if err:
            return None, err
        row = self.db.execute("SELECT * FROM accounts WHERE nick_key=?", (key,)).fetchone()
        if not row:
            return None, "No account by that name."
        if row["password"] != password:
            return None, "Wrong password."
        return self._bind(rec, key), None

    def register(self, rec, nickname, password):
        """New user. A taken name is refused and the stored password is left as it is."""
        nick, key, err = self._named(nickname, password)
        if err:
            return None, err
        row = self.db.execute("SELECT * FROM accounts WHERE nick_key=?", (key,)).fetchone()
        if row:
            return None, "That name is already registered."
        self.db.execute(
            "INSERT INTO accounts (nick_key, nickname, password, created) VALUES (?,?,?,?)",
            (key, nick, password, int(time.time())),
        )
        return self._bind(rec, key), None

    def create_hero(self, rec, name, gender):
        acc = self.account(rec)
        if not acc:
            return False, ""
        name = (name or "").strip()
        if not name:
            return False, _suggest("Hero", self._names())
        owner = self._hero(name)
        if owner and owner["account"] != rec.get("account"):
            return False, _suggest(name, self._names())
        heroes = list(acc.get("heroes") or [])
        if name.lower() in (h.lower() for h in heroes):
            return False, _suggest(name, self._names())
        if len(heroes) >= 2:
            rec["hero"] = heroes[0]
            self._bind_hero(rec)
            return True, ""
        gender = 2 if gender == 2 else 1
        self.db.execute(
            """
            INSERT INTO heroes (name_key, name, account, gender, gold)
            VALUES (?,?,?,?,?)
            """,
            (name.lower(), name, rec["account"], gender, START_GOLD),
        )
        rec["hero"] = name
        self._bind_hero(rec)
        return True, ""

    def choose(self, rec, name):
        acc = self.account(rec)
        if not acc:
            return
        picked = None
        for hero in acc.get("heroes") or []:
            if hero.lower() == (name or "").strip().lower():
                picked = hero
                break
        if picked is None and acc.get("heroes"):
            picked = acc["heroes"][0]
        rec["hero"] = picked
        self._bind_hero(rec)

    def delete_hero(self, rec, name):
        acc = self.account(rec)
        if not acc or not name:
            return
        key = name.strip().lower()
        row = self._hero(name)
        if row:
            self.rooms.drop(row["name"])
            self.db.execute("DELETE FROM heroes WHERE name_key=?", (row["name_key"],))
        heroes = [
            r["name"]
            for r in self.db.execute(
                "SELECT name FROM heroes WHERE account=? ORDER BY rowid", (rec.get("account"),)
            )
        ]
        if (rec.get("hero") or "").lower() == key:
            rec["hero"] = heroes[0] if heroes else None
        self._bind_hero(rec)

    def _names(self):
        return {r["name_key"] for r in self.db.execute("SELECT name_key FROM heroes")}

    def _hero(self, name):
        if not name:
            return None
        return self.db.execute(
            "SELECT * FROM heroes WHERE name_key=?", (name.strip().lower(),)
        ).fetchone()

    def _bind_hero(self, rec):
        self.db.execute(
            "UPDATE sessions SET hero=? WHERE token=?", (rec.get("hero"), rec["token"])
        )
        self.db.commit()

    def chips(self, name):
        row = self._hero(name)
        if not row:
            return {"gold": 0, "in_play": 0, "committed": 0}
        return {
            "gold": row["gold"],
            "in_play": row["in_play"],
            "committed": row["committed"],
        }

    def purse(self, rec):
        row = self._hero(rec.get("hero") or "")
        if not row:
            return "Create a hero first."
        line = "Gold: %s" % _money(row["gold"])
        if row["in_play"]:
            line += "\nAt the table: %s" % _money(row["in_play"])
        return line

    def buy(self, hero, amount):
        row = self._hero(hero)
        if not row:
            return 0
        take = min(int(amount), int(row["gold"]))
        if take <= 0:
            return 0
        self.db.execute(
            "UPDATE heroes SET gold=gold-?, in_play=in_play+? WHERE name_key=?",
            (take, take, row["name_key"]),
        )
        self.db.commit()
        return take

    def rebuy(self, hero, amount):
        return self.buy(hero, amount)

    def add_gold(self, hero, amount):
        amount = int(amount or 0)
        row = self._hero(hero)
        if not row or amount == 0:
            return
        self.db.execute(
            "UPDATE heroes SET gold=gold+? WHERE name_key=?", (amount, row["name_key"])
        )
        self.db.commit()

    def cash_stack(self, hero, stack):
        self.add_gold(hero, stack)

    def set_table(self, hero, stack, committed):
        self.write_chips(hero, stack, committed)

    def clear_committed(self, hero):
        row = self._hero(hero)
        if not row:
            return
        self.db.execute(
            "UPDATE heroes SET committed=0 WHERE name_key=?", (row["name_key"],)
        )
        self.db.commit()

    def write_chips(self, hero, in_play, committed):
        row = self._hero(hero)
        if not row:
            return
        self.db.execute(
            "UPDATE heroes SET in_play=?, committed=? WHERE name_key=?",
            (int(in_play), int(committed), row["name_key"]),
        )
        self.db.commit()


def _suggest(name, names):
    stem = (name or "").strip() or "Hero"
    n = 2
    while f"{stem}{n}".lower() in names:
        n += 1
    return f"{stem}{n}"


def _rows(acc):
    return [field_row(20, name) for name in (acc.get("heroes") or [])]


def _cookie(token):
    return [field_bytes(0, token)]


def handle(script, body, store):
    op = opcode_of(script)
    fields = parse_request(body)
    with store.lock:
        return _dispatch(op, fields, store)


def _dispatch(op, fields, store):
    raw = _first(fields, 0, (bytes, bytearray))
    if not raw and op in (1, 19):
        raw = _first(fields, 1, (bytes, bytearray))
    token, rec = store.session(raw or None)
    if op in (1, 19):
        game = _first(fields, 4, int)
        if game:
            store.note_game(rec, game)
    acc = store.account(rec)

    if op in (1, 19):
        if not acc:
            return frame(2, _cookie(token) + [field_str(21, HELLO)])
        return frame(1, _cookie(token) + [field_bytes(21, token)] + _rows(acc))

    if op == 2:
        acc, err = store.login(rec, _first(fields, 2, str) or "", _first(fields, 3, str) or "")
        if err:
            # Status 2 is the New user / Existing user screen, and tag 21 is its text.
            return frame(2, _cookie(token) + [field_str(21, err)])
        return frame(1, _cookie(token) + [field_bytes(21, token)] + _rows(acc))

    if op == 3:
        acc, err = store.register(rec, _first(fields, 2, str) or "", _first(fields, 3, str) or "")
        if err:
            # Opcode 3 ignores every status except 1, so the refusal is a dialog.
            return frame(2, _cookie(token) + [field_str(2, err)])
        # Status 1 is re-read as a login. An empty hero list is create-hero.
        return frame(1, _cookie(token) + [field_bytes(21, token)] + _rows(acc))

    if op == 5:
        if not store.account(rec):
            return frame(2, _cookie(token) + [field_str(2, "Create an account first.")])
        ok, suggestion = store.create_hero(
            rec, _first(fields, 1, str) or "", _first(fields, 2, int)
        )
        if not ok:
            return frame(2, _cookie(token) + [field_str(20, suggestion)])
        return frame(1, _cookie(token))

    if op == 4:
        store.choose(rec, _first(fields, 1, str) or "")
        return frame(1, _cookie(token))

    if op == 6:
        store.delete_hero(rec, _first(fields, 1, str) or "")
        return frame(1, _cookie(token) + [field_str(2, NOTE)])

    if op == 35 or op in (30, 31, 32, 34, 36, 63):
        answered = store.rooms.handle(rec, op, fields)
        if answered is not None:
            status, parts = answered
            return frame(status, _cookie(token) + [encode(*part) for part in parts])

    if op in LIST_OPS:
        # No tag 20: the phone builds an empty vector and adds Back itself.
        # Status 1 on opcode 38 would insert a sign-up row we have no text for.
        return frame(3, _cookie(token) + [field_str(21, "Not preserved")])

    if op == 51:
        return frame(1, _cookie(token) + [field_str(20, NOTE), field_str(21, "Mail")])

    if op == 20:
        return frame(1, _cookie(token) + [field_str(20, store.purse(rec))])

    if op == 39:
        return frame(1, _cookie(token) + [field_str(2, store.purse(rec))])

    return frame(1, _cookie(token) + [field_str(2, NOTE)])


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
        except Exception:
            traceback.print_exc()
            reply = frame(1, [field_str(2, NOTE)])
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(reply)))
        self.end_headers()
        self.wfile.write(reply)
        op = opcode_of(script)
        print(f"{op}.pl -> {reply[2]} ({len(reply)} bytes)", flush=True)

    def log_message(self, fmt, *args):
        return


def main(argv):
    port = int(argv[1]) if len(argv) > 1 else 8082
    os.makedirs(LOGS, exist_ok=True)
    Handler.store = Store(SAVE)
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"cards on http://127.0.0.1:{port}/3/  save {SAVE}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main(sys.argv)
