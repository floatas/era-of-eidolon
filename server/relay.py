#!/usr/bin/env python3
"""Era of Eidolon relay server.

The gen-2 clients honour a `Relay` JAD property: when set they POST every
request to it and pass the real URL in an X-relay-url header. So this needs no
patching of the game at all.

    python3 relay.py [port]        default 8080

Every request is written to capture/NNNN-<game>-op<N>.bin and decoded to stdout.
handlers.py is reloaded per request, so you can edit responses while the game
is running.
"""

import importlib
import os
import re
import struct
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import codec
import handlers

HERE = os.path.dirname(os.path.abspath(__file__))
CAPTURE = os.path.join(HERE, "capture")
LOGS = os.path.join(HERE, "logs")
os.makedirs(CAPTURE, exist_ok=True)
os.makedirs(LOGS, exist_ok=True)


class Tee:
    """Everything printed goes to the terminal AND to logs/relay.log, so a play
    session leaves a record without anyone having to remember to redirect.

    Note what this can and cannot capture. The gen-2 client never reports its
    own errors upstream — i.java:669 only builds a dialog; the errorreport.pl
    endpoint existed in gen 1 and was dropped. So an in-game "Error" box is
    NOT in here. What is: every request decoded, every response, the world
    state after each turn, and any exception a handler raised.

    The emulator's own stdout (the [net] lines, missing-resource warnings,
    stack traces it prints itself) goes to logs/emulator.log via run/play.sh.
    """

    def __init__(self, stream, path):
        self.stream = stream
        self.file = open(path, "a", buffering=1)
        self.file.write(f"\n=== session started {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    def write(self, data):
        self.stream.write(data)
        # keep the log readable: no terminal colour codes on disk
        self.file.write(re.sub(r"\x1b\[[0-9;]*m", "", data))

    def flush(self):
        self.stream.flush()
        self.file.flush()


sys.stdout = Tee(sys.stdout, os.path.join(LOGS, "relay.log"))

GAMES = {"prod4": "ShiradsForge", "prod5": "SterlingLake"}
_seq = 0

# What each jar already carries, so a want-list can be shown as have/missing.
# Resource key is (restype << 8) | id, named "<restype><hex id>" in the jar.
JARS = os.path.join(os.path.dirname(HERE), "jars")
_have = {}


def have(game):
    if game not in _have:
        import zipfile
        names = set()
        path = os.path.join(JARS, f"EoE-{game}.jar")
        if os.path.exists(path):
            with zipfile.ZipFile(path) as z:
                names = {n for n in z.namelist() if "/" not in n}
        _have[game] = names
    return _have[game]


def show_keylist(raw, game):
    """A chunk that is a flat list of u16 resource keys — the want-list."""
    if len(raw) < 2 or len(raw) % 2:
        return None
    keys = [struct.unpack_from(">H", raw, i)[0] for i in range(0, len(raw), 2)]
    if not all(0 < (k >> 8) <= 16 for k in keys):
        return None
    hits, miss = [], []
    pool = have(game)
    for k in keys:
        nm = f"{k >> 8}{k & 0xFF:x}"
        (hits if nm in pool else miss).append(f"{k >> 8}:{k & 0xFF:02x}")
    out = [f"      {len(keys)} resource keys requested"]
    if hits:
        out.append(f"      in jar  ({len(hits)}): " + " ".join(hits))
    if miss:
        out.append(f"      \033[33mMISSING ({len(miss)}): " + " ".join(miss)
                   + " <- server must supply\033[0m")
    return "\n".join(out)


class Req:
    def __init__(self, opcode, game, body, relay_url):
        self.opcode = opcode
        self.game = game
        self.body = body
        self.relay_url = relay_url
        self.chunks = codec.parse_chunks(body)
        # tag 0 / type 0 leading chunk is the echoed session blob B
        self.session = next(
            (raw for tag, typ, raw in self.chunks if tag == 0 and typ == 0), None)

    def all(self, tag):
        return [raw for t, _, raw in self.chunks if t == tag]

    def get(self, tag, default=b""):
        """Last chunk with this tag. d.java:686 re-adds tag 1 on every loop
        iteration with a growing buffer, so the last one is the complete set."""
        vals = self.all(tag)
        return vals[-1] if vals else default

    def int_(self, tag, default=0):
        raw = self.get(tag)
        return int.from_bytes(raw, "big", signed=True) if raw else default


def parse_target(url):
    """http://prod4.eraofeidolon.com/2/7.pl -> (7, 'ShiradsForge')"""
    opcode, game = None, "unknown"
    if url:
        tail = url.rsplit("/", 1)[-1]
        if tail.endswith(".pl"):
            try:
                opcode = int(tail[:-3])
            except ValueError:
                pass
        for host, name in GAMES.items():
            if host in url:
                game = name
    return opcode, game


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass  # we do our own

    def do_POST(self):
        global _seq
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length)
        relay_url = self.headers.get("X-relay-url")
        opcode, game = parse_target(relay_url or self.path)

        _seq += 1
        name = f"{_seq:04d}-{game}-op{opcode}"
        with open(os.path.join(CAPTURE, name + ".bin"), "wb") as f:
            f.write(body)

        req = Req(opcode, game, body, relay_url)

        print(f"\n\033[1m>>> #{_seq}  {game}  opcode={opcode}  {length}B\033[0m")
        print(f"    url: {relay_url}")
        if req.session is not None:
            print(f"    session B: {len(req.session)}B "
                  f"{req.session[:16].hex()}{'...' if len(req.session) > 16 else ''}")
        for tag, typ, raw in req.chunks:
            if tag == 0 and typ == 0:
                continue
            print(codec.fmt_chunks([(tag, typ, raw)]))
            kl = show_keylist(raw, game) if typ == 0 else None
            if kl:
                print(kl)

        try:
            importlib.reload(handlers)
            resp = handlers.dispatch(req)
        except Exception as e:  # never 500 — the client gives up on rc500
            print(f"    \033[31mhandler error: {e!r}\033[0m")
            resp = codec.build_response(status=1, chunks=[])

        print(f"\033[36m<<< {len(resp)}B  "
              f"status={resp[2] if len(resp) > 2 else '?'}  "
              f"chunks={struct.unpack_from('>H', resp, 8)[0] if len(resp) >= 10 else '?'}"
              f"\033[0m")

        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)

    do_GET = do_POST


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f"Era of Eidolon relay on http://127.0.0.1:{port}/  "
          f"(captures -> {CAPTURE})")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
