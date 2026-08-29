"""A live audit board for a directory of traces.

    receipts watch traces/

Leave it open on a second screen. Every time an agent finishes a task and drops
its trace into the directory, the run appears here already audited — verdict,
findings, and the trace lines that prove them.

Deliberately small: the standard library's HTTP server, bound to loopback, no
build step and no dependencies. It serves exactly three things it generates
itself and never reads a path supplied by the client, so there is no file
serving to get wrong.
"""

from __future__ import annotations

import hashlib
import json
import threading
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .bundle import NoTraces, build_payload, render

WATCH_SUBHEAD = (
    "Watching for new traces. Each run is audited the moment it lands — against "
    "the record of what it actually did, not what it said it did."
)


class Board:
    """Rebuilds the audit whenever the traces directory changes."""

    def __init__(self, traces: Path, labels: dict[str, str] | None = None) -> None:
        self.traces = traces
        self.labels = labels or {}
        self._lock = threading.Lock()
        self._fingerprint: str | None = None
        self._payload: dict = {}
        self._error: str | None = None

    def _scan(self) -> str:
        """A cheap fingerprint of the directory: names, sizes, mtimes."""
        parts = []
        for path in sorted(self.traces.glob("*.ndjson")):
            try:
                stat = path.stat()
            except OSError:
                continue
            parts.append(f"{path.name}:{stat.st_size}:{stat.st_mtime_ns}")
        return hashlib.sha256("|".join(parts).encode()).hexdigest()[:16]

    def payload(self) -> dict:
        """The current audit, rebuilt only when the directory has changed."""
        fingerprint = self._scan()
        with self._lock:
            if fingerprint != self._fingerprint:
                self._fingerprint = fingerprint
                try:
                    self._payload = build_payload(self.traces, self.labels, WATCH_SUBHEAD)
                    self._error = None
                except NoTraces as exc:
                    self._payload = _waiting(str(exc))
                    self._error = str(exc)
            data = dict(self._payload)
        data["live"] = True
        data["revision"] = fingerprint
        return data


def _waiting(reason: str) -> dict:
    """What the board shows before the first trace arrives."""
    from . import __version__

    return {
        "receipts_version": __version__,
        "generated": "",
        "headline": "Waiting for the first trace",
        "subhead": f"{reason}. Point an agent at this directory and its run will appear here.",
        "totals": {"diverged": 0, "clean": 0, "findings": 0, "false_alarms": None},
        "runs": [],
    }


class _Handler(BaseHTTPRequestHandler):
    server_version = "Receipts"

    def __init__(self, *args, board: Board, **kwargs) -> None:
        self.board = board
        super().__init__(*args, **kwargs)

    def log_message(self, *args) -> None:  # noqa: D102 - quiet by default
        pass

    def _send(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        route = self.path.split("?", 1)[0]
        try:
            if route == "/":
                self._send(render(self.board.payload()).encode("utf-8"), "text/html; charset=utf-8")
            elif route == "/api/audit":
                body = json.dumps(self.board.payload()).encode("utf-8")
                self._send(body, "application/json; charset=utf-8")
            elif route == "/api/revision":
                body = json.dumps({"revision": self.board.payload()["revision"]}).encode()
                self._send(body, "application/json; charset=utf-8")
            else:
                self._send(b"not found", "text/plain; charset=utf-8", 404)
        except BrokenPipeError:
            pass  # the browser navigated away mid-response

    do_HEAD = do_GET


def serve(traces: Path, port: int = 7878, labels: dict[str, str] | None = None) -> str:
    """Run the board until interrupted. Returns the URL it listened on."""
    board = Board(traces, labels)
    server = ThreadingHTTPServer(("127.0.0.1", port), partial(_Handler, board=board))
    url = f"http://127.0.0.1:{server.server_address[1]}"
    print(f"receipts: watching {traces} — {url}")
    print("receipts: press Ctrl-C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nreceipts: stopped")
    finally:
        server.server_close()
    return url
