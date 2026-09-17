"""Cassino: the Hungarian two-player version, 52-card French deck.

Cards are strings: rank, then suit. Ranks A 2 3 4 5 6 7 8 9 10 J Q K,
suits S H D C.
"""
from dataclasses import dataclass, replace
from typing import NamedTuple, Optional

RANK_VALUES = {r: i + 1 for i, r in enumerate(
    ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
)}


def value(card: str) -> int:
    """The card's value: A=1 ... 10=10, J=11, Q=12, K=13."""
    return RANK_VALUES[card[:-1]]


class Move(NamedTuple):
    hand: frozenset
    table: frozenset


@dataclass(frozen=True)
class State:
    hands: tuple
    table: tuple
    talon: tuple
    piles: tuple
    sweeps: tuple
    player: int
    last_capturer: Optional[int] = None


def new_deal(deck, first: int = 0) -> State:
    """Deal from `deck`: 3 cards to `first`, 3 to the other, 4 to the table."""
    first_group = tuple(deck[0:3])
    second_group = tuple(deck[3:6])
    table = tuple(deck[6:10])
    talon = tuple(deck[10:])
    hands = (first_group, second_group) if first == 0 else (second_group, first_group)
    return State(
        hands=hands,
        table=table,
        talon=talon,
        piles=((), ()),
        sweeps=(0, 0),
        player=first,
        last_capturer=None,
    )


def _subsets_with_sums(cards, targets):
    """Every subset of `cards` (as lists) whose value-sum is in `targets`."""
    targets = set(targets)
    result = {t: [] for t in targets}
    if not targets:
        return result
    max_target = max(targets)
    cards = list(cards)
    vals = [value(c) for c in cards]
    n = len(cards)
    current = []

    def dfs(i, total):
        if total in targets:
            result[total].append(list(current))
        if i == n:
            return
        for j in range(i, n):
            if total + vals[j] > max_target:
                continue
            current.append(cards[j])
            dfs(j + 1, total + vals[j])
            current.pop()

    dfs(0, 0)
    return result


def legal_moves(state: State):
    """Every legal Move for the player to move."""
    hand = state.hands[state.player]
    if not hand:
        return []

    moves = []

    hand = list(hand)
    n = len(hand)
    hand_subsets_by_sum = {}
    for mask in range(1, 1 << n):
        subset = [hand[i] for i in range(n) if mask & (1 << i)]
        s = sum(value(c) for c in subset)
        hand_subsets_by_sum.setdefault(s, []).append(subset)

    if state.table and hand_subsets_by_sum:
        table_subsets_by_sum = _subsets_with_sums(state.table, hand_subsets_by_sum.keys())
        for s, table_subsets in table_subsets_by_sum.items():
            for hand_subset in hand_subsets_by_sum[s]:
                for table_subset in table_subsets:
                    moves.append(Move(frozenset(hand_subset), frozenset(table_subset)))

    for card in hand:
        moves.append(Move(frozenset({card}), frozenset()))

    return moves


def play(state: State, move: Move) -> State:
    """The state after `move`, including everything the rules make happen."""
    player = state.player
    hand = state.hands[player]
    hand_set = set(hand)

    if not move.hand or not move.hand <= hand_set:
        raise ValueError("you don't hold those cards")

    if move.table:
        table_set = set(state.table)
        if not move.table <= table_set:
            raise ValueError("those cards aren't on the table")
        if sum(value(c) for c in move.hand) != sum(value(c) for c in move.table):
            raise ValueError("a capture must add up")
    else:
        if len(move.hand) != 1:
            raise ValueError("place exactly one card")

    new_hand = tuple(c for c in hand if c not in move.hand)
    hands = list(state.hands)
    hands[player] = new_hand
    hands = tuple(hands)

    table_was_empty = len(state.table) == 0
    piles = state.piles
    sweeps = state.sweeps
    last_capturer = state.last_capturer

    if move.table:
        remaining_table = tuple(c for c in state.table if c not in move.table)
        taken = tuple(move.hand) + tuple(move.table)
        piles = list(piles)
        piles[player] = piles[player] + taken
        piles = tuple(piles)
        if not remaining_table:
            sweeps = list(sweeps)
            sweeps[player] += 1
            sweeps = tuple(sweeps)
        new_table = remaining_table
        last_capturer = player
        pass_turn = True
    else:
        new_table = state.table + tuple(move.hand)
        pass_turn = not table_was_empty

    candidate = (1 - player) if pass_turn else player
    other = 1 - candidate
    if not hands[candidate] and hands[other]:
        candidate = other
    next_player = candidate

    talon = state.talon

    if not hands[0] and not hands[1]:
        if talon:
            hands = (talon[0:3], talon[3:6])
            talon = talon[6:]
            next_player = last_capturer if last_capturer is not None else next_player
        else:
            if new_table:
                winner = last_capturer if last_capturer is not None else player
                piles = list(piles)
                piles[winner] = piles[winner] + new_table
                piles = tuple(piles)
            new_table = ()

    return State(
        hands=hands,
        table=new_table,
        talon=talon,
        piles=piles,
        sweeps=sweeps,
        player=next_player,
        last_capturer=last_capturer,
    )


def deal_over(state: State) -> bool:
    """True once every card has been taken."""
    return (
        not state.hands[0]
        and not state.hands[1]
        and not state.talon
        and not state.table
    )


def score(state: State):
    """A pair: the points each player earned in the finished deal."""
    points = []
    for p in (0, 1):
        pile = state.piles[p]
        pts = 0
        if len(pile) >= 27:
            pts += 3
        if sum(1 for c in pile if c.endswith("S")) >= 7:
            pts += 2
        pts += sum(1 for c in pile if c.startswith("A"))
        if "10D" in pile:
            pts += 2
        if "2S" in pile:
            pts += 1
        pts += state.sweeps[p]
        points.append(pts)
    return tuple(points)
