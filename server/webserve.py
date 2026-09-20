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

import os
import re
import sys
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


class Handler(relay.Handler):
    """relay.Handler already does POST; this adds a Range-capable static GET."""

    def log_message(self, *a):
        pass

    def do_POST(self):
        return relay.Handler.do_POST(self)

    def do_HEAD(self):
        self.do_GET(head=True)

    def do_GET(self, head=False):
        path = self.path.split("?", 1)[0]
        if path.rstrip("/") == "/relay":
            return relay.Handler.do_POST(self)

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


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    if not os.path.isdir(WEB):
        print(f"freej2me-web not found at {WEB}")
        sys.exit(1)
    print(f"player + relay on http://localhost:{port}/   (web root: {WEB})")
    print(f"MIDlet Relay property should be http://localhost:{port}/relay")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
