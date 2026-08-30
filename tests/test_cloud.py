from __future__ import annotations

import pytest

from receipts import cloud


def _report() -> dict:
    return {
        "verdict": "clean",
        "agent": "bob",
        "claim": "done",
        "findings": [],
        "ground_truth": {"files_written": [], "commands": []},
    }


def test_push_refuses_to_send_token_to_a_changed_api(monkeypatch) -> None:
    monkeypatch.setattr(
        cloud,
        "load_token",
        lambda: {"token": "secret", "workspace": "ws", "api": "https://one.test"},
    )
    monkeypatch.setenv("RECEIPTS_API", "https://two.test")

    with pytest.raises(cloud.CloudError, match="changed since login"):
        cloud.push(_report(), "run")


def test_push_uses_token_when_api_matches(monkeypatch) -> None:
    monkeypatch.setattr(
        cloud,
        "load_token",
        lambda: {"token": "secret", "workspace": "ws", "api": "https://one.test"},
    )
    monkeypatch.setenv("RECEIPTS_API", "https://one.test")
    seen = {}

    def request(path, payload=None, token=None):
        seen.update(path=path, payload=payload, token=token)
        return 200, {"url": "https://one.test/w/ws"}

    monkeypatch.setattr(cloud, "_request", request)

    assert cloud.push(_report(), "run") == 0
    assert seen["path"] == "/api/runs"
    assert seen["token"] == "secret"
