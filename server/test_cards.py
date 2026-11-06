#!/usr/bin/env python3
"""What the Badaz phone will accept, checked without the emulator.

The reader below is g.run() / h.run(): magic 0xBABE, a status byte, a
discarded byte, a skipped int, then count fields of tag, type, and length.
Type 4 is a hero row and is not sliced by that length. Status 0 is the
"second login" kick, so no reply here may use it.
"""

import os
import random
import sys
import tempfile
import threading
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cards
import dealer

FAILED = []


def check(name, cond, detail=""):
    if cond:
        print(f"  \033[32mok\033[0m   {name}")
    else:
        print(f"  \033[31mFAIL\033[0m {name}" + (f"  — {detail}" if detail else ""))
        FAILED.append(name)


def client_read(blob):
    if len(blob) < 10 or int.from_bytes(blob[:2], "big") != cards.MAGIC:
        raise AssertionError("phone shows Magic number")
    status = blob[2]
    count = int.from_bytes(blob[8:10], "big")
    i = 10
    tags = {}
    for _ in range(count):
        tag, typ = blob[i], blob[i + 1]
        ln = int.from_bytes(blob[i + 2:i + 4], "big")
        i += 4
        if typ == 1:
            if ln == 1:
                val = int.from_bytes(blob[i:i + 1], "big", signed=True)
                i += 1
            elif ln == 2:
                val = int.from_bytes(blob[i:i + 2], "big", signed=True)
                i += 2
            elif ln == 4:
                val = int.from_bytes(blob[i:i + 4], "big", signed=True)
                i += 4
            else:
                raise AssertionError(f"ChnkLen:{ln}")
        elif typ in (2, 3):
            val = blob[i:i + ln].decode("utf-8")
            i += ln
        elif typ == 4:
            n = blob[i]
            i += 1
            val = blob[i:i + n].decode("utf-8")
            i += n
            n2 = blob[i]
            i += 1 + n2
            i += 2  # icon byte and flags
            n3 = blob[i]
            i += 1 + n3
            extra = int.from_bytes(blob[i:i + 2], "big")
            i += 2 + extra
        else:
            val = bytes(blob[i:i + ln])
            i += ln
        tags.setdefault(tag, []).append(val)
    if i != len(blob):
        raise AssertionError(f"left {len(blob) - i} bytes")
    if status == 0:
        raise AssertionError("status 0 kicks the phone out")
    return status, tags


def post(store, op, body):
    reply = cards.handle(f"/3/{op}.pl", body, store)
    return client_read(reply)


def hello_body(token=None, game=11):
    version = "1.0.0" if game == 10 else "1.0.2"
    parts = [cards.field_int(255, 1), cards.field_str(2, version), cards.field_int(4, game)]
    if token:
        parts.insert(0, cards.field_bytes(0, token))
    return b"".join(parts)


def cookie(token):
    return cards.field_bytes(0, token)


def ints4(blob):
    return [int.from_bytes(blob[i:i + 4], "big", signed=True) for i in range(0, len(blob), 4)]


def seat_names(records):
    found = {}
    for rec in records:
        found[rec[0]] = rec[2:].decode("utf-8")
    return found


def banked(store, name):
    row = store.chips(name)
    return row["gold"] + row["in_play"] + row["committed"]


def open_hero(store, nick, hero, game=11):
    status, tags = post(store, 1, hello_body(game=game))
    token = tags[0][0]
    post(store, 3, b"".join([cookie(token), cards.field_str(2, nick), cards.field_str(3, "pw")]))
    post(store, 5, b"".join([
        cookie(token), cards.field_str(1, hero), cards.field_int(2, 1),
    ]))
    return token


class Scripted(random.Random):
    """Shuffle so pop() deals `dealt` first, then the rest of the deck."""

    def __init__(self, dealt):
        super().__init__(0)
        self.dealt = list(dealt)

    def shuffle(self, x):
        pool = list(x)
        front = []
        for card in self.dealt:
            pool.remove(card)
            front.append(card)
        x[:] = pool + front[::-1]


def ranks():
    print("hand ranks")
    same = lambda ranks, suit=0: [dealer.card_byte(suit, rank) for rank in ranks]
    mixed = lambda ranks: [dealer.card_byte(i % 4, rank) for i, rank in enumerate(ranks)]

    def cat(cards):
        return dealer.category(dealer._eval5(cards))

    check("royal flush is 9", cat(same((1, 13, 12, 11, 10))) == 9)
    check("a wheel straight flush is 8", cat(same((1, 2, 3, 4, 5))) == 8)
    check("four of a kind is 7", cat(
        [dealer.card_byte(suit, 1) for suit in range(4)] + [dealer.card_byte(0, 13)]
    ) == 7)
    check("a full house is 6", cat([
        dealer.card_byte(0, 13), dealer.card_byte(1, 13), dealer.card_byte(2, 13),
        dealer.card_byte(0, 12), dealer.card_byte(1, 12),
    ]) == 6)
    check("a flush is 5", cat(same((2, 4, 6, 8, 11))) == 5)
    check("a straight is 4", cat(mixed((10, 11, 12, 13, 1))) == 4)
    check("a wheel is a straight and not a royal", cat(mixed((1, 2, 3, 4, 5))) == 4)
    check("three of a kind is 3", cat([
        dealer.card_byte(0, 7), dealer.card_byte(1, 7), dealer.card_byte(2, 7),
        dealer.card_byte(0, 13), dealer.card_byte(1, 12),
    ]) == 3)
    check("two pair is 2", cat([
        dealer.card_byte(0, 8), dealer.card_byte(1, 8),
        dealer.card_byte(0, 9), dealer.card_byte(1, 9),
        dealer.card_byte(2, 2),
    ]) == 2)
    check("a pair is 1", cat([
        dealer.card_byte(0, 1), dealer.card_byte(1, 1),
        dealer.card_byte(2, 13), dealer.card_byte(3, 12), dealer.card_byte(0, 11),
    ]) == 1)
    check("high card is 0", cat(mixed((2, 4, 6, 8, 11))) == 0)
    aces = dealer._eval5([
        dealer.card_byte(0, 1), dealer.card_byte(1, 1),
        dealer.card_byte(2, 13), dealer.card_byte(3, 12), dealer.card_byte(0, 11),
    ])
    kings = dealer._eval5([
        dealer.card_byte(0, 13), dealer.card_byte(1, 13),
        dealer.card_byte(2, 1), dealer.card_byte(3, 12), dealer.card_byte(0, 11),
    ])
    check("a pair of aces beats a pair of kings", aces > kings)
    check("blackjack ace and king is 21", dealer.hand_value([
        dealer.card_byte(0, 1), dealer.card_byte(1, 13),
    ]) == 21)
    check("two aces is 12", dealer.hand_value([
        dealer.card_byte(0, 1), dealer.card_byte(1, 1),
    ]) == 12)
    check("a soft 17 stands as 17", dealer.hand_value([
        dealer.card_byte(0, 1), dealer.card_byte(1, 6),
    ]) == 17)
    check("king queen two is a bust", dealer.hand_value([
        dealer.card_byte(0, 13), dealer.card_byte(1, 12), dealer.card_byte(2, 2),
    ]) == 22)


def poker_goblin():
    print("goblin poker")
    path = os.path.join(tempfile.mkdtemp(), "cards.json")
    store = cards.Store(path)
    token = open_hero(store, "Ned", "Ned")
    status, tags = post(store, 30, b"".join([cookie(token), cards.field_int(1, 1)]))
    names = seat_names(tags.get(22, []))
    stacks = ints4(tags[32][0]) if 32 in tags else []
    check("goblin deal puts the hero in seat 0 against the three opponents",
          status == 2 and tags.get(21) == [0] and tags.get(23) == [0]
          and tags.get(29) == [3] and len(tags.get(24, [b""])[0]) == 2
          and names.get(0) == "Ned"
          and [names.get(i) for i in (1, 2, 3)] == list(dealer.BOTS)
          and sum(stacks) + tags.get(30, [0])[0] == 400,
          "status %s seat %s button %s actor %s names %s" % (
              status, tags.get(21), tags.get(23), tags.get(29), names))
    status, tags = post(store, 63, cookie(token))
    status, tags = post(store, 63, b"".join([
        cookie(token), cards.field_str(5, "9:Menu"),
    ]))
    check("the menu request does not fold the hero",
          status == 1 and tags.get(29) == [0] and ints4(tags[26][0])[0] != -1,
          "status %s actor %s" % (status, tags.get(29)))
    for _ in range(40):
        if status == 3:
            break
        actor = tags.get(29, [-1])[0]
        extra = b""
        if actor == tags.get(21, [-1])[0]:
            text = "1:Check" if tags.get(34, [0])[0] == 0 else "1:Call"
            extra = cards.field_str(5, text)
        status, tags = post(store, 63, cookie(token) + extra)
        if status != 3 and 32 in tags and 30 in tags:
            held = sum(ints4(tags[32][0])) + tags[30][0]
            if held != 400:
                check("chips stay on the table during the hand", False, str(held))
                return
    wins = ints4(tags[26][0]) if 26 in tags else []
    final = ints4(tags[32][0]) if 32 in tags else []
    check("the hand reaches showdown and every chip is still there",
          status == 3 and len(tags.get(36, [b""])[0]) == 8
          and sum(final) == 400 and sum(w for w in wins if w > 0) == tags.get(30, [-1])[0],
          "status %s stacks %s wins %s pot %s" % (status, final, wins, tags.get(30)))

    token = open_hero(store, "Ida", "Ida")
    status, tags = post(store, 30, b"".join([cookie(token), cards.field_int(1, 1)]))
    check("a fresh goblin hand still deals", status == 2 and tags.get(21) == [0])
    status, tags = post(store, 34, cookie(token))
    gone = store.chips("Ida")
    check("leaving before acting returns the whole buy-in",
          status == 1 and 2 not in tags and gone["gold"] == 1000
          and gone["in_play"] == 0 and gone["committed"] == 0,
          str(gone))


def poker_public():
    print("public poker")
    path = os.path.join(tempfile.mkdtemp(), "cards.json")
    store = cards.Store(path)
    ann = open_hero(store, "Ann", "Ann")
    bob = open_hero(store, "Bob", "Bob")
    cyd = open_hero(store, "Cyd", "Cyd")
    status, tags = post(store, 30, cookie(ann))
    check("the first public seat waits",
          status == 1 and isinstance(tags.get(20, [None])[0], str)
          and tags.get(22) and 24 not in tags)
    status, bob_tags = post(store, 30, cookie(bob))
    status_a, ann_tags = post(store, 31, cookie(ann))
    check("two players are dealt different hole cards",
          status == 2 and status_a == 2
          and len(bob_tags.get(24, [b""])[0]) == 2
          and ann_tags.get(24) != bob_tags.get(24),
          "%s vs %s" % (ann_tags.get(24), bob_tags.get(24)))
    status, tags = post(store, 30, cookie(cyd))
    check("a third player waits out the current hand",
          status == 1 and 24 not in tags, str(status))
    status, tags = post(store, 34, cookie(bob))
    check("leaving the table does not open a dialog", status == 1 and 2 not in tags)
    status, tags = post(store, 63, cookie(ann))
    check("the player still sitting is shown the finished hand",
          status == 3 and len(tags.get(36, [b""])[0]) == 8, str(status))
    total = banked(store, "Ann") + banked(store, "Bob") + banked(store, "Cyd")
    check("public chips only move between the three players", total == 3000, str(total))


def blackjack_goblin():
    print("goblin blackjack")
    path = os.path.join(tempfile.mkdtemp(), "cards.json")
    store = cards.Store(path)
    token = open_hero(store, "Bea", "Bea", game=10)
    status, tags = post(store, 30, b"".join([cookie(token), cards.field_int(1, 1)]))
    hero = [rec for rec in tags.get(23, []) if rec and rec[0] == 0]
    check("blackjack deals the hero at seat 0",
          status == 2 and tags.get(21) == [0] and hero and len(hero[0]) == 7
          and len(tags.get(23, [])) == 4,
          "status %s seat %s cards %s" % (status, tags.get(21), len(tags.get(23, []))))
    status, tags = post(store, 32, b"".join([cookie(token), cards.field_str(5, "2:Stand")]))
    table = store.rooms.tables[(10, "goblin", "Bea")]
    held = sum(seat.stack for seat in table.seats if seat) + table.carried
    check("standing lets the opponents finish and keeps the chips",
          status == 3 and held == 400, "status %s held %s" % (status, held))

    path = os.path.join(tempfile.mkdtemp(), "cards.json")
    store = cards.Store(path)
    store.rooms.rng = Scripted([
        dealer.card_byte(0, 2), dealer.card_byte(1, 3),
        dealer.card_byte(0, 10), dealer.card_byte(1, 10),
        dealer.card_byte(2, 10), dealer.card_byte(3, 10),
        dealer.card_byte(0, 9), dealer.card_byte(1, 9),
        dealer.card_byte(2, 4),
    ])
    token = open_hero(store, "Gil", "Gil", game=10)
    post(store, 30, b"".join([cookie(token), cards.field_int(1, 1)]))
    status, tags = post(store, 32, b"".join([cookie(token), cards.field_str(5, "1:Hit")]))
    grown = [rec for rec in tags.get(23, []) if rec[:1] == b"\x00" and len(rec) == 4]
    check("a hit adds a third card and the turn stays open",
          status == 2 and len(grown) == 1 and list(grown[0]) == [
              0, dealer.card_byte(0, 2), dealer.card_byte(1, 3), dealer.card_byte(2, 4),
          ],
          "status %s %s" % (status, tags.get(23)))
    status, tags = post(store, 32, b"".join([cookie(token), cards.field_str(5, "2:Stand")]))
    table = store.rooms.tables[(10, "goblin", "Gil")]
    held = sum(seat.stack for seat in table.seats if seat) + table.carried
    check("standing after the hit finishes the hand", status == 3 and held == 400,
          "status %s held %s" % (status, held))


def refund_on_start():
    print("sqlite")
    path = os.path.join(tempfile.mkdtemp(), "cards.json")
    store = cards.Store(path)
    open_hero(store, "Rex", "Rex")
    store.db.execute(
        "UPDATE heroes SET gold=500, in_play=40, committed=10 WHERE name_key='rex'"
    )
    store.db.commit()
    again = cards.Store(path)
    row = again.chips("Rex")
    check("a restart pays table chips back to gold",
          row["gold"] == 550 and row["in_play"] == 0 and row["committed"] == 0, str(row))
    status, tags = post(again, 1, hello_body())
    token = tags[0][0]
    status, tags = post(again, 2, b"".join([
        cookie(token), cards.field_str(2, "Rex"), cards.field_str(3, "later"),
    ]))
    kept = again.db.execute(
        "SELECT password FROM accounts WHERE nick_key='rex'"
    ).fetchone()[0]
    check("a restarted save still refuses a different password",
          status == 2 and tags.get(21) == ["Wrong password."] and kept == "pw",
          str(tags.get(21)))


def main():
    path = os.path.join(tempfile.mkdtemp(), "cards.json")
    store = cards.Store(path)

    print("login")
    status, tags = post(store, 1, hello_body())
    check("hello with no key asks for a nickname",
          status == 2 and tags.get(21) == [cards.HELLO] and tags.get(23) is None
          and isinstance(tags.get(0, [None])[0], bytes),
          str(tags))
    token = tags[0][0]

    status, tags = post(store, 2, b"".join([
        cards.field_bytes(0, token),
        cards.field_str(2, "Zed"),
        cards.field_str(3, "secret"),
    ]))
    missing = store.db.execute(
        "SELECT nick_key FROM accounts WHERE nick_key='zed'"
    ).fetchone()
    check("login of an unknown name does not create an account",
          status == 2 and tags.get(21) == ["No account by that name."]
          and 20 not in tags and missing is None,
          str(tags.get(21)))

    status, tags = post(store, 3, b"".join([
        cards.field_bytes(0, token),
        cards.field_str(2, "Zed"),
        cards.field_str(3, ""),
    ]))
    check("register without a password is refused",
          status == 2 and tags.get(2) == ["Type a password."], str(tags.get(2)))

    status, tags = post(store, 3, b"".join([
        cards.field_bytes(0, token),
        cards.field_str(2, "Zed"),
        cards.field_str(3, "secret"),
    ]))
    check("register opens an account with no hero yet",
          status == 1 and 20 not in tags and tags.get(0) == [token],
          str({k: tags[k] for k in tags if k != 21}))

    status, tags = post(store, 2, b"".join([
        cards.field_bytes(0, token),
        cards.field_str(2, "Zed"),
        cards.field_str(3, "not-the-password"),
    ]))
    check("a different password is refused",
          status == 2 and tags.get(21) == ["Wrong password."] and 20 not in tags,
          str(tags.get(21)))
    stored = store.db.execute(
        "SELECT password FROM accounts WHERE nick_key='zed'"
    ).fetchone()[0]
    check("the stored password is unchanged", stored == "secret")

    status, tags = post(store, 3, b"".join([
        cards.field_bytes(0, token),
        cards.field_str(2, "Zed"),
        cards.field_str(3, "other"),
    ]))
    check("register of a known nickname is refused",
          status == 2 and tags.get(2) == ["That name is already registered."],
          str(tags.get(2)))
    stored = store.db.execute(
        "SELECT password FROM accounts WHERE nick_key='zed'"
    ).fetchone()[0]
    check("a refused register leaves the password", stored == "secret")

    status, tags = post(store, 2, b"".join([
        cards.field_bytes(0, token),
        cards.field_str(2, "Zed"),
        cards.field_str(3, "secret"),
    ]))
    check("the password from registration opens the account",
          status == 1 and 20 not in tags and tags.get(0) == [token])

    status, tags = post(store, 5, b"".join([
        cards.field_bytes(0, token),
        cards.field_str(1, "Zed"),
        cards.field_int(2, 1),
    ]))
    check("create hero status 1 is the town", status == 1 and tags.get(23) is None)

    status, tags = post(store, 1, hello_body(token))
    check("the saved key comes back to that hero",
          status == 1 and tags.get(20) == ["Zed"] and isinstance(tags.get(21, [None])[0], bytes),
          str(tags.get(20)))

    status, _ = post(store, 4, b"".join([
        cards.field_bytes(0, token),
        cards.field_str(1, "Zed"),
    ]))
    check("picking the hero is status 1, which enters town", status == 1)

    status, tags = post(store, 5, b"".join([
        cards.field_bytes(0, token),
        cards.field_str(1, "Zed"),
        cards.field_int(2, 2),
    ]))
    check("a duplicate hero name is handed back to type again",
          status == 2 and tags.get(20) == ["Zed2"], str(tags.get(20)))

    print("town screens that have no recovered rows")
    status, tags = post(store, 20, cards.field_bytes(0, token))
    check("hero info shows the starting gold",
          status == 1 and tags.get(20) == ["Gold: 100 gold 0 silver"], str(tags.get(20)))
    status, tags = post(store, 39, cards.field_bytes(0, token))
    check("my stats shows the same gold",
          status == 1 and tags.get(2) == ["Gold: 100 gold 0 silver"], str(tags.get(2)))
    status, tags = post(store, 50, cards.field_bytes(0, token))
    check("mail is an empty list, and the phone adds its own rows",
          status != 0 and tags.get(21) == ["Not preserved"] and 20 not in tags)
    status, tags = post(store, 30, cards.field_bytes(0, token))
    check("one player at the public table waits, and no hand is dealt",
          status == 1 and isinstance(tags.get(20, [None])[0], str) and tags.get(22)
          and 24 not in tags and 36 not in tags, str(tags))
    status, tags = post(store, 7, cards.field_bytes(0, token))
    check("a menu with no reply shape shows a note",
          status == 1 and tags.get(2) == [cards.NOTE])

    print("http")
    httpd = cards.ThreadingHTTPServer(("127.0.0.1", 0), cards.Handler)
    cards.Handler.store = store
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    body = hello_body(token)
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/3/1.pl", data=body, method="POST")
    with urllib.request.urlopen(req, timeout=5) as resp:
        raw = resp.read()
        code = resp.status
    httpd.shutdown()
    status, tags = client_read(raw)
    check("POST /3/1.pl answers 200 and the hero",
          code == 200 and status == 1 and tags.get(20) == ["Zed"])

    store2 = cards.Store(path)
    status, tags = post(store2, 1, hello_body(token))
    check("the save reloads Zed", status == 1 and tags.get(20) == ["Zed"], str(tags.get(20)))
    refunded = store2.chips("Zed")
    check("reopening the save returns table chips to gold",
          refunded["gold"] == 1000 and refunded["in_play"] == 0 and refunded["committed"] == 0,
          str(refunded))

    ranks()
    poker_goblin()
    poker_public()
    blackjack_goblin()
    refund_on_start()

    if FAILED:
        print(f"\n{len(FAILED)} FAILED")
        return 1
    print("\nall card checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
