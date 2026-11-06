"""Dealers for the Badaz phones.

The jars already draw the table and rank the cards. This module fills in
the tags those screens read. It is not a recovered watAgame table dump:
mail, rankings, the shop, portraits, and tournaments stay empty.

A card is one byte, (suit << 4) | rank, suit 0..3 and rank 1..13. Ace is
rank 1 and counts as 14 in poker, or as 1 or 11 in blackjack.

Poker matches the offline table: four seats, small blind 1, big blind 2,
buy-in 100. The phone shows a chip count as n/10 gold and n%10 silver.
Blackjack's offline "100" is a hand counter stored on the phone, not a
stake. The online bet sizes are 1, 2, 5, 10, 20 and 50; a goblin or public
blackjack table uses 10, the "1 gold" row.
"""

import random
from itertools import combinations

SEATS = 4
BUY_IN = 100
POKER_SB = 1
POKER_BB = 2
BJ_ANTE = 10
TURN = 20
BOTS = ("Slick Rick", "Jinxy", "Tiny Tut")


def card_byte(suit, rank):
    return ((suit & 3) << 4) | (rank & 0xF)


def hand_value(cards):
    """Blackjack total. Matches b.a(cards, 0, n): faces are 10, aces 1 plus 10 while the total stays at or under 11."""
    total = 0
    aces = 0
    for by in cards:
        if not by:
            continue
        rank = by & 0xF
        if 2 <= rank <= 10:
            total += rank
        elif rank >= 11:
            total += 10
        elif rank == 1:
            total += 1
            aces += 1
    for _ in range(aces):
        if total <= 11:
            total += 10
    return total


def _eval5(cards):
    """Five-card rank from the offline poker dealer. The top byte is the category."""
    counts = [0] * 15
    suits = [0] * 4
    ordered = []
    for by in cards:
        rank = by & 0xF
        counts[rank] += 1
        sort_rank = 14 if rank == 1 else rank
        if rank == 1:
            counts[14] += 1
        suits[(by >> 4) & 3] += 1
        placed = False
        index = 0
        while not placed:
            if index >= len(ordered):
                ordered.append(by)
                break
            other = ordered[index] & 0xF
            if other == 1:
                other = 14
            if sort_rank > other:
                ordered.insert(index, by)
                break
            index += 1
    straight = 0
    for start in range(0, len(counts) - 4):
        if all(counts[start + step] == 1 for step in range(5)):
            straight = 1
            break
    flush = 1 if any(n == 5 for n in suits) else 0
    freq = [0] * 5
    max_count = 0
    for rank in range(2, 15):
        n = counts[rank]
        if 0 <= n < 5:
            freq[n] += 1
        if n > max_count:
            max_count = n
    if straight and counts[1] == 1 and counts[5] == 1 and ordered:
        ordered.append(ordered.pop(0))
    if max_count > 1:
        primary = []
        rest = []
        for by in ordered:
            rank = by & 0xF
            sort_rank = 14 if rank == 1 else rank
            if counts[sort_rank] == max_count:
                primary.append(by)
            else:
                rest.append(by)
        ordered = primary + rest
    score = 0
    for index, by in enumerate(ordered[:5]):
        rank = by & 0xF
        if rank == 1:
            rank = 14
        score += rank << (5 * (4 - index))
    if straight and flush and ordered and (ordered[4] & 0xF) == 10:
        score += 0x12000000
    elif straight and flush:
        score += 0x10000000
    elif freq[4] == 1:
        score += 0x0E000000
    elif freq[3] == 1 and freq[2] == 1:
        score += 0x0C000000
    elif flush:
        score += 0x0A000000
    elif straight:
        score += 0x08000000
    elif freq[3] == 1:
        score += 0x06000000
    elif freq[2] == 2:
        score += 0x04000000
    elif freq[2] == 1:
        score += 0x02000000
    return score


def best_score(cards):
    cards = [c for c in cards if c]
    if len(cards) < 5:
        return 0
    return max(_eval5(combo) for combo in combinations(cards, 5))


def category(score):
    return {
        0x12: 9, 0x10: 8, 0x0E: 7, 0x0C: 6, 0x0A: 5,
        0x08: 4, 0x06: 3, 0x04: 2, 0x02: 1,
    }.get((score >> 24) & 0xFF, 0)


def award(contrib, folded, score, button):
    """Pay a pot. Returns chips each seat gets back, and the winning category.

    Every contributed chip is paid out. A seat that already folded is not
    eligible. If nobody is eligible the chips are returned to the seats
    that posted them.
    """
    if not any(not folded[i] for i in range(SEATS)):
        return list(contrib), 0
    winnings = [0] * SEATS
    prev = 0
    best = 0
    for level in sorted({c for c in contrib if c > 0}):
        layer = level - prev
        involved = [i for i in range(SEATS) if contrib[i] >= level]
        size = layer * len(involved)
        eligible = [i for i in involved if not folded[i]]
        prev = level
        if size <= 0:
            continue
        if not eligible:
            # Nobody who posted this layer is still in. It was not called.
            ordered = [(button + step) % SEATS for step in range(1, SEATS + 1)]
            ordered = [i for i in ordered if i in involved]
            share, extra = divmod(size, len(ordered))
            for n, seat in enumerate(ordered):
                winnings[seat] += share + (1 if n < extra else 0)
            continue
        top = max(score[i] for i in eligible)
        winners = [i for i in eligible if score[i] == top]
        ordered = [(button + step) % SEATS for step in range(1, SEATS + 1)]
        ordered = [i for i in ordered if i in winners]
        share, extra = divmod(size, len(ordered))
        for n, seat in enumerate(ordered):
            winnings[seat] += share + (1 if n < extra else 0)
        best = top
    return winnings, category(best)


def fresh_deck(rng):
    deck = [card_byte(suit, rank) for suit in range(4) for rank in range(1, 14)]
    rng.shuffle(deck)
    return deck


def ints4(values):
    return b"".join(int(v).to_bytes(4, "big", signed=True) for v in values)


def seat_record(seat, name, flag=1):
    raw = (name or "").encode("utf-8")
    return bytes([seat & 0xFF, flag & 0xFF]) + raw


def blind_heuristic(seat, button, occupied, sb):
    """Chips the phone thinks this seat has already put in before anyone acts.

    It only looks at the two occupied seats after the button. That matches
    a full table. Heads-up leaves the button's own blind out, so the bet we
    send is adjusted per phone in the action frame.
    """
    found = 0
    posted = 0
    for step in range(1, SEATS):
        other = (button + step) % SEATS
        if other not in occupied:
            continue
        found += 1
        if other == seat:
            posted = sb * found
        if found >= 2:
            break
    return posted


class Seat:
    def __init__(self, name, stack, owner):
        self.name = name
        self.stack = stack
        self.owner = owner  # hero name, or None for a bot
        self.hole = []
        self.folded = False
        self.contrib = 0
        self.street = 0
        self.client_street = 0
        self.action = 0
        self.acted = False
        self.left = False

    @property
    def human(self):
        return bool(self.owner) and not self.left


class PokerTable:
    def __init__(self, bank, sb=POKER_SB, bb=POKER_BB, cap=4, turn=TURN, goblin=False, rng=None):
        self.bank = bank
        self.sb = sb or POKER_SB
        self.bb = bb or self.sb * 2
        self.cap = cap or 4
        self.turn = turn or TURN
        self.goblin = goblin
        self.rng = rng or random.Random()
        self.seats = [None] * SEATS
        self.phase = "waiting"
        self.button = -1
        self.deck = []
        self.board = []
        self.pot = 0
        self.bet = 0
        self.raises = 0
        self.actor = None
        self.seen = {}
        self.wins = [0] * SEATS
        self.rank = 0
        self.token = 0

    def occupants(self):
        return [i for i, seat in enumerate(self.seats) if seat and not seat.left]

    def _next(self, start, pred):
        for step in range(1, SEATS + 1):
            seat = (start + step) % SEATS
            if pred(seat):
                return seat
        return None

    def sitting(self, hero):
        for seat in self.seats:
            if seat and seat.owner == hero and not seat.left:
                return True
        return False

    def sit(self, hero, stack):
        if self.sitting(hero):
            return self._index(hero)
        for index, seat in enumerate(self.seats):
            if seat is None:
                player = Seat(hero, stack, hero)
                # Joining during a hand waits for the next deal.
                if self.phase == "hand":
                    player.folded = True
                    player.acted = True
                self.seats[index] = player
                self.seen[hero] = "waiting"
                self.bank.set_table(hero, stack, 0)
                return index
        return None

    def sit_bots(self):
        used = {seat.name for seat in self.seats if seat}
        for name in BOTS:
            if name in used:
                continue
            for index, seat in enumerate(self.seats):
                if seat is None:
                    self.seats[index] = Seat(name, BUY_IN, None)
                    break

    def _index(self, hero):
        for index, seat in enumerate(self.seats):
            if seat and seat.owner == hero and not seat.left:
                return index
        return None

    def leave(self, hero):
        index = self._index(hero)
        if index is None:
            return
        seat = self.seats[index]
        if self.phase != "hand":
            self.bank.add_gold(hero, seat.stack)
            self.seats[index] = None
            self.seen.pop(hero, None)
            return
        # Fold. Chips already in the pot stay there for whoever is still in.
        seat.folded = True
        seat.left = True
        seat.action = -1
        seat.acted = True
        self.seen.pop(hero, None)
        if self.actor == index or self._one_left() or self._round_done():
            self._after_action(index)
        self._bots()
        self.bank.add_gold(hero, seat.stack)
        seat.stack = 0

    def _refund_abandoned(self):
        """Nobody is sitting. Give posted chips back to the heroes who posted them."""
        for index, seat in enumerate(self.seats):
            if seat and seat.owner and seat.contrib:
                self.bank.add_gold(seat.owner, seat.contrib)
                seat.contrib = 0
            if seat and (seat.left or not seat.human):
                self.seats[index] = None
        self.pot = 0
        self.phase = "waiting"
        self.board = []

    def _sync(self):
        for seat in self.seats:
            if seat and seat.human:
                committed = seat.contrib if self.phase == "hand" else 0
                self.bank.set_table(seat.owner, seat.stack, committed)
        if self.phase != "hand":
            for seat in self.seats:
                if seat and seat.left and seat.owner:
                    self.bank.clear_committed(seat.owner)

    def _live(self, index):
        seat = self.seats[index]
        return bool(seat) and not seat.folded and not seat.left and seat.stack > 0

    def _restock(self, hero):
        for index, seat in enumerate(list(self.seats)):
            if not seat:
                continue
            if seat.human and seat.stack <= 0:
                seat.stack += self.bank.rebuy(seat.owner, BUY_IN)
            elif self.goblin and not seat.owner and seat.stack <= 0:
                seat.stack = BUY_IN
            if seat.stack <= 0 or (seat.left and self.phase != "hand"):
                if seat.human and seat.stack <= 0:
                    self.bank.set_table(seat.owner, 0, 0)
                self.seats[index] = None
                self.seen.pop(seat.owner, None)
        if hero and self._index(hero) is None:
            return False
        humans = [s for s in self.seats if s and s.human]
        if self.goblin:
            return len([s for s in self.seats if s]) >= 2
        return len(humans) >= 2

    def start_hand(self, hero):
        if not self._restock(hero):
            self.phase = "waiting"
            return "wait" if self._index(hero) is not None else "broke"
        players = [i for i, seat in enumerate(self.seats) if seat and seat.stack > 0]
        if len(players) < 2:
            self.phase = "waiting"
            return "wait"
        self.token += 1
        self.phase = "hand"
        self.deck = fresh_deck(self.rng)
        self.board = []
        self.pot = 0
        self.bet = 0
        self.raises = 0
        self.wins = [0] * SEATS
        self.rank = 0
        for seat in self.seats:
            if not seat:
                continue
            seat.hole = [self.deck.pop(), self.deck.pop()]
            seat.folded = False
            seat.contrib = 0
            seat.street = 0
            seat.client_street = 0
            seat.action = 0
            seat.acted = False
            seat.left = False
        self.button = self._next(self.button, lambda i: self.seats[i] and self.seats[i].stack > 0)
        if len(players) == 2:
            sb = self.button
            bb = self._next(sb, self._live)
            first = sb
        else:
            sb = self._next(self.button, self._live)
            bb = self._next(sb, self._live)
            first = self._next(bb, self._live)
        self._post(sb, self.sb, -5)
        self._post(bb, self.bb, -4)
        self.bet = max(seat.street for seat in self.seats if seat)
        occupied = set(self.occupants())
        for index, seat in enumerate(self.seats):
            if seat:
                seat.client_street = blind_heuristic(index, self.button, occupied, self.sb)
        self.actor = first if first is not None else sb
        self._skip_actor()
        for seat in self.seats:
            if seat and seat.owner:
                self.seen[seat.owner] = "need"
        self._sync()
        return "deal"

    def _post(self, index, amount, code):
        seat = self.seats[index]
        take = min(amount, seat.stack)
        seat.stack -= take
        seat.street += take
        seat.contrib += take
        self.pot += take
        seat.action = code
        if seat.stack == 0:
            seat.acted = True

    def _skip_actor(self):
        if self.actor is None:
            return
        for _ in range(SEATS):
            seat = self.seats[self.actor]
            if seat and not seat.folded and not seat.left and seat.stack > 0 and not (
                seat.acted and seat.street >= self.bet
            ):
                return
            nxt = self._next(self.actor, lambda i: True)
            if nxt is None or nxt == self.actor:
                return
            self.actor = nxt

    def _round_done(self):
        live = [s for s in self.seats if s and not s.folded and not s.left]
        if len(live) <= 1:
            return True
        for seat in live:
            if seat.stack > 0 and (not seat.acted or seat.street < self.bet):
                return False
        return True

    def _one_left(self):
        return sum(1 for s in self.seats if s and not s.folded and not s.left) <= 1

    def _take(self, seat, amount):
        amount = max(0, min(amount, seat.stack))
        seat.stack -= amount
        seat.street += amount
        seat.contrib += amount
        self.pot += amount
        return amount

    def _act(self, index, kind):
        seat = self.seats[index]
        if seat is None or seat.folded or seat.left or self.phase != "hand":
            return
        owed = max(0, self.bet - seat.street)
        inc = self.bb if len(self.board) <= 3 else self.bb * 2
        if kind == "raise" and (self.raises >= self.cap or seat.stack <= owed):
            kind = "call"
        if kind == "check" and owed > 0:
            kind = "call"
        client_add = 0
        if seat.human:
            ae = seat.client_street + owed if owed else 0
            if kind == "call":
                client_add = max(0, min(ae - seat.client_street, seat.stack))
            elif kind == "raise":
                client_add = max(0, min(ae + inc - 2 * seat.client_street, seat.stack))
        if kind == "fold":
            seat.folded = True
            seat.action = -1
            seat.acted = True
        elif kind == "call" or kind == "check":
            poker = owed if kind == "call" else 0
            self._take(seat, max(poker, client_add))
            seat.action = -3 if owed == 0 and client_add == 0 else -2
            seat.acted = True
        elif kind == "raise":
            poker = min(owed + inc, seat.stack)
            self._take(seat, max(poker, client_add))
            self.bet = seat.street
            self.raises += 1
            seat.action = seat.street
            seat.acted = True
            for other in self.seats:
                if other is not None and other is not seat and not other.folded and not other.left and other.stack > 0:
                    other.acted = False
        if seat.human:
            seat.client_street += client_add
        self._after_action(index)

    def _after_action(self, index):
        if self._one_left() or not any(s and not s.folded and not s.left for s in self.seats):
            self._showdown()
            return
        if not self._round_done():
            nxt = self._next(index, lambda i: self._needs_to_act(i))
            self.actor = nxt if nxt is not None else index
            return
        actionable = [
            s for s in self.seats
            if s and not s.folded and not s.left and s.stack > 0
        ]
        if len(self.board) >= 5 or len(actionable) <= 1:
            while len(self.board) < 5 and not self._one_left():
                self.board.append(self.deck.pop())
            self._showdown()
            return
        deal = 3 if not self.board else 1
        for _ in range(deal):
            self.board.append(self.deck.pop())
        self.bet = 0
        self.raises = 0
        for seat in self.seats:
            if not seat:
                continue
            seat.street = 0
            seat.client_street = 0
            seat.acted = seat.stack <= 0 or seat.folded or seat.left
            if not seat.folded and not seat.left and seat.stack > 0:
                seat.action = 0
        nxt = self._next(self.button, self._live)
        self.actor = nxt if nxt is not None else self.button
        if self._round_done():
            self._after_action(self.actor if self.actor is not None else 0)

    def _needs_to_act(self, index):
        seat = self.seats[index]
        if not seat or seat.folded or seat.left or seat.stack <= 0:
            return False
        return (not seat.acted) or seat.street < self.bet

    def _showdown(self):
        folded = []
        contrib = []
        score = []
        live = 0
        for index, seat in enumerate(self.seats):
            if not seat:
                folded.append(True)
                contrib.append(0)
                score.append(0)
                continue
            gone = seat.folded or seat.left
            folded.append(gone)
            contrib.append(seat.contrib)
            if gone:
                score.append(0)
            else:
                live += 1
                score.append(best_score(list(seat.hole) + list(self.board)) if len(self.board) == 5 else 0)
        winnings, rank = award(contrib, folded, score, self.button if self.button >= 0 else 0)
        if live <= 1:
            rank = 0
        self.rank = rank
        self.wins = [0] * SEATS
        for index, seat in enumerate(self.seats):
            if not seat:
                continue
            seat.stack += winnings[index]
            seat.contrib = 0
            seat.street = 0
            if seat.folded or seat.left:
                self.wins[index] = -1
            elif winnings[index] > 0:
                self.wins[index] = winnings[index]
            else:
                self.wins[index] = 0
        self.pot = sum(contrib)
        self.phase = "showdown"
        self.actor = None
        for seat in list(self.seats):
            if seat and seat.left and seat.owner:
                self.bank.clear_committed(seat.owner)
        self.seats = [seat if seat and not seat.left else None for seat in self.seats]
        self._sync()

    def _bots(self):
        guard = 0
        while self.phase == "hand" and self.actor is not None and guard < 24:
            seat = self.seats[self.actor]
            if seat is None or seat.human:
                return
            if seat.left or seat.folded or seat.stack <= 0:
                self._after_action(self.actor)
                guard += 1
                continue
            owed = max(0, self.bet - seat.street)
            if owed <= 0:
                kind = "check"
            elif owed <= max(1, seat.stack // 4):
                kind = "call"
            else:
                kind = "fold"
            self._act(self.actor, kind)
            guard += 1

    def _parse(self, action, owed):
        text = action or ""
        if text.startswith("1:Check"):
            return "check"
        if text.startswith("1:Call"):
            return "call"
        if text.startswith("2:Bet") or text.startswith("2:Raise"):
            return "raise"
        if text.startswith("3:Fold"):
            return "fold"
        if text.startswith("9:") or text.startswith("0:") or text.startswith("7:"):
            return ""
        if text:
            return ""
        return "check" if owed <= 0 else "fold"

    def request(self, hero, opcode, action, joining):
        seat_index = self._index(hero)
        if seat_index is None:
            return 3, [("s", 35, "You are out of gold.")]
        if self.phase == "waiting":
            if joining or opcode in (30, 31, 36):
                started = self.start_hand(hero)
                if started == "broke":
                    return 3, [("s", 35, "You are out of gold.")]
                if started == "deal":
                    self.seen[hero] = "dealt"
                    return 2, self._deal_fields(hero)
            return 1, self._wait_fields(hero)
        if self.phase == "showdown":
            # New hand is the button after the results dialog, opcode 31.
            # A player who has not been sent that dialog stays on the wait.
            if opcode == 31 and self.seen.get(hero) == "showdown":
                started = self.start_hand(hero)
                if started == "broke":
                    return 3, [("s", 35, "You are out of gold.")]
                if started == "deal":
                    self.seen[hero] = "dealt"
                    return 2, self._deal_fields(hero)
                return 1, self._wait_fields(hero)
            if opcode == 63:
                self.seen[hero] = "showdown"
                return 3, self._show_fields(hero)
            return 1, self._wait_fields(hero)
        if self.seen.get(hero) == "need":
            self.seen[hero] = "dealt"
            return 2, self._deal_fields(hero)
        if self.seen.get(hero) != "dealt":
            # Sat down during this hand. The next deal includes them.
            return 1, self._wait_fields(hero)
        mine = self._index(hero)
        if mine is not None and mine == self.actor and self.phase == "hand":
            owed = max(0, self.bet - self.seats[mine].street)
            kind = self._parse(action, owed)
            if kind:
                self._act(mine, kind)
        self._bots()
        self._sync()
        if self.phase == "showdown":
            # Status 3 on opcode 31 walks the phone back to town. The
            # showdown has to be the answer to the in-hand poll, opcode 63.
            if opcode == 63:
                self.seen[hero] = "showdown"
                return 3, self._show_fields(hero)
            return 1, self._wait_fields(hero)
        if opcode == 31:
            return 2, self._deal_fields(hero)
        return 1, self._action_fields(hero)

    def _label(self, hero):
        return "poker:%s:%s" % (self.token, hero)

    def _wait_fields(self, hero):
        index = self._index(hero)
        fields = [("s", 20, self._label(hero)), ("i", 21, index if index is not None else 0), ("i", 31, 1)]
        for seat, player in enumerate(self.seats):
            if player and not player.left:
                fields.append(("b", 22, seat_record(seat, player.name)))
        return fields

    def _stacks(self):
        return ints4([seat.stack if seat else 0 for seat in self.seats])

    def _actions(self):
        return ints4([seat.action if seat else 0 for seat in self.seats])

    def _ae(self, seat):
        owed = max(0, self.bet - seat.street)
        if owed <= 0:
            return 0
        return seat.client_street + owed

    def _only_call(self, seat):
        owed = max(0, self.bet - seat.street)
        inc = self.bb if len(self.board) <= 3 else self.bb * 2
        if self.raises >= self.cap or seat.stack <= owed + inc - 1:
            return 1
        return 1 if seat.stack <= owed else 0

    def _common(self, hero):
        index = self._index(hero) or 0
        seat = self.seats[index]
        fields = [
            ("s", 20, self._label(hero)),
            ("i", 21, index),
            ("b", 26, self._actions()),
            ("b", 27, bytes(self.board)),
            ("i", 30, self.pot),
            ("b", 32, self._stacks()),
            ("i", 28, self.turn),
            ("i", 29, self.actor if self.actor is not None else -1),
            ("i", 33, self._only_call(seat) if seat else 0),
            ("i", 34, self._ae(seat) if seat else self.bet),
            ("i", 31, self.turn if self.actor == index else 1),
        ]
        for n, player in enumerate(self.seats):
            if player and not player.left:
                fields.append(("b", 22, seat_record(n, player.name)))
        return fields

    def _deal_fields(self, hero):
        index = self._index(hero) or 0
        seat = self.seats[index]
        holes = bytes(seat.hole) if seat else b"\x00\x00"
        fields = [
            ("i", 23, self.button if self.button >= 0 else 0),
            ("b", 24, holes),
            ("i", 25, self.sb),
            ("i", 37, BUY_IN),
        ]
        fields.extend(self._common(hero))
        return fields

    def _action_fields(self, hero):
        return self._common(hero)

    def _show_fields(self, hero):
        index = self._index(hero) or 0
        holes = bytearray(8)
        for n, seat in enumerate(self.seats):
            if seat and not seat.folded and len(seat.hole) == 2:
                holes[n * 2] = seat.hole[0]
                holes[n * 2 + 1] = seat.hole[1]
        fields = [
            ("s", 20, self._label(hero)),
            ("b", 36, bytes(holes)),
            ("i", 39, self.rank),
            ("b", 26, ints4(self.wins)),
            ("b", 27, bytes(self.board)),
            ("i", 30, self.pot),
            ("b", 32, self._stacks()),
            ("i", 31, 1),
        ]
        for n, player in enumerate(self.seats):
            if player and not player.left:
                fields.append(("b", 22, seat_record(n, player.name)))
        return fields


class BlackjackTable:
    def __init__(self, bank, ante=BJ_ANTE, turn=TURN, goblin=False, rng=None):
        self.bank = bank
        self.ante = ante or BJ_ANTE
        self.turn = turn or TURN
        self.goblin = goblin
        self.rng = rng or random.Random()
        self.seats = [None] * SEATS
        self.cards = [[] for _ in range(SEATS)]
        self.stood = [False] * SEATS
        self.phase = "waiting"
        self.actor = None
        self.pot = 0
        self.carried = 0
        self.seen = {}
        self.winner = None
        self.token = 0
        self.shown_pot = 0

    def sitting(self, hero):
        return any(seat and seat.owner == hero and not seat.left for seat in self.seats)

    def sit(self, hero, stack):
        if self.sitting(hero):
            return self._index(hero)
        for index, seat in enumerate(self.seats):
            if seat is None:
                player = Seat(hero, stack, hero)
                if self.phase == "hand":
                    player.folded = True
                    self.stood[index] = True
                self.seats[index] = player
                self.seen[hero] = "waiting"
                self.bank.set_table(hero, stack, 0)
                return index
        return None

    def sit_bots(self):
        used = {seat.name for seat in self.seats if seat}
        for name in BOTS:
            if name in used:
                continue
            for index, seat in enumerate(self.seats):
                if seat is None:
                    self.seats[index] = Seat(name, BUY_IN, None)
                    break

    def _index(self, hero):
        for index, seat in enumerate(self.seats):
            if seat and seat.owner == hero and not seat.left:
                return index
        return None

    def leave(self, hero):
        index = self._index(hero)
        if index is None:
            return
        seat = self.seats[index]
        if self.phase != "hand":
            self.bank.add_gold(hero, seat.stack)
            self.seats[index] = None
            self.seen.pop(hero, None)
            return
        seat.folded = True
        seat.left = True
        self.stood[index] = True
        self.seen.pop(hero, None)
        if self.actor == index:
            self._advance(index)
        self._bots()
        self.bank.add_gold(hero, seat.stack)
        seat.stack = 0

    def _sync(self):
        for index, seat in enumerate(self.seats):
            if seat and seat.human:
                committed = seat.contrib if self.phase == "hand" else 0
                self.bank.set_table(seat.owner, seat.stack, committed)
        if self.phase != "hand":
            for seat in self.seats:
                if seat and seat.left and seat.owner:
                    self.bank.clear_committed(seat.owner)

    def _restock(self, hero):
        for index, seat in enumerate(list(self.seats)):
            if not seat:
                continue
            if seat.human and seat.stack < self.ante:
                seat.stack += self.bank.rebuy(seat.owner, BUY_IN)
            elif self.goblin and not seat.owner and seat.stack < self.ante:
                seat.stack = BUY_IN
            if seat.stack < self.ante:
                if seat.human:
                    self.bank.set_table(seat.owner, seat.stack, 0)
                self.seats[index] = None
                self.seen.pop(seat.owner, None)
        if hero and self._index(hero) is None:
            return False
        humans = [s for s in self.seats if s and s.human]
        if self.goblin:
            return len([s for s in self.seats if s and s.stack >= self.ante]) >= 2
        return len(humans) >= 2

    def start_hand(self, hero):
        if not self._restock(hero):
            self.phase = "waiting"
            return "wait" if self._index(hero) is not None else "broke"
        players = [i for i, seat in enumerate(self.seats) if seat and seat.stack >= self.ante]
        if len(players) < 2:
            self.phase = "waiting"
            return "wait"
        self.token += 1
        self.deck = fresh_deck(self.rng)
        self.cards = [[] for _ in range(SEATS)]
        self.stood = [True] * SEATS
        self.pot = self.carried
        self.carried = 0
        self.winner = None
        self.phase = "hand"
        for index in players:
            seat = self.seats[index]
            take = min(self.ante, seat.stack)
            seat.stack -= take
            seat.contrib = take
            self.pot += take
            seat.folded = False
            seat.left = False
            self.stood[index] = False
            self.cards[index] = [self.deck.pop(), self.deck.pop()]
        self.actor = players[0]
        for seat in self.seats:
            if seat and seat.owner:
                self.seen[seat.owner] = "need"
        self.shown_pot = self.pot
        self._sync()
        return "deal"

    def _advance(self, index):
        if self.phase != "hand":
            return
        live = [i for i, seat in enumerate(self.seats) if seat and not seat.folded and not seat.left and not self.stood[i]]
        if not live:
            self._finish()
            return
        for step in range(1, SEATS + 1):
            nxt = (index + step) % SEATS
            if nxt in live:
                self.actor = nxt
                return
        self._finish()

    def _finish(self):
        scores = []
        for index, seat in enumerate(self.seats):
            if not seat or seat.folded or seat.left or not self.cards[index]:
                scores.append(None)
            else:
                scores.append(hand_value(self.cards[index]))
        best = -1
        winners = []
        for index, total in enumerate(scores):
            if total is None or total > 21:
                continue
            if total > best:
                best = total
                winners = [index]
            elif total == best:
                winners.append(index)
        self.shown_pot = self.pot
        if len(winners) == 1:
            self.seats[winners[0]].stack += self.pot
            self.winner = winners[0]
            self.pot = 0
            self.carried = 0
        else:
            self.winner = None
            self.carried = self.pot
        for seat in self.seats:
            if seat:
                seat.contrib = 0
        self.phase = "showdown"
        self.actor = None
        for seat in list(self.seats):
            if seat and seat.left and seat.owner:
                self.bank.clear_committed(seat.owner)
        self.seats = [seat if seat and not seat.left else None for seat in self.seats]
        self._sync()

    def _act(self, index, kind):
        if self.phase != "hand" or self.stood[index]:
            return
        cards = self.cards[index]
        if kind == "hit" and len(cards) < 6:
            cards.append(self.deck.pop())
            if hand_value(cards) > 21 or len(cards) >= 6:
                self.stood[index] = True
                self._advance(index)
            return
        self.stood[index] = True
        self._advance(index)

    def _bots(self):
        guard = 0
        while self.phase == "hand" and self.actor is not None and guard < 24:
            seat = self.seats[self.actor]
            if seat is None or seat.human:
                return
            if seat.left or seat.folded or self.stood[self.actor]:
                self._advance(self.actor)
                guard += 1
                continue
            total = hand_value(self.cards[self.actor])
            kind = "hit" if total < 17 and len(self.cards[self.actor]) < 6 else "stand"
            self._act(self.actor, kind)
            guard += 1

    def _parse(self, action):
        text = action or ""
        if text.startswith("1:Hit"):
            return "hit"
        if text.startswith("1:Cheat") or text.startswith("2:Stand"):
            return "stand"
        if text.startswith("9:") or text.startswith("3:") or text.startswith("0:"):
            return ""
        if text:
            return ""
        return "stand"

    def request(self, hero, opcode, action, joining):
        if self._index(hero) is None:
            return 3, [("s", 35, "You are out of gold.")]
        if self.phase == "waiting":
            if joining or opcode in (30, 31, 36):
                started = self.start_hand(hero)
                if started == "broke":
                    return 3, [("s", 35, "You are out of gold.")]
                if started == "deal":
                    self.seen[hero] = "dealt"
                    return 2, self._deal_fields(hero)
            return 1, self._wait_fields(hero)
        if self.phase == "showdown":
            if opcode == 31 and self.seen.get(hero) == "showdown":
                started = self.start_hand(hero)
                if started == "broke":
                    return 3, [("s", 35, "You are out of gold.")]
                if started == "deal":
                    self.seen[hero] = "dealt"
                    return 2, self._deal_fields(hero)
                return 1, self._wait_fields(hero)
            if opcode == 32:
                self.seen[hero] = "showdown"
                return 3, self._show_fields(hero)
            return 1, self._wait_fields(hero)
        if self.seen.get(hero) == "need":
            self.seen[hero] = "dealt"
            return 2, self._deal_fields(hero)
        if self.seen.get(hero) != "dealt":
            return 1, self._wait_fields(hero)
        mine = self._index(hero)
        if opcode == 32 and mine is not None and mine == self.actor:
            kind = self._parse(action)
            if kind:
                self._act(mine, kind)
        self._bots()
        self._sync()
        if self.phase == "showdown":
            # Status 3 on opcode 31 leaves the table. Showdown is opcode 32.
            if opcode == 32:
                self.seen[hero] = "showdown"
                return 3, self._show_fields(hero)
            return 1, self._wait_fields(hero)
        if opcode == 32:
            return 2, self._update_fields(hero)
        return 2, self._deal_fields(hero)

    def _view(self, real, hero_seat):
        return (real - hero_seat) % SEATS

    def _label(self, hero):
        return "bj:%s:%s" % (self.token, hero)

    def _wait_fields(self, hero):
        hero_seat = self._index(hero) or 0
        fields = [
            ("s", 20, self._label(hero)),
            ("i", 21, 0),
            ("i", 25, 0),
            ("i", 31, 1),
        ]
        for index, seat in enumerate(self.seats):
            if seat and not seat.left:
                fields.append(("b", 22, seat_record(self._view(index, hero_seat), seat.name)))
        return fields

    def _record(self, index, hero_seat):
        cards = self.cards[index]
        return bytes([self._view(index, hero_seat)]) + bytes(cards)

    def _deal_fields(self, hero):
        hero_seat = self._index(hero) or 0
        fields = [
            ("s", 20, self._label(hero)),
            ("i", 21, 0),
            ("i", 25, 0),
            ("i", 26, self.turn),
            ("i", 28, 0),
            ("i", 29, self.pot),
            ("i", 31, self.turn if self.actor == hero_seat else 1),
        ]
        for index, seat in enumerate(self.seats):
            if seat and not seat.left:
                fields.append(("b", 22, seat_record(self._view(index, hero_seat), seat.name)))
            if seat and self.cards[index]:
                # Six bytes after the seat, the width of one blackjack hand.
                padded = list(self.cards[index]) + [0] * (6 - len(self.cards[index]))
                fields.append(("b", 23, bytes([self._view(index, hero_seat)]) + bytes(padded[:6])))
        return fields

    def _update_fields(self, hero):
        hero_seat = self._index(hero) or 0
        extra = 0
        for cards in self.cards:
            if len(cards) > 2:
                extra = max(extra, len(cards) - 2)
        fields = [
            ("i", 31, self.turn if self.actor == hero_seat else 1),
            ("i", 22, extra),
            ("i", 24, self.turn),
            ("i", 25, -1),
        ]
        for index, seat in enumerate(self.seats):
            if seat and self.cards[index]:
                fields.append(("b", 23, self._record(index, hero_seat)))
        return fields

    def _show_fields(self, hero):
        hero_seat = self._index(hero) or 0
        fields = [("i", 31, 1), ("i", 29, self.shown_pot)]
        for index, seat in enumerate(self.seats):
            if seat and self.cards[index]:
                fields.append(("b", 23, self._record(index, hero_seat)))
        if self.winner is not None and self.seats[self.winner]:
            fields.append(("i", 28, self._view(self.winner, hero_seat)))
        return fields


class Rooms:
    """One goblin table per hero, one public table per game, and named tables."""

    def __init__(self, bank):
        self.bank = bank
        self.tables = {}
        self.rng = None

    def _game(self, rec):
        return 10 if rec.get("game") == 10 else 11

    def drop(self, hero):
        for key in list(self.tables):
            table = self.tables[key]
            if table.sitting(hero):
                table.leave(hero)
            if not any(seat and seat.human for seat in table.seats):
                if key[1] != "public":
                    self.tables.pop(key, None)
        self.reconcile(hero)

    def names(self, game):
        found = []
        for key, table in self.tables.items():
            if key[0] == game and key[1] == "private":
                found.append(key[2])
        return found

    def _new(self, game, goblin, sb, bb, ante, cap, turn):
        if game == 10:
            return BlackjackTable(self.bank, ante=ante, turn=turn, goblin=goblin, rng=self.rng)
        return PokerTable(self.bank, sb=sb, bb=bb, cap=cap, turn=turn, goblin=goblin, rng=self.rng)

    def _table_for(self, rec, fields, create):
        game = self._game(rec)
        hero = rec.get("hero")
        goblin = False
        for value in fields.get(1) or []:
            if isinstance(value, int) and value == 1 and not create:
                goblin = True
        name = None
        for value in fields.get(2) or []:
            if isinstance(value, str) and value.strip():
                name = value.strip()
        if create:
            name = ""
            for value in fields.get(1) or []:
                if isinstance(value, str) and value.strip():
                    name = value.strip()
            if not name:
                name = "Table"
        if goblin:
            key = (game, "goblin", hero)
        elif name and not create:
            key = (game, "private", name)
        elif create:
            key = (game, "private", name)
        else:
            key = (game, "public", "")
        table = self.tables.get(key)
        if table is None and key[1] == "private" and not create:
            return None, key
        if table is None:
            sb, bb, ante, cap, turn = POKER_SB, POKER_BB, BJ_ANTE, 4, TURN
            ints = {}
            for tag, values in fields.items():
                for value in values:
                    if isinstance(value, int) and tag not in ints:
                        ints[tag] = value
            if game == 10:
                ante = ints.get(3) or BJ_ANTE
                turn = ints.get(4) or TURN
            else:
                sb = ints.get(3) or POKER_SB
                bb = sb * 2
                turn = ints.get(4) or TURN
                cap = ints.get(7) or 4
            table = self._new(game, goblin, sb, bb, ante, cap, turn)
            self.tables[key] = table
        return table, key

    def _leave_others(self, hero, keep):
        """One hero sits at one table. Cash out of any other seat first."""
        for key in list(self.tables):
            if key == keep:
                continue
            table = self.tables[key]
            if any(seat and seat.owner == hero and not seat.left for seat in table.seats):
                table.leave(hero)
            if not any(seat and seat.human for seat in table.seats):
                if key[1] != "public":
                    self.tables.pop(key, None)
        self.reconcile(hero)

    def handle(self, rec, opcode, fields):
        hero = rec.get("hero")
        game = self._game(rec)
        if opcode == 35:
            return 1, [("r", 20, name) for name in self.names(game)]
        if opcode not in (30, 31, 32, 34, 36, 63):
            return None
        if not hero:
            return 3, [("s", 35, "Create a hero first.")]
        action = ""
        for value in fields.get(5) or []:
            if isinstance(value, str):
                action = value
        if opcode == 34:
            self.drop(hero)
            # Tag 2 would pop a dialog on top of the town the phone already opened.
            return 1, []
        # A poll does not say which table. Stay in the seat they already have.
        # Opcode 63 status 3 is a showdown, so a missing seat uses status 4,
        # which is the phone's "leave the table" reply.
        if opcode in (31, 32, 63):
            table, key = self._current(hero, game)
            if table is None:
                if opcode == 31:
                    return 3, [("s", 35, "You are out of gold.")]
                return 4, [("s", 35, "You are out of gold.")]
            return self._finish(hero, table, key, opcode, action, False)
        create = opcode == 36
        table, key = self._table_for(rec, fields, create)
        if table is None:
            return 3, [("s", 35, "That table is not open.")]
        if not table.sitting(hero):
            self._leave_others(hero, key)
            if all(seat is not None for seat in table.seats):
                return 3, [("s", 35, "That table is full.")]
            stack = self.bank.buy(hero, BUY_IN)
            if stack <= 0:
                return 3, [("s", 35, "You are out of gold.")]
            sat = table.sit(hero, stack)
            if sat is None:
                self.bank.cash_stack(hero, stack)
                return 3, [("s", 35, "That table is full.")]
            # Seat 0 is the human. The three offline names fill the rest.
            if table.goblin:
                table.sit_bots()
        return self._finish(hero, table, key, opcode, action, opcode in (30, 36))

    def _current(self, hero, game):
        for key, table in self.tables.items():
            if key[0] != game:
                continue
            if any(seat and seat.owner == hero and not seat.left for seat in table.seats):
                return table, key
        return None, None

    def _finish(self, hero, table, key, opcode, action, joining):
        involved = set()
        for open_table in self.tables.values():
            for seat in open_table.seats:
                if seat and seat.owner:
                    involved.add(seat.owner)
        status, parts = table.request(hero, opcode, action, joining)
        for open_table in self.tables.values():
            for seat in open_table.seats:
                if seat and seat.owner:
                    involved.add(seat.owner)
        for name in involved:
            self.reconcile(name)
        if key is not None and not any(seat and seat.human for seat in table.seats) and key[1] != "public":
            self.tables.pop(key, None)
        return status, parts

    def reconcile(self, hero):
        """Write the hero's table stack and pot contribution from the seats."""
        in_play = 0
        committed = 0
        for table in self.tables.values():
            for seat in table.seats:
                if not seat or seat.owner != hero:
                    continue
                committed += seat.contrib
                if not seat.left:
                    in_play += seat.stack
        self.bank.write_chips(hero, in_play, committed)
