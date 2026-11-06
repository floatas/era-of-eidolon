#!/usr/bin/env python3
"""Serve the browser build and the game server from ONE origin.

CheerpJ maps Java HTTP onto the browser's fetch, so it obeys the same-origin
rule: scheme, host and port must match the page. Serving the emulator and the
relay from a single port sidesteps CORS entirely — the MIDlet's `Relay`
manifest property just points at /relay on the same host.

CheerpJ also requires the static files to honour the Range header, which
http.server does not do, so that is implemented here.

    python3 webserve.py [port]        default 8000

Then open http://localhost:<port>/ and load run/EoE-ShiradsForge-web.jar.
"""

import http.client
import json
import os
import re
import socket
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import relay  # noqa: E402  (reuses its decoding, capture and dispatch)

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(os.path.dirname(HERE), "tools", "freej2me-web", "web")

TYPES = {
    ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript",
    ".css": "text/css", ".json": "application/json", ".wasm": "application/wasm",
    ".jar": "application/java-archive", ".zip": "application/zip",
    ".png": "image/png", ".svg": "image/svg+xml", ".ico": "image/x-icon",
    ".sf2": "application/octet-stream", ".bin": "application/octet-stream",
}


def compendium_view(store=None):
    """The panel's contents: the hero's trophies, then the reference.

    The reference is not session-dependent. It used to name the room the
    player was in, which meant knowing where they were — and under CheerpJ
    the client's map-loaded ping never reaches the server, so the panel sat
    on a stale room. It is a reference now: the player opens what they want.

    The Trophies tab belongs to whichever hero the latest request came from
    (saves().playing()); before any hero has played it lists every trophy as
    not yet earned. The page reloads this each time the panel is opened.
    """
    from compendium import reference
    import trophies
    from world import saves
    book = reference()
    hero = (store or saves()).playing()
    return {**book, "sections": [trophies.panel(hero)] + list(book.get("sections", []))}


class Handler(relay.Handler):
    """relay.Handler already does POST; this adds a Range-capable static GET."""

    def log_message(self, *a):
        pass

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        # Card tables and towns post to this same origin. A desktop server
        # already on that port is used as-is; otherwise this process answers.
        if "/3/" in path and path.endswith(".pl"):
            return self.online_post("cards", 8082)
        if path.startswith("/1/"):
            return self.online_post("arena", 8081)
        return relay.Handler.do_POST(self)

    def online_post(self, kind, port):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        if _listening(port):
            try:
                self._proxy(port, body)
                return
            except OSError as exc:
                print(f"{kind} proxy failed: {exc}", flush=True)
        if kind == "cards":
            import cards
            if cards.Handler.store is None:
                cards.Handler.store = cards.Store(cards.SAVE)
            try:
                reply = cards.handle(self.path, body, cards.Handler.store)
            except Exception:
                traceback.print_exc()
                reply = cards.frame(1, [cards.field_str(2, cards.NOTE)])
            ctype = "application/octet-stream"
        else:
            import arena
            if arena.Handler.store is None:
                arena.Handler.store = arena.Store(arena.SAVE)
            try:
                reply = arena.handle(self.path, body, arena.Handler.store).encode("utf-8")
            except Exception as exc:
                print(f"arena {self.path} failed: {exc}", flush=True)
                reply = (arena.BAR + "1" + arena.BAR + "0" + arena.BAR + "0"
                         + arena.BAR + "0" + arena.BAR + "0").encode("utf-8")
            ctype = "text/plain"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(reply)))
        self.end_headers()
        self.wfile.write(reply)

    def _proxy(self, port, body):
        headers = {}
        for key in ("Content-Type", "X-relay-url"):
            val = self.headers.get(key)
            if val:
                headers[key] = val
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=30)
        try:
            conn.request("POST", self.path, body, headers)
            resp = conn.getresponse()
            data = resp.read()
            status = resp.status
            ctype = resp.getheader("Content-Type") or "application/octet-stream"
        finally:
            conn.close()
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_HEAD(self):
        self.do_GET(head=True)

    def do_GET(self, head=False):
        path = self.path.split("?", 1)[0]
        if path.rstrip("/") == "/relay":
            return relay.Handler.do_POST(self)
        if path == "/compendium":
            return self.compendium(head)

        rel = path.lstrip("/") or "index.html"
        full = os.path.normpath(os.path.join(WEB, rel))
        # The launcher links to /run, not /run.html — upstream is served behind
        # a dev server with clean-URL fallback, so do the same.
        if not os.path.isfile(full) and os.path.isfile(full + ".html"):
            full += ".html"
        if not full.startswith(WEB) or not os.path.isfile(full):
            self.send_error(404)
            return

        size = os.path.getsize(full)
        ctype = TYPES.get(os.path.splitext(full)[1].lower(),
                          "application/octet-stream")

        # CheerpJ fetches its runtime and the jar with Range requests.
        start, end = 0, size - 1
        rng = self.headers.get("Range")
        partial = False
        if rng:
            m = re.match(r"bytes=(\d*)-(\d*)", rng)
            if m:
                a, b = m.group(1), m.group(2)
                if a:
                    start = int(a)
                    end = int(b) if b else size - 1
                elif b:
                    start = max(0, size - int(b))
                start = min(start, size - 1 if size else 0)
                end = min(end, size - 1)
                partial = True

        length = max(0, end - start + 1)
        print(f"GET {path} -> {206 if partial else 200} {length}B")
        self.send_response(206 if partial else 200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(length))
        if partial:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        # No COOP/COEP here: `require-corp` blocks CheerpJ's own runtime,
        # which is fetched from their CDN and does not opt in with CORP.
        self.end_headers()
        if head:
            return
        with open(full, "rb") as fh:
            fh.seek(start)
            remaining = length
            while remaining > 0:
                chunk = fh.read(min(65536, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    def compendium(self, head=False):
        body = json.dumps(compendium_view()).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if not head:
            self.wfile.write(body)


def _listening(port):
    try:
        sock = socket.create_connection(("127.0.0.1", port), 0.2)
    except OSError:
        return False
    sock.close()
    return True


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    if not os.path.isdir(WEB):
        print(f"freej2me-web not found at {WEB}")
        sys.exit(1)
    print(f"player + relay on http://localhost:{port}/   (web root: {WEB})")
    print(f"MIDlet Relay property should be http://localhost:{port}/relay")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
