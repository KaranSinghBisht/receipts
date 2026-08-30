"""Connect a machine to a workspace, and push audited runs to it.

    receipts login          authorise this machine
    receipts push trace.ndjson
    receipts whoami / logout

The flow is the standard device authorisation shape: this machine asks for a
code, a browser confirms it, and this machine collects a bearer token. Be exact
about what that establishes -- it authorises a *machine* to write to a
workspace. There is no identity provider behind it and it does not identify a
person, so nothing here calls it an account.

Only the audit result is uploaded. The trace stays on the machine that produced
it: it is the most sensitive thing in the room, since it contains whatever the
agent printed, and there is no reason for a dashboard to hold it.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
from typing import Any

DEFAULT_API = "https://receipts-bob.vercel.app"
CONFIG = Path.home() / ".receipts" / "auth.json"
POLL_TIMEOUT_S = 600


class CloudError(RuntimeError):
    """Anything that stops a login or a push, phrased for the person reading it."""


def api_base() -> str:
    return os.environ.get("RECEIPTS_API", DEFAULT_API).rstrip("/")


def _request(path: str, payload: dict | None = None, token: str | None = None) -> tuple[int, dict]:
    url = f"{api_base()}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, method="POST" if data else "GET")
    request.add_header("content-type", "application/json")
    if token:
        request.add_header("authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as exc:
        body = exc.read()
        try:
            return exc.code, json.loads(body or b"{}")
        except json.JSONDecodeError:
            return exc.code, {"error": body.decode("utf-8", "replace")[:200]}
    except urllib.error.URLError as exc:
        raise CloudError(f"could not reach {api_base()}: {exc.reason}") from exc


def save_token(token: str, workspace: str) -> None:
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps({"token": token, "workspace": workspace, "api": api_base()}))
    CONFIG.chmod(0o600)


def load_token() -> dict[str, str] | None:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def login() -> int:
    status, start = _request("/api/device/start", {})
    if status != 200:
        raise CloudError(f"could not start a login: {start.get('error', status)}")

    code = start["user_code"]
    complete = start["verification_uri_complete"]

    # flush=True throughout: when stdout is a pipe -- CI, an IDE pane, `| tee` --
    # block buffering would otherwise hold the code back while we silently poll,
    # and the person would never see what they are meant to type.
    print(f"\n  Your code:  {code}\n", flush=True)
    print(f"  Confirm it at  {complete}\n", flush=True)
    if webbrowser.open(complete):
        print("  (opened in your browser)\n", flush=True)

    deadline = time.time() + POLL_TIMEOUT_S
    interval = max(1, int(start.get("interval", 2)))
    while time.time() < deadline:
        time.sleep(interval)
        status, body = _request("/api/device/poll", {"device_code": start["device_code"]})
        if status == 200:
            save_token(body["access_token"], body["workspace"])
            print(f"  Connected. Runs will appear at {api_base()}/w/{body['workspace']}", flush=True)
            return 0
        if body.get("error") == "authorization_pending":
            continue
        raise CloudError(f"login failed: {body.get('error', status)}")

    raise CloudError("timed out waiting for the code to be confirmed")


def push(report: dict[str, Any], name: str) -> int:
    auth = load_token()
    if not auth:
        raise CloudError("not connected. Run `receipts login` first.")
    if auth.get("api") != api_base():
        raise CloudError(
            "RECEIPTS_API has changed since login. Run `receipts login` again "
            "before sending this machine's token to a different server."
        )

    ground = report.get("ground_truth", {})
    payload = {
        "name": name,
        "verdict": report.get("verdict"),
        "agent": report.get("agent"),
        "claim": report.get("claim", ""),
        "findings": [
            {"severity": f["severity"], "title": f["title"], "detail": f["detail"]}
            for f in report.get("findings", [])
        ],
        "filesWritten": len(ground.get("files_written", [])),
        "commands": len(ground.get("commands", [])),
    }

    status, body = _request("/api/runs", payload, token=auth["token"])
    if status == 401:
        raise CloudError("this machine is no longer authorised. Run `receipts login`.")
    if status != 200:
        raise CloudError(f"push failed: {body.get('error', status)}")

    print(f"  Pushed {name} -> {body['url']}")
    return 0


def whoami() -> int:
    auth = load_token()
    if not auth:
        print("  Not connected. Run `receipts login`.")
        return 1
    print(f"  Connected to {auth['api']}/w/{auth['workspace']}")
    return 0


def logout() -> int:
    """Revoke the token server-side, then remove the local copy.

    Deleting only the local file used to leave a copied token working until its
    record was cleaned up by hand. Revocation is attempted first, but a network
    failure must not strand the credential on disk -- so the local file goes
    either way, and the failure is reported rather than swallowed.
    """
    auth = load_token()
    if auth is None:
        print("  Nothing to disconnect.")
        return 0

    revoked = False
    try:
        status, _ = _request("/api/device/revoke", {}, token=auth["token"])
        revoked = status == 200
    except CloudError as exc:
        print(f"  Could not reach the server to revoke: {exc}")

    CONFIG.unlink(missing_ok=True)
    if revoked:
        print("  Disconnected. The token is revoked and removed from this machine.")
    else:
        print("  Removed the token from this machine, but it was not revoked.")
        print("  Run `receipts logout` again once you are online to revoke it.")
    return 0
