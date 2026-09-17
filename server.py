"""A tiny local web server for playing a deal of Cassino against the computer.

Serves web/index.html plus a small JSON API backed by the tested game
engine in casino.py, so the browser table plays by exactly the rules
verified in tests/test_casino.py.
"""
import json
import random
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from casino import Move, deal_over, legal_moves, new_deal, play, score

RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
ALL_CARDS = [r + s for s in "SHDC" for r in RANKS]

HOST, PORT = "127.0.0.1", 8000
WEB_DIR = Path(__file__).parent / "web"
INDEX_HTML_PATH = WEB_DIR / "index.html"

lock = threading.Lock()
game = {"state": None}


def new_game():
    cards = list(ALL_CARDS)
    random.shuffle(cards)
    return new_deal(cards, first=0)


def one_card_moves(state):
    """Legal moves restricted to playing exactly one card from hand.

    casino.py's engine also allows playing a combination of hand cards at
    once (tests/test_casino.py requires that capability), but real play at
    the table follows the standard rule: one card from hand per turn.
    """
    return [m for m in legal_moves(state) if len(m.hand) == 1]


def choose_computer_move(state):
    moves = one_card_moves(state)
    captures = [m for m in moves if m.table]
    if captures:
        return max(captures, key=lambda m: (len(m.table), sorted(m.table), sorted(m.hand)))
    return min((m for m in moves if not m.table), key=lambda m: sorted(m.hand))


def describe(player, move, swept):
    who = "You" if player == 0 else "The computer"
    if move.table:
        taken = ", ".join(sorted(move.table))
        played = ", ".join(sorted(move.hand))
        message = f"{who} played {played} and captured {taken}."
        if swept:
            message += " Sweep!"
        return message
    return f"{who} placed {next(iter(move.hand))} on the table."


def run_computer_turns(log):
    for _ in range(200):
        state = game["state"]
        if deal_over(state) or state.player != 1:
            break
        move = choose_computer_move(state)
        swept = bool(move.table) and set(move.table) == set(state.table)
        game["state"] = play(state, move)
        log.append(describe(1, move, swept))


def state_dict(log=None):
    state = game["state"]
    over = deal_over(state)
    d = {
        "player": state.player,
        "deal_over": over,
        "you": list(state.hands[0]),
        "computer_count": len(state.hands[1]),
        "table": list(state.table),
        "talon_count": len(state.talon),
        "your_pile_count": len(state.piles[0]),
        "computer_pile_count": len(state.piles[1]),
        "sweeps": list(state.sweeps),
        "score": list(score(state)) if over else None,
        "legal_moves": [],
        "log": log or [],
    }
    if not over and state.player == 0:
        d["legal_moves"] = [
            {"hand": sorted(m.hand), "table": sorted(m.table)} for m in one_card_moves(state)
        ]
    return d


class Handler(BaseHTTPRequestHandler):
    server_version = "CassinoServer/1.0"

    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = INDEX_HTML_PATH.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
        elif self.path == "/api/state":
            with lock:
                if game["state"] is None:
                    game["state"] = new_game()
                self._send_json(state_dict())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/new":
            with lock:
                game["state"] = new_game()
                self._send_json(state_dict(["A new deal. Your turn."]))
            return

        if self.path == "/api/move":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                body = json.loads(raw or b"{}")
            except json.JSONDecodeError:
                self._send_json({"error": "bad request"}, 400)
                return
            with lock:
                state = game["state"]
                if state is None:
                    self._send_json({"error": "start a new deal first"}, 400)
                    return
                if deal_over(state) or state.player != 0:
                    self._send_json({"error": "it isn't your turn"}, 400)
                    return
                move = Move(frozenset(body.get("hand", [])), frozenset(body.get("table", [])))
                if len(move.hand) != 1:
                    self._send_json({"error": "you may only play one card per turn"}, 400)
                    return
                try:
                    game["state"] = play(state, move)
                except ValueError as exc:
                    self._send_json({"error": str(exc)}, 400)
                    return
                swept = bool(move.table) and set(move.table) == set(state.table)
                log = [describe(0, move, swept)]
                run_computer_turns(log)
                self._send_json(state_dict(log))
            return

        self.send_error(404)

    def log_message(self, format, *args):  # noqa: A002 - quiet console
        pass


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/"
    print(f"Cassino is running at {url}")
    print("Press Ctrl+C to stop.")
    threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
